# Jenkins Plugin Requirements

If you are using `yojenkins` on a pre-existing Jenkins server, make sure that the
following Jenkins plugin are installed for `yojenkins` to use all its functionalities.
However, *these plugins tend to be installed by default.*

1. [Folders](https://plugins.jenkins.io/cloudbees-folder/) (cloudbees-folder)
2. [Next Build Number](https://plugins.jenkins.io/next-build-number/) (next-build-number)
3. [Promoted Builds](https://plugins.jenkins.io/promoted-builds/) (promoted-builds)
4. [Role-based Authorization Strategy](https://plugins.jenkins.io/role-strategy/) (role-strategy)
5. [GitHub Branch Source Plugin](https://plugins.jenkins.io/github-branch-source/) (github-branch-source)

In order to check if a Jenkins plugin is installed, or to install a plugin, you can:

- In the Jenkins web user interface, go to
    - **Manage Jenkins > Manage Plugins > Installed OR Available**
- `yojenkins server plugins --pretty --list`
