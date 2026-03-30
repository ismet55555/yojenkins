"""Integration tests for Credential operations against a live Jenkins instance."""

import pytest

pytestmark = [pytest.mark.docker, pytest.mark.slow]

CREDENTIAL_ID = 'integration-test-cred'


@pytest.fixture(scope='class')
def credential_config_file(tmp_path_factory):
    """Write a minimal credential XML config to a temp file."""
    xml_content = f"""<?xml version='1.1' encoding='UTF-8'?>
<com.cloudbees.plugins.credentials.impl.UsernamePasswordCredentialsImpl>
  <scope>GLOBAL</scope>
  <id>{CREDENTIAL_ID}</id>
  <description>Integration test credential</description>
  <username>testuser</username>
  <password>testpass</password>
</com.cloudbees.plugins.credentials.impl.UsernamePasswordCredentialsImpl>"""
    cred_file = tmp_path_factory.mktemp('creds') / 'test_credential.xml'
    cred_file.write_text(xml_content)
    return str(cred_file)


class TestCredentialIntegration:
    """Credential CRUD tests. Tests run in definition order."""

    def test_create_credential(self, yojenkins_instance, credential_config_file):
        """Create a username/password credential in the global domain."""
        result = yojenkins_instance.credential.create(
            config_file=credential_config_file,
            folder='.',
            domain='_',
        )
        assert result is True

    def test_list_credentials(self, yojenkins_instance):
        """List credentials; our created one should appear."""
        creds, _cred_names = yojenkins_instance.credential.list(
            domain='_',
            keys='all',
            folder='.',
        )
        assert len(creds) >= 1

    def test_credential_info(self, yojenkins_instance):
        """Get info on the specific credential."""
        info = yojenkins_instance.credential.info(
            credential=CREDENTIAL_ID,
            folder='.',
            domain='_',
        )
        assert isinstance(info, dict)

    def test_delete_credential(self, yojenkins_instance):
        """Delete the integration test credential."""
        result = yojenkins_instance.credential.delete(
            credential=CREDENTIAL_ID,
            folder='.',
            domain='_',
        )
        assert result is True
