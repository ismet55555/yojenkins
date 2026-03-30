"""Tests for yojenkins/yo_jenkins/job.py"""

from unittest.mock import MagicMock, patch

import pytest

from yojenkins.yo_jenkins.exceptions import YoJenkinsException

# Valid Jenkins job class type for use in fixtures
JOB_CLASS = 'org.jenkinsci.plugins.workflow.job.WorkflowJob'
FOLDER_CLASS = 'com.cloudbees.hudson.plugins.folder.Folder'
SERVER_URL = 'http://localhost:8080/'


@pytest.fixture
def mock_folder():
    """Mock Folder object."""
    folder = MagicMock()
    folder.item_list.return_value = ([], [])
    return folder


@pytest.fixture
def mock_jenkins_sdk():
    """Mock Jenkins SDK."""
    sdk = MagicMock()
    sdk.get_all_jobs.return_value = []
    return sdk


@pytest.fixture
def mock_build():
    """Mock Build object."""
    return MagicMock()


@pytest.fixture
def job_instance(mock_rest, mock_folder, mock_jenkins_sdk, mock_auth, mock_build):
    """Create a Job instance with all mocked dependencies."""
    with patch('yojenkins.yo_jenkins.job.JobMonitor'):
        from yojenkins.yo_jenkins.job import Job

        return Job(mock_rest, mock_folder, mock_jenkins_sdk, mock_auth, mock_build)


# ---------------------------------------------------------------------------
# Constructor
# ---------------------------------------------------------------------------


class TestJobConstructor:
    def test_constructor_assigns_dependencies(self, mock_rest, mock_folder, mock_jenkins_sdk, mock_auth, mock_build):
        with patch('yojenkins.yo_jenkins.job.JobMonitor'):
            from yojenkins.yo_jenkins.job import Job

            job = Job(mock_rest, mock_folder, mock_jenkins_sdk, mock_auth, mock_build)
        assert job.rest is mock_rest
        assert job.folder is mock_folder
        assert job.jenkins_sdk is mock_jenkins_sdk
        assert job.auth is mock_auth
        assert job.build is mock_build

    def test_constructor_initializes_search_state(self, job_instance):
        assert job_instance.search_results == []
        assert job_instance.search_items_count == 0


# ---------------------------------------------------------------------------
# info()
# ---------------------------------------------------------------------------


class TestJobInfo:
    def test_info_by_url(self, job_instance):
        job_info = {
            '_class': JOB_CLASS,
            'name': 'my-job',
            'url': 'http://localhost:8080/job/my-job/',
        }
        job_instance.rest.request.return_value = (job_info, {}, True)

        result = job_instance.info(job_url='http://localhost:8080/job/my-job/')

        assert result['_class'] == JOB_CLASS
        assert result['name'] == 'my-job'
        job_instance.rest.request.assert_called_once()

    def test_info_by_name(self, job_instance):
        job_info = {
            '_class': JOB_CLASS,
            'name': 'my-job',
            'url': 'http://localhost:8080/job/my-job/',
        }
        job_instance.rest.request.return_value = (job_info, {}, True)

        result = job_instance.info(job_name='my-job')

        assert result['name'] == 'my-job'

    def test_info_no_name_no_url_exits(self, job_instance):
        with pytest.raises(YoJenkinsException):
            job_instance.info()

    def test_info_request_failure_exits(self, job_instance):
        job_instance.rest.request.return_value = ({}, {}, False)
        with pytest.raises(YoJenkinsException):
            job_instance.info(job_url='http://localhost:8080/job/bad/')

    def test_info_wrong_class_exits(self, job_instance):
        job_info = {
            '_class': FOLDER_CLASS,
            'name': 'a-folder',
            'url': 'http://localhost:8080/job/a-folder/',
        }
        job_instance.rest.request.return_value = (job_info, {}, True)
        with pytest.raises(YoJenkinsException):
            job_instance.info(job_url='http://localhost:8080/job/a-folder/')

    def test_info_adds_derived_fields(self, job_instance):
        job_info = {
            '_class': JOB_CLASS,
            'name': 'my-job',
            'url': 'http://localhost:8080/job/folder1/job/my-job/',
        }
        job_instance.rest.request.return_value = (job_info, {}, True)

        result = job_instance.info(job_url='http://localhost:8080/job/folder1/job/my-job/')

        assert 'fullName' in result
        assert 'jobUrl' in result
        assert 'folderUrl' in result
        assert 'serverURL' in result
        assert 'serverDomain' in result


# ---------------------------------------------------------------------------
# _recursive_search()
# ---------------------------------------------------------------------------


