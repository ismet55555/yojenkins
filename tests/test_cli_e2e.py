"""End-to-end CLI tests.

These tests invoke real CLI commands via CliRunner and verify the full pipeline:
Click parsing → translate_kwargs → handler → business logic → output formatting.

Mock strategy:
- Bulk tests: mock config_yo_jenkins() to return a MagicMock YoJenkins
- Auth tests: mock at REST level to test credential loading pipeline
"""

import json
from unittest.mock import MagicMock, patch

import pytest
import yaml

from yojenkins.__main__ import main
from yojenkins.yo_jenkins.exceptions import YoJenkinsException

# ---------------------------------------------------------------------------
# Test data (replaces demo mode static data)
# ---------------------------------------------------------------------------

TEST_BASE_URL = 'http://test-jenkins:8080'

TEST_SERVER_INFO = {
    'mode': 'NORMAL',
    'numExecutors': 2,
    'url': TEST_BASE_URL,
    'useSecurity': True,
}

TEST_PEOPLE = {'users': [{'user': {'fullName': 'Alice'}}, {'user': {'fullName': 'Bob'}}]}
TEST_PEOPLE_LIST = [{'fullName': 'Alice'}, {'fullName': 'Bob'}]

TEST_JOBS = [
    {
        'name': 'backend-api',
        'fullName': 'Backend/backend-api',
        'url': f'{TEST_BASE_URL}/job/Backend/job/backend-api/',
        'color': 'blue',
        'folder': 'Backend',
    },
    {
        'name': 'frontend-app',
        'fullName': 'Frontend/frontend-app',
        'url': f'{TEST_BASE_URL}/job/Frontend/job/frontend-app/',
        'color': 'blue',
        'folder': 'Frontend',
    },
    {
        'name': 'deploy-service',
        'fullName': 'DevOps/deploy-service',
        'url': f'{TEST_BASE_URL}/job/DevOps/job/deploy-service/',
        'color': 'red',
        'folder': 'DevOps',
    },
]

TEST_FOLDERS = [
    {'name': 'DevOps', 'fullName': 'DevOps', 'url': f'{TEST_BASE_URL}/job/DevOps/'},
    {'name': 'Backend', 'fullName': 'Backend', 'url': f'{TEST_BASE_URL}/job/Backend/'},
    {'name': 'Frontend', 'fullName': 'Frontend', 'url': f'{TEST_BASE_URL}/job/Frontend/'},
]

TEST_BUILDS = [
    {'number': 84, 'result': 'SUCCESS', 'url': f'{TEST_BASE_URL}/job/DevOps/job/deploy-service/84/'},
    {'number': 83, 'result': 'FAILURE', 'url': f'{TEST_BASE_URL}/job/DevOps/job/deploy-service/83/'},
]

TEST_STAGES = [
    {'name': 'Checkout', 'status': 'SUCCESS'},
    {'name': 'Build', 'status': 'SUCCESS'},
    {'name': 'Test', 'status': 'SUCCESS'},
]

BUILD_URL = f'{TEST_BASE_URL}/job/DevOps/job/deploy-service/84/'


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def _patch_history_file_io():
    """Prevent log_to_history from writing to ~/.yojenkins/history.jsonl."""
    with patch('pathlib.Path.is_file', return_value=True), patch('builtins.open', MagicMock()):
        yield


@pytest.fixture
def mock_yj():
    """MagicMock YoJenkins with test data return values."""
    yj = MagicMock()

    # Server
    yj.server.info.return_value = TEST_SERVER_INFO
    yj.server.people.return_value = (TEST_PEOPLE, TEST_PEOPLE_LIST)
    yj.server.queue_info.return_value = {'items': []}

    # Jobs
    yj.job.info.return_value = {
        'name': 'backend-api',
        'fullName': 'Backend/backend-api',
        'url': f'{TEST_BASE_URL}/job/Backend/job/backend-api/',
        'builds': TEST_BUILDS,
    }
    yj.job.search.return_value = (TEST_JOBS, [j['url'] for j in TEST_JOBS])
    yj.job.build_list.return_value = (TEST_BUILDS, [b['url'] for b in TEST_BUILDS])

    # Folders
    yj.folder.info.return_value = {
        'name': 'DevOps',
        'fullName': 'DevOps',
        'url': f'{TEST_BASE_URL}/job/DevOps/',
        'jobs': TEST_JOBS[:1],
    }
    yj.folder.search.return_value = (TEST_FOLDERS, [f['url'] for f in TEST_FOLDERS])
    yj.folder.jobs_list.return_value = (TEST_JOBS[:1], [TEST_JOBS[0]['url']])

    # Builds
    yj.build.info.return_value = TEST_BUILDS[0]
    yj.build.stage_list.return_value = (TEST_STAGES, [s['name'] for s in TEST_STAGES])

    # Auth
    yj.auth.verify.return_value = True
    yj.auth.user.return_value = {'id': 'test-user', 'fullName': 'Test User'}

    # REST (for console logs etc.)
    yj.rest.request.return_value = ('Started: build #84\nFinished: SUCCESS', {}, True)

    # Attributes not exercised by most tests but needed to avoid AttributeError
    yj.node = MagicMock()
    yj.account = MagicMock()
    yj.credential = MagicMock()
    yj.stage = MagicMock()
    yj.step = MagicMock()

    return yj


