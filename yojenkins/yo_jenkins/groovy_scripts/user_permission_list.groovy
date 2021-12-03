#!groovy

// Reference:
//   - https://javadoc.jenkins.io/jenkins/model/Jenkins.html
//   - https://javadoc.jenkins.io/hudson/security/Permission.html
//   - https://javadoc.jenkins.io/jenkins/security/LastGrantedAuthoritiesProperty.html

import groovy.json.JsonOutput
import hudson.security.Permission

ArrayList permissionInfoList = []
Permission.getAll().each { permission ->
    LinkedHashMap permissionInfo = [
        'id': permission.getId().toString(),
        'name': permission.name,
        'description': permission.description ? permission.description.toString() : '',
        'enabled': permission.enabled
    ]
    permissionInfoList.add(permissionInfo)
}
String jsonOut = JsonOutput.toJson(permissionInfoList)
String jsonOutPretty = JsonOutput.prettyPrint(jsonOut)
print (jsonOutPretty)
