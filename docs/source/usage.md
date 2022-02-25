# Usage

[TOC]

---


## CLI Basics

As with other command line interface (CLI) tools, the format of a typical `yojenkins` CLI
interaction looks like this:

```text
yojenkins <command> <subcommand> [options] [ARGUMENTS]
```

Here `[optoins]` are flags that do not have to be specified. For example, `--yaml` is a common
option. `[ARGUMENTS]` are documneted as uppder case and must be specified for the command.
For example, `yojenkins folder info [OPTIONS] FOLDER`, where folder name/URL are required.

To look up any command and sub-command help documentation, supplement the command with `--help`.
For example, `yojenkins auth configure --help`

!!! tip
    To troubleshoot any issues or to see what `yojenkins` is doing behind the scenes, use the `--debug` option



## Menu Overview

The following is the main menu displayed when running `yojenkins --help`.

```txt
❯ yojenkins --help

                        YOJENKINS (Version: 0.0.00)

  yojenkins is a tool that is focused on interfacing with a Jenkins server from
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

The sub-menus can be accessed by entering `yojenkins` followed by the sub-menu name.
For example, `yojenkins server` will display the server sub-menu.


```txt
❯ yojenkins server --help

Usage: yojenkins server [OPTIONS] COMMAND [ARGS]...

  Server Management

Options:
  --help  Show this message and exit.

Commands:
  browser          Open server home page in web browser
  info             Server information
  people           Show all people/users on server
  plugins          Show plugin information
  queue            Show current job build queues on server
  quiet            Server quite mode enable/disable
  reachable        Check if server is reachable
  restart          Restart the server
  server-deploy    Create a local development server using Docker
  server-teardown  Remove a local development server
  shutdown         Shut down the server
```

In turn, the sub-menu commands can be accessed by entering `yojenkins server` followed by the
sub-menu command name. For example, `yojenkins server browser` will open the Jenkins server
home page in the browser.

!!! note
    Some commands may be greyed out. These commands are not yet implemented.

Of course you can view the help menu for the sub-menu's commands by adding `--help`.
For example, `yojenkins server browser --help` will display the help menu for the `browser`

```txt
❯ yojenkins server browser --help

Usage: yojenkins server browser [OPTIONS]

  Open server home page in web browser

Options:
  --debug         Enable debug level log messages
  --profile TEXT  Authentication profile for command
  --help          Show this message and exit.
```



## Authentication

Effortless authentication is something that `yojenkins` can do for you. Once you have
authentication profiles set up, it is not something you have to think about much while using `yojenkins`.

### Authentication Profiles

`yojenkins` has the ability to store and manage authentication profiles. You are able to
store and manage different authentication credentials and use them to authenticate with the Jenkins
server as you need them, without having to enter them each time you need to interact with each
Jenkins server.

Different authentication profiles can be used for different Jenkins servers. For example, you can
have a profile for your local development server and a profile for your production Jenkins server.

You can also have different authentication profiles for different Jenkins user accounts. For example,
you may have a profile for an Jenkins administrator and a profile for a regular user.

Authentication profiles are stored in your local `~/.yojenkins` directory inside the `credentials`
file. The `credentials` file is a TOML file that contains a list of authentication profiles.
Remember that the `~` is a shorthand for the user's home directory.

!!! note
    Authentication profiles work very similar to that of AWS CLI, storing credentials locally inside
    the `~/.aws/credentials` file.

The `~/.yojenkins` directory and the `credentials` file can be manually created, however, `yojenkins`
will create these files for you if they do not exist.

An example of the contents of the `credentials` file looks like this:

```toml
[default]
jenkins_server_url = "https://cool-company.jenkins.com"
username = "id236"
api_token = "11fb9cb61d34edfe73f82763cf8879c79a"
active = true

