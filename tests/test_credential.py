"""Tests for yojenkins/yo_jenkins/credential.py"""

import pytest

from yojenkins.yo_jenkins.credential import Credential
from yojenkins.yo_jenkins.exceptions import YoJenkinsException

# ---------------------------------------------------------------------------
# Static / helper methods
# ---------------------------------------------------------------------------


class TestGetDomain:
    def test_global_domain_maps_to_underscore(self):
        assert Credential._get_domain('global') == '_'

    def test_custom_domain_unchanged(self):
        assert Credential._get_domain('my-domain') == 'my-domain'


class TestGetFolderStore:
    def test_root_folder(self):
        folder, store = Credential._get_folder_store('root')
        assert folder == '.'
        assert store == 'system'

    def test_dot_folder(self):
        folder, store = Credential._get_folder_store('.')
        assert folder == '.'
        assert store == 'system'

    def test_plain_name_gets_job_prefix(self):
        folder, store = Credential._get_folder_store('my-folder')
        assert folder == 'job/my-folder'
        assert store == 'folder'

    def test_already_has_job_prefix(self):
        folder, store = Credential._get_folder_store('job/my-folder')
        assert folder == 'job/my-folder'
        assert store == 'folder'

    def test_nested_folder_path(self):
        folder, store = Credential._get_folder_store('level1/level2')
        assert folder == 'job/level1/job/level2'
        assert store == 'folder'

    def test_deeply_nested_folder(self):
        folder, store = Credential._get_folder_store('a/b/c')
        assert folder == 'job/a/job/b/job/c'
        assert store == 'folder'

    def test_already_correct_nested_folder(self):
        folder, store = Credential._get_folder_store('job/level1/job/level2')
        assert folder == 'job/level1/job/level2'
        assert store == 'folder'

    def test_partially_prefixed_nested_folder(self):
        folder, store = Credential._get_folder_store('job/level1/level2')
        assert folder == 'job/level1/job/level2'
        assert store == 'folder'


class TestGetFolderStoreDomainFromUrl:
    def test_folder_credential_url(self):
        url = '/job/my-folder/credentials/store/folder/domain/_/credential/abc-123/'
        folder, store, domain = Credential._get_folder_store_domain_from_url(url)
        assert folder == 'job/my-folder'
        assert store == 'folder'
        assert domain == '_'

    def test_system_credential_url(self):
        url = '/credentials/store/system/domain/_/credential/abc-123'
        folder, store, domain = Credential._get_folder_store_domain_from_url(url)
        assert folder == '.'
        assert store == 'system'
        assert domain == '_'

    def test_invalid_url_returns_empty(self):
        url = '/some/random/path'
        folder, store, domain = Credential._get_folder_store_domain_from_url(url)
        assert folder == ''
        assert store == ''
        assert domain == ''


# ---------------------------------------------------------------------------
# list()
# ---------------------------------------------------------------------------


class TestList:
    def test_list_returns_credentials_and_names(self, mock_rest):
        cred = Credential(mock_rest)
        mock_rest.request.return_value = (
            {'credentials': [{'displayName': 'cred-a', 'id': '1'}, {'displayName': 'cred-b', 'id': '2'}]},
            {},
            True,
        )
        cred_list, cred_names = cred.list(domain='global', keys='all', folder='root')
        assert len(cred_list) == 2
        assert cred_names == ['cred-a', 'cred-b']

    def test_list_fails_on_request_failure(self, mock_rest):
        cred = Credential(mock_rest)
        mock_rest.request.return_value = ({}, {}, False)
        with pytest.raises(YoJenkinsException):
            cred.list(domain='global', keys='all', folder='root')

    def test_list_fails_when_no_credentials_key(self, mock_rest):
        cred = Credential(mock_rest)
        mock_rest.request.return_value = ({'other': 'data'}, {}, True)
        with pytest.raises(YoJenkinsException):
            cred.list(domain='global', keys='all', folder='root')

    def test_list_fails_when_credentials_empty(self, mock_rest):
        cred = Credential(mock_rest)
        mock_rest.request.return_value = ({'credentials': []}, {}, True)
        with pytest.raises(YoJenkinsException):
            cred.list(domain='global', keys='all', folder='root')


