#!/bin/bash

###################################################################
# This bash script uses yojenkins to create a new user/passoword credential. It generates a
# configuration file template, assigns template variables, and then creates the new credential.
###################################################################

set -e

# Define varaibles to be plugged into the credntial template
CRED_SCOPE_DOMAIN="global"
CRED_ID="area-51-access"
CRED_DESCRIPTION="Credential used as an example"
CRED_USERNAME="area-51-user"
CRED_PASSWORD="T0P_sEcReT"
CRED_USERNAME_AS_SECRET=false

# Generate the credential template
CRED_CONFIG_TEMPLATE=$(yojenkins credential get-template user-pass --filepath example-cred-config.xml)

# Interpolate (Plug in) the variables into the template
CRED_CONFIG="$(eval "echo -e \"`<example-cred-config.xml`\"")"

# Save it back to file
echo "$CRED_CONFIG" > example-cred-config.xml

# Create the credential using the interpolated file
yojenkins credential create example-cred-config.xml
echo "Successfully created credential '$CRED_ID'"
