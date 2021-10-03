#!groovy

// Reference:
//   - https://javadoc.jenkins.io/jenkins/model/Jenkins.html
//   - https://javadoc.jenkins.io/hudson/model/class-use/User.html
//   - https://javadoc.jenkins-ci.org/hudson/security/AuthorizationStrategy.html

import hudson.model.User
import hudson.security.HudsonPrivateSecurityRealm
import hudson.security.GlobalMatrixAuthorizationStrategy
import hudson.tasks.Mailer

// Get the variables added via templating
//      NOTE: Paceholders are replaced at runtime depending on user specification
String userId = "${user_id}"
String userPassword = "${password}"
Boolean isAdmin = ${is_admin}  // true or false
String userEmail = "${email}"
String userDescription = "${description}"

Hudson instance = Jenkins.get()

// Create the user
try {
    HudsonPrivateSecurityRealm hudsonRealm = new HudsonPrivateSecurityRealm(false)
    hudsonRealm.createAccount(userId, userPassword)
    instance.setSecurityRealm(hudsonRealm)
} catch (groovyError) {
    print "['yojenkins groovy script failed', '${groovyError.message}', 'failed to create new user ${userId}']"
}

// Convert the user to an admin, if specified
if (isAdmin) {
    try {
        GlobalMatrixAuthorizationStrategy authStrategy = Jenkins.instance.getAuthorizationStrategy()
        authStrategy.add(Jenkins.ADMINISTER, userId)
        instance.setAuthorizationStrategy(authStrategy)
    } catch (groovyError) {
        print "['yojenkins groovy script failed', '${groovyError.message}', 'failed to give user ${userId} admin permissions']"
    }
}

// Adding addition account information
def user = instance.getSecurityRealm().getUser(userId)
if (userEmail) {
    user.addProperty(new Mailer.UserProperty(userEmail))
}
if (userDescription) {
    user.setDescription(userDescription)
}

instance.save()
