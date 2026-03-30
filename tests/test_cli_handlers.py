"""Tests for all CLI handler functions across cli_*.py modules.

Each test mocks config_yo_jenkins (or Auth where used directly) to return
a mock YoJenkins object, calls the handler, and verifies the correct
business logic method was invoked.
"""

import json
from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

import pytest

from yojenkins.cli import (
    cli_account,
    cli_auth,
    cli_build,
    cli_credential,
    cli_folder,
    cli_job,
    cli_node,
    cli_server,
    cli_stage,
    cli_step,
    cli_tools,
)

# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

COMMON_KWARGS = {
    'opt_pretty': False,
    'opt_yaml': False,
    'opt_xml': False,
    'opt_toml': False,
}

PROFILE_TOKEN = {'profile': 'default', 'token': None}


def _mock_yj():
    """Create a fully-mocked YoJenkins object with sub-objects."""
    yj = MagicMock()
    yj.folder = MagicMock()
    yj.job = MagicMock()
    yj.build = MagicMock()
    yj.server = MagicMock()
    yj.credential = MagicMock()
    yj.node = MagicMock()
    yj.account = MagicMock()
    yj.stage = MagicMock()
    yj.step = MagicMock()
    yj.auth = MagicMock()
    yj.rest = MagicMock()
    return yj


@pytest.fixture(autouse=True)
def _patch_history_file_io():
    """Prevent log_to_history from touching the filesystem in all tests."""
    with patch('pathlib.Path.is_file', return_value=True), patch('builtins.open', MagicMock()):
        yield


# ============================================================================
# cli_folder tests
# ============================================================================


class TestCliFolderHandlers:
    @patch('yojenkins.cli.cli_folder.cu.standard_out')
    @patch('yojenkins.cli.cli_folder.cu.config_yo_jenkins')
    @patch('yojenkins.cli.cli_folder.cu.is_full_url', return_value=False)
    def test_folder_info_by_name(self, mock_is_url, mock_config, mock_stdout):
        mock_yj = _mock_yj()
        mock_config.return_value = mock_yj
        mock_yj.folder.info.return_value = {'name': 'test-folder'}

        cli_folder.info(folder='test-folder', **PROFILE_TOKEN, **COMMON_KWARGS)
        mock_yj.folder.info.assert_called_once_with(folder_name='test-folder')
        mock_stdout.assert_called_once()

    @patch('yojenkins.cli.cli_folder.cu.standard_out')
    @patch('yojenkins.cli.cli_folder.cu.config_yo_jenkins')
    @patch('yojenkins.cli.cli_folder.cu.is_full_url', return_value=True)
    def test_folder_info_by_url(self, mock_is_url, mock_config, mock_stdout):
        mock_yj = _mock_yj()
        mock_config.return_value = mock_yj
        url = 'http://localhost:8080/job/test-folder'
        mock_yj.folder.info.return_value = {'name': 'test-folder'}

        cli_folder.info(folder=url, **PROFILE_TOKEN, **COMMON_KWARGS)
        mock_yj.folder.info.assert_called_once_with(folder_url=url)

    @patch('yojenkins.cli.cli_folder.cu.standard_out')
    @patch('yojenkins.cli.cli_folder.cu.config_yo_jenkins')
    @patch('yojenkins.cli.cli_folder.cu.is_full_url', return_value=False)
    def test_folder_subfolders(self, mock_is_url, mock_config, mock_stdout):
        mock_yj = _mock_yj()
        mock_config.return_value = mock_yj
        mock_yj.folder.subfolder_list.return_value = ([{'name': 'sub'}], ['sub'])

        cli_folder.subfolders(folder='root', opt_list=False, **PROFILE_TOKEN, **COMMON_KWARGS)
        mock_yj.folder.subfolder_list.assert_called_once_with(folder_name='root')

    @patch('yojenkins.cli.cli_folder.cu.standard_out')
    @patch('yojenkins.cli.cli_folder.cu.config_yo_jenkins')
    @patch('yojenkins.cli.cli_folder.cu.is_full_url', return_value=False)
    def test_folder_subfolders_opt_list(self, mock_is_url, mock_config, mock_stdout):
        mock_yj = _mock_yj()
        mock_config.return_value = mock_yj
        mock_yj.folder.subfolder_list.return_value = ([{'name': 'sub'}], ['sub'])

        cli_folder.subfolders(folder='root', opt_list=True, **PROFILE_TOKEN, **COMMON_KWARGS)
        call_args = mock_stdout.call_args[0]
        assert call_args[0] == ['sub']

    @patch('yojenkins.cli.cli_folder.cu.standard_out')
    @patch('yojenkins.cli.cli_folder.cu.config_yo_jenkins')
    @patch('yojenkins.cli.cli_folder.cu.is_full_url', return_value=False)
    def test_folder_jobs(self, mock_is_url, mock_config, mock_stdout):
        mock_yj = _mock_yj()
        mock_config.return_value = mock_yj
        mock_yj.folder.jobs_list.return_value = ([{'name': 'job1'}], ['job1'])

        cli_folder.jobs(folder='root', opt_list=False, **PROFILE_TOKEN, **COMMON_KWARGS)
        mock_yj.folder.jobs_list.assert_called_once_with(folder_name='root')

    @patch('yojenkins.cli.cli_folder.cu.standard_out')
    @patch('yojenkins.cli.cli_folder.cu.config_yo_jenkins')
    @patch('yojenkins.cli.cli_folder.cu.is_full_url', return_value=False)
    def test_folder_views(self, mock_is_url, mock_config, mock_stdout):
        mock_yj = _mock_yj()
        mock_config.return_value = mock_yj
        mock_yj.folder.view_list.return_value = ([{'name': 'v1'}], ['v1'])

        cli_folder.views(folder='root', opt_list=False, **PROFILE_TOKEN, **COMMON_KWARGS)
        mock_yj.folder.view_list.assert_called_once_with(folder_name='root')

    @patch('yojenkins.cli.cli_folder.cu.standard_out')
    @patch('yojenkins.cli.cli_folder.cu.config_yo_jenkins')
    @patch('yojenkins.cli.cli_folder.cu.is_full_url', return_value=False)
    def test_folder_items(self, mock_is_url, mock_config, mock_stdout):
        mock_yj = _mock_yj()
        mock_config.return_value = mock_yj
        mock_yj.folder.item_list.return_value = ([{'name': 'item'}], ['item'])

        cli_folder.items(folder='root', opt_list=False, **PROFILE_TOKEN, **COMMON_KWARGS)
        mock_yj.folder.item_list.assert_called_once_with(folder_name='root')

    @patch('yojenkins.cli.cli_folder.cu.config_yo_jenkins')
    @patch('yojenkins.cli.cli_folder.cu.is_full_url', return_value=False)
    def test_folder_browser(self, mock_is_url, mock_config):
        mock_yj = _mock_yj()
        mock_config.return_value = mock_yj

        cli_folder.browser(folder='root', **PROFILE_TOKEN)
        mock_yj.folder.browser_open.assert_called_once_with(folder_name='root')

    @patch('yojenkins.cli.cli_folder.browser_open')
    @patch('yojenkins.cli.cli_folder.cu.config_yo_jenkins')
    @patch('yojenkins.cli.cli_folder.cu.is_full_url', return_value=True)
    def test_folder_browser_url_skips_auth(self, mock_is_url, mock_config, mock_browser):
        cli_folder.browser(folder='http://jenkins/job/my-folder', **PROFILE_TOKEN)
        mock_browser.assert_called_once_with('http://jenkins/job/my-folder')
        mock_config.assert_not_called()

    @patch('click.secho')
    @patch('yojenkins.cli.cli_folder.cu.config_yo_jenkins')
    @patch('yojenkins.cli.cli_folder.cu.is_full_url', return_value=False)
    def test_folder_delete(self, mock_is_url, mock_config, mock_secho):
        mock_yj = _mock_yj()
        mock_config.return_value = mock_yj

        cli_folder.delete(folder='old-folder', **PROFILE_TOKEN)
        mock_yj.folder.delete.assert_called_once_with(folder_name='old-folder')

    @patch('click.secho')
    @patch('yojenkins.cli.cli_folder.cu.config_yo_jenkins')
    @patch('yojenkins.cli.cli_folder.cu.is_full_url', return_value=False)
    def test_folder_create(self, mock_is_url, mock_config, mock_secho):
        mock_yj = _mock_yj()
        mock_config.return_value = mock_yj

        cli_folder.create(
            name='new-folder', folder='parent', type='folder', config_file=None, config_is_json=False, **PROFILE_TOKEN
        )
        mock_yj.folder.create.assert_called_once()

    @patch('click.secho')
    @patch('yojenkins.cli.cli_folder.cu.config_yo_jenkins')
    @patch('yojenkins.cli.cli_folder.cu.is_full_url', return_value=False)
    def test_folder_copy(self, mock_is_url, mock_config, mock_secho):
        mock_yj = _mock_yj()
        mock_config.return_value = mock_yj

        cli_folder.copy(folder='parent', original='orig', new='new-copy', **PROFILE_TOKEN)
        mock_yj.folder.copy.assert_called_once_with(original_name='orig', new_name='new-copy', folder_name='parent')


# ============================================================================
# cli_job tests
# ============================================================================


