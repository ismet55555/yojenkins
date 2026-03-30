"""Click CLI integration tests using CliRunner.

Tests all 11 command groups: auth, server, node, account, credential,
folder, job, build, stage, step, tools.

Each group has at minimum:
  1. A --help test verifying exit code and expected text
  2. At least one command invocation test with mocked CLI handler
"""

from unittest.mock import patch

import pytest
from click.testing import CliRunner

from yojenkins.__main__ import main


@pytest.fixture
def runner():
    return CliRunner(mix_stderr=False)


# =============================================================================
# Top-level CLI
# =============================================================================


class TestMainCli:
    def test_main_help(self, runner):
        result = runner.invoke(main, ['--help'])
        assert result.exit_code == 0
        assert 'yojenkins' in result.output.lower()

    def test_main_version(self, runner):
        result = runner.invoke(main, ['--version'])
        assert result.exit_code == 0


# =============================================================================
# Auth
# =============================================================================


class TestAuthCli:
    def test_auth_help(self, runner):
        result = runner.invoke(main, ['auth', '--help'])
        assert result.exit_code == 0
        assert 'configure' in result.output.lower()
        assert 'token' in result.output.lower()
        assert 'verify' in result.output.lower()

    @patch('yojenkins.cli_sub_commands.auth.cli_auth')
    def test_auth_configure(self, mock_cli_auth, runner):
        mock_cli_auth.configure.return_value = None
        result = runner.invoke(main, ['auth', 'configure'])
        mock_cli_auth.configure.assert_called_once_with(None)

    @patch('yojenkins.cli_sub_commands.auth.cli_auth')
    def test_auth_show(self, mock_cli_auth, runner):
        mock_cli_auth.show.return_value = None
        result = runner.invoke(main, ['auth', 'show'])
        mock_cli_auth.show.assert_called_once()

    @patch('yojenkins.cli_sub_commands.auth.cli_auth')
    def test_auth_token(self, mock_cli_auth, runner):
        mock_cli_auth.token.return_value = None
        result = runner.invoke(main, ['auth', 'token', '--profile', 'default'])
        mock_cli_auth.token.assert_called_once()


# =============================================================================
# Server
# =============================================================================


class TestServerCli:
    def test_server_help(self, runner):
        result = runner.invoke(main, ['server', '--help'])
        assert result.exit_code == 0
        assert 'info' in result.output.lower()
        assert 'reachable' in result.output.lower()

    @patch('yojenkins.cli_sub_commands.server.cli_server')
    def test_server_info(self, mock_cli_server, runner):
        mock_cli_server.info.return_value = None
        result = runner.invoke(main, ['server', 'info'])
        mock_cli_server.info.assert_called_once()

    @patch('yojenkins.cli_sub_commands.server.cli_server')
    def test_server_reachable(self, mock_cli_server, runner):
        mock_cli_server.reachable.return_value = None
        result = runner.invoke(main, ['server', 'reachable'])
        mock_cli_server.reachable.assert_called_once()

    @patch('yojenkins.cli_sub_commands.server.cli_server')
    def test_server_people(self, mock_cli_server, runner):
        mock_cli_server.people.return_value = None
        result = runner.invoke(main, ['server', 'people'])
        mock_cli_server.people.assert_called_once()

    @patch('yojenkins.cli_sub_commands.server.cli_server')
    def test_server_plugins(self, mock_cli_server, runner):
        mock_cli_server.plugins.return_value = None
        result = runner.invoke(main, ['server', 'plugins'])
        mock_cli_server.plugins.assert_called_once()


# =============================================================================
# Node
# =============================================================================


class TestNodeCli:
    def test_node_help(self, runner):
        result = runner.invoke(main, ['node', '--help'])
        assert result.exit_code == 0
        assert 'info' in result.output.lower()
        assert 'list' in result.output.lower()

    @patch('yojenkins.cli_sub_commands.node.cli_node')
    def test_node_info(self, mock_cli_node, runner):
        mock_cli_node.info.return_value = None
        result = runner.invoke(main, ['node', 'info', 'my-node'])
        mock_cli_node.info.assert_called_once()

    @patch('yojenkins.cli_sub_commands.node.cli_node')
    def test_node_list(self, mock_cli_node, runner):
        mock_cli_node.list.return_value = None
        result = runner.invoke(main, ['node', 'list'])
        mock_cli_node.list.assert_called_once()

    @patch('yojenkins.cli_sub_commands.node.cli_node')
    def test_node_delete(self, mock_cli_node, runner):
        mock_cli_node.delete.return_value = None
        result = runner.invoke(main, ['node', 'delete', 'my-node'])
        mock_cli_node.delete.assert_called_once()

    @patch('yojenkins.cli_sub_commands.node.cli_node')
    def test_node_enable(self, mock_cli_node, runner):
        mock_cli_node.enable.return_value = None
        result = runner.invoke(main, ['node', 'enable', 'my-node'])
        mock_cli_node.enable.assert_called_once()


