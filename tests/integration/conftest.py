"""Docker-based integration test fixtures.

Provides a session-scoped Jenkins server running in Docker and a
pre-authenticated YoJenkins instance for integration tests.

Imports for docker, Auth, Rest, and YoJenkins are deferred inside fixtures
so that tests skip gracefully when Docker is unavailable rather than
failing at import time.
"""

import logging
import time
from pathlib import Path

import pytest
import requests

# ruff: noqa: PLC0415

logger = logging.getLogger(__name__)

INTEGRATION_PORT = 9999
INTEGRATION_ADMIN_USER = 'admin'
INTEGRATION_ADMIN_PASSWORD = 'integrationtestpassword'
CONTAINER_NAME = 'yojenkins-integration-test'
IMAGE_NAME = 'yojenkins-integration:latest'
VOLUME_NAME = 'yojenkins-integration-vol'

# JCasC config for integration testing.
# The default crumbIssuer in Jenkins 2.x no longer binds crumbs to client IPs,
# so a simple 'standard: {}' is sufficient for cross-session crumb reuse.
INTEGRATION_JCASC = """\
jenkins:
  systemMessage: "Integration test server"
  numExecutors: 4
  scmCheckoutRetryCount: 2
  mode: NORMAL
  crumbIssuer:
    standard: {{}}
  securityRealm:
    local:
      allowsSignup: false
      users:
        - id: {admin_user}
          password: {admin_password}
  authorizationStrategy:
    globalMatrix:
      permissions:
        - "Overall/Administer:{admin_user}"
        - "Overall/Read:authenticated"
  remotingSecurity:
    enabled: true
unclassified:
  location:
    url: http://localhost:{port}/
"""


def _is_docker_available():
    """Check if Docker daemon is reachable."""
    try:
        import docker

        client = docker.from_env()
        client.ping()
        return True
    except Exception:
        return False


def _wait_for_jenkins(url, username, password, container_name, timeout=240, poll_interval=3):
    """Poll Jenkins /api/json until it responds 200 or timeout is reached.

    Checks that the Docker container is still running each iteration to
    fail fast if the container crashed during startup.
    """
    import docker as docker_lib

    deadline = time.time() + timeout
    attempt = 0
    while time.time() < deadline:
        attempt += 1
        elapsed = int(time.time() + timeout - deadline)

        # Fail fast if the container exited or crashed
        try:
            client = docker_lib.from_env()
            container = client.containers.get(container_name)
            if container.status != 'running':
                logger.error('Container %s status is "%s" (not running)', container_name, container.status)
                return False
        except Exception as container_exc:
            logger.warning('Could not check container status for %s: %s', container_name, container_exc)

        # Poll Jenkins API
        try:
            resp = requests.get(f'{url}/api/json', auth=(username, password), timeout=10)
            if resp.status_code == 200:
                logger.info('Jenkins ready at %s after %ds (%d attempts)', url, elapsed, attempt)
                return True
            logger.info('[%ds] Poll %d: HTTP %d', elapsed, attempt, resp.status_code)
        except requests.RequestException as exc:
            logger.info('[%ds] Poll %d: %s', elapsed, attempt, type(exc).__name__)

        time.sleep(poll_interval)

    logger.error('Jenkins did not become healthy within %ds', timeout)
    return False


