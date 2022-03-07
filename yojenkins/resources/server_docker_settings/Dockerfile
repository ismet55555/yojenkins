##############################################################################
#
# Test image:
#   docker build -t jenkins:jcasc .
#   docker run --name jenkins --rm -p 8080:8080 jenkins:jcasc
#
##############################################################################

# Base image with defaults
ARG JENKINS_BASE_IMAGE='jenkins/jenkins'
ARG JENKINS_BASE_VERSION='latest'
FROM $JENKINS_BASE_IMAGE:$JENKINS_BASE_VERSION

# Passed build arguments with defaults
ARG JENKINS_CONFIG_FILE='config_as_code.yaml'
ARG JENKINS_PLUGINS_FILE='plugins.txt'
ARG PROTOCOL_SCHEMA='http'
ARG JENKINS_HOSTNAME='localhost'
ARG JENKINS_PORT='8080'
ARG JENKINS_ADMIN_ID='admin'
ARG JENKINS_ADMIN_PASSWORD='password'

# Image labels
LABEL name="Jenkins Server"
LABEL contact="ismet.handzic@gmail.com"
LABEL description="Jenkins server for development and testing"

# Environmental Variables
ENV PROTOCOL_SCHEMA=${PROTOCOL_SCHEMA}
ENV JENKINS_HOSTNAME=${JENKINS_HOSTNAME}
ENV JENKINS_PORT=${JENKINS_PORT}
ENV JENKINS_ADMIN_ID=${JENKINS_ADMIN_ID}
ENV JENKINS_ADMIN_PASSWORD=${JENKINS_ADMIN_PASSWORD}
ENV JAVA_OPTS -Djenkins.install.runSetupWizard=false
ENV CASC_JENKINS_CONFIG="/var/jenkins_home/casc.yaml"

# NOTE: By default this script is run as "jenkins" user

# Installing Plugins
COPY --chown=jenkins:jenkins ./${JENKINS_PLUGINS_FILE} /usr/share/jenkins/ref/plugins.txt
RUN jenkins-plugin-cli --plugin-file /usr/share/jenkins/ref/plugins.txt

# Creating directory for potential bind mount
RUN mkdir /tmp/my_things

# Get configuration as code file
#   TODO: URL option ARG for remote configuration as code
COPY --chown=jenkins:jenkins ./${JENKINS_CONFIG_FILE} /var/jenkins_home/casc.yaml

# Copy and run extra/custom setup script passed by user
USER root
COPY extra_setup_script.sh /usr/local/bin/
RUN chmod 766 /usr/local/bin/extra_setup_script.sh
RUN /usr/local/bin/extra_setup_script.sh
USER jenkins