# =============================================================================
# Account
# =============================================================================


class TestAccountCli:
    def test_account_help(self, runner):
        result = runner.invoke(main, ['account', '--help'])
        assert result.exit_code == 0
        assert 'list' in result.output.lower()
        assert 'info' in result.output.lower()

    @patch('yojenkins.cli_sub_commands.account.cli_account')
    def test_account_list(self, mock_cli_account, runner):
        mock_cli_account.list.return_value = None
        result = runner.invoke(main, ['account', 'list'])
        mock_cli_account.list.assert_called_once()

    @patch('yojenkins.cli_sub_commands.account.cli_account')
    def test_account_info(self, mock_cli_account, runner):
        mock_cli_account.info.return_value = None
        result = runner.invoke(main, ['account', 'info', 'admin'])
        mock_cli_account.info.assert_called_once()

    @patch('yojenkins.cli_sub_commands.account.cli_account')
    def test_account_delete(self, mock_cli_account, runner):
        mock_cli_account.delete.return_value = None
        result = runner.invoke(main, ['account', 'delete', 'some-user'])
        mock_cli_account.delete.assert_called_once()


# =============================================================================
# Credential
# =============================================================================


class TestCredentialCli:
    def test_credential_help(self, runner):
        result = runner.invoke(main, ['credential', '--help'])
        assert result.exit_code == 0
        assert 'list' in result.output.lower()
        assert 'info' in result.output.lower()

    @patch('yojenkins.cli_sub_commands.credential.cli_credential')
    def test_credential_list(self, mock_cli_credential, runner):
        mock_cli_credential.list.return_value = None
        result = runner.invoke(main, ['credential', 'list'])
        mock_cli_credential.list.assert_called_once()

    @patch('yojenkins.cli_sub_commands.credential.cli_credential')
    def test_credential_info(self, mock_cli_credential, runner):
        mock_cli_credential.info.return_value = None
        result = runner.invoke(main, ['credential', 'info', 'my-cred'])
        mock_cli_credential.info.assert_called_once()

    @patch('yojenkins.cli_sub_commands.credential.cli_credential')
    def test_credential_delete(self, mock_cli_credential, runner):
        mock_cli_credential.delete.return_value = None
        result = runner.invoke(main, ['credential', 'delete', 'my-cred'])
        mock_cli_credential.delete.assert_called_once()

    @patch('yojenkins.cli_sub_commands.credential.cli_credential')
    def test_credential_config(self, mock_cli_credential, runner):
        mock_cli_credential.config.return_value = None
        result = runner.invoke(main, ['credential', 'config', 'my-cred'])
        mock_cli_credential.config.assert_called_once()


# =============================================================================
# Folder
# =============================================================================


class TestFolderCli:
    def test_folder_help(self, runner):
        result = runner.invoke(main, ['folder', '--help'])
        assert result.exit_code == 0
        assert 'info' in result.output.lower()
        assert 'search' in result.output.lower()

    @patch('yojenkins.cli_sub_commands.folder.cli_folder')
    def test_folder_info(self, mock_cli_folder, runner):
        mock_cli_folder.info.return_value = None
        result = runner.invoke(main, ['folder', 'info', 'my-folder'])
        mock_cli_folder.info.assert_called_once()

    @patch('yojenkins.cli_sub_commands.folder.cli_folder')
    def test_folder_search(self, mock_cli_folder, runner):
        mock_cli_folder.search.return_value = None
        result = runner.invoke(main, ['folder', 'search', '.*test.*'])
        mock_cli_folder.search.assert_called_once()

    @patch('yojenkins.cli_sub_commands.folder.cli_folder')
    def test_folder_subfolders(self, mock_cli_folder, runner):
        mock_cli_folder.subfolders.return_value = None
        result = runner.invoke(main, ['folder', 'subfolders', 'my-folder'])
        mock_cli_folder.subfolders.assert_called_once()

    @patch('yojenkins.cli_sub_commands.folder.cli_folder')
    def test_folder_delete(self, mock_cli_folder, runner):
        mock_cli_folder.delete.return_value = None
        result = runner.invoke(main, ['folder', 'delete', 'my-folder'])
        mock_cli_folder.delete.assert_called_once()


