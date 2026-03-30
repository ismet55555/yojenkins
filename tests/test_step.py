"""Tests for yojenkins.yo_jenkins.step.Step"""

import pytest

from yojenkins.yo_jenkins.exceptions import YoJenkinsException
from yojenkins.yo_jenkins.step import Step


@pytest.fixture
def step(mock_rest):
    """Create a Step instance with mocked rest."""
    return Step(rest=mock_rest)


class TestStepInit:
    def test_init_sets_rest(self, mock_rest):
        s = Step(rest=mock_rest)
        assert s.rest is mock_rest


class TestStepInfo:
    def test_info_returns_content(self, step):
        step.rest.request.return_value = ({'text': 'log output', 'length': 10}, {}, True)
        result = step.info(step_url='/job/test/1/execution/node/6/log/')
        assert result == {'text': 'log output', 'length': 10}
        # strip("/") removes both leading and trailing slashes
        step.rest.request.assert_called_once_with('job/test/1/execution/node/6/log', 'get', is_endpoint=True)

    def test_info_strips_slashes_from_url(self, step):
        step.rest.request.return_value = ({'text': 'ok', 'length': 2}, {}, True)
        step.info(step_url='/some/path/')
        # strip("/") removes both leading and trailing slashes
        step.rest.request.assert_called_once_with('some/path', 'get', is_endpoint=True)

    def test_info_fail_out_on_empty_response(self, step):
        step.rest.request.return_value = ({}, {}, True)
        with pytest.raises(YoJenkinsException):
            step.info(step_url='/job/test/1/execution/node/6/log/')

    def test_info_fail_out_on_none_response(self, step):
        step.rest.request.return_value = (None, {}, True)
        with pytest.raises(YoJenkinsException):
            step.info(step_url='/job/test/1/execution/node/6/log/')
