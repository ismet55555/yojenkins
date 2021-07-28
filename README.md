<p align="center"><img width="150" alt="portfolio_view" src="https://raw.githubusercontent.com/ismet55555/yo-jenkins/readme_work/dev_things/assets/logo_final.png"></p>

<h1 align="center">yo-jenkins</h1>

<!-- [![Testing, Building, and Publishing](https://github.com/ismet55555/yo-jenkins/actions/workflows/test-build-publish.yml/badge.svg?branch=main)](https://github.com/ismet55555/yo-jenkins/actions/workflows/test-build-publish.yml) -->


<!-- Licence Shield from https://shields.io/-->
<p align="center">

<a href="https://pypi.org/project/yo-jenkins/">
  <img alt="PYPI Version" src="https://img.shields.io/pypi/v/yo-jenkins?color=blue">
</a>

<a href="https://pypi.org/project/yo-jenkins/">
  <img alt="Python Versions" src="https://img.shields.io/pypi/pyversions/yo-jenkins">
</a>

<a href="https://pypi.org/project/yo-jenkins/">
  <img alt="Packaging Format" src="https://img.shields.io/pypi/format/yo-jenkins">
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


`yo-jenkins` is a command line interface (CLI) tool to monitor, manage, and have fun with a Jenkins server.  

**NOTE:** *This tool is in **pre-alpha** release phase. Please report any issues, odd behavior, or suggestions. Read more about the [release cycle](https://en.wikipedia.org/wiki/Software_release_life_cycle).*

&nbsp;

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

# Jenkins Plugin Requirements

The following Jenkins plugin are required for `yo-jenkins` to use all its functionalities. In order to install a plugin, go to *Manage Jenkins > Manage Plugins > Available*
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

# Usage

<p align="center"><img width="150" alt="portfolio_view" src="https://raw.githubusercontent.com/ismet55555/yo-jenkins/readme_work/dev_things/assets/help_carbon.png"></p>

&nbsp;

# Report Bugs and Issues
As with any other software, issues do come up during various usage scenarios that may not be accounted for during development and testing. **Help from real users is enormously helpful.**

Please report and bugs and odd behaviors to [GitHub Issues](https://github.com/ismet55555/yo-jenkins/issues/new?assignees=&labels=&template=bug_report.md&title=). If possible, please include the command that caused the issue with `--debug`. For example:

```bash
yo-jenkins server server-deploy --debug
```

# Contributors
**Ismet Handžić** - GitHub: [@ismet55555](https://github.com/ismet55555)


# Licence
This project is licensed under the *GNU General Public License Version 3* License. Please see the [LICENSE](LICENSE) file for details. Also a complete [history of this licence](https://en.wikipedia.org/wiki/GNU_General_Public_License).
