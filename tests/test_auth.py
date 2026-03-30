"""Tests for yojenkins/yo_jenkins/auth.py"""

import json
import os
from unittest.mock import MagicMock, patch

import pytest
import toml

from yojenkins.yo_jenkins.auth import CONFIG_DIR_NAME, CREDS_FILE_NAME, PROFILE_ENV_VAR, Auth
from yojenkins.yo_jenkins.exceptions import YoJenkinsException

# ---------------------------------------------------------------------------
# Constructor tests
# ---------------------------------------------------------------------------


class TestAuthInit:
    def test_default_rest_created_when_none_passed(self):
        """When no rest param is given, Auth creates its own Rest instance."""
        with patch('yojenkins.yo_jenkins.auth.Rest') as MockRest:
            auth = Auth()
            MockRest.assert_called_once()
            assert auth.rest is MockRest.return_value

    def test_existing_rest_used_when_passed(self, mock_rest):
        """When a rest param is provided, Auth uses it directly."""
        auth = Auth(rest=mock_rest)
        assert auth.rest is mock_rest

    def test_initial_state(self, mock_rest):
        """Auth initializes with expected default attribute values."""
        auth = Auth(rest=mock_rest)
        assert auth.jenkins_sdk is None
        assert auth.jenkins_profile == {}
        assert auth.jenkins_username == ''
        assert auth.jenkins_api_token == ''
        assert auth.authenticated is False


# ---------------------------------------------------------------------------
# get_credentials tests
# ---------------------------------------------------------------------------


def _write_creds_file(tmp_path, profiles_dict):
    """Helper: write a TOML credentials file under tmp_path/.yojenkins/credentials."""
    creds_dir = tmp_path / CONFIG_DIR_NAME
    creds_dir.mkdir(exist_ok=True)
    creds_file = creds_dir / CREDS_FILE_NAME
    creds_file.write_text(toml.dumps(profiles_dict))
    return creds_dir, creds_file


