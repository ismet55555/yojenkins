"""Tests for yojenkins.yo_jenkins.server.Server"""

from unittest.mock import patch

import pytest

from yojenkins.yo_jenkins.exceptions import YoJenkinsException
from yojenkins.yo_jenkins.server import Server


@pytest.fixture
def server(mock_rest, mock_auth):
    """Create a Server instance with mocked rest and auth."""
    return Server(rest=mock_rest, auth=mock_auth)


# --- Server.__init__ ---

class TestServerInit:
    def test_init_sets_rest_and_auth(self, mock_rest, mock_auth):
        srv = Server(rest=mock_rest, auth=mock_auth)
        assert srv.rest is mock_rest
        assert srv.auth is mock_auth

    def test_init_sets_server_base_url(self, mock_rest, mock_auth):
        srv = Server(rest=mock_rest, auth=mock_auth)
        assert srv.server_base_url == 'http://localhost:8080/'


# --- Server.info ---

class TestServerInfo:
    def test_info_returns_data_on_success(self, server):
        server.rest.request.return_value = ({'mode': 'NORMAL'}, {}, True)
        result = server.info()
        assert result == {'mode': 'NORMAL'}
        server.rest.request.assert_called_once_with('api/json', 'get')

    def test_info_fail_out_on_failure(self, server):
        server.rest.request.return_value = ({}, {}, False)
        with pytest.raises(YoJenkinsException):
            server.info()


# --- Server.people ---

class TestServerPeople:
    def test_people_returns_users_and_names(self, server):
        users_data = {
            'users': [
                {'user': {'fullName': 'Alice'}},
                {'user': {'fullName': 'Bob'}},
            ]
        }
        server.rest.request.return_value = (users_data, {}, True)
        people_info, people_list = server.people()
        assert people_info == users_data['users']
        assert people_list == ['Alice', 'Bob']

    def test_people_fail_out_on_request_failure(self, server):
        server.rest.request.return_value = ({}, {}, False)
        with pytest.raises(YoJenkinsException):
            server.people()

    def test_people_fail_out_on_missing_keys(self, server):
        server.rest.request.return_value = ({'users': [{'bad': 'data'}]}, {}, True)
        with pytest.raises(YoJenkinsException):
            server.people()


# --- Server.queue_info ---

class TestServerQueueInfo:
    def test_queue_info_returns_data(self, server):
        queue_data = {'items': []}
        server.rest.request.return_value = (queue_data, {}, True)
        result = server.queue_info()
        assert result == queue_data

    def test_queue_info_fail_out_on_failure(self, server):
        server.rest.request.return_value = ({}, {}, False)
        with pytest.raises(YoJenkinsException):
            server.queue_info()


# --- Server.queue_list ---

class TestServerQueueList:
    def test_queue_list_returns_items(self, server):
        queue_data = {
            'items': [
                {'task': {'url': 'http://localhost:8080/job/test/1'}},
                {'task': {'url': 'http://localhost:8080/job/test/2'}},
            ]
        }
        server.rest.request.return_value = (queue_data, {}, True)
        result = server.queue_list()
        assert len(result) == 2

    def test_queue_list_empty(self, server):
        server.rest.request.return_value = ({'items': []}, {}, True)
        result = server.queue_list()
        assert result == []


# --- Server.plugin_list ---

class TestServerPluginList:
    def test_plugin_list_returns_plugins_and_descriptions(self, server):
        plugins_data = {
            'plugins': [
                {'longName': 'Git Plugin', 'shortName': 'git', 'version': '4.0'},
                {'longName': 'Docker Plugin', 'shortName': 'docker', 'version': '1.2'},
            ]
        }
        server.rest.request.return_value = (plugins_data, {}, True)
        plugins_info, plugin_list = server.plugin_list()
        assert len(plugins_info) == 2
        assert 'Git Plugin - git - 4.0' in plugin_list
        assert 'Docker Plugin - docker - 1.2' in plugin_list

    def test_plugin_list_fail_out_on_request_failure(self, server):
        server.rest.request.return_value = ({}, {}, False)
        with pytest.raises(YoJenkinsException):
            server.plugin_list()

    def test_plugin_list_fail_out_on_missing_keys(self, server):
        server.rest.request.return_value = ({'plugins': [{'bad': 'data'}]}, {}, True)
        with pytest.raises(YoJenkinsException):
            server.plugin_list()


# --- Server.restart ---

class TestServerRestart:
    def test_restart_force(self, server):
        server.rest.request.return_value = ('', {}, True)
        result = server.restart(force=True)
        assert result is True
        server.rest.request.assert_called_once_with(
            'restart', 'post', is_endpoint=True, json_content=True, allow_redirect=False
        )

    def test_restart_safe(self, server):
        server.rest.request.return_value = ('', {}, True)
        result = server.restart(force=False)
        assert result is True
        server.rest.request.assert_called_once_with(
            'safeRestart', 'post', is_endpoint=True, json_content=True, allow_redirect=False
        )

    def test_restart_fail_out(self, server):
        server.rest.request.return_value = ('', {}, False)
        with pytest.raises(YoJenkinsException):
            server.restart()


# --- Server.shutdown ---

class TestServerShutdown:
    def test_shutdown_force(self, server):
        server.rest.request.return_value = ('', {}, True)
        result = server.shutdown(force=True)
        assert result is True
        server.rest.request.assert_called_once_with(
            'exit', 'post', is_endpoint=True, json_content=False, allow_redirect=False
        )

    def test_shutdown_safe(self, server):
        server.rest.request.return_value = ('', {}, True)
        result = server.shutdown(force=False)
        assert result is True
        server.rest.request.assert_called_once_with(
            'safeExit', 'post', is_endpoint=True, json_content=False, allow_redirect=False
        )

    def test_shutdown_fail_out(self, server):
        server.rest.request.return_value = ('', {}, False)
        with pytest.raises(YoJenkinsException):
            server.shutdown()


# --- Server.quiet ---

class TestServerQuiet:
    def test_quiet_enable(self, server):
        server.rest.request.return_value = ('', {}, True)
        result = server.quiet(off=False)
        assert result is True
        server.rest.request.assert_called_once_with(
            'quietDown', 'post', is_endpoint=True, json_content=True, allow_redirect=False
        )

    def test_quiet_disable(self, server):
        server.rest.request.return_value = ('', {}, True)
        result = server.quiet(off=True)
        assert result is True
        server.rest.request.assert_called_once_with(
            'cancelQuietDown', 'post', is_endpoint=True, json_content=True, allow_redirect=False
        )

    def test_quiet_fail_out(self, server):
        server.rest.request.return_value = ('', {}, False)
        with pytest.raises(YoJenkinsException):
            server.quiet()


# --- Server.browser_open ---

class TestServerBrowserOpen:
    @patch('yojenkins.yo_jenkins.server.utility.browser_open', return_value=True)
    def test_browser_open_success(self, mock_browser, server):
        result = server.browser_open()
        assert result is True
        mock_browser.assert_called_once_with(url='http://localhost:8080/')

    @patch('yojenkins.yo_jenkins.server.utility.browser_open', return_value=False)
    def test_browser_open_failure_exits(self, mock_browser, server):
        with pytest.raises(YoJenkinsException):
            server.browser_open()
