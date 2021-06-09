# TODO

- *BUG FIXES*

================================================

- yo-jenkins server server-deploy
  - Output progress, progress bar ... look in to click add-on


- Job - config
  - Output the config.xml file
  - Option for config.json

- Folder - config
  - mimic folder config

- Job - Create
  - Move to both folder/job and job menu
  - Blank job
  - Create a job using config.xml
  - Option for config.json


- Job
    - Add on single bash or powershell script
    - RUN SCRIPT: https://www.jenkins.io/doc/book/managing/script-console/



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

- Concurrent requests for stage logs
    - ALREADY WORKS? - TEST ...
    - Separate monitoring object?
    - Use for stage logs

- Look into partially downloading logs
    - specify headers
        - Byte range: 14.5: https://stackoverflow.com/questions/23602412/only-download-a-part-of-the-document-using-python-requests
        - Other:
            - https://www.w3.org/Protocols/rfc2616/rfc2616-sec14.html
        
- Maybe probe log files the file first for size?
    - If large, can we divide it up?
    - https://stackoverflow.com/questions/41546386/check-if-a-large-file-exists-without-downloading-it

- Clean sensitive data fro repo history
    - https://www.cidean.com/blog/2019/clean-sensitive-files-from-git-repo/
    - https://stackoverflow.com/questions/4110652/how-to-substitute-text-from-files-in-git-history

- Change the username and email for past commits:
    - https://stackoverflow.com/questions/2919878/git-rewrite-previous-commit-usernames-and-emails
    - https://docs.github.com/en/github/setting-up-and-managing-your-github-profile/managing-contribution-graphs-on-your-profile/why-are-my-contributions-not-showing-up-on-my-profile#contributions-that-are-counted

- Use .yo-jenkins directory in home instead of just a file

- yo-jenkins auth wipe [HOLD OFF, DO LATER]

- Waiting spinning thingy [ HOLD OFF, DO LATER ]
    - OR click progress bar: https://click.palletsprojects.com/en/7.x/utils/#showing-progress-bars

- Add "ey-yo" to "step" -> "'sup" ASCII sign [ HOLD OFF, DO LATER ]



# Zipping up stuff
## Zip For Moving
ZIP_NAME='a-6.zip' && \
zip -r $ZIP_NAME ./yo-jenkins -x \
    "**/.git/*" \
    "**/.VSCodeCounter/*" \
    "**/env/*" \
    "**/__pycache__/*" \
    "**/*.html" \
    "**/*.sqlite" \
    "**/*.log" && \
    du -hs $ZIP_NAME

## Zip for Testing
ZIP_NAME='for_testing.zip' && \
zip -r $ZIP_NAME ./yo-jenkins -x \
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


# Docstring format

    """<SHORT DESCRIPTION>

    Details: <DETAILED DESCRIPTION>

    Args:
        param1 : This is the first param.
        param2 : This is a second param.

    Returns:
        This is a description of what is returned.
    """


### Monitoring

- Predefined monitoring file
    - .monitor
        - per profile (like aws)
    - Defines what to monitor
        - jobs
        - stages
        - builds



### Configuring Profile


1. Add explicity --json flag even though it is default
2. Folders


RULE
1. NEED .yo-jeknins.conf file to run command!



Reading the profile
1. If no yo-jenkins.conf file is present, run prompts to create profile
    - yo-jenkins auth configure ---> default
    - yo-jenkins auth configure --profile test-jenkins  ----> test jenkins
2. If "default" profile is there, use it
3. If no default profile is there
    - if one profile is in config, use it
    - if multiple profile is in config, error out
3. If YOJENKINS_PROFILE is defined, use it
    - must match what is in the config file


#### Checking profile order
Profile Picking

1. --profile specified
        - No matter if active or not
        - If not found -> error

2. YOJENKINS_PROFILE env var set
        - No matter if active or not
        - If not found -> error

3. "default" profile
        - If not active -> move on
        
4. Only listed profile that is active

If no specified, default, or active profile -> error