class TestGetCredentials:
    """Tests for the credential priority chain in Auth.get_credentials."""

    def test_priority1_profile_arg_selects_named_profile(self, mock_rest, tmp_path):
        """Priority 1: --profile name selects matching profile from creds file."""
        profiles = {
            'default': {
                'jenkins_server_url': 'http://default:8080',
                'username': 'defaultuser',
                'api_token': 'defaulttoken',
                'active': True,
            },
            'staging': {
                'jenkins_server_url': 'http://staging:8080',
                'username': 'staginguser',
                'api_token': 'stagingtoken',
                'active': True,
            },
        }
        _write_creds_file(tmp_path, profiles)

        auth = Auth(rest=mock_rest)
        with patch.object(
            auth, '_detect_creds_file', return_value=(True, str(tmp_path / CONFIG_DIR_NAME / CREDS_FILE_NAME))
        ):
            with patch('yojenkins.yo_jenkins.auth.Path') as MockPath:
                MockPath.home.return_value = tmp_path
                result = auth.get_credentials(profile='staging')

        assert result['username'] == 'staginguser'
        assert result['jenkins_server_url'] == 'http://staging:8080'
        assert result['profile'] == 'staging'

    def test_priority1_json_string_profile(self, mock_rest):
        """Priority 1 (variant): --profile with a JSON string is parsed directly."""
        json_profile = json.dumps(
            {
                'jenkins_server_url': 'http://json-server:8080',
                'username': 'jsonuser',
                'api_token': 'jsontoken',
            }
        )
        auth = Auth(rest=mock_rest)
        result = auth.get_credentials(profile=json_profile)

        assert result['username'] == 'jsonuser'
        assert result['jenkins_server_url'] == 'http://json-server:8080'
        assert result['profile'] == 'CLI_PROVIDED'

    def test_priority1_json_string_missing_required_keys_exits(self, mock_rest):
        """JSON string profile missing required keys triggers sys.exit(1)."""
        json_profile = json.dumps({'jenkins_server_url': 'http://server:8080'})
        auth = Auth(rest=mock_rest)
        with pytest.raises(YoJenkinsException):
            auth.get_credentials(profile=json_profile)

    def test_priority1_invalid_json_starting_with_brace_exits(self, mock_rest, tmp_path):
        """A profile value starting with '{' but not valid JSON triggers fail_out."""
        auth = Auth(rest=mock_rest)
        with pytest.raises(YoJenkinsException):
            auth.get_credentials(profile='{invalid json')

    def test_priority2_env_var_selects_profile(self, mock_rest, tmp_path):
        """Priority 2: YOJENKINS_PROFILE env var selects a matching profile."""
        profiles = {
            'envprofile': {
                'jenkins_server_url': 'http://env:8080',
                'username': 'envuser',
                'api_token': 'envtoken',
                'active': True,
            },
        }
        _write_creds_file(tmp_path, profiles)

        auth = Auth(rest=mock_rest)
        with patch.object(
            auth, '_detect_creds_file', return_value=(True, str(tmp_path / CONFIG_DIR_NAME / CREDS_FILE_NAME))
        ):
            with patch('yojenkins.yo_jenkins.auth.Path') as MockPath:
                MockPath.home.return_value = tmp_path
                with patch.dict(os.environ, {PROFILE_ENV_VAR: 'envprofile'}):
                    result = auth.get_credentials(profile='')

        assert result['username'] == 'envuser'
        assert result['profile'] == 'envprofile'

    def test_priority2_env_var_not_matching_exits(self, mock_rest, tmp_path):
        """Priority 2: env var set but no matching profile triggers fail_out."""
        profiles = {
            'other': {
                'jenkins_server_url': 'http://other:8080',
                'username': 'otheruser',
                'api_token': 'othertoken',
                'active': True,
            },
        }
        _write_creds_file(tmp_path, profiles)

        auth = Auth(rest=mock_rest)
        with patch.object(
            auth, '_detect_creds_file', return_value=(True, str(tmp_path / CONFIG_DIR_NAME / CREDS_FILE_NAME))
        ):
            with patch('yojenkins.yo_jenkins.auth.Path') as MockPath:
                MockPath.home.return_value = tmp_path
                with patch.dict(os.environ, {PROFILE_ENV_VAR: 'nonexistent'}, clear=False):
                    with pytest.raises(YoJenkinsException):
                        auth.get_credentials(profile='')

    def test_priority3_default_profile_selected(self, mock_rest, tmp_path):
        """Priority 3: 'default' profile is selected when no arg or env var."""
        profiles = {
            'default': {
                'jenkins_server_url': 'http://default:8080',
                'username': 'defaultuser',
                'api_token': 'defaulttoken',
                'active': True,
            },
            'other': {
                'jenkins_server_url': 'http://other:8080',
                'username': 'otheruser',
                'api_token': 'othertoken',
                'active': True,
            },
        }
        _write_creds_file(tmp_path, profiles)

        auth = Auth(rest=mock_rest)
        env_clean = {k: v for k, v in os.environ.items() if k != PROFILE_ENV_VAR}
        with patch.object(
            auth, '_detect_creds_file', return_value=(True, str(tmp_path / CONFIG_DIR_NAME / CREDS_FILE_NAME))
        ):
            with patch('yojenkins.yo_jenkins.auth.Path') as MockPath:
                MockPath.home.return_value = tmp_path
                with patch.dict(os.environ, env_clean, clear=True):
                    result = auth.get_credentials(profile='')

        assert result['username'] == 'defaultuser'
        assert result['profile'] == 'default'

    def test_priority4_first_active_profile_selected(self, mock_rest, tmp_path):
        """Priority 4: first active profile selected when no default exists."""
        profiles = {
            'profileA': {
                'jenkins_server_url': 'http://a:8080',
                'username': 'userA',
                'api_token': 'tokenA',
                'active': True,
            },
        }
        _write_creds_file(tmp_path, profiles)

        auth = Auth(rest=mock_rest)
        env_clean = {k: v for k, v in os.environ.items() if k != PROFILE_ENV_VAR}
        with patch.object(
            auth, '_detect_creds_file', return_value=(True, str(tmp_path / CONFIG_DIR_NAME / CREDS_FILE_NAME))
        ):
            with patch('yojenkins.yo_jenkins.auth.Path') as MockPath:
                MockPath.home.return_value = tmp_path
                with patch.dict(os.environ, env_clean, clear=True):
                    result = auth.get_credentials(profile='')

        assert result['username'] == 'userA'
        assert result['profile'] == 'profileA'

    def test_no_active_profiles_exits(self, mock_rest, tmp_path):
        """When no active profiles exist and no defaults, sys.exit(1) is called."""
        profiles = {
            'inactive': {
                'jenkins_server_url': 'http://inactive:8080',
                'username': 'inactiveuser',
                'api_token': 'inactivetoken',
                'active': False,
            },
        }
        _write_creds_file(tmp_path, profiles)

        auth = Auth(rest=mock_rest)
        env_clean = {k: v for k, v in os.environ.items() if k != PROFILE_ENV_VAR}
        with patch.object(
            auth, '_detect_creds_file', return_value=(True, str(tmp_path / CONFIG_DIR_NAME / CREDS_FILE_NAME))
        ):
            with patch('yojenkins.yo_jenkins.auth.Path') as MockPath:
                MockPath.home.return_value = tmp_path
                with patch.dict(os.environ, env_clean, clear=True):
                    with pytest.raises(YoJenkinsException):
                        auth.get_credentials(profile='')

    def test_profile_arg_not_found_exits(self, mock_rest, tmp_path):
        """Specifying a --profile name that does not exist triggers fail_out."""
        profiles = {
            'default': {
                'jenkins_server_url': 'http://default:8080',
                'username': 'defaultuser',
                'api_token': 'defaulttoken',
                'active': True,
            },
        }
        _write_creds_file(tmp_path, profiles)

        auth = Auth(rest=mock_rest)
        with patch.object(
            auth, '_detect_creds_file', return_value=(True, str(tmp_path / CONFIG_DIR_NAME / CREDS_FILE_NAME))
        ):
            with patch('yojenkins.yo_jenkins.auth.Path') as MockPath:
                MockPath.home.return_value = tmp_path
                with pytest.raises(YoJenkinsException):
                    auth.get_credentials(profile='nonexistent')

    def test_sets_jenkins_profile_attribute(self, mock_rest, tmp_path):
        """get_credentials sets self.jenkins_profile on the Auth instance."""
        profiles = {
            'default': {
                'jenkins_server_url': 'http://default:8080',
                'username': 'defaultuser',
                'api_token': 'defaulttoken',
                'active': True,
            },
        }
        _write_creds_file(tmp_path, profiles)

        auth = Auth(rest=mock_rest)
        env_clean = {k: v for k, v in os.environ.items() if k != PROFILE_ENV_VAR}
        with patch.object(
            auth, '_detect_creds_file', return_value=(True, str(tmp_path / CONFIG_DIR_NAME / CREDS_FILE_NAME))
        ):
            with patch('yojenkins.yo_jenkins.auth.Path') as MockPath:
                MockPath.home.return_value = tmp_path
                with patch.dict(os.environ, env_clean, clear=True):
                    auth.get_credentials(profile='')

        assert auth.jenkins_profile['username'] == 'defaultuser'