class TestCliJobHandlers:
    @patch('yojenkins.cli.cli_job.cu.standard_out')
    @patch('yojenkins.cli.cli_job.cu.config_yo_jenkins')
    @patch('yojenkins.cli.cli_job.cu.is_full_url', return_value=False)
    def test_job_info_by_name(self, mock_is_url, mock_config, mock_stdout):
        mock_yj = _mock_yj()
        mock_config.return_value = mock_yj
        mock_yj.job.info.return_value = {'name': 'my-job'}

        cli_job.info(job='my-job', **PROFILE_TOKEN, **COMMON_KWARGS)
        mock_yj.job.info.assert_called_once_with(job_name='my-job')

    @patch('click.secho')
    @patch('yojenkins.cli.cli_job.cu.config_yo_jenkins')
    @patch('yojenkins.cli.cli_job.cu.is_full_url', return_value=False)
    def test_job_build_next(self, mock_is_url, mock_config, mock_secho):
        mock_yj = _mock_yj()
        mock_config.return_value = mock_yj
        mock_yj.job.build_next_number.return_value = 42

        cli_job.build_next(job='my-job', **PROFILE_TOKEN)
        mock_yj.job.build_next_number.assert_called_once_with(job_name='my-job')

    @patch('click.secho')
    @patch('yojenkins.cli.cli_job.cu.config_yo_jenkins')
    @patch('yojenkins.cli.cli_job.cu.is_full_url', return_value=False)
    def test_job_build_last(self, mock_is_url, mock_config, mock_secho):
        mock_yj = _mock_yj()
        mock_config.return_value = mock_yj
        mock_yj.job.build_last_number.return_value = 41

        cli_job.build_last(job='my-job', **PROFILE_TOKEN)
        mock_yj.job.build_last_number.assert_called_once_with(job_name='my-job')

    @patch('click.secho')
    @patch('yojenkins.cli.cli_job.cu.config_yo_jenkins')
    @patch('yojenkins.cli.cli_job.cu.is_full_url', return_value=False)
    def test_job_disable(self, mock_is_url, mock_config, mock_secho):
        mock_yj = _mock_yj()
        mock_config.return_value = mock_yj

        cli_job.disable(job='my-job', **PROFILE_TOKEN)
        mock_yj.job.disable.assert_called_once_with(job_name='my-job')

    @patch('click.secho')
    @patch('yojenkins.cli.cli_job.cu.config_yo_jenkins')
    @patch('yojenkins.cli.cli_job.cu.is_full_url', return_value=False)
    def test_job_enable(self, mock_is_url, mock_config, mock_secho):
        mock_yj = _mock_yj()
        mock_config.return_value = mock_yj

        cli_job.enable(job='my-job', **PROFILE_TOKEN)
        mock_yj.job.enable.assert_called_once_with(job_name='my-job')

    @patch('click.secho')
    @patch('yojenkins.cli.cli_job.cu.config_yo_jenkins')
    @patch('yojenkins.cli.cli_job.cu.is_full_url', return_value=False)
    def test_job_rename(self, mock_is_url, mock_config, mock_secho):
        mock_yj = _mock_yj()
        mock_config.return_value = mock_yj

        cli_job.rename(job='my-job', name='new-name', **PROFILE_TOKEN)
        mock_yj.job.rename.assert_called_once_with(new_name='new-name', job_name='my-job')

    @patch('click.secho')
    @patch('yojenkins.cli.cli_job.cu.config_yo_jenkins')
    @patch('yojenkins.cli.cli_job.cu.is_full_url', return_value=False)
    def test_job_delete(self, mock_is_url, mock_config, mock_secho):
        mock_yj = _mock_yj()
        mock_config.return_value = mock_yj

        cli_job.delete(job='my-job', **PROFILE_TOKEN)
        mock_yj.job.delete.assert_called_once_with(job_name='my-job')

    @patch('click.secho')
    @patch('yojenkins.cli.cli_job.cu.config_yo_jenkins')
    @patch('yojenkins.cli.cli_job.cu.is_full_url', return_value=False)
    def test_job_wipe(self, mock_is_url, mock_config, mock_secho):
        mock_yj = _mock_yj()
        mock_config.return_value = mock_yj

        cli_job.wipe(job='my-job', **PROFILE_TOKEN)
        mock_yj.job.wipe_workspace.assert_called_once_with(job_name='my-job')

    @patch('click.secho')
    @patch('yojenkins.cli.cli_job.cu.config_yo_jenkins')
    @patch('yojenkins.cli.cli_job.cu.is_full_url', return_value=False)
    def test_job_build_trigger_no_follow(self, mock_is_url, mock_config, mock_secho):
        mock_yj = _mock_yj()
        mock_config.return_value = mock_yj
        mock_yj.job.build_trigger.return_value = 123

        cli_job.build(job='my-job', parameter=(), follow_logs=False, **PROFILE_TOKEN)
        mock_yj.job.build_trigger.assert_called_once_with(job_name='my-job', paramters={})

    @patch('yojenkins.cli.cli_job.cu.standard_out')
    @patch('yojenkins.cli.cli_job.cu.config_yo_jenkins')
    @patch('yojenkins.cli.cli_job.cu.is_full_url', return_value=False)
    def test_job_build_list(self, mock_is_url, mock_config, mock_stdout):
        mock_yj = _mock_yj()
        mock_config.return_value = mock_yj
        mock_yj.job.build_list.return_value = ([{'number': 1}], [1])

        cli_job.build_list(job='my-job', opt_list=False, **PROFILE_TOKEN, **COMMON_KWARGS)
        mock_yj.job.build_list.assert_called_once_with(job_name='my-job')

    @patch('yojenkins.cli.cli_job.cu.standard_out')
    @patch('yojenkins.cli.cli_job.cu.config_yo_jenkins')
    @patch('yojenkins.cli.cli_job.cu.is_full_url', return_value=False)
    def test_job_parameters(self, mock_is_url, mock_config, mock_stdout):
        mock_yj = _mock_yj()
        mock_config.return_value = mock_yj
        mock_yj.job.parameters.return_value = ([{'name': 'p1'}], ['p1'])

        cli_job.parameters(job='my-job', opt_list=False, **PROFILE_TOKEN, **COMMON_KWARGS)
        mock_yj.job.parameters.assert_called_once_with(job_name='my-job')

    @patch('yojenkins.cli.cli_job.cu.config_yo_jenkins')
    def test_job_diff(self, mock_config):
        mock_yj = _mock_yj()
        mock_config.return_value = mock_yj

        cli_job.diff(job_1='job-a', job_2='job-b', no_color=False, diff_only=False, diff_guide=False, **PROFILE_TOKEN)
        mock_yj.job.diff.assert_called_once_with('job-a', 'job-b', False, False, False)

    @patch('click.secho')
    @patch('yojenkins.cli.cli_job.cu.config_yo_jenkins')
    @patch('yojenkins.cli.cli_job.cu.is_full_url', return_value=False)
    def test_job_build_set(self, mock_is_url, mock_config, mock_secho):
        mock_yj = _mock_yj()
        mock_config.return_value = mock_yj

        cli_job.build_set(job='my-job', build_number=99, **PROFILE_TOKEN)
        mock_yj.job.build_set_next_number.assert_called_once_with(build_number=99, job_name='my-job')

    @patch('click.secho')
    @patch('yojenkins.cli.cli_job.cu.config_yo_jenkins')
    @patch('yojenkins.cli.cli_job.cu.is_full_url', return_value=False)
    def test_job_build_exist_true(self, mock_is_url, mock_config, mock_secho):
        mock_yj = _mock_yj()
        mock_config.return_value = mock_yj
        mock_yj.job.build_number_exist.return_value = True

        cli_job.build_exist(job='my-job', build_number=5, **PROFILE_TOKEN)
        mock_yj.job.build_number_exist.assert_called_once()
        mock_secho.assert_called_with('true', fg='bright_green', bold=True)

    @patch('click.secho')
    @patch('yojenkins.cli.cli_job.cu.config_yo_jenkins')
    @patch('yojenkins.cli.cli_job.cu.is_full_url', return_value=False)
    def test_job_build_exist_false(self, mock_is_url, mock_config, mock_secho):
        mock_yj = _mock_yj()
        mock_config.return_value = mock_yj
        mock_yj.job.build_number_exist.return_value = False

        cli_job.build_exist(job='my-job', build_number=999, **PROFILE_TOKEN)
        mock_secho.assert_called_with('false', fg='bright_red', bold=True)


# ============================================================================
# cli_build tests
# ============================================================================


class TestCliBuildHandlers:
    @patch('yojenkins.cli.cli_build.cu.standard_out')
    @patch('yojenkins.cli.cli_build.cu.config_yo_jenkins')
    @patch('yojenkins.cli.cli_build.cu.is_full_url', return_value=False)
    @patch('yojenkins.cli.cli_build.is_complete_build_url', return_value=False)
    def test_build_info_by_job_name_latest(self, mock_is_build_url, mock_is_url, mock_config, mock_stdout):
        mock_yj = _mock_yj()
        mock_config.return_value = mock_yj
        mock_yj.build.info.return_value = {'number': 1}

        cli_build.info(job='my-job', number=None, url=None, latest=True, **PROFILE_TOKEN, **COMMON_KWARGS)
        mock_yj.build.info.assert_called_once()

    @patch('click.secho')
    @patch('yojenkins.cli.cli_build.cu.config_yo_jenkins')
    @patch('yojenkins.cli.cli_build.cu.is_full_url', return_value=False)
    @patch('yojenkins.cli.cli_build.is_complete_build_url', return_value=False)
    def test_build_abort(self, mock_is_build_url, mock_is_url, mock_config, mock_secho):
        mock_yj = _mock_yj()
        mock_config.return_value = mock_yj

        cli_build.abort(job='my-job', number=5, url=None, latest=False, **PROFILE_TOKEN)
        mock_yj.build.abort.assert_called_once()

    @patch('click.secho')
    @patch('yojenkins.cli.cli_build.cu.config_yo_jenkins')
    @patch('yojenkins.cli.cli_build.cu.is_full_url', return_value=False)
    @patch('yojenkins.cli.cli_build.is_complete_build_url', return_value=False)
    def test_build_delete(self, mock_is_build_url, mock_is_url, mock_config, mock_secho):
        mock_yj = _mock_yj()
        mock_config.return_value = mock_yj

        cli_build.delete(job='my-job', number=5, url=None, latest=False, **PROFILE_TOKEN)
        mock_yj.build.delete.assert_called_once()

    @patch('yojenkins.cli.cli_build.cu.standard_out')
    @patch('yojenkins.cli.cli_build.cu.config_yo_jenkins')
    @patch('yojenkins.cli.cli_build.cu.is_full_url', return_value=False)
    @patch('yojenkins.cli.cli_build.is_complete_build_url', return_value=False)
    def test_build_stages(self, mock_is_build_url, mock_is_url, mock_config, mock_stdout):
        mock_yj = _mock_yj()
        mock_config.return_value = mock_yj
        mock_yj.build.stage_list.return_value = ([{'name': 's1'}], ['s1'])

        cli_build.stages(
            job='my-job', number=1, url=None, latest=False, opt_list=False, **PROFILE_TOKEN, **COMMON_KWARGS
        )
        mock_yj.build.stage_list.assert_called_once()

    @patch('yojenkins.cli.cli_build.cu.config_yo_jenkins')
    @patch('yojenkins.cli.cli_build.cu.is_full_url', return_value=False)
    @patch('yojenkins.cli.cli_build.is_complete_build_url', return_value=False)
    def test_build_logs(self, mock_is_build_url, mock_is_url, mock_config):
        mock_yj = _mock_yj()
        mock_config.return_value = mock_yj

        cli_build.logs(
            job='my-job', number=1, url=None, latest=False, tail=0, download_dir=None, follow=False, **PROFILE_TOKEN
        )
        mock_yj.build.logs.assert_called_once()

    @patch('yojenkins.cli.cli_build.cu.standard_out')
    @patch('yojenkins.cli.cli_build.cu.config_yo_jenkins')
    @patch('yojenkins.cli.cli_build.cu.is_full_url', return_value=False)
    @patch('yojenkins.cli.cli_build.is_complete_build_url', return_value=False)
    def test_build_parameters(self, mock_is_build_url, mock_is_url, mock_config, mock_stdout):
        mock_yj = _mock_yj()
        mock_config.return_value = mock_yj
        mock_yj.build.parameters.return_value = ([{'name': 'p1'}], ['p1'])

        cli_build.parameters(
            job='my-job', number=1, url=None, latest=False, opt_list=False, **PROFILE_TOKEN, **COMMON_KWARGS
        )
        mock_yj.build.parameters.assert_called_once()

    @patch('yojenkins.cli.cli_build.is_complete_build_url', return_value=False)
    def test_build_info_missing_number_and_latest_exits(self, mock_is_build_url):
        """Should sys.exit(1) when job is given but no --number or --latest."""
        with pytest.raises(SystemExit) as exc_info:
            cli_build.info(job='my-job', number=None, url=None, latest=False, **PROFILE_TOKEN, **COMMON_KWARGS)
        assert exc_info.value.code == 1

    @patch('yojenkins.cli.cli_build.cu.config_yo_jenkins')
    def test_build_diff(self, mock_config):
        mock_yj = _mock_yj()
        mock_config.return_value = mock_yj

        cli_build.diff(
            build_url_1='http://j:8080/job/a/1/',
            build_url_2='http://j:8080/job/a/2/',
            logs=False,
            line_pattern=(),
            char_ignore=0,
            no_color=False,
            diff_only=False,
            diff_guide=False,
            **PROFILE_TOKEN,
        )
        mock_yj.build.diff.assert_called_once()

    @patch('click.secho')
    @patch('yojenkins.cli.cli_build.cu.config_yo_jenkins')
    @patch('yojenkins.cli.cli_build.cu.is_full_url', return_value=False)
    @patch('yojenkins.cli.cli_build.is_complete_build_url', return_value=False)
    def test_build_rebuild_no_follow(self, mock_is_build_url, mock_is_url, mock_config, mock_secho):
        mock_yj = _mock_yj()
        mock_config.return_value = mock_yj
        mock_yj.build.rebuild.return_value = 456

        cli_build.rebuild(job='my-job', number=1, url=None, latest=False, follow_logs=False, **PROFILE_TOKEN)
        mock_yj.build.rebuild.assert_called_once()
        mock_secho.assert_called_with('success. queue number: 456', fg='bright_green', bold=True)


