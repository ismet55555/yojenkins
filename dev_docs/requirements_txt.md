# `requirements.txt`

**NOTE: requirements.txt is not used for this project. Instead this project uses `pipenv`
to set up a specified virtual environment.**

---

- Upgrade pip (python package manager)
    - `pip install --upgrade pip`

- Making a virtual environment called `env`
    - `python -m venv env`

- Activating the virtual environment
    - MacOS/Linux: `source ./env/bin/activate`
    - Windows: `.\env\Scripts\activate`

- *(Inside env)* Install all python packages listed
    - `pip install -r requirements.txt`

- *(Inside env)* List all packages installed in the virtual envirnonment
    - `pip list`

- *(Inside env)* When done, deactivate the virtual environment
    - `deactivate`

- Deleting a virtual environment
    - MacOS/Linux: `rm -rf ./env`
    - Windows: `rm -Force .\env`