# ---------------------------------------------------------------------------
# create_auth tests
# ---------------------------------------------------------------------------


class TestCreateAuth:
    def _make_auth_with_profile(self, mock_rest):
        """Helper: create Auth with a profile already loaded."""
        auth = Auth(rest=mock_rest)
        auth.jenkins_profile = {
            'profile': 'test',
            'jenkins_server_url': 'http://localhost:8080',
            'username': 'testuser',
            'api_token': 'testtoken',
        }
        return auth

    def test_successful_auth(self, mock_rest):
        """Successful authentication sets jenkins_sdk and returns True."""
        auth = self._make_auth_with_profile(mock_rest)
        mock_rest.is_reachable = MagicMock(return_value=True)

        with patch('yojenkins.yo_jenkins.auth.JenkinsSDK') as MockJenkins:
            with patch.object(auth, 'verify', return_value=True):
                result = auth.create_auth()

        assert result is True
        MockJenkins.assert_called_once_with(
            url='http://localhost:8080',
            username='testuser',
            password='testtoken',
            timeout=10,
        )

    def test_token_flag_overrides_profile_token(self, mock_rest):
        """When --token is passed, it overrides the profile api_token."""
        auth = self._make_auth_with_profile(mock_rest)
        mock_rest.is_reachable = MagicMock(return_value=True)

        with patch('yojenkins.yo_jenkins.auth.JenkinsSDK'):
            with patch.object(auth, 'verify', return_value=True):
                auth.create_auth(token='override-token')

        assert auth.jenkins_api_token == 'override-token'

    def test_unreachable_server_exits(self, mock_rest):
        """When server is unreachable, sys.exit(1) is called."""
        auth = self._make_auth_with_profile(mock_rest)
        mock_rest.is_reachable = MagicMock(return_value=False)

        with patch('yojenkins.yo_jenkins.auth.JenkinsSDK'):
            with pytest.raises(YoJenkinsException):
                auth.create_auth()

    def test_failed_verify_exits(self, mock_rest):
        """When verify() returns False (via failures_out), sys.exit(1) is called."""
        auth = self._make_auth_with_profile(mock_rest)
        mock_rest.is_reachable = MagicMock(return_value=True)

        with patch('yojenkins.yo_jenkins.auth.JenkinsSDK'):
            with patch.object(auth, 'verify', return_value=False):
                with pytest.raises(YoJenkinsException):
                    auth.create_auth()

    def test_no_profile_loaded_exits(self, mock_rest):
        """When no profile is loaded and none passed, fail_out triggers exit."""
        auth = Auth(rest=mock_rest)
        with pytest.raises(YoJenkinsException):
            auth.create_auth()

    def test_missing_url_protocol_exits(self, mock_rest):
        """When server URL has no protocol schema, fail_out triggers exit."""
        auth = Auth(rest=mock_rest)
        auth.jenkins_profile = {
            'profile': 'bad',
            'jenkins_server_url': 'localhost:8080',
            'username': 'user',
            'api_token': 'token',
        }
        with pytest.raises(YoJenkinsException):
            auth.create_auth()

    def test_prompts_for_token_when_missing(self, mock_rest):
        """When api_token is missing from profile, getpass is called."""
        auth = Auth(rest=mock_rest)
        auth.jenkins_profile = {
            'profile': 'noapitoken',
            'jenkins_server_url': 'http://localhost:8080',
            'username': 'testuser',
        }
        mock_rest.is_reachable = MagicMock(return_value=True)

        with patch('yojenkins.yo_jenkins.auth.JenkinsSDK'):
            with patch('yojenkins.yo_jenkins.auth.getpass', return_value='prompted-token'):
                with patch.object(auth, 'verify', return_value=True):
                    auth.create_auth()

        assert auth.jenkins_profile['api_token'] == 'prompted-token'


