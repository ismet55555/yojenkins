#!groovy

// Reference:
//   - https://javadoc.jenkins.io/jenkins/model/Jenkins.html
//   - https://javadoc.jenkins.io/hudson/model/class-use/User.html
//   - https://javadoc.jenkins.io/hudson/security/Permission.html
//   - https://javadoc.jenkins-ci.org/hudson/security/AuthorizationStrategy.html
//   - https://javadoc.jenkins-ci.org/hudson/model/package-summary.html
//   - https://github.com/ivanaudisio/Jenkins/blob/master/create-user.groovy

import hudson.model.*
import jenkins.model.*
import Jenkins.*
import hudson.security.Permission
import hudson.security.GlobalMatrixAuthorizationStrategy

// Get the variables added via templating
//      NOTE: Paceholders are replaced at runtime depending on user specification
String userId = "${user_id}"
List<Object> userPermissionList
Boolean permissionEnabled = ${permission_enabled}  // true of false

try {
    userPermissionList = ${permission_groovy_list}
} catch (groovyError) {
    print "['yojenkins groovy script failed', '${groovyError.message}', 'failed to find/match permission ID(s). Please review docs for permission class']"
    return
}

Hudson instance = Jenkins.get()
GlobalMatrixAuthorizationStrategy authStrategy = Jenkins.instance.getAuthorizationStrategy()

// Adding each permission
userPermissionList.each { permission ->
    try {
        permission.enabled = permissionEnabled
        authStrategy.add(permission, userId)
        instance.setAuthorizationStrategy(authStrategy)
    } catch (groovyError) {
        print "['yojenkins groovy script failed', '${groovyError.message}', 'failed to add permission ${permission}']"
        return
    }
}

instance.save()