class TestRecursiveSearch:
    def test_finds_matching_jobs(self, job_instance):
        items = [
            {'_class': JOB_CLASS, 'fullname': 'my-job-1', 'name': 'my-job-1', 'url': 'http://x/job/my-job-1/'},
            {'_class': JOB_CLASS, 'fullname': 'other-thing', 'name': 'other-thing', 'url': 'http://x/job/other/'},
        ]
        job_instance._recursive_search('my-job', items, 0)
        assert len(job_instance.search_results) == 1
        assert job_instance.search_results[0]['fullname'] == 'my-job-1'

    def test_searches_nested_folders(self, job_instance):
        items = [
            {
                '_class': FOLDER_CLASS,
                'name': 'folder1',
                'url': 'http://x/job/folder1/',
                'jobs': [
                    {
                        '_class': JOB_CLASS,
                        'fullname': 'folder1/nested-job',
                        'name': 'nested-job',
                        'url': 'http://x/job/folder1/job/nested-job/',
                    },
                ],
            }
        ]
        job_instance._recursive_search('nested', items, 0)
        assert len(job_instance.search_results) == 1

    def test_name_only_search(self, job_instance):
        items = [
            {'_class': JOB_CLASS, 'fullname': 'folder/deploy', 'name': 'deploy', 'url': 'http://x/job/deploy/'},
        ]
        # fullname=False means search on 'name' key only
        job_instance._recursive_search('folder', items, 0, fullname=False)
        assert len(job_instance.search_results) == 0

        job_instance.search_results = []
        job_instance._recursive_search('deploy', items, 0, fullname=False)
        assert len(job_instance.search_results) == 1

    def test_regex_search(self, job_instance):
        items = [
            {'_class': JOB_CLASS, 'fullname': 'build-123', 'name': 'build-123', 'url': 'http://x/1/'},
            {'_class': JOB_CLASS, 'fullname': 'build-abc', 'name': 'build-abc', 'url': 'http://x/2/'},
            {'_class': JOB_CLASS, 'fullname': 'test-job', 'name': 'test-job', 'url': 'http://x/3/'},
        ]
        job_instance._recursive_search(r'build-\d+', items, 0)
        assert len(job_instance.search_results) == 1
        assert job_instance.search_results[0]['fullname'] == 'build-123'

    def test_counts_all_items_searched(self, job_instance):
        items = [
            {'_class': JOB_CLASS, 'fullname': 'a', 'name': 'a', 'url': 'http://x/a/'},
            {'_class': JOB_CLASS, 'fullname': 'b', 'name': 'b', 'url': 'http://x/b/'},
            {
                '_class': FOLDER_CLASS,
                'name': 'f',
                'url': 'http://x/f/',
                'jobs': [
                    {'_class': JOB_CLASS, 'fullname': 'f/c', 'name': 'c', 'url': 'http://x/f/c/'},
                ],
            },
        ]
        job_instance._recursive_search('zzz', items, 0)
        assert job_instance.search_items_count == 4  # a, b, folder f, c

    def test_invalid_regex_does_not_crash(self, job_instance):
        items = [
            {'_class': JOB_CLASS, 'fullname': 'job1', 'name': 'job1', 'url': 'http://x/1/'},
        ]
        job_instance._recursive_search('[invalid', items, 0)
        assert len(job_instance.search_results) == 0


# ---------------------------------------------------------------------------
# search()
# ---------------------------------------------------------------------------


class TestJobSearch:
    def test_search_all_jenkins(self, job_instance):
        all_jobs = [
            {'_class': JOB_CLASS, 'fullname': 'my-job', 'name': 'my-job', 'url': 'http://x/job/my-job/'},
        ]
        job_instance.jenkins_sdk.get_all_jobs.return_value = all_jobs

        results, urls = job_instance.search('my-job')

        assert len(results) == 1
        assert 'http://x/job/my-job/' in urls

    def test_search_with_folder_restriction(self, job_instance):
        folder_items = [
            {
                '_class': JOB_CLASS,
                'fullname': 'folder/job-a',
                'name': 'job-a',
                'url': 'http://x/job/folder/job/job-a/',
            },
        ]
        job_instance.folder.item_list.return_value = (folder_items, [])

        results, urls = job_instance.search('job-a', folder_name='folder')

        job_instance.folder.item_list.assert_called_once()
        assert len(results) == 1

    def test_search_name_only(self, job_instance):
        all_jobs = [
            {'_class': JOB_CLASS, 'fullname': 'prefix/target', 'name': 'target', 'url': 'http://x/job/target/'},
        ]
        job_instance.jenkins_sdk.get_all_jobs.return_value = all_jobs

        results, _ = job_instance.search('prefix', fullname=False)
        assert len(results) == 0

        results, _ = job_instance.search('target', fullname=False)
        assert len(results) == 1

    def test_search_jenkins_exception_exits(self, job_instance):
        import jenkins

        job_instance.jenkins_sdk.get_all_jobs.side_effect = jenkins.JenkinsException('Server error\n<html>')
        with pytest.raises(YoJenkinsException):
            job_instance.search('anything')


# ---------------------------------------------------------------------------
# build_trigger()
# ---------------------------------------------------------------------------