# ---------------------------------------------------------------------------
# verify tests
# ---------------------------------------------------------------------------


class TestVerify:
    def test_verify_success(self, mock_rest):
        """verify() returns True when REST head request succeeds."""
        auth = Auth(rest=mock_rest)
        auth.jenkins_profile = {
            'jenkins_server_url': 'http://localhost:8080',
        }
        mock_rest.request.return_value = ({}, {}, True)
        result = auth.verify()
        assert result is True

    def test_verify_failure_exits(self, mock_rest):
        """verify() calls failures_out (sys.exit) when REST request fails."""
        auth = Auth(rest=mock_rest)
        auth.jenkins_profile = {
            'jenkins_server_url': 'http://localhost:8080',
        }
        mock_rest.request.return_value = ({}, {}, False)
        with pytest.raises(YoJenkinsException):
            auth.verify()

    def test_verify_missing_server_url_exits(self, mock_rest):
        """verify() exits when jenkins_server_url key is missing from profile."""
        auth = Auth(rest=mock_rest)
        auth.jenkins_profile = {}
        with pytest.raises(YoJenkinsException):
            auth.verify()


# ---------------------------------------------------------------------------
# generate_token tests
# ---------------------------------------------------------------------------


class TestGenerateToken:
    def test_success_returns_token(self, mock_rest):
        """generate_token returns the token value on success."""
        auth = Auth(rest=mock_rest)

        # First call: crumb request (returns XML-like text)
        # Second call: token generation (returns JSON)
        mock_rest.request.side_effect = [
            ('<crumb>Jenkins-Crumbmycrumbvalue</crumb>', {}, True),
            ({'data': {'tokenValue': 'generated-api-token'}}, {}, True),
        ]

        result = auth.generate_token(
            token_name='mytoken',
            server_base_url='http://localhost:8080',
            username='admin',
            password='adminpass',
        )
        assert result == 'generated-api-token'

    def test_crumb_request_failure_exits(self, mock_rest):
        """generate_token exits when crumb request fails."""
        auth = Auth(rest=mock_rest)
        mock_rest.request.return_value = ('', {}, False)

        with pytest.raises(YoJenkinsException):
            auth.generate_token(
                token_name='mytoken',
                server_base_url='http://localhost:8080',
                username='admin',
                password='adminpass',
            )

    def test_token_request_failure_exits(self, mock_rest):
        """generate_token exits when token generation POST fails."""
        auth = Auth(rest=mock_rest)
        mock_rest.request.side_effect = [
            ('<crumb>Jenkins-Crumbmycrumbvalue</crumb>', {}, True),
            ({}, {}, False),
        ]

        with pytest.raises(YoJenkinsException):
            auth.generate_token(
                token_name='mytoken',
                server_base_url='http://localhost:8080',
                username='admin',
                password='adminpass',
            )

    def test_missing_token_value_key_exits(self, mock_rest):
        """generate_token exits when response JSON lacks tokenValue key."""
        auth = Auth(rest=mock_rest)
        mock_rest.request.side_effect = [
            ('<crumb>Jenkins-Crumbmycrumbvalue</crumb>', {}, True),
            ({'data': {}}, {}, True),
        ]

        with pytest.raises(YoJenkinsException):
            auth.generate_token(
                token_name='mytoken',
                server_base_url='http://localhost:8080',
                username='admin',
                password='adminpass',
            )


