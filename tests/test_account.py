"""Tests for yojenkins.yo_jenkins.account.Account"""

from unittest.mock import patch

import pytest

from yojenkins.yo_jenkins.account import Account
from yojenkins.yo_jenkins.exceptions import YoJenkinsException


@pytest.fixture
def account(mock_rest):
    """Create an Account instance with mocked rest."""
    return Account(rest=mock_rest)


# --- Account.__init__ ---


class TestAccountInit:
    def test_init_sets_rest(self, mock_rest):
        acc = Account(rest=mock_rest)
        assert acc.rest is mock_rest

    def test_init_sets_groovy_script_directory(self, mock_rest):
        acc = Account(rest=mock_rest)
        assert str(acc.groovy_script_directory).endswith('groovy_scripts')


# --- Account.list ---


class TestAccountList:
    @patch('yojenkins.yo_jenkins.account.utility.run_groovy_script')
    def test_list_returns_accounts_and_ids(self, mock_groovy, account):
        mock_groovy.return_value = (
            [{'id': 'alice', 'name': 'Alice'}, {'id': 'bob', 'name': 'Bob'}],
            True,
            '',
        )
        account_list, account_ids = account.list()
        assert len(account_list) == 2
        assert account_ids == ['alice', 'bob']

    @patch('yojenkins.yo_jenkins.account.utility.run_groovy_script')
    def test_list_fail_out_on_failure(self, mock_groovy, account):
        mock_groovy.return_value = ([], False, 'some error')
        with pytest.raises(YoJenkinsException):
            account.list()

    @patch('yojenkins.yo_jenkins.account.utility.run_groovy_script')
    def test_list_skips_items_without_id(self, mock_groovy, account):
        mock_groovy.return_value = (
            [{'id': 'alice'}, {'name': 'no-id'}],
            True,
            '',
        )
        account_list, account_ids = account.list()
        assert account_ids == ['alice']


# --- Account.info ---


class TestAccountInfo:
    @patch('yojenkins.yo_jenkins.account.utility.run_groovy_script')
    def test_info_returns_matching_user(self, mock_groovy, account):
        mock_groovy.return_value = (
            [{'id': 'alice', 'name': 'Alice'}, {'id': 'bob', 'name': 'Bob'}],
            True,
            '',
        )
        result = account.info('bob')
        assert result == {'id': 'bob', 'name': 'Bob'}

    @patch('yojenkins.yo_jenkins.account.utility.run_groovy_script')
    def test_info_fail_out_on_request_failure(self, mock_groovy, account):
        mock_groovy.return_value = ([], False, 'error')
        with pytest.raises(YoJenkinsException):
            account.info('alice')

    @patch('yojenkins.yo_jenkins.account.utility.run_groovy_script')
    def test_info_fail_out_when_user_not_found(self, mock_groovy, account):
        mock_groovy.return_value = (
            [{'id': 'alice', 'name': 'Alice'}],
            True,
            '',
        )
        with pytest.raises(YoJenkinsException):
            account.info('nonexistent')


# --- Account.create ---


class TestAccountCreate:
    @patch('yojenkins.yo_jenkins.account.utility.run_groovy_script')
    def test_create_success(self, mock_groovy, account):
        mock_groovy.return_value = ('', True, '')
        result = account.create('newuser', 'pass123', is_admin=False, email='a@b.com', description='Test')
        assert result is True

    @patch('yojenkins.yo_jenkins.account.utility.run_groovy_script')
    def test_create_fail_out(self, mock_groovy, account):
        mock_groovy.return_value = ('', False, 'creation error')
        with pytest.raises(YoJenkinsException):
            account.create('newuser', 'pass123', is_admin=False, email='', description='')

    @patch('yojenkins.yo_jenkins.account.utility.run_groovy_script')
    def test_create_admin_sets_is_admin_true(self, mock_groovy, account):
        mock_groovy.return_value = ('', True, '')
        account.create('admin', 'pass', is_admin=True, email=None, description=None)
        call_kwargs = mock_groovy.call_args[1]
        assert call_kwargs['is_admin'] == 'true'


# --- Account.delete ---


class TestAccountDelete:
    @patch('yojenkins.yo_jenkins.account.utility.run_groovy_script')
    def test_delete_success(self, mock_groovy, account):
        mock_groovy.return_value = ('', True, '')
        result = account.delete('olduser')
        assert result is True

    @patch('yojenkins.yo_jenkins.account.utility.run_groovy_script')
    def test_delete_fail_out(self, mock_groovy, account):
        mock_groovy.return_value = ('', False, 'delete error')
        with pytest.raises(YoJenkinsException):
            account.delete('olduser')


# --- Account.permission ---


class TestAccountPermission:
    @patch('yojenkins.yo_jenkins.account.utility.run_groovy_script')
    @patch('yojenkins.yo_jenkins.account.utility.parse_and_check_input_string_list', return_value='perm1, perm2')
    def test_permission_add(self, mock_parse, mock_groovy, account):
        mock_groovy.return_value = ('', True, '')
        result = account.permission('alice', 'add', 'perm1,perm2')
        assert result is True
        call_kwargs = mock_groovy.call_args[1]
        assert call_kwargs['permission_enabled'] == 'true'

    @patch('yojenkins.yo_jenkins.account.utility.run_groovy_script')
    @patch('yojenkins.yo_jenkins.account.utility.parse_and_check_input_string_list', return_value='perm1')
    def test_permission_remove(self, mock_parse, mock_groovy, account):
        mock_groovy.return_value = ('', True, '')
        result = account.permission('alice', 'remove', 'perm1')
        assert result is True
        call_kwargs = mock_groovy.call_args[1]
        assert call_kwargs['permission_enabled'] == 'false'

    @patch('yojenkins.yo_jenkins.account.utility.parse_and_check_input_string_list', return_value='perm1')
    def test_permission_invalid_action_fail_out(self, mock_parse, account):
        with pytest.raises(YoJenkinsException):
            account.permission('alice', 'invalid', 'perm1')


# --- Account.permission_list ---


class TestAccountPermissionList:
    @patch('yojenkins.yo_jenkins.account.utility.run_groovy_script')
    def test_permission_list_returns_ids(self, mock_groovy, account):
        mock_groovy.return_value = (
            [
                {'id': 'hudson.model.Item.GenericRead', 'description': 'Read'},
                {'id': 'hudson.model.Item.Build', 'description': 'Build'},
            ],
            True,
            '',
        )
        perm_list, perm_ids = account.permission_list()
        # GenericRead -> last part uppercased with GENERIC removed -> READ
        assert 'hudson.model.Item.READ' in perm_ids
        assert 'hudson.model.Item.BUILD' in perm_ids

    @patch('yojenkins.yo_jenkins.account.utility.run_groovy_script')
    def test_permission_list_fail_out(self, mock_groovy, account):
        mock_groovy.return_value = ([], False, 'error')
        with pytest.raises(YoJenkinsException):
            account.permission_list()
