
## Categories

- Authentication
    - configure
        - Set up a new credentials file (with default) - DONE
        - pass entire json string to setup a new profile
        - --remove a profile
    - token
        - generate a token - DONE
        - add token to specified token - DONE
        - --refresh-all for all profiles
    - activate
        - activate a profile
    - deactivate
        - deactivate a profile
    - wipe
        - wipe all credentials
    - verify - DONE
yo  
- Server
    - Info - **NEEDS TESTING**
    - User info - DONE
    - Build queue - DONE
    - Quite / unquite down
    - Is reachable - DONE
    - Wait for normal operation
    - Restart / safe restart
    - https://dheerajgambhir.medium.com/optimized-way-to-stop-restart-jenkins-72fb52aeac49#:~:text=Jenkins%20provides%20a%20set%20of,it%20in%20a%20quiet%20mode.&text=cancelQuietDown%3A%20Cancel%20the%20effect%20of,completed%2C%20and%20then%20restart%20Jenkins.


- Node
    - Info
    - List
    - Type
    - Create
    - Delete
    - Toggle offline
    - Config

- Folder
    - Search - DONE
    - Info - DONE
    - List subfolders - DONE
    - List jobs - DONE
    - List views - DONE
    - List all items - DONE
    - Open folder in browser - DONE
    - Create folder - DONE
    - Create job - DONE
    - Create view - DONE
    - Copy new item - DONE
    - Check if item exists
    - Folder XML config.xml - DONE


- Job
    - Search - DONE
    - Info - DONE
    - List Builds - DONE
    - Check if in queue - DONE
    - Return builds that are currently running
    - Get next build in line - DONE
    - Set next build number - DONE
    - Check if build exists - DONE
    - Start a build - DONE
    - Check if in queue - DONE
    - Open Job in browser - DONE
    - Job Parameters/Config - DONE
    - Disable job - DONE
    - Enable job - DONE
    - Create job - DONE
    - Delete job - DONE
    - Rename job - DONE
    - Wipeout job workspace - DONE
    - Copy job - DONE
    - Job XML config.xml - DONE
    - Job report
        - Builds over time
        - Builds per user
        - Build success %
        - User trigger / interaction

- Build
    - Info - DONE
    - Build status text - DONE
    - Abort build - DONE
    - Delete a build - DONE
    - List stages - DONE
    - List artifacts - DONE - **NEEDS TESTING**
    - Download artifact
    - Download log - DONE
    - Build queue info - DONE
    - Abort build queue - **NEEDS TESTING**
    - Open build in browser - DONE
    - Monitor a build 
        - Notification - Play tune? System notification?
    - Build success/failure kick off command
    - More in jenkins-python module????

- Stage
    - Info - DONE
    - Status text - DONE
    - List steps - DONE
    - Download logs - DONE
    - List checkpoint (/checkpoints) - LATER
    - Restart form checkpoint (1/restart - post) - LATER

- Step
    - Info - DONE

- Creds (Folder)
    - info
    - list credentials
    - create credentials
    - config credentials

- Logs
    - search - Regex search
    - repo - Cross reference a error repo file
        - error_log_repo/errors.yaml
        - Load all files in this directory with yaml extension
    - diff - Compare two build logs, show difference somehow

- Utility
    - URL to name - DONE
    - Build URL to job URL - DONE
    - name to URL