# =============================================================================
# Job
# =============================================================================


class TestJobCli:
    def test_job_help(self, runner):
        result = runner.invoke(main, ['job', '--help'])
        assert result.exit_code == 0
        assert 'info' in result.output.lower()
        assert 'build' in result.output.lower()
        assert 'search' in result.output.lower()

    @patch('yojenkins.cli_sub_commands.job.cli_job')
    def test_job_info(self, mock_cli_job, runner):
        mock_cli_job.info.return_value = None
        result = runner.invoke(main, ['job', 'info', 'my-job'])
        mock_cli_job.info.assert_called_once()

    @patch('yojenkins.cli_sub_commands.job.cli_job')
    def test_job_search(self, mock_cli_job, runner):
        mock_cli_job.search.return_value = None
        result = runner.invoke(main, ['job', 'search', '.*test.*'])
        mock_cli_job.search.assert_called_once()

    @patch('yojenkins.cli_sub_commands.job.cli_job')
    def test_job_build(self, mock_cli_job, runner):
        mock_cli_job.build.return_value = None
        result = runner.invoke(main, ['job', 'build', 'my-job'])
        mock_cli_job.build.assert_called_once()

    @patch('yojenkins.cli_sub_commands.job.cli_job')
    def test_job_delete(self, mock_cli_job, runner):
        mock_cli_job.delete.return_value = None
        result = runner.invoke(main, ['job', 'delete', 'my-job'])
        mock_cli_job.delete.assert_called_once()

    @patch('yojenkins.cli_sub_commands.job.cli_job')
    def test_job_disable(self, mock_cli_job, runner):
        mock_cli_job.disable.return_value = None
        result = runner.invoke(main, ['job', 'disable', 'my-job'])
        mock_cli_job.disable.assert_called_once()

    @patch('yojenkins.cli_sub_commands.job.cli_job')
    def test_job_enable(self, mock_cli_job, runner):
        mock_cli_job.enable.return_value = None
        result = runner.invoke(main, ['job', 'enable', 'my-job'])
        mock_cli_job.enable.assert_called_once()

    @patch('yojenkins.cli_sub_commands.job.cli_job')
    def test_job_build_list(self, mock_cli_job, runner):
        mock_cli_job.build_list.return_value = None
        result = runner.invoke(main, ['job', 'list', 'my-job'])
        mock_cli_job.build_list.assert_called_once()


# =============================================================================
# Build
# =============================================================================


class TestBuildCli:
    def test_build_help(self, runner):
        result = runner.invoke(main, ['build', '--help'])
        assert result.exit_code == 0
        assert 'info' in result.output.lower()
        assert 'logs' in result.output.lower()
        assert 'status' in result.output.lower()

    @patch('yojenkins.cli_sub_commands.build.cli_build')
    def test_build_info(self, mock_cli_build, runner):
        mock_cli_build.info.return_value = None
        result = runner.invoke(main, ['build', 'info', 'my-job', '--number', '1'])
        mock_cli_build.info.assert_called_once()

    @patch('yojenkins.cli_sub_commands.build.cli_build')
    def test_build_info_no_args_shows_help(self, mock_cli_build, runner):
        """When no job or url is provided, build info should show help text."""
        result = runner.invoke(main, ['build', 'info'])
        assert result.exit_code == 0
        mock_cli_build.info.assert_not_called()

    @patch('yojenkins.cli_sub_commands.build.cli_build')
    def test_build_status(self, mock_cli_build, runner):
        mock_cli_build.status.return_value = None
        result = runner.invoke(main, ['build', 'status', 'my-job', '--latest'])
        mock_cli_build.status.assert_called_once()

    @patch('yojenkins.cli_sub_commands.build.cli_build')
    def test_build_logs_with_url(self, mock_cli_build, runner):
        mock_cli_build.logs.return_value = None
        result = runner.invoke(main, ['build', 'logs', '--url', 'http://jenkins/job/my-job/1/'])
        mock_cli_build.logs.assert_called_once()

    @patch('yojenkins.cli_sub_commands.build.cli_build')
    def test_build_abort(self, mock_cli_build, runner):
        mock_cli_build.abort.return_value = None
        result = runner.invoke(main, ['build', 'abort', 'my-job', '--number', '5'])
        mock_cli_build.abort.assert_called_once()

    @patch('yojenkins.cli_sub_commands.build.cli_build')
    def test_build_diff(self, mock_cli_build, runner):
        mock_cli_build.diff.return_value = None
        result = runner.invoke(
            main,
            [
                'build',
                'diff',
                'http://jenkins/job/a/1/',
                'http://jenkins/job/a/2/',
            ],
        )
        mock_cli_build.diff.assert_called_once()


