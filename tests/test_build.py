"""Tests for yojenkins.yo_jenkins.build module"""

from unittest.mock import MagicMock, patch

import pytest

from yojenkins.yo_jenkins.build import Build
from yojenkins.yo_jenkins.exceptions import YoJenkinsException
from yojenkins.yo_jenkins.status import BuildStatus

# ---------------------------------------------------------------------------
# Helpers / fixtures
# ---------------------------------------------------------------------------

VALID_BUILD_CLASS = 'org.jenkinsci.plugins.workflow.job.WorkflowRun'
VALID_JOB_CLASS = 'org.jenkinsci.plugins.workflow.job.WorkflowJob'
SERVER_URL = 'http://localhost:8080/'
BUILD_URL = 'http://localhost:8080/job/my_job/42/'
JOB_URL = 'http://localhost:8080/job/my_job/'


def _make_build_info(
    build_number=42,
    result='SUCCESS',
    timestamp=1700000000000,
    duration=60000,
    estimated_duration=120000,
    build_class=VALID_BUILD_CLASS,
    url=BUILD_URL,
    built_on='',
):
    """Return a realistic Jenkins build info dict."""
    return {
        '_class': build_class,
        'number': build_number,
        'url': url,
        'result': result,
        'timestamp': timestamp,
        'duration': duration,
        'estimatedDuration': estimated_duration,
        'builtOn': built_on,
        'actions': [],
    }


def _make_job_info(last_build_number=42, job_class=VALID_JOB_CLASS):
    return {
        '_class': job_class,
        'fullName': 'my_job',
        'lastBuild': {'number': last_build_number},
    }


@pytest.fixture
def build_obj(mock_rest, mock_auth):
    """Create a Build instance with mocked dependencies."""
    with patch('yojenkins.yo_jenkins.build.BuildMonitor'):
        return Build(mock_rest, mock_auth)


# ---------------------------------------------------------------------------
# Constructor
# ---------------------------------------------------------------------------


class TestBuildConstructor:
    def test_init_stores_rest_and_auth(self, mock_rest, mock_auth):
        with patch('yojenkins.yo_jenkins.build.BuildMonitor'):
            b = Build(mock_rest, mock_auth)
        assert b.rest is mock_rest
        assert b.auth is mock_auth

    def test_init_sets_log_extension(self, build_obj):
        assert build_obj.build_logs_extension == '.log'


# ---------------------------------------------------------------------------
# info()
# ---------------------------------------------------------------------------


