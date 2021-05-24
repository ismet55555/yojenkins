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
FROM jenkins/jenkins:latest

LABEL name="Jenkins Server" \
      contact="ismet.handzic@gmail.com"

ARG PROTOCOL_SCHEMA
ARG JENKINS_HOSTNAME
ARG JENKINS_PORT
ARG JENKINS_ADMIN_ID
ARG JENKINS_ADMIN_PASSWORD

# Environmental Variables
ENV PROTOCOL_SCHEMA=$PROTOCOL_SCHEMA
ENV JENKINS_HOSTNAME=$JENKINS_HOSTNAME
ENV JENKINS_PORT=$JENKINS_PORT
ENV JENKINS_ADMIN_ID=$JENKINS_ADMIN_ID
ENV JENKINS_ADMIN_PASSWORD=$JENKINS_ADMIN_PASSWORD

ENV JAVA_OPTS -Djenkins.install.runSetupWizard=false
ENV CASC_JENKINS_CONFIG /var/jenkins_home/casc.yaml

# Installing Plugins
COPY plugins.txt /usr/share/jenkins/ref/plugins.txt
RUN /usr/local/bin/install-plugins.sh < /usr/share/jenkins/ref/plugins.txt

# Get configuration as code file
COPY casc.yaml /var/jenkins_home/casc.yaml