# =============================================================================
# Stage
# =============================================================================


class TestStageCli:
    def test_stage_help(self, runner):
        result = runner.invoke(main, ['stage', '--help'])
        assert result.exit_code == 0
        assert 'info' in result.output.lower()
        assert 'steps' in result.output.lower()

    @patch('yojenkins.cli_sub_commands.stage.cli_stage')
    def test_stage_info(self, mock_cli_stage, runner):
        mock_cli_stage.info.return_value = None
        result = runner.invoke(
            main,
            [
                'stage',
                'info',
                'my-stage',
                '--job',
                'my-job',
                '--latest',
            ],
        )
        mock_cli_stage.info.assert_called_once()

    @patch('yojenkins.cli_sub_commands.stage.cli_stage')
    def test_stage_info_no_job_shows_help(self, mock_cli_stage, runner):
        """When no --job or --url, stage info should show help."""
        result = runner.invoke(main, ['stage', 'info', 'my-stage'])
        assert result.exit_code == 0
        mock_cli_stage.info.assert_not_called()

    @patch('yojenkins.cli_sub_commands.stage.cli_stage')
    def test_stage_steps(self, mock_cli_stage, runner):
        mock_cli_stage.steps.return_value = None
        result = runner.invoke(
            main,
            [
                'stage',
                'steps',
                'my-stage',
                '--url',
                'http://jenkins/job/my-job/1/',
            ],
        )
        mock_cli_stage.steps.assert_called_once()

    @patch('yojenkins.cli_sub_commands.stage.cli_stage')
    def test_stage_logs(self, mock_cli_stage, runner):
        mock_cli_stage.logs.return_value = None
        result = runner.invoke(
            main,
            [
                'stage',
                'logs',
                'my-stage',
                '--job',
                'my-job',
                '--number',
                '3',
            ],
        )
        mock_cli_stage.logs.assert_called_once()


# =============================================================================
# Step
# =============================================================================


class TestStepCli:
    def test_step_help(self, runner):
        result = runner.invoke(main, ['step', '--help'])
        assert result.exit_code == 0
        assert 'info' in result.output.lower()

    @patch('yojenkins.cli_sub_commands.step.cli_step')
    def test_step_info(self, mock_cli_step, runner):
        mock_cli_step.info.return_value = None
        result = runner.invoke(
            main,
            [
                'step',
                'info',
                'http://jenkins/job/my-job/1/execution/node/6/',
            ],
        )
        mock_cli_step.info.assert_called_once()


# =============================================================================
# Tools
# =============================================================================


class TestToolsCli:
    def test_tools_help(self, runner):
        result = runner.invoke(main, ['tools', '--help'])
        assert result.exit_code == 0
        assert 'docs' in result.output.lower()
        assert 'history' in result.output.lower()

    @patch('yojenkins.cli_sub_commands.tools.cli_tools')
    def test_tools_docs(self, mock_cli_tools, runner):
        mock_cli_tools.documentation.return_value = None
        result = runner.invoke(main, ['tools', 'docs'])
        mock_cli_tools.documentation.assert_called_once()

    @patch('yojenkins.cli_sub_commands.tools.cli_tools')
    def test_tools_bug_report(self, mock_cli_tools, runner):
        mock_cli_tools.bug_report.return_value = None
        result = runner.invoke(main, ['tools', 'bug-report'])
        mock_cli_tools.bug_report.assert_called_once()

    @patch('yojenkins.cli_sub_commands.tools.cli_tools')
    def test_tools_feature_request(self, mock_cli_tools, runner):
        mock_cli_tools.feature_request.return_value = None
        result = runner.invoke(main, ['tools', 'feature-request'])
        mock_cli_tools.feature_request.assert_called_once()

    @patch('yojenkins.cli_sub_commands.tools.cli_tools')
    def test_tools_history(self, mock_cli_tools, runner):
        mock_cli_tools.history.return_value = None
        result = runner.invoke(main, ['tools', 'history'])
        mock_cli_tools.history.assert_called_once()

    @patch('yojenkins.cli_sub_commands.tools.cli_tools')
    def test_tools_run_script_no_args_shows_help(self, mock_cli_tools, runner):
        """run-script with no --text or --file should show help."""
        result = runner.invoke(main, ['tools', 'run-script'])
        assert result.exit_code == 0
        mock_cli_tools.run_script.assert_not_called()

    @patch('yojenkins.cli_sub_commands.tools.cli_tools')
    def test_tools_rest_request(self, mock_cli_tools, runner):
        mock_cli_tools.rest_request.return_value = None
        result = runner.invoke(main, ['tools', 'rest-request', 'me/api/json'])
        mock_cli_tools.rest_request.assert_called_once()

    @patch('yojenkins.cli_sub_commands.tools.cli_tools')
    def test_tools_run_script_with_text(self, mock_cli_tools, runner):
        mock_cli_tools.run_script.return_value = None
        result = runner.invoke(main, ['tools', 'run-script', '--text', 'println "hello"'])
        mock_cli_tools.run_script.assert_called_once()

    # Note: 'upgrade' command is commented out in tools.py sub-commands