# ============================================================================
# cli_server tests
# ============================================================================


class TestCliServerHandlers:
    @patch('yojenkins.cli.cli_server.cu.standard_out')
    @patch('yojenkins.cli.cli_server.cu.config_yo_jenkins')
    def test_server_info(self, mock_config, mock_stdout):
        mock_yj = _mock_yj()
        mock_config.return_value = mock_yj
        mock_yj.server.info.return_value = {'version': '2.300'}

        cli_server.info(**PROFILE_TOKEN, **COMMON_KWARGS)
        mock_yj.server.info.assert_called_once()

    @patch('yojenkins.cli.cli_server.cu.standard_out')
    @patch('yojenkins.cli.cli_server.cu.config_yo_jenkins')
    def test_server_people(self, mock_config, mock_stdout):
        mock_yj = _mock_yj()
        mock_config.return_value = mock_yj
        mock_yj.server.people.return_value = ([{'name': 'admin'}], ['admin'])

        cli_server.people(opt_list=False, **PROFILE_TOKEN, **COMMON_KWARGS)
        mock_yj.server.people.assert_called_once()

    @patch('yojenkins.cli.cli_server.cu.standard_out')
    @patch('yojenkins.cli.cli_server.cu.config_yo_jenkins')
    def test_server_queue(self, mock_config, mock_stdout):
        mock_yj = _mock_yj()
        mock_config.return_value = mock_yj
        mock_yj.server.queue_info.return_value = {'items': []}

        cli_server.queue(opt_list=False, **PROFILE_TOKEN, **COMMON_KWARGS)
        mock_yj.server.queue_info.assert_called_once()

    @patch('yojenkins.cli.cli_server.cu.standard_out')
    @patch('yojenkins.cli.cli_server.cu.config_yo_jenkins')
    def test_server_queue_opt_list(self, mock_config, mock_stdout):
        mock_yj = _mock_yj()
        mock_config.return_value = mock_yj
        mock_yj.server.queue_list.return_value = ['item1']

        cli_server.queue(opt_list=True, **PROFILE_TOKEN, **COMMON_KWARGS)
        mock_yj.server.queue_list.assert_called_once()

    @patch('yojenkins.cli.cli_server.cu.standard_out')
    @patch('yojenkins.cli.cli_server.cu.config_yo_jenkins')
    def test_server_plugins(self, mock_config, mock_stdout):
        mock_yj = _mock_yj()
        mock_config.return_value = mock_yj
        mock_yj.server.plugin_list.return_value = ([{'name': 'git'}], ['git'])

        cli_server.plugins(opt_list=False, **PROFILE_TOKEN, **COMMON_KWARGS)
        mock_yj.server.plugin_list.assert_called_once()

    @patch('yojenkins.cli.cli_server.cu.config_yo_jenkins')
    def test_server_browser(self, mock_config):
        mock_yj = _mock_yj()
        mock_config.return_value = mock_yj

        cli_server.browser(**PROFILE_TOKEN)
        mock_yj.server.browser_open.assert_called_once()

    @patch('click.secho')
    @patch('yojenkins.cli.cli_server.cu.config_yo_jenkins')
    def test_server_quiet(self, mock_config, mock_secho):
        mock_yj = _mock_yj()
        mock_config.return_value = mock_yj

        cli_server.quiet(off=False, **PROFILE_TOKEN)
        mock_yj.server.quiet.assert_called_once_with(off=False)

    @patch('click.secho')
    @patch('yojenkins.cli.cli_server.cu.config_yo_jenkins')
    def test_server_restart(self, mock_config, mock_secho):
        mock_yj = _mock_yj()
        mock_config.return_value = mock_yj

        cli_server.restart(force=False, **PROFILE_TOKEN)
        mock_yj.server.restart.assert_called_once_with(force=False)

    @patch('click.secho')
    @patch('yojenkins.cli.cli_server.cu.config_yo_jenkins')
    def test_server_shutdown(self, mock_config, mock_secho):
        mock_yj = _mock_yj()
        mock_config.return_value = mock_yj

        cli_server.shutdown(force=True, **PROFILE_TOKEN)
        mock_yj.server.shutdown.assert_called_once_with(force=True)


# ============================================================================
# cli_credential tests
# ============================================================================


class TestCliCredentialHandlers:
    @patch('yojenkins.cli.cli_credential.cu.standard_out')
    @patch('yojenkins.cli.cli_credential.cu.config_yo_jenkins')
    def test_credential_list(self, mock_config, mock_stdout):
        mock_yj = _mock_yj()
        mock_config.return_value = mock_yj
        mock_yj.credential.list.return_value = ([{'id': 'c1'}], ['c1'])

        cli_credential.list(opt_list=False, folder='/', domain='_', keys='', **PROFILE_TOKEN, **COMMON_KWARGS)
        mock_yj.credential.list.assert_called_once()

    @patch('yojenkins.cli.cli_credential.cu.standard_out')
    @patch('yojenkins.cli.cli_credential.cu.config_yo_jenkins')
    def test_credential_info(self, mock_config, mock_stdout):
        mock_yj = _mock_yj()
        mock_config.return_value = mock_yj
        mock_yj.credential.info.return_value = {'id': 'cred-1'}

        cli_credential.info(credential='cred-1', folder='/', domain='_', **PROFILE_TOKEN, **COMMON_KWARGS)
        mock_yj.credential.info.assert_called_once_with(credential='cred-1', folder='/', domain='_')

    @patch('click.secho')
    @patch('yojenkins.cli.cli_credential.cu.config_yo_jenkins')
    def test_credential_create(self, mock_config, mock_secho):
        mock_yj = _mock_yj()
        mock_config.return_value = mock_yj

        cli_credential.create(config_file='cred.xml', folder='/', domain='_', **PROFILE_TOKEN)
        mock_yj.credential.create.assert_called_once_with(config_file='cred.xml', folder='/', domain='_')

    @patch('click.secho')
    @patch('yojenkins.cli.cli_credential.cu.config_yo_jenkins')
    def test_credential_delete(self, mock_config, mock_secho):
        mock_yj = _mock_yj()
        mock_config.return_value = mock_yj

        cli_credential.delete(credential='cred-1', folder='/', domain='_', **PROFILE_TOKEN)
        mock_yj.credential.delete.assert_called_once_with(credential='cred-1', folder='/', domain='_')


# ============================================================================
# cli_node tests
# ============================================================================


class TestCliNodeHandlers:
    @patch('yojenkins.cli.cli_node.cu.standard_out')
    @patch('yojenkins.cli.cli_node.cu.config_yo_jenkins')
    def test_node_info(self, mock_config, mock_stdout):
        mock_yj = _mock_yj()
        mock_config.return_value = mock_yj
        mock_yj.node.info.return_value = {'displayName': 'built-in'}

        cli_node.info(name='built-in', depth=0, **PROFILE_TOKEN, **COMMON_KWARGS)
        mock_yj.node.info.assert_called_once_with('built-in', 0)

    @patch('yojenkins.cli.cli_node.cu.standard_out')
    @patch('yojenkins.cli.cli_node.cu.config_yo_jenkins')
    def test_node_list(self, mock_config, mock_stdout):
        mock_yj = _mock_yj()
        mock_config.return_value = mock_yj
        mock_yj.node.list.return_value = ([{'name': 'n1'}], ['n1'])

        cli_node.list(opt_list=False, depth=0, **PROFILE_TOKEN, **COMMON_KWARGS)
        mock_yj.node.list.assert_called_once_with(0)

    @patch('click.secho')
    @patch('yojenkins.cli.cli_node.cu.config_yo_jenkins')
    def test_node_delete(self, mock_config, mock_secho):
        mock_yj = _mock_yj()
        mock_config.return_value = mock_yj

        cli_node.delete(name='agent-1', **PROFILE_TOKEN)
        mock_yj.node.delete.assert_called_once_with('agent-1')

    @patch('click.secho')
    @patch('yojenkins.cli.cli_node.cu.config_yo_jenkins')
    def test_node_disable(self, mock_config, mock_secho):
        mock_yj = _mock_yj()
        mock_config.return_value = mock_yj

        cli_node.disable(name='agent-1', message='maintenance', **PROFILE_TOKEN)
        mock_yj.node.disable.assert_called_once_with('agent-1', 'maintenance')

    @patch('click.secho')
    @patch('yojenkins.cli.cli_node.cu.config_yo_jenkins')
    def test_node_enable(self, mock_config, mock_secho):
        mock_yj = _mock_yj()
        mock_config.return_value = mock_yj

        cli_node.enable(name='agent-1', message='back online', **PROFILE_TOKEN)
        mock_yj.node.enable.assert_called_once_with('agent-1', 'back online')

    @patch('click.secho')
    @patch('yojenkins.cli.cli_node.cu.config_yo_jenkins')
    def test_node_reconfig(self, mock_config, mock_secho):
        mock_yj = _mock_yj()
        mock_config.return_value = mock_yj

        cli_node.reconfig(name='agent-1', config_file='node.xml', config_is_json=False, **PROFILE_TOKEN)
        mock_yj.node.reconfig.assert_called_once_with(
            config_file='node.xml', node_name='agent-1', config_is_json=False
        )


# ============================================================================
# cli_account tests
# ============================================================================


class TestCliAccountHandlers:
    @patch('yojenkins.cli.cli_account.cu.standard_out')
    @patch('yojenkins.cli.cli_account.cu.config_yo_jenkins')
    def test_account_list(self, mock_config, mock_stdout):
        mock_yj = _mock_yj()
        mock_config.return_value = mock_yj
        mock_yj.account.list.return_value = ([{'id': 'admin'}], ['admin'])

        cli_account.list(opt_list=False, **PROFILE_TOKEN, **COMMON_KWARGS)
        mock_yj.account.list.assert_called_once()

    @patch('yojenkins.cli.cli_account.cu.standard_out')
    @patch('yojenkins.cli.cli_account.cu.config_yo_jenkins')
    def test_account_info(self, mock_config, mock_stdout):
        mock_yj = _mock_yj()
        mock_config.return_value = mock_yj
        mock_yj.account.info.return_value = {'id': 'admin'}

        cli_account.info(user_id='admin', **PROFILE_TOKEN, **COMMON_KWARGS)
        mock_yj.account.info.assert_called_once_with(user_id='admin')

    @patch('click.secho')
    @patch('yojenkins.cli.cli_account.cu.config_yo_jenkins')
    def test_account_create(self, mock_config, mock_secho):
        mock_yj = _mock_yj()
        mock_config.return_value = mock_yj

        cli_account.create(
            user_id='newuser',
            password='pass123',
            is_admin=False,
            email='test@example.com',
            description='test user',
            **PROFILE_TOKEN,
        )
        mock_yj.account.create.assert_called_once_with(
            user_id='newuser', password='pass123', is_admin=False, email='test@example.com', description='test user'
        )

    @patch('click.secho')
    @patch('yojenkins.cli.cli_account.cu.config_yo_jenkins')
    def test_account_delete(self, mock_config, mock_secho):
        mock_yj = _mock_yj()
        mock_config.return_value = mock_yj

        cli_account.delete(user_id='olduser', **PROFILE_TOKEN)
        mock_yj.account.delete.assert_called_once_with(user_id='olduser')

    @patch('click.secho')
    @patch('yojenkins.cli.cli_account.cu.config_yo_jenkins')
    def test_account_permission(self, mock_config, mock_secho):
        mock_yj = _mock_yj()
        mock_config.return_value = mock_yj

        cli_account.permission(user_id='admin', action='add', permission_id='Overall/Read', **PROFILE_TOKEN)
        mock_yj.account.permission.assert_called_once_with(user_id='admin', action='add', permission_id='Overall/Read')

    @patch('yojenkins.cli.cli_account.cu.standard_out')
    @patch('yojenkins.cli.cli_account.cu.config_yo_jenkins')
    def test_account_permission_list(self, mock_config, mock_stdout):
        mock_yj = _mock_yj()
        mock_config.return_value = mock_yj
        mock_yj.account.permission_list.return_value = ([{'id': 'perm1'}], ['perm1'])

        cli_account.permission_list(opt_list=True, **PROFILE_TOKEN, **COMMON_KWARGS)
        call_args = mock_stdout.call_args[0]
        assert call_args[0] == ['perm1']


