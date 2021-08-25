import hudson.model.User
import groovy.json.JsonOutput

def userInfoList = []
User.getAll().each { user ->
    userId = user.getId()
    if (!["unknown", "getId", "getUser"].contains(userId)) {
        def userInfo = [
            "id": userId,
            "fullName": user.getFullName() ? user.getFullName() : "",
            "description": user.getDescription() ? user.getDescription() : "",
            "absoluteUrl": user.getAbsoluteUrl() ? user.getAbsoluteUrl() : "empty",
            "canDelete": user.canDelete(),
            "userFolder": user.getUserFolder() ? user.getUserFolder() : ""
        ]
        userInfoList.add(userInfo)
    }
}
def jsonOut = JsonOutput.toJson(userInfoList)
def jsonOutPretty = JsonOutput.prettyPrint(jsonOut)
println (jsonOutPretty)