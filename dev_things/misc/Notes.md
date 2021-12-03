# Notes

- CLI Guidelines: https://clig.dev/

- Shared library example: https://github.com/DigiaFactory/automated-jenkins-pipeline/blob/master/jenkins/init.groovy.d/40-shared-libraries.groovy

- Look into junit XML format for testing results

- Use existing jenkins-python module as much as possible!

- build_info (/api/json) will give {}?????

- `<URL>/api/json` is different than `<URL>/wfapi/describe`
- `<URL>/wfapi/describe` will show stages

- python module python-jenkins ".build_job()" FIX:
  - FIXED BY USING REQUESTS !!!!
  - jenkins_api_test/env/lib/python3.8/site-packages/jenkins/__init__.py
  - Line 378
  - SHOULD BE: if self.crumb and isinstance(req.headers, dict):
  - Script to fix this after pip install?  install script?
  - Consider replacing the errored thing (build or remove) with requests call
  - Create a Pull request



- yojenkins server server-deploy
  - Output progress, progress bar ... look in to click add-on


- Job - Create
  - Move to both folder/job and job menu
  - Blank job
  - Create a job using config.xml
  - Option for config.json


- Job
  - Add on single bash or powershell script
  - RUN SCRIPT: https://www.jenkins.io/doc/book/managing/script-console/
  - Give



- CLI Testing using click:
  - https://github.com/cdeil/python-cli-examples/blob/master/click/greet/test_cli.py

- Logo!

- look into faster json encoding and decoding:
  - https://github.com/ultrajson/ultrajson

- server
  - Run a groovy script

- Look into scrolling
  - https://docs.python.org/2/library/curses.html#curses.window.scroll

- Job Monitors
  - Job queue check

- Job monitor sound
  - New job arrives - halo sound

- Build and Job Monitor
  - I key to stop monitor and output job/build info in yaml format

- Build Monitor:
  - L - Build logs
    - L - All logs output
    - S - For certain stage - need a way to pick? (enter text for now?)
    - F - Switch to follow logs

- For temporary message, look into
  threading timer
  - t = threading.Timer(30.0, my_function)
  - maybe itertools.cycle((True, False))

- Folder combine the following:
  - items
  - jobs
  - subfolders
  - views

- Folder
  - View - delete

- __main__.py
  - sort in alphabetical order
  - Split into separate files and just import the files (will this work with click?)

- Format everything
  - yapf

- Add pre-commit hook on the code
  - https://github.com/google/yapf/tree/main/plugins

- In monitor, D key - Debug curses stats
  - elapsed loop time
  - curses.boudrate
  - ... need at least like 4
  - Find a way to show user error messages

- Curses scrolling:
  - Build Monitor - Stages
  - Job Monitor - Builds
  - Folder Monitor - Jobs


- Clean sensitive data fro repo history
  - https://www.cidean.com/blog/2019/clean-sensitive-files-from-git-repo/
  - https://stackoverflow.com/questions/4110652/how-to-substitute-text-from-files-in-git-history

- Change the username and email for past commits:
  - https://stackoverflow.com/questions/2919878/git-rewrite-previous-commit-usernames-and-emails
  - https://docs.github.com/en/github/setting-up-and-managing-your-github-profile/managing-contribution-graphs-on-your-profile/why-are-my-contributions-not-showing-up-on-my-profile#contributions-that-are-counted

- yojenkins auth wipe [HOLD OFF, DO LATER]

- Waiting spinning thingy [ HOLD OFF, DO LATER ]
  - OR click progress bar: https://click.palletsprojects.com/en/7.x/utils/#showing-progress-bars

- Add "ey-yo" to "step" -> "'sup" ASCII sign [ HOLD OFF, DO LATER ]
  - yojenkins yo ey-yo



## Zipping up stuff
### Zip For Moving
```
ZIP_NAME='a-6.zip' && \
zip -r $ZIP_NAME ./yojenkins -x \
    "**/.git/*" \
    "**/.VSCodeCounter/*" \
    "**/env/*" \
    "**/__pycache__/*" \
    "**/*.html" \
    "**/*.sqlite" \
    "**/*.log" && \
    du -hs $ZIP_NAME
```

### Zip for Testing
```
ZIP_NAME='for_testing.zip' && \
zip -r $ZIP_NAME ./yojenkins -x \
    "**/.git/*" \
    "**/.VSCodeCounter/*" \
    "**/env/*" \
    "**/__pycache__/*" \
    "**/*.html" \
    "**/*.sqlite" \
    "**/*.log" \
    "**/misc/*" \
    "**/test/*" \
    "**/.vscode/*" \
    "README.md" && \
    du -hs $ZIP_NAME
```

---

# References

- GitHub - https://github.com/jenkinsci

- Pipeline Stage View Plugin - https://github.com/jenkinsci/pipeline-stage-view-plugin/tree/master/rest-api

- API (General) - https://www.jenkins.io/doc/book/using/remote-access-api/

- Python package: python-jenkins

  - https://python-jenkins.readthedocs.io/en/latest/api.html
  - https://python-jenkins.readthedocs.io/en/latest/

- Python audio playing: https://pythonbasics.org/python-play-sound/

- Blessed: https://github.com/jquast/blessed
- Blessings: https://github.com/erikrose/blessings

- Click

  - Options - https://click.palletsprojects.com/en/7.x/options/#
  - Parameters
    - https://click.palletsprojects.com/en/7.x/parameters/
    - Extended list: https://github.com/click-contrib/click_params
  - Context - https://click.palletsprojects.com/en/7.x/api/?highlight=context#click.Context
  - Accepting passwords

    - https://pymbook.readthedocs.io/en/latest/click.html#super-fast-way-to-accept-password-with-confirmation
    - https://click.palletsprojects.com/en/7.x/options/#password-prompts

  - Changing Options for click

    - https://stackoverflow.com/questions/48391777/nargs-equivalent-for-options-in-click

  - Help menu colors - https://github.com/click-contrib/click-help-colors
  - Did you mean hinting - https://github.com/click-contrib/click-didyoumean
  - Click command completion
    - https://github.com/click-contrib/click-completion
    - Run a quick python code to set this up on the system?
  - Extended parameter list - https://github.com/click-contrib/click_params
  - Aliases for commands - https://github.com/click-contrib/click-aliases
  - Spinner for waiting (maybe better one out there) - https://github.com/click-contrib/click-spinner

  - Jenkins stage view plug in: https://github.com/jenkinsci/pipeline-stage-view-plugin/blob/master/rest-api/README.md