# ============================================================================
# cli_auth tests
# ============================================================================


class TestCliAuthHandlers:
    @patch('yojenkins.cli.cli_auth.cu.standard_out')
    @patch('yojenkins.cli.cli_auth.Auth')
    def test_auth_show(self, mock_auth_cls, mock_stdout):
        mock_auth = MagicMock()
        mock_auth.show_local_credentials.return_value = {'default': {'url': 'http://localhost'}}
        mock_auth_cls.return_value = mock_auth

        cli_auth.show(**COMMON_KWARGS)
        mock_auth.show_local_credentials.assert_called_once()
        mock_stdout.assert_called_once()

    @patch('click.secho')
    @patch('yojenkins.cli.cli_auth.Auth')
    def test_auth_configure(self, mock_auth_cls, mock_secho):
        mock_auth = MagicMock()
        mock_auth_cls.return_value = mock_auth

        cli_auth.configure(auth_file=None)
        mock_auth.configure.assert_called_once_with(None)

    @patch('click.secho')
    @patch('yojenkins.cli.cli_auth.Auth')
    @patch('yojenkins.cli.cli_auth.Rest')
    def test_auth_verify(self, mock_rest_cls, mock_auth_cls, mock_secho):
        mock_auth = MagicMock()
        mock_auth_cls.return_value = mock_auth

        cli_auth.verify(profile='default', token='my-token')
        mock_auth.get_credentials.assert_called_once_with('default')
        mock_auth.create_auth.assert_called_once_with(token='my-token')

    @patch('click.secho')
    @patch('yojenkins.cli.cli_auth.Auth')
    @patch('yojenkins.cli.cli_auth.Rest')
    def test_auth_verify_token_passed_through(self, mock_rest_cls, mock_auth_cls, mock_secho):
        """Regression test for issue #217: YOJENKINS_TOKEN env var must reach create_auth()"""
        mock_auth = MagicMock()
        mock_auth_cls.return_value = mock_auth

        cli_auth.verify(profile='default', token='env-token-value')
        mock_auth.create_auth.assert_called_once_with(token='env-token-value')

    @patch('yojenkins.cli.cli_auth.cu.standard_out')
    @patch('yojenkins.cli.cli_auth.cu.config_yo_jenkins')
    def test_auth_user(self, mock_config, mock_stdout):
        mock_yj = _mock_yj()
        mock_config.return_value = mock_yj
        mock_yj.auth.user.return_value = {'id': 'admin'}

        cli_auth.user(**PROFILE_TOKEN, **COMMON_KWARGS)
        mock_yj.auth.user.assert_called_once()


# ============================================================================
# cli_stage tests
# ============================================================================


class TestCliStageHandlers:
    @patch('yojenkins.cli.cli_stage.cu.standard_out')
    @patch('yojenkins.cli.cli_stage.cu.config_yo_jenkins')
    @patch('yojenkins.cli.cli_stage.cu.is_full_url', return_value=False)
    def test_stage_info(self, mock_is_url, mock_config, mock_stdout):
        mock_yj = _mock_yj()
        mock_config.return_value = mock_yj
        mock_yj.stage.info.return_value = {'name': 'Build'}

        cli_stage.info(name='Build', job='my-job', number=1, url=None, latest=False, **PROFILE_TOKEN, **COMMON_KWARGS)
        mock_yj.stage.info.assert_called_once()

    @patch('yojenkins.cli.cli_stage.cu.standard_out')
    @patch('yojenkins.cli.cli_stage.cu.config_yo_jenkins')
    @patch('yojenkins.cli.cli_stage.cu.is_full_url', return_value=False)
    def test_stage_steps(self, mock_is_url, mock_config, mock_stdout):
        mock_yj = _mock_yj()
        mock_config.return_value = mock_yj
        mock_yj.stage.step_list.return_value = ([{'name': 'step1'}], ['step1'])

        cli_stage.steps(
            name='Build',
            job='my-job',
            number=1,
            url=None,
            latest=False,
            opt_list=False,
            **PROFILE_TOKEN,
            **COMMON_KWARGS,
        )
        mock_yj.stage.step_list.assert_called_once()

    @patch('yojenkins.cli.cli_stage.cu.config_yo_jenkins')
    @patch('yojenkins.cli.cli_stage.cu.is_full_url', return_value=False)
    def test_stage_logs(self, mock_is_url, mock_config):
        mock_yj = _mock_yj()
        mock_config.return_value = mock_yj

        cli_stage.logs(
            name='Build', job='my-job', number=1, url=None, latest=False, download_dir=None, **PROFILE_TOKEN
        )
        mock_yj.stage.logs.assert_called_once()

    @patch('yojenkins.cli.cli_stage.fail_out', side_effect=SystemExit(1))
    def test_stage_info_missing_number_and_latest_exits(self, mock_fail):
        """Should exit when job given without --number or --latest."""
        with pytest.raises(SystemExit):
            cli_stage.info(
                name='Build', job='my-job', number=None, url=None, latest=False, **PROFILE_TOKEN, **COMMON_KWARGS
            )


# ============================================================================
# cli_step tests
# ============================================================================


class TestCliStepHandlers:
    @patch('yojenkins.cli.cli_step.cu.standard_out')
    @patch('yojenkins.cli.cli_step.cu.config_yo_jenkins')
    @patch('yojenkins.cli.cli_step.cu.is_full_url', return_value=True)
    def test_step_info(self, mock_is_url, mock_config, mock_stdout):
        mock_yj = _mock_yj()
        mock_config.return_value = mock_yj
        mock_yj.step.info.return_value = {'id': '1'}

        step_url = 'http://localhost:8080/job/test/1/execution/node/1/wfapi/describe'
        cli_step.info(url=step_url, **PROFILE_TOKEN, **COMMON_KWARGS)
        mock_yj.step.info.assert_called_once_with(step_url=step_url)

    @patch('click.secho')
    @patch('yojenkins.cli.cli_step.cu.is_full_url', return_value=False)
    def test_step_info_invalid_url_exits(self, mock_is_url, mock_secho):
        """Should sys.exit(1) when URL is not valid."""
        with pytest.raises(SystemExit) as exc_info:
            cli_step.info(url='not-a-url', **PROFILE_TOKEN, **COMMON_KWARGS)
        assert exc_info.value.code == 1


# ============================================================================
# cli_tools tests
# ============================================================================


