# `pipenv`

`pipenv` is used to setup a virtual environment for execution or development.
While it can be used for building packages, a seperate process is needed to build and package a module.

The process and theory around `pipenv` is similar to other package managers such as **RUBY** **NPM**, etc.  Essentially, it aims to constraint all dependencies and versions such that the resulting environment is consistent throughout installations

Learn more: 
  - https://pipenv.pypa.io
  - https://realpython.com/pipenv-guide/


## Pipfile and Pipfile.lock

At a verfy high level, `Pipfile` is human readable and can be edited, while `Pipfile.lock` should not be edited by any individual and is read by the computer.

The `Pipfile` is an specification of all the packages to include in the virtual environment.
This file separates packages that are always included by default and packages that are used for development.
This file is meant to be live and editable, unlike the resulting `Pipfile.lock`

The Pipfile will then yield a `Pipfile.lock`


## Installation

- `pip install pipenv`


## Basic Workflows


### Development
TODO


### Production deployment





## REDO ME

Reference: https://pipenv.pypa.io/en/latest/cli/

- Create pipenv and install packages from Pipfile:
  - `pipenv install [OPTIONS] [PROJECT DIRECTORY]`

  - `[OPTIONS]`:
    - `--deploy` - Abort if the Pipfile.lock is out-of-date, or Python version is wrong
    - `--ignore-pipfile` - Install from `Pipfile.lock`, ignore the `Pipfile`
    - `--skip-lock` - Ignore the `Pipfile.lock` and install from the `Pipfile`. In addition, do not write out a Pipfile.lock reflecting changes to the Pipfile.
    - `--editable .` - Actively editable current directory. Sub-dependencies are not added to the Pipfile.lock if you leave the `-e` option out
    - `--two`, `--three` - Python Major version
    - `--python 3.7` - Use specific python version
    - `--quiet` - No standard output

  - **Development Example:** *(includes `[dev-packages]` section in `Pipfile`)*
    - `pipenv install --skip-lock --three --dev --editable .`
  - **Production/Deployment Example:** *(includes `[packages]` section in `Pipfile`)*
    - `pipenv install --deploy --three --ignore-pipfile`



- Activate the created pipenv virtual environment
  - `pipenv shell`

- Installing additional packages:
  - `pipenv install <PACKAGE NAME>`

- Locking the current pipenv dependencies and package versions. Creates/modifies a `Pipfile.lock`
  - `pipenv lock`
  - `--clear` - Clears caches (pipenv, pip, and pip-tools)

- Upgrade packages
  - `pipenv update <PACKAGE NAME>`

- Uninstall the development packages
  - Specific package: `pipenv uninstall <PACKAGE NAME>`
  - All development packages: `pipenv uninstall --all-dev`

- Deactivating a active pipenv (reverse `pipenv shell`)
  - Linux: `exit` or `CTRL+D`
  - Windows: `exit`

- List all pipenv virtual environments for current directory/project
  - `cd` into project
  -  `pipenv --where`
  - **NOTE:** Typically virtual environments are stored in `$HOME/.virtualenvs/`

- List all python packages installed in an environment
  - Once you activate a environment (`pipenv shell`), run `pip list`

- Removing the pipenv virtual environment
  - `pipenv --rm`



## Other Useful Things:
- Run single command in the created pipenv
  - `pipenv run [COMMAND]`
  - Example: `pipenv run python main.py`
- Install all packages specified in `Pipfile.lock`
  - `pipenv sync`
- Find out what packages have changed upstream and update
  - Runs lock than sync
  - `pipenv update --outdated`
