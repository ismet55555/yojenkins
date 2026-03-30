"""Integration tests for Auth operations against a live Jenkins instance."""

import pytest

pytestmark = [pytest.mark.docker, pytest.mark.slow]


class TestAuthIntegration:
    def test_verify_credentials(self, yojenkins_instance):
        """Auth.verify() returns True with valid admin credentials."""
        assert yojenkins_instance.auth.verify() is True

    def test_rest_is_reachable(self, yojenkins_instance):
        """Rest.is_reachable() confirms the server is up."""
        assert yojenkins_instance.rest.is_reachable() is True

    def test_generate_api_token(self, yojenkins_instance, docker_jenkins_server):
        """Auth.generate_token() creates a new API token.

        All 4 args must be passed to avoid interactive input() / getpass() prompts.
        """
        info = docker_jenkins_server
        token = yojenkins_instance.auth.generate_token(
            token_name='integration-test-token',
            server_base_url=info['url'],
            username=info['username'],
            password=info['password'],
        )
        assert token
        assert len(token) > 0