[test-server]
jenkins_server_url = "http://localhost:8080"
username = "admin"
api_token = "55fg9cb61d34edfe83f82763cf8879c70v"
active = true
```

Note the different profile names in the `credentials` file. The first profile is `default`.
This is the profile that is used when no other profile is specified. If available, the `default` profile is
automatically activated when the `yojenkins` command is run.

The profile sections are as follows:

- `jenkins_server_url`: The full URL of the Jenkins server's home page.
- `username`: The username of the Jenkins user account.
- `api_token`: The API token of the Jenkins user account. This can be fetched through the Jenkins
server UI, or through `yojenkins`. If this has no value assigned to it, you will be prompted to
enter your password or API token at each command.
- `active`: Whether the profile can be used or not. This can be useful if you want to temporarily disable
a profile and ensure that you don't accidentally use it.

!!! caution
    The `api_token` can be the account password, however it is **highly recommended** that you use
    an API token. You do not want to store a Jenkins account password in plain text.

### Configuring a Profile

To use an authentication profile you need to first create a profile. For example, to create a profile
for your local development server, you can do one of the following two methods.

#### Run `yojenkins auth configure` *(Recommended)*

Running this command will prompt you for the required information, The prompt will look something
like the following:

```txt
❯ yojenkins auth configure

Credentials profile file found in current user home directory:
/home/user/.yojenkins/credentials
Adding a new profile to the current credentials profile file ...
Please enter the following information to add a profile:

[ OPTIONAL ] Enter PROFILE NAME (default):  demo-profile
[ REQUIRED ] Enter Jenkins SERVER BASE URL:  http://demo.jenkins.com
[ REQUIRED ] Enter USERNAME:  demo_user
[ OPTIONAL ] Enter API TOKEN:

Successfully configured credentials file
```

You can leave the API token blank since you can use `yojenkins` to add the API token later.

!!! caution
    The profile name is optional because if you do not enter anything for this item, the profile
    will be named `default` and overwrite any existing `default` profile with the same name.


#### Manually edit the `~/.yojenkins/credentials` file directly

You can manually edit the `~/.yojenkins/credentials` file directly. The file is in
TOML file format. Each profile will have the following information structure:

```toml
[demo-profile]
jenkins_server_url = "http://demo.jenkins.com"
username = "demo_user"
api_token = ""
active = true
```

The `active` field is used to determine whether the profile can be used or not. If you want to
temporarily disable a profile, you can set the `active` field to `false`.

You can leave the API token blank since you can use `yojenkins` to add the API token later.


#### Using a JSON file

If you need to configure profiles without terminal prompts or manually adding tokens to the
credentials file, you can use a predefined JSON file to configure profiles. This method allows
you to simultaneously configure multiple profiles at once.

The predefined JSON file can be specified with the `--auth-file` option.

The following is an example of the JSON file used to set up two authentication profiles:

```json
{
    "server_1": {
        "active": true,
        "api_token": "11fb9cb61d34edfe73f82763cf8879c79a",
        "jenkins_server_url": "https://server_1.jenkins.com",
        "username": "my_user_id_1"
    },
    "server_2": {
        "active": true,
        "api_token": "48fb9cb61d34edfe73f82763cf8879u79y",
        "jenkins_server_url": "https://server_2.jenkins.com",
        "username": "my_user_id_2"
    }
}
```

These profiles would then be configured with

```bash
yojenkins auth configure --auth-file my_auth_file.json
```


### Requesting and Storing API Tokens

`yojenkins` is able to request an API token from the Jenkins server to use for subsequent authentication
requests.

To simply generate and display the API token, you can run the following command. Note that `yojenkins`
does not reference a profile, so it will ask a few question to be able to generate the API token.

```txt
❯ yojenkins auth token

Enter desired API TOKEN NAME: demo-test
Enter Jenkins SERVER BASE URL: http://localhost:8080/
Enter Jenkins server USERNAME: admin
Enter "admin" PASSWORD:

55d8c325c876fake58d61274d41744bc0d
```

More conveniently, you can generate an API token using the information stored in a authentication
profile and subsequently store the new API token inside an existing authentication profile.
The following command will request a new API token from the server and store it within the
`default` under the `api_token` key.
```txt
❯ yojenkins auth token --profile default

