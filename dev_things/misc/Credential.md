# Credential


- System store: `system`
- Default domain: `_`


#### List all
```
yojenkins credential list \
    --folder <folder> \          # <--- default: root
    --domain global \            # <--- default: global ("_")
    --keys id,displayName        # <--- default: *
```

#### Get info
```
yojenkins credential info \
    --credential <credential> \  # <--- id, name, or url
    --folder <folder> \          # <--- default: root
    --domain global \            # <--- default: global ("_")
```

#### Get configuration

- Templates have place holders: {{ HERE }}
- Saved as json, but can be outputted in different format

```
yojenkins credential config \
    --store system \             # <--- default: system
    --domain global \            # <--- default: global ("_")
```

#### Generate credential template
```
yojenkins credential template \
    --

```

#### Create
- Have a blank credential template to fill in using f-string, like the node thing
- Should I convert form JSON to XML, or accept json as is? Maybe test it to see if it can be parsed?
- For not maybe only have a configuration file setting?
    - Def need a little smoother way than this ...
```
yojenkins credential create \
    --folder <folder> \                     # <--- default: root
    --domain <domain> \                     # <--- default: global ("_")
    --type user-pass|ssh-key|secret-text    # <--- default: user-pass
    --description "Credential description"  # <--- default: ""
    --config-file config.json
    --config-as-json
```

- From monitoring developer tools:
    ```
    POST - http://localhost:8080/credentials/store/system/domain/_/createCredentials
    POST - http://localhost:8080/credentials/store/system/domain/_/createCredentials
    ```


- From Jenkins SDK:
    ```python
    CREATE_CREDENTIAL = '%(folder_url)sjob/%(short_name)s/credentials/store/folder/' \
                    'domain/%(domain_name)s/createCredentials'

    ...

    def create_credential(self, folder_name, config_xml,
                          domain_name='_'):
        '''Create credentail in domain of folder
        :param folder_name: Folder name, ``str``
        :param config_xml: New XML configuration, ``str``
        :param domain_name: Domain name, default is '_', ``str``
        '''
        folder_url, short_name = self._get_job_folder(folder_name)
        name = self._get_tag_text('id', config_xml)
        if self.credential_exists(name, folder_name, domain_name):
            raise JenkinsException('credential[%s] already exists '
                                   'in the domain[%s] of [%s]'
                                   % (name, domain_name, folder_name))

        self.jenkins_open(requests.Request(
                        'POST',
                        self._build_url(CREATE_CREDENTIAL, locals()),
                        data=config_xml.encode('utf-8'),
                        headers=DEFAULT_HEADERS
        ))
    ```

- Example from docs
    ```bash
    $ cat > credential.xml <<EOF
        <com.cloudbees.plugins.credentials.impl.UsernamePasswordCredentialsImpl>
        <scope>GLOBAL</scope>
        <id>deploy-key</id>
        <username>wecoyote</username>
        <password>secret123</password>
        </com.cloudbees.plugins.credentials.impl.UsernamePasswordCredentialsImpl>
    EOF

    $ curl -X POST -H content-type:application/xml -d @credential.xml \
        https://jenkins.example.com/job/example-folder/credentials/store/folder/domain/testing/createCredentials
    ```

- Web UI call data structure
    - **NOTE**: I don't think any of the `$class` need to be there
    - Username and Password
        ```json
        {
            "credentials": {
                "scope": "GLOBAL",
                "username": "USERNAME1",
                "usernameSecret": false,
                "password": "PASSWORD2",
                "$redact": "password",
                "id": "",
                "description": "DESCRIPTION",
                "stapler-class": "com.cloudbees.plugins.credentials.impl.UsernamePasswordCredentialsImpl",
                "$class": "com.cloudbees.plugins.credentials.impl.UsernamePasswordCredentialsImpl"
            }
        }
        ```

    - SSH - Username with Private Key
        ```json
        {
            "credentials": {
                "scope": "GLOBAL",
                "id": "",
                "description": "DESC1",
                "username": "USERNAME1",
                "usernameSecret": false,
                "privateKeySource": {
                    "value": "0",               // MAYBE NOT NEEDED
                    "privateKey": "PRIVATE KEY XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXxxx",
                    "stapler-class": "com.cloudbees.jenkins.plugins.sshcredentials.impl.BasicSSHUserPrivateKey$DirectEntryPrivateKeySource",
                    "$class": "com.cloudbees.jenkins.plugins.sshcredentials.impl.BasicSSHUserPrivateKey$DirectEntryPrivateKeySource"
                },
                "passphrase": "PASSWHRASE!",
                "$redact": "passphrase",
                "stapler-class": "com.cloudbees.jenkins.plugins.sshcredentials.impl.BasicSSHUserPrivateKey",
                "$class": "com.cloudbees.jenkins.plugins.sshcredentials.impl.BasicSSHUserPrivateKey"
            }
        }
        ```
    - Secret Text
        ```json
            {
                "credentials": {
                    "scope": "GLOBAL",
                    "secret": "SECRET1",
                    "$redact": "secret",
                    "id": "",
                    "description": "DESC1",
                    "stapler-class": "org.jenkinsci.plugins.plaincredentials.impl.StringCredentialsImpl",
                    "$class": "org.jenkinsci.plugins.plaincredentials.impl.StringCredentialsImpl"
                }
            }
        ```


