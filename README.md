<h1 align="center">yo-jenkins</h1>


`yo-jenkins` is a command line interface (CLI) tool to monitor, manage, and have fun with a Jenkins server.  

Things that you can do (so far) with `yo-jenkins`:
    - TODO

## Requirements

- Jenkins server base URL
- Jenkins server credentials
    - Username _(Click on your name, top right in UI)_
    - Password -OR- API Token _(In your user profile > Configure > API Token)_ 


## Install

- Install the package locally using `setup.py`
    - ```bash
        python3 setup.py install
        ```

- Add your python directories to `.bash_profile`
    - Remember to change <YOUR USERNAME> and the python version
    - ```bash
        export PATH="/Users/<YOUR USERNAME>/Library/Python/3.8/bin/:$PATH"
        export PATH="/Users/<YOUR USERNAME>/Python/2.7/bin:$PATH"
        ```