class TestBuildInfo:
    def test_info_by_build_url(self, build_obj):
        """info() with a build URL should request <url>/api/json."""
        build_info = _make_build_info()
        build_obj.rest.request.return_value = (build_info, {}, True)

        result = build_obj.info(build_url=BUILD_URL)

        assert result['_class'] == VALID_BUILD_CLASS
        assert result['number'] == 42
        # Verify derived fields were added
        assert 'startDatetime' in result
        assert 'fullName' in result

    def test_info_by_job_name_and_build_number(self, build_obj):
        """info() with job_name + build_number should look up the job first."""
        job_info = _make_job_info()
        build_info = _make_build_info()

        build_obj.rest.request.side_effect = [
            (job_info, {}, True),     # job info request
            (build_info, {}, True),   # build info request
        ]

        result = build_obj.info(job_name='my_job', build_number=42)

        assert result['number'] == 42
        assert build_obj.rest.request.call_count == 2

    def test_info_by_job_name_latest(self, build_obj):
        """info() with job_name + latest=True uses the last build number."""
        job_info = _make_job_info(last_build_number=99)
        build_info = _make_build_info(build_number=99)

        build_obj.rest.request.side_effect = [
            (job_info, {}, True),
            (build_info, {}, True),
        ]

        result = build_obj.info(job_name='my_job', latest=True)
        assert result['number'] == 99

    def test_info_no_job_no_url_fails(self, build_obj):
        """info() without job_name, job_url, or build_url calls fail_out."""
        with pytest.raises(YoJenkinsException):
            build_obj.info()

    def test_info_build_number_exceeds_last_fails(self, build_obj):
        """info() fails when build_number > last build number."""
        job_info = _make_job_info(last_build_number=10)
        build_obj.rest.request.return_value = (job_info, {}, True)

        with pytest.raises(YoJenkinsException):
            build_obj.info(job_name='my_job', build_number=999)

    def test_info_invalid_build_class_fails(self, build_obj):
        """info() fails when the returned class is not a build type."""
        bad_build = _make_build_info(build_class='com.cloudbees.hudson.plugins.folder.Folder')
        build_obj.rest.request.return_value = (bad_build, {}, True)

        with pytest.raises(YoJenkinsException):
            build_obj.info(build_url=BUILD_URL)

    def test_info_failed_request_by_url_fails(self, build_obj):
        """info() fails when REST request for build URL returns falsy data."""
        build_obj.rest.request.return_value = ({}, {}, True)

        with pytest.raises(YoJenkinsException):
            build_obj.info(build_url=BUILD_URL)

    def test_info_running_build_has_running_status(self, build_obj):
        """A build with result=None should have resultText RUNNING."""
        build_info = _make_build_info(result=None)
        build_obj.rest.request.return_value = (build_info, {}, True)

        result = build_obj.info(build_url=BUILD_URL)
        assert result['resultText'] == BuildStatus.RUNNING.value

    def test_info_no_timestamp_sets_not_run(self, build_obj):
        """A build without timestamp should have resultText NOT_RUN."""
        build_info = _make_build_info()
        del build_info['timestamp']
        build_obj.rest.request.return_value = (build_info, {}, True)

        result = build_obj.info(build_url=BUILD_URL)
        assert result['resultText'] == BuildStatus.NOT_RUN.value
        assert result['startDatetime'] is None

    def test_info_no_builton_key_sets_na(self, build_obj):
        """If builtOn key is missing, it should be set to N/A."""
        build_info = _make_build_info()
        del build_info['builtOn']
        build_obj.rest.request.return_value = (build_info, {}, True)

        result = build_obj.info(build_url=BUILD_URL)
        assert result['builtOn'] == 'N/A'

    def test_info_no_build_number_no_latest_fails(self, build_obj):
        """info() with job_name but no build_number and latest=False should fail."""
        job_info = _make_job_info()
        build_obj.rest.request.return_value = (job_info, {}, True)

        with pytest.raises(YoJenkinsException):
            build_obj.info(job_name='my_job', build_number=None, latest=False)


# ---------------------------------------------------------------------------
# abort()
# ---------------------------------------------------------------------------


class TestBuildAbort:
    @patch('yojenkins.yo_jenkins.build.utility.build_url_to_build_number', return_value=42)
    def test_abort_by_build_url_success(self, mock_bn, build_obj):
        """abort() with build_url sends POST to <url>/stop."""
        build_obj.rest.request.return_value = ({}, {}, True)

        result = build_obj.abort(build_url=BUILD_URL)

        assert result == 42
        # Verify the stop endpoint was called
        call_args = build_obj.rest.request.call_args
        assert '/stop' in call_args[0][0]
        assert call_args[0][1] == 'post'

    def test_abort_failure_raises_exception(self, build_obj):
        """abort() raises RequestError when request fails."""
        build_obj.rest.request.return_value = ({}, {}, False)

        with pytest.raises(YoJenkinsException):
            build_obj.abort(build_url=BUILD_URL)

    @patch('yojenkins.yo_jenkins.build.utility.build_url_to_build_number', return_value=42)
    def test_abort_by_job_name_gets_info_first(self, mock_bn, build_obj):
        """abort() without build_url calls info() to get the URL."""
        build_info = _make_build_info()
        build_obj.rest.request.return_value = (build_info, {}, True)

        with patch.object(build_obj, 'info', return_value=build_info):
            result = build_obj.abort(job_name='my_job', build_number=42)

        assert result == 42


# ---------------------------------------------------------------------------
# delete()
# ---------------------------------------------------------------------------


