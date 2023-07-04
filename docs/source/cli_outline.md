# CLI Command Outline

Below is a complete outline of the `yojenkins` CLI command structure.

!!! note
As of Version: **0.0.86**

```text
yojenkins
    |
    |-- account     Manage user accounts
    |     |--- create           Create a user account
    |     |--- delete           Delete a user account
    |     |--- info             Get user information
    |     |--- list             List all users
    |     |--- password-reset   Reset a user password
    |     |--- permission       Add or remove user permission
    |     |--- permission-list  List all available permissions
    |
    |
    |-- auth        Manage authentication and profiles
    |     |--- configure  Configure authentication
    |     |--- show       Show the local credentials profiles
    |     |--- token      Generate authentication API token
    |     |--- user       Show current user information
    |     |--- verify     Check if credentials can authenticate
    |     |--- wipe       Wipe all credentials for this device
    |
    |
    |-- build       Manage builds
    |     |--- abort    Abort build
    |     |--- browser  Open build in web browser
    |     |--- delete   Delete build
    |     |--- diff     Find difference between two builds
    |     |--- info     Build information
    |     |--- logs     Get build logs
    |     |--- monitor  Start monitor UI
    |     |--- rebuild  Rebuild a build with same parameters
    |     |--- stages   Get build stages
    |     |--- status   Build status text/label
    |
    |
    |-- credential  Manage credentials
    |     |--- config        Get credential configuration
    |     |--- create        Create new credentials
    |     |--- delete        Remove credentials
    |     |--- get-template  Credential type template to create a credential
    |     |--- info          Credential information
    |     |--- list          List credentials
    |     |--- move          Move a credential to another folder/domain
    |     |--- update        Reconfigure existing credentials
    |
    |
    |-- folder      Manage folders
    |     |--- browser     Open folder in web browser
    |     |--- config      Get folder configuration
    |     |--- copy        Copy an existing item
    |     |--- create      Create an item [folder, view, job]
    |     |--- delete      Delete folder or view
    |     |--- info        Folder information
    |     |--- items       List all items in folder
    |     |--- jobs        List all jobs in folder
    |     |--- search      Search folders by REGEX pattern
    |     |--- subfolders  List all subfolders in folder
    |     |--- views       List all views in folder
    |
    |
    |-- job         Manage jobs
    |     |--- browser       Open job in web browser
    |     |--- build         Build a job
    |     |--- build-exist   Check if build number exists
    |     |--- config        Get job configuration
    |     |--- create        Create a job
    |     |--- delete        Delete job
    |     |--- diff          Find difference between two jobs
    |     |--- disable       Disable job
    |     |--- enable        Enable job
    |     |--- info          Job information
    |     |--- last          Get previous build number
    |     |--- list          List all builds for job
    |     |--- monitor       Start monitor UI
    |     |--- next          Get next build number
    |     |--- queue-cancel  Cancel this job in queue
    |     |--- queue-check   Check if this job is in queue
    |     |--- rename        Rename job
    |     |--- search        Search jobs by REGEX pattern
    |     |--- set           Set the next build number
    |     |--- wipe          Wipe job workspace
    |
    |
    |-- node        Manage nodes
    |     |--- config            Get node configuration
    |     |--- create-ephemeral  Setup a local or remote ephemeral/as-needed node
    |     |--- create-permanent  Setup a local or remote persistent node
    |     |--- delete            Delete a node
    |     |--- disable           Disable a node
    |     |--- enable            Enable a node
    |     |--- info              Node information
    |     |--- list              List all nodes
    |     |--- logs              Node logs
    |     |--- prepare           Prepare a remote machine to become a node
    |     |--- reconfig          Reconfigure the node
    |     |--- status            Node status
    |
    |
    |-- server      Manage server
    |     |--- browser          Open server home page in web browser
    |     |--- info             Server information
    |     |--- people           Show all people/users on server
    |     |--- plugins          Show plugin information
    |     |--- queue            Show current job build queues on server
    |     |--- quiet            Server quite mode enable/disable
    |     |--- reachable        Check if server is reachable
    |     |--- restart          Restart the server
    |     |--- server-deploy    Create a local development server using Docker
    |     |--- server-teardown  Remove a local development server
    |     |--- shutdown         Shut down the server
    |
    |
    |-- stage       Manage build stages
    |     |--- info    Stage information
    |     |--- logs    Stage steps
    |     |--- status  Stage status text
    |     |--- steps   Get stage steps
    |
    |
    |-- step        Manage stage steps
    |     |--- info  Step information
    |
    |
    |-- tools       Tools and more
          |--- bug-report        Report a bug
          |--- docs              Open browser to the documentation
          |--- feature-request   Request a feature
          |--- history           Show detailed command usage history
          |--- rest-request      Send a generic Rest request to server
          |--- run-script        Run Groovy script on server, return result
          |--- shared-lib-setup  Set up a Jenkins shared library
```
