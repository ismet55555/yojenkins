# Notes


# General

- Check which profile is active
    - pick active
    - if none are active, ask
- If password is missing, ask


- In the configuration file there is a key to designate the active profile

- User command flow
    1. yo-jenkins
    2. server (command group)
    3. info (command group) (with options)
    4. YoJenkins (class)
    5. server_info (method)


# settings.json
```json
    "python.analysis.extraPaths": [
        "./yo_jenkins"
    ],
    "python.autoComplete.extraPaths": [
        "./yo_jenkins"
    ],
```

## Ideas

- yo-jenkins yo do <URL>
  - custom url send, see feature list

- yo-jenkins man
    - info
    - Check for updates
    - Report an issue
    - Request a feature



- Total log bytes indicator on monitor
- Log size option in logs -b, --bytes

- On creation and deletion of things have --dry-run flag
    to make sure the operation would works (THIS EVEN POSSIBLE?)
        - create
        - delete
        - abort
        - cancel

- Compare passed url with server url ???

- Add click command input validate functions: https://click.palletsprojects.com/en/7.x/options/#callbacks-for-validation

- Store last output into a temp file like .drop.temp

- Some type of stash for key-value info
    - How to plug in values?  Pipe?

- Pass list of items for any function to run
    - Example: yo-jenkins build info [ref1, ref2, ref3]
    - Get list back

- Input request recognition (last line in logs)
    - NOTE: Build status will change ... maybe a way to affirm or pick?

- Testing
    - pytest
    - need some kind of mock jenkins server
    - create, info, build, delete
    - folder, job, build

- Can we find a public jenkins server to test on?
    - Use terraform to spin up an image to test?
    - Use docker to spin up a server with pre-defined configs

- Run the tool inside docker
    - Not part of the tool, but part of the setup

- Create separate configuration files:
    - credentials.conf   -> when in home place into `./yo-jenkins` directory
    - yo-jenkins-conf

- HTML output of build results

- After creation, deletion, build start, etc return job name like docker (maybe if flag is set)

- Recursively show directories/items for specified folder
    - Something like tree


## STDIN PIPE
```python
for line in sys.stdin:
    line = line.strip()
    if line:
        messaging.post_message(destination_id, line, pre=pre, username=username)
```



## General Notes

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


