"""Tests for yojenkins.cli.cli_utility module."""

import json
import logging
from unittest.mock import MagicMock, mock_open, patch

import pytest

from yojenkins.cli import cli_utility as cu
from yojenkins.yo_jenkins.exceptions import AuthenticationError, YoJenkinsException


class TestSetDebugLogLevel:
    """Tests for set_debug_log_level."""

    @patch('yojenkins.cli.cli_utility.platform_information')
    @patch('click.secho')
    def test_debug_true_sets_debug_level(self, mock_secho, mock_platform):
        """When debug_flag is True, logger level should be DEBUG."""
        logger = logging.getLogger()
        cu.set_debug_log_level(True)
        assert logger.level == logging.DEBUG

    @patch('yojenkins.cli.cli_utility.platform_information')
    @patch('click.secho')
    def test_debug_false_sets_info_level(self, mock_secho, mock_platform):
        """When debug_flag is False, logger level should be INFO."""
        logger = logging.getLogger()
        cu.set_debug_log_level(False)
        assert logger.level == logging.INFO

    @patch('yojenkins.cli.cli_utility.platform_information')
    @patch('click.secho')
    def test_debug_true_prints_header(self, mock_secho, mock_platform):
        """When debug_flag is True, should print debug header via click.secho."""
        cu.set_debug_log_level(True)
        assert mock_secho.call_count >= 1
        first_call_args = mock_secho.call_args_list[0]
        assert 'DEBUG' in first_call_args[0][0]

    @patch('yojenkins.cli.cli_utility.platform_information')
    @patch('click.secho')
    def test_debug_false_does_not_print_header(self, mock_secho, mock_platform):
        """When debug_flag is False, should not print debug header."""
        cu.set_debug_log_level(False)
        mock_secho.assert_not_called()


class TestStandardOut:
    """Tests for standard_out output formatting."""

    @patch('yojenkins.cli.cli_utility.print2')
    def test_json_output_default(self, mock_print2):
        """Default output should be JSON."""
        data = {'name': 'test', 'value': 42}
        cu.standard_out(data)
        call_arg = mock_print2.call_args[0][0]
        parsed = json.loads(call_arg)
        assert parsed['name'] == 'test'

    @patch('yojenkins.cli.cli_utility.print2')
    def test_json_pretty_output(self, mock_print2):
        """Pretty JSON output should be indented."""
        data = {'name': 'test'}
        cu.standard_out(data, opt_pretty=True)
        call_arg = mock_print2.call_args[0][0]
        assert '\n' in call_arg
        assert '    ' in call_arg

    @patch('yojenkins.cli.cli_utility.print2')
    def test_yaml_output(self, mock_print2):
        """YAML output flag should produce yaml-formatted text."""
        data = {'name': 'test'}
        cu.standard_out(data, opt_yaml=True)
        call_arg = mock_print2.call_args[0][0]
        assert 'name: test' in call_arg

    @patch('yojenkins.cli.cli_utility.print2')
    def test_toml_output(self, mock_print2):
        """TOML output flag should produce toml-formatted text."""
        data = {'name': 'test'}
        cu.standard_out(data, opt_toml=True)
        call_arg = mock_print2.call_args[0][0]
        assert 'name = "test"' in call_arg

    @patch('yojenkins.cli.cli_utility.print2')
    def test_toml_output_with_list_wraps_in_item_key(self, mock_print2):
        """TOML output with list data should wrap in 'item' key."""
        data = [{'a': 1}, {'b': 2}]
        cu.standard_out(data, opt_toml=True)
        call_arg = mock_print2.call_args[0][0]
        assert 'item' in call_arg

    @patch('yojenkins.cli.cli_utility.print2')
    def test_xml_output(self, mock_print2):
        """XML output flag should produce xml-formatted text."""
        data = {'name': 'test'}
        cu.standard_out(data, opt_xml=True)
        call_arg = mock_print2.call_args[0][0]
        assert '<name>' in call_arg
        assert 'test' in call_arg


class TestIsFullUrl:
    """Tests for is_full_url."""

    def test_full_url_returns_true(self):
        assert cu.is_full_url('http://localhost:8080/job/test') is True

    def test_https_url_returns_true(self):
        assert cu.is_full_url('https://jenkins.example.com/job/test') is True

    def test_name_only_returns_false(self):
        assert cu.is_full_url('my-folder') is False

    def test_missing_scheme_returns_false(self):
        assert cu.is_full_url('localhost:8080/job/test') is False


