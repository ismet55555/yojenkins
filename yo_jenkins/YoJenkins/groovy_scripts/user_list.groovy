#!groovy

// Reference:
//   - https://javadoc.jenkins.io/jenkins/model/Jenkins.html
//   - https://javadoc.jenkins.io/hudson/model/class-use/User.html
//   - https://javadoc.jenkins.io/hudson/security/Permission.html
//   - https://javadoc.jenkins.io/jenkins/security/LastGrantedAuthoritiesProperty.html

import hudson.model.User
import groovy.json.JsonOutput
import hudson.security.Permission
import jenkins.security.LastGrantedAuthoritiesProperty
import hudson.security.GlobalMatrixAuthorizationStrategy
import java.util.Date

String userIdCurrent = User.current().getId()
GlobalMatrixAuthorizationStrategy authStrategy = Jenkins.instance.getAuthorizationStrategy()

ArrayList userInfoList = []
User.getAll().each { user ->
    String userId = user.getId()

    if (!['unknown', 'getId', 'getUser'].contains(userId)) {
        LastGrantedAuthoritiesProperty prop = user.getProperty(LastGrantedAuthoritiesProperty)
        LinkedHashMap userInfo = [
            'id': userId,
            'me': userId == userIdCurrent,
            'fullName': user.getFullName() ? user.getFullName() : '',
            'description': user.getDescription() ? user.getDescription() : '',
            'absoluteUrl': user.getAbsoluteUrl() ? user.getAbsoluteUrl() : '',
            'userFolder': user.getUserFolder() ? user.getUserFolder() : '',
            'isAdmin': authStrategy.hasPermission(userId, Jenkins.ADMINISTER),
            'isManager': authStrategy.hasPermission(userId, Jenkins.MANAGE),
            'isSystemRead': authStrategy.hasPermission(userId, Jenkins.SYSTEM_READ),
            'canRead': authStrategy.hasPermission(userId, Permission.READ),
            'canWrite': authStrategy.hasPermission(userId, Permission.WRITE),
            'canUpdate': authStrategy.hasPermission(userId, Permission.UPDATE),
            'canDelete': authStrategy.hasPermission(userId, Permission.DELETE),
            'canConfigure': authStrategy.hasPermission(userId, Permission.CONFIGURE),
            'authorities': user.authorities,
            'lastGrantedAuthoritiesChanged' : prop ? (new Date(prop.timestamp).toString()) : 'never',
        ]
        userInfoList.add(userInfo)
    }
}
String jsonOut = JsonOutput.toJson(userInfoList)
String jsonOutPretty = JsonOutput.prettyPrint(jsonOut)
print (jsonOutPretty)