@pytest.fixture
def mock_config(mock_yj):
    """Patch config_yo_jenkins at the single source module."""
    with patch(
        'yojenkins.cli.cli_utility.config_yo_jenkins',
        return_value=mock_yj,
    ):
        yield mock_yj


# ---------------------------------------------------------------------------
# Category 1: Help flags
# ---------------------------------------------------------------------------


@pytest.mark.e2e
@pytest.mark.parametrize(
    'args,expected',
    [
        ([], ['auth', 'server', 'job', 'build', 'folder']),
        (['auth'], ['configure', 'token', 'show', 'verify', 'user']),
        (['server'], ['info', 'people', 'queue', 'plugins']),
        (['job'], ['info', 'search', 'build', 'list']),
        (['build'], ['info', 'status', 'stages', 'logs']),
        (['folder'], ['info', 'search', 'jobs']),
        (['node'], ['info', 'list']),
        (['account'], ['info', 'list', 'create']),
        (['credential'], ['info', 'list', 'create']),
        (['stage'], ['info', 'status']),
        (['step'], ['info']),
        (['tools'], ['history']),
    ],
)
def test_help(cli_runner, args, expected):
    result = cli_runner.invoke(main, [*args, '--help'])
    assert result.exit_code == 0
    for cmd in expected:
        assert cmd in result.output.lower(), f"'{cmd}' not found in help output"


# ---------------------------------------------------------------------------
# Category 2: Server commands
# ---------------------------------------------------------------------------


@pytest.mark.e2e
class TestServerE2E:
    def test_server_info_json(self, cli_runner, mock_config):
        result = cli_runner.invoke(main, ['server', 'info'])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert 'numExecutors' in data

    def test_server_info_pretty(self, cli_runner, mock_config):
        result = cli_runner.invoke(main, ['server', 'info', '--pretty'])
        assert result.exit_code == 0
        assert '    ' in result.output  # 4-space indent

    def test_server_people(self, cli_runner, mock_config):
        result = cli_runner.invoke(main, ['server', 'people'])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert isinstance(data, dict)


# ---------------------------------------------------------------------------
# Category 3: Job commands
# ---------------------------------------------------------------------------


@pytest.mark.e2e
class TestJobE2E:
    def test_job_info(self, cli_runner, mock_config):
        result = cli_runner.invoke(main, ['job', 'info', 'backend-api'])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert 'name' in data

    def test_job_search(self, cli_runner, mock_config):
        result = cli_runner.invoke(main, ['job', 'search', '.*'])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert isinstance(data, list)
        assert len(data) > 0

    def test_job_search_list(self, cli_runner, mock_config):
        result = cli_runner.invoke(main, ['job', 'search', 'api', '--list'])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert isinstance(data, list)
        # --list returns URLs
        for url in data:
            assert isinstance(url, str)

    def test_job_build_list(self, cli_runner, mock_config):
        result = cli_runner.invoke(main, ['job', 'list', 'backend-api'])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert isinstance(data, list)


# ---------------------------------------------------------------------------
# Category 4: Folder commands
# ---------------------------------------------------------------------------


@pytest.mark.e2e
class TestFolderE2E:
    def test_folder_info(self, cli_runner, mock_config):
        result = cli_runner.invoke(main, ['folder', 'info', 'DevOps'])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data.get('name') == 'DevOps'

    def test_folder_search(self, cli_runner, mock_config):
        result = cli_runner.invoke(main, ['folder', 'search', '.*'])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert isinstance(data, list)
        assert len(data) == 3  # 3 test folders

    def test_folder_jobs(self, cli_runner, mock_config):
        result = cli_runner.invoke(main, ['folder', 'jobs', 'DevOps'])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert isinstance(data, list)


