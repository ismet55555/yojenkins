# Usage

[TOC]

---


## Menu Overview and Navigation

The following is the main menu displayed when running `yojenkins --help`. 

```txt
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

Of course you can view the help menu for the sub-menu's commands by adding `--help`.
For example, `yojenkins server browser --help` will display the help menu for the `browser`

```txt
Usage: yojenkins server browser [OPTIONS]

  Open server home page in web browser

Options:
  --debug         Enable debug level log messages
  --profile TEXT  Authentication profile for command
  --help          Show this message and exit.
```


## Authentication

Effortless authentication is something that `yojenkins` can do for you. That is, once you have 
authentication profiles set up, it is not something you have to think about much while using `yojenkins`.

### Authentication Profiles

`yojenkins` has the ability to store and manage authentication profiles. That is, you are able to
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
server UI, or through `yojenkins`
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

Alternatively, you can manually edit the `~/.yojenkins/credentials` file directly. The file is in
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
    You can also manually fetch the API token form the Jenkins UI:

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



## General Operation

TODO



## Output Formatting

TODO



## Live Monitoring

TODO

### Job Monitor

TODO

### Build Monitor

TODO



## Tools

TODO


### Working with Command History

TODO

### Generic REST Server Requests

TODO


### Run Groovy Script on Server

TODO


### Setup Jenkins Shared Library

TODO





!!! tip "Remember"
    For help on any `yojenkins` command and sub-command, use the `--help` option

!!! tip "Remember"
    To troubleshoot any issues or to see what `yojenkins` is doing behind the scenes, use the `--debug` option



## Local Jenkins Server Setup Using Docker

`yojenkins` offers an easy way to quickly set up a local Jenkins server within a Docker container.
This containerized server is set up and ready to go to use to test `yojenkins`.

!!! warning "Warning"
    The locally containerized server set up using `server-deploy` is for development, training,
    demonstration, or testing purposes only. **Do not use this server for production use.**

!!! note "Note"
    For the locally containerized server to work, you must have Docker installed and running.
    See [Docker installation guide](docker_install.md) on how to install Docker.


### Deploying the Local Jenkins Server

Run the following `yojenkins` command to set up a local and containerized Jenkins server.

```bash
yojenkins server server-deploy
```

If this is the very first time running this command, it will take a minute or two to complete.
Any subsequent time will be faster since the base image has already been downloaded

Note that this command can be run without any specified options or arguments. All default
options should work out of the box. However, you can use the `--help` option to see all available
options in order to change any defaults.

Here are some examples of how to use the `server-deploy` command:

```bash
yojenkins server server-deploy --image-base jenkinsci/blueocean
yojenkins server server-deploy --admin-user ismet --password Abc123
yojenkins server server-deploy --config-file /path/to/config_as_code.yaml
```


### Tearing Down the Local Jenkins Server

In order to tear down the local and containerized Jenkins server, run the following `yojenkins` command:

```bash
yojenkins server server-teardown
```

Behind the scenes `yojenkins` holds a log file which outlines any active deployments.
When you run `server-teardown` it will remove the server deployment that was logged.

If there are any issues tearing down a running `yojenkins` deployed server, you can always
use `docker` to manually remove the server.
