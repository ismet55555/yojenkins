<p align="center">
  <img width="120" alt="portfolio_view" src="https://raw.githubusercontent.com/ismet55555/yojenkins/main/docs/source/logo_final.png">
</p>

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

<a href="https://github.com/ismet55555/yojenkins/actions/workflows/test-build-publish.yml">
  <img alt="Workflow" src="https://github.com/ismet55555/yojenkins/actions/workflows/test-build-publish.yml/badge.svg">
</a>

<h3 align="center">
<a href="https://www.yojenkins.com/installation/">Install Now!</a>
</h3>

</p>

**`yojenkins`** is a cross-platform command line interface (CLI) tool to monitor, manage, and deal with Jenkins server. It makes it possible to interact with a Jenkins server without using the browser based Jenkins UI.

This tool is able to be integrated into a script as middleware in order to automate Jenkins related tasks or enable Jenkins configuration as code.

**`yojenkins` will liberate you and your browser from the Jenkins Web UI**

With **`yojenkins`** you can manage:

- **Authentication**: _Authentication structure similar to AWS API_
- **Server**: _Create, shutdown, view queue, and more_
- **User accounts**: _Create, delete, add/remove permission, and more_
- **Nodes/agents:** _Create, delete, shut down server, and more_
- **Credentials**: _Create, update, delete, list, and more_
- **Folders:** _Create items, delete items, disable, enable, and more_
- **Jobs:** _Create, delete, trigger, monitor, search, and more_
- **Builds:** _Monitor, abort, tail logs, follow logs, and more_
- **Stages:** _Get info, get logs, view steps, view status_
- **Steps:** _Get info_
- **Other tools and functions:** _Run groovy scripts remotely, run custom REST calls, setup a shared library, view command usage history, and more_

