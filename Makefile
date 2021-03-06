# ----------------------------------
#          INSTALL & TEST
# ----------------------------------
install_requirements:
	@pip install -r requirements.txt

check_code:
	@flake8 scripts/* cc_detector/*.py

black:
	@black scripts/* cc_detector/*.py

test:
	@coverage run -m pytest tests/*.py
	@coverage report -m --omit="${VIRTUAL_ENV}/lib/python*"

ftest:
	@Write me

clean:
	@rm -f */version.txt
	@rm -f .coverage
	@rm -fr */__pycache__ */*.pyc __pycache__
	@rm -fr build dist
	@rm -fr cc_detector-*.dist-info
	@rm -fr cc_detector.egg-info

install:
	@pip install . -U

all: clean install test black check_code

count_lines:
	@find ./ -name '*.py' -exec  wc -l {} \; | sort -n| awk \
        '{printf "%4s %s\n", $$1, $$2}{s+=$$0}END{print s}'
	@echo ''
	@find ./scripts -name '*-*' -exec  wc -l {} \; | sort -n| awk \
		        '{printf "%4s %s\n", $$1, $$2}{s+=$$0}END{print s}'
	@echo ''
	@find ./tests -name '*.py' -exec  wc -l {} \; | sort -n| awk \
        '{printf "%4s %s\n", $$1, $$2}{s+=$$0}END{print s}'
	@echo ''

# ----------------------------------
#      UPLOAD PACKAGE TO PYPI
# ----------------------------------
PYPI_USERNAME=<AUTHOR>
build:
	@python setup.py sdist bdist_wheel

pypi_test:
	@twine upload -r testpypi dist/* -u $(PYPI_USERNAME)

pypi:
	@twine upload dist/* -u $(PYPI_USERNAME)

# ----------------------------------
#      			GCP Setup
# ----------------------------------

# project id - replace with your GCP project id
PROJECT_ID=ccdetectorproject

# bucket name - replace with your GCP bucket name
BUCKET_NAME=cc_detector

# choose your region from https://cloud.google.com/storage/docs/locations#available_locations
REGION=europe-west1

# path to the file to upload to GCP
LOCAL_PATH='raw_data/Fics_data_pc_data.pgn'

# bucket directory in which to store the uploaded file (`data` is an arbitrary name that we choose to use)
BUCKET_FOLDER=data
BUCKET_TRAINING_FOLDER = 'trainings'

# name for the uploaded file inside of the bucket (we choose not to rename the file that we upload)
BUCKET_FILE_NAME=$(shell basename ${LOCAL_PATH})

PYTHON_VERSION=3.7
FRAMEWORK=scikit-learn
RUNTIME_VERSION=1.15

PACKAGE_NAME=cc_detector
FILENAME=trainer

JOB_NAME=cc_detector_training_$(shell date +'%Y%m%d_%H%M%S')

DOCKER_IMAGE_NAME=chessapiimage

set_project:
	@gcloud config set project ${PROJECT_ID}

create_bucket:
	@gsutil mb -l ${REGION} -p ${PROJECT_ID} gs://${BUCKET_NAME}

upload_data:
	@gsutil cp ${LOCAL_PATH} gs://${BUCKET_NAME}/${BUCKET_FOLDER}/${BUCKET_FILE_NAME}

run_locally:
	@python -m ${PACKAGE_NAME}.${FILENAME}

gcp_submit_training:
	gcloud ai-platform jobs submit training ${JOB_NAME} \
	--job-dir gs://${BUCKET_NAME}/${BUCKET_TRAINING_FOLDER}  \
	--package-path ${PACKAGE_NAME} \
	--module-name ${PACKAGE_NAME}.${FILENAME} \
	--python-version=${PYTHON_VERSION} \
	--runtime-version=${RUNTIME_VERSION} \
	--scale-tier CUSTOM \
	--master-machine-type n1-standard-16 \
	--region ${REGION} \
	--stream-logs

# ----------------------------------
#          DOCKER SET UP
# ----------------------------------
## https://vsupalov.com/docker-arg-env-variable-guide/

# run locally
run_image:
	docker run -e GOOGLE_APPLICATION_CREDENTIALS=/ccdetectorproject-e3fc70984fb0.json -p 8080:8000 eu.gcr.io/ccdetectorproject/chessapiimage:latest

# build, push and deploy
build_image:
	docker build -t eu.gcr.io/$PROJECT_ID/$DOCKER_IMAGE_NAME .
push_image:
	docker push eu.gcr.io/$PROJECT_ID/$DOCKER_IMAGE_NAME
deploy_image:
	gcloud run deploy \
		--image eu.gcr.io/$PROJECT_ID/$DOCKER_IMAGE_NAME \
		--platform managed \
		--region europe-west1 \
		--set-env-vars "GOOGLE_APPLICATION_CREDENTIALS=/ccdetectorproject-e3fc70984fb0.json"


##### Prediction API - - - - - - - - - - - - - - - - - - - - - - - - -
# load web server with code autoreload
run_api:
	uvicorn chessapi:app --reload
