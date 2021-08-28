#!groovy

import hudson.model.User
import groovy.json.JsonOutput
import hudson.security.Permission
import jenkins.security.LastGrantedAuthoritiesProperty
import java.util.Date

// Get all autherization strategy from Jenkins instance
authStrategy = Jenkins.instance.getAuthorizationStrategy()

userIdCurrent = User.current().getId()

def userInfoList = []
User.getAll().each { user ->
    def userId = user.getId()

    if (!["unknown", "getId", "getUser"].contains(userId)) {
        def prop = user.getProperty(LastGrantedAuthoritiesProperty)

        def userInfo = [
            "id": userId,
          	"me": userId == userIdCurrent,
            "fullName": user.getFullName() ? user.getFullName() : "",
            "description": user.getDescription() ? user.getDescription() : "",
            "absoluteUrl": user.getAbsoluteUrl() ? user.getAbsoluteUrl() : "",
            "userFolder": user.getUserFolder() ? user.getUserFolder() : "",
            "isAdmin": authStrategy.hasPermission(userId, Jenkins.ADMINISTER),
            "isManager": authStrategy.hasPermission(userId, Jenkins.MANAGE),
            "isSystemRead": authStrategy.hasPermission(userId, Jenkins.SYSTEM_READ),
            "canRead": authStrategy.hasPermission(userId, Permission.READ),
            "canWrite": authStrategy.hasPermission(userId, Permission.WRITE),
            "canUpdate": authStrategy.hasPermission(userId, Permission.UPDATE),
            "canDelete": authStrategy.hasPermission(userId, Permission.DELETE),
            "canConfigure": authStrategy.hasPermission(userId, Permission.CONFIGURE),
            "authorities": user.authorities,
            "lastGrantedAuthChanged" : prop ? (new Date(prop.timestamp).toString()) : "never",
        ]
        userInfoList.add(userInfo)
    }
}
def jsonOut = JsonOutput.toJson(userInfoList)
def jsonOutPretty = JsonOutput.prettyPrint(jsonOut)
println (jsonOutPretty)