class TestBuildDelete:
    @patch('yojenkins.yo_jenkins.build.utility.build_url_to_build_number', return_value=42)
    def test_delete_by_build_url_success(self, mock_bn, build_obj):
        """delete() with build_url sends POST to <url>/doDelete."""
        build_obj.rest.request.return_value = ({}, {}, True)

        result = build_obj.delete(build_url=BUILD_URL)

        assert result == 42
        call_args = build_obj.rest.request.call_args
        assert '/doDelete' in call_args[0][0]
        assert call_args[0][1] == 'post'

    def test_delete_failure_exits(self, build_obj):
        """delete() calls fail_out when request fails."""
        build_obj.rest.request.return_value = ({}, {}, False)

        with pytest.raises(YoJenkinsException):
            build_obj.delete(build_url=BUILD_URL)

    @patch('yojenkins.yo_jenkins.build.utility.build_url_to_build_number', return_value=42)
    def test_delete_by_job_name(self, mock_bn, build_obj):
        """delete() without build_url calls info() to resolve URL."""
        build_info = _make_build_info()

        with patch.object(build_obj, 'info', return_value=build_info):
            build_obj.rest.request.return_value = ({}, {}, True)
            result = build_obj.delete(job_name='my_job', build_number=42)

        assert result == 42


# ---------------------------------------------------------------------------
# stage_list()
# ---------------------------------------------------------------------------


class TestBuildStageList:
    def test_stage_list_returns_stages(self, build_obj):
        """stage_list() returns parsed stages with derived fields."""
        stages_response = {
            'stages': [
                {
                    'name': 'Build',
                    'status': 'SUCCESS',
                    'startTimeMillis': 1700000000000,
                    'durationMillis': 5000,
                    'pauseDurationMillis': 0,
                    '_links': {'self': {'href': '/some/link'}},
                },
                {
                    'name': 'Test',
                    'status': 'SUCCESS',
                    'startTimeMillis': 1700000005000,
                    'durationMillis': 3000,
                    'pauseDurationMillis': 100,
                    '_links': {'self': {'href': '/some/other/link'}},
                },
            ]
        }
        build_obj.rest.request.return_value = (stages_response, {}, True)

        stage_list, stage_names = build_obj.stage_list(build_url=BUILD_URL)

        assert len(stage_list) == 2
        assert stage_names == ['Build', 'Test']
        assert 'startDatetime' in stage_list[0]
        assert 'durationFormatted' in stage_list[0]

    def test_stage_list_no_stages_key_fails(self, build_obj):
        """stage_list() fails when response has no 'stages' key."""
        build_obj.rest.request.return_value = ({'other': 'data'}, {}, True)

        with pytest.raises(YoJenkinsException):
            build_obj.stage_list(build_url=BUILD_URL)

    def test_stage_list_request_failure_exits(self, build_obj):
        """stage_list() fails when the REST request fails."""
        build_obj.rest.request.return_value = ({}, {}, False)

        with pytest.raises(YoJenkinsException):
            build_obj.stage_list(build_url=BUILD_URL)


# ---------------------------------------------------------------------------
# logs()
# ---------------------------------------------------------------------------


class TestBuildLogs:
    def test_logs_by_build_url(self, build_obj):
        """logs() fetches console text and returns True."""
        log_text = 'Started by user admin\nBuilding...\nFinished: SUCCESS'
        build_obj.rest.request.return_value = (log_text, {}, True)

        with patch('yojenkins.yo_jenkins.build.print2'):
            result = build_obj.logs(build_url=BUILD_URL)

        assert result is True

    def test_logs_with_tail(self, build_obj):
        """logs() with tail parameter trims log output."""
        log_text = 'line1\nline2\nline3\nline4\nline5'
        build_obj.rest.request.return_value = (log_text, {}, True)

        with patch('yojenkins.yo_jenkins.build.print2') as mock_print:
            build_obj.logs(build_url=BUILD_URL, tail=2)

        # tail=2 means last 2 lines
        printed_text = mock_print.call_args[0][0]
        assert 'line4' in printed_text
        assert 'line5' in printed_text

    def test_logs_request_failure_exits(self, build_obj):
        """logs() fails when REST request fails."""
        build_obj.rest.request.return_value = ('', {}, False)

        with pytest.raises(YoJenkinsException):
            build_obj.logs(build_url=BUILD_URL)

    def test_logs_without_build_url_uses_info(self, build_obj):
        """logs() without build_url calls info() to resolve URL."""
        build_info = _make_build_info()
        log_text = 'some logs'

        with patch.object(build_obj, 'info', return_value=build_info):
            build_obj.rest.request.return_value = (log_text, {}, True)
            with patch('yojenkins.yo_jenkins.build.print2'):
                result = build_obj.logs(job_name='my_job', build_number=42)

        assert result is True


