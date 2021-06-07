<h1 align="center">yo-jenkins</h1>

<!-- [![Testing, Building, and Publishing](https://github.com/ismet55555/yo-jenkins/actions/workflows/test-build-publish.yml/badge.svg?branch=main)](https://github.com/ismet55555/yo-jenkins/actions/workflows/test-build-publish.yml) -->

`yo-jenkins` is a command line interface (CLI) tool to monitor, manage, and have fun with a Jenkins server.  

## Installation

1. Install system dependencies for `simpleaudio` sound python package
   - | Platform 	| Command                                                                        	|
     |----------	|--------------------------------------------------------------------------------	|
     | MacOS    	| Not needed                                                                     	|
     | Windows  	| Not needed                                                                     	|
     | Ubuntu   	| `sudo apt update && apt-get install -y python3-dev python3-pip libasound2-dev` 	|
     | CentOS   	| `sudo yum update && yum install -y python3-devel gcc alsa-lib-devel`           	|


2. Install `yo-jenkins`
    - **Option 1:** From Python Package Index (PYPI)
      - ```bash
        pip install yo-jenkins
        ```

   - **Option 2:** Install using the included `setup.py`
     - ```bash
         python setup.py install
         ```