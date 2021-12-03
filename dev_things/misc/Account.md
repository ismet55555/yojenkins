# Account

- Jenkins API Docs:
    - Jenkins instance: https://javadoc.jenkins.io/jenkins/model/Jenkins.html
    - Authorization Strategy: https://javadoc.jenkins-ci.org/hudson/security/AuthorizationStrategy.html
        - GlobalMatrixAuthorizationStrategy: https://javadoc.jenkins.io/plugin/matrix-auth/hudson/security/GlobalMatrixAuthorizationStrategy.html
    - HudsonPrivateSecurityRealm: https://javadoc.jenkins.io/hudson/security/HudsonPrivateSecurityRealm.html
    - User: https://javadoc.jenkins.io/hudson/model/class-use/User.html
    - UserProperty: https://javadoc.jenkins.io/hudson/model/UserProperty.html
    - Permission: https://javadoc.jenkins.io/hudson/security/Permission.html
    - Run List: https://javadoc.jenkins.io/hudson/util/RunList.html
    - Matrix-Based Security: https://wiki.jenkins.io/plugins/servlet/mobile?contentId=67569939#content/view/67569939

- Cloudbees Jenkins Scripts
    - https://github.com/cloudbees/jenkins-scripts


- Might need to use jenkins groovy script to deal with users
    - See `cli/cli_tools` -> `run_script()`
    - ```python
        # Send the request to the server
        content, header, success = yj_obj.Rest.request(target='scriptText',
                                                    request_type='post',
                                                    data={'script': script},
                                                    json_content=False)
        ```

- User object
    - Docs: https://javadoc.jenkins.io/hudson/model/User.html
    - Usage: ```groovy
        import hudson.model.User

        User.getAll().each { user ->
            println "=================="
            println user.getId()
            println user.getFullName()
            println user.getAbsoluteUrl()
            println user.canDelete()
            println user.getUserFolder()
            println user.getBuilds()
        }

    ```


### List all

- getAllUsers - All users who can login to the system.

- http://localhost:8080/asynchPeople/api/xml?depth=1

- Using Groovy
- https://javadoc.jenkins.io/hudson/model/User.html
- https://javadoc.jenkins.io/hudson/model/Run.html
- Also FreeStyleBuild



### User Permission

- getACL - Obtains the ACL associated with this object.
- checkPermission - Convenient short-cut for getACL().checkPermission(permission)
- hasPermission - Convenient short-cut for getACL().hasPermission(permission)


### Get info

TODO

### Get configuration

TODO


### Create

- Can create with:
    - Admin
        - doCreateFirstAccount - Creates a first admin user account
        - doCreateAccountByAdmin - Creates a user account other than yourself. Requires Jenkins.ADMINISTER
    - User - Self-registration
        - doCreateAccount - Creates an user account. Used for self-registration.
    - Federation identity - **TODO**
        - `doCreateAccountWithFederatedIdentity - Creates an account and associates that with the given identity. Used in conjunction with commenceSignup(hudson.security.FederatedLoginService.FederatedIdentity)
- https://github.com/nsayed123/jenkins_setup/blob/aa1db4c7c66ca7599f57c453dd44c2717ac04de8/roles/jenkins/templates/create_user.groovy


```
yojenkins user create \
    --admin \
    --password XXXX \
    --username XXXX
```

- From monitoring developer tools:
    - `POST - http://localhost:8080/securityRealm/createAccountByAdmin`
    - ```json
        {
            "username": "test_user_1",
            "password1": "blahblah",
            "password2": "blahblah",
            "$redact": ["password1", "password2"],
            "fullname": "ismet handzic",
            "email": "ismet.handzic@gmail.com",
            "Jenkins-Crumb": "cdb0a02bf285bda957084b4249ba2b056286fb11352efe10e98ac0a81d35b133"}
    ```

- From Jenkins SDK: `N/A`

- Snippets from Web:
    - ```python
        uurl="http://demo.com:8080/securityRealm/createAccountByAdmin"
        refdata = {"username": userName,
                    "password1": '123456',
                    "password2": '123456',
                    "fullname" : userName,
                    "email" : userName + '@jenkins.com'}
    ```


- Groovy Script
    - ```groovy
        import jenkins.model.*
        import hudson.security.*

        def instance = Jenkins.getInstance()

        def hudsonRealm = new HudsonPrivateSecurityRealm(false)
        hudsonRealm.createAccount("${username}","${password}")
        instance.setSecurityRealm(hudsonRealm)

        def userIsAdmin = ${admin}

        def strategy = new GlobalMatrixAuthorizationStrategy()
        strategy.add(Jenkins.ADMINISTER, "${username}")
        instance.setAuthorizationStrategy(strategy)

        instance.save()
    ```
