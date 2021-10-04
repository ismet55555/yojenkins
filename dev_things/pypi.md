# Python Package Index (PYPI)

**NOTE: This outlines how to package and ship a python package to PYPI manually.
However, GitHub actions does this automatically.
Only do this manually in rare necessary situations.**

---

PYPI is a packaging repository for python. Typically, when you run `pip install <PACKAGE NAME>` you
are fetching the package from https://pypi.org.

There is also a mirror site of PYPI used for testing: https://test.pypi.org. This is a completely
separate site and repository only used for testing various things regarding packaging and deployment.
Anything done on TestPYPI will have no effect on PYPI.

If you have any question or issues, feel free to contact the project owner.
If you have and suggestions or imporvements, feel free to submit a pull request.

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
  - https://test.pypi.org/project/yojenkins/
  - `twine upload -r testpypi dist/* --verbose`
- PYPI:
  - The real deal. This is what users will download from
  - https://pypi.org/project/yojenkins/
  - `twine upload dist/* --verbose`


## Post-hoc Installation of the Package from PYPI

- TestPYPI:
  - `pip install --extra-index-url https://test.pypi.org/simple/ yojenkins -U`
  - *NOTE:* The `-i` *(another index/repo url)* option will not work because `pip` will try
  to install dependencies from TestPYPI
- PYPI:
  - `pip install yojenkins`