class TestBuildTrigger:
    def _setup_trigger(self, job_instance):
        """Helper: configure mocks for a successful trigger."""
        job_info = {
            '_class': JOB_CLASS,
            'name': 'my-job',
            'url': 'http://localhost:8080/job/my-job/',
            'nextBuildNumber': 42,
        }
        # First call: info request (from build_next_number -> info)
        # Second call: post trigger
        job_instance.rest.request.side_effect = [
            (job_info, {}, True),
            ({}, {'Location': 'http://localhost:8080/queue/item/99/'}, True),
        ]

    def test_trigger_without_params(self, job_instance):
        self._setup_trigger(job_instance)

        result = job_instance.build_trigger(job_url='http://localhost:8080/job/my-job/')

        assert result == 99
        # Verify the post call used /build endpoint
        post_call = job_instance.rest.request.call_args_list[1]
        assert '/build' in post_call[0][0]
        assert 'buildWithParameters' not in post_call[0][0]

    def test_trigger_with_params(self, job_instance):
        self._setup_trigger(job_instance)

        result = job_instance.build_trigger(
            job_url='http://localhost:8080/job/my-job/',
            paramters={'BRANCH': 'main'},
        )

        assert result == 99
        post_call = job_instance.rest.request.call_args_list[1]
        assert 'buildWithParameters' in post_call[0][0]
        assert 'BRANCH=main' in post_call[0][0]

    def test_trigger_no_name_no_url_exits(self, job_instance):
        with pytest.raises(YoJenkinsException):
            job_instance.build_trigger()

    def test_trigger_no_headers_exits(self, job_instance):
        job_info = {
            '_class': JOB_CLASS,
            'name': 'my-job',
            'url': 'http://localhost:8080/job/my-job/',
            'nextBuildNumber': 42,
        }
        job_instance.rest.request.side_effect = [
            (job_info, {}, True),
            ({}, {}, True),  # empty headers
        ]
        with pytest.raises(YoJenkinsException):
            job_instance.build_trigger(job_url='http://localhost:8080/job/my-job/')


# ---------------------------------------------------------------------------
# config()
# ---------------------------------------------------------------------------


class TestJobConfig:
    def test_get_config_xml(self, job_instance):
        xml_content = '<project><description>test</description></project>'
        job_instance.rest.request.return_value = (xml_content, {}, True)

        result = job_instance.config(job_url='http://localhost:8080/job/my-job/')

        assert result == xml_content
        call_args = job_instance.rest.request.call_args
        assert 'config.xml' in call_args[0][0]

    def test_get_config_failure_exits(self, job_instance):
        job_instance.rest.request.return_value = ('', {}, False)
        with pytest.raises(YoJenkinsException):
            job_instance.config(job_url='http://localhost:8080/job/my-job/')

    def test_config_no_name_no_url_exits(self, job_instance):
        with pytest.raises(YoJenkinsException):
            job_instance.config()

    def test_config_by_name(self, job_instance):
        xml_content = '<project/>'
        job_instance.rest.request.return_value = (xml_content, {}, True)

        result = job_instance.config(job_name='my-job')

        assert result == xml_content


# ---------------------------------------------------------------------------
# create()
# ---------------------------------------------------------------------------


class TestJobCreate:
    @patch('yojenkins.yo_jenkins.job.utility.item_exists_in_folder', return_value=False)
    def test_create_success(self, mock_exists, job_instance, tmp_path):
        config_file = tmp_path / 'config.xml'
        config_file.write_text('<project/>')

        job_instance.rest.request.return_value = ({}, {}, True)

        result = job_instance.create(
            name='new-job',
            folder_url='http://localhost:8080/job/folder/',
            config_file=str(config_file),
        )

        assert result is True

    @patch('yojenkins.yo_jenkins.job.utility.item_exists_in_folder', return_value=False)
    def test_create_no_folder_exits(self, mock_exists, job_instance):
        with pytest.raises(YoJenkinsException):
            job_instance.create(name='new-job')

    @patch('yojenkins.yo_jenkins.job.utility.item_exists_in_folder', return_value=True)
    def test_create_already_exists_exits(self, mock_exists, job_instance):
        with pytest.raises(YoJenkinsException):
            job_instance.create(name='existing-job', folder_url='http://localhost:8080/job/folder/')

    @patch('yojenkins.yo_jenkins.job.utility.item_exists_in_folder', return_value=False)
    def test_create_blank_name_exits(self, mock_exists, job_instance):
        with pytest.raises(YoJenkinsException):
            job_instance.create(name='', folder_url='http://localhost:8080/job/folder/')


# ---------------------------------------------------------------------------
# delete()
# ---------------------------------------------------------------------------


class TestJobDelete:
    def test_delete_success(self, job_instance):
        job_instance.rest.request.return_value = ({}, {}, True)
        result = job_instance.delete(job_url='http://localhost:8080/job/my-job/')
        assert result is True
        call_args = job_instance.rest.request.call_args
        assert 'doDelete' in call_args[0][0]

    def test_delete_no_name_no_url_exits(self, job_instance):
        with pytest.raises(YoJenkinsException):
            job_instance.delete()

    def test_delete_failure_exits(self, job_instance):
        job_instance.rest.request.return_value = ({}, {}, False)
        with pytest.raises(YoJenkinsException):
            job_instance.delete(job_url='http://localhost:8080/job/my-job/')


# ---------------------------------------------------------------------------
# enable() / disable()
# ---------------------------------------------------------------------------