@pytest.fixture(scope='session')
def docker_jenkins_server():
    """Spin up a Jenkins container for the entire test session.

    Yields a dict with url, username, and password.
    Skips all docker-marked tests if Docker is unavailable.
    """
    if not _is_docker_available():
        pytest.skip('Docker daemon is not available')

    from yojenkins.docker_container.docker_jenkins_server import DockerJenkinsServer
    from yojenkins.utility.utility import get_resource_path

    # Write a test-specific JCasC config with CSRF disabled into the Docker context dir
    docker_context = get_resource_path(str(Path('resources') / 'server_docker_settings'))
    test_config_name = 'integration_test_casc.yaml'
    test_config_path = Path(docker_context) / test_config_name
    test_config_path.write_text(
        INTEGRATION_JCASC.format(
            admin_user=INTEGRATION_ADMIN_USER,
            admin_password=INTEGRATION_ADMIN_PASSWORD,
            port=INTEGRATION_PORT,
        )
    )

    server = DockerJenkinsServer(
        config_file=test_config_name,
        port=INTEGRATION_PORT,
        admin_user=INTEGRATION_ADMIN_USER,
        password=INTEGRATION_ADMIN_PASSWORD,
        container_name=CONTAINER_NAME,
        image_fullname=IMAGE_NAME,
        new_volume_name=VOLUME_NAME,
        new_volume=True,
        image_rebuild=True,
    )

    # Disable auto-remove so we can inspect logs on crash
    server.container_remove = False

    if not server.docker_client_init():
        pytest.skip('Failed to initialize Docker client')

    _deployed, success = server.setup()
    if not success:
        server.clean(remove_volume=True, remove_image=True)
        pytest.fail('Failed to set up Jenkins Docker container')

    server_url = f'http://localhost:{INTEGRATION_PORT}'

    if not _wait_for_jenkins(
        server_url, INTEGRATION_ADMIN_USER, INTEGRATION_ADMIN_PASSWORD, container_name=CONTAINER_NAME
    ):
        # Dump container logs for debugging before cleanup
        try:
            import docker as docker_lib

            client = docker_lib.from_env()
            container = client.containers.get(CONTAINER_NAME)
            logger.error('Jenkins container logs:\n%s', container.logs(tail=100).decode('utf-8', errors='replace'))
        except Exception:
            logger.error('Could not retrieve container logs')
        server.clean(remove_volume=True, remove_image=True)
        pytest.fail('Jenkins did not become healthy within 240s timeout')

    yield {
        'url': server_url,
        'username': INTEGRATION_ADMIN_USER,
        'password': INTEGRATION_ADMIN_PASSWORD,
    }

    server.clean(remove_volume=True, remove_image=True)
    test_config_path.unlink(missing_ok=True)


@pytest.fixture(scope='session')
def yojenkins_instance(docker_jenkins_server):
    """Return a fully authenticated YoJenkins composite object.

    After authentication, fetches a Jenkins crumb token and injects it
    into the REST session's default headers so POST requests succeed.
    """
    from yojenkins.yo_jenkins.auth import Auth
    from yojenkins.yo_jenkins.rest import Rest
    from yojenkins.yo_jenkins.yojenkins import YoJenkins

    server_info = docker_jenkins_server
    profile = {
        'jenkins_server_url': server_info['url'],
        'username': server_info['username'],
        'api_token': server_info['password'],
    }

    auth = Auth(Rest())
    auth.create_auth(profile_info=profile)

    yj = YoJenkins(auth)

    # Fetch crumb using the SAME REST session so session cookies are shared.
    # In Jenkins 2.x, crumbs are tied to the HTTP session (JSESSIONID cookie),
    # so the crumb must be fetched and used from the same session.
    crumb_data, _, crumb_ok = yj.rest.request(
        target=f'{server_info["url"]}/crumbIssuer/api/json',
        request_type='get',
        is_endpoint=False,
    )
    if not crumb_ok or not isinstance(crumb_data, dict):
        pytest.fail('Failed to fetch CSRF crumb. Check JCasC crumbIssuer config.')

    crumb_field = crumb_data['crumbRequestField']
    crumb_value = crumb_data['crumb']
    logger.info('Fetched CSRF crumb: %s=%s...', crumb_field, crumb_value[:12])

    # Inject crumb into the REST session's default headers so all POST requests include it
    rest_session = yj.rest.get_active_session()
    rest_session.headers.update({crumb_field: crumb_value})
    logger.info('Session headers after crumb injection: %s', dict(rest_session.headers))

    return yj
