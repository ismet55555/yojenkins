# Contribution Guide

This document is to get you started to adding contribution to this project.
This guide assumes that a contributor is just getting started with open source
development, so it may come off as overly detailed.

In addition please look over these documents
    - [`pipenv`](pipenv.md)
    - [`pypi`](pypi.md)

If you have any question or issues, feel free to contact the project owner.
If you have and suggestions or improvements, feel free to submit a pull request.

Note that some of these things can be automated, however that is a `TODO` for now.
Also, note that as of now there are no sufficient tests setup (ie. pytest, unitest)


## Getting the Code to Your Computer
1. Clone the repo locally
    - `git clone <CLONE LINK>`


## Setting Up the Virtual Environment

Please review the `pipenv` guide: **TODO**

1. Change directory into the repo directory
    - `cd yo-jenkins`

2. Find out what python 3 version you are working with
    - `python3 --version`
    - *NOTE*: You may have more than one python 3 version on your computer

3. Install `pipenv`
    - `python -m pip install --upgrade pip`
    - `python -m pip install --upgrade-strategy=only-if-needed pipenv`

4. Install pipenv with development environment
    - `pipenv install --skip-lock --three --python 3.X --dev --editable .`
    -  _(`X` is the python version you would like to use)_

5. Get into the virtual environment
    - `pipenv shell`

6. *(Inside env)* Check that all packages are installed
    - `pip list`


## Running and Iterating Changes
1. Create a branch form the `main` branch
    - `git pull`
    - `git checkout -b <YOUR BRANCH NAME>`

2. Activate/Enter the virtual environment
    - `pipenv shell`

3. Make your changes to the project

4. Run the changes
    - `python yo_jenkins/__main__py` - This is effectivly what is run when running `yo-jenkins`

5. `git` add and commit as you like, adding good and useful commit messages

6. Once all changes and interations are complete, increment and tag the build version
    - `bumpversion patch`

6. Push changes to your development branch
    - `git push origin <YOUR BRANCH NAME>`

7. On GitHub open a pull request to merge to the `main` branch


8. **[BONUS]** Setting a alias for convenience
    - Linux / MacOS / WSL:
        1. ```bash
            alias yo-jenkins="pipenv run python <PATH TO PROEJCT>/yo_jenkins/__main__.py"
            ```
    - Windows:
        1. Add the following to your powershell profile (`$profile`)
        2. ```powershell
            function yo-jenkins {
            $PATH_TO_PROJECT='<PATH to PROJECT>'; `
            $CURRENT_DIR=pwd; `
            cd $PATH_TO_PROJECT; `
            pipenv run python $PATH_TO_PROJECT\yo_jenkins\__main__.py $args; `
            cd $CURRENT_DIR
            }
            ```

## Adding a New Dependency *(If needed)*

1. Install the package
    -  `pipenv install <PACKAGE NAME>`
    - `--dev` - Install the package for the dev environment only

2. Check `Pipfile` if the package was added
2. Lock `Pipfile.lock`
    - `pipenv lock`
    - `--clear` - Clears caches (pipenv, pip, and pip-tools)

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
    - `git push origin <YOUR BRANCH NAME>`

4. On GitHub open a pull request to merge to the `main` branch
