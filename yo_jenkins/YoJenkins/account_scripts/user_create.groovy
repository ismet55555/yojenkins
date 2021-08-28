#!groovy

// Reference:
//   - https://javadoc.jenkins.io/jenkins/model/Jenkins.html
//   - https://javadoc.jenkins.io/hudson/model/class-use/User.html

import hudson.model.User
import hudson.security.*
import hudson.tasks.Mailer


// NOTE: Paceholders are replaced at runtime depending on user specification
def USERNAME = "${username}"
def PASSWORD = "${password}"
def IS_ADMIN = ${is_admin}  // true or false
def EMAIL = "${email}"
def DESCRIPTION = "${description}"

def instance = Jenkins.getInstance()

// Create the user
def hudsonRealm = new HudsonPrivateSecurityRealm(false)
hudsonRealm.createAccount(USERNAME, PASSWORD)
instance.setSecurityRealm(hudsonRealm)

// Convert the user to an admin, if specified
if (IS_ADMIN) { 
    def authStrategy = Jenkins.instance.getAuthorizationStrategy()
    authStrategy.add(Jenkins.ADMINISTER, USERNAME)
    instance.setAuthorizationStrategy(authStrategy)
}

// Adding addition account information
def user = instance.getSecurityRealm().getUser(USERNAME)
if (EMAIL) {
    user.addProperty(new Mailer.UserProperty(EMAIL))
}
if (DESCRIPTION) {
    user.setDescription(DESCRIPTION)
}

instance.save()