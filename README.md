# Data analysis
- Document here the project: cc_detector
- Description: The intrinsic idea behind this project is to build a model that can detect whether a chess engine is being used to play an online chess game between two human players.
- Data Source: https://www.ficsgames.org/
- Type of analysis: 

The base model and initial approach takes on a supervised form and learns from a dataset comprised of around 50.000 games where every game is played by a human vs a computer.

# Startup the project

The initial setup.

Create virtualenv and install the project:
```bash
sudo apt-get install virtualenv python-pip python-dev
deactivate; virtualenv ~/venv ; source ~/venv/bin/activate ;\
    pip install pip -U; pip install -r requirements.txt
```

Unittest test:
```bash
make clean install test
```

Check for cc_detector in gitlab.com/{group}.
If your project is not set please add it:

- Create a new project on `gitlab.com/{group}/cc_detector`
- Then populate it:

```bash
##   e.g. if group is "{group}" and project_name is "cc_detector"
git remote add origin git@github.com:{group}/cc_detector.git
git push -u origin master
git push -u origin --tags
```

Functionnal test with a script:

```bash
cd
mkdir tmp
cd tmp
cc_detector-run
```

# Install

Go to `https://github.com/{group}/cc_detector` to see the project, manage issues,
setup you ssh public key, ...

Create a python3 virtualenv and activate it:

```bash
sudo apt-get install virtualenv python-pip python-dev
deactivate; virtualenv -ppython3 ~/venv ; source ~/venv/bin/activate
```

Clone the project and install it:

```bash
git clone git@github.com:{group}/cc_detector.git
cd cc_detector
pip install -r requirements.txt
make clean install test                # install and test
```
Functionnal test with a script:

```bash
cd
mkdir tmp
cd tmp
cc_detector-run
```
