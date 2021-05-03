# TODO

- Bug Fixes

- Find a way to show user error messages

- Concurrent requests
    - grequests?
    - Separate monitoring object?
    - Use for stage logs

- Look into partially downloading logs
    - specify headers
        - Byte range: 14.5: https://stackoverflow.com/questions/23602412/only-download-a-part-of-the-document-using-python-requests
        - Other:
            - https://www.w3.org/Protocols/rfc2616/rfc2616-sec14.html
        
 - Saving logs to file: 
    - https://stackoverflow.com/questions/16694907/download-large-file-in-python-with-requests
    - Streaming big files: https://www.geeksforgeeks.org/downloading-files-web-using-python/
        - maybe probe the file first?
            - https://stackoverflow.com/questions/41546386/check-if-a-large-file-exists-without-downloading-it




## ZIP IT UP
zip -r b.zip /Users/ezg822/Projects/Personal/yo-jenkins -x \
    "**/.git/*" \
    "**/.VSCodeCounter/*" \
    "**/env/*" \
    "**/__pycache__/*" && \
    du -hs b.zip



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

- Monitor a running build

- Seperate class
    - Monitoring thread
    - Curses rendering
        - What layout?
        - Simple text at the beginning
    - Log text box


### Configuring Profile


1. Add explicity --json flag even though it is default
2. Folders


RULE
1. NEED .yo-jeknins.conf file to run command!




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