## Domain information

- Form: `<SERVER>/credentials/store/<STORE>/domain/<DOMAIN>/_/api/json`
- Request: `http://localhost:8080/credentials/store/system/domain/_/api/json`
- Response:
    ```json
    {
        "_class": "com.cloudbees.plugins.credentials.CredentialsStoreAction$DomainWrapper",
        "credentials": [
            {},
            {},
            {}
        ],
        "description": "Credentials that should be available irrespective of domain specification to requirements matching.",
        "displayName": "Global credentials (unrestricted)",
        "fullDisplayName": "System » Global credentials (unrestricted)",
        "fullName": "system/_",
        "global": true,
        "urlName": "_"
    }
    ```


## Get information on one single credential
- Form: `<SERVER>/credentials/store/<STORE>/domain/<DOMAIN>/credential/<CRED ID>/api/json`
- Request: `http://localhost:8080/credentials/store/system/domain/_/credential/eaf28a93-6f20-4e65-99d6-37220f1355d9/api/json`
- Response:
    ```json
    {
        "_class": "com.cloudbees.plugins.credentials.CredentialsStoreAction$CredentialsWrapper",
        "description": "aws-key-1",
        "displayName": "ec2-user (aws-key-1)",
        "fingerprint": null,
        "fullName": "system/_/eaf28a93-6f20-4e65-99d6-37220f1355d9",
        "id": "eaf28a93-6f20-4e65-99d6-37220f1355d9",
        "typeName": "SSH Username with private key"
    }
    ```


## List all credentials in a store/domain

### Single Key

- Form: `<SERVER>/credentials/store/<STORE>/domain/<DOMAIN>/api/json?tree=credentials[<KEY>]`
- Request: `http://localhost:8080/credentials/store/system/domain/_/api/json?tree=credentials[id]`
- Response:
    ```json
    {
        "_class": "com.cloudbees.plugins.credentials.CredentialsStoreAction$DomainWrapper",
        "credentials": [
        {
            "883b70d2-b689-4a2b-98ba-c3d7037256c0"
        },
        {
            "eaf28a93-6f20-4e65-99d6-37220f1355d9"
        },
        {
            "15ad1f93-dc24-4f71-b92b-18ae9b13b1d0"
        }
        ]
    }
    ```

### All the Keys

- Form: `<SERVER>/credentials/store/<STORE>/domain/<DOMAIN>/api/json?tree=credentials[*]`
- Request: `http://localhost:8080/credentials/store/system/domain/_/api/json?tree=credentials[*]`
- Response:
    ```json
    {
        "_class": "com.cloudbees.plugins.credentials.CredentialsStoreAction$DomainWrapper",
        "credentials": [
        {
            "description": "yojenkins key",
            "displayName": "jenkins (yojenkins key)",
            "fingerprint": {},
            "fullName": "system/_/883b70d2-b689-4a2b-98ba-c3d7037256c0",
            "id": "883b70d2-b689-4a2b-98ba-c3d7037256c0",
            "typeName": "SSH Username with private key"
            },
            {
            "description": "aws-key-1",
            "displayName": "ec2-user (aws-key-1)",
            "fingerprint": null,
            "fullName": "system/_/eaf28a93-6f20-4e65-99d6-37220f1355d9",
            "id": "eaf28a93-6f20-4e65-99d6-37220f1355d9",
            "typeName": "SSH Username with private key"
            },
            {
            "description": "aws-key-1",
            "displayName": "jenkins (aws-key-1)",
            "fingerprint": {},
            "fullName": "system/_/15ad1f93-dc24-4f71-b92b-18ae9b13b1d0",
            "id": "15ad1f93-dc24-4f71-b92b-18ae9b13b1d0",
            "typeName": "SSH Username with private key"
            }
        ]
    }
    ```

## Get credentials configurations

- Form: `<SERVER>/credentials/store/<STORE>/domain/<DOMAIN>/credential/<CRED ID>/config.xml`
- Request: `http://localhost:8080/credentials/store/system/domain/_/credential/eaf28a93-6f20-4e65-99d6-37220f1355d9/config.xml`
- Response:
    ```xml
    <com.cloudbees.jenkins.plugins.sshcredentials.impl.BasicSSHUserPrivateKey plugin="ssh-credentials@1.19">
    <scope>GLOBAL</scope>
    <id>eaf28a93-6f20-4e65-99d6-37220f1355d9</id>
    <description>aws-key-1</description>
    <username>ec2-user</username>
    <usernameSecret>false</usernameSecret>
    <privateKeySource class="com.cloudbees.jenkins.plugins.sshcredentials.impl.BasicSSHUserPrivateKey$DirectEntryPrivateKeySource">
    <privateKey>
    <secret-redacted/>
    </privateKey>
    </privateKeySource>
    </com.cloudbees.jenkins.plugins.sshcredentials.impl.BasicSSHUserPrivateKey>

    ```