class TestCliToolsHandlers:
    @patch('yojenkins.cli.cli_tools.browser_open')
    def test_documentation(self, mock_browser):
        mock_browser.return_value = True
        cli_tools.documentation()
        mock_browser.assert_called_once()

    @patch('yojenkins.cli.cli_tools.browser_open')
    def test_bug_report(self, mock_browser):
        mock_browser.return_value = True
        cli_tools.bug_report()
        mock_browser.assert_called_once()

    @patch('yojenkins.cli.cli_tools.browser_open')
    def test_feature_request(self, mock_browser):
        mock_browser.return_value = True
        cli_tools.feature_request()
        mock_browser.assert_called_once()

    @patch('click.secho')
    @patch('yojenkins.cli.cli_tools.Package')
    def test_upgrade_success(self, mock_package, mock_secho):
        mock_package.install.return_value = True
        cli_tools.upgrade(user=True, proxy=None)
        mock_package.install.assert_called_once_with(user=True, proxy=None)

    @patch('click.secho')
    @patch('yojenkins.cli.cli_tools.Package')
    def test_upgrade_failure_exits(self, mock_package, mock_secho):
        mock_package.install.return_value = False
        with pytest.raises(SystemExit) as exc_info:
            cli_tools.upgrade(user=False, proxy=None)
        assert exc_info.value.code == 1

    @patch('yojenkins.cli.cli_tools.print2')
    @patch('yojenkins.cli.cli_tools.cu.config_yo_jenkins')
    def test_rest_request_success(self, mock_config, mock_print2):
        mock_yj = _mock_yj()
        mock_config.return_value = mock_yj
        mock_yj.rest.request.return_value = ({'key': 'value'}, {}, True)

        cli_tools.rest_request(
            request_text='/api/json', request_type='GET', raw=False, clean_html=False, **PROFILE_TOKEN
        )
        mock_yj.rest.request.assert_called_once()

    @patch('yojenkins.cli.cli_tools.fail_out', side_effect=SystemExit(1))
    @patch('yojenkins.cli.cli_tools.cu.config_yo_jenkins')
    def test_rest_request_failure_exits(self, mock_config, mock_fail):
        mock_yj = _mock_yj()
        mock_config.return_value = mock_yj
        mock_yj.rest.request.return_value = (None, {}, False)

        with pytest.raises(SystemExit):
            cli_tools.rest_request(
                request_text='/api/json', request_type='GET', raw=False, clean_html=False, **PROFILE_TOKEN
            )

    @patch('click.echo')
    @patch('yojenkins.cli.cli_tools.cu.config_yo_jenkins')
    def test_run_script_with_text(self, mock_config, mock_echo):
        mock_yj = _mock_yj()
        mock_config.return_value = mock_yj
        mock_yj.rest.request.return_value = ('println "hello"', {}, True)

        cli_tools.run_script(text='println "hello"', file=None, output=None, **PROFILE_TOKEN)
        mock_yj.rest.request.assert_called_once()

    @patch('click.echo')
    @patch('builtins.open', MagicMock(read_data='script content'))
    @patch('yojenkins.cli.cli_tools.Path')
    @patch('yojenkins.cli.cli_tools.cu.config_yo_jenkins')
    def test_run_script_with_file(self, mock_config, mock_path_cls, mock_echo):
        mock_path_cls.return_value.stat.return_value.st_size = 15
        mock_yj = _mock_yj()
        mock_config.return_value = mock_yj
        mock_yj.rest.request.return_value = ('output', {}, True)

        cli_tools.run_script(text=None, file='/tmp/script.groovy', output=None, **PROFILE_TOKEN)
        mock_yj.rest.request.assert_called_once()

    @patch('yojenkins.cli.cli_tools.fail_out', side_effect=SystemExit(1))
    @patch('yojenkins.cli.cli_tools.cu.config_yo_jenkins')
    def test_run_script_failure_exits(self, mock_config, mock_fail):
        mock_yj = _mock_yj()
        mock_config.return_value = mock_yj
        mock_yj.rest.request.return_value = (None, {}, False)

        with pytest.raises(SystemExit):
            cli_tools.run_script(text='println "hello"', file=None, output=None, **PROFILE_TOKEN)

    @patch('yojenkins.cli.cli_tools.print2')
    @patch('yojenkins.cli.cli_tools.cu.config_yo_jenkins')
    def test_rest_request_head(self, mock_config, mock_print2):
        mock_yj = _mock_yj()
        mock_config.return_value = mock_yj
        mock_yj.rest.request.return_value = ('', {'Content-Type': 'text/html'}, True)

        with pytest.raises(SystemExit) as exc_info:
            cli_tools.rest_request(
                request_text='/api/json', request_type='HEAD', raw=False, clean_html=False, **PROFILE_TOKEN
            )
        assert exc_info.value.code == 0

    @patch('yojenkins.cli.cli_tools.print2')
    @patch('yojenkins.cli.cli_tools.html_clean', return_value='clean text')
    @patch('yojenkins.cli.cli_tools.cu.config_yo_jenkins')
    def test_rest_request_clean_html(self, mock_config, mock_html_clean, mock_print2):
        mock_yj = _mock_yj()
        mock_config.return_value = mock_yj
        mock_yj.rest.request.return_value = ('<b>text</b>', {}, True)

        cli_tools.rest_request(
            request_text='/api/json', request_type='GET', raw=True, clean_html=True, **PROFILE_TOKEN
        )
        mock_html_clean.assert_called_once()

    @patch('yojenkins.cli.cli_tools.fail_out', side_effect=SystemExit(1))
    @patch('yojenkins.cli.cli_tools.cu.config_yo_jenkins')
    def test_rest_request_empty_content(self, mock_config, mock_fail):
        mock_yj = _mock_yj()
        mock_config.return_value = mock_yj
        mock_yj.rest.request.return_value = (None, {}, True)

        with pytest.raises(SystemExit):
            cli_tools.rest_request(
                request_text='/api/json', request_type='GET', raw=False, clean_html=False, **PROFILE_TOKEN
            )

    @patch('click.confirm', return_value=True)
    @patch('yojenkins.cli.cli_tools.Package')
    def test_remove_confirmed(self, mock_package, mock_confirm):
        cli_tools.remove()
        mock_package.uninstall.assert_called_once()

    @patch('click.confirm', return_value=False)
    @patch('yojenkins.cli.cli_tools.Package')
    def test_remove_declined(self, mock_package, mock_confirm):
        cli_tools.remove()
        mock_package.uninstall.assert_not_called()

    @patch('click.secho')
    @patch('yojenkins.cli.cli_tools.fail_out', side_effect=SystemExit(1))
    @patch('yojenkins.cli.cli_tools.SharedLibrary')
    @patch('yojenkins.cli.cli_tools.cu.config_yo_jenkins')
    def test_shared_lib_setup_failure(self, mock_config, mock_sl, mock_fail, mock_secho):
        mock_yj = _mock_yj()
        mock_config.return_value = mock_yj
        mock_sl.return_value.setup.return_value = False

        with pytest.raises(SystemExit):
            cli_tools.shared_lib_setup(**PROFILE_TOKEN)

    @patch('click.secho')
    @patch('yojenkins.cli.cli_tools.SharedLibrary')
    @patch('yojenkins.cli.cli_tools.cu.config_yo_jenkins')
    def test_shared_lib_setup_success(self, mock_config, mock_sl, mock_secho):
        mock_yj = _mock_yj()
        mock_config.return_value = mock_yj
        mock_sl.return_value.setup.return_value = True

        cli_tools.shared_lib_setup(**PROFILE_TOKEN)
        mock_secho.assert_called_with('success', fg='bright_green', bold=True)

    @patch('click.echo')
    @patch('yojenkins.cli.cli_tools.load_contents_from_local_file')
    def test_history_display(self, mock_load, mock_echo):
        mock_load.return_value = [
            {
                'profile': 'default',
                'datetime': '2024-01-01 12:00:00',
                'tool_version': '1.0.0',
                'tool_path': 'server info',
                'arguments': '',
            }
        ]
        cli_tools.history(profile=None, clear=False)
        mock_echo.assert_called()

    @patch('click.secho')
    @patch('pathlib.Path.unlink')
    def test_history_clear(self, mock_unlink, mock_secho):
        with pytest.raises(SystemExit) as exc_info:
            cli_tools.history(profile=None, clear=True)
        assert exc_info.value.code == 0

    @patch('yojenkins.cli.cli_tools.load_contents_from_local_file', return_value=None)
    def test_history_empty(self, mock_load):
        with pytest.raises(SystemExit) as exc_info:
            cli_tools.history(profile=None, clear=False)
        assert exc_info.value.code == 1

    @patch('click.secho')
    @patch('builtins.open', new_callable=mock_open)
    def test_history_disable(self, mocked_open, mock_secho):
        with patch('pathlib.Path.home', return_value=Path('/tmp/fakehome')):
            with patch('pathlib.Path.is_file', return_value=False):
                with patch('pathlib.Path.mkdir'):
                    with pytest.raises(SystemExit) as exc_info:
                        cli_tools.history(profile=None, clear=False, disable=True, enable=False)
        assert exc_info.value.code == 0
        mock_secho.assert_called_with('History tracking disabled', fg='bright_green', bold=True)
        mocked_open().writelines.assert_called_once()
        written = mocked_open().writelines.call_args[0][0]
        assert any('history_enabled=false' in line for line in written)

    @patch('click.secho')
    @patch('builtins.open', new_callable=mock_open)
    def test_history_enable(self, mocked_open, mock_secho):
        with patch('pathlib.Path.home', return_value=Path('/tmp/fakehome')):
            with patch('pathlib.Path.is_file', return_value=False):
                with patch('pathlib.Path.mkdir'):
                    with pytest.raises(SystemExit) as exc_info:
                        cli_tools.history(profile=None, clear=False, disable=False, enable=True)
        assert exc_info.value.code == 0
        mock_secho.assert_called_with('History tracking enabled', fg='bright_green', bold=True)
        mocked_open().writelines.assert_called_once()
        written = mocked_open().writelines.call_args[0][0]
        assert any('history_enabled=true' in line for line in written)


# ============================================================================
# Additional cli_build tests for uncovered branches
# ============================================================================


