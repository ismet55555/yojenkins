"""Integration tests for Folder operations against a live Jenkins instance."""

import pytest

pytestmark = [pytest.mark.docker, pytest.mark.slow]

FOLDER_NAME = 'integration-test-folder'


class TestFolderIntegration:
    """Folder CRUD tests. Tests run in definition order within this class."""

    def test_create_folder(self, yojenkins_instance):
        """Create a folder in the root."""
        result = yojenkins_instance.folder.create(
            name=FOLDER_NAME,
            folder_url=yojenkins_instance.rest.get_server_url(),
            config='',
        )
        assert result is True

    def test_folder_info(self, yojenkins_instance):
        """Get info on the created folder."""
        info = yojenkins_instance.folder.info(folder_name=FOLDER_NAME)
        assert isinstance(info, dict)
        assert 'displayName' in info

    def test_folder_item_list(self, yojenkins_instance):
        """New folder should be empty initially."""
        items, _urls = yojenkins_instance.folder.item_list(folder_name=FOLDER_NAME)
        assert isinstance(items, list)

    def test_create_job_inside_folder(self, yojenkins_instance):
        """Create a freestyle job inside the integration folder."""
        result = yojenkins_instance.job.create(
            name='folder-sub-job',
            folder_name=FOLDER_NAME,
            config_file='',
        )
        assert result is True

    def test_folder_jobs_list(self, yojenkins_instance):
        """Folder should now contain the sub-job."""
        jobs, _urls = yojenkins_instance.folder.jobs_list(folder_name=FOLDER_NAME)
        assert len(jobs) >= 1

    def test_delete_folder(self, yojenkins_instance):
        """Delete the integration test folder (cascading delete)."""
        result = yojenkins_instance.folder.delete(folder_name=FOLDER_NAME)
        assert result is True
