# Bug Report



As with any other software, issues do come up during various usage scenarios
that may not be accounted for during development and testing.
**Help from real users is enormously helpful.**

Please report bugs and odd behaviors with:

- Online at [GitHub Issues](https://github.com/ismet55555/yojenkins/issues/new?assignees=ismet55555&labels=bug%2Ctriage&template=bug_report.yml&title=%5BBug%5D%3A+)
- `yojenkins tools bug-report`


## Include `--debug` Output

If possible, when reporting a bug, please include the command that caused
the issue in debug mode. You can do this by running the command
with the `--debug` option. This will allow for clearer communication of what was going on
and a somewhat easier time resolving the issue.

For example, below is the output of a failed `yojenkins` command in debug mode.

**Command**

```
yojenkins server info --debug
```

**Terminal Output**

```text
[ LOGGING LEVEL ] : DEBUG

[  TIME  ] [ MS ] [FILENAME              :  LN] MESSAGE
---------------------------------------------------------------------------
[18:49:09] [505 ] [cli_utility.py          :  64] Tool version: 0.0.00
[18:49:09] [506 ] [cli_utility.py          :  76] System information:
[18:49:09] [506 ] [cli_utility.py          :  77]     - System:    Linux
[18:49:09] [506 ] [cli_utility.py          :  78]     - Release:   5.11.0-43-generic
[18:49:09] [506 ] [cli_utility.py          :  79]     - Version:   #47~20.04.2-Ubuntu SMP Mon Dec 13 11:06:56 UTC 2021
[18:49:09] [506 ] [cli_utility.py          :  80]     - Machine:   x86_64
[18:49:09] [506 ] [cli_utility.py          :  81]     - Processor: x86_64
[18:49:09] [506 ] [cli_utility.py          :  82]     - Python:    3.8.10
[18:49:09] [506 ] [cli_utility.py          :  83]     - In Docker: False
[18:49:09] [507 ] [cli_utility.py          :  84]     - Bundled:   False
[18:49:09] [513 ] [utility.py              :  94] Loading specified local .json file: '/home/ismet/.yojenkins/history' ...
[18:49:09] [515 ] [utility.py              : 106] Successfully loaded local .json file
[18:49:09] [516 ] [cli_utility.py          : 246] Logging command to command history file: "/home/ismet/.yojenkins/history" ...
[18:49:09] [523 ] [rest.py                 :  32] Starting new requests session (Type: FuturesSession) ...
[18:49:09] [524 ] [auth.py                 : 334] Successfully found credential file "credentials" found in user configuration directory: /home/ismet/.yojenkins
[18:49:09] [524 ] [utility.py              :  94] Loading specified local .toml file: '/home/ismet/.yojenkins/credentials' ...
[18:49:09] [525 ] [utility.py              : 106] Successfully loaded local .toml file
[18:49:09] [525 ] [auth.py                 : 371] Number of listed profiles found: 4
[18:49:09] [526 ] [auth.py                 : 376] Ignoring profiles that do not have at least the following keys: jenkins_server_url, username ...
[18:49:09] [526 ] [auth.py                 : 380]     - Profile 1 of 2: "default" - OK
[18:49:09] [526 ] [auth.py                 : 380]     - Profile 2 of 2: "testing" - OK
[18:49:09] [526 ] [auth.py                 : 403] Argument "--profile" was not specified
[18:49:09] [526 ] [auth.py                 : 418] Environmental Variable "YOJENKINS_PROFILE" not set
[18:49:09] [526 ] [auth.py                 : 426] Successfully found "default" profile in the configuration file
[18:49:09] [527 ] [auth.py                 : 447] The following profile has been loaded:
[18:49:09] [527 ] [auth.py                 : 448]     - Profile:             default
[18:49:09] [527 ] [auth.py                 : 449]     - Jenkins Server URL:  http://localhost:8080
[18:49:09] [527 ] [auth.py                 : 450]     - Username:            admin
[18:49:09] [527 ] [auth.py                 : 502]     - API Token:           **********************************
[18:49:09] [527 ] [rest.py                 :  98] Checking if server is reachable: "http://localhost:8080/login" ...
[18:49:09] [528 ] [rest.py                 : 157] Request URL: http://localhost:8080/login
[18:49:09] [533 ] [rest.py                 : 221] Failed to make request. Exception: HTTPConnectionPool(host='localhost', port=8080): Max retries
exceeded with url: /login (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x7effbfcd6c40>: Failed to establish a new
connection: [Errno 111] Connection refused'))
[18:49:09] [533 ] [rest.py                 : 110] Failed. Server cannot be reached or is offline

Jenkins server connection failed (Server: http://localhost:8080)
Possible causes:
  - Wrong Jenkins server URL: http://localhost:8080
  - Network/Internet is down
  - Server container is down
Possible solutions:
   - Fix yo network connection to server
   - Check if the server container or container engine is up and running
```


!!! danger
    The `--debug` option is designed such that it will not expose any sensitive information, however
    please make sure that you censor any shown information that you do not want appear in public!