_For a complete CLI command outline, see [section below](#complete-cli-outline)_

## :blue_book: Documentation

For all information and documentation, please visit [yojenkins.com](https://yojenkins.com)

## :movie_camera: Overview Video

This video presents an overview of `yojenkins`, while demonstrating a few basic funcitonalities and workflow.

<a target="_blank" rel="noopener noreferrer" href="https://youtu.be/w1p-eMzKuLE">
  <img width="35%" alt="overview_video" style="border:2px solid black;" src="https://img.youtube.com/vi/w1p-eMzKuLE/hqdefault.jpg">
</a>

## :ballot_box_with_check: Project Contact

If you happen to find any issues with this project or think of any features that you want to
request, see the following links:

- Read more about the [release cycle](https://en.wikipedia.org/wiki/Software_release_life_cycle).
- [Bug Reports](https://www.yojenkins.com/bug_report/)
- [Feature Requests](https://www.yojenkins.com/feature_request/)

## :heartbeat: Help this Project

This is a very young project and I am always looking for help in any way. If you like this project, please consider helping.

- For financial or marketing support options see [Support This Project!](https://www.yojenkins.com/support/).
- To contribute to this project, see [Contribute to This Project!](https://www.yojenkins.com/contribute/).

## :broken_heart: Similar Projects

If this project is not something you were were looking for, that ok, there are similar projects out there,
which each one with their own advantages and disadvantages.

- [Official Jenkins CLI](https://www.jenkins.io/doc/book/managing/cli/)
- [jenkins-cli](https://github.com/jenkins-zh/jenkins-cli)
- [jenni](https://github.com/m-sureshraj/jenni)
- [jenkins-job-cli](https://github.com/gocruncher/jenkins-job-cli)

## Complete CLI Outline

```txt
yojenkins
    |
    |-- account     Manage user accounts
    |     |--- create           Create a user account
    |     |--- delete           Delete a user account
    |     |--- info             Get user information
    |     |--- list             List all users
    |     |--- password-reset   Reset a user password
    |     |--- permission       Add or remove user permission
    |     |--- permission-list  List all available permissions
    |
    |
    |-- auth        Manage authentication and profiles
    |     |--- configure  Configure authentication
    |     |--- show       Show the local credentials profiles
    |     |--- token      Generate authentication API token
    |     |--- user       Show current user information
    |     |--- verify     Check if credentials can authenticate
    |     |--- wipe       Wipe all credentials for this device
    |
    |
    |-- build       Manage builds
    |     |--- abort    Abort build
    |     |--- browser  Open build in web browser
    |     |--- delete   Delete build
    |     |--- diff     Find difference between two builds
    |     |--- info     Build information
    |     |--- logs     Get build logs
    |     |--- monitor  Start monitor UI
    |     |--- rebuild  Rebuild a build with same parameters
    |     |--- stages   Get build stages
    |     |--- status   Build status text/label
    |
    |
    |-- credential  Manage credentials
    |     |--- config        Get credential configuration
    |     |--- create        Create new credentials
    |     |--- delete        Remove credentials
    |     |--- get-template  Cred. type template to create a cred.
    |     |--- info          Credential information
    |     |--- list          List credentials
    |     |--- move          Move a credential to another folder/domain
    |     |--- update        Reconfigure existing credentials
    |
    |
    |-- folder      Manage folders
    |     |--- browser     Open folder in web browser
    |     |--- config      Get folder configuration
    |     |--- copy        Copy an existing item
    |     |--- create      Create an item [folder, view, job]
    |     |--- delete      Delete folder or view
    |     |--- info        Folder information
    |     |--- items       List all items in folder
    |     |--- jobs        List all jobs in folder
    |     |--- search      Search folders by REGEX pattern
    |     |--- subfolders  List all subfolders in folder
    |     |--- views       List all views in folder
    |
    |
    |-- job         Manage jobs
    |     |--- browser       Open job in web browser
    |     |--- build         Build a job
    |     |--- build-exist   Check if build number exists
    |     |--- config        Get job configuration
    |     |--- create        Create a job
    |     |--- delete        Delete job
    |     |--- diff          Find difference between two jobs
    |     |--- disable       Disable job
    |     |--- enable        Enable job
    |     |--- info          Job information
    |     |--- last          Get previous build number
    |     |--- list          List all builds for job
    |     |--- monitor       Start monitor UI
    |     |--- next          Get next build number
    |     |--- queue-cancel  Cancel this job in queue
    |     |--- queue-check   Check if this job is in queue
    |     |--- rename        Rename job
    |     |--- search        Search jobs by REGEX pattern
    |     |--- set           Set the next build number
    |     |--- wipe          Wipe job workspace
    |
    |
    |-- node        Manage nodes
    |     |--- config            Get node configuration
    |     |--- create-ephemeral  Setup a local or remote ephemeral node
    |     |--- create-permanent  Setup a local or remote persistent node
    |     |--- delete            Delete a node
    |     |--- disable           Disable a node
    |     |--- enable            Enable a node
    |     |--- info              Node information
    |     |--- list              List all nodes
    |     |--- logs              Node logs
    |     |--- prepare           Prepare a remote machine to become a node
    |     |--- reconfig          Reconfigure the node
    |     |--- status            Node status
    |
    |
    |-- server      Manage server
    |     |--- browser          Open server home page in web browser
    |     |--- info             Server information
    |     |--- people           Show all people/users on server
    |     |--- plugins          Show plugin information
    |     |--- queue            Show current job build queues on server
    |     |--- quiet            Server quite mode enable/disable
    |     |--- reachable        Check if server is reachable
    |     |--- restart          Restart the server
    |     |--- server-deploy    Create a local development server (Docker)
    |     |--- server-teardown  Remove a local development server
    |     |--- shutdown         Shut down the server
    |
    |
    |-- stage       Manage build stages
    |     |--- info    Stage information
    |     |--- logs    Stage steps
    |     |--- status  Stage status text
    |     |--- steps   Get stage steps
    |
    |
    |-- step        Manage stage steps
    |     |--- info  Step information
    |
    |
    |-- tools       Tools and more
          |--- bug-report        Report a bug
          |--- docs              Open browser to the documentation
          |--- feature-request   Request a feature
          |--- history           Show detailed command usage history
          |--- rest-request      Send a generic Rest request to server
          |--- run-script        Run Groovy script on server, return result
          |--- shared-lib-setup  Set up a Jenkins shared library
```
