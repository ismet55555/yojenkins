
# Categories

## Auth
- configure
    - Set up a new credentials file (with default) - DONE
    - pass entire json string or ref to file to setup a new profile or multiple profiles
- token
    - generate a token - DONE
    - add token to specified token - DONE
- verify - DONE
- user - DONE
- activate - activate a profile
- deactivate - deactivate a profile
- wipe - wipe all credentials
- deconfigure - remove a profile


## Server
- Info - DONE
- All user/people info - DONE
- Show plugins - DONE
- Build queue - DONE
- Quite / unquite down - DONE
- Is reachable - DONE
- Restart / safe restart - DONE
- Shutdown / exit - DONE
- Install a plugin


## Node
- Info
- List
- Type
- Create
- Delete
- Toggle offline
- Config


## Folder
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
- Folder XML config.xml - DONE
- Check if item exists (header)


## Job
- Search - DONE
- Info - DONE
- List Builds - DONE
- Check if in queue - DONE
- Return builds that are currently running
  - Maybe part of list ??
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
- monitor - DONE
- Job report
    - Builds over time
    - Builds per user
    - Build success %
    - User trigger / interaction


## Build
- Info - DONE
- Build status text - DONE
- Abort build - DONE
- Delete a build - DONE
- List stages - DONE
- List artifacts - DONE - **NEEDS TESTING**
- Download artifact
- logs
    - download - DONE
    - tail/follow - DONE
- Build queue info - DONE
- Abort build queue - **NEEDS TESTING**
- Open build in browser - DONE
- Monitor a build  - DONE


## Stage
- Info - DONE
- Status text - DONE
- List steps - DONE
- Download logs - DONE
- List checkpoint (/checkpoints) - LATER
- Restart form checkpoint (1/restart - post) - LATER


## Step
- Info - DONE


## user
- **Currently `server people` as `all`**
- info
- all
- create
- delete
- modify


## cred
- info
- list credentials
- create credentials
- config credentials


## logs
Point to remote logs or local logs
- search - Regex search
- repo - Cross reference a error repo file
    - error_log_repo/errors.yaml
    - Load all files in this directory with yaml extension
- diff - Compare two build logs, show difference somehow


## yo
    - set of custom functionalities
    - yojenkins yo
      - get <URL>
      - post <URL>
      - --header
      - --content
      - all the custom formatting
