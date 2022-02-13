# Scripting Examples

[TOC]

!!! note
    For clarity, all of the following script examples are for simplified use cases.
    More advanced use cases may require additional logic and error handling.


## Example 1 - Create job, wait for build, search logs

Here we use a `bash` script with `yojenkins` to do the following:

- Create a new job using a predefined JSON configuration file
- Start a new build for the job
- Wait 12 seconds for the build to start and finish
- Search the build log for the string "Hello beautiful world!"

!!! tip
    Within the job configuration XML definition, notice how variable usage is escaped with `\`
    to avoid variable interpretation.
    Here specifically, using `$VARIABLE` instead of `\$VARIABLE` would cause the variable to be
    interpreted as a local variable name and not as a string.


**Code**
```bash
#!/bin/bash

JOB_NAME="Example Job"
SEARCH_TEXT="Hello world"

# Define the Job configuration
cat > EXAMPLE_JOB_CONFIG.xml << EOF
<?xml version='1.1' encoding='UTF-8'?>
<project>
    <scm class="hudson.scm.NullSCM" />
    <builders>
        <hudson.tasks.Shell>
            <command>

for VARIABLE in "yall" "people" "world"
do
echo "Hello \$VARIABLE"
done

            </command>
            <configuredLocalRules />
        </hudson.tasks.Shell>
    </builders>
</project>
EOF

echo
echo "Creating '$JOB_NAME' job in Jenkins root folder ..."
yojenkins job create \
    --config-file EXAMPLE_JOB_CONFIG.xml  \
    "$JOB_NAME" .

echo
echo "Building '$JOB_NAME' job ..."
yojenkins job build "$JOB_NAME"

echo
echo "Waiting 12 seconds for job to build and complete ..."
sleep 12

echo
echo "Checking build logs for substring '$SEARCH_TEXT' ..."
BUILD_LOGS=$(yojenkins build logs "$JOB_NAME" --latest)

if [[ "$BUILD_LOGS" == *"$SEARCH_TEXT"* ]]; then
    echo "Successfully found text '$SEARCH_TEXT' in build logs"
else
    echo "Failed to find text '$SEARCH_TEXT' in build logs"
    exit 1
fi
```

**Output**
```text
Creating 'Example Job' job in Jenkins root folder ...
success

Building 'Example Job' job ...
success. queue number: 131

Waiting 12 seconds for job to build and complete ...

Checking build logs for substring 'Hello world' ...
Successfully found text 'Hello world'!
```


## Example 2 - Create folder, job, wait for build, and delete

The following `bash` script uses `yojenkins` to do the following:

1. Create a new folder named `Test Folder`
2. Create a new job named `Test Job` inside `Test Folder`
3. Start a new build for job `Test Job`
4. Wait for the build to leave the queue and start running
5. Wait for the job to finish

**Code**
```bash
#!/bin/bash

echo
echo 'Creating "Test Folder" folder ...'
yojenkins folder create --type folder "Test Folder" .

echo
echo 'Creating "Test Job" job in "Test Folder" folder ...'
yojenkins job create "Test Job" "Test Folder"

echo
echo 'Building "Test Job" job ...'
next_build_number=$(yojenkins job next "Test Folder/Test Job")
yojenkins job build "Test Folder/Test Job"

echo
echo 'Waiting for the "Test Job" Job to leave the queue and start running ...'
while [ true ]; do
    last_build_number=$(yojenkins job last "Test Folder/Test Job")
    difference=$((last_build_number - next_build_number))
    if [ $difference == 0 ]; then
        echo
        break
    fi
    echo -n '.'
    sleep 1
done
echo "'Test Job' build $last_build_number has started running"

echo
echo "Waiting for job 'Test Job', build $last_build_number to finish ..."
build_number=$(yojenkins job last "Test Folder/Test Job")
SUCCESS=""
while [ "$SUCCESS" != "SUCCESS" ]; do
    SUCCESS=$(yojenkins build status "Test Folder/Test Job" --number $last_build_number)
    echo -n '.'
    sleep 1
done
echo
echo "Finished job 'Test Job', build $build_number, with SUCCESS status"

echo
echo "Deleting 'Test Job' job and 'Test Folder' folder ..."
yojenkins job delete "Test Folder/Test Job"
yojenkins folder delete "Test Folder"
```

**Output**
```text
Creating "Test Folder" folder ...
success

Creating "Test Job" job in "Test Folder" folder ...
success

Building "Test Job" job ...
success. queue number: 133

Waiting for the "Test Job" Job to leave the queue and start running ...
.....
'Test Job' build 1 has started running

Waiting for job 'Test Job', build 1 to finish ...
.
Finished job 'Test Job', build 1, with SUCCESS status

Deleting 'Test Job' job and 'Test Folder' folder ...
success
success
```

## Example 3 - Search for job on two servers, delete if found

The following `bash` script uses `yojenkins` to search all jobs on two different Jenkins server.
If it is found, delete it.

!!! note
    This example assumes that you have two different profiles listed in your
    `~/.yojenkins/credentials` file with two different Jenkins servers for each profile.
    We are going to assume the profile names are `jenkins-1` and `jenkins-2`.


**Code**
```bash
TODO
```

**Output**
```text
TODO
```


## Example 4 - Creating a User

This `bash` script uses `yojenkins` to set up a new user account and assign them
the right permissions.

**Code**
```bash
#!/bin/bash

set -e

USER_ID="example_user_1"
USER_PASSWORD="54321"    # <-- Simple password for demo only 
USER_PERMISSIONS=(
    'hudson.model.Item.CREATE'
    'hudson.model.Item.DELETE'
)

echo
echo "Creating new user '$USER_ID' ..."
yojenkins account create $USER_ID $USER_PASSWORD

joined_permission_list=$(IFS=,; printf '%s' "${USER_PERMISSIONS[*]}")
echo
echo "Adding the following user permissions: $joined_permission_list"
yojenkins account permission --action add --permission-id $joined_permission_list $USER_ID
```

**Output**
```text
Creating new user 'example_user_1' ...
success

Adding the following user permissions: hudson.model.Item.CREATE,hudson.model.Item.DELETE
success
```


## Example 5 - Creating a Credential

This `bash` script uses `yojenkins` to create a new user/passoword credential. It generates a
configuration file template, assigns template variables, and then creates the new credential.

**Code**
```bash
#!/bin/bash

# Define varaibles to be plugged into the credntial template
CRED_SCOPE_DOMAIN="global"
CRED_ID="area-51-access"
CRED_DESCRIPTION="Credential used as an example"
CRED_USERNAME="area-51-user"
CRED_PASSWORD="T0P_sEcReT"
CRED_USERNAME_AS_SECRET=false

# Generate the credential template and save to file
yojenkins credential get-template user-pass --filepath example-cred-config.xml

# Interpolate (Plug in) the variables into the template
CRED_CONFIG="$(eval "echo -e \"`<example-cred-config.xml`\"")"

# Save it back to file
echo "$CRED_CONFIG" > example-cred-config.xml

# Create the credential using the interpolated file
yojenkins credential create example-cred-config.xml
echo "Successfully created credential '$CRED_ID'"
```

**Output**
```text
Successfully created credential 'area-51-access'
```