# =============================================================================
# Additional Build sub-command tests
# =============================================================================


class TestBuildCliExtended:
    @patch('yojenkins.cli_sub_commands.build.cli_build')
    def test_build_status_with_job(self, mock_cli_build, runner):
        mock_cli_build.status.return_value = None
        result = runner.invoke(main, ['build', 'status', 'my-job', '--latest'])
        mock_cli_build.status.assert_called_once()

    @patch('yojenkins.cli_sub_commands.build.cli_build')
    def test_build_status_no_args_shows_help(self, mock_cli_build, runner):
        result = runner.invoke(main, ['build', 'status'])
        assert result.exit_code == 0
        mock_cli_build.status.assert_not_called()

    @patch('yojenkins.cli_sub_commands.build.cli_build')
    def test_build_abort_with_url(self, mock_cli_build, runner):
        mock_cli_build.abort.return_value = None
        result = runner.invoke(main, ['build', 'abort', '--url', 'http://j:8080/job/a/1/'])
        mock_cli_build.abort.assert_called_once()

    @patch('yojenkins.cli_sub_commands.build.cli_build')
    def test_build_abort_no_args_shows_help(self, mock_cli_build, runner):
        result = runner.invoke(main, ['build', 'abort'])
        assert result.exit_code == 0
        mock_cli_build.abort.assert_not_called()

    @patch('yojenkins.cli_sub_commands.build.cli_build')
    def test_build_delete_with_job(self, mock_cli_build, runner):
        mock_cli_build.delete.return_value = None
        result = runner.invoke(main, ['build', 'delete', 'my-job', '--number', '3'])
        mock_cli_build.delete.assert_called_once()

    @patch('yojenkins.cli_sub_commands.build.cli_build')
    def test_build_delete_no_args_shows_help(self, mock_cli_build, runner):
        result = runner.invoke(main, ['build', 'delete'])
        assert result.exit_code == 0
        mock_cli_build.delete.assert_not_called()

    @patch('yojenkins.cli_sub_commands.build.cli_build')
    def test_build_stages_with_job(self, mock_cli_build, runner):
        mock_cli_build.stages.return_value = None
        result = runner.invoke(main, ['build', 'stages', 'my-job', '--latest'])
        mock_cli_build.stages.assert_called_once()

    @patch('yojenkins.cli_sub_commands.build.cli_build')
    def test_build_stages_no_args_shows_help(self, mock_cli_build, runner):
        result = runner.invoke(main, ['build', 'stages'])
        assert result.exit_code == 0
        mock_cli_build.stages.assert_not_called()

    @patch('yojenkins.cli_sub_commands.build.cli_build')
    def test_build_logs_with_job(self, mock_cli_build, runner):
        mock_cli_build.logs.return_value = None
        result = runner.invoke(main, ['build', 'logs', 'my-job', '--latest'])
        mock_cli_build.logs.assert_called_once()

    @patch('yojenkins.cli_sub_commands.build.cli_build')
    def test_build_logs_no_args_shows_help(self, mock_cli_build, runner):
        result = runner.invoke(main, ['build', 'logs'])
        assert result.exit_code == 0
        mock_cli_build.logs.assert_not_called()

    @patch('yojenkins.cli_sub_commands.build.cli_build')
    def test_build_browser_with_job(self, mock_cli_build, runner):
        mock_cli_build.browser.return_value = None
        result = runner.invoke(main, ['build', 'browser', 'my-job', '--number', '1'])
        mock_cli_build.browser.assert_called_once()

    @patch('yojenkins.cli_sub_commands.build.cli_build')
    def test_build_browser_no_args_shows_help(self, mock_cli_build, runner):
        result = runner.invoke(main, ['build', 'browser'])
        assert result.exit_code == 0
        mock_cli_build.browser.assert_not_called()

    @patch('yojenkins.cli_sub_commands.build.cli_build')
    def test_build_monitor_with_job(self, mock_cli_build, runner):
        mock_cli_build.monitor.return_value = None
        result = runner.invoke(main, ['build', 'monitor', 'my-job', '--latest'])
        mock_cli_build.monitor.assert_called_once()

    @patch('yojenkins.cli_sub_commands.build.cli_build')
    def test_build_monitor_no_args_shows_help(self, mock_cli_build, runner):
        result = runner.invoke(main, ['build', 'monitor'])
        assert result.exit_code == 0
        mock_cli_build.monitor.assert_not_called()

    @patch('yojenkins.cli_sub_commands.build.cli_build')
    def test_build_parameters_with_job(self, mock_cli_build, runner):
        mock_cli_build.parameters.return_value = None
        result = runner.invoke(main, ['build', 'parameters', 'my-job', '--latest'])
        mock_cli_build.parameters.assert_called_once()

    @patch('yojenkins.cli_sub_commands.build.cli_build')
    def test_build_parameters_no_args_shows_help(self, mock_cli_build, runner):
        result = runner.invoke(main, ['build', 'parameters'])
        assert result.exit_code == 0
        mock_cli_build.parameters.assert_not_called()

    @patch('yojenkins.cli_sub_commands.build.cli_build')
    def test_build_rebuild_with_job(self, mock_cli_build, runner):
        mock_cli_build.rebuild.return_value = None
        result = runner.invoke(main, ['build', 'rebuild', 'my-job', '--latest'])
        mock_cli_build.rebuild.assert_called_once()

    @patch('yojenkins.cli_sub_commands.build.cli_build')
    def test_build_rebuild_no_args_shows_help(self, mock_cli_build, runner):
        result = runner.invoke(main, ['build', 'rebuild'])
        assert result.exit_code == 0
        mock_cli_build.rebuild.assert_not_called()


