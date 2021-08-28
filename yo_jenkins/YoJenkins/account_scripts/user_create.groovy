#!groovy

import jenkins.model.*
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

///////////////////////////////////////////////////////////////////////////////

// // TODO: Figure out why I loose admin privelages
// //       when creating an admin user

// // Defing auth strategy
// def roleBasedAuthenticationStrategy = new RoleBasedAuthorizationStrategy()

// // Set the Jenkins auth strategy
// Jenkins.instance.setAuthorizationStrategy(roleBasedAuthenticationStrategy)

// // Define admin permissions
// def adminPermissions = [
// "hudson.model.Hudson.Administer",
// "hudson.model.Hudson.Read"
// ]

// // Check if admin role even exists!
// // TODO

// // Create the role
// Role adminRole = new Role(globalRoleAdmin, adminPermissions);
// roleBasedAuthenticationStrategy.addRole(RoleType.fromString(RoleBasedAuthorizationStrategy.GLOBAL), adminRole);

// // Assign the role to the user
// roleBasedAuthenticationStrategy.assignRole(RoleType.fromString(RoleBasedAuthorizationStrategy.GLOBAL), adminRole, env.JENKINS_USER);
// // OR
// roleBasedAuthenticationStrategy.assignRole(RoleType.Global, adminRole, env.JENKINS_USER); 

// ///////////////////////////////////////////////////////////////////////////////

// Convert the user to an admin, if specified
if (IS_ADMIN) { 
    def strategy = new GlobalMatrixAuthorizationStrategy()
    strategy.setAllowAnonymousRead(false)
    strategy.add(Jenkins.ADMINISTER, USERNAME)
    instance.setAuthorizationStrategy(strategy)

    // jenkins.getAuthorizationStrategy().add(Jenkins.ADMINISTER, env.JENKINS_USER)
    // def strategy = new GlobalMatrixAuthorizationStrategy()
    // strategy.add(Jenkins.ADMINISTER, env.JENKINS_USER)
    // jenkins.setAuthorizationStrategy(strategy)
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