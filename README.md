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

## Main Menu

```txt

Usage: __main__.py [OPTIONS] COMMAND [ARGS]...

                        YO-JENKINS (Version: 0.0.16) 

  yo-jenkins is a tool that is focused on interfacing with Jenkins server from
  the comfort of the beloved command line.  This tool can also be used as a
  middleware utility, generating and passing Jenkins information or automating
  tasks.

  QUICK START:

      1. Configure yo profile:  yo-jenkins auth configure

      2. Add yo API token:      yo-jenkins auth token --profile <PROFILE>

      3. Verify yo creds:       yo-jenkins auth verify

      4. Explore yo-jenkins

Options:
  -v, --version  Show the version
  --help         Show this message and exit.

Commands:
  auth    Manage authentication and profiles
  build   Manage builds
  folder  Manage folders
  job     Manage jobs
  node    Manage nodes
  server  Manage server
  stage   Manage build stages
  step    Manage stage steps

```