# ---------------------------------------------------------------------------
# rebuild()
# ---------------------------------------------------------------------------


class TestBuildRebuild:
    def test_rebuild_with_parameters(self, build_obj):
        """rebuild() triggers buildWithParameters when build had parameters."""
        build_info = _make_build_info()
        build_info['actions'] = [
            {
                '_class': 'hudson.model.ParametersAction',
                'parameters': [
                    {'_class': 'hudson.model.StringParameterValue', 'name': 'BRANCH', 'value': 'main'},
                ],
            }
        ]
        headers = {'Location': 'http://localhost:8080/queue/item/123/'}

        with patch.object(build_obj, 'info', return_value=build_info):
            build_obj.rest.request.return_value = ({}, headers, True)
            result = build_obj.rebuild(build_url=BUILD_URL)

        assert result == 123

    def test_rebuild_without_parameters(self, build_obj):
        """rebuild() triggers /build when no parameters found."""
        build_info = _make_build_info()
        build_info['actions'] = []
        headers = {'Location': 'http://localhost:8080/queue/item/456/'}

        with patch.object(build_obj, 'info', return_value=build_info):
            build_obj.rest.request.return_value = ({}, headers, True)
            result = build_obj.rebuild(build_url=BUILD_URL)

        assert result == 456

    def test_rebuild_no_headers_fails(self, build_obj):
        """rebuild() fails when no Location header is returned."""
        build_info = _make_build_info()
        build_info['actions'] = []

        with patch.object(build_obj, 'info', return_value=build_info):
            build_obj.rest.request.return_value = ({}, {}, True)
            with pytest.raises(YoJenkinsException):
                build_obj.rebuild(build_url=BUILD_URL)


# ---------------------------------------------------------------------------
# diff()
# ---------------------------------------------------------------------------


class TestBuildDiff:
    def test_diff_logs_fetches_both_builds(self, build_obj):
        """diff() with logs=True fetches console text for both builds."""
        build_url_1 = 'http://localhost:8080/job/my_job/1/'
        build_url_2 = 'http://localhost:8080/job/my_job/2/'

        build_obj.rest.request.side_effect = [
            ('log content 1', {}, True),
            ('log content 2', {}, True),
        ]

        with patch('yojenkins.yo_jenkins.build.diff_show') as mock_diff:
            build_obj.diff(build_url_1=build_url_1, build_url_2=build_url_2, logs=True)

        mock_diff.assert_called_once()
        args = mock_diff.call_args[0]
        assert args[0] == 'log content 1'
        assert args[1] == 'log content 2'

    def test_diff_info_compares_yaml(self, build_obj):
        """diff() without logs compares build info as YAML."""
        build_url_1 = 'http://localhost:8080/job/my_job/1/'
        build_url_2 = 'http://localhost:8080/job/my_job/2/'

        build_info_1 = _make_build_info(build_number=1, url=build_url_1)
        build_info_2 = _make_build_info(build_number=2, url=build_url_2)

        with patch.object(build_obj, 'info', side_effect=[build_info_1, build_info_2]):
            with patch('yojenkins.yo_jenkins.build.diff_show') as mock_diff:
                build_obj.diff(build_url_1=build_url_1, build_url_2=build_url_2, logs=False)

        mock_diff.assert_called_once()

    def test_diff_empty_url_1_fails(self, build_obj):
        """diff() fails when BUILD_URL_1 is empty."""
        with pytest.raises(YoJenkinsException):
            build_obj.diff(build_url_1='', build_url_2=BUILD_URL)

    def test_diff_empty_url_2_fails(self, build_obj):
        """diff() fails when BUILD_URL_2 is empty."""
        with pytest.raises(YoJenkinsException):
            build_obj.diff(build_url_1=BUILD_URL, build_url_2='')

    def test_diff_logs_fetch_failure_exits(self, build_obj):
        """diff() with logs=True exits when first log fetch fails."""
        build_url_1 = 'http://localhost:8080/job/my_job/1/'
        build_url_2 = 'http://localhost:8080/job/my_job/2/'

        build_obj.rest.request.return_value = ('', {}, False)

        with pytest.raises(YoJenkinsException):
            build_obj.diff(build_url_1=build_url_1, build_url_2=build_url_2, logs=True)

    def test_diff_logs_second_fetch_failure_exits(self, build_obj):
        """diff() with logs=True exits when second log fetch fails."""
        build_url_1 = 'http://localhost:8080/job/my_job/1/'
        build_url_2 = 'http://localhost:8080/job/my_job/2/'

        build_obj.rest.request.side_effect = [
            ('log content 1', {}, True),
            ('', {}, False),
        ]

        with pytest.raises(YoJenkinsException):
            build_obj.diff(build_url_1=build_url_1, build_url_2=build_url_2, logs=True)


