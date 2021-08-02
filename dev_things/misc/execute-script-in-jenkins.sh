#!/bin/bash

##############################################################################
#
# Usage:
#   1. Hardcode parameters and run the script
#   2. Pass parameters into script.
#       Example: ./execute-script-in-jenkins.sh https://localhost:8080 test-token myid mypassword
#
# NOTE: For security purposes, maybe better to pass password with envirnmental variable
#
##############################################################################

set -e

# Assign default values if parameters are not passed into script
PASSWORD=${1:-'password'}
USERNAME=${2:-'admin'}
JENKINS_SERVER_URL=${3:-"http://localhost:8080"}
SCRIPT_COMMAND=${4:-"println(Jenkins.instance.pluginManager.plugins)"}  # No spaces

echo "Password: ****"
echo "Username: ${USERNAME}"
echo "Server URL: ${JENKINS_SERVER_URL}"
echo "Script Command: ${SCRIPT_COMMAND}"

# Creating the cookie to jeknins server
echo
echo "Generating server cookie ..."
CRUMB=$(curl ${JENKINS_SERVER_URL}/crumbIssuer/api/xml?xpath=concat\(//crumbRequestField,%22:%22,//crumb\) \
        --silent \
        --cookie-jar temp_cookie_file \
        --user "${USERNAME}:${PASSWORD}" )
echo "Cookie: ${CRUMB}"


# Execute the script
echo
echo "Sending groovy script ..."
curl -X POST ${JENKINS_SERVER_URL}/scriptText \
        -d "script=${SCRIPT_COMMAND}" \
        --silent \
        --header ${CRUMB} \
        --cookie temp_cookie_file \
        --user "${USERNAME}:${PASSWORD}"


# Remove the cookie file
echo
echo "Removing temporary cookie file ..."
rm -f temp_cookie_file

echo
echo "DONE"