class TestJobEnableDisable:
    def test_enable_success(self, job_instance):
        job_instance.rest.request.return_value = ({}, {}, True)
        result = job_instance.enable(job_url='http://localhost:8080/job/my-job/')
        assert result is True
        call_args = job_instance.rest.request.call_args
        assert '/enable' in call_args[0][0]

    def test_enable_no_name_no_url_exits(self, job_instance):
        with pytest.raises(YoJenkinsException):
            job_instance.enable()

    def test_enable_failure_exits(self, job_instance):
        job_instance.rest.request.return_value = ({}, {}, False)
        with pytest.raises(YoJenkinsException):
            job_instance.enable(job_url='http://localhost:8080/job/my-job/')

    def test_disable_success(self, job_instance):
        job_instance.rest.request.return_value = ({}, {}, True)
        result = job_instance.disable(job_url='http://localhost:8080/job/my-job/')
        assert result is True
        call_args = job_instance.rest.request.call_args
        assert '/disable' in call_args[0][0]

    def test_disable_no_name_no_url_exits(self, job_instance):
        with pytest.raises(YoJenkinsException):
            job_instance.disable()

    def test_disable_failure_exits(self, job_instance):
        job_instance.rest.request.return_value = ({}, {}, False)
        with pytest.raises(YoJenkinsException):
            job_instance.disable(job_url='http://localhost:8080/job/my-job/')


# ---------------------------------------------------------------------------
# browser_open()
# ---------------------------------------------------------------------------


class TestBrowserOpen:
    @patch('yojenkins.yo_jenkins.job.utility.browser_open', return_value=True)
    def test_browser_open_success(self, mock_browser, job_instance):
        result = job_instance.browser_open(job_url='http://localhost:8080/job/my-job/')
        assert result is True
        mock_browser.assert_called_once()

    @patch('yojenkins.yo_jenkins.job.utility.browser_open', return_value=False)
    def test_browser_open_failure_exits(self, mock_browser, job_instance):
        with pytest.raises(YoJenkinsException):
            job_instance.browser_open(job_url='http://localhost:8080/job/my-job/')

    def test_browser_open_no_name_no_url_exits(self, job_instance):
        with pytest.raises(YoJenkinsException):
            job_instance.browser_open()


# ---------------------------------------------------------------------------
# build_next_number() / build_last_number()
# ---------------------------------------------------------------------------


class TestBuildNumbers:
    def test_build_next_number(self, job_instance):
        job_info = {
            '_class': JOB_CLASS,
            'name': 'my-job',
            'url': 'http://localhost:8080/job/my-job/',
            'nextBuildNumber': 42,
        }
        job_instance.rest.request.return_value = (job_info, {}, True)

        result = job_instance.build_next_number(job_url='http://localhost:8080/job/my-job/')
        assert result == 42

    def test_build_next_number_missing_exits(self, job_instance):
        job_info = {
            '_class': JOB_CLASS,
            'name': 'my-job',
            'url': 'http://localhost:8080/job/my-job/',
        }
        job_instance.rest.request.return_value = (job_info, {}, True)
        with pytest.raises(YoJenkinsException):
            job_instance.build_next_number(job_url='http://localhost:8080/job/my-job/')

    def test_build_last_number_from_info(self, job_instance):
        job_info = {
            '_class': JOB_CLASS,
            'name': 'my-job',
            'url': 'http://localhost:8080/job/my-job/',
            'lastBuild': {'number': 10, 'url': 'http://localhost:8080/job/my-job/10/'},
        }
        result = job_instance.build_last_number(job_info=job_info)
        assert result == 10

    def test_build_last_number_no_last_build(self, job_instance):
        job_info = {
            '_class': JOB_CLASS,
            'name': 'my-job',
            'url': 'http://localhost:8080/job/my-job/',
        }
        result = job_instance.build_last_number(job_info=job_info)
        assert result == 0


# ---------------------------------------------------------------------------
# rename()
# ---------------------------------------------------------------------------


class TestJobRename:
    def test_rename_success(self, job_instance):
        job_instance.rest.request.return_value = ({}, {}, True)
        result = job_instance.rename('new-name', job_url='http://localhost:8080/job/old-name/')
        assert result is True
        call_args = job_instance.rest.request.call_args
        assert 'doRename' in call_args[0][0]
        assert 'newName=new-name' in call_args[0][0]

    def test_rename_blank_name_exits(self, job_instance):
        with pytest.raises(YoJenkinsException):
            job_instance.rename('', job_url='http://localhost:8080/job/old/')

    def test_rename_special_chars_exits(self, job_instance):
        with pytest.raises(YoJenkinsException):
            job_instance.rename('bad@name!', job_url='http://localhost:8080/job/old/')

    def test_rename_no_name_no_url_exits(self, job_instance):
        with pytest.raises(YoJenkinsException):
            job_instance.rename('new-name')


# ---------------------------------------------------------------------------
# wipe_workspace()
# ---------------------------------------------------------------------------