# ---------------------------------------------------------------------------
# status_text()
# ---------------------------------------------------------------------------


class TestBuildStatusText:
    def test_status_text_queued(self, build_obj):
        """status_text() returns QUEUED when build is in queue."""
        build_info = _make_build_info()
        queue_all = {
            'items': [
                {
                    'task': {
                        '_class': 'org.jenkinsci.plugins.workflow.job.WorkflowJob',
                        'url': JOB_URL,
                    },
                    'id': 99,
                }
            ]
        }
        with patch.object(build_obj, 'info', return_value=build_info):
            build_obj.rest.request.return_value = (queue_all, {}, True)
            result = build_obj.status_text(build_url=BUILD_URL)
        assert result == BuildStatus.QUEUED.value

    def test_status_text_not_found(self, build_obj):
        """status_text() exits when build is not found in queue."""
        build_info = _make_build_info()
        queue_all = {'items': []}
        with patch.object(build_obj, 'info', return_value=build_info):
            build_obj.rest.request.return_value = (queue_all, {}, True)
            with pytest.raises(YoJenkinsException):
                build_obj.status_text(build_url=BUILD_URL)

    def test_status_text_no_args_exits(self, build_obj):
        """status_text() exits when no identifiers are provided."""
        build_info = _make_build_info()
        # No job_url or job_name extractable, build_url is empty
        with patch.object(build_obj, 'info', return_value=build_info):
            build_obj.rest.request.return_value = ({'items': []}, {}, True)
            with pytest.raises(YoJenkinsException):
                build_obj.status_text(build_url='', job_name='', job_url='')


# ---------------------------------------------------------------------------
# browser_open()
# ---------------------------------------------------------------------------


class TestBuildBrowserOpen:
    @patch('yojenkins.yo_jenkins.build.utility.browser_open', return_value=True)
    def test_browser_open_by_url(self, mock_browser, build_obj):
        """browser_open() opens browser for given build URL."""
        result = build_obj.browser_open(build_url=BUILD_URL)
        assert result is True
        mock_browser.assert_called_once()

    @patch('yojenkins.yo_jenkins.build.utility.browser_open', return_value=False)
    def test_browser_open_failure_exits(self, mock_browser, build_obj):
        """browser_open() exits when browser_open utility fails."""
        with pytest.raises(YoJenkinsException):
            build_obj.browser_open(build_url=BUILD_URL)

    @patch('yojenkins.yo_jenkins.build.utility.browser_open', return_value=True)
    def test_browser_open_by_job_name(self, mock_browser, build_obj):
        """browser_open() resolves build URL from job name."""
        build_info = _make_build_info()
        with patch.object(build_obj, 'info', return_value=build_info):
            result = build_obj.browser_open(job_name='my_job', build_number=42)
        assert result is True


# ---------------------------------------------------------------------------
# parameters()
# ---------------------------------------------------------------------------


