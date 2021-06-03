# Python Package Index (PYPI) Update

- Bump the Package Version Number

  - Version format: `MAJOR.MINOR.PATCH`
  - `bumpversion major`, `bumpverison minor`, or `bumpversion patch`
  - Run inside directory containing file `.bumpversion.cfg`

- Clean Any Previous Build

  - Build: `python3 setup.py clean --all`
  - Dist: `rm -rf dist` (Windows: `rm -force dist`)

- Create source distribution and pure python wheels build

  - `python3 setup.py sdist bdist_wheel`

- Upload Package to PYPI

  - TestPYPI:
    - This is preferred for development work
    - https://test.pypi.org/project/exam-terminal/
    - `twine upload -r testpypi dist/*`
  - PYPI:
    - The real deal. This is what users will download from
    - https://pypi.org/project/exam-terminal/
    - `twine upload dist/*`

- Post-hoc Installation of Package
  - TestPYPI:
    - `pip install --extra-index-url https://test.pypi.org/simple/ exam-terminal -U`
    - NOTE: The `-i` option will not work because pip will try to install dependencies from TestPYPI
  - PYPI:
    - `pip install exam-terminal`