Enter "admin" PASSWORD:

success
```


!!! tip
    You can also manually fetch the API token from the Jenkins UI:

    1. Click on your username in the top right corner of the Jenkins UI
    2. Click on the *"Configure"* button in the menu on the right
    3. In the *"API Token"* section, click *"Add new Token"*
    3. Copy the generated API token and paste it into the `api_token` field
    in the `~/.yojenkins/credentials` file




### Order of Precedence Specifying Profiles

Each time `yojenkins` is run, it will look for a way to determine which authentication profile to use.
The order of precedence of looking for a profile specifier is as follows:

1. `--profile` command argument
    - The `--profile` command argument specifies the profile name, the profile specified by the argument will be used.
    - *Example:* `yojenkins server info --profile my-profile`
2. Environment variable `YOJENKINS_PROFILE`
    - *Example:* `export YOJENKINS_PROFILE=my-profile`
3. "default" profile in the `~/.yojenkins/credentials` file
4. First active profile in the `~/.yojenkins/credentials` file

If none of the above are satisfied, `yojenkins` will prompt for Jenkins server credentials.



## Output Formatting

Often times you will want to see the output of a command in a different format.
For example, you may want to see the output of a `yojenkins server info` command in a different
format than the default.

The following output formats are supported:

- [JSON](https://www.json.org/json-en.html)
- [YAML](https://yaml.org/)
- [TOML](https://toml.io/en/)
- [XML](https://www.w3.org/XML/)

Any output with any format can be supplemented with `--pretty` to make the output more readable.

Here are some examples of how different output formats looks like using the `yojenkins account list` command:

**Default**
```text
❯ yojenkins account list
[{"id": "admin", "me": true, "fullName": "admin", "description": "", "absoluteUrl": "http://localhost:8080/user/admin", "userFolder": {"directory": true, "file": false, "freeSpace": 18083065856, "invalid": false, "canonicalPath": "/var/jenkins_home/users/admin_6787401061636913615", "usableSpace": 16512360448, "hidden": false, "totalSpace": 30525820928, "path": "/var/jenkins_home/users/admin_6787401061636913615", "name": "admin_6787401061636913615", "prefixLength": 1, "absolute": true, "absolutePath": "/var/jenkins_home/users/admin_6787401061636913615", "parent": "/var/jenkins_home/users"}, "isAdmin": true, "isManager": true, "isSystemRead": true, "canRead": true, "canWrite": true, "canUpdate": true, "canDelete": true, "canConfigure": true, "authorities": [], "lastGrantedAuthoritiesChanged": "Mon Nov 15 14:19:08 UTC 2021"}]
```

**Pretty Formatting**
```text
❯ yojenkins account list --pretty

[
    {
        "absoluteUrl": "http://localhost:8080/user/admin",
        "authorities": [],
        --- SNIP ---
        "lastGrantedAuthoritiesChanged": "Mon Nov 15 14:19:08 UTC 2021",
        "me": true,
        "userFolder": {
            "absolute": true,
            "absolutePath": "/var/jenkins_home/users/admin_6787401061636913615",
            --- SNIP ---
            "totalSpace": 30525820928,
            "usableSpace": 16512339968
        }
    }
]
```

**YAML**
```text
❯ yojenkins account list --yaml

- absoluteUrl: http://localhost:8080/user/admin
  authorities: []
  --- SNIP ---
  lastGrantedAuthoritiesChanged: Mon Nov 15 14:19:08 UTC 2021
  me: true
  userFolder:
    absolute: true
    absolutePath: /var/jenkins_home/users/admin_6787401061636913615
    --- SNIP ---
    totalSpace: 30525820928
    usableSpace: 16620826624
```

**TOML**
```text
❯ yojenkins account list --toml

[[item]]
id = "admin"
me = true
--- SNIP ---
authorities = []
lastGrantedAuthoritiesChanged = "Mon Nov 15 14:19:08 UTC 2021"