class TestBuildParameters:
    def test_parameters_returns_params(self, build_obj):
        """parameters() extracts build parameters."""
        build_info = _make_build_info()
        build_info['actions'] = [
            {
                '_class': 'hudson.model.ParametersAction',
                'parameters': [
                    {'_class': 'hudson.model.StringParameterValue', 'name': 'BRANCH', 'value': 'main'},
                ],
            }
        ]
        with patch.object(build_obj, 'info', return_value=build_info):
            params, params_list = build_obj.parameters(build_url=BUILD_URL)
        assert len(params) == 1
        assert 'BRANCH' in params_list[0]

    def test_parameters_no_params_exits(self, build_obj):
        """parameters() exits when no parameter actions found."""
        build_info = _make_build_info()
        build_info['actions'] = []
        with patch.object(build_obj, 'info', return_value=build_info):
            with pytest.raises(YoJenkinsException):
                build_obj.parameters(build_url=BUILD_URL)


# ---------------------------------------------------------------------------
# info() edge cases
# ---------------------------------------------------------------------------


class TestBuildInfoEdgeCases:
    def test_info_by_job_url(self, build_obj):
        """info() with job_url resolves build info."""
        job_info = _make_job_info(last_build_number=10)
        build_info = _make_build_info(build_number=5)
        build_obj.rest.request.side_effect = [
            (job_info, {}, True),
            (build_info, {}, True),
        ]
        result = build_obj.info(job_url=JOB_URL, build_number=5)
        assert result['number'] == 5

    def test_info_job_request_failure_exits(self, build_obj):
        """info() exits when job info request fails."""
        build_obj.rest.request.return_value = ({}, {}, False)
        with pytest.raises(YoJenkinsException):
            build_obj.info(job_name='my_job', build_number=1)

    def test_info_job_wrong_class_exits(self, build_obj):
        """info() exits when job class is not a job type."""
        job_info = {'_class': 'com.cloudbees.hudson.plugins.folder.Folder', 'fullName': 'f'}
        build_obj.rest.request.return_value = (job_info, {}, True)
        with pytest.raises(YoJenkinsException):
            build_obj.info(job_name='my_job', build_number=1)

    def test_info_build_request_failure_exits(self, build_obj):
        """info() exits when build info request fails."""
        job_info = _make_job_info(last_build_number=10)
        build_obj.rest.request.side_effect = [
            (job_info, {}, True),
            ({}, {}, False),
        ]
        with pytest.raises(YoJenkinsException):
            build_obj.info(job_name='my_job', build_number=5)

    def test_info_result_unknown_when_no_result_key(self, build_obj):
        """info() sets resultText to UNKNOWN when result key is missing."""
        build_info = _make_build_info()
        del build_info['result']
        build_obj.rest.request.return_value = (build_info, {}, True)
        result = build_obj.info(build_url=BUILD_URL)
        assert result['resultText'] == BuildStatus.UNKNOWN.value

    def test_info_empty_builton_set_to_na(self, build_obj):
        """info() sets builtOn to N/A when builtOn is empty string."""
        build_info = _make_build_info(built_on='')
        build_obj.rest.request.return_value = (build_info, {}, True)
        result = build_obj.info(build_url=BUILD_URL)
        assert result['builtOn'] == 'N/A'

    def test_info_estimated_duration_zero(self, build_obj):
        """info() handles zero estimatedDuration."""
        build_info = _make_build_info(estimated_duration=0)
        build_obj.rest.request.return_value = (build_info, {}, True)
        result = build_obj.info(build_url=BUILD_URL)
        assert result['estimatedDurationFormatted'] is None


# ---------------------------------------------------------------------------
# artifact_list()
# ---------------------------------------------------------------------------


class TestBuildArtifactList:
    def test_artifact_list_returns_artifacts(self, build_obj):
        """artifact_list() returns artifacts from build info."""
        build_info = _make_build_info()
        build_info['artifacts'] = [{'fileName': 'out.jar'}]
        build_obj.rest.request.return_value = (build_info, {}, True)
        result = build_obj.artifact_list(build_url=BUILD_URL)
        assert len(result) == 1

    def test_artifact_list_none(self, build_obj):
        """artifact_list() returns None when no artifacts."""
        build_info = _make_build_info()
        build_obj.rest.request.return_value = (build_info, {}, True)
        result = build_obj.artifact_list(build_url=BUILD_URL)
        assert result is None


# ---------------------------------------------------------------------------
# logs() edge cases
# ---------------------------------------------------------------------------


