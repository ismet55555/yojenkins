# Getting Started

This document is to get you started to get developing

1. Clone the repo locally
    - `git clone <CLONE LINK>`

2. Change directory into the repo directory
    - `cd exam-terminal`

3. Find out what python 3 version you are working with
    - `python3 --version`

3. Install pipenv with development environment
    - `pipenv install --three --python 3.X --dev -e .`  _(X is the python version you would like to use)_

4. Start the pipenv
    - `pipenv shell`

6. Check that all packages are installed
    - `pip list`

7. Run the program
    - `exam-terminal --sample`


After this any change you make in the code will be reflected when you run the program.
If you want to install a new pip package, you have to do it with `pipenv install`, and subsequently lock the environment with `pipenv lock`.  Also add the package to `requirements.txt`