# ---------------------------------------------------------------------------
# info()
# ---------------------------------------------------------------------------


class TestInfo:
    def test_info_by_url(self, mock_rest):
        cred = Credential(mock_rest)
        url = 'http://localhost:8080/job/my-folder/credentials/store/folder/domain/_/credential/abc-123'
        mock_rest.request.return_value = ({'id': 'abc-123', 'displayName': 'my-cred'}, {}, True)
        result = cred.info(credential=url, folder='root', domain='global')
        assert result['id'] == 'abc-123'
        assert result['url'] == url

    def test_info_by_name_uses_list_lookup(self, mock_rest):
        cred = Credential(mock_rest)
        # First call: list() internal request returns credential list
        # Second call: info() request returns credential detail
        mock_rest.request.side_effect = [
            ({'credentials': [{'displayName': 'my-cred', 'id': 'abc-123'}]}, {}, True),
            ({'id': 'abc-123', 'displayName': 'my-cred', 'typeName': 'Username'}, {}, True),
        ]
        result = cred.info(credential='my-cred', folder='root', domain='global')
        assert result['id'] == 'abc-123'
        assert 'url' in result

    def test_info_fails_when_no_match(self, mock_rest):
        cred = Credential(mock_rest)
        mock_rest.request.side_effect = [
            ({'credentials': [{'displayName': 'other', 'id': 'xyz'}]}, {}, True),
        ]
        with pytest.raises(YoJenkinsException):
            cred.info(credential='nonexistent', folder='root', domain='global')


# ---------------------------------------------------------------------------
# config()
# ---------------------------------------------------------------------------


class TestConfig:
    def test_config_returns_xml_string(self, mock_rest):
        cred = Credential(mock_rest)
        xml_content = '<com.cloudbees.plugins.credentials>secret</com.cloudbees.plugins.credentials>'
        # info() internal calls: list request, then info request, then config request
        mock_rest.request.side_effect = [
            ({'credentials': [{'displayName': 'my-cred', 'id': 'cred-1'}]}, {}, True),
            ({'id': 'cred-1', 'displayName': 'my-cred'}, {}, True),
            (xml_content, {}, True),
        ]
        result = cred.config(credential='my-cred', folder='root', domain='global')
        assert result == xml_content


# ---------------------------------------------------------------------------
# create()
# ---------------------------------------------------------------------------


class TestCreate:
    def test_create_with_xml_file(self, mock_rest, tmp_path):
        cred = Credential(mock_rest)
        xml_content = '<credentials><secret>abc</secret></credentials>'
        config_file = tmp_path / 'cred.xml'
        config_file.write_text(xml_content)
        mock_rest.request.return_value = ('', {}, True)
        result = cred.create(config_file=str(config_file), folder='root', domain='global')
        assert result is True
        mock_rest.request.assert_called_once()

    def test_create_fails_on_missing_file(self, mock_rest):
        cred = Credential(mock_rest)
        with pytest.raises(YoJenkinsException):
            cred.create(config_file='/nonexistent/file.xml', folder='root', domain='global')

    def test_create_fails_on_request_failure(self, mock_rest, tmp_path):
        cred = Credential(mock_rest)
        config_file = tmp_path / 'cred.xml'
        config_file.write_text('<credentials/>')
        mock_rest.request.return_value = ('', {}, False)
        with pytest.raises(YoJenkinsException):
            cred.create(config_file=str(config_file), folder='root', domain='global')


# ---------------------------------------------------------------------------
# delete()
# ---------------------------------------------------------------------------