class TestBuildLogsEdgeCases:
    def test_logs_with_tail_fraction(self, build_obj):
        """logs() with tail as fraction trims proportionally."""
        lines = '\n'.join([f'line{i}' for i in range(100)])
        build_obj.rest.request.return_value = (lines, {}, True)
        with patch('yojenkins.yo_jenkins.build.print2') as mock_print:
            build_obj.logs(build_url=BUILD_URL, tail=0.1)
        printed = mock_print.call_args[0][0]
        # Should show roughly last 10% of lines
        assert 'line99' in printed

    def test_logs_download_to_file(self, build_obj, tmp_path):
        """logs() with download_dir saves to file."""
        mock_response = MagicMock()
        mock_response.iter_content.return_value = [b'log data']
        mock_response.raise_for_status = MagicMock()
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)
        with patch('yojenkins.yo_jenkins.build.requests.get', return_value=mock_response):
            result = build_obj.logs(build_url=BUILD_URL, download_dir=str(tmp_path))
        assert result is True

    def test_logs_download_failure_exits(self, build_obj, tmp_path):
        """logs() download failure calls fail_out."""
        with patch('yojenkins.yo_jenkins.build.requests.get', side_effect=Exception('net error')):
            with pytest.raises(YoJenkinsException):
                build_obj.logs(build_url=BUILD_URL, download_dir=str(tmp_path))

    def test_logs_follow_progressive_text(self, build_obj):
        """logs() with follow uses progressiveText when supported."""
        build_obj.rest.request.side_effect = [
            ('', {'X-Text-Size': '0'}, True),  # head check
            ('log line 1\n', {'X-Text-Size': '100'}, True),  # first get (no X-More-Data = stop)
        ]
        with patch('yojenkins.yo_jenkins.build.print2'):
            result = build_obj.logs(build_url=BUILD_URL, follow=True)
        assert result is True

    def test_logs_follow_no_progressive_text(self, build_obj):
        """logs() with follow falls back to diff method when no progressiveText."""
        # The code checks 'content-length' (lowercase) in dict but reads 'Content-Length'
        headers_with_cl = {'content-length': '10', 'Content-Length': '10'}
        build_obj.rest.request.side_effect = [
            ('', {}, True),  # head check for progressiveText - no X-Text-Size
            ('', headers_with_cl, True),  # METHOD 2: first head sample 1
        ]
        # KeyboardInterrupt on sleep(1) between the two head samples
        with patch('yojenkins.yo_jenkins.build.sleep', side_effect=KeyboardInterrupt):
            with patch('yojenkins.yo_jenkins.build.print2'):
                result = build_obj.logs(build_url=BUILD_URL, follow=True)
        assert result is True


# ---------------------------------------------------------------------------
# monitor()
# ---------------------------------------------------------------------------


class TestBuildMonitor:
    def test_monitor_with_build_url(self, build_obj):
        """monitor() with build_url calls monitor_start."""
        build_obj.rest.request.return_value = ({}, {}, True)
        build_obj.build_monitor = MagicMock()
        build_obj.build_monitor.monitor_start.return_value = True
        result = build_obj.monitor(build_url=BUILD_URL)
        assert result is True

    def test_monitor_with_job_name_uses_info(self, build_obj):
        """monitor() without build_url gets info first."""
        build_info = _make_build_info()
        build_obj.build_monitor = MagicMock()
        build_obj.build_monitor.monitor_start.return_value = True
        with patch.object(build_obj, 'info', return_value=build_info):
            result = build_obj.monitor(job_name='my_job', latest=True)
        assert result is True

    def test_monitor_failure_exits(self, build_obj):
        """monitor() exits when monitor_start fails."""
        build_obj.rest.request.return_value = ({}, {}, True)
        build_obj.build_monitor = MagicMock()
        build_obj.build_monitor.monitor_start.return_value = False
        with pytest.raises(YoJenkinsException):
            build_obj.monitor(build_url=BUILD_URL)


# ---------------------------------------------------------------------------
# parameters() edge cases
# ---------------------------------------------------------------------------


