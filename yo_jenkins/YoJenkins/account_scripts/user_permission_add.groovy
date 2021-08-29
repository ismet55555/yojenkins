#!groovy

// Reference:
//   - https://javadoc.jenkins.io/jenkins/model/Jenkins.html
//   - https://javadoc.jenkins.io/hudson/model/class-use/User.html
//   - https://javadoc.jenkins.io/hudson/security/Permission.html
//   - https://javadoc.jenkins-ci.org/hudson/security/AuthorizationStrategy.html
//   - https://javadoc.jenkins-ci.org/hudson/model/package-summary.html

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
} catch (error) {
    print "['yo-jenkins groovy script failed', '${error}']"
    return
}

Hudson instance = Jenkins.get()
GlobalMatrixAuthorizationStrategy authStrategy = Jenkins.instance.getAuthorizationStrategy()

// Adding each permission
userPermissionList.each { permission ->
    try {
        authStrategy.add(permission, userId)
        instance.setAuthorizationStrategy(authStrategy)
    } catch (error) {
        print "['yo-jenkins groovy script failed', '${error}']"
        return
    }
}

instance.save()
