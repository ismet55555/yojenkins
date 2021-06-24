#!/bin/bash

##############################################################################
#
# Usage:
#   1. Hardcode parameters and run the script
#   2. Pass parameters into script.
#       Example: ./jenkins-generate-api-token.sh https://localhost:8080 test-token myid mypassword
#
# NOTE: For security purposes, maybe better to pass password with envirnmental variable
#
##############################################################################

set -e

# Assign default values if parameters are not passed into script
PASSWORD=${1:-'<DEFAULT PASSWORD>'}
USERNAME=${2:-'***REMOVED***'}
JENKINS_SERVER_URL=${3:-"https://localhost:8080"}
NEW_TOKEN_NAME=${4:-"My-new-generated-api-token"}  # No spaces

echo "Password: ****"
echo "Username: ${USERNAME}"
echo "Server URL: ${JENKINS_SERVER_URL}"
echo "Token Name: ${NEW_TOKEN_NAME}"

# Creating the cookie to jeknins server
echo "Generating server cookie ..."
CRUMB=$(curl ${JENKINS_SERVER_URL}/crumbIssuer/api/xml?xpath=concat\(//crumbRequestField,%22:%22,//crumb\) \
        --silent \
        --cookie-jar temp_cookie_file \
        --user "${USERNAME}:${PASSWORD}" )
echo "Cookie: ${CRUMB}"

# Make the request to generate the API token
echo "Generating API token ..."
TOKEN_VALUE=$(curl -X POST ${JENKINS_SERVER_URL}/me/descriptorByName/jenkins.security.ApiTokenProperty/generateNewToken/api/json?newTokenName="${NEW_TOKEN_NAME}&tree=data[tokenValue]" \
            --silent \
            --header ${CRUMB} \
            --cookie temp_cookie_file \
            --user "${USERNAME}:${PASSWORD}" \
            | jq -r '.data.tokenValue')
echo "API Token Value: ${TOKEN_VALUE}"

# Remove the cookie file
echo "Removing temporary cookie file ..."
rm -f temp_cookie_file

echo "DONE"