class TestBuildParametersEdgeCases:
    def test_parameters_no_url_gets_from_info(self, build_obj):
        """parameters() with no build_url gets URL from info."""
        build_info = _make_build_info()
        build_info['actions'] = [
            {'_class': 'hudson.model.ParametersAction', 'parameters': [
                {'name': 'BRANCH', 'value': 'main', '_class': 'StringParameterValue'}
            ]}
        ]
        with patch.object(build_obj, 'info', return_value=build_info):
            with patch('yojenkins.yo_jenkins.build.utility.build_url_complete', return_value=None):
                with patch('yojenkins.yo_jenkins.build.utility.get_item_action', return_value=[
                    {'parameters': [{'name': 'BRANCH', 'value': 'main', '_class': 'StringParameterValue'}]}
                ]):
                    params, params_list = build_obj.parameters(job_name='my_job', latest=True)
        assert params[0]['name'] == 'BRANCH'


# ---------------------------------------------------------------------------
# rebuild()
# ---------------------------------------------------------------------------


class TestBuildRebuild:
    def test_rebuild_with_parameters(self, build_obj):
        """rebuild() triggers build with parameters."""
        build_info = _make_build_info()
        build_info['actions'] = [
            {'_class': 'hudson.model.ParametersAction', 'parameters': [
                {'name': 'BRANCH', 'value': 'main'}
            ]}
        ]
        build_obj.rest.request.return_value = ({}, {'Location': 'http://localhost:8080/queue/item/99/'}, True)
        with patch.object(build_obj, 'info', return_value=build_info):
            with patch('yojenkins.yo_jenkins.build.utility.build_url_complete', return_value=None):
                with patch('yojenkins.yo_jenkins.build.utility.get_item_action', return_value=[
                    {'parameters': [{'name': 'BRANCH', 'value': 'main'}]}
                ]):
                    with patch('yojenkins.yo_jenkins.build.utility.build_url_to_other_url',
                               return_value='http://localhost:8080/job/my_job'):
                        queue_num = build_obj.rebuild(job_name='my_job', latest=True)
        assert queue_num == 99

    def test_rebuild_without_parameters(self, build_obj):
        """rebuild() triggers build without parameters."""
        build_info = _make_build_info()
        build_info['actions'] = []
        build_obj.rest.request.return_value = ({}, {'Location': 'http://localhost:8080/queue/item/50/'}, True)
        with patch.object(build_obj, 'info', return_value=build_info):
            with patch('yojenkins.yo_jenkins.build.utility.build_url_complete', return_value=None):
                with patch('yojenkins.yo_jenkins.build.utility.get_item_action', return_value=[]):
                    with patch('yojenkins.yo_jenkins.build.utility.build_url_to_other_url',
                               return_value='http://localhost:8080/job/my_job'):
                        queue_num = build_obj.rebuild(job_name='my_job', latest=True)
        assert queue_num == 50


# ---------------------------------------------------------------------------
# status_text() edge cases
# ---------------------------------------------------------------------------


class TestBuildStatusTextEdgeCases:
    def test_status_queued(self, build_obj):
        """status_text() returns QUEUED when build is in queue."""
        build_info = _make_build_info()
        build_obj.rest.request.return_value = (
            {'items': [{'task': {'url': JOB_URL}, 'id': 1}]}, {}, True
        )
        with patch.object(build_obj, 'info', return_value=build_info):
            with patch('yojenkins.yo_jenkins.build.utility.build_url_complete', return_value=BUILD_URL):
                with patch('yojenkins.yo_jenkins.build.utility.queue_find',
                           return_value=[{'id': 1, 'task': {'url': JOB_URL}}]):
                    with patch('yojenkins.yo_jenkins.build.utility.build_url_to_other_url',
                               return_value=JOB_URL):
                        result = build_obj.status_text(build_url=BUILD_URL)
        assert result == 'QUEUED'

    def test_lastbuild_none_exits(self, build_obj):
        """status_text() exits when lastBuild is None (TypeError)."""
        job_info = _make_job_info()
        job_info['lastBuild'] = None
        build_obj.rest.request.return_value = (job_info, {}, True)
        with pytest.raises(YoJenkinsException):
            build_obj.status_text(job_name='my_job', build_number=1)