class TestWipeWorkspace:
    def test_wipe_workspace_success(self, job_instance):
        job_instance.rest.request.return_value = ({}, {}, True)
        result = job_instance.wipe_workspace(job_url='http://localhost:8080/job/my-job/')
        assert result is True
        call_args = job_instance.rest.request.call_args
        assert 'doWipeOutWorkspace' in call_args[0][0]

    def test_wipe_workspace_no_name_no_url_exits(self, job_instance):
        with pytest.raises(YoJenkinsException):
            job_instance.wipe_workspace()

    def test_wipe_workspace_failure_exits(self, job_instance):
        job_instance.rest.request.return_value = ({}, {}, False)
        with pytest.raises(YoJenkinsException):
            job_instance.wipe_workspace(job_url='http://localhost:8080/job/my-job/')


# ---------------------------------------------------------------------------
# build_list()
# ---------------------------------------------------------------------------


class TestBuildList:
    def test_build_list_returns_builds(self, job_instance):
        job_info = {
            '_class': JOB_CLASS,
            'name': 'my-job',
            'url': 'http://localhost:8080/job/my-job/',
            'builds': [
                {'_class': 'org.jenkinsci.plugins.workflow.job.WorkflowRun', 'url': 'http://x/1/'},
                {'_class': 'org.jenkinsci.plugins.workflow.job.WorkflowRun', 'url': 'http://x/2/'},
            ],
        }
        job_instance.rest.request.return_value = (job_info, {}, True)
        builds, urls = job_instance.build_list(job_url='http://localhost:8080/job/my-job/')
        assert len(builds) == 2


# ---------------------------------------------------------------------------
# build_set_next_number()
# ---------------------------------------------------------------------------


class TestBuildSetNextNumber:
    def test_set_next_number_success(self, job_instance):
        result = job_instance.build_set_next_number(100, job_url='http://localhost:8080/job/my-job/')
        assert result == 100
        job_instance.jenkins_sdk.set_next_build_number.assert_called_once()

    def test_set_next_number_no_args_exits(self, job_instance):
        with pytest.raises(YoJenkinsException):
            job_instance.build_set_next_number(100)

    def test_set_next_number_jenkins_exception_exits(self, job_instance):
        import jenkins

        job_instance.jenkins_sdk.set_next_build_number.side_effect = jenkins.JenkinsException('Error\n<html>')
        with pytest.raises(YoJenkinsException):
            job_instance.build_set_next_number(100, job_url='http://localhost:8080/job/my-job/')


# ---------------------------------------------------------------------------
# queue_info()
# ---------------------------------------------------------------------------


class TestQueueInfo:
    def test_queue_info_by_number(self, job_instance):
        queue_data = {
            'id': 99,
            'url': 'queue/item/99/',
            'task': {'url': 'http://localhost:8080/job/my-job/'},
            'isQueuedItem': False,
        }
        job_instance.rest.request.return_value = (queue_data, {}, True)
        job_instance.rest.get_server_url = MagicMock(return_value='http://localhost:8080/')
        result = job_instance.queue_info(build_queue_number=99)
        assert result['isQueuedItem'] is True
        assert 'jobUrl' in result
        assert 'fullUrl' in result

    def test_queue_info_no_args_exits(self, job_instance):
        with pytest.raises(YoJenkinsException):
            job_instance.queue_info()

    def test_queue_info_empty_response(self, job_instance):
        job_instance.rest.request.return_value = ({}, {}, True)
        result = job_instance.queue_info(build_queue_number=99)
        assert result == {}


# ---------------------------------------------------------------------------
# in_queue_check()
# ---------------------------------------------------------------------------


class TestInQueueCheck:
    def test_in_queue_check_no_args_exits(self, job_instance):
        with pytest.raises(YoJenkinsException):
            job_instance.in_queue_check()

    def test_in_queue_check_found(self, job_instance):
        queue_all = {
            'items': [
                {
                    'task': {
                        '_class': JOB_CLASS,
                        'url': 'http://localhost:8080/job/my-job/',
                    },
                    'id': 99,
                    'url': 'queue/item/99/',
                    'inQueueSince': 5000,
                }
            ]
        }
        job_instance.rest.request.return_value = (queue_all, {}, True)
        job_instance.rest.get_server_url = MagicMock(return_value='http://localhost:8080/')
        result, queue_id = job_instance.in_queue_check(job_url='http://localhost:8080/job/my-job/')
        assert queue_id == 99

    def test_in_queue_check_not_found(self, job_instance):
        queue_all = {'items': []}
        job_instance.rest.request.return_value = (queue_all, {}, True)
        result, queue_id = job_instance.in_queue_check(job_name='my-job')
        assert result == {}
        assert queue_id == 0


# ---------------------------------------------------------------------------
# queue_abort()
# ---------------------------------------------------------------------------


class TestQueueAbort:
    def test_queue_abort_no_number_exits(self, job_instance):
        with pytest.raises(YoJenkinsException):
            job_instance.queue_abort(0)

    def test_queue_abort_success(self, job_instance):
        job_instance.rest.request.return_value = ('OK', {}, True)
        result = job_instance.queue_abort(99)
        assert result is True


# ---------------------------------------------------------------------------
# parameters()
# ---------------------------------------------------------------------------


