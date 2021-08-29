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
List<String> userPermissionIdList = ${permission_groovy_list}

Hudson instance = Jenkins.get()
GlobalMatrixAuthorizationStrategy authStrategy = Jenkins.instance.getAuthorizationStrategy()

// Adding each permission
userPermissionIdList.each { permissionId ->
    try {
        println permissionId
        String permission = Permission.fromId(permissionId)
        println permission
        authStrategy.add(permission, userId)
        instance.setAuthorizationStrategy(authStrategy)
    } catch (groovy_error) {
        println "--- ERROR ---"
        println groovy_error
        // Convert the last term in permission name to all upper case and retrying
        List<String>  permissionSplit = permissionId.toString().tokenize(".")
        permissionSplit[-1] = permissionSplit.last().toUpperCase()
        String permissionJoin = permissionSplit.join('.')
        println permissionJoin
        String permission = Permission.fromId(permissionJoin)
        println permission

        try {
            authStrategy.add(permission, userId)
            instance.setAuthorizationStrategy(authStrategy)

        } catch (groovy_error2) {
            print "['yo-jenkins groovy script failed', '${groovy_error2.message}']"
            return
        }
    } catch (groovy_error) {
        println groovy_error.getClass()
        print "['yo-jenkins groovy script failed', '${groovy_error.message}']"
    }
}

instance.save()
