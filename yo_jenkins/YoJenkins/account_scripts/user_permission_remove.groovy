#!groovy

// Reference:
//   - https://javadoc.jenkins.io/jenkins/model/Jenkins.html
//   - https://javadoc.jenkins.io/hudson/model/class-use/User.html
//   - https://javadoc.jenkins.io/hudson/security/Permission.html
//   - https://javadoc.jenkins-ci.org/hudson/security/AuthorizationStrategy.html
//   - https://javadoc.jenkins-ci.org/hudson/model/package-summary.html




// TODO: Figgure out how to remove a specific permission from a user.



import hudson.model.*
import Jenkins.*
import hudson.security.Permission
import hudson.security.GlobalMatrixAuthorizationStrategy

// Get the variables added via templating
//      NOTE: Paceholders are replaced at runtime depending on user specification
String userId = "${user_id}"
List<String> userPermissionList
try {
    userPermissionList = ${permission_groovy_list}
} catch (groovy_error) {
    print "['yo-jenkins groovy script failed', '${groovy_error.message}', 'failed to find/match permission ID(s)']"
    return
}

Hudson instance = Jenkins.get()
GlobalMatrixAuthorizationStrategy authStrategy = Jenkins.instance.getAuthorizationStrategy()

// Adding each permission
userPermissionList.each { permission ->
    try {
        authStrategy.delete(permission, userId)
        instance.setAuthorizationStrategy(authStrategy)
    } catch (groovy_error) {
        print "['yo-jenkins groovy script failed', '${groovy_error.message}', 'failed to remove permission ${permission}']"
    }
}

instance.save()
