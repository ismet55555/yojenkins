#!groovy

// Reference:
//   - https://javadoc.jenkins.io/jenkins/model/Jenkins.html
//   - https://javadoc.jenkins.io/hudson/model/class-use/User.html

import hudson.model.User


// NOTE: Paceholders are replaced at runtime depending on user specification
def USERNAME = "${username}"

def instance = Jenkins.getInstance()

def user = instance.getSecurityRealm().getUser(USERNAME)
user.delete()

instance.save()