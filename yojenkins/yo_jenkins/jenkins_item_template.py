"""Jenkins item template definition"""

from enum import Enum


class JenkinsItemTemplate(Enum):
    """Enum of Jenkins item templates ordered in categories

    Usage Examples:
        - `JenkinsItemTemplate.CREDENTIAL.value['ssh-user']`
    """

    CREDENTIAL = {
        "user-pass":
            '''
<com.cloudbees.plugins.credentials.impl.UsernamePasswordCredentialsImpl>
    <scope>${CRED_SCOPE_DOMAIN}</scope>
    <id>${CRED_ID}</id>
    <description>${CRED_DESCRIPTION}</description>
    <username>${CRED_USERNAME}</username>
    <password>${CRED_PASSWORD}</password>
    <usernameSecret>${CRED_USERNAME_AS_SECRET}</usernameSecret>
</com.cloudbees.plugins.credentials.impl.UsernamePasswordCredentialsImpl>''',
        "secret-text":
            '''
<org.jenkinsci.plugins.plaincredentials.impl.StringCredentialsImpl>
    <scope>${CRED_SCOPE_DOMAIN}</scope>
    <id>${CRED_ID}</id>
    <description>${CRED_DESCRIPTION}</description>
    <secret>${CRED_SECRET_TEXT}</secret>
</org.jenkinsci.plugins.plaincredentials.impl.StringCredentialsImpl>''',
        "ssh-key":
            '''
<com.cloudbees.jenkins.plugins.sshcredentials.impl.BasicSSHUserPrivateKey>
    <scope>${CRED_SCOPE_DOMAIN}</scope>
    <id>${CRED_ID}</id>
    <description>${CRED_DESCRIPTION}</description>
    <username>${CRED_USERNAME}</username>
    <usernameSecret>${CRED_USERNAME_AS_SECRET}</usernameSecret>
    <privateKeySource class="com.cloudbees.jenkins.plugins.sshcredentials.impl.BasicSSHUserPrivateKey$DirectEntryPrivateKeySource">
        <privateKey>${CRED_PRIVATE_KEY}</privateKey>
    </privateKeySource>
</com.cloudbees.jenkins.plugins.sshcredentials.impl.BasicSSHUserPrivateKey>'''
    }