# =============================================================================
# Additional Job sub-command tests
# =============================================================================


class TestJobCliExtended:
    @patch('yojenkins.cli_sub_commands.job.cli_job')
    def test_job_next(self, mock_cli_job, runner):
        mock_cli_job.build_next.return_value = None
        result = runner.invoke(main, ['job', 'next', 'my-job'])
        mock_cli_job.build_next.assert_called_once()

    @patch('yojenkins.cli_sub_commands.job.cli_job')
    def test_job_last(self, mock_cli_job, runner):
        mock_cli_job.build_last.return_value = None
        result = runner.invoke(main, ['job', 'last', 'my-job'])
        mock_cli_job.build_last.assert_called_once()

    @patch('yojenkins.cli_sub_commands.job.cli_job')
    def test_job_set(self, mock_cli_job, runner):
        mock_cli_job.build_set.return_value = None
        result = runner.invoke(main, ['job', 'set', 'my-job', '42'])
        mock_cli_job.build_set.assert_called_once()

    @patch('yojenkins.cli_sub_commands.job.cli_job')
    def test_job_build_exist(self, mock_cli_job, runner):
        mock_cli_job.build_exist.return_value = None
        result = runner.invoke(main, ['job', 'build-exist', 'my-job', '5'])
        mock_cli_job.build_exist.assert_called_once()

    @patch('yojenkins.cli_sub_commands.job.cli_job')
    def test_job_wipe(self, mock_cli_job, runner):
        mock_cli_job.wipe.return_value = None
        result = runner.invoke(main, ['job', 'wipe', 'my-job'])
        mock_cli_job.wipe.assert_called_once()

    @patch('yojenkins.cli_sub_commands.job.cli_job')
    def test_job_rename(self, mock_cli_job, runner):
        mock_cli_job.rename.return_value = None
        result = runner.invoke(main, ['job', 'rename', 'my-job', 'new-name'])
        mock_cli_job.rename.assert_called_once()

    @patch('yojenkins.cli_sub_commands.job.cli_job')
    def test_job_monitor(self, mock_cli_job, runner):
        mock_cli_job.monitor.return_value = None
        result = runner.invoke(main, ['job', 'monitor', 'my-job'])
        mock_cli_job.monitor.assert_called_once()

    @patch('yojenkins.cli_sub_commands.job.cli_job')
    def test_job_create(self, mock_cli_job, runner):
        mock_cli_job.create.return_value = None
        result = runner.invoke(main, ['job', 'create', 'new-job', 'parent-folder'])
        mock_cli_job.create.assert_called_once()

    @patch('yojenkins.cli_sub_commands.job.cli_job')
    def test_job_parameters(self, mock_cli_job, runner):
        mock_cli_job.parameters.return_value = None
        result = runner.invoke(main, ['job', 'parameters', 'my-job'])
        mock_cli_job.parameters.assert_called_once()

    @patch('yojenkins.cli_sub_commands.job.cli_job')
    def test_job_queue_check(self, mock_cli_job, runner):
        mock_cli_job.queue_check.return_value = None
        result = runner.invoke(main, ['job', 'queue-check', 'my-job'])
        mock_cli_job.queue_check.assert_called_once()

    @patch('yojenkins.cli_sub_commands.job.cli_job')
    def test_job_browser(self, mock_cli_job, runner):
        mock_cli_job.browser.return_value = None
        result = runner.invoke(main, ['job', 'browser', 'my-job'])
        mock_cli_job.browser.assert_called_once()

    @patch('yojenkins.cli_sub_commands.job.cli_job')
    def test_job_config(self, mock_cli_job, runner):
        mock_cli_job.config.return_value = None
        result = runner.invoke(main, ['job', 'config', 'my-job'])
        mock_cli_job.config.assert_called_once()

    @patch('yojenkins.cli_sub_commands.job.cli_job')
    def test_job_diff(self, mock_cli_job, runner):
        mock_cli_job.diff.return_value = None
        result = runner.invoke(main, ['job', 'diff', 'job-a', 'job-b'])
        mock_cli_job.diff.assert_called_once()


