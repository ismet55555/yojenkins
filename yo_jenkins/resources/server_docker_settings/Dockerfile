##############################################################################
#
# Commands:
#   docker build -t jenkins:jcasc .
#   docker run --name jenkins \
#              --rm -p 8080:8080 \
#              --env JENKINS_ADMIN_ID=admin \
#              --env JENKINS_ADMIN_PASSWORD=password \
#              jenkins:jcasc
#
##############################################################################


# Base image
ARG JENKINS_BASE_IMAGE='jenkins/jenkins'
ARG JENKINS_BASE_VERSION='latest'
FROM $JENKINS_BASE_IMAGE:$JENKINS_BASE_VERSION


# Passed build arguments
ARG JENKINS_CONFIG_FILE='config_as_code.yaml'
ARG JENKINS_PLUGINS_FILE
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
ENV CASC_JENKINS_CONFIG /var/jenkins_home/casc.yaml

# Installing Plugins
COPY ${JENKINS_PLUGINS_FILE} /usr/share/jenkins/ref/plugins.txt
RUN /usr/local/bin/install-plugins.sh < /usr/share/jenkins/ref/plugins.txt


# Creating directory for potential bind mount
RUN mkdir /tmp/my_things


# Get configuration as code file
# TODO: Remote URL for configuration as code
COPY ${JENKINS_CONFIG_FILE} /var/jenkins_home/casc.yaml
