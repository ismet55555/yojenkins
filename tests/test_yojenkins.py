"""Tests for yojenkins/yo_jenkins/yojenkins.py - Composite root class"""

from unittest.mock import MagicMock

from yojenkins.yo_jenkins.yojenkins import YoJenkins


class TestYoJenkinsInit:
    def test_init_sets_auth(self):
        mock_auth = MagicMock()
        mock_auth.get_rest.return_value = MagicMock()
        mock_auth.jenkins_sdk = MagicMock()

        yj = YoJenkins(auth=mock_auth)
        assert yj.auth is mock_auth

    def test_init_sets_rest_from_auth(self):
        mock_auth = MagicMock()
        mock_rest = MagicMock()
        mock_auth.get_rest.return_value = mock_rest
        mock_auth.jenkins_sdk = MagicMock()

        yj = YoJenkins(auth=mock_auth)
        assert yj.rest is mock_rest

    def test_init_sets_jenkins_sdk(self):
        mock_auth = MagicMock()
        mock_sdk = MagicMock()
        mock_auth.get_rest.return_value = MagicMock()
        mock_auth.jenkins_sdk = mock_sdk

        yj = YoJenkins(auth=mock_auth)
        assert yj.jenkins_sdk is mock_sdk

    def test_init_creates_all_sub_objects(self):
        mock_auth = MagicMock()
        mock_auth.get_rest.return_value = MagicMock()
        mock_auth.jenkins_sdk = MagicMock()

        yj = YoJenkins(auth=mock_auth)
        assert yj.server is not None
        assert yj.node is not None
        assert yj.account is not None
        assert yj.credential is not None
        assert yj.folder is not None
        assert yj.build is not None
        assert yj.job is not None
        assert yj.step is not None
        assert yj.stage is not None
