#!/bin/bash

###################################################################
# Create a new job using a predefined JSON configuration file
# Start a new build for the job
# Wait some predefined time for the build to start and finish
# Search the build log for the string "Hello beautiful world!"
###################################################################

set -e

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
