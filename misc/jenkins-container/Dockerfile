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

LABEL name="Jenkins server" \
      contact="ismet.handzic@gmail.com"

# Environmental Variables
ENV JAVA_OPTS -Djenkins.install.runSetupWizard=false
ENV CASC_JENKINS_CONFIG /var/jenkins_home/casc.yaml

# Installing Plugins
COPY plugins.txt /usr/share/jenkins/ref/plugins.txt
RUN /usr/local/bin/install-plugins.sh < /usr/share/jenkins/ref/plugins.txt

# Get configuration as code file
COPY casc.yaml /var/jenkins_home/casc.yaml