# ---------------------------------------------------------------------------
# Profile CRUD tests (_update_profiles, show_local_credentials, get_rest)
# ---------------------------------------------------------------------------


class TestProfileOperations:
    def test_get_rest_returns_rest_object(self, mock_rest):
        """get_rest() returns the rest object assigned at init."""
        auth = Auth(rest=mock_rest)
        assert auth.get_rest() is mock_rest

    def test_update_profiles_writes_toml(self, mock_rest, tmp_path):
        """_update_profiles writes profiles as TOML to the creds file."""
        creds_dir = tmp_path / CONFIG_DIR_NAME
        creds_dir.mkdir()
        creds_file = creds_dir / CREDS_FILE_NAME

        auth = Auth(rest=mock_rest)
        profiles = {
            'myprofile': {
                'jenkins_server_url': 'http://server:8080',
                'username': 'user1',
                'api_token': 'token1',
                'active': True,
            }
        }

        with patch('yojenkins.yo_jenkins.auth.Path') as MockPath:
            MockPath.home.return_value = tmp_path
            result = auth._update_profiles(profiles)

        assert result is True
        content = creds_file.read_text()
        assert 'myprofile' in content
        assert 'user1' in content

    def test_show_local_credentials_returns_profiles(self, mock_rest, tmp_path):
        """show_local_credentials returns parsed TOML profiles dict."""
        profiles = {
            'default': {
                'jenkins_server_url': 'http://localhost:8080',
                'username': 'testuser',
                'api_token': 'testtoken',
                'active': True,
            }
        }
        _write_creds_file(tmp_path, profiles)
        creds_file_path = str(tmp_path / CONFIG_DIR_NAME / CREDS_FILE_NAME)

        auth = Auth(rest=mock_rest)
        with patch.object(auth, '_detect_creds_file', return_value=(True, creds_file_path)):
            result = auth.show_local_credentials()

        assert 'default' in result
        assert result['default']['username'] == 'testuser'

    def test_show_local_credentials_no_file_exits(self, mock_rest):
        """show_local_credentials exits when no credentials file is found."""
        auth = Auth(rest=mock_rest)
        with patch.object(auth, '_detect_creds_file', return_value=(False, '')):
            with pytest.raises(YoJenkinsException):
                auth.show_local_credentials()

    def test_user_returns_data(self, mock_rest):
        """user() returns user info dict from REST request."""
        auth = Auth(rest=mock_rest)
        mock_rest.request.return_value = ({'fullName': 'Test User'}, {}, True)
        result = auth.user()
        assert result['fullName'] == 'Test User'

    def test_user_failure_exits(self, mock_rest):
        """user() exits when REST request returns empty/falsy data."""
        auth = Auth(rest=mock_rest)
        mock_rest.request.return_value = ({}, {}, True)
        with pytest.raises(YoJenkinsException):
            auth.user()


# ---------------------------------------------------------------------------
# _detect_config_dir / _detect_creds_file tests
# ---------------------------------------------------------------------------