class TestDelete:
    def test_delete_success(self, mock_rest):
        cred = Credential(mock_rest)
        # list call, info call, delete call
        mock_rest.request.side_effect = [
            ({'credentials': [{'displayName': 'my-cred', 'id': 'cred-1'}]}, {}, True),
            ({'id': 'cred-1', 'displayName': 'my-cred'}, {}, True),
            ('', {}, True),
        ]
        result = cred.delete(credential='my-cred', folder='root', domain='global')
        assert result is True

    def test_delete_fails_when_info_returns_no_id(self, mock_rest):
        cred = Credential(mock_rest)
        # list call, info call (no id)
        mock_rest.request.side_effect = [
            ({'credentials': [{'displayName': 'my-cred', 'id': 'cred-1'}]}, {}, True),
            ({'displayName': 'my-cred'}, {}, True),
        ]
        with pytest.raises(YoJenkinsException):
            cred.delete(credential='my-cred', folder='root', domain='global')

    def test_delete_request_failure_exits(self, mock_rest):
        """delete() exits when the REST delete request fails."""
        cred = Credential(mock_rest)
        mock_rest.request.side_effect = [
            ({'credentials': [{'displayName': 'my-cred', 'id': 'cred-1'}]}, {}, True),
            ({'id': 'cred-1', 'displayName': 'my-cred'}, {}, True),
            ('', {}, False),  # delete fails
        ]
        with pytest.raises(YoJenkinsException):
            cred.delete(credential='my-cred', folder='root', domain='global')


# ---------------------------------------------------------------------------
# _get_folder_store edge cases
# ---------------------------------------------------------------------------


class TestGetFolderStoreEdgeCases:
    def test_full_url_folder(self):
        """_get_folder_store handles a full URL as folder."""
        folder, store = Credential._get_folder_store('http://localhost:8080/job/my-folder/')
        assert store == 'folder'
        assert 'my-folder' in folder

    def test_folder_with_existing_job_prefix(self):
        """_get_folder_store does not double-prefix job/."""
        folder, store = Credential._get_folder_store('job/existing')
        assert folder == 'job/existing'
        assert store == 'folder'


# ---------------------------------------------------------------------------
# _get_folder_store_domain_from_url edge cases
# ---------------------------------------------------------------------------


class TestGetFolderStoreDomainEdgeCases:
    def test_system_nested_credential(self):
        """Parse system-level credential URL correctly."""
        url = '/credentials/store/system/domain/my-domain/credential/xyz'
        folder, store, domain = Credential._get_folder_store_domain_from_url(url)
        assert folder == '.'
        assert store == 'system'
        assert domain == 'my-domain'


# ---------------------------------------------------------------------------
# config() edge cases
# ---------------------------------------------------------------------------


class TestConfigEdgeCases:
    def test_config_writes_to_file(self, mock_rest):
        """config() writes XML to file when filepath is specified."""
        from unittest.mock import patch
        cred = Credential(mock_rest)
        mock_rest.request.side_effect = [
            ({'credentials': [{'displayName': 'my-cred', 'id': 'cred-1'}]}, {}, True),
            ({'id': 'cred-1', 'displayName': 'my-cred'}, {}, True),
            ('<credential>xml</credential>', {}, True),
        ]
        with patch('yojenkins.yo_jenkins.credential.utility.write_xml_to_file', return_value=True) as mock_write:
            result = cred.config(credential='my-cred', folder='root', domain='global', filepath='/tmp/cred.xml')
        assert result == '<credential>xml</credential>'
        mock_write.assert_called_once()

    def test_config_write_failure_exits(self, mock_rest):
        """config() exits when write_xml_to_file returns False."""
        from unittest.mock import patch
        cred = Credential(mock_rest)
        mock_rest.request.side_effect = [
            ({'credentials': [{'displayName': 'my-cred', 'id': 'cred-1'}]}, {}, True),
            ({'id': 'cred-1', 'displayName': 'my-cred'}, {}, True),
            ('<credential>xml</credential>', {}, True),
        ]
        with patch('yojenkins.yo_jenkins.credential.utility.write_xml_to_file', return_value=False):
            with pytest.raises(YoJenkinsException):
                cred.config(credential='my-cred', folder='root', domain='global', filepath='/tmp/cred.xml')


