<!-- <p align="center"><img width="120
" alt="portfolio_view" src="https://raw.githubusercontent.com/ismet55555/yojenkins/main/dev_things/assets/logo_final.png"></p> -->
<h1 align="center">yojenkins</h1>


<p align="center">

<a href="https://pypi.org/project/yojenkins/">
  <img alt="PYPI Version" src="https://img.shields.io/pypi/v/yojenkins?color=blue">
</a>

<a href="https://pypi.org/project/yojenkins/">
  <img alt="Python Versions" src="https://img.shields.io/pypi/pyversions/yojenkins">
</a>

<a href="https://pypi.org/project/yojenkins/">
  <img alt="PYPI Status" src="https://img.shields.io/pypi/status/yojenkins">
</a>

<a href="https://github.com/ismet55555/yojenkins/blob/main/LICENSE">
  <img alt="Licence" src="https://img.shields.io/pypi/l/yojenkins">
</a>

</p>


`yojenkins` is a cross-platform command line interface (CLI) tool to monitor, manage, and have fun with a Jenkins server. It makes it possible to interact with Jenkins server without using the browser based Jenkins UI.

This tool is able to be integrated into a script as middleware in order to automate Jenkins related tasks and enable Jenkins configuration as code.

> `yojenkins` will liberate you and your browser from the Jenkins Web UI

With `yojenkins` you can manage:

- **Authentication**: *Authentication structure similar to AWS CLI*
- **Server**: *Create, shutdown, view queue, and more*
- **User accounts**: *Create, delete, add/remove permission, and more*
- **Nodes/agents:** *Create, delete, shut down server, and more*
- **Credentials**: *Create, update, delete, list, and more*
- **Folders:** *Create items, delete items, disable, enable, and more*
- **Jobs:** *Create, delete, trigger, monitor, search, and more*
- **Builds:** *Monitor, abort, tail logs, follow logs, and more*
- **Stages:** *Get info, get logs, view steps, view status*
- **Steps:** *Get info*
- **Other tools and functions:** *Run groovy scripts remotely, run custom REST calls, setup a shared library, view command usage history, and more*




