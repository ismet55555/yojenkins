"""Tests for yojenkins/docker_container/docker_jenkins_server.py"""

from unittest.mock import MagicMock, patch

import pytest
from docker.errors import DockerException


@pytest.fixture
def mock_shutil_copy():
    with patch('yojenkins.docker_container.docker_jenkins_server.shutil.copy2') as mock_copy:
        yield mock_copy


@pytest.fixture
def docker_server(mock_shutil_copy):
    """Create a DockerJenkinsServer with shutil.copy2 mocked to avoid filesystem access."""
    from yojenkins.docker_container.docker_jenkins_server import DockerJenkinsServer

    return DockerJenkinsServer()


@pytest.fixture
def docker_server_custom(mock_shutil_copy):
    """Create a DockerJenkinsServer with custom params."""
    from yojenkins.docker_container.docker_jenkins_server import DockerJenkinsServer

    return DockerJenkinsServer(
        port=9090,
        host='myhost',
        protocol_schema='https',
        container_name='my-jenkins',
        image_fullname='my-image:v1',
        admin_user='testadmin',
        password='testpass',
        bind_mount_dir='/tmp/mydir',
        new_volume=True,
        new_volume_name='my-vol',
    )


class TestDockerJenkinsServerInit:
    """Tests for DockerJenkinsServer.__init__"""

    def test_default_container_name(self, docker_server):
        assert docker_server.container_name == 'yojenkins-jenkins'

    def test_default_container_address(self, docker_server):
        assert docker_server.container_address == 'http://localhost:8080'

    def test_default_ports(self, docker_server):
        assert docker_server.container_ports == {'8080/tcp': 8080, '50000/tcp': 50000}

    def test_default_image_fullname(self, docker_server):
        assert docker_server.image_fullname == 'yojenkins-jenkins:latest'

    def test_default_no_bind_volumes(self, docker_server):
        assert docker_server.volumes_bind == {}

    def test_default_named_volume(self, docker_server):
        assert 'yojenkins-jenkins' in docker_server.volumes_named
        assert docker_server.volumes_named['yojenkins-jenkins'] == '/var/jenkins_home'

    def test_custom_port_in_address(self, docker_server_custom):
        assert docker_server_custom.container_address == 'https://myhost:9090'

    def test_custom_container_name(self, docker_server_custom):
        assert docker_server_custom.container_name == 'my-jenkins'

    def test_custom_image_fullname(self, docker_server_custom):
        assert docker_server_custom.image_fullname == 'my-image:v1'

    def test_custom_bind_mount(self, docker_server_custom):
        assert '/tmp/mydir' in docker_server_custom.volumes_bind
        assert docker_server_custom.volumes_bind['/tmp/mydir']['bind'] == '/tmp/my_things'

    def test_custom_named_volume(self, docker_server_custom):
        assert 'my-vol' in docker_server_custom.volumes_named

    def test_build_args_contain_credentials(self, docker_server_custom):
        args = docker_server_custom.image_build_args
        assert args['JENKINS_ADMIN_ID'] == 'testadmin'
        assert args['JENKINS_ADMIN_PASSWORD'] == 'testpass'
        assert args['JENKINS_PORT'] == '9090'
        assert args['PROTOCOL_SCHEMA'] == 'https'

    def test_new_volume_flag(self, docker_server_custom):
        assert docker_server_custom.new_volume is True

    def test_shutil_copy_called_on_init(self, mock_shutil_copy):
        from yojenkins.docker_container.docker_jenkins_server import DockerJenkinsServer

        DockerJenkinsServer()
        mock_shutil_copy.assert_called_once()

    def test_shutil_copy_failure_exits(self):
        with patch('yojenkins.docker_container.docker_jenkins_server.shutil.copy2', side_effect=OSError('copy fail')):
            with pytest.raises(SystemExit):
                from yojenkins.docker_container.docker_jenkins_server import DockerJenkinsServer

                DockerJenkinsServer()


class TestDockerClientInit:
    """Tests for docker_client_init"""

    @patch('yojenkins.docker_container.docker_jenkins_server.docker.from_env')
    def test_successful_init(self, mock_from_env, docker_server):
        mock_client = MagicMock()
        mock_client.ping.return_value = True
        mock_from_env.return_value = mock_client

        result = docker_server.docker_client_init()

        assert result is True
        assert docker_server.docker_client is mock_client

    @patch('yojenkins.docker_container.docker_jenkins_server.docker.from_env')
    def test_docker_exception_returns_false(self, mock_from_env, docker_server):
        mock_from_env.side_effect = DockerException('no docker')

        result = docker_server.docker_client_init()

        assert result is False

    @patch('yojenkins.docker_container.docker_jenkins_server.docker.from_env')
    def test_ping_failure_returns_false(self, mock_from_env, docker_server):
        mock_client = MagicMock()
        mock_client.ping.return_value = False
        mock_from_env.return_value = mock_client

        result = docker_server.docker_client_init()

        assert result is False


