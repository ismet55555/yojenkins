# Usage

[TOC]

---

!!! tip "Remember"
    For help on any `yojenkins` command and sub-command, use the `--help` option

!!! tip "Remember"
    To troubleshoot any issues or to see what `yojenkins` is doing behind the scenes, use the `--debug` option



## Local Jenkins Server Setup Using Docker

`yojenkins` offers an easy way to quickly set up a local Jenkins server within a Docker container.
This containerized server is set up and ready to go to tinker with `yojenkins`.

!!! warning "Warning"
    The locally containerized server set up using `server-deploy` is for development, training, or
    testing purposes only. **Do not** use this server for production use.

!!! note "Note"
    You must have Docker installed and running.
    See [Docker installation guide](dev_things/docker.md) on how to install Docker.


Run the following `yojenkins` command to set up a local and containerized Jenkins server:

```bash
yojenkins server server-deploy
```

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
