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

- Add click command input validate functions: https://click.palletsprojects.com/en/7.x/options/#callbacks-for-validation

- Store last output into a temp file like .drop.temp

- Add option flag to search for fullpath over name of folder/job

- Some type of stash for key-value info
    - How to plug in values?  Pipe?

- Item operation pass a list of items to run that function on

- Make `--version` work on top level menu

- Input request recognition (last line in logs)

- Generate and add link to blue ocean for build and stages
    - Need to check the plugin



- Add pytest testing
- Can we find a public jenkins server to test on?
    - Use terraform to spin up an image to test?

- Separate thread to execute function - Tested, works fine

- Create separate configuration files:
    - credentials.conf   -> when in home place into `./yo-jenkins` directory
    - yo-jenkins-conf

- PDF output of build results

- After creation, deletion, build start, etc return job name like docker (maybe if flag is set)


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





## Possible Commands

- `yo-jenkins build monitor <build address>`
    - pulls up curses window
    - desktop notification