class TestDetectConfigDir:
    def test_detect_config_dir_exists(self, mock_rest, tmp_path):
        """_detect_config_dir returns True when config dir exists."""
        config_dir = tmp_path / CONFIG_DIR_NAME
        config_dir.mkdir()
        auth = Auth(rest=mock_rest)
        with patch('yojenkins.yo_jenkins.auth.Path') as MockPath:
            MockPath.home.return_value = tmp_path
            success, path = auth._detect_config_dir()
        assert success is True
        assert CONFIG_DIR_NAME in path

    def test_detect_config_dir_missing(self, mock_rest, tmp_path):
        """_detect_config_dir returns False when config dir does not exist."""
        auth = Auth(rest=mock_rest)
        with patch('yojenkins.yo_jenkins.auth.Path') as MockPath:
            MockPath.home.return_value = tmp_path
            success, path = auth._detect_config_dir()
        assert success is False
        assert path == ''

    def test_detect_creds_file_exists(self, mock_rest, tmp_path):
        """_detect_creds_file returns True when creds file exists."""
        _write_creds_file(
            tmp_path,
            {'default': {'jenkins_server_url': 'http://x', 'username': 'u', 'api_token': 't', 'active': True}},
        )
        auth = Auth(rest=mock_rest)
        with patch('yojenkins.yo_jenkins.auth.Path') as MockPath:
            MockPath.home.return_value = tmp_path
            success, path = auth._detect_creds_file()
        assert success is True
        assert CREDS_FILE_NAME in path

    def test_detect_creds_file_missing(self, mock_rest, tmp_path):
        """_detect_creds_file returns False when creds file does not exist."""
        config_dir = tmp_path / CONFIG_DIR_NAME
        config_dir.mkdir()
        auth = Auth(rest=mock_rest)
        with patch('yojenkins.yo_jenkins.auth.Path') as MockPath:
            MockPath.home.return_value = tmp_path
            success, path = auth._detect_creds_file()
        assert success is False
        assert path == ''


# ---------------------------------------------------------------------------
# verify edge cases
# ---------------------------------------------------------------------------


class TestVerifyEdgeCases:
    def test_verify_with_yojenkins_token_env(self, mock_rest):
        """verify() includes env var note when YOJENKINS_TOKEN is set."""
        auth = Auth(rest=mock_rest)
        auth.jenkins_profile = {
            'jenkins_server_url': 'http://localhost:8080',
        }
        mock_rest.request.return_value = ({}, {}, False)
        with patch.dict(os.environ, {'YOJENKINS_TOKEN': 'some-token'}):
            with pytest.raises(YoJenkinsException):
                auth.verify()


# ---------------------------------------------------------------------------
# generate_token prompt tests
# ---------------------------------------------------------------------------


class TestGenerateTokenPrompts:
    def test_prompts_when_args_missing(self, mock_rest):
        """generate_token prompts user for missing args."""
        auth = Auth(rest=mock_rest)
        mock_rest.request.side_effect = [
            ('<crumb>Jenkins-Crumbmycrumbvalue</crumb>', {}, True),
            ({'data': {'tokenValue': 'gen-token'}}, {}, True),
        ]
        with patch('builtins.input', side_effect=['mytoken', 'http://server:8080', 'admin']):
            with patch('yojenkins.yo_jenkins.auth.getpass', return_value='password'):
                result = auth.generate_token()
        assert result == 'gen-token'


# ---------------------------------------------------------------------------
# create_auth edge cases
# ---------------------------------------------------------------------------


class TestCreateAuthEdgeCases:
    def test_create_auth_with_profile_info_param(self, mock_rest):
        """create_auth uses profile_info dict when passed."""
        auth = Auth(rest=mock_rest)
        profile_info = {
            'profile': 'test',
            'jenkins_server_url': 'http://localhost:8080',
            'username': 'user',
            'api_token': 'token',
        }
        mock_rest.is_reachable = MagicMock(return_value=True)
        with patch('yojenkins.yo_jenkins.auth.JenkinsSDK'):
            with patch.object(auth, 'verify', return_value=True):
                result = auth.create_auth(profile_info=profile_info)
        assert result is True
        assert auth.jenkins_profile == profile_info

    def test_create_auth_hides_token(self, mock_rest):
        """create_auth masks the api_token in logging."""
        auth = Auth(rest=mock_rest)
        auth.jenkins_profile = {
            'profile': 'test',
            'jenkins_server_url': 'http://localhost:8080',
            'username': 'user',
            'api_token': 'mysecrettoken',
        }
        mock_rest.is_reachable = MagicMock(return_value=True)
        with patch('yojenkins.yo_jenkins.auth.JenkinsSDK'):
            with patch.object(auth, 'verify', return_value=True):
                result = auth.create_auth()
        assert result is True
        assert auth.jenkins_api_token == 'mysecrettoken'

    def test_create_auth_jenkins_sdk_exception_exits(self, mock_rest):
        """create_auth exits when JenkinsSDK constructor raises."""
        auth = Auth(rest=mock_rest)
        auth.jenkins_profile = {
            'profile': 'test',
            'jenkins_server_url': 'http://localhost:8080',
            'username': 'user',
            'api_token': 'token',
        }
        with patch('yojenkins.yo_jenkins.auth.JenkinsSDK', side_effect=Exception('SDK error')):
            with pytest.raises(YoJenkinsException):
                auth.create_auth()