class TestLogToHistory:
    """Tests for log_to_history decorator."""

    @patch('builtins.open', mock_open())
    @patch('pathlib.Path.is_file', return_value=True)
    def test_decorated_function_still_called(self, mock_isfile):
        """The decorated function should still execute."""
        inner = MagicMock(return_value='result')
        inner.__name__ = 'inner'
        # Manually set argspec compatible attributes
        inner.__code__ = MagicMock()
        inner.__code__.co_varnames = ('profile',)
        inner.__defaults__ = None
        inner.__kwdefaults__ = None
        inner.__annotations__ = {}

        @cu.log_to_history
        def my_func(profile=None):
            return inner(profile)

        result = my_func(profile='default')
        inner.assert_called_once_with('default')

    @patch('builtins.open', mock_open())
    @patch('pathlib.Path.is_file', return_value=False)
    @patch('yojenkins.cli.cli_utility.create_new_history_file')
    def test_creates_history_file_if_missing(self, mock_create, mock_isfile):
        """If history file does not exist, create_new_history_file should be called."""

        @cu.log_to_history
        def my_func(profile=None):
            pass

        my_func(profile='default')
        mock_create.assert_called_once()


    @patch('builtins.open', mock_open())
    @patch('pathlib.Path.is_file', return_value=True)
    def test_env_var_disables_history(self, mock_isfile):
        """YOJENKINS_DISABLE_HISTORY=true should skip history logging."""
        write_calls = []
        original_open = open

        @cu.log_to_history
        def my_func(profile=None):
            pass

        import os
        os.environ['YOJENKINS_DISABLE_HISTORY'] = 'true'
        try:
            with patch('builtins.open', mock_open()) as mocked_file:
                my_func(profile='default')
                # open should not have been called for writing history
                for call in mocked_file.call_args_list:
                    assert 'a' not in str(call), "History file should not be opened for appending"
        finally:
            del os.environ['YOJENKINS_DISABLE_HISTORY']


class TestConfigYoJenkins:
    """Tests for config_yo_jenkins."""

    @patch('yojenkins.cli.cli_utility.YoJenkins')
    @patch('yojenkins.cli.cli_utility.Auth')
    @patch('yojenkins.cli.cli_utility.Rest')
    def test_returns_yojenkins_on_success(self, mock_rest_cls, mock_auth_cls, mock_yj_cls):
        """Should return a YoJenkins object when auth succeeds."""
        mock_auth = MagicMock()
        mock_auth.get_credentials.return_value = True
        mock_auth.create_auth.return_value = True
        mock_auth_cls.return_value = mock_auth
        mock_yj = MagicMock()
        mock_yj_cls.return_value = mock_yj

        result = cu.config_yo_jenkins('default', None)
        assert result == mock_yj
        mock_auth.get_credentials.assert_called_once_with('default')
        mock_auth.create_auth.assert_called_once_with(token=None)

    @patch('yojenkins.cli.cli_utility.YoJenkins')
    @patch('yojenkins.cli.cli_utility.Auth')
    @patch('yojenkins.cli.cli_utility.Rest')
    def test_raises_on_failed_credentials(self, mock_rest_cls, mock_auth_cls, mock_yj_cls):
        """Should raise YoJenkinsException if get_credentials fails."""
        mock_auth = MagicMock()
        mock_auth.get_credentials.side_effect = AuthenticationError('No profiles found')
        mock_auth_cls.return_value = mock_auth

        with pytest.raises(YoJenkinsException):
            cu.config_yo_jenkins('bad_profile', None)

    @patch('yojenkins.cli.cli_utility.YoJenkins')
    @patch('yojenkins.cli.cli_utility.Auth')
    @patch('yojenkins.cli.cli_utility.Rest')
    def test_raises_on_failed_auth(self, mock_rest_cls, mock_auth_cls, mock_yj_cls):
        """Should raise YoJenkinsException if create_auth fails."""
        mock_auth = MagicMock()
        mock_auth.get_credentials.return_value = True
        mock_auth.create_auth.side_effect = AuthenticationError('Auth failed')
        mock_auth_cls.return_value = mock_auth

        with pytest.raises(YoJenkinsException):
            cu.config_yo_jenkins('default', None)