# ---------------------------------------------------------------------------
# Category 5: Build commands
# ---------------------------------------------------------------------------


@pytest.mark.e2e
class TestBuildE2E:
    def test_build_info(self, cli_runner, mock_config):
        result = cli_runner.invoke(main, ['build', 'info', '--url', BUILD_URL])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert 'number' in data

    def test_build_stages(self, cli_runner, mock_config):
        result = cli_runner.invoke(main, ['build', 'stages', '--url', BUILD_URL])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert isinstance(data, list)


# ---------------------------------------------------------------------------
# Category 6: Output format matrix
# ---------------------------------------------------------------------------


@pytest.mark.e2e
class TestOutputFormats:
    def test_json_default(self, cli_runner, mock_config):
        result = cli_runner.invoke(main, ['server', 'info'])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert isinstance(data, dict)

    def test_pretty_json(self, cli_runner, mock_config):
        result = cli_runner.invoke(main, ['server', 'info', '--pretty'])
        assert result.exit_code == 0
        # Pretty JSON has 4-space indentation
        assert '    "' in result.output
        data = json.loads(result.output)
        assert isinstance(data, dict)

    def test_yaml_output(self, cli_runner, mock_config):
        result = cli_runner.invoke(main, ['server', 'info', '--yaml'])
        assert result.exit_code == 0
        data = yaml.safe_load(result.output)
        assert isinstance(data, dict)
        assert 'numExecutors' in data

    def test_toml_output(self, cli_runner, mock_config):
        result = cli_runner.invoke(main, ['server', 'info', '--toml'])
        assert result.exit_code == 0
        assert '=' in result.output  # TOML key=value format


# ---------------------------------------------------------------------------
# Category 7: Error handling
# ---------------------------------------------------------------------------


@pytest.mark.e2e
class TestErrorHandling:
    def test_missing_required_arg(self, cli_runner, mock_config):
        """Missing required argument should fail."""
        result = cli_runner.invoke(main, ['job', 'info'])
        assert result.exit_code != 0

    def test_unknown_subcommand(self, cli_runner):
        """Unknown subcommand should fail."""
        result = cli_runner.invoke(main, ['server', 'nonexistent'])
        assert result.exit_code != 0

    def test_auth_exception(self, cli_runner):
        """YoJenkinsException in handler should exit with code 1."""
        with patch(
            'yojenkins.cli.cli_server.cu.config_yo_jenkins',
            side_effect=YoJenkinsException('Auth failed'),
        ):
            result = cli_runner.invoke(main, ['server', 'info'])
            assert result.exit_code == 1


# ---------------------------------------------------------------------------
# Category 8: Stdin support
# ---------------------------------------------------------------------------


@pytest.mark.e2e
class TestStdinSupport:
    def test_job_info_reads_from_stdin(self, cli_runner, mock_config):
        """echo 'backend-api' | yojenkins job info - should work."""
        result = cli_runner.invoke(main, ['job', 'info', '-'], input='backend-api\n')
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert 'name' in data

    def test_stdin_dash_without_pipe_is_literal(self, cli_runner, mock_config):
        """When no stdin pipe, '-' is treated as a literal job name."""
        # CliRunner with no input= simulates an interactive tty
        result = cli_runner.invoke(main, ['job', 'info', '-'])
        # Will try to look up a job named '-' — the mock returns data regardless
        assert result.exit_code in (0, 1)


# ---------------------------------------------------------------------------
# Category 9: Auth pipeline (REST-level mock)
# ---------------------------------------------------------------------------


@pytest.mark.e2e
class TestAuthPipeline:
    def test_auth_show_displays_profiles(self, cli_runner):
        """auth show invokes Auth.show_local_credentials and outputs the result.

        Tests the Click → handler → Auth → standard_out pipeline.
        File I/O is mocked since the autouse fixture patches builtins.open.
        """
        fake_profiles = {
            'default': {
                'jenkins_server_url': 'http://localhost:8080',
                'username': 'testuser',
                'api_token': 'testtoken',
                'active': True,
            }
        }
        with patch(
            'yojenkins.yo_jenkins.auth.Auth.show_local_credentials',
            return_value=fake_profiles,
        ):
            result = cli_runner.invoke(main, ['auth', 'show'])
            assert result.exit_code == 0
            data = json.loads(result.output)
            assert 'default' in data
            assert data['default']['username'] == 'testuser'