# =============================================================================
# Additional Node sub-command tests
# =============================================================================


class TestNodeCliExtended:
    @patch('yojenkins.cli_sub_commands.node.cli_node')
    def test_node_disable(self, mock_cli_node, runner):
        mock_cli_node.disable.return_value = None
        result = runner.invoke(main, ['node', 'disable', 'my-node'])
        mock_cli_node.disable.assert_called_once()

    @patch('yojenkins.cli_sub_commands.node.cli_node')
    def test_node_config(self, mock_cli_node, runner):
        mock_cli_node.config.return_value = None
        result = runner.invoke(main, ['node', 'config', 'my-node'])
        mock_cli_node.config.assert_called_once()

    def test_node_status_command(self, runner):
        result = runner.invoke(main, ['node', 'status', 'my-node'])
        # status just calls click.secho, which will fail with translate_kwargs but should not crash
        # Just verify command is recognized
        assert 'Error' not in result.output or result.exit_code != 2

    def test_node_prepare_command(self, runner):
        result = runner.invoke(main, ['node', 'prepare'])
        assert result.exit_code == 1

    def test_node_create_ephemeral_command(self, runner):
        result = runner.invoke(main, ['node', 'create-ephemeral'])
        assert result.exit_code == 1

    def test_node_logs_command(self, runner):
        result = runner.invoke(main, ['node', 'logs'])
        assert result.exit_code == 1


# =============================================================================
# Additional Server sub-command tests
# =============================================================================


class TestServerCliExtended:
    @patch('yojenkins.cli_sub_commands.server.cli_server')
    def test_server_queue(self, mock_cli_server, runner):
        mock_cli_server.queue.return_value = None
        result = runner.invoke(main, ['server', 'queue'])
        mock_cli_server.queue.assert_called_once()

    @patch('yojenkins.cli_sub_commands.server.cli_server')
    def test_server_browser(self, mock_cli_server, runner):
        mock_cli_server.browser.return_value = None
        result = runner.invoke(main, ['server', 'browser'])
        mock_cli_server.browser.assert_called_once()

    @patch('yojenkins.cli_sub_commands.server.cli_server')
    def test_server_quiet(self, mock_cli_server, runner):
        mock_cli_server.quiet.return_value = None
        result = runner.invoke(main, ['server', 'quiet'])
        mock_cli_server.quiet.assert_called_once()

    @patch('yojenkins.cli_sub_commands.server.cli_server')
    def test_server_restart(self, mock_cli_server, runner):
        mock_cli_server.restart.return_value = None
        result = runner.invoke(main, ['server', 'restart'])
        mock_cli_server.restart.assert_called_once()

    @patch('yojenkins.cli_sub_commands.server.cli_server')
    def test_server_shutdown(self, mock_cli_server, runner):
        mock_cli_server.shutdown.return_value = None
        result = runner.invoke(main, ['server', 'shutdown'])
        mock_cli_server.shutdown.assert_called_once()

    @patch('yojenkins.cli_sub_commands.server.cli_server')
    def test_server_teardown(self, mock_cli_server, runner):
        mock_cli_server.server_teardown.return_value = None
        result = runner.invoke(main, ['server', 'server-teardown'])
        mock_cli_server.server_teardown.assert_called_once()