class TestCliBuildHandlersExtended:
    @patch('yojenkins.cli.cli_build.cu.standard_out')
    @patch('yojenkins.cli.cli_build.cu.config_yo_jenkins')
    @patch('yojenkins.cli.cli_build.cu.is_full_url', return_value=True)
    @patch('yojenkins.cli.cli_build.is_complete_build_url', return_value=False)
    def test_build_info_by_url(self, mock_is_build_url, mock_is_url, mock_config, mock_stdout):
        mock_yj = _mock_yj()
        mock_config.return_value = mock_yj
        mock_yj.build.info.return_value = {'number': 1}

        cli_build.info(
            job=None,
            number=None,
            url='http://j:8080/job/my-job/1/',
            latest=False,
            **PROFILE_TOKEN,
            **{**COMMON_KWARGS},
        )
        mock_yj.build.info.assert_called_once()

    @patch('yojenkins.cli.cli_build.cu.standard_out')
    @patch('yojenkins.cli.cli_build.cu.config_yo_jenkins')
    @patch('yojenkins.cli.cli_build.cu.is_full_url', return_value=True)
    @patch('yojenkins.cli.cli_build.is_complete_build_url', return_value=True)
    def test_build_info_auto_detect_build_url(self, mock_is_build_url, mock_is_url, mock_config, mock_stdout):
        """When job argument is actually a build URL, it should be swapped."""
        mock_yj = _mock_yj()
        mock_config.return_value = mock_yj
        mock_yj.build.info.return_value = {'number': 1}

        cli_build.info(
            job='http://j:8080/job/my-job/1/', number=None, url=None, latest=True, **PROFILE_TOKEN, **{**COMMON_KWARGS}
        )
        mock_yj.build.info.assert_called_once()

    @patch('click.secho')
    @patch('yojenkins.cli.cli_build.cu.config_yo_jenkins')
    @patch('yojenkins.cli.cli_build.cu.is_full_url', return_value=False)
    @patch('yojenkins.cli.cli_build.is_complete_build_url', return_value=False)
    def test_build_status_success(self, mock_is_build_url, mock_is_url, mock_config, mock_secho):
        mock_yj = _mock_yj()
        mock_config.return_value = mock_yj
        mock_yj.build.status_text.return_value = 'SUCCESS'

        cli_build.status(job='my-job', number=1, url=None, latest=False, **PROFILE_TOKEN)
        mock_secho.assert_called_with('SUCCESS', fg='bright_green', bold=True)

    @patch('click.secho')
    @patch('yojenkins.cli.cli_build.cu.config_yo_jenkins')
    @patch('yojenkins.cli.cli_build.cu.is_full_url', return_value=False)
    @patch('yojenkins.cli.cli_build.is_complete_build_url', return_value=False)
    def test_build_status_failure(self, mock_is_build_url, mock_is_url, mock_config, mock_secho):
        mock_yj = _mock_yj()
        mock_config.return_value = mock_yj
        mock_yj.build.status_text.return_value = 'FAILURE'

        cli_build.status(job='my-job', number=1, url=None, latest=False, **PROFILE_TOKEN)
        mock_secho.assert_called_with('FAILURE', fg='bright_red', bold=True)

    @patch('click.secho')
    @patch('yojenkins.cli.cli_build.cu.config_yo_jenkins')
    @patch('yojenkins.cli.cli_build.cu.is_full_url', return_value=False)
    @patch('yojenkins.cli.cli_build.is_complete_build_url', return_value=False)
    def test_build_status_running(self, mock_is_build_url, mock_is_url, mock_config, mock_secho):
        mock_yj = _mock_yj()
        mock_config.return_value = mock_yj
        mock_yj.build.status_text.return_value = 'IN_PROGRESS'

        cli_build.status(job='my-job', number=1, url=None, latest=False, **PROFILE_TOKEN)
        mock_secho.assert_called_with('IN_PROGRESS', fg='blue', bold=True)

    @patch('click.secho')
    @patch('yojenkins.cli.cli_build.cu.config_yo_jenkins')
    @patch('yojenkins.cli.cli_build.cu.is_full_url', return_value=False)
    @patch('yojenkins.cli.cli_build.is_complete_build_url', return_value=False)
    def test_build_status_unknown(self, mock_is_build_url, mock_is_url, mock_config, mock_secho):
        mock_yj = _mock_yj()
        mock_config.return_value = mock_yj
        mock_yj.build.status_text.return_value = 'UNKNOWN'

        cli_build.status(job='my-job', number=1, url=None, latest=False, **PROFILE_TOKEN)
        mock_secho.assert_called_with('UNKNOWN', fg='black', bold=True)

    @patch('click.secho')
    @patch('yojenkins.cli.cli_build.cu.config_yo_jenkins')
    @patch('yojenkins.cli.cli_build.cu.is_full_url', return_value=False)
    @patch('yojenkins.cli.cli_build.is_complete_build_url', return_value=False)
    def test_build_status_none(self, mock_is_build_url, mock_is_url, mock_config, mock_secho):
        mock_yj = _mock_yj()
        mock_config.return_value = mock_yj
        mock_yj.build.status_text.return_value = None

        cli_build.status(job='my-job', number=1, url=None, latest=False, **PROFILE_TOKEN)
        mock_secho.assert_called_with('NONE', fg='black', bold=True)

    @patch('yojenkins.cli.cli_build.cu.config_yo_jenkins')
    @patch('yojenkins.cli.cli_build.cu.is_full_url', return_value=False)
    @patch('yojenkins.cli.cli_build.is_complete_build_url', return_value=False)
    def test_build_browser(self, mock_is_build_url, mock_is_url, mock_config):
        mock_yj = _mock_yj()
        mock_config.return_value = mock_yj

        cli_build.browser(job='my-job', number=1, url=None, latest=False, **PROFILE_TOKEN)
        mock_yj.build.browser_open.assert_called_once()

    @patch('yojenkins.cli.cli_build.cu.config_yo_jenkins')
    @patch('yojenkins.cli.cli_build.cu.is_full_url', return_value=False)
    @patch('yojenkins.cli.cli_build.is_complete_build_url', return_value=False)
    def test_build_monitor(self, mock_is_build_url, mock_is_url, mock_config):
        mock_yj = _mock_yj()
        mock_config.return_value = mock_yj

        cli_build.monitor(job='my-job', number=1, url=None, latest=False, sound=False, **PROFILE_TOKEN)
        mock_yj.build.monitor.assert_called_once()

    @patch('click.secho')
    @patch('yojenkins.cli.cli_build.cu.config_yo_jenkins')
    @patch('yojenkins.cli.cli_build.cu.is_full_url', return_value=False)
    @patch('yojenkins.cli.cli_build.is_complete_build_url', return_value=False)
    def test_build_logs_with_download_dir(self, mock_is_build_url, mock_is_url, mock_config, mock_secho):
        mock_yj = _mock_yj()
        mock_config.return_value = mock_yj

        cli_build.logs(
            job='my-job', number=1, url=None, latest=False, tail=0, download_dir='/tmp', follow=False, **PROFILE_TOKEN
        )
        mock_yj.build.logs.assert_called_once()
        mock_secho.assert_called_with('success', fg='bright_green', bold=True)

    @patch('yojenkins.cli.cli_build.wait_for_build_and_follow_logs')
    @patch('yojenkins.cli.cli_build.cu.config_yo_jenkins')
    @patch('yojenkins.cli.cli_build.cu.is_full_url', return_value=False)
    @patch('yojenkins.cli.cli_build.is_complete_build_url', return_value=False)
    def test_build_rebuild_with_follow(self, mock_is_build_url, mock_is_url, mock_config, mock_follow):
        mock_yj = _mock_yj()
        mock_config.return_value = mock_yj
        mock_yj.build.rebuild.return_value = 789

        cli_build.rebuild(job='my-job', number=1, url=None, latest=False, follow_logs=True, **PROFILE_TOKEN)
        mock_follow.assert_called_once_with(mock_yj, 789)

    @patch('yojenkins.cli.cli_build.wait_for_build_and_monitor')
    @patch('yojenkins.cli.cli_build.cu.config_yo_jenkins')
    @patch('yojenkins.cli.cli_build.cu.is_full_url', return_value=False)
    @patch('yojenkins.cli.cli_build.is_complete_build_url', return_value=False)
    def test_build_rebuild_with_monitor(self, mock_is_build_url, mock_is_url, mock_config, mock_monitor):
        mock_yj = _mock_yj()
        mock_config.return_value = mock_yj
        mock_yj.build.rebuild.return_value = 888

        cli_build.rebuild(
            job='my-job', number=1, url=None, latest=False, follow_logs=False, monitor=True, **PROFILE_TOKEN
        )
        mock_monitor.assert_called_once_with(mock_yj, 888)

    @patch('yojenkins.cli.cli_build.cu.standard_out')
    @patch('yojenkins.cli.cli_build.cu.config_yo_jenkins')
    @patch('yojenkins.cli.cli_build.cu.is_full_url', return_value=False)
    @patch('yojenkins.cli.cli_build.is_complete_build_url', return_value=False)
    def test_build_stages_opt_list(self, mock_is_build_url, mock_is_url, mock_config, mock_stdout):
        mock_yj = _mock_yj()
        mock_config.return_value = mock_yj
        mock_yj.build.stage_list.return_value = ([{'name': 's1'}], ['s1'])

        cli_build.stages(
            job='my-job', number=1, url=None, latest=False, opt_list=True, **PROFILE_TOKEN, **COMMON_KWARGS
        )
        call_args = mock_stdout.call_args[0]
        assert call_args[0] == ['s1']

    @patch('yojenkins.cli.cli_build.cu.standard_out')
    @patch('yojenkins.cli.cli_build.cu.config_yo_jenkins')
    @patch('yojenkins.cli.cli_build.cu.is_full_url', return_value=False)
    @patch('yojenkins.cli.cli_build.is_complete_build_url', return_value=False)
    def test_build_parameters_opt_list(self, mock_is_build_url, mock_is_url, mock_config, mock_stdout):
        mock_yj = _mock_yj()
        mock_config.return_value = mock_yj
        mock_yj.build.parameters.return_value = ([{'name': 'p1'}], ['p1'])

        cli_build.parameters(
            job='my-job', number=1, url=None, latest=False, opt_list=True, **PROFILE_TOKEN, **COMMON_KWARGS
        )
        call_args = mock_stdout.call_args[0]
        assert call_args[0] == ['p1']

    @patch('yojenkins.cli.cli_build.is_complete_build_url', return_value=False)
    def test_build_status_missing_number_and_latest_exits(self, mock_is_build_url):
        with pytest.raises(SystemExit) as exc_info:
            cli_build.status(job='my-job', number=None, url=None, latest=False, **PROFILE_TOKEN)
        assert exc_info.value.code == 1

    @patch('yojenkins.cli.cli_build.is_complete_build_url', return_value=False)
    def test_build_abort_missing_number_and_latest_exits(self, mock_is_build_url):
        with pytest.raises(SystemExit) as exc_info:
            cli_build.abort(job='my-job', number=None, url=None, latest=False, **PROFILE_TOKEN)
        assert exc_info.value.code == 1

    @patch('yojenkins.cli.cli_build.is_complete_build_url', return_value=False)
    def test_build_delete_missing_number_and_latest_exits(self, mock_is_build_url):
        with pytest.raises(SystemExit) as exc_info:
            cli_build.delete(job='my-job', number=None, url=None, latest=False, **PROFILE_TOKEN)
        assert exc_info.value.code == 1

    @patch('yojenkins.cli.cli_build.is_complete_build_url', return_value=False)
    def test_build_logs_missing_number_and_latest_exits(self, mock_is_build_url):
        with pytest.raises(SystemExit) as exc_info:
            cli_build.logs(
                job='my-job',
                number=None,
                url=None,
                latest=False,
                tail=0,
                download_dir=None,
                follow=False,
                **PROFILE_TOKEN,
            )
        assert exc_info.value.code == 1

    @patch('yojenkins.cli.cli_build.browser_open')
    @patch('yojenkins.cli.cli_build.cu.config_yo_jenkins')
    @patch('yojenkins.cli.cli_build.cu.is_full_url', return_value=True)
    @patch('yojenkins.cli.cli_build.is_complete_build_url', return_value=False)
    def test_build_browser_url_skips_auth(self, mock_is_build_url, mock_is_url, mock_config, mock_browser):
        cli_build.browser(job=None, number=None, url='http://jenkins/job/my-job/42', latest=False, **PROFILE_TOKEN)
        mock_browser.assert_called_once_with('http://jenkins/job/my-job/42')
        mock_config.assert_not_called()

    @patch('yojenkins.cli.cli_build.is_complete_build_url', return_value=False)
    def test_build_browser_missing_number_and_latest_exits(self, mock_is_build_url):
        with pytest.raises(SystemExit) as exc_info:
            cli_build.browser(job='my-job', number=None, url=None, latest=False, **PROFILE_TOKEN)
        assert exc_info.value.code == 1

    @patch('yojenkins.cli.cli_build.is_complete_build_url', return_value=False)
    def test_build_monitor_missing_number_and_latest_exits(self, mock_is_build_url):
        with pytest.raises(SystemExit) as exc_info:
            cli_build.monitor(job='my-job', number=None, url=None, latest=False, sound=False, **PROFILE_TOKEN)
        assert exc_info.value.code == 1

    @patch('yojenkins.cli.cli_build.is_complete_build_url', return_value=False)
    def test_build_stages_missing_number_and_latest_exits(self, mock_is_build_url):
        with pytest.raises(SystemExit) as exc_info:
            cli_build.stages(
                job='my-job', number=None, url=None, latest=False, opt_list=False, **PROFILE_TOKEN, **COMMON_KWARGS
            )
        assert exc_info.value.code == 1

    @patch('yojenkins.cli.cli_build.is_complete_build_url', return_value=False)
    def test_build_parameters_missing_number_and_latest_exits(self, mock_is_build_url):
        with pytest.raises(SystemExit) as exc_info:
            cli_build.parameters(
                job='my-job', number=None, url=None, latest=False, opt_list=False, **PROFILE_TOKEN, **COMMON_KWARGS
            )
        assert exc_info.value.code == 1

    @patch('yojenkins.cli.cli_build.is_complete_build_url', return_value=False)
    def test_build_rebuild_missing_number_and_latest_exits(self, mock_is_build_url):
        with pytest.raises(SystemExit) as exc_info:
            cli_build.rebuild(job='my-job', number=None, url=None, latest=False, follow_logs=False, **PROFILE_TOKEN)
        assert exc_info.value.code == 1


# ============================================================================
# Additional cli_server tests for uncovered branches
# ============================================================================


class TestCliServerHandlersExtended:
    @patch('click.secho')
    @patch('yojenkins.cli.cli_server.YoJenkins')
    @patch('yojenkins.cli.cli_server.Auth')
    def test_server_reachable_true(self, mock_auth_cls, mock_yj_cls, mock_secho):
        mock_auth = MagicMock()
        mock_auth.jenkins_profile = {'jenkins_server_url': 'http://localhost:8080/'}
        mock_auth_cls.return_value = mock_auth
        mock_yj = _mock_yj()
        mock_yj_cls.return_value = mock_yj
        mock_yj.rest.is_reachable.return_value = True

        cli_server.reachable(profile='default', timeout=10)
        mock_secho.assert_called_with('true', fg='bright_green', bold=True)

    @patch('click.secho')
    @patch('yojenkins.cli.cli_server.YoJenkins')
    @patch('yojenkins.cli.cli_server.Auth')
    def test_server_reachable_false(self, mock_auth_cls, mock_yj_cls, mock_secho):
        mock_auth = MagicMock()
        mock_auth.jenkins_profile = {'jenkins_server_url': 'http://localhost:8080/'}
        mock_auth_cls.return_value = mock_auth
        mock_yj = _mock_yj()
        mock_yj_cls.return_value = mock_yj
        mock_yj.rest.is_reachable.return_value = False

        cli_server.reachable(profile='default', timeout=5)
        mock_secho.assert_called_with('false', fg='bright_red', bold=True)


# ============================================================================
# cli_server.server_deploy and server_teardown tests (lines 174-290)
# ============================================================================


class TestCliServerDeploy:
    @patch('yojenkins.cli.cli_server.print2')
    @patch('yojenkins.cli.cli_server.click.echo')
    @patch('yojenkins.cli.cli_server.DockerJenkinsServer')
    @patch('yojenkins.cli.cli_server.logger')
    def test_server_deploy_success(self, mock_logger, mock_djs_cls, mock_echo, mock_print2):
        mock_logger.level = 5  # debug level, skip spinner
        mock_djs = MagicMock()
        mock_djs_cls.return_value = mock_djs
        mock_djs.docker_client_init.return_value = True
        deployed = {
            'image': 'jenkins/jenkins:lts',
            'container': 'yojenkins-jenkins',
            'volumes': [{'named': 'yojenkins-vol'}],
            'address': 'http://localhost:8080',
        }
        mock_djs.setup.return_value = (deployed, True)

        with patch('builtins.open', mock_open()):
            cli_server.server_deploy(
                config_file='',
                plugins_file='',
                protocol_schema='http',
                host='localhost',
                port=8080,
                image_base='jenkins/jenkins:lts',
                extra_setup_script='',
                image_rebuild=False,
                new_volume=False,
                new_volume_name='',
                bind_mount_dir='',
                container_name='yojenkins-jenkins',
                registry='',
                admin_user='admin',
                password='',
            )
        mock_djs.setup.assert_called_once()

    @patch('yojenkins.cli.cli_server.DockerJenkinsServer')
    @patch('yojenkins.cli.cli_server.logger')
    def test_server_deploy_docker_client_fail(self, mock_logger, mock_djs_cls):
        mock_logger.level = 5
        mock_djs = MagicMock()
        mock_djs_cls.return_value = mock_djs
        mock_djs.docker_client_init.return_value = False

        with pytest.raises(SystemExit):
            cli_server.server_deploy(
                config_file='',
                plugins_file='',
                protocol_schema='http',
                host='localhost',
                port=8080,
                image_base='jenkins/jenkins:lts',
                extra_setup_script='',
                image_rebuild=False,
                new_volume=False,
                new_volume_name='',
                bind_mount_dir='',
                container_name='',
                registry='',
                admin_user='admin',
                password='',
            )

    @patch('yojenkins.cli.cli_server.DockerJenkinsServer')
    @patch('yojenkins.cli.cli_server.logger')
    def test_server_deploy_setup_failure(self, mock_logger, mock_djs_cls):
        mock_logger.level = 5
        mock_djs = MagicMock()
        mock_djs_cls.return_value = mock_djs
        mock_djs.docker_client_init.return_value = True
        mock_djs.setup.return_value = ({'image': 'x', 'container': 'y'}, False)

        with pytest.raises(SystemExit):
            cli_server.server_deploy(
                config_file='',
                plugins_file='',
                protocol_schema='http',
                host='localhost',
                port=8080,
                image_base='jenkins/jenkins:lts',
                extra_setup_script='',
                image_rebuild=False,
                new_volume=False,
                new_volume_name='',
                bind_mount_dir='',
                container_name='',
                registry='',
                admin_user='admin',
                password='',
            )


