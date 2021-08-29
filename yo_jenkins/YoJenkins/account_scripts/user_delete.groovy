#!groovy

// Reference:
//   - https://javadoc.jenkins.io/jenkins/model/Jenkins.html
//   - https://javadoc.jenkins.io/hudson/model/class-use/User.html

import hudson.model.User


// NOTE: Paceholders are replaced at runtime depending on user specification
def userId = "${user_id}"

def instance = Jenkins.get()

def user = instance.getSecurityRealm().getUser(userId)
user.delete()

instance.save()