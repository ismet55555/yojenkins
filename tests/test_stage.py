"""Tests for yojenkins.yo_jenkins.stage.Stage"""

from unittest.mock import MagicMock, patch

import pytest

from yojenkins.yo_jenkins.exceptions import YoJenkinsException
from yojenkins.yo_jenkins.stage import Stage


@pytest.fixture
def mock_build():
    """Mock Build object."""
    build = MagicMock()
    return build


@pytest.fixture
def mock_step_obj():
    """Mock Step object."""
    step = MagicMock()
    return step


@pytest.fixture
def stage(mock_rest, mock_build, mock_step_obj):
    """Create a Stage instance with mocked dependencies."""
    return Stage(rest=mock_rest, build=mock_build, step=mock_step_obj)


def _make_stage_info():
    """Helper to produce a valid stage info response."""
    return {
        'name': 'Build',
        'status': 'SUCCESS',
        'startTimeMillis': 1700000000000,
        'durationMillis': 5000,
        'pauseDurationMillis': 0,
        'stageFlowNodes': [
            {
                'name': 'Shell Script',
                'startTimeMillis': 1700000000000,
                'durationMillis': 3000,
                'pauseDurationMillis': 0,
                '_links': {
                    'self': {'href': '/job/test/1/execution/node/6/'},
                    'log': {'href': '/job/test/1/execution/node/6/log/'},
                    'console': {'href': '/job/test/1/execution/node/6/console/'},
                },
            }
        ],
    }


# --- Stage.__init__ ---

class TestStageInit:
    def test_init_sets_attributes(self, mock_rest, mock_build, mock_step_obj):
        s = Stage(rest=mock_rest, build=mock_build, step=mock_step_obj)
        assert s.rest is mock_rest
        assert s.build is mock_build
        assert s.step is mock_step_obj
        assert s.build_logs_extension == '.log'


# --- Stage.info ---

class TestStageInfo:
    def test_info_returns_enriched_stage_data(self, stage):
        stage.build.stage_list.return_value = (
            [{'name': 'Build', 'url': 'http://localhost:8080/job/test/1/execution/node/5/'}],
            ['Build'],
        )
        stage_info = _make_stage_info()
        stage.rest.request.return_value = (stage_info, {}, True)
        stage.rest.get_server_url = MagicMock(return_value='http://localhost:8080')

        result = stage.info(stage_name='Build', build_url='http://localhost:8080/job/test/1/')
        assert 'startDatetime' in result
        assert 'durationFormatted' in result
        assert 'numberOfSteps' in result
        assert result['numberOfSteps'] == 1

    def test_info_fail_out_when_stage_not_found(self, stage):
        stage.build.stage_list.return_value = (
            [{'name': 'Deploy'}],
            ['Deploy'],
        )
        with pytest.raises(YoJenkinsException):
            stage.info(stage_name='NonExistent', build_url='http://localhost:8080/job/test/1/')

    def test_info_case_insensitive_stage_name(self, stage):
        stage.build.stage_list.return_value = (
            [{'name': 'Build', 'url': 'http://localhost:8080/job/test/1/execution/node/5/'}],
            ['Build'],
        )
        stage_info = _make_stage_info()
        stage.rest.request.return_value = (stage_info, {}, True)
        stage.rest.get_server_url = MagicMock(return_value='http://localhost:8080')

        result = stage.info(stage_name='  build  ', build_url='http://localhost:8080/job/test/1/')
        assert result['name'] == 'Build'

    def test_info_fail_out_on_empty_response(self, stage):
        stage.build.stage_list.return_value = (
            [{'name': 'Build', 'url': 'http://localhost:8080/job/test/1/execution/node/5/'}],
            ['Build'],
        )
        stage.rest.request.return_value = ({}, {}, True)
        with pytest.raises(YoJenkinsException):
            stage.info(stage_name='Build', build_url='http://localhost:8080/job/test/1/')


# --- Stage.status_text ---

class TestStageStatusText:
    def test_status_text_returns_status(self, stage):
        stage.build.stage_list.return_value = (
            [{'name': 'Build', 'url': 'http://localhost:8080/job/test/1/execution/node/5/'}],
            ['Build'],
        )
        stage_info = _make_stage_info()
        stage.rest.request.return_value = (stage_info, {}, True)
        stage.rest.get_server_url = MagicMock(return_value='http://localhost:8080')

        result = stage.status_text(stage_name='Build', build_url='http://localhost:8080/job/test/1/')
        assert result == 'SUCCESS'

    def test_status_text_returns_unknown_when_no_status(self, stage):
        stage.build.stage_list.return_value = (
            [{'name': 'Build', 'url': 'http://localhost:8080/job/test/1/execution/node/5/'}],
            ['Build'],
        )
        stage_info = _make_stage_info()
        stage_info['status'] = None
        stage.rest.request.return_value = (stage_info, {}, True)
        stage.rest.get_server_url = MagicMock(return_value='http://localhost:8080')

        result = stage.status_text(stage_name='Build', build_url='http://localhost:8080/job/test/1/')
        assert result == 'UNKNOWN'


