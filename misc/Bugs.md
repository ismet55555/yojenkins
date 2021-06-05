# BUGS

--------------------------------------------------

with pipenv on `python yo_jenkins/__main__.py` will give error:
    - Maybe related to the previoiusly missing `__init__.py`?
    - Try without `.` now?
```
Traceback (most recent call last):
  File ".\yo_jenkins\__main__.py", line 8, in <module>
    from .cli import (cli_auth, cli_build, cli_folder, cli_job, cli_server,
ImportError: attempted relative import with no known parent package
```

--------------------------------------------------

- yo-jenkins server server-deploy --debug
    - Failed to setup server
    - Items deployed:
    - {}
    - Too much output. Items deployed??


--------------------------------------------------


- yo-jenkins build logs --follow <JOB> --latest
    - KeyError: `content-length`
    - Clue: `Content Length Bytes: N/A`
    - Catch this error! 
    - Test


--------------------------------------------------


- Cannot install on WSL
    ```
    Collecting yo-jenkins
    Could not find a version that satisfies the requirement yo-jenkins (from versions: )
    No matching distribution found for yo-jenkins
    ```


--------------------------------------------------


- Cannot install from testPYPI
    - Dependency issue
    - Can it be that something went bad from 0.0.1 to 0.0.2???
    - Try again with later versions


--------------------------------------------------


When starting a monitor, don't instantly play sound
at no status change!


--------------------------------------------------


Derived full folder path: folderFullName
in Job() object cuts off one too many directories


--------------------------------------------------


Build monitor SOMETIMES does not update
    - Maybe threads fail?
    - Restart if they fail?
    - Heart beat on the threads


--------------------------------------------------
