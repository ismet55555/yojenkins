"""Integration tests for Job operations against a live Jenkins instance."""

import time

import pytest

pytestmark = [pytest.mark.docker, pytest.mark.slow]

JOB_NAME = 'integration-test-job'


class TestJobIntegration:
    """Job CRUD + build trigger tests. Tests run in definition order."""

    def test_create_job(self, yojenkins_instance):
        """Create a freestyle job in the root folder."""
        result = yojenkins_instance.job.create(
            name=JOB_NAME,
            folder_url=yojenkins_instance.rest.get_server_url(),
            config_file='',
        )
        assert result is True

    def test_job_info(self, yojenkins_instance):
        """Get info on the created job."""
        info = yojenkins_instance.job.info(job_name=JOB_NAME)
        assert isinstance(info, dict)
        assert info['name'] == JOB_NAME

    def test_build_trigger(self, yojenkins_instance):
        """Trigger a build and verify a queue number is returned."""
        queue_number = yojenkins_instance.job.build_trigger(job_name=JOB_NAME)
        assert isinstance(queue_number, int)
        assert queue_number > 0
        # Wait for build to complete (empty freestyle is fast)
        time.sleep(10)

    def test_build_list_after_trigger(self, yojenkins_instance):
        """After triggering, build list should have at least 1 entry."""
        builds, _build_urls = yojenkins_instance.job.build_list(job_name=JOB_NAME)
        assert len(builds) >= 1

    def test_delete_job(self, yojenkins_instance):
        """Delete the integration test job."""
        result = yojenkins_instance.job.delete(job_name=JOB_NAME)
        assert result is True
