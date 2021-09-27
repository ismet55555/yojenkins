# Contribution Guide

This document is to get you started to adding contribution to this project.
This guide assumes that a contributor is just getting started with open source
development, so it may come off as overly detailed.

In addition please look over these documents
- [pipenv](pipenv.md)
- [pypi](pypi.md)

If you have any question or issues, feel free to contact the project owner.
If you have and suggestions or improvements, feel free to submit a pull request.

Note that some of these things can be automated, however that is a `TODO` for now.
Also, note that as of now there are no sufficient tests setup (ie. pytest, unitest)


## Getting the Code to Your Computer
1. Clone the repo locally
    - `git clone <GITHUB CLONE LINK>`


## Setting Up the Virtual Environment


1. Change directory into the repo directory
    - `cd yo-jenkins`

2. Find out what python 3 version you are working with
    - `python --version`
    - *NOTE*: You may have more than one python version on your computer. You may have to explicitly use `python3`

3. Add system dependencies for `simpleaudio` sound python package
    - **Windows:** Not needed, uses `winsound`
    - **MacOS:** Not needed
    - **Ubuntu:** `sudo apt update -y && apt-get install -y python3-dev python3-pip libasound2-dev`
    - **CentOS:** `sudo yum update -y && yum install -y python3-devel gcc alsa-lib-devel`

4. Upgrade tooling and install `pipenv`
    - `python3 -m pip install --upgrade pip setuptools virtualenv pipenv`

5. Install pipenv with development environment
    - `pipenv install --deploy --three --dev`
      -  `--python 3.X` - If needed, specify the exact python version to use
      -  `--editable .` - This is already included in `Pipenv` and will allow to actively run the project with the most recent changes

6. Check that all packages are installed
    - `pipenv graph`

7. Get into the virtual environment
    - `pipenv shell`




## Running and Iterating Changes
1. Create a branch form the `main` branch
    - `git pull`
    - `git checkout -b <YOUR BRANCH NAME>`

2. Activate/Enter the virtual environment
    - `pipenv shell`

3. Make your changes to the project

4. Run the changes
    - `yo-jenkins` - This works because the current package is marked as editable in `Pipfile`
    - `python yo_jenkins/__main__py` - This is effectively what is run when running `yo-jenkins`

5. `git` add and commit as you like, adding good and useful commit messages

6. Once all changes and interations are complete, increment and tag the build version
    - `bumpversion patch`

6. Push changes to your development branch
    - `git push origin <YOUR GIT BRANCH NAME>`

7. On GitHub open a pull request to merge to the `main` branch



## Formatting and Linting Code
1. If you haven't already, activate/enter the virtual environment
    - `pipenv shell`

2. Make sure you are in the root directory of the project

3. Run `yapf` formatter
    - `yapf --in-place --recursive .`

3. Run `pylint` code linter
    - `pylint yo_jenkins --fail-under=8 --reports y`


## Adding a New Dependency *(If needed)*

1. Install the package
    -  `pipenv install <NEW PACKAGE NAME>`
    - `--dev` - Install the package for the dev environment only

2. Check `Pipfile` if the package was added

3. Lock `Pipfile.lock`
    - `pipenv lock`
    - `--clear` - Clears caches (pipenv, pip, and pip-tools)
    - `--keep-outdated` - prevents pipenv from updating unrelated locked packages

4. Add the exact package listed in `Pipfile.lock` to `requirements.txt`


## Installing and Building the Project

This step is mainly to check if installation and building gives no errors

1. Install the project
    - `python setup.py install --verbose`

2. Run the project to test that everything set up fine
    - `yo-jenkins --help`

3. Build the project
    - `python setup.py sdist bdist_wheel`


## Submitting Your Changes

1. `git add` and `git commit` as you like, as you go along, adding good and useful commit messages

2. Once all changes and interations are complete, increment and tag the build version
    - `bumpversion patch`

3. Push changes to your development branch
    - `git push origin <YOUR GIT BRANCH NAME>`

4. On GitHub open a pull request to merge to the `main` branch
