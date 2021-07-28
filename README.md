<p align="center"><img width="120
" alt="portfolio_view" src="https://raw.githubusercontent.com/ismet55555/yo-jenkins/main/dev_things/assets/logo_final.png"></p>

<h1 align="center">yo-jenkins</h1>


<!-- Licence Shield from https://shields.io/-->
<p align="center">

<a href="https://pypi.org/project/yo-jenkins/">
  <img alt="PYPI Version" src="https://img.shields.io/pypi/v/yo-jenkins?color=blue">
</a>

<a href="https://pypi.org/project/yo-jenkins/">
  <img alt="Python Versions" src="https://img.shields.io/pypi/pyversions/yo-jenkins">
</a>

<a href="https://pypi.org/project/yo-jenkins/">
  <img alt="PYPI Status" src="https://img.shields.io/pypi/status/yo-jenkins">
</a>

<a href="https://github.com/ismet55555/yo-jenkins/blob/main/LICENSE">
  <img alt="Licence" src="https://img.shields.io/github/license/ismet55555/yo-jenkins">
</a>

<!-- <a href="https://travis-ci.com/github/ismet55555/exam-terminal">
  <img alt="Build Status" src="https://img.shields.io/travis/com/ismet55555/exam-terminal/master">
</a>

<a href="https://www.codacy.com/gh/ismet55555/exam-terminal/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=ismet55555/exam-terminal&amp;utm_campaign=Badge_Grade">
  <img src="https://app.codacy.com/project/badge/Grade/dc108e18f27b4b86a9f6304745e6869c"/>
</a> -->
</p>


`yo-jenkins` is a cross-platform command line interface (CLI) tool to monitor, manage, and have fun with a Jenkins server. `yo-jenkins` makes it possible to interact with Jenkins server without using the browser based Jenkins UI. This tool is able to be integrated into a script as middleware in order to automate Jenkins related tasks.

**NOTE:** *This project is in **pre-alpha** release phase. Please report any issues, odd behavior, or suggestions. Read more about the [release cycle](https://en.wikipedia.org/wiki/Software_release_life_cycle).*

<!-- &nbsp; -->

# Overview

- [Overview](#overview)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Usage](#usage)
- [Jenkins Plugin Requirements](#jenkins-plugin-requirements)
- [Local Jenkins Server Setup Using Docker](#local-jenkins-server-setup-using-docker)
- [Bug Reports](#bug-reports)
- [Feature Requests](#feature-requests)
- [Contributing](#contributing)
  - [Contributors](#contributors)
- [Licence](#licence)


# Quick Start

TODO

# Installation

1. Install system dependencies for `simpleaudio` sound Python package
   - | Platform 	| Command                                                                        	|
     |----------	|--------------------------------------------------------------------------------	|
     | MacOS    	| Not needed                                                                     	|
     | Windows  	| Not needed                                                                     	|
     | Ubuntu   	| `sudo apt update && apt-get install -y python3-dev python3-pip libasound2-dev` 	|
     | CentOS   	| `sudo yum update && yum install -y python3-devel gcc alsa-lib-devel`           	|


2. Install `yo-jenkins`
    - Depending on your access rights, you may need to add `--user` to the below commands
    - **Option 1:** From Python Package Index (PYPI) using `pip`
      - ```bash
        pip install yo-jenkins
        ```

   - **Option 2:** Download all files in this GitHub repository and install using the included `setup.py`
     - ```bash
         python setup.py install

        # OR

         pip install .
         ```

# Usage

Each top level command has sub-commands. For example, `yo-jenkins server` has sub-commands `server-deploy` and `server-start`.

```txt
Usage: yo-jenkins [OPTIONS] COMMAND [ARGS]...

                        YO-JENKINS (Version: 0.0.0) 

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
  auth     Manage authentication and profiles
  build    Manage builds
  folder   Manage folders
  job      Manage jobs
  node     Manage nodes
  server   Manage server
  stage    Manage build stages
  step     Manage stage steps
  tools    Tools and more
```

# Jenkins Plugin Requirements

If you are using `yo-jenkins` on a pre-existing Jenkins server, make sure that the following Jenkins plugin are installed for `yo-jenkins` to use all its functionalities. However, these plugins tend to be installed by default.

In order to check/install a plugin, go to *Manage Jenkins > Manage Plugins > Installed OR Available*

- [Folders](https://plugins.jenkins.io/cloudbees-folder/) (cloudbees-folder)
- [Next Build Number](https://plugins.jenkins.io/next-build-number/) (next-build-number)
- [Promoted Builds](https://plugins.jenkins.io/promoted-builds/) (promoted-builds)

# Local Jenkins Server Setup Using Docker

`yo-jenkins` offers an easy way to quickly set up a local Jenkins server within a Docker container. This server is setup and ready to go to tinker with `yo-jenkins`. 

**NOTE:** You must have Docker on running. See [Docker installation guide](dev_things\docker.md).

Run the following command to set up a local Jenkins server:
```bash
yo-jenkins server server-deploy
```

Use `--help` for available options, and use `--debug` to troubleshoot any issues.

&nbsp;

---

# Bug Reports

As with any other software, issues do come up during various usage scenarios that may not be accounted for during development and testing. **Help from real users is enormously helpful.**

Please report and bugs and odd behaviors with either of these:

- Online at [GitHub Issues](https://github.com/ismet55555/yo-jenkins/issues/new?assignees=&labels=&template=bug_report.md&title=)
-  `yo-jenkins tools bug-report`

If possible, please include the command that caused the issue, running it with the `--debug` option. For example, `yo-jenkins server server-deploy --debug`

Note, that your issue may already be in queue, so please check the project [FIXME](https://github.com/ismet55555/yo-jenkins/projects/2).

# Feature Requests

This is a very young project, and we are always looking for new features and improvements. Please feel free to open an issue and suggest a feature. Please be as specific as possible, and include as much information as possible.

- Online at [GitHub Feature Request](https://github.com/ismet55555/yo-jenkins/issues/new?assignees=&labels=&template=feature_request.md&title=)
- `yo-jenkins tools feature-request`

Note, your suggestion may be part of the Project plan, so be sure to check the [TODO](https://github.com/ismet55555/yo-jenkins/projects/1) to see if it is already planned.


# Contributing

This project is an on-going effort, slowly adding various features and improvements. If you would like to contribute, please fork the project, make your changes, and submit a pull request.

**Any help, ideas, or testing is much appreciated.**

There is definitely work to be done. If you don't have a genius great idea for the next big change, or if you spot an issue you are able to fix, please checkout the [TODO](https://github.com/ismet55555/yo-jenkins/projects/1) and [FIXME](https://github.com/ismet55555/yo-jenkins/projects/2) or add your own ideas. For guides and information on how to get started and help out, check out the `dev_things` directory.

## Contributors

- **Ismet Handžić** - GitHub: [@ismet55555](https://github.com/ismet55555)


# Licence
This project is licensed under the *GNU General Public License Version 3* License. Please see the [LICENSE](LICENSE) file for details. Also a complete [history of this licence](https://en.wikipedia.org/wiki/GNU_General_Public_License).
