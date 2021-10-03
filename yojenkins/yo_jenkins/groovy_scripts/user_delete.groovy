#!groovy

// Reference:
//   - https://javadoc.jenkins.io/jenkins/model/Jenkins.html
//   - https://javadoc.jenkins.io/hudson/model/class-use/User.html

import hudson.model.User

// NOTE: Paceholders are replaced at runtime depending on user specification
String userId = "${user_id}"

Hudson instance = Jenkins.get()
User user = instance.getSecurityRealm().getUser(userId)
try {
    user.delete()
} catch (groovyError) {
    print "['yojenkins groovy script failed', '${groovyError.message}', 'failed to find user']"
    return
}

instance.save()
