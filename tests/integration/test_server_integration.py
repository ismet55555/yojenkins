"""Integration tests for Server operations against a live Jenkins instance."""

import pytest

pytestmark = [pytest.mark.docker, pytest.mark.slow]


class TestServerIntegration:
    def test_server_info(self, yojenkins_instance):
        """Server.info() returns a dict with expected keys."""
        info = yojenkins_instance.server.info()
        assert isinstance(info, dict)
        assert 'numExecutors' in info

    def test_server_has_4_executors(self, yojenkins_instance):
        """JCasC configures 4 executors."""
        info = yojenkins_instance.server.info()
        assert info['numExecutors'] == 4

    def test_plugin_list(self, yojenkins_instance):
        """Server.plugin_list() returns installed plugins including git."""
        plugins, _plugin_names = yojenkins_instance.server.plugin_list()
        assert len(plugins) > 0
        short_names = [p['shortName'] for p in plugins]
        assert 'git' in short_names

    def test_people(self, yojenkins_instance):
        """Server.people() lists at least the admin user."""
        try:
            people_info, _people_list = yojenkins_instance.server.people()
        except Exception as exc:
            pytest.skip(f'asynchPeople endpoint not available: {exc}')
        assert len(people_info) > 0

    def test_queue_info(self, yojenkins_instance):
        """Server.queue_info() returns a dict (queue may be empty)."""
        queue = yojenkins_instance.server.queue_info()
        assert isinstance(queue, dict)