class TestJobParameters:
    def test_parameters_found(self, job_instance):
        job_info = {
            '_class': JOB_CLASS,
            'name': 'my-job',
            'url': 'http://localhost:8080/job/my-job/',
            'actions': [
                {
                    '_class': 'hudson.model.ParametersDefinitionProperty',
                    'parameterDefinitions': [
                        {
                            'type': 'StringParameterDefinition',
                            'name': 'BRANCH',
                            'description': 'Branch name',
                            'defaultParameterValue': {
                                '_class': 'hudson.model.StringParameterValue',
                                'value': 'main',
                            },
                        }
                    ],
                }
            ],
        }
        job_instance.rest.request.return_value = (job_info, {}, True)
        params, params_list = job_instance.parameters(job_url='http://localhost:8080/job/my-job/')
        assert len(params) == 1
        assert 'BRANCH' in params_list[0]

    def test_parameters_not_found_exits(self, job_instance):
        job_info = {
            '_class': JOB_CLASS,
            'name': 'my-job',
            'url': 'http://localhost:8080/job/my-job/',
            'actions': [],
        }
        job_instance.rest.request.return_value = (job_info, {}, True)
        with pytest.raises(YoJenkinsException):
            job_instance.parameters(job_url='http://localhost:8080/job/my-job/')

    def test_parameters_bool_default(self, job_instance):
        job_info = {
            '_class': JOB_CLASS,
            'name': 'my-job',
            'url': 'http://localhost:8080/job/my-job/',
            'actions': [
                {
                    '_class': 'hudson.model.ParametersDefinitionProperty',
                    'parameterDefinitions': [
                        {
                            'type': 'BooleanParameterDefinition',
                            'name': 'DRY_RUN',
                            'description': '',
                            'defaultParameterValue': {
                                '_class': 'hudson.model.BooleanParameterValue',
                                'value': None,
                            },
                        }
                    ],
                }
            ],
        }
        job_instance.rest.request.return_value = (job_info, {}, True)
        params, params_list = job_instance.parameters(job_url='http://localhost:8080/job/my-job/')
        assert 'False' in params_list[0]


# ---------------------------------------------------------------------------
# diff()
# ---------------------------------------------------------------------------


class TestJobDiff:
    def test_diff_by_name(self, job_instance):
        job_info = {
            '_class': JOB_CLASS,
            'name': 'job1',
            'url': 'http://localhost:8080/job/job1/',
        }
        job_instance.rest.request.return_value = (job_info, {}, True)
        with patch('yojenkins.yo_jenkins.job.diff_show') as mock_diff:
            job_instance.diff(job_1='job1', job_2='job2')
        mock_diff.assert_called_once()

    def test_diff_by_url(self, job_instance):
        job_info = {
            '_class': JOB_CLASS,
            'name': 'job1',
            'url': 'http://localhost:8080/job/job1/',
        }
        job_instance.rest.request.return_value = (job_info, {}, True)
        with patch('yojenkins.yo_jenkins.job.diff_show') as mock_diff:
            job_instance.diff(
                job_1='http://localhost:8080/job/job1/',
                job_2='http://localhost:8080/job/job2/',
            )
        mock_diff.assert_called_once()


# ---------------------------------------------------------------------------
# config() edge cases
# ---------------------------------------------------------------------------


class TestJobConfigEdgeCases:
    @patch('yojenkins.yo_jenkins.job.utility.write_xml_to_file', return_value=True)
    def test_config_writes_to_file(self, mock_write, job_instance):
        xml_content = '<project/>'
        job_instance.rest.request.return_value = (xml_content, {}, True)
        result = job_instance.config(filepath='/tmp/config.xml', job_url='http://localhost:8080/job/my-job/')
        assert result == xml_content
        mock_write.assert_called_once()

    @patch('yojenkins.yo_jenkins.job.utility.write_xml_to_file', return_value=False)
    def test_config_write_failure_exits(self, mock_write, job_instance):
        job_instance.rest.request.return_value = ('<project/>', {}, True)
        with pytest.raises(YoJenkinsException):
            job_instance.config(filepath='/tmp/config.xml', job_url='http://localhost:8080/job/my-job/')


# ---------------------------------------------------------------------------
# disable() / enable() / rename() / delete() / wipe_workspace()
# ---------------------------------------------------------------------------


class TestJobDisable:
    def test_disable_by_url(self, job_instance):
        job_instance.rest.request.return_value = ({}, {}, True)
        result = job_instance.disable(job_url='http://localhost:8080/job/my-job/')
        assert result is True

    def test_disable_by_name(self, job_instance):
        job_instance.rest.request.return_value = ({}, {}, True)
        with patch('yojenkins.yo_jenkins.job.utility.name_to_url', return_value='http://localhost:8080/job/my-job'):
            result = job_instance.disable(job_name='my-job')
        assert result is True

    def test_disable_failure_exits(self, job_instance):
        job_instance.rest.request.return_value = ({}, {}, False)
        with pytest.raises(YoJenkinsException):
            job_instance.disable(job_url='http://localhost:8080/job/my-job/')


