
## Deployment

- Fix  reference to `yo_jenkins/server_docker_settings` and `yo_jenkins/sound`
    - How to get the reference

    ```python
    import sysconfig

    site_package_dir = sysconfig.get_paths()["purelib"]
    exam_file_location = os.path.abspath(
        os.path.join(
            site_package_dir,
            "yo_jenkins",
            "<DIRECTORY>",
                "<FILENAME>"
                )
        )
    ```





- Cannot install on WSL
    Collecting yo-jenkins
    Could not find a version that satisfies the requirement yo-jenkins (from versions: )
    No matching distribution found for yo-jenkins

- Cannot install from testPYPI
    - Dependency issue
    - Can it be that something went bad from 0.0.1 to 0.0.2???


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