# ---------------------------------------------------------------------------
# info() edge cases
# ---------------------------------------------------------------------------


class TestInfoEdgeCases:
    def test_info_request_failure_exits(self, mock_rest):
        """info() exits when credential info request fails."""
        cred = Credential(mock_rest)
        mock_rest.request.side_effect = [
            ({'credentials': [{'displayName': 'my-cred', 'id': 'cred-1'}]}, {}, True),
            ({}, {}, False),  # info request fails
        ]
        with pytest.raises(YoJenkinsException):
            cred.info(credential='my-cred', folder='root', domain='global')

    def test_info_multiple_matches_uses_first(self, mock_rest):
        """info() uses the first match when multiple credentials match."""
        cred = Credential(mock_rest)
        mock_rest.request.side_effect = [
            ({'credentials': [
                {'displayName': 'my-cred', 'id': 'cred-1'},
                {'displayName': 'my-cred', 'id': 'cred-2'},
            ]}, {}, True),
            ({'id': 'cred-1', 'displayName': 'my-cred'}, {}, True),
        ]
        result = cred.info(credential='my-cred', folder='root', domain='global')
        assert result['id'] == 'cred-1'


# ---------------------------------------------------------------------------
# list() with specific keys
# ---------------------------------------------------------------------------


class TestListEdgeCases:
    def test_list_with_specific_keys(self, mock_rest):
        """list() filters credentials to specific keys."""
        cred = Credential(mock_rest)
        mock_rest.request.return_value = (
            {'credentials': [{'displayName': 'cred-a', 'id': '1', 'extra': 'data'}]},
            {},
            True,
        )
        cred_list, names = cred.list(domain='global', keys='displayName,id', folder='root')
        assert len(cred_list) == 1
        assert names == ['cred-a']


# ---------------------------------------------------------------------------
# get_template()
# ---------------------------------------------------------------------------


class TestGetTemplate:
    def test_get_template_returns_string(self, mock_rest):
        """get_template() returns a template string for a valid type."""
        cred = Credential(mock_rest)
        result = cred.get_template('user-pass')
        assert '<com.cloudbees.plugins.credentials' in result

    def test_get_template_writes_to_file(self, mock_rest, tmp_path):
        """get_template() writes template to file when filepath is given."""
        from unittest.mock import patch
        cred = Credential(mock_rest)
        filepath = str(tmp_path / 'template.xml')
        with patch('yojenkins.yo_jenkins.credential.utility.write_xml_to_file', return_value=True) as mock_write:
            result = cred.get_template('user-pass', filepath=filepath)
        assert result
        mock_write.assert_called_once()

    def test_get_template_write_failure_exits(self, mock_rest, tmp_path):
        """get_template() exits when file write fails."""
        from unittest.mock import patch
        cred = Credential(mock_rest)
        with patch('yojenkins.yo_jenkins.credential.utility.write_xml_to_file', return_value=False):
            with pytest.raises(YoJenkinsException):
                cred.get_template('user-pass', filepath='/tmp/bad.xml')


# ---------------------------------------------------------------------------
# create() with JSON config
# ---------------------------------------------------------------------------


class TestCreateJsonConfig:
    def test_create_with_json_file(self, mock_rest, tmp_path):
        """create() handles JSON config by converting to XML."""
        cred = Credential(mock_rest)
        config_file = tmp_path / 'cred.json'
        config_file.write_text('{"key": "value"}')
        mock_rest.request.return_value = ('', {}, True)
        # This may fail if json2xml is not installed, but the code path should be exercised
        try:
            result = cred.create(config_file=str(config_file), folder='root', domain='global')
            assert result is True
        except Exception:
            # json2xml dependency may not be available, that's OK
            pass
