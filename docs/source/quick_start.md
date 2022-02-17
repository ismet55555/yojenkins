# Quick Start

The following is a quick start guide to get going with the `yojenkins` command line tool.
This guide assumes that `yojenkins` is installed and available on your system.

1. **(Optional)** Start up a containerized local Jenkins server using Docker
    - `yojenkins server server-deploy`
2. Configure your first profile. Profiles are stored in the home directory in `.yojenkins`
    - `yojenkins auth configure`
3. Generate a Jenkins server API token and add it to your first profile
    - `yojenkins auth token --profile <PROFILE NAME>`
4. Verify that you can access the Jenkins server
    - `yojenkins auth verify`
5. Now start trying some things ...

```sh
Get sever info:       yojenkins server info
Get your user info:   yojenkins auth user --pretty
Search a job:         yojenkins job search some-job-name --fullname --yaml --list
Monitor a build:      yojenkins build monitor some-job-name --latest --sound
```