class TestContainerStop:
    """Tests for _container_stop"""

    def test_stop_success(self, docker_server):
        mock_client = MagicMock()
        mock_container = MagicMock()
        mock_client.containers.get.return_value = mock_container
        docker_server.docker_client = mock_client

        result = docker_server._container_stop()

        assert result is True
        mock_container.stop.assert_called_once()

    def test_stop_docker_exception_returns_false(self, docker_server):
        mock_client = MagicMock()
        mock_client.containers.get.side_effect = DockerException('not found')
        docker_server.docker_client = mock_client

        result = docker_server._container_stop()

        assert result is False


class TestContainerKill:
    """Tests for _container_kill"""

    def test_kill_success(self, docker_server):
        mock_client = MagicMock()
        mock_container = MagicMock()
        mock_client.containers.get.return_value = mock_container
        docker_server.docker_client = mock_client

        result = docker_server._container_kill()

        assert result is True
        mock_container.kill.assert_called_once()

    def test_kill_exception_still_returns_true(self, docker_server):
        mock_client = MagicMock()
        mock_client.containers.get.side_effect = DockerException('not found')
        docker_server.docker_client = mock_client

        # _container_kill always returns True even on exception
        result = docker_server._container_kill()

        assert result is True


class TestImageBuild:
    """Tests for _image_build"""

    def test_build_success(self, docker_server):
        mock_client = MagicMock()
        mock_client.images.build.return_value = (MagicMock(), [])
        docker_server.docker_client = mock_client

        result = docker_server._image_build()

        assert result == docker_server.image_fullname
        mock_client.images.build.assert_called_once()

    def test_build_failure_returns_empty_string(self, docker_server):
        mock_client = MagicMock()
        mock_client.images.build.side_effect = DockerException('build failed')
        docker_server.docker_client = mock_client

        result = docker_server._image_build()

        assert result == ''


class TestImageRemove:
    """Tests for _image_remove"""

    def test_remove_success(self, docker_server):
        mock_client = MagicMock()
        docker_server.docker_client = mock_client

        result = docker_server._image_remove()

        assert result is True
        mock_client.images.remove.assert_called_once_with(docker_server.image_fullname)

    def test_remove_failure_returns_false(self, docker_server):
        mock_client = MagicMock()
        mock_client.images.remove.side_effect = DockerException('remove failed')
        docker_server.docker_client = mock_client

        result = docker_server._image_remove()

        assert result is False


class TestClean:
    """Tests for clean method"""

    def test_clean_container_only(self, docker_server):
        mock_client = MagicMock()
        docker_server.docker_client = mock_client

        result = docker_server.clean(remove_volume=False, remove_image=False)

        assert result is True

    def test_clean_with_volume_removal(self, docker_server):
        mock_client = MagicMock()
        mock_volume = MagicMock()
        mock_client.volumes.get.return_value = mock_volume
        docker_server.docker_client = mock_client

        result = docker_server.clean(remove_volume=True, remove_image=False)

        assert result is True

    def test_clean_with_image_removal(self, docker_server):
        mock_client = MagicMock()
        docker_server.docker_client = mock_client

        result = docker_server.clean(remove_volume=False, remove_image=True)

        assert result is True

    def test_clean_kill_failure_returns_false(self, docker_server):
        mock_client = MagicMock()
        docker_server.docker_client = mock_client
        with patch.object(docker_server, '_container_kill', return_value=False):
            result = docker_server.clean(remove_volume=False, remove_image=False)
        assert result is False

    def test_clean_volume_removal_failure_returns_false(self, docker_server):
        mock_client = MagicMock()
        docker_server.docker_client = mock_client
        with (
            patch.object(docker_server, '_container_kill', return_value=True),
            patch.object(docker_server, '_volumes_remove', return_value=False),
        ):
            result = docker_server.clean(remove_volume=True, remove_image=False)
        assert result is False

    def test_clean_image_removal_failure_returns_false(self, docker_server):
        mock_client = MagicMock()
        docker_server.docker_client = mock_client
        with (
            patch.object(docker_server, '_container_kill', return_value=True),
            patch.object(docker_server, '_image_remove', return_value=False),
        ):
            result = docker_server.clean(remove_volume=False, remove_image=True)
        assert result is False


