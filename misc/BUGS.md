# BUGS


--------------------------------------------------

- yo-jenkins buld logs <JOB URL> --latest --follow --debug
  - Each request opens up a new connection 
  - Starting new HTTP connection (1): localhost:8080
  - Should be:
    - http://localhost:8080 "GET /job/testing/api/json HTTP/1.1" 200 525


--------------------------------------------------


- System information in log:
  - Ptyhon: 3.9.2 (REV:)
  - Don't put rev if there is none



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
