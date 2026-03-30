"""PyTest Configurations and Fixtures"""

from unittest.mock import MagicMock

import pytest
from click.testing import CliRunner

from yojenkins.yo_jenkins.rest import Rest


@pytest.fixture
def mock_rest(mocker):
    """Mock Rest object with mocked session and request method.

    Rest.request() returns tuple[dict|str, dict, bool] — (content, headers, success).
    """
    rest = Rest.__new__(Rest)
    rest.username = 'testuser'
    rest.api_token = 'testtoken'
    rest.server_url = 'http://localhost:8080/'
    rest.has_credentials = True
    rest.session = mocker.MagicMock()
    mocker.patch.object(rest, 'request', return_value=({}, {}, True))
    return rest


@pytest.fixture
def mock_auth(mocker):
    """Mock Auth object with pre-set credentials and mocked REST."""
    auth = MagicMock()
    auth.username = 'testuser'
    auth.api_token = 'testtoken'
    auth.server_url = 'http://localhost:8080/'
    auth.jenkins_profile = {
        'jenkins_server_url': 'http://localhost:8080/',
        'username': 'testuser',
        'api_token': 'testtoken',
    }
    auth.get_rest.return_value = MagicMock(spec=Rest)
    auth.jenkins_sdk = MagicMock()
    return auth


@pytest.fixture
def jenkins_api_response():
    """Factory for Jenkins JSON API responses.

    Usage:
        resp = jenkins_api_response({'key': 'value'})
        resp = jenkins_api_response({'error': 'msg'}, status_code=404)
    """

    def _response(data, status_code=200):
        resp = MagicMock()
        resp.status_code = status_code
        resp.json.return_value = data
        resp.text = str(data)
        resp.ok = 200 <= status_code < 300
        return resp

    return _response


@pytest.fixture
def tmp_creds_file(tmp_path):
    """Create a temporary credentials TOML file.

    Returns (creds_dir, creds_file) tuple.
    """
    creds_dir = tmp_path / '.yojenkins'
    creds_dir.mkdir()
    creds_file = creds_dir / 'credentials'
    creds_file.write_text(
        '[default]\n'
        'jenkins_server_url = "http://localhost:8080"\n'
        'username = "testuser"\n'
        'api_token = "testtoken"\n'
        'active = true\n'
    )
    return creds_dir, creds_file


@pytest.fixture
def cli_runner():
    """Click CLI test runner."""
    return CliRunner(mix_stderr=False)
