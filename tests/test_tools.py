"""Tests for yojenkins/tools/package.py and yojenkins/tools/shared_library.py"""

import subprocess
from unittest.mock import MagicMock, patch

from yojenkins.tools.package import Package
from yojenkins.tools.shared_library import SharedLibrary

# ============================================================================
# Package tests
# ============================================================================


class TestPackageInstall:
    @patch('subprocess.check_call')
    def test_install_default(self, mock_check_call):
        result = Package.install()
        assert result is True
        mock_check_call.assert_called_once()
        args = mock_check_call.call_args[0][0]
        assert 'pip' in args[2]
        assert 'install' in args
        assert '--upgrade' in args
        assert '--user' in args
        assert 'yojenkins' in args

    @patch('subprocess.check_call')
    def test_install_no_upgrade_no_user(self, mock_check_call):
        result = Package.install(upgrade=False, user=False)
        assert result is True
        args = mock_check_call.call_args[0][0]
        assert '--upgrade' not in args
        assert '--user' not in args

    @patch('subprocess.check_call')
    def test_install_with_proxy(self, mock_check_call):
        result = Package.install(proxy='http://proxy:8080')
        assert result is True
        args = mock_check_call.call_args[0][0]
        assert 'http://proxy:8080' in args

    @patch('subprocess.check_call', side_effect=subprocess.CalledProcessError(1, 'pip'))
    def test_install_failure_returns_false(self, mock_check_call):
        result = Package.install()
        assert result is False

    @patch('subprocess.check_call')
    def test_install_custom_package(self, mock_check_call):
        result = Package.install(package_name='my-package')
        assert result is True
        args = mock_check_call.call_args[0][0]
        assert 'my-package' in args


class TestPackageUninstall:
    @patch('subprocess.check_call')
    def test_uninstall_default(self, mock_check_call):
        result = Package.uninstall()
        assert result is True
        mock_check_call.assert_called_once()
        args = mock_check_call.call_args[0][0]
        assert 'uninstall' in args
        assert '--yes' in args
        assert 'yojenkins' in args

    @patch('subprocess.check_call')
    def test_uninstall_no_auto_yes(self, mock_check_call):
        result = Package.uninstall(auto_yes=False)
        assert result is True
        args = mock_check_call.call_args[0][0]
        assert '--yes' not in args

    @patch('subprocess.check_call', side_effect=subprocess.CalledProcessError(1, 'pip'))
    def test_uninstall_failure_returns_false(self, mock_check_call):
        result = Package.uninstall()
        assert result is False


# ============================================================================
# SharedLibrary tests
# ============================================================================


class TestSharedLibraryInit:
    def test_groovy_script_directory_set(self):
        sl = SharedLibrary()
        assert 'groovy_scripts' in str(sl.groovy_script_directory)
        assert sl.groovy_script_directory.is_absolute()


class TestSharedLibrarySetup:
    def test_setup_no_repo_info_returns_false(self):
        sl = SharedLibrary()
        mock_rest = MagicMock()
        result = sl.setup(
            rest=mock_rest,
            lib_name='my-lib',
            repo_owner='',
            repo_name='',
            repo_url='',
            repo_branch='main',
            implicit=True,
            credential_id='cred-1',
        )
        assert result is False

    def test_setup_owner_without_name_returns_false(self):
        sl = SharedLibrary()
        mock_rest = MagicMock()
        result = sl.setup(
            rest=mock_rest,
            lib_name='my-lib',
            repo_owner='my-org',
            repo_name='',
            repo_url='',
            repo_branch='main',
            implicit=True,
            credential_id='cred-1',
        )
        assert result is False

    def test_setup_name_without_owner_returns_false(self):
        sl = SharedLibrary()
        mock_rest = MagicMock()
        result = sl.setup(
            rest=mock_rest,
            lib_name='my-lib',
            repo_owner='',
            repo_name='my-repo',
            repo_url='',
            repo_branch='main',
            implicit=False,
            credential_id='cred-1',
        )
        assert result is False

    @patch('yojenkins.utility.utility.run_groovy_script')
    def test_setup_with_repo_url_success(self, mock_groovy):
        mock_groovy.return_value = ('output', True, '')
        sl = SharedLibrary()
        mock_rest = MagicMock()
        result = sl.setup(
            rest=mock_rest,
            lib_name='my-lib',
            repo_owner='',
            repo_name='',
            repo_url='https://github.com/org/repo.git',
            repo_branch='main',
            implicit=True,
            credential_id='cred-1',
        )
        assert result is True
        mock_groovy.assert_called_once()

    @patch('yojenkins.utility.utility.run_groovy_script')
    def test_setup_with_owner_and_name_success(self, mock_groovy):
        mock_groovy.return_value = ('output', True, '')
        sl = SharedLibrary()
        mock_rest = MagicMock()
        result = sl.setup(
            rest=mock_rest,
            lib_name='my-lib',
            repo_owner='my-org',
            repo_name='my-repo',
            repo_url='',
            repo_branch='main',
            implicit=False,
            credential_id='cred-1',
        )
        assert result is True

    @patch('yojenkins.utility.utility.run_groovy_script')
    def test_setup_groovy_failure(self, mock_groovy):
        mock_groovy.return_value = ('', False, 'error message')
        sl = SharedLibrary()
        mock_rest = MagicMock()
        result = sl.setup(
            rest=mock_rest,
            lib_name='my-lib',
            repo_owner='',
            repo_name='',
            repo_url='https://github.com/org/repo.git',
            repo_branch='main',
            implicit=True,
            credential_id='cred-1',
        )
        assert result is False
