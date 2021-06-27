# `pipenv`

`pipenv` is used to setup a virtual environment for execution or development.
While it can be used for building of this project, a separate process is needed to build and package a module (`setup.py`).

The process and theory around `pipenv` is similar to other package managers such as RubyGems, npm, etc.  Essentially, it aims to constraint all dependencies and versions such that the resulting environment is consistent throughout installations.

Learn more: 
  - https://pipenv.pypa.io
  - https://realpython.com/pipenv-guide/
  - https://pipenv.pypa.io/en/latest/cli/

If you have any question or issues, feel free to contact the project owner.
If you have and suggestions or improvements, feel free to submit a pull request.

## Pipfile and Pipfile.lock

The `Pipfile` is an specification of all the packages to include in the virtual environment.
This file separates packages that are always included by default and packages that are used for development.

At a verfy high level, `Pipfile` is human readable and can be edited, while `Pipfile.lock` should not be edited by any individual and is read by the computer. `Pipfile` is meant to be alive and be editable, unlike the resulting `Pipfile.lock`

The `Pipfile` will yield a `Pipfile.lock`


## Installation of `pipenv`

- `pip install pipenv`


## Creating Environments 
### Development
  - `pipenv install --skip-lock --three --dev --editable .`
    - `--skip-lock` - Ignore the `Pipfile.lock` and install from the `Pipfile`. In addition, do not write out a Pipfile.lock reflecting changes to the Pipfile.
    - `--two`, `--three` - Python Major version to use
    - `--python 3.7` - Use specific python version for this environment
    - `--dev` - Indicate to install packages listed in the `Pipfile` sections `[dev-packages]` + `[packages]`
    - `--editable .` - Actively editable current directory. Sub-dependencies are not added to the Pipfile.lock if you leave the `--editable` option out


### Production deployment
- `pipenv install --deploy --three --ignore-pipfile`
    - `--deploy` - Abort if the `Pipfile.lock` is out-of-date, or Python version is wrong
    - `--two`, `--three` - Python Major version to use
    - `--ignore-pipfile` - Install from `Pipfile.lock`, ignore the `Pipfile`



## Other Useful pipenv CLI Commands
- `pipenv run` - Run one single command inside the virtual environment

- `pipenv shell` - Activate the created pipenv virtual environment

- `pipenv sync` - Installs all packages specified in Pipfile.lock

- `pipenv install <PACKAGE NAME>` - Installing additional packages:

- `pipenv lock` - Locking the current pipenv dependencies and package versions. Creates/modifies a `Pipfile.lock`
  - `--clear` - Clears caches (pipenv, pip, and pip-tools)

- `pipenv update` - Upgrade packages
  - Specific package: `pipenv update <PACKAGE NAME>`

- `pipenv uninstall` Uninstall packages
  - Specific package: `pipenv uninstall <PACKAGE NAME>`
  - All development packages: `pipenv uninstall --all-dev`

- `exit` or `CTRL+D` - Deactivating a active pipenv (reverse `pipenv shell`)

- `pipenv --where` - Output project home information.

- `pipenv graph` - List all python packages installed in an environment

- `pipenv update --outdated` - List out-of-date dependencies

- `pipenv --rm` - Removing the pipenv virtual environment

