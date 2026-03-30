"""Integration tests for Build operations against a live Jenkins instance."""

import time

import pytest

pytestmark = [pytest.mark.docker, pytest.mark.slow]

BUILD_JOB_NAME = 'build-integration-test-job'


@pytest.fixture(scope='class')
def build_test_job(yojenkins_instance):
    """Create a job, trigger a build, wait for completion, then cleanup."""
    yojenkins_instance.job.create(
        name=BUILD_JOB_NAME,
        folder_url=yojenkins_instance.rest.get_server_url(),
        config_file='',
    )
    yojenkins_instance.job.build_trigger(job_name=BUILD_JOB_NAME)
    time.sleep(15)
    yield BUILD_JOB_NAME
    try:
        yojenkins_instance.job.delete(job_name=BUILD_JOB_NAME)
    except Exception:
        pass


class TestBuildIntegration:
    def test_build_info(self, yojenkins_instance, build_test_job):
        """Build.info() returns dict with build details."""
        info = yojenkins_instance.build.info(
            job_name=build_test_job,
            latest=True,
        )
        assert isinstance(info, dict)
        assert 'result' in info

    def test_build_logs(self, yojenkins_instance, build_test_job):
        """Build.logs() fetches console output without error."""
        result = yojenkins_instance.build.logs(
            job_name=build_test_job,
            latest=True,
        )
        assert result is True