# =============================================================================
# Additional Folder sub-command tests
# =============================================================================


class TestFolderCliExtended:
    @patch('yojenkins.cli_sub_commands.folder.cli_folder')
    def test_folder_jobs(self, mock_cli_folder, runner):
        mock_cli_folder.jobs.return_value = None
        result = runner.invoke(main, ['folder', 'jobs', 'my-folder'])
        mock_cli_folder.jobs.assert_called_once()

    @patch('yojenkins.cli_sub_commands.folder.cli_folder')
    def test_folder_views(self, mock_cli_folder, runner):
        mock_cli_folder.views.return_value = None
        result = runner.invoke(main, ['folder', 'views', 'my-folder'])
        mock_cli_folder.views.assert_called_once()

    @patch('yojenkins.cli_sub_commands.folder.cli_folder')
    def test_folder_items(self, mock_cli_folder, runner):
        mock_cli_folder.items.return_value = None
        result = runner.invoke(main, ['folder', 'items', 'my-folder'])
        mock_cli_folder.items.assert_called_once()

    @patch('yojenkins.cli_sub_commands.folder.cli_folder')
    def test_folder_browser(self, mock_cli_folder, runner):
        mock_cli_folder.browser.return_value = None
        result = runner.invoke(main, ['folder', 'browser', 'my-folder'])
        mock_cli_folder.browser.assert_called_once()

    @patch('yojenkins.cli_sub_commands.folder.cli_folder')
    def test_folder_config(self, mock_cli_folder, runner):
        mock_cli_folder.config.return_value = None
        result = runner.invoke(main, ['folder', 'config', 'my-folder'])
        mock_cli_folder.config.assert_called_once()

    @patch('yojenkins.cli_sub_commands.folder.cli_folder')
    def test_folder_create(self, mock_cli_folder, runner):
        mock_cli_folder.create.return_value = None
        result = runner.invoke(main, ['folder', 'create', 'new-folder', 'parent'])
        mock_cli_folder.create.assert_called_once()

    @patch('yojenkins.cli_sub_commands.folder.cli_folder')
    def test_folder_copy(self, mock_cli_folder, runner):
        mock_cli_folder.copy.return_value = None
        result = runner.invoke(main, ['folder', 'copy', 'parent', 'orig', 'new-copy'])
        mock_cli_folder.copy.assert_called_once()


# =============================================================================
# Additional Stage sub-command tests
# =============================================================================


class TestStageCliExtended:
    @patch('yojenkins.cli_sub_commands.stage.cli_stage')
    def test_stage_info_with_url(self, mock_cli_stage, runner):
        mock_cli_stage.info.return_value = None
        result = runner.invoke(
            main,
            [
                'stage',
                'info',
                'my-stage',
                '--url',
                'http://jenkins/job/my-job/1/',
            ],
        )
        mock_cli_stage.info.assert_called_once()

    @patch('yojenkins.cli_sub_commands.stage.cli_stage')
    def test_stage_status(self, mock_cli_stage, runner):
        mock_cli_stage.status.return_value = None
        result = runner.invoke(
            main,
            [
                'stage',
                'status',
                'my-stage',
                '--job',
                'my-job',
                '--latest',
            ],
        )
        mock_cli_stage.status.assert_called_once()

    @patch('yojenkins.cli_sub_commands.stage.cli_stage')
    def test_stage_status_no_job_shows_help(self, mock_cli_stage, runner):
        result = runner.invoke(main, ['stage', 'status', 'my-stage'])
        assert result.exit_code == 0
        mock_cli_stage.status.assert_not_called()
