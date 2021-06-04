# Python Package Index (PYPI)

PYPI is a packaging repository for python. Typically, when you run `pip install <PACKAGE NAME>` you
are fetching the package from https://pypi.org. 

There is also a mirror site of PYPI used for testing: https://test.pypi.org. This is a completely
separate site and repository only used for testing various things regarding packaging and deployment.
Anything done on TestPYPI will have no effect on PYPI.


## Bump the Package Version Number

- *NOTE:* You cannot push the same version to PYPI, it has to be different
- Version format: `MAJOR.MINOR.PATCH`
  - Example: `0.2.21`
- Run command:
  - Increase MAJOR: `bumpversion major`
  - Increase MINOR: `bumpverison minor`
  - Increase PATCH: `bumpversion patch`
- Run inside directory containing this file `.bumpversion.cfg`


## Clean Any Previous Build

- Build:
  - `python setup.py clean --all`
- Dist:
  - Linux/MacOS: `rm -rf dist`
  - Windows: `rm -force dist`


## Create source distribution and pure python wheels build

- `python setup.py sdist bdist_wheel`


## Upload Package to PYPI

- TestPYPI:
  - This is preferred for development work
  - https://test.pypi.org/project/exam-terminal/
  - `twine upload -r testpypi dist/* --verbose`
- PYPI:
  - The real deal. This is what users will download from
  - https://pypi.org/project/exam-terminal/
  - `twine upload dist/* --verbose`


## Post-hoc Installation of the Package from PYPI

- TestPYPI:
  - `pip install --extra-index-url https://test.pypi.org/simple/ exam-terminal -U`
  - *NOTE:* The `-i` *(another index/repo url)* option will not work because `pip` will try 
  to install dependencies from TestPYPI
- PYPI:
  - `pip install exam-terminal`