**NOTE:** *This project is in **pre-alpha** release phase. Please report any issues, odd behavior, or suggestions. Read more about the [release cycle](https://en.wikipedia.org/wiki/Software_release_life_cycle).*
See [Bug Reports](#bug-reports) and [Feature Requests](#feature-requests)

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

- **(Optional)** Start up a local Jenkins server using Docker
  - ```sh
    yojenkins server server-deploy
    ```

- Configure your first profile. Profiles are stored in the home directory in the `.yojenkins` directory
  - ```sh
    yojenkins auth configure
    ```

- Generate a Jenkins server API token and add it to your first profile
  - ```sh
    yojenkins auth token --profile <PROFILE NAME>
    ```

- Verify that you can access the Jenkins server
  - ```sh
    yojenkins auth verify
    ```
- Now start trying some things
  - ```sh
    Get sever info:       yojenkins server info
    Get your user info:   yojenkins auth user --pretty
    Search a job:         yojenkins job search some-job-name --fullname --yaml --list
    Monitor a build:      yojenkins build monitor some-job-name --latest --sound
    ```

# Installation

1. Install system dependencies for `simpleaudio` sound Python package for job and build monitor
   - | Platform           | Command                                                                        	|
     |------------------  |--------------------------------------------------------------------------------	|
     | MacOS and Windows  | Not needed                                                                     	|
     | Ubuntu             | `sudo apt update && apt-get install -y python3-dev python3-pip libasound2-dev` 	|
     | CentOS             | `sudo yum update && yum install -y python3-devel gcc alsa-lib-devel`           	|


2. Install `yojenkins`
    - **Option 1 (Recommended):** Install from Python Package Index (PYPI) using `pip`
      - ```bash
        pip install yojenkins
        ```

   - **Option 2:** Download all files from this GitHub repository and install using the included `setup.py`
     - ```bash
         python setup.py install
         ```

# Usage

Each top level command has sub-commands. For example, `yojenkins server` has sub-commands `server-deploy` and `server-start`. To see the sub-commands of a command, or to see the options of a command, use the `--help` option.

```txt
                        YOJENKINS (Version: 0.0.0)

  yojenkins is a tool that is focused on interfacing with Jenkins server from
  the comfort of the beloved command line.  This tool can also be used as a
  middleware utility, generating and passing Jenkins information or automating
  tasks.

  QUICK START:

    1. Configure yo profile:  yojenkins auth configure
    2. Add yo API token:      yojenkins auth token --profile <PROFILE NAME>
    3. Verify yo creds:       yojenkins auth verify
    4. Explore yojenkins

Options:
  -v, --version  Show the version
  --help         Show this message and exit.

Commands:
  account     Manage user accounts
  auth        Manage authentication and profiles
  build       Manage builds
  credential  Manage credentials
  folder      Manage folders
  job         Manage jobs
  node        Manage nodes
  server      Manage server
  stage       Manage build stages
  step        Manage stage steps
  tools       Tools and more
```

# Jenkins Plugin Requirements

If you are using `yojenkins` on a pre-existing Jenkins server, make sure that the following Jenkins plugin are installed for `yojenkins` to use all its functionalities. However, these plugins tend to be installed by default.

In order to check/install a plugin, go to *Manage Jenkins > Manage Plugins > Installed OR Available*

1. [Folders](https://plugins.jenkins.io/cloudbees-folder/) (cloudbees-folder)
2. [Next Build Number](https://plugins.jenkins.io/next-build-number/) (next-build-number)
3. [Promoted Builds](https://plugins.jenkins.io/promoted-builds/) (promoted-builds)
4. [Role-based Authorization Strategy](https://plugins.jenkins.io/role-strategy/) (role-strategy)
5. [GitHub Branch Source Plugin](https://plugins.jenkins.io/github-branch-source/) (github-branch-source)


# Local Jenkins Server Setup Using Docker

`yojenkins` offers an easy way to quickly set up a local Jenkins server within a Docker container. This server is setup and ready to go to tinker with `yojenkins`.

> **NOTE:** You must have Docker installed and running. See [Docker installation guide](dev_things/docker.md).

Run the following command to set up a local Jenkins server:
```bash
yojenkins server server-deploy
```

Use `--help` for available options, and use `--debug` to troubleshoot any issues.

&nbsp;

---

# Bug Reports

As with any other software, issues do come up during various usage scenarios that may not be accounted for during development and testing. **Help from real users is enormously helpful.**

Please report and bugs and odd behaviors with either of these:

- Online at [GitHub Issues](https://github.com/ismet55555/yojenkins/issues/new?assignees=&labels=&template=bug_report.md&title=)
-  `yojenkins tools bug-report`

If possible, please include the command that caused the issue, running it with the `--debug` option. For example, `yojenkins server server-deploy --debug`

Note, that your issue may already be in queue, so please check the project [FIXME](https://github.com/ismet55555/yojenkins/projects/2).

# Feature Requests

This is a very young project, and we are always looking for new features and improvements. Please feel free to open an issue and suggest a feature. Please be as specific as possible, and include as much information as possible.

- Online at [GitHub Feature Request](https://github.com/ismet55555/yojenkins/issues/new?assignees=&labels=&template=feature_request.md&title=)
- `yojenkins tools feature-request`

Note, your suggestion may be part of the Project plan, so be sure to check the [TODO](https://github.com/ismet55555/yojenkins/projects/1) to see if it is already planned.


# Contributing

This project is an on-going effort, slowly adding various features and improvements. If you would like to contribute, please fork the project, make your changes, and submit a pull request.

> **Any help, ideas, or user testing is much appreciated!**

There is definitely work to be done. If you don't happen to have a great genius idea for the next big change, or if you spot an issue you are able to fix, please checkout the [TODO](https://github.com/ismet55555/yojenkins/projects/1) and [FIXME](https://github.com/ismet55555/yojenkins/projects/2) or add your own ideas. For guides and information on how to get started and help out, check out the `dev_things` directory.

## Contributors

- **Ismet Handžić**: GitHub: [@ismet55555](https://github.com/ismet55555)


# Licence
This project is licensed under the *GNU General Public License Version 3* License. Please see the [LICENSE](LICENSE) file for details. Also a complete [history of this licence](https://en.wikipedia.org/wiki/GNU_General_Public_License).
