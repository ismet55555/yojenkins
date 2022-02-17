# Contribute to This Project

`yojenkins` is a Python project that is an on-going effort, slowly adding various features and improvements.
If you would like to contribute, please fork the project, make your changes,
and submit a pull request.

!!! tip "Big Thank You"
    **Any help, ideas, or user testing is much appreciated!**

There is definitely work to be done. If you spot an issue you are able to fix,
or if you are eying a open issue or feature request, feel free to submit some code.

For guides and information on how to get started and help out, check out the various
sections on this page.

[TOC]

---

## Roadmap

!!! note
    The roadmap is currently in flux and is yet to be refined

Please see the `TODO` and `FIXME` kanban board for this projects on GitHub

- [**TODO**](https://github.com/ismet55555/yojenkins/projects/1) - Any currently outstanding tasks
- [**FIXME**](https://github.com/ismet55555/yojenkins/projects/2) - Any known issues

## Forking and Locally Cloning Project

The purpose of forking this project GitHub repository is to create a local copy of the project,
make changes to it, and submit a pull request of your work into the original repository.

Here is a guide by GitHub on how to fork and clone a project:

- [Fork and Clone a GitHub Repository](https://docs.github.com/en/get-started/quickstart/fork-a-repo)



## Environment Setup

The following steps assume that you have successfully cloned the project and are in the
root directory of the project.

1. Add the system dependencies, if applicable

    | Platform          | Command                                                                        |
    | ----------------- | ------------------------------------------------------------------------------ |
    | MacOS and Windows | Not needed                                                                     |
    | Ubuntu            | `sudo apt update && apt-get install -y python3-dev python3-pip libasound2-dev` |
    | CentOS            | `sudo yum update && yum install -y python3-devel gcc alsa-lib-devel`           |

2.  Ensure Python is installed and is a compatible version for this project
    - `python --version`
    - If it is not, install it: [Guide](https://realpython.com/installing-python/)
3.  Ensure that `pip` is installed
    - `pip --version`
    - If it is not, install it: [Guide](https://pip.pypa.io/en/stable/installation/)
4.  Upgrade tooling and install `pipenv`
    - `python -m pip install --upgrade pip setuptools wheel virtualenv pipenv`
5. With `pipenv`, set up the development virtual environment
    - `pipenv sync --three --dev`
6. Get into (activate) the virtual environment
    - `pipenv shell`
7. Test if `yojenkins` starts up without any errors
    - `yojenkins --help`



## Making Changes

!!! tip "`git`"
    This project uses the ["trunk-based"](https://www.atlassian.com/continuous-delivery/continuous-integration/trunk-based-development)
    `git` version control workflow. Each time you make a change, you should create a new branch
    and push your changes to the `main` branch.

    These days you do not have to be a `git` terminal master in order to get going with a `git`
    source controlled project. Depending on your preferences, there are many visual UI-based `git`
    clients such as [GitHub Desktop](https://desktop.github.com/),
    [SourceTree](https://www.sourcetreeapp.com/), or even through the Visual Studio Code IDE.


1. Create a new `git` branch from the `main` branch
    - `git checkout main`
    - `git pull`
    - `git checkout -b <YOUR NEW GIT BRANCH NAME>`
2. Update your virtual environment
    - `pipenv sync --three --dev`
3. Activate/Enter the virtual environment
    - `pipenv shell`
4. **Make your changes to the project ...**
5. Run the changes
    - `yojenkins` - This works because the current package is marked as editable in `Pipfile`
    - `python yojenkins/__main__py` - This is effectively what is run when running `yojenkins`
6. Stage the changes
    - `git add .`
7. Run `pre-commit` (See section below)
    - `pre-commit run`
8. Stage and commit the changes
    - `git commit -m "<YOUR GIT COMMIT MESSAGE>"`
9. Once all your changes and commits are complete, increment and tag the build version of `yojenkins`
    - `bumpversion patch`
10. Push changes to your development branch
    - `git push origin <YOUR NEW GIT BRANCH NAME>`
11. On GitHub, open a new pull request into the original repository





## Adding New Dependencies

Sometimes a new Python dependency is required for the project. In these cases, you can add dependencies
as follows:

1. Add the dependency to the `Pipfile`
2. Lock the dependency, updating the `Pipfile.lock`
    - `pipenv lock --clear`
3. Update `requirements.txt` with the new dependency and its version
    - Typically you can search it inside `Pipfile.lock`

!!! caution
    Some dependencies are exclusive to a specific Operating system (ie. Windows).
    Make sure to specify these appropriately as seen with other dependencies.



## Formatting and Linting

Both, formatting and linting are standardized and automated using [`pre-commit`](https://pre-commit.com/).
`pre-commit` is a tool that runs a set of predefined tasks and checks on your code when you
run `git commit`.

This projects holds a `.pre-commit-config.yaml` file, which dictates which tasks are run.
Currently, this file outlines the following tasks and checks:

1. Remove any trailing whitespace
2. Fix end of the file with a newline
3. Check if Python docstrings are listed first
4. Check JSON file formatting
5. Check YAML file formatting
6. Check TOML file formatting
7. Check if tests have the right naming
8. Python Code Formatting (yapf)
9. Python Imports Sorting (isort)
10. Python Code Linting (pylint)

You can manually run these checks by running `pre-commit run`, or you can add the `pre-commit`
command to your `.git/hooks/pre-commit` file by running `pre-commit install`. This adding a
git hook is a good way to make sure your code is formatted and linted before you commit.

!!! note
    `pre-commit` will only run on files that have been staged. However, if you want to run
    `pre-commit` on the entire project, you can run `pre-commit run --all-files`

!!! caution "Note"
    Make sure you have the project's virtual environment activated before running the checks.

The workflow for running `pre-commit` checks is typically as follows:

1. Make and finish up code changes
2. Stage the changes with `git add .`
3. Run `pre-commit run`
4. Stage any changes made by `pre-commit`
5. Commit the staged changes with `git commit`



## Unit Testing

Currently, there are no unit tests. This big tech debt is mainly caused by
the the focus so far being on the development of `yojenkins` and its various features.

However, the outline of a unit test framework is in place. The directory `tests` holds the outline
of a [`pytest`](https://docs.pytest.org/) framework.

Adding unit tests to the various functions, classes, methods, and the CLI tool as a whole is
deeply needed.



## Documentation

This project uses `mkdocs` to generate documentation. `mkdocs` is a static site generator that is
used to generate documentation for this project. To learn more about `mkdocs`, check out its
[documentation](https://www.mkdocs.org/).

### Layout

In this project, all work related to documentation is inside the `docs` directory as follows:

```text
docs/
    |-- site/
    |-- source/
          |-- index.md
          |-- contributing.md
          |-- <etc>
    |-- mkdocs.yml
```

`site/` is the directory where the documentation will be generated.
Anything inside this directory is not touched by anyone directly.

`source/` is the directory where the documentation source files are located.
This directory holds all the files that will be edited and used to generate the documentation.

`mkdocs.yml` is the configuration file for `mkdocs`. Most content inside this file is
fairly constant except the `nav` section, which may changes if a new site is added.


### Live Server for Preview

While editing and working with the documentation, you may want to preview the documentation
in real time as you change it. `mkdocs` offers a live server feature that will automatically
rebuild the documentation when you save a file.

In order to start this live server

1. Open a terminal and navigate to the `docs` directory.
2. Inside `docs`, run the following command: `mkdocs serve`
3. Open a browser and navigate to http://127.0.0.1:8000 to actively view your changes


### Building the Documentation

The documentation is built using `mkdocs`, which will use the `source` directory and
the `mkdocs.yml` configuration file.

1. Open a terminal and navigate to the `docs` directory.
2. Inside `docs`, run the following command: `mkdocs build`
3. Watch out for any warnings or errors that may need to be fixed.

!!! note "Note"
    Currently the documentation is build manually using the `mkdocs` command. However, future plans
    adding this task to GitHub Actions to automate the build process.

### Deploying The Documentation to GitHub Pages

Deploying to GitHub Pages is a separate process where `mkdocs` will generate the documentation on
its own branch in the `yojenkins` repository under branch name `gh-pages`.

1. Open a terminal and navigate to the `docs` directory.
2. Inside `docs`, run the following command: `mkdocs gh-deploy --site-dir site --verbose --config-file mkdocs.yml`

## Visual Studio Code Setup (Optional)

Here included are some general suggestions for setting up your VS Code environment in order
to operate and contribute on this project. The main reason for including this section is to
encourage even beginner level developers to hopefully contribute to this project.

!!! note "Note"
    This entire section is a mare suggestions. Developers can be picky about their tools and
    everyone tends to have their own ways of doing things

### Extensions

- **Python** - General Python Language Support
- **Better TOML** - TOML Language Support
- **YAML** - YAML Language Support
- **XML** - XML Language Support
- **Markdown Preview Enhancements** - Live Markdown File Preview
- **Git Graph** - Clear view of git history
- **GitLens** - All kinds of useful git tools
- **Pylance** - Code assistance for Python
- **Visual Studio IntelliCode** - Code assistance for Visual Studio
- **Path Intellisense** - Auto-complete for paths in code
- **Docker** - Manage docker containers within VS Code

### VS Code Settings


#### Changing Settings

VS Code setting can be changed by editing the settings JSON file.

!!! caution "Note"
    When adding or removing JSON settings, do not forget to add commas and quotes
    appropriately as all the other settings are formatted in the JSON.

- **User Settings**
    - Settings applied globally to the user
    - To edit: `Ctrl + Shift + P` type: `Preferences: Open Settings (JSON)`
- **Workspace Settings**
    - Settings applied for a current workspace or project
    - To edit: `Ctrl + Shift + P` type: `Preferences: Open Workspace Settings (JSON)`

#### Settings to Change

- Show `.git` directory in the file tree
```json
    "files.exclude": {
        "**/.git": false
    }
```

- Increase terminal scroll back history
```json
    "terminal.integrated.scrollback": 5000,
```

- Increase the visibility of scroll bars
```json
    "editor.scrollbar.verticalScrollbarSize": 30,
    "editor.scrollbar.horizontal": "visible",
    "editor.scrollbar.horizontalScrollbarSize": 30,
```

- Add a Vertical Line at Line Length / Column Position
```json
    "editor.rulers": [100],
```


## Contributors

- **Ismet Handžić**: GitHub: [@ismet55555](https://github.com/ismet55555)