class TestSetup:
    """Tests for the setup method."""

    def test_setup_no_client(self, docker_server):
        docker_server.docker_client = None
        with patch.object(docker_server, 'docker_client_init', return_value=False):
            result = docker_server.setup()
            deployed = result
            assert deployed == {}

    def test_setup_full_success(self, docker_server):
        mock_client = MagicMock()
        mock_client.info.return_value = {'ServerVersion': '20.10.0'}
        docker_server.docker_client = mock_client
        with (
            patch.object(docker_server, '_container_kill', return_value=True),
            patch.object(docker_server, '_image_build', return_value='yojenkins-jenkins:latest'),
            patch.object(docker_server, '_volumes_create', return_value=[{'named': 'vol'}]),
            patch.object(docker_server, '_container_run', return_value=('yojenkins-jenkins', 'http://localhost:8080')),
        ):
            deployed, success = docker_server.setup()
        assert success is True
        assert deployed['image'] == 'yojenkins-jenkins:latest'
        assert deployed['container'] == 'yojenkins-jenkins'
        assert deployed['address'] == 'http://localhost:8080'

    def test_setup_image_build_failure(self, docker_server):
        mock_client = MagicMock()
        docker_server.docker_client = mock_client
        with (
            patch.object(docker_server, '_container_kill', return_value=True),
            patch.object(docker_server, '_image_build', return_value=''),
        ):
            deployed, success = docker_server.setup()
        assert success is False

    def test_setup_container_run_failure(self, docker_server):
        mock_client = MagicMock()
        docker_server.docker_client = mock_client
        with (
            patch.object(docker_server, '_container_kill', return_value=True),
            patch.object(docker_server, '_image_build', return_value='img:latest'),
            patch.object(docker_server, '_volumes_create', return_value=[{'named': 'vol'}]),
            patch.object(docker_server, '_container_run', return_value=('', '')),
        ):
            deployed, success = docker_server.setup()
        assert success is False


class TestVolumesCreate:
    """Tests for _volumes_create."""

    def test_volumes_create_named(self, docker_server):
        mock_client = MagicMock()
        # Simulate volume not found -> create new
        mock_client.volumes.get.side_effect = Exception('not found')
        docker_server.docker_client = mock_client

        result = docker_server._volumes_create()
        assert len(result) > 0

    def test_volumes_create_existing_no_new(self, docker_server):
        mock_client = MagicMock()
        mock_volume = MagicMock()
        mock_client.volumes.get.return_value = mock_volume
        docker_server.docker_client = mock_client
        docker_server.new_volume = False

        result = docker_server._volumes_create()
        mock_volume.remove.assert_not_called()
        assert len(result) > 0

    def test_volumes_create_existing_with_new_volume(self, docker_server):
        mock_client = MagicMock()
        mock_volume = MagicMock()
        mock_client.volumes.get.return_value = mock_volume
        docker_server.docker_client = mock_client
        docker_server.new_volume = True

        result = docker_server._volumes_create()
        mock_volume.remove.assert_called_once_with(force=True)


class TestVolumesRemove:
    """Tests for _volumes_remove."""

    def test_volumes_remove_success(self, docker_server):
        mock_client = MagicMock()
        mock_volume = MagicMock()
        mock_client.volumes.get.return_value = mock_volume
        docker_server.docker_client = mock_client

        result = docker_server._volumes_remove()
        assert result is True
        mock_volume.remove.assert_called_once_with(force=True)

    def test_volumes_remove_exception_still_returns_true(self, docker_server):
        mock_client = MagicMock()
        mock_client.volumes.get.side_effect = DockerException('not found')
        docker_server.docker_client = mock_client

        result = docker_server._volumes_remove()
        assert result is True


class TestContainerRun:
    """Tests for _container_run."""

    @patch('platform.system', return_value='Linux')
    @patch('yojenkins.docker_container.docker_jenkins_server.getgrnam')
    def test_container_run_success(self, mock_getgrnam, mock_system, docker_server):
        mock_grp = MagicMock()
        mock_grp.gr_gid = 999
        mock_getgrnam.return_value = mock_grp
        mock_client = MagicMock()
        docker_server.docker_client = mock_client

        name, address = docker_server._container_run()
        assert name == docker_server.container_name
        assert address == docker_server.container_address
        mock_client.containers.run.assert_called_once()

    @patch('platform.system', return_value='Linux')
    @patch('yojenkins.docker_container.docker_jenkins_server.getgrnam')
    def test_container_run_failure(self, mock_getgrnam, mock_system, docker_server):
        mock_grp = MagicMock()
        mock_grp.gr_gid = 999
        mock_getgrnam.return_value = mock_grp
        mock_client = MagicMock()
        mock_client.containers.run.side_effect = DockerException('run failed')
        docker_server.docker_client = mock_client

        name, address = docker_server._container_run()
        assert name == ''
        assert address == ''


class TestImageBuildExtended:
    """Extended tests for _image_build error code branches."""

    def test_build_error_code_1(self, docker_server):
        mock_client = MagicMock()
        mock_client.images.build.side_effect = DockerException('build failed: 1')
        docker_server.docker_client = mock_client

        result = docker_server._image_build()
        assert result == ''

    def test_build_error_code_127(self, docker_server):
        mock_client = MagicMock()
        mock_client.images.build.side_effect = DockerException('build failed: 127')
        docker_server.docker_client = mock_client

        result = docker_server._image_build()
        assert result == ''

    def test_build_error_code_2(self, docker_server):
        mock_client = MagicMock()
        mock_client.images.build.side_effect = DockerException('build failed: 2')
        docker_server.docker_client = mock_client

        result = docker_server._image_build()
        assert result == ''

    def test_build_error_code_126(self, docker_server):
        mock_client = MagicMock()
        mock_client.images.build.side_effect = DockerException('build failed: 126')
        docker_server.docker_client = mock_client

        result = docker_server._image_build()
        assert result == ''