class TestJobEnable:
    def test_enable_by_url(self, job_instance):
        job_instance.rest.request.return_value = ({}, {}, True)
        result = job_instance.enable(job_url='http://localhost:8080/job/my-job/')
        assert result is True

    def test_enable_by_name(self, job_instance):
        job_instance.rest.request.return_value = ({}, {}, True)
        with patch('yojenkins.yo_jenkins.job.utility.name_to_url', return_value='http://localhost:8080/job/my-job'):
            result = job_instance.enable(job_name='my-job')
        assert result is True


class TestJobRename:
    def test_rename_by_url(self, job_instance):
        job_instance.rest.request.return_value = ({}, {}, True)
        result = job_instance.rename(new_name='new-job', job_url='http://localhost:8080/job/my-job/')
        assert result is True

    def test_rename_failure_exits(self, job_instance):
        job_instance.rest.request.return_value = ({}, {}, False)
        with pytest.raises(YoJenkinsException):
            job_instance.rename(new_name='new-job', job_url='http://localhost:8080/job/my-job/')

    def test_rename_blank_name_exits(self, job_instance):
        with pytest.raises(YoJenkinsException):
            job_instance.rename(new_name='', job_url='http://localhost:8080/job/my-job/')

    def test_rename_special_char_exits(self, job_instance):
        with pytest.raises(YoJenkinsException):
            job_instance.rename(new_name='bad@name', job_url='http://localhost:8080/job/my-job/')


class TestJobDelete:
    def test_delete_by_url(self, job_instance):
        job_instance.rest.request.return_value = ({}, {}, True)
        result = job_instance.delete(job_url='http://localhost:8080/job/my-job/')
        assert result is True

    def test_delete_by_name(self, job_instance):
        job_instance.rest.request.return_value = ({}, {}, True)
        with patch('yojenkins.yo_jenkins.job.utility.name_to_url', return_value='http://localhost:8080/job/my-job'):
            result = job_instance.delete(job_name='my-job')
        assert result is True


class TestJobWipeWorkspace:
    def test_wipe_by_url(self, job_instance):
        job_instance.rest.request.return_value = ({}, {}, True)
        result = job_instance.wipe_workspace(job_url='http://localhost:8080/job/my-job/')
        assert result is True

    def test_wipe_by_name(self, job_instance):
        job_instance.rest.request.return_value = ({}, {}, True)
        with patch('yojenkins.yo_jenkins.job.utility.name_to_url', return_value='http://localhost:8080/job/my-job'):
            result = job_instance.wipe_workspace(job_name='my-job')
        assert result is True


# ---------------------------------------------------------------------------
# monitor()
# ---------------------------------------------------------------------------


class TestJobMonitor:
    def test_monitor_by_url(self, job_instance):
        job_instance.rest.request.return_value = ({}, {}, True)
        job_instance.JM = MagicMock()
        job_instance.JM.monitor_start.return_value = True
        result = job_instance.monitor(job_url='http://localhost:8080/job/my-job/')
        assert result is True

    def test_monitor_failure_exits(self, job_instance):
        job_instance.rest.request.return_value = ({}, {}, True)
        job_instance.JM = MagicMock()
        job_instance.JM.monitor_start.return_value = False
        with pytest.raises(YoJenkinsException):
            job_instance.monitor(job_url='http://localhost:8080/job/my-job/')

    def test_monitor_job_not_found_exits(self, job_instance):
        job_instance.rest.request.return_value = ({}, {}, False)
        with pytest.raises(YoJenkinsException):
            job_instance.monitor(job_url='http://localhost:8080/job/my-job/')


# ---------------------------------------------------------------------------
# create()
# ---------------------------------------------------------------------------