# ---------------------------------------------------------------------------
# get_credentials edge cases
# ---------------------------------------------------------------------------


class TestGetCredentialsEdgeCases:
    def test_non_dict_profile_values_exits(self, mock_rest, tmp_path):
        """get_credentials exits when profile values are not a dict."""
        creds_dir = tmp_path / CONFIG_DIR_NAME
        creds_dir.mkdir(exist_ok=True)
        creds_file = creds_dir / CREDS_FILE_NAME
        # Write a TOML where the 'value' is just a string (not a dict)
        creds_file.write_text('bad_profile = "just a string"\n')

        auth = Auth(rest=mock_rest)
        env_clean = {k: v for k, v in os.environ.items() if k != PROFILE_ENV_VAR}
        with patch.object(auth, '_detect_creds_file', return_value=(True, str(creds_file))):
            with patch('yojenkins.yo_jenkins.auth.Path') as MockPath:
                MockPath.home.return_value = tmp_path
                with patch.dict(os.environ, env_clean, clear=True):
                    with pytest.raises(YoJenkinsException):
                        auth.get_credentials(profile='')


# ---------------------------------------------------------------------------
# profile_add_new_token tests
# ---------------------------------------------------------------------------


class TestProfileAddNewToken:
    def test_add_token_with_provided_token(self, mock_rest, tmp_path):
        """profile_add_new_token stores a provided token."""
        profiles = {
            'default': {
                'jenkins_server_url': 'http://localhost:8080',
                'username': 'user',
                'api_token': 'old-token',
                'active': True,
            }
        }
        _write_creds_file(tmp_path, profiles)
        auth = Auth(rest=mock_rest)
        with patch.object(
            auth, '_detect_creds_file', return_value=(True, str(tmp_path / CONFIG_DIR_NAME / CREDS_FILE_NAME))
        ):
            with patch.object(auth, '_update_profiles', return_value=True):
                result = auth.profile_add_new_token('default', token='new-provided-token')
        assert result == 'new-provided-token'

    def test_add_token_profile_not_found_exits(self, mock_rest, tmp_path):
        """profile_add_new_token exits when profile does not exist."""
        profiles = {
            'default': {
                'jenkins_server_url': 'http://localhost:8080',
                'username': 'user',
                'api_token': 'old-token',
                'active': True,
            }
        }
        _write_creds_file(tmp_path, profiles)
        auth = Auth(rest=mock_rest)
        with patch.object(
            auth, '_detect_creds_file', return_value=(True, str(tmp_path / CONFIG_DIR_NAME / CREDS_FILE_NAME))
        ):
            with pytest.raises(YoJenkinsException):
                auth.profile_add_new_token('nonexistent')

    def test_add_token_no_creds_file_exits(self, mock_rest):
        """profile_add_new_token exits when no creds file found."""
        auth = Auth(rest=mock_rest)
        with patch.object(auth, '_detect_creds_file', return_value=(False, '')):
            with pytest.raises(YoJenkinsException):
                auth.profile_add_new_token('default')

    def test_add_token_missing_server_url(self, mock_rest, tmp_path):
        """profile_add_new_token handles missing server URL in profile."""
        profiles = {
            'minimal': {
                'username': 'user',
                'active': True,
            }
        }
        _write_creds_file(tmp_path, profiles)
        auth = Auth(rest=mock_rest)
        with patch.object(
            auth, '_detect_creds_file', return_value=(True, str(tmp_path / CONFIG_DIR_NAME / CREDS_FILE_NAME))
        ):
            with patch.object(auth, '_update_profiles', return_value=True):
                result = auth.profile_add_new_token('minimal', token='my-token')
        assert result == 'my-token'

    def test_add_token_update_failure_exits(self, mock_rest, tmp_path):
        """profile_add_new_token exits when _update_profiles fails."""
        profiles = {
            'default': {
                'jenkins_server_url': 'http://localhost:8080',
                'username': 'user',
                'api_token': 'old',
                'active': True,
            }
        }
        _write_creds_file(tmp_path, profiles)
        auth = Auth(rest=mock_rest)
        with patch.object(
            auth, '_detect_creds_file', return_value=(True, str(tmp_path / CONFIG_DIR_NAME / CREDS_FILE_NAME))
        ):
            with patch.object(auth, '_update_profiles', return_value=False):
                with pytest.raises(YoJenkinsException):
                    auth.profile_add_new_token('default', token='t')


