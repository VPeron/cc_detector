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
#          DOCKER SET UP
# ----------------------------------
DOCKER_IMAGE_NAME = 'chess-api-image'

# run locally
run_image:
	docker run -e GOOGLE_APPLICATION_CREDENTIALS=/credentials.json -p 8080:8000 chess-api-image

build_image:
	docker build -t eu.gcr.io/$PROJECT_ID/$DOCKER_IMAGE_NAME .
push_image:
	docker push eu.gcr.io/$PROJECT_ID/$DOCKER_IMAGE_NAME
deploy_image:
	gcloud run deploy \
		--image eu.gcr.io/$PROJECT_ID/$DOCKER_IMAGE_NAME \
		--platform managed \
		--region europe-west1 \
		--set-env-vars "GOOGLE_APPLICATION_CREDENTIALS=/credentials.json"

#TODO set env variables

##### Prediction API - - - - - - - - - - - - - - - - - - - - - - - - -
# load web server with code autoreload
run_api:
	uvicorn chessapi:app --reload