# --- Stage.step_list ---

class TestStageStepList:
    def test_step_list_returns_steps_and_names(self, stage):
        stage.build.stage_list.return_value = (
            [{'name': 'Build', 'url': 'http://localhost:8080/job/test/1/execution/node/5/'}],
            ['Build'],
        )
        stage_info = _make_stage_info()
        stage.rest.request.return_value = (stage_info, {}, True)
        stage.rest.get_server_url = MagicMock(return_value='http://localhost:8080')

        step_list, step_names = stage.step_list(
            stage_name='Build', build_url='http://localhost:8080/job/test/1/'
        )
        assert len(step_list) == 1
        assert 'Shell Script' in step_names

    def test_step_list_fail_out_when_no_stage_flow_nodes(self, stage):
        # Mock info() directly to return data without stageFlowNodes
        stage_info_no_steps = {
            'name': 'Build',
            'status': 'SUCCESS',
            'startDatetime': 'Monday, January 01, 2024 12:00:00',
            'durationFormatted': '0:05',
            'pauseDurationFormatted': '0:00:00',
            'numberOfSteps': 0,
        }
        with patch.object(stage, 'info', return_value=stage_info_no_steps):
            with pytest.raises(YoJenkinsException):
                stage.step_list(stage_name='Build', build_url='http://localhost:8080/job/test/1/')

    def test_step_list_adds_default_parameter_description(self, stage):
        stage.build.stage_list.return_value = (
            [{'name': 'Build', 'url': 'http://localhost:8080/job/test/1/execution/node/5/'}],
            ['Build'],
        )
        stage_info = _make_stage_info()
        # Ensure no parameterDescription exists
        for node in stage_info['stageFlowNodes']:
            node.pop('parameterDescription', None)
        stage.rest.request.return_value = (stage_info, {}, True)
        stage.rest.get_server_url = MagicMock(return_value='http://localhost:8080')

        step_list, _ = stage.step_list(
            stage_name='Build', build_url='http://localhost:8080/job/test/1/'
        )
        assert step_list[0]['parameterDescription'] == 'No command parameters listed'


# --- Stage.logs ---

class TestStageLogs:
    @patch('yojenkins.yo_jenkins.stage.print2')
    def test_logs_prints_to_console(self, mock_print2, stage):
        stage.build.stage_list.return_value = (
            [{'name': 'Build', 'url': 'http://localhost:8080/job/test/1/execution/node/5/'}],
            ['Build'],
        )
        stage_info = _make_stage_info()
        stage.rest.request.return_value = (stage_info, {}, True)
        stage.rest.get_server_url = MagicMock(return_value='http://localhost:8080')
        stage.step.info.return_value = {'text': '<b>hello</b>', 'length': 5}

        result = stage.logs(stage_name='Build', build_url='http://localhost:8080/job/test/1/')
        assert result is True
        mock_print2.assert_called_once()

    @patch('builtins.open', MagicMock())
    def test_logs_download_to_file(self, stage):
        stage.build.stage_list.return_value = (
            [{'name': 'Build', 'url': 'http://localhost:8080/job/test/1/execution/node/5/'}],
            ['Build'],
        )
        stage_info = _make_stage_info()
        stage.rest.request.return_value = (stage_info, {}, True)
        stage.rest.get_server_url = MagicMock(return_value='http://localhost:8080')
        stage.step.info.return_value = {'text': '<b>hello</b>', 'length': 5}

        result = stage.logs(
            stage_name='Build', build_url='http://localhost:8080/job/test/1/',
            download_dir='/tmp'
        )
        assert result is True

    def test_step_list_key_error(self, stage):
        """Test step_list when stageFlowNodes items are missing 'name' key."""
        bad_stage_info = {
            'name': 'Build',
            'status': 'SUCCESS',
            'startDatetime': 'Monday, January 01, 2024 12:00:00',
            'durationFormatted': '0:05',
            'pauseDurationFormatted': '0:00:00',
            'numberOfSteps': 1,
            'stageFlowNodes': [{'bad_key': 'value'}],
        }
        with patch.object(stage, 'info', return_value=bad_stage_info):
            with pytest.raises(YoJenkinsException):
                stage.step_list(stage_name='Build', build_url='http://localhost:8080/job/test/1/')
