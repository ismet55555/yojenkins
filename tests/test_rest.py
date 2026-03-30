"""Tests for yojenkins/yo_jenkins/rest.py"""

from unittest.mock import MagicMock, patch

import requests
from requests.auth import HTTPBasicAuth

from yojenkins.yo_jenkins.rest import Rest

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_mock_response(
    status_code=200,
    headers=None,
    json_data=None,
    text='',
    content=b'content',
    ok=True,
    history=None,
    reason='OK',
    method='GET',
):
    """Build a mock requests.Response suitable for Rest.request()."""
    resp = MagicMock()
    resp.status_code = status_code
    resp.headers = headers or {'Content-Type': 'application/json'}
    resp.json.return_value = json_data if json_data is not None else {}
    resp.text = text
    resp.content = content
    resp.ok = ok
    resp.history = history or []
    resp.reason = reason
    resp.request = MagicMock()
    resp.request.method = method
    return resp


def _make_future(response):
    """Wrap a mock response in a future-like object with .result()."""
    future = MagicMock()
    future.result.return_value = response
    return future


# ---------------------------------------------------------------------------
# __init__ tests
# ---------------------------------------------------------------------------

class TestRestInit:

    @patch('yojenkins.yo_jenkins.rest.FuturesSession')
    def test_default_session_creation(self, mock_fs_cls):
        """When no session is passed, a new FuturesSession is created."""
        rest = Rest()
        mock_fs_cls.assert_called_once_with(max_workers=16)
        assert rest.session == mock_fs_cls.return_value

    @patch('yojenkins.yo_jenkins.rest.FuturesSession')
    def test_existing_session_wrapped(self, mock_fs_cls):
        """When a session is passed in, it gets wrapped in FuturesSession."""
        existing = MagicMock()
        rest = Rest(session=existing)
        mock_fs_cls.assert_called_once_with(session=existing, max_workers=16)
        assert rest.session == mock_fs_cls.return_value

    def test_credentials_default_to_empty_strings(self):
        """Default credentials are empty strings and has_credentials is False."""
        with patch('yojenkins.yo_jenkins.rest.FuturesSession'):
            rest = Rest()
        assert rest.username == ''
        assert rest.api_token == ''
        assert rest.server_url == ''
        assert rest.has_credentials is False

    def test_credentials_passed_in_constructor(self):
        """Credentials passed to constructor are stored."""
        with patch('yojenkins.yo_jenkins.rest.FuturesSession'):
            rest = Rest(username='user', api_token='token', server_url='http://j:8080')
        assert rest.username == 'user'
        assert rest.api_token == 'token'
        assert rest.server_url == 'http://j:8080'


# ---------------------------------------------------------------------------
# set_credentials tests
# ---------------------------------------------------------------------------

class TestSetCredentials:

    def test_sets_all_fields(self):
        """set_credentials stores username, api_token, server_url."""
        with patch('yojenkins.yo_jenkins.rest.FuturesSession'):
            rest = Rest()
        rest.set_credentials('admin', 'secret', 'http://jenkins:8080')
        assert rest.username == 'admin'
        assert rest.api_token == 'secret'

    def test_adds_trailing_slash(self):
        """server_url gets a trailing slash after stripping existing ones."""
        with patch('yojenkins.yo_jenkins.rest.FuturesSession'):
            rest = Rest()
        rest.set_credentials('u', 't', 'http://jenkins:8080/')
        assert rest.server_url == 'http://jenkins:8080/'

    def test_adds_trailing_slash_when_missing(self):
        """server_url gets a trailing slash if none was present."""
        with patch('yojenkins.yo_jenkins.rest.FuturesSession'):
            rest = Rest()
        rest.set_credentials('u', 't', 'http://jenkins:8080')
        assert rest.server_url == 'http://jenkins:8080/'

    def test_has_credentials_becomes_true(self):
        """has_credentials flag is set to True after set_credentials."""
        with patch('yojenkins.yo_jenkins.rest.FuturesSession'):
            rest = Rest()
        assert rest.has_credentials is False
        rest.set_credentials('u', 't', 'http://jenkins:8080')
        assert rest.has_credentials is True


# ---------------------------------------------------------------------------
# is_reachable tests
# ---------------------------------------------------------------------------

class TestIsReachable:

    def test_returns_true_when_request_succeeds(self):
        """is_reachable returns True when the head request returns non-empty headers."""
        with patch('yojenkins.yo_jenkins.rest.FuturesSession'):
            rest = Rest()
        rest.server_url = 'http://jenkins:8080/'
        # is_reachable checks request()[1] -- the headers dict
        resp = _make_mock_response(status_code=200, method='HEAD')
        future = _make_future(resp)
        rest.session = MagicMock()
        rest.session.head.return_value = future
        assert rest.is_reachable() is True

    def test_returns_false_when_request_fails(self):
        """is_reachable returns False when the request raises ConnectionError."""
        with patch('yojenkins.yo_jenkins.rest.FuturesSession'):
            rest = Rest()
        rest.server_url = 'http://jenkins:8080/'
        rest.session = MagicMock()
        rest.session.head.side_effect = requests.exceptions.ConnectionError('down')
        assert rest.is_reachable() is False