class TestCliServerTeardown:
    @patch('yojenkins.cli.cli_server.print2')
    @patch('pathlib.Path.unlink')
    @patch('yojenkins.cli.cli_server.DockerJenkinsServer')
    def test_server_teardown_success(self, mock_djs_cls, mock_unlink, mock_print2):
        deployed = {
            'image': 'jenkins/jenkins:lts',
            'container': 'yojenkins-jenkins',
            'volumes': [{'named': 'yojenkins-vol'}],
            'address': 'http://localhost:8080',
        }
        mock_djs = MagicMock()
        mock_djs_cls.return_value = mock_djs
        mock_djs.docker_client_init.return_value = True
        mock_djs.clean.return_value = True

        with patch('builtins.open', mock_open(read_data=json.dumps(deployed))):
            cli_server.server_teardown(remove_volume=True, remove_image=True)
        mock_djs.clean.assert_called_once_with(True, True)

    @patch('yojenkins.cli.cli_server.DockerJenkinsServer')
    def test_server_teardown_file_not_found_exits(self, mock_djs_cls):
        with patch('builtins.open', side_effect=FileNotFoundError('not found')):
            with pytest.raises(SystemExit):
                cli_server.server_teardown(remove_volume=False, remove_image=False)

    @patch('yojenkins.cli.cli_server.DockerJenkinsServer')
    def test_server_teardown_clean_failure_exits(self, mock_djs_cls):
        deployed = {
            'image': 'jenkins/jenkins:lts',
            'container': 'yojenkins-jenkins',
            'volumes': [{'named': 'yojenkins-vol'}],
            'address': 'http://localhost:8080',
        }
        mock_djs = MagicMock()
        mock_djs_cls.return_value = mock_djs
        mock_djs.docker_client_init.return_value = True
        mock_djs.clean.return_value = False

        with patch('builtins.open', mock_open(read_data=json.dumps(deployed))):
            with pytest.raises(SystemExit):
                cli_server.server_teardown(remove_volume=False, remove_image=False)


# ============================================================================
# Additional cli_job tests for uncovered branches
# ============================================================================


class TestCliJobHandlersExtended:
    @patch('yojenkins.cli.cli_job.cu.standard_out')
    @patch('yojenkins.cli.cli_job.cu.config_yo_jenkins')
    @patch('yojenkins.cli.cli_job.cu.is_full_url', return_value=True)
    def test_job_info_by_url(self, mock_is_url, mock_config, mock_stdout):
        mock_yj = _mock_yj()
        mock_config.return_value = mock_yj
        url = 'http://localhost:8080/job/my-job'
        mock_yj.job.info.return_value = {'name': 'my-job'}

        cli_job.info(job=url, **PROFILE_TOKEN, **COMMON_KWARGS)
        mock_yj.job.info.assert_called_once_with(job_url=url)

    @patch('yojenkins.cli.cli_job.cu.standard_out')
    @patch('yojenkins.cli.cli_job.cu.config_yo_jenkins')
    @patch('yojenkins.cli.cli_job.cu.is_full_url', return_value=False)
    def test_job_search_by_name(self, mock_is_url, mock_config, mock_stdout):
        mock_yj = _mock_yj()
        mock_config.return_value = mock_yj
        mock_yj.job.search.return_value = ([{'name': 'job1'}], ['job1'])

        cli_job.search(
            search_pattern='.*test.*',
            search_folder='',
            depth=4,
            fullname=False,
            opt_list=False,
            **PROFILE_TOKEN,
            **COMMON_KWARGS,
        )
        mock_yj.job.search.assert_called_once()

    @patch('yojenkins.cli.cli_job.print2')
    @patch('yojenkins.cli.cli_job.cu.config_yo_jenkins')
    @patch('yojenkins.cli.cli_job.cu.is_full_url', return_value=False)
    def test_job_search_no_results_exits(self, mock_is_url, mock_config, mock_print2):
        mock_yj = _mock_yj()
        mock_config.return_value = mock_yj
        mock_yj.job.search.return_value = ([], [])

        with pytest.raises(SystemExit) as exc_info:
            cli_job.search(
                search_pattern='nope',
                search_folder='',
                depth=4,
                fullname=False,
                opt_list=False,
                **PROFILE_TOKEN,
                **COMMON_KWARGS,
            )
        assert exc_info.value.code == 1

    @patch('yojenkins.cli.cli_job.cu.standard_out')
    @patch('yojenkins.cli.cli_job.cu.config_yo_jenkins')
    @patch('yojenkins.cli.cli_job.cu.is_full_url', return_value=False)
    def test_job_queue_check_by_name(self, mock_is_url, mock_config, mock_stdout):
        mock_yj = _mock_yj()
        mock_config.return_value = mock_yj
        mock_yj.job.in_queue_check.return_value = ({'queued': True}, 42)

        cli_job.queue_check(job='my-job', opt_id=False, **PROFILE_TOKEN, **COMMON_KWARGS)
        mock_stdout.assert_called_once()

    @patch('click.secho')
    @patch('yojenkins.cli.cli_job.cu.config_yo_jenkins')
    @patch('yojenkins.cli.cli_job.cu.is_full_url', return_value=False)
    def test_job_queue_check_opt_id(self, mock_is_url, mock_config, mock_secho):
        mock_yj = _mock_yj()
        mock_config.return_value = mock_yj
        mock_yj.job.in_queue_check.return_value = ({'queued': True}, 42)

        cli_job.queue_check(job='my-job', opt_id=True, **PROFILE_TOKEN, **COMMON_KWARGS)
        mock_secho.assert_called_with('42', fg='bright_green', bold=True)

    @patch('yojenkins.cli.cli_job.cu.config_yo_jenkins')
    @patch('yojenkins.cli.cli_job.cu.is_full_url', return_value=False)
    def test_job_browser(self, mock_is_url, mock_config):
        mock_yj = _mock_yj()
        mock_config.return_value = mock_yj

        cli_job.browser(job='my-job', **PROFILE_TOKEN)
        mock_yj.job.browser_open.assert_called_once_with(job_name='my-job')

    @patch('yojenkins.cli.cli_job.browser_open')
    @patch('yojenkins.cli.cli_job.cu.config_yo_jenkins')
    @patch('yojenkins.cli.cli_job.cu.is_full_url', return_value=True)
    def test_job_browser_url_skips_auth(self, mock_is_url, mock_config, mock_browser):
        cli_job.browser(job='http://jenkins/job/my-job', **PROFILE_TOKEN)
        mock_browser.assert_called_once_with('http://jenkins/job/my-job')
        mock_config.assert_not_called()

    @patch('yojenkins.cli.cli_job.cu.config_yo_jenkins')
    @patch('yojenkins.cli.cli_job.cu.is_full_url', return_value=False)
    def test_job_monitor(self, mock_is_url, mock_config):
        mock_yj = _mock_yj()
        mock_config.return_value = mock_yj

        cli_job.monitor(job='my-job', sound=False, **PROFILE_TOKEN)
        mock_yj.job.monitor.assert_called_once_with(job_name='my-job', sound=False)

    @patch('click.secho')
    @patch('yojenkins.cli.cli_job.cu.config_yo_jenkins')
    @patch('yojenkins.cli.cli_job.cu.is_full_url', return_value=False)
    def test_job_create(self, mock_is_url, mock_config, mock_secho):
        mock_yj = _mock_yj()
        mock_config.return_value = mock_yj

        cli_job.create(name='new-job', folder='my-folder', config_file='', config_is_json=False, **PROFILE_TOKEN)
        mock_yj.job.create.assert_called_once()

    @patch('yojenkins.cli.cli_job.cu.standard_out')
    @patch('yojenkins.cli.cli_job.cu.config_yo_jenkins')
    @patch('yojenkins.cli.cli_job.cu.is_full_url', return_value=False)
    def test_job_config_xml(self, mock_is_url, mock_config, mock_stdout):
        mock_yj = _mock_yj()
        mock_config.return_value = mock_yj
        mock_yj.job.config.return_value = '<project></project>'

        cli_job.config(
            job='my-job',
            filepath=None,
            opt_pretty=False,
            opt_yaml=False,
            opt_xml=False,
            opt_toml=False,
            opt_json=False,
            **PROFILE_TOKEN,
        )
        mock_stdout.assert_called_once()

    @patch('yojenkins.cli.cli_job.wait_for_build_and_follow_logs')
    @patch('yojenkins.cli.cli_job.cu.config_yo_jenkins')
    @patch('yojenkins.cli.cli_job.cu.is_full_url', return_value=False)
    def test_job_build_with_follow_logs(self, mock_is_url, mock_config, mock_follow):
        mock_yj = _mock_yj()
        mock_config.return_value = mock_yj
        mock_yj.job.build_trigger.return_value = 555

        cli_job.build(job='my-job', parameter=(), follow_logs=True, **PROFILE_TOKEN)
        mock_follow.assert_called_once_with(mock_yj, 555)

    @patch('yojenkins.cli.cli_job.wait_for_build_and_monitor')
    @patch('yojenkins.cli.cli_job.cu.config_yo_jenkins')
    @patch('yojenkins.cli.cli_job.cu.is_full_url', return_value=False)
    def test_job_build_with_monitor(self, mock_is_url, mock_config, mock_monitor):
        mock_yj = _mock_yj()
        mock_config.return_value = mock_yj
        mock_yj.job.build_trigger.return_value = 777

        cli_job.build(job='my-job', parameter=(), follow_logs=False, monitor=True, **PROFILE_TOKEN)
        mock_monitor.assert_called_once_with(mock_yj, 777)


# ============================================================================
# Additional cli_folder tests for uncovered branches
# ============================================================================


