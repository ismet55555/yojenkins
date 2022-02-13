#!/bin/bash

###################################################################
# Creating a user
# Adding specific user permission to the user
###################################################################

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