[item.userFolder]
directory = true
file = false
freeSpace = 18191482880
--- SNIP ---
absolutePath = "/var/jenkins_home/users/admin_6787401061636913615"
parent = "/var/jenkins_home/users"
```

**XML**
```text
❯ yojenkins account list --xml --pretty

<?xml version="1.0" ?>
<None>
        <item>
                <id>admin</id>
                <me>True</me>
                <fullName>admin</fullName>
                <description/>
                <absoluteUrl>http://localhost:8080/user/admin</absoluteUrl>
                <userFolder>
                        <directory>True</directory>
                        --- SNIP ---
                        <absolutePath>/var/jenkins_home/users/admin_6787401061636913615</absolutePath>
                        <parent>/var/jenkins_home/users</parent>
                </userFolder>
                <isAdmin>True</isAdmin>
                --- SNIP ---
                <authorities/>
                <lastGrantedAuthoritiesChanged>Mon Nov 15 14:19:08 UTC 2021</lastGrantedAuthoritiesChanged>
        </item>
</None>
```


## Live Monitoring

Sometimes you would like to keep a watch on a Job, monitoring the status of its builds, or a
specific Build, monitoring its steps or status. `yojenkins` makes this possible with a CLI-based
user interface for job and build monitoring.

### Job Monitor

`yojenkins` offers a CLI based user interface for monitoring jobs. The job monitor will display
the status of all past and current build of the job.

In addition, the job monitors offers some job actions that can be activated via shortcut keys.

*TODO: Complete this section*

```bash
yojenkins job monitor <JOB>
```

### Build Monitor

`yojenkins` offers a CLI based user interface for monitoring individual builds. This build monitor
will display some basic information about the build, including build status.

In addition, the build monitor offers some build actions that can be activated via shortcut keys.

*TODO: Complete this section*

```bash
yojenkins build monitor <JOB> --latest --sound
```



## Tools

### Command History

By default, each time you run a `yojenkins` command, that command is logged to the `~/.yojenkins/history` file.
If the file does not exist, it will be created.

This file is essentially a JSON file which holds the following meta data for each command:

1. The profile used for the command
2. `yojenkins` path
3. Command arguments
4. Timestamp
5. Formatted datatime
6. The version of the `yojenkins` used to run the command

To show the history of commands, run `yojenkins tools history`. To only show the history of a
specific profile, run `yojenkins tools history --profile <PROFILE NAME>`.

Here is a sample output of the `yojenkins tools history` command:

```text
❯ yojenkins tools history

[default] [Tuesday, December 28, 2021 10:34:58] [v0.0.00] - yojenkins server info --debug
[default] [Tuesday, December 28, 2021 10:35:54] [v0.0.00] - yojenkins account list
[default] [Tuesday, December 28, 2021 10:36:15] [v0.0.00] - yojenkins credential get-template user-pass --json --pretty
[demo-profile] [Tuesday, December 28, 2021 10:38:45] [v0.0.00] - yojenkins account list
[demo-profile] [Tuesday, December 28, 2021 10:39:05] [v0.0.00] - yojenkins server info
```

Clearing the entire `yojenkins` history file, run `yojenkins tools history --clear`.


### Generic REST Server Requests

Sometimes `yojenkins` does not support a specific request to the server. For example, if there is
a new or complex REST request you may want to use, you can use the `yojenkins tools rest-request` command

The convenience of this command is that it will automatically use your authentication profile to
make the request. It will know to use the host, username, and password from your authentication profile.

For example, given the following authentication profile:

```toml
[default]
jenkins_server_url = "https://cool-company.jenkins.com"
username = "id236"
api_token = "11fb9cb61d34FAKE73f82763cf8879c79a"
active = true
```

The command `yojenkins tools rest-request "me/api/json"` will make a `GET` request to the Jenkins
server at `http://localhost:8080/me/api/json` using the username and API token from the
authentication profile.

This command supports the following options:

- `--request-type` - Type of REST request. Default is `GET`.
- `--raw` - If set, the response will be printed as raw text. The response will not be parsed as JSON.
- `--clean-html` - If set, the response will be cleaned of HTML tags. This is useful if the response is in HTML format and you only want the content.



### Run Groovy Script on Server

Often times you want to run a Groovy script on the Jenkins server. The `yojenkins tools run-script`
command allows you to do just that.

This may be useful for Jenkins administrative tasks or simply running Groovy test scripts and tutorials.

You can specify the Groovy script by using one of the following options:

1. `--text <SCRIPT TEXT>`
    - The Groovy script is specified as a string within the command.
    - *Example:* `yojenkins tools run-script --text 'println("Hello fun world")'`
2. `--file <SCRIPT FILE PATH>`
    - The Groovy script is specified as a file path.
    - *Example:* `yojenkins tools run-script --file /path/to/script.groovy`

!!! attention
    In order to run a Groovy script, you must have the appropriate permissions on the Jenkins server
    for the user account you are using.

### Setup Jenkins Shared Library

Jenkins allows users to share Groovy code libraries between jobs and pipelines. This is useful
in that projects and pipelines will often share the same code. For example, a piece of
code used to report test results may be used in more than one pipeline without copy-pasting
it into each pipeline. [Shared libraries](https://www.jenkins.io/doc/book/pipeline/shared-libraries/)
are a way to share code between projects and pipelines.

!!! danger
    Jenkins sharable libraries available to any Pipeline jobs running on this system. These libraries will
    be fully trusted, meaning they run code without “sandbox” restrictions and may use @Grab.
    So be careful what code is being added to a Jenkins shared library.

`yojenkins` provides a command to setup a shared library using the following command:

```text
yojenkins tools shared-lib-setup
```

This command provides options to specify shared library setup options such as the git repository
in which the shared library is stored, git branch name, and if the shared library is loaded
implicitly.

*As of now, the only git repository that is supported by `yojenkins` is GitHub.*



## Local Jenkins Server Setup Using Docker

`yojenkins` offers an easy way to quickly set up a local Jenkins server within a Docker container.
This containerized server is set up and ready to go to use to test `yojenkins`.

!!! warning "Warning"
    The locally containerized server set up using `server-deploy` is for development, training,
    demonstration, or testing purposes only. **Do not use this server for any production environments.**

!!! note "Note"
    For the locally containerized server to work, you must have Docker installed and running.
    See [Docker installation guide](docker_install.md) on how to install Docker.


### Deploying the Local Jenkins Server

Run the following `yojenkins` command to set up a local and containerized Jenkins server.

```bash
yojenkins server server-deploy
```

If this is the very first time running this command, it will take a minute or two to complete.
Any subsequent time will be faster since the base image has already been downloaded.
This initial lag is due to the Docker image being downloaded and built.

Note that this command can be run without any specified options or arguments. All default
options should work out of the box. However, you can use the `--help` option to see all available
options in order to change any defaults.

Here are some examples of how to use the `server-deploy` command:

- Use the Blue Ocean Jenkins Docker base image
    - `yojenkins server server-deploy --image-base jenkinsci/blueocean`
- Change the default username and password
    - `yojenkins server server-deploy --admin-user ismet --password Abc123`
- Use a different Jenkins configuration as code file
    - `yojenkins server server-deploy --config-file /path/to/config_as_code.yaml`
- Use a custom list of plugins to create a Jenkins server
    - `yojenkins server server-deploy --plugins-file /path/to/plugins.txt`


### Tearing Down the Local Jenkins Server

In order to tear down the local and containerized Jenkins server, run the following `yojenkins` command:

```bash
yojenkins server server-teardown
```

Behind the scenes `yojenkins` holds a log file which outlines any active deployments, its image used,
container created, volume created, etc. When you run `server-teardown` it will remove the server deployment that
was logged and the log file itself.

If there are any issues tearing down a running `yojenkins` deployed server, you can always
use `docker` to manually remove the stop and remove the server container.

```text
docker container ls
docker kill <CONTAINER ID>
docker container rm <CONTAINER ID>
```