class TestJobCreate:
    def test_create_success(self, job_instance, tmp_path):
        config_file = tmp_path / 'config.xml'
        config_file.write_text('<project/>')
        job_instance.rest.request.return_value = ({}, {}, True)
        with patch('yojenkins.yo_jenkins.job.utility.item_exists_in_folder', return_value=False):
            result = job_instance.create(
                name='new-job',
                folder_url='http://localhost:8080/job/folder/',
                config_file=str(config_file),
            )
        assert result is True

    def test_create_no_folder_exits(self, job_instance):
        with pytest.raises(YoJenkinsException):
            job_instance.create(name='new-job')

    def test_create_blank_name_exits(self, job_instance):
        with pytest.raises(YoJenkinsException):
            job_instance.create(name='', folder_url='http://localhost:8080/job/folder/')

    def test_create_special_char_name_exits(self, job_instance):
        with pytest.raises(YoJenkinsException):
            job_instance.create(name='bad@name', folder_url='http://localhost:8080/job/folder/')

    def test_create_already_exists_exits(self, job_instance):
        with patch('yojenkins.yo_jenkins.job.utility.item_exists_in_folder', return_value=True):
            with pytest.raises(YoJenkinsException):
                job_instance.create(
                    name='existing-job',
                    folder_url='http://localhost:8080/job/folder/',
                )

    def test_create_json_config(self, job_instance, tmp_path):
        config_file = tmp_path / 'config.json'
        config_file.write_bytes(b'{"project": {}}')
        job_instance.rest.request.return_value = ({}, {}, True)
        with patch('yojenkins.yo_jenkins.job.utility.item_exists_in_folder', return_value=False):
            with patch('yojenkins.yo_jenkins.job.xmltodict.unparse', return_value='<project/>'):
                result = job_instance.create(
                    name='new-job',
                    folder_url='http://localhost:8080/job/folder/',
                    config_file=str(config_file),
                    config_is_json=True,
                )
        assert result is True

    def test_create_auto_detects_json_config(self, job_instance, tmp_path):
        """create() auto-detects JSON format without --config-is-json flag."""
        config_file = tmp_path / 'config.json'
        config_file.write_bytes(b'{"project": {}}')
        job_instance.rest.request.return_value = ({}, {}, True)
        with patch('yojenkins.yo_jenkins.job.utility.item_exists_in_folder', return_value=False):
            with patch('yojenkins.yo_jenkins.job.xmltodict.unparse', return_value='<project/>') as mock_unparse:
                result = job_instance.create(
                    name='new-job',
                    folder_url='http://localhost:8080/job/folder/',
                    config_file=str(config_file),
                    config_is_json=False,
                )
        assert result is True
        mock_unparse.assert_called_once()

    def test_create_xml_config_not_converted(self, job_instance, tmp_path):
        """create() does not convert XML config files."""
        config_file = tmp_path / 'config.xml'
        config_file.write_bytes(b'<project/>')
        job_instance.rest.request.return_value = ({}, {}, True)
        with patch('yojenkins.yo_jenkins.job.utility.item_exists_in_folder', return_value=False):
            with patch('yojenkins.yo_jenkins.job.xmltodict.unparse') as mock_unparse:
                result = job_instance.create(
                    name='new-job',
                    folder_url='http://localhost:8080/job/folder/',
                    config_file=str(config_file),
                    config_is_json=False,
                )
        assert result is True
        mock_unparse.assert_not_called()

    def test_create_config_file_read_error_exits(self, job_instance):
        with patch('yojenkins.yo_jenkins.job.utility.item_exists_in_folder', return_value=False):
            with pytest.raises(YoJenkinsException):
                job_instance.create(
                    name='new-job',
                    folder_url='http://localhost:8080/job/folder/',
                    config_file='/nonexistent/config.xml',
                )


# ---------------------------------------------------------------------------
# build_list_number() edge case
# ---------------------------------------------------------------------------


class TestJobBuildListNumberEdge:
    def test_last_build_none_returns_zero(self, job_instance):
        """build_last_number returns 0 when lastBuild is falsy."""
        job_info = {
            '_class': JOB_CLASS,
            'fullName': 'my-job',
            'lastBuild': None,
        }
        result = job_instance.build_last_number(job_url='http://localhost:8080/job/my-job/', job_info=job_info)
        assert result == 0

    def test_build_number_exist_true(self, job_instance):
        job_info = {
            '_class': JOB_CLASS,
            'builds': [{'number': 1}, {'number': 2}, {'number': 3}],
        }
        result = job_instance.build_number_exist(
            build_number=2, job_url='http://localhost:8080/job/my-job/', job_info=job_info
        )
        assert result is True

    def test_build_number_exist_false(self, job_instance):
        job_info = {
            '_class': JOB_CLASS,
            'builds': [{'number': 1}, {'number': 2}],
        }
        result = job_instance.build_number_exist(
            build_number=99, job_url='http://localhost:8080/job/my-job/', job_info=job_info
        )
        assert result is False


# ---------------------------------------------------------------------------
# queue_abort()
# ---------------------------------------------------------------------------


class TestJobQueueCancel:
    def test_queue_abort_success(self, job_instance):
        job_instance.rest.request.return_value = ('cancelled', {}, True)
        result = job_instance.queue_abort(build_queue_number=1)
        assert result is True

    def test_queue_abort_no_number_exits(self, job_instance):
        with pytest.raises(YoJenkinsException):
            job_instance.queue_abort(build_queue_number=0)

    def test_queue_abort_failure_exits(self, job_instance):
        job_instance.rest.request.return_value = ('', {}, True)
        job_instance.in_queue_check = MagicMock(
            return_value=[{'id': 1, 'task': {'url': 'http://localhost:8080/job/x/'}}]
        )
        with pytest.raises(YoJenkinsException):
            job_instance.queue_abort(build_queue_number=999)


# ---------------------------------------------------------------------------
# browser_open()
# ---------------------------------------------------------------------------


class TestJobBrowserOpen:
    def test_browser_open_by_url(self, job_instance):
        with patch('yojenkins.yo_jenkins.job.utility.browser_open', return_value=True):
            result = job_instance.browser_open(job_url='http://localhost:8080/job/my-job/')
        assert result is True

    def test_browser_open_failure_exits(self, job_instance):
        with patch('yojenkins.yo_jenkins.job.utility.browser_open', return_value=False):
            with pytest.raises(YoJenkinsException):
                job_instance.browser_open(job_url='http://localhost:8080/job/my-job/')