class TestCliFolderHandlersExtended:
    @patch('yojenkins.cli.cli_folder.cu.standard_out')
    @patch('yojenkins.cli.cli_folder.cu.config_yo_jenkins')
    @patch('yojenkins.cli.cli_folder.cu.is_full_url', return_value=False)
    def test_folder_search_by_name(self, mock_is_url, mock_config, mock_stdout):
        mock_yj = _mock_yj()
        mock_config.return_value = mock_yj
        mock_yj.folder.search.return_value = ([{'name': 'f1'}], ['f1'])

        cli_folder.search(
            search_pattern='.*',
            search_folder='',
            depth=4,
            fullname=False,
            opt_list=False,
            **PROFILE_TOKEN,
            **COMMON_KWARGS,
        )
        mock_yj.folder.search.assert_called_once()

    @patch('yojenkins.cli.cli_folder.print2')
    @patch('yojenkins.cli.cli_folder.cu.config_yo_jenkins')
    @patch('yojenkins.cli.cli_folder.cu.is_full_url', return_value=False)
    def test_folder_search_no_results_exits(self, mock_is_url, mock_config, mock_print2):
        mock_yj = _mock_yj()
        mock_config.return_value = mock_yj
        mock_yj.folder.search.return_value = ([], [])

        with pytest.raises(SystemExit) as exc_info:
            cli_folder.search(
                search_pattern='nope',
                search_folder='',
                depth=4,
                fullname=False,
                opt_list=False,
                **PROFILE_TOKEN,
                **COMMON_KWARGS,
            )
        assert exc_info.value.code == 1

    @patch('yojenkins.cli.cli_folder.cu.standard_out')
    @patch('yojenkins.cli.cli_folder.cu.config_yo_jenkins')
    @patch('yojenkins.cli.cli_folder.cu.is_full_url', return_value=False)
    def test_folder_config_xml(self, mock_is_url, mock_config, mock_stdout):
        mock_yj = _mock_yj()
        mock_config.return_value = mock_yj
        mock_yj.folder.config.return_value = '<folder></folder>'

        cli_folder.config(
            folder='my-folder',
            filepath=None,
            opt_pretty=False,
            opt_yaml=False,
            opt_xml=False,
            opt_toml=False,
            opt_json=False,
            **PROFILE_TOKEN,
        )
        mock_stdout.assert_called_once()


# ============================================================================
# Additional cli_stage tests for uncovered branches
# ============================================================================


class TestCliStageHandlersExtended:
    @patch('yojenkins.cli.cli_stage.print2')
    @patch('yojenkins.cli.cli_stage.cu.config_yo_jenkins')
    @patch('yojenkins.cli.cli_stage.cu.is_full_url', return_value=False)
    def test_stage_status_success(self, mock_is_url, mock_config, mock_print2):
        mock_yj = _mock_yj()
        mock_config.return_value = mock_yj
        mock_yj.stage.status_text.return_value = 'SUCCESS'

        cli_stage.status(name='Build', job='my-job', number=1, url=None, latest=False, **PROFILE_TOKEN)
        mock_print2.assert_called_with('SUCCESS', bold=True, color='green')

    @patch('yojenkins.cli.cli_stage.print2')
    @patch('yojenkins.cli.cli_stage.cu.config_yo_jenkins')
    @patch('yojenkins.cli.cli_stage.cu.is_full_url', return_value=False)
    def test_stage_status_failure(self, mock_is_url, mock_config, mock_print2):
        mock_yj = _mock_yj()
        mock_config.return_value = mock_yj
        mock_yj.stage.status_text.return_value = 'FAILURE'

        cli_stage.status(name='Build', job='my-job', number=1, url=None, latest=False, **PROFILE_TOKEN)
        mock_print2.assert_called_with('FAILURE', bold=True, color='red')

    @patch('yojenkins.cli.cli_stage.print2')
    @patch('yojenkins.cli.cli_stage.cu.config_yo_jenkins')
    @patch('yojenkins.cli.cli_stage.cu.is_full_url', return_value=False)
    def test_stage_status_unknown(self, mock_is_url, mock_config, mock_print2):
        mock_yj = _mock_yj()
        mock_config.return_value = mock_yj
        mock_yj.stage.status_text.return_value = 'UNKNOWN'

        cli_stage.status(name='Build', job='my-job', number=1, url=None, latest=False, **PROFILE_TOKEN)
        mock_print2.assert_called_with('UNKNOWN', bold=True, color='black')

    @patch('yojenkins.cli.cli_stage.print2')
    @patch('yojenkins.cli.cli_stage.cu.config_yo_jenkins')
    def test_stage_status_with_url(self, mock_config, mock_print2):
        mock_yj = _mock_yj()
        mock_config.return_value = mock_yj
        mock_yj.stage.status_text.return_value = 'SUCCESS'

        cli_stage.status(
            name='Build', job=None, number=None, url='http://j:8080/job/my-job/1/', latest=False, **PROFILE_TOKEN
        )
        mock_yj.stage.status_text.assert_called_once()

    @patch('yojenkins.cli.cli_stage.cu.standard_out')
    @patch('yojenkins.cli.cli_stage.cu.config_yo_jenkins')
    def test_stage_info_with_url(self, mock_config, mock_stdout):
        mock_yj = _mock_yj()
        mock_config.return_value = mock_yj
        mock_yj.stage.info.return_value = {'name': 'Build'}

        cli_stage.info(
            name='Build',
            job=None,
            number=None,
            url='http://j:8080/job/my-job/1/',
            latest=False,
            **PROFILE_TOKEN,
            **COMMON_KWARGS,
        )
        mock_yj.stage.info.assert_called_once()

    @patch('yojenkins.cli.cli_stage.cu.standard_out')
    @patch('yojenkins.cli.cli_stage.cu.config_yo_jenkins')
    def test_stage_steps_with_url(self, mock_config, mock_stdout):
        mock_yj = _mock_yj()
        mock_config.return_value = mock_yj
        mock_yj.stage.step_list.return_value = ([{'name': 'step1'}], ['step1'])

        cli_stage.steps(
            name='Build',
            job=None,
            number=None,
            url='http://j:8080/job/my-job/1/',
            latest=False,
            opt_list=True,
            **PROFILE_TOKEN,
            **COMMON_KWARGS,
        )
        call_args = mock_stdout.call_args[0]
        assert call_args[0] == ['step1']

    @patch('yojenkins.cli.cli_stage.cu.config_yo_jenkins')
    def test_stage_logs_with_url(self, mock_config):
        mock_yj = _mock_yj()
        mock_config.return_value = mock_yj

        cli_stage.logs(
            name='Build',
            job=None,
            number=None,
            url='http://j:8080/job/my-job/1/',
            latest=False,
            download_dir=None,
            **PROFILE_TOKEN,
        )
        mock_yj.stage.logs.assert_called_once()

    @patch('yojenkins.cli.cli_stage.fail_out', side_effect=SystemExit(1))
    def test_stage_status_missing_number_and_latest_exits(self, mock_fail):
        with pytest.raises(SystemExit):
            cli_stage.status(name='Build', job='my-job', number=None, url=None, latest=False, **PROFILE_TOKEN)

    @patch('yojenkins.cli.cli_stage.fail_out', side_effect=SystemExit(1))
    def test_stage_steps_missing_number_and_latest_exits(self, mock_fail):
        with pytest.raises(SystemExit):
            cli_stage.steps(
                name='Build',
                job='my-job',
                number=None,
                url=None,
                latest=False,
                opt_list=False,
                **PROFILE_TOKEN,
                **COMMON_KWARGS,
            )

    @patch('yojenkins.cli.cli_stage.fail_out', side_effect=SystemExit(1))
    def test_stage_logs_missing_number_and_latest_exits(self, mock_fail):
        with pytest.raises(SystemExit):
            cli_stage.logs(
                name='Build', job='my-job', number=None, url=None, latest=False, download_dir=None, **PROFILE_TOKEN
            )


# ============================================================================
# Additional cli_auth tests for uncovered branches
# ============================================================================


class TestCliAuthHandlersExtended:
    @patch('click.secho')
    @patch('yojenkins.cli.cli_auth.Auth')
    def test_auth_token_with_profile(self, mock_auth_cls, mock_secho):
        mock_auth = MagicMock()
        mock_auth.profile_add_new_token.return_value = 'new-token'
        mock_auth_cls.return_value = mock_auth

        cli_auth.token(
            profile='default', token=None, name='my-token', server_base_url=None, username=None, password='pass'
        )
        mock_auth.profile_add_new_token.assert_called_once()
        mock_secho.assert_called_with('success', fg='bright_green', bold=True)

    @patch('click.secho')
    @patch('yojenkins.cli.cli_auth.Auth')
    def test_auth_token_without_profile(self, mock_auth_cls, mock_secho):
        mock_auth = MagicMock()
        mock_auth.generate_token.return_value = 'generated-token'
        mock_auth_cls.return_value = mock_auth

        cli_auth.token(
            profile=None,
            token=None,
            name='my-token',
            server_base_url='http://localhost:8080',
            username='admin',
            password='pass',
        )
        mock_auth.generate_token.assert_called_once()
        mock_secho.assert_called_with('generated-token', fg='bright_green', bold=True)

    @patch('click.secho')
    @patch('builtins.print')
    @patch('yojenkins.cli.cli_auth.Auth')
    def test_auth_token_without_profile_ignores_token_flag(self, mock_auth_cls, mock_print, mock_secho):
        mock_auth = MagicMock()
        mock_auth.generate_token.return_value = 'generated-token'
        mock_auth_cls.return_value = mock_auth

        cli_auth.token(
            profile=None,
            token='some-token',
            name='my-token',
            server_base_url='http://localhost:8080',
            username='admin',
            password='pass',
        )
        mock_auth.generate_token.assert_called_once()


# ============================================================================
# Additional cli_credential tests for uncovered branches
# ============================================================================


class TestCliCredentialHandlersExtended:
    @patch('yojenkins.cli.cli_credential.cu.standard_out')
    @patch('yojenkins.cli.cli_credential.cu.config_yo_jenkins')
    def test_credential_config(self, mock_config, mock_stdout):
        mock_yj = _mock_yj()
        mock_config.return_value = mock_yj
        mock_yj.credential.config.return_value = '<credential></credential>'

        cli_credential.config(
            credential='cred-1',
            folder='/',
            domain='_',
            filepath=None,
            opt_pretty=False,
            opt_yaml=False,
            opt_xml=False,
            opt_toml=False,
            opt_json=False,
            **PROFILE_TOKEN,
        )
        mock_stdout.assert_called_once()

    @patch('yojenkins.cli.cli_credential.cu.standard_out')
    @patch('yojenkins.cli.cli_credential.cu.config_yo_jenkins')
    def test_credential_get_template(self, mock_config, mock_stdout):
        mock_yj = _mock_yj()
        mock_config.return_value = mock_yj
        mock_yj.credential.get_template.return_value = '<template></template>'

        cli_credential.get_template(
            type='secret-text',
            filepath=None,
            opt_pretty=False,
            opt_yaml=False,
            opt_xml=False,
            opt_toml=False,
            opt_json=False,
            **PROFILE_TOKEN,
        )
        mock_stdout.assert_called_once()


# ============================================================================
# Additional cli_node tests for uncovered branches
# ============================================================================


class TestCliNodeHandlersExtended:
    @patch('click.secho')
    @patch('yojenkins.cli.cli_node.cu.config_yo_jenkins')
    def test_node_create_permanent(self, mock_config, mock_secho):
        mock_yj = _mock_yj()
        mock_config.return_value = mock_yj

        cli_node.create_permanent(name='my-node', host='192.168.1.1', credential='ssh-cred', **PROFILE_TOKEN)
        mock_yj.node.create_permanent.assert_called_once()

    @patch('yojenkins.cli.cli_node.cu.standard_out')
    @patch('yojenkins.cli.cli_node.cu.config_yo_jenkins')
    def test_node_config(self, mock_config, mock_stdout):
        mock_yj = _mock_yj()
        mock_config.return_value = mock_yj
        mock_yj.node.config.return_value = '<node></node>'

        cli_node.config(
            name='my-node',
            filepath=None,
            opt_pretty=False,
            opt_yaml=False,
            opt_xml=False,
            opt_toml=False,
            opt_json=False,
            **PROFILE_TOKEN,
        )
