# BUGS


- yo-jenkins build monitor <some job-PR-448> --latest
  - Build.py - 507 -> 74
  - yo_jenkins.YoJenkins.JenkinsItemClasses has no attribute 'job'


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


- System information in log:
  - Ptyhon: 3.9.2 (REV:)
  - Don't put rev if there is none


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