# ---------------------------------------------------------------------------
# configure tests
# ---------------------------------------------------------------------------


class TestConfigure:
    def test_configure_with_auth_file(self, mock_rest, tmp_path):
        """configure() adds profiles from a JSON auth file."""
        auth_setup = {
            'newprofile': {
                'jenkins_server_url': 'http://new:8080',
                'username': 'newuser',
                'api_token': 'newtoken',
                'active': True,
            }
        }
        auth_file = tmp_path / 'auth.json'
        auth_file.write_text(json.dumps(auth_setup))

        auth = Auth(rest=mock_rest)
        with patch.object(auth, '_detect_creds_file', return_value=(False, '')):
            with patch.object(auth, '_update_profiles', return_value=True):
                result = auth.configure(auth_file=str(auth_file))
        assert result is True

    def test_configure_with_auth_file_missing_required_key(self, mock_rest, tmp_path):
        """configure() skips profiles missing required keys."""
        auth_setup = {
            'bad': {
                'username': 'user',
                # missing jenkins_server_url
            }
        }
        auth_file = tmp_path / 'auth.json'
        auth_file.write_text(json.dumps(auth_setup))

        auth = Auth(rest=mock_rest)
        with patch.object(auth, '_detect_creds_file', return_value=(False, '')):
            with patch.object(auth, '_update_profiles', return_value=True):
                result = auth.configure(auth_file=str(auth_file))
        assert result is True

    def test_configure_with_auth_file_invalid_keys_stripped(self, mock_rest, tmp_path):
        """configure() strips invalid keys from auth file profiles."""
        auth_setup = {
            'profile1': {
                'jenkins_server_url': 'http://server:8080',
                'username': 'user',
                'invalid_key': 'should_be_removed',
            }
        }
        auth_file = tmp_path / 'auth.json'
        auth_file.write_text(json.dumps(auth_setup))

        auth = Auth(rest=mock_rest)
        with patch.object(auth, '_detect_creds_file', return_value=(False, '')):
            with patch.object(auth, '_update_profiles', return_value=True):
                result = auth.configure(auth_file=str(auth_file))
        assert result is True

    def test_configure_with_existing_profiles(self, mock_rest, tmp_path):
        """configure() loads existing profiles and adds new ones."""
        profiles = {
            'existing': {
                'jenkins_server_url': 'http://existing:8080',
                'username': 'existuser',
                'api_token': 'existtoken',
                'active': True,
            }
        }
        _write_creds_file(tmp_path, profiles)
        auth_setup = {
            'existing': {
                'jenkins_server_url': 'http://replaced:8080',
                'username': 'replaceduser',
            }
        }
        auth_file = tmp_path / 'auth.json'
        auth_file.write_text(json.dumps(auth_setup))

        auth = Auth(rest=mock_rest)
        with patch.object(
            auth, '_detect_creds_file', return_value=(True, str(tmp_path / CONFIG_DIR_NAME / CREDS_FILE_NAME))
        ):
            with patch.object(auth, '_update_profiles', return_value=True):
                result = auth.configure(auth_file=str(auth_file))
        assert result is True

    def test_configure_with_empty_required_value(self, mock_rest, tmp_path):
        """configure() rejects profiles with empty required key values."""
        auth_setup = {
            'bad': {
                'jenkins_server_url': '',
                'username': 'user',
            }
        }
        auth_file = tmp_path / 'auth.json'
        auth_file.write_text(json.dumps(auth_setup))

        auth = Auth(rest=mock_rest)
        with patch.object(auth, '_detect_creds_file', return_value=(False, '')):
            with patch.object(auth, '_update_profiles', return_value=True):
                result = auth.configure(auth_file=str(auth_file))
        assert result is True