# ---------------------------------------------------------------------------
# request() method tests
# ---------------------------------------------------------------------------

class TestRequest:

    def _make_rest(self):
        """Create a Rest instance with mocked session."""
        with patch('yojenkins.yo_jenkins.rest.FuturesSession'):
            rest = Rest(username='user', api_token='tok', server_url='http://j:8080/')
        rest.session = MagicMock()
        return rest

    def test_get_request_success(self):
        """GET request returns (json_data, headers, True)."""
        rest = self._make_rest()
        resp = _make_mock_response(json_data={'key': 'value'})
        rest.session.get.return_value = _make_future(resp)

        content, headers, success = rest.request('api/json', request_type='get', is_endpoint=False)
        assert success is True
        assert content == {'key': 'value'}
        rest.session.get.assert_called_once()

    def test_post_request_success(self):
        """POST request returns (json_data, headers, True)."""
        rest = self._make_rest()
        resp = _make_mock_response(json_data={'created': True})
        rest.session.post.return_value = _make_future(resp)

        content, headers, success = rest.request('create', request_type='post', is_endpoint=False)
        assert success is True
        assert content == {'created': True}
        rest.session.post.assert_called_once()

    def test_head_request_success(self):
        """HEAD request returns ({}, headers, response.ok)."""
        rest = self._make_rest()
        resp_headers = {'X-Jenkins': '2.300', 'Content-Type': 'text/html'}
        resp = _make_mock_response(status_code=200, headers=resp_headers, method='HEAD')
        rest.session.head.return_value = _make_future(resp)

        content, headers, success = rest.request('/', request_type='head', is_endpoint=False)
        assert content == {}
        assert headers == resp_headers
        assert success is True

    def test_401_response_returns_false(self):
        """401 Unauthorized returns ({}, {}, False)."""
        rest = self._make_rest()
        resp = _make_mock_response(status_code=401, ok=False, reason='Unauthorized')
        rest.session.get.return_value = _make_future(resp)

        content, headers, success = rest.request('/api', request_type='get', is_endpoint=False)
        assert success is False
        assert content == {}

    def test_403_response_returns_false(self):
        """403 Forbidden returns ({}, {}, False)."""
        rest = self._make_rest()
        resp = _make_mock_response(status_code=403, ok=False, reason='Forbidden')
        rest.session.get.return_value = _make_future(resp)

        content, headers, success = rest.request('/api', request_type='get', is_endpoint=False)
        assert success is False

    def test_connection_error_returns_false(self):
        """ConnectionError returns ({}, {}, False)."""
        rest = self._make_rest()
        rest.session.get.side_effect = requests.exceptions.ConnectionError('refused')

        content, headers, success = rest.request('http://bad', request_type='get', is_endpoint=False)
        assert success is False
        assert content == {}
        assert headers == {}

    def test_json_parse_failure_falls_back_to_empty(self):
        """When JSON parsing fails and json_content=True, return_content is {}."""
        rest = self._make_rest()
        resp = _make_mock_response(text='<html>not json</html>', content=b'<html>not json</html>')
        resp.json.side_effect = ValueError('No JSON')
        rest.session.get.return_value = _make_future(resp)

        content, headers, success = rest.request('/page', request_type='get', is_endpoint=False, json_content=True)
        assert success is True
        # When json parse fails and json_content=True, return_content stays as {}
        assert content == {}

    def test_json_content_false_returns_text(self):
        """When json_content=False, response.text is returned."""
        rest = self._make_rest()
        resp = _make_mock_response(text='plain text response', content=b'plain text response')
        rest.session.get.return_value = _make_future(resp)

        content, headers, success = rest.request('/text', request_type='get', is_endpoint=False, json_content=False)
        assert success is True
        assert content == 'plain text response'

    def test_is_endpoint_true_prepends_server_url(self):
        """is_endpoint=True prepends server_url to target."""
        rest = self._make_rest()
        resp = _make_mock_response(json_data={'ok': True})
        rest.session.get.return_value = _make_future(resp)

        rest.request('api/json', request_type='get', is_endpoint=True)
        call_args = rest.session.get.call_args
        assert call_args[0][0] == 'http://j:8080/api/json'

    def test_is_endpoint_false_uses_target_as_is(self):
        """is_endpoint=False uses the target URL verbatim."""
        rest = self._make_rest()
        resp = _make_mock_response(json_data={})
        rest.session.get.return_value = _make_future(resp)

        rest.request('http://other:9090/path', request_type='get', is_endpoint=False)
        call_args = rest.session.get.call_args
        assert call_args[0][0] == 'http://other:9090/path'

    @patch('yojenkins.yo_jenkins.rest.FuturesSession')
    def test_new_session_creates_fresh_session(self, mock_fs_cls):
        """new_session=True creates a new FuturesSession."""
        rest = self._make_rest()
        # Make new_session branch create a new mock session
        new_mock_session = MagicMock()
        mock_fs_cls.return_value = new_mock_session
        resp = _make_mock_response(json_data={})
        new_mock_session.get.return_value = _make_future(resp)

        rest.request('url', request_type='get', is_endpoint=False, new_session=True)
        mock_fs_cls.assert_called_with(max_workers=16)
        new_mock_session.get.assert_called_once()

    def test_auth_parameter_override(self):
        """Custom auth tuple overrides default HTTPBasicAuth."""
        rest = self._make_rest()
        resp = _make_mock_response(json_data={})
        rest.session.get.return_value = _make_future(resp)
        custom_auth = ('other_user', 'other_pass')

        rest.request('/api', request_type='get', is_endpoint=False, auth=custom_auth)
        call_kwargs = rest.session.get.call_args[1]
        assert call_kwargs['auth'] == custom_auth

    def test_unrecognized_request_type_returns_false(self):
        """Unrecognized request type returns ({}, {}, False)."""
        rest = self._make_rest()
        content, headers, success = rest.request('/api', request_type='patch', is_endpoint=False)
        assert success is False
        assert content == {}

    def test_result_exception_returns_false(self):
        """Exception during future.result() returns ({}, {}, False)."""
        rest = self._make_rest()
        future = MagicMock()
        future.result.side_effect = requests.exceptions.ReadTimeout('timeout')
        rest.session.get.return_value = future

        content, headers, success = rest.request('/api', request_type='get', is_endpoint=False)
        assert success is False

    def test_empty_content_returns_empty_dict(self):
        """When response.content is empty, return_content is {}."""
        rest = self._make_rest()
        resp = _make_mock_response(content=b'', json_data={})
        rest.session.get.return_value = _make_future(resp)

        content, headers, success = rest.request('/api', request_type='get', is_endpoint=False)
        assert success is True
        assert content == {}

    def test_409_conflict_returns_false(self):
        """409 Conflict returns ({}, {}, False)."""
        rest = self._make_rest()
        resp = _make_mock_response(status_code=409, ok=False, reason='Conflict')
        rest.session.get.return_value = _make_future(resp)

        content, headers, success = rest.request('/api', request_type='get', is_endpoint=False)
        assert success is False

    def test_non_ok_status_returns_false(self):
        """Non-OK status (e.g. 500) returns ({}, {}, False)."""
        rest = self._make_rest()
        resp = _make_mock_response(status_code=500, ok=False, reason='Server Error')
        rest.session.get.return_value = _make_future(resp)

        content, headers, success = rest.request('/api', request_type='get', is_endpoint=False)
        assert success is False

    def test_delete_request_success(self):
        """DELETE request type is supported."""
        rest = self._make_rest()
        resp = _make_mock_response(json_data={'deleted': True})
        rest.session.delete.return_value = _make_future(resp)

        content, headers, success = rest.request('/item', request_type='delete', is_endpoint=False)
        assert success is True
        assert content == {'deleted': True}

    def test_default_auth_uses_httpbasicauth(self):
        """When no auth is passed, HTTPBasicAuth is used with stored credentials."""
        rest = self._make_rest()
        resp = _make_mock_response(json_data={})
        rest.session.get.return_value = _make_future(resp)

        rest.request('/api', request_type='get', is_endpoint=False)
        call_kwargs = rest.session.get.call_args[1]
        auth_used = call_kwargs['auth']
        assert isinstance(auth_used, HTTPBasicAuth)
        assert auth_used.username == 'user'
        assert auth_used.password == 'tok'

    def test_auth_needed_false_sends_no_auth(self):
        """When auth_needed=False, no auth is sent."""
        rest = self._make_rest()
        resp = _make_mock_response(json_data={}, method='HEAD')
        rest.session.head.return_value = _make_future(resp)

        rest.request('/login', request_type='head', is_endpoint=False, auth_needed=False)
        call_kwargs = rest.session.head.call_args[1]
        assert call_kwargs['auth'] is None


# ---------------------------------------------------------------------------
# get_server_url / get_active_session tests
# ---------------------------------------------------------------------------

class TestAccessors:

    def test_get_server_url(self):
        with patch('yojenkins.yo_jenkins.rest.FuturesSession'):
            rest = Rest(server_url='http://j:8080')
        assert rest.get_server_url() == 'http://j:8080'

    def test_get_active_session(self):
        with patch('yojenkins.yo_jenkins.rest.FuturesSession') as mock_fs:
            rest = Rest()
        assert rest.get_active_session() == mock_fs.return_value
