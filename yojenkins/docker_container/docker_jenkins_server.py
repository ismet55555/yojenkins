"""Containerized Jenkins instance Management"""

import logging
import os
import platform
import shutil
from datetime import datetime

if platform.system() != "Windows":
    # Non-windows systems get group ID
    from grp import getgrnam

from time import perf_counter
from typing import Any, Dict, Tuple

import docker
from docker.errors import DockerException

from yojenkins.utility.utility import fail_out, get_resource_path, print2

# Getting the logger reference
logger = logging.getLogger()


class DockerJenkinsServer():
    """Class managing containerized Jenkins instance"""

    def __init__(self,
                 config_file: str = 'config_as_code.yaml',
                 plugins_file: str = 'plugins.txt',
                 protocol_schema: str = 'http',
                 host: str = 'localhost',
                 port: int = 8080,
                 image_fullname: str = 'yojenkins-jenkins:latest',
                 image_base: str = 'jenkins/jenkins',
                 extra_setup_script: str = '',
                 image_rebuild: bool = False,
                 new_volume: bool = False,
                 new_volume_name: str = 'yojenkins-jenkins',
                 bind_mount_dir: str = '',
                 container_name: str = 'yojenkins-jenkins',
                 registry: str = '',
                 admin_user: str = 'admin',
                 password: str = 'password'):
        """Object constructor method, called at object creation

        ### TODO: Use kwargs instead of positional arguments

        Args:
            None

        Returns:
            None
        """

        # TODO: Option flag to mount docker socket (for security)

        self.docker_client = None

        # Image Related
        self.docker_registry = registry
        self.image_base_image = image_base
        self.image_base_version = 'latest'
        self.image_dockerfile_dir = get_resource_path(os.path.join('resources', 'server_docker_settings'))
        self.image_fullname = image_fullname
        self.image_rebuild = image_rebuild
        self.image_build_args = {
            "JENKINS_BASE_IMAGE": self.image_base_image,
            "JENKINS_BASE_VERSION": self.image_base_version,
            "JENKINS_CONFIG_FILE": config_file,
            "JENKINS_PLUGINS_FILE": plugins_file,
            "PROTOCOL_SCHEMA": protocol_schema,
            "JENKINS_HOSTNAME": host,
            "JENKINS_PORT": f"{port}",
            "JENKINS_ADMIN_ID": admin_user,
            "JENKINS_ADMIN_PASSWORD": password
        }

        # Container Related
        self.container_name = container_name
        self.container_address = f"{protocol_schema}://{host}:{port}"
        self.container_ports = {'8080/tcp': port, '50000/tcp': 50000}
        self.container_env_vars = []
        self.container_restart_policy = {}
        self.container_remove = False if self.container_restart_policy else True

        # Volume Related
        self.volumes_bind = {} if not bind_mount_dir else {bind_mount_dir: {'bind': '/tmp/my_things', 'mode': 'rw'}}
        self.volumes_named = {f'{new_volume_name}': '/var/jenkins_home'}
        self.volumes_mounts = []
        self.new_volume = new_volume

        # Extra/Custom Setup Script File
        self.extra_setup_script = extra_setup_script
        if extra_setup_script:
            logger.debug("Extra setup script for image build provided")
            logger.debug(f'Copying extra setup script to Docker context directory ...')
            source_path = os.path.abspath(extra_setup_script)
            target_path = os.path.join(self.image_dockerfile_dir, 'extra_setup_script.sh')
        else:
            logger.debug("Extra setup script for image build NOT provided")
            logger.debug(f'Copying empty dummy script as extra setup script ...')
            source_path = os.path.join(self.image_dockerfile_dir, 'dummy.sh')
            target_path = os.path.join(self.image_dockerfile_dir, 'extra_setup_script.sh')
        logger.debug(f'    - Source: {source_path}')
        logger.debug(f'    - Target: {target_path}')
        try:
            shutil.copy2(source_path, target_path)
        except (IOError, PermissionError) as error:
            fail_out(f'Failed to copy "{source_path}" to "{target_path}". Exception: {error}')

        # Output all attributes
        logger.debug(f'Jenkins server build attributes:')
        for key, value in vars(self).items():
            if key in ['image_build_args', 'docker_client', 'container_env_vars']:
                continue
            logger.debug(f'    - {key}: {value}')

    def docker_client_init(self) -> bool:
        """TODO Docstring

        Details: TODO

        Args:
            TODO

        Returns:
            TODO
        """
        logger.debug('Connecting to local docker client/engine ...')
        # Get the local docker client
        try:
            self.docker_client = docker.from_env()
        except DockerException as error:
            logger.debug(f'Failed to get docker client/engine handle. Exception: {error}')
            return False

        # Ping the docker client
        if not self.docker_client.ping():
            logger.debug('Failed to ping local docker client')
            return False
        logger.debug('Successfully connected to local docker client/engine')

        return True

    def setup(self) -> dict:
        """TODO Docstring

        Details: TODO

        Args:
            TODO

        Returns:
            TODO
        """
        deployed: Dict[str, Any] = {}

        if not self.docker_client:
            if not self.docker_client_init():
                logger.debug('Docker client was not initialized. Please run .docker_client_init() first')
                return deployed

        if not self._container_kill():
            return deployed, False
        if self.image_rebuild:
            if not self._image_remove():
                return deployed, False

        image_name = self._image_build()
        if not image_name:
            return deployed, False
        deployed['image'] = image_name

        volume_names = self._volumes_create()
        if not volume_names:
            return deployed, False
        deployed['volumes'] = volume_names

        container_name, server_address = self._container_run()
        if not server_address:
            return deployed, False
        deployed['container'] = container_name
        deployed['address'] = server_address
        deployed['deploy_timestamp'] = datetime.now().timestamp()
        deployed['deploy_datetime'] = datetime.now().strftime("%A, %B %d, %Y %I:%M:%S")
        deployed['docker_version'] = self.docker_client.info(
        )['ServerVersion'] if 'ServerVersion' in self.docker_client.info() else 'N/A'

        return deployed, True

    def clean(self, remove_volume: bool = False, remove_image: bool = False) -> bool:
        """TODO Docstring

        Details: TODO

        Args:
            TODO

        Returns:
            TODO
        """
        removed = {}

        if not self._container_kill():
            return False

        if remove_volume:
            if not self._volumes_remove():
                return False

        if remove_image:
            if not self._image_remove():
                return False

        return True

    def _image_build(self) -> str:
        """Building docker image with specified parameters

        Details:
            - https://docker-py.readthedocs.io/en/stable/images.html

        Returns:
            Name of the image that was built
        """
        start_time = perf_counter()
        logger.debug(f'Building image: {self.image_fullname} ...')
        logger.debug(f'Dockerfile context directory: {self.image_dockerfile_dir}')
        try:
            _, build_logs = self.docker_client.images.build(path=self.image_dockerfile_dir,
                                                            tag=self.image_fullname,
                                                            rm=True,
                                                            buildargs=self.image_build_args,
                                                            quiet=False,
                                                            forcerm=True)
            logger.debug('Docker image build logs:')
            for chunk in build_logs:
                if 'stream' in chunk:
                    for line in chunk['stream'].splitlines():
                        logger.debug(f"    {line}")
        except DockerException as error:
            print2(f'Failed to build image: {self.image_fullname}. Exception: {error}', bold=True, color="red")
            if ": 1" in str(error):
                print2('   Error Code 1   : Operation not permitted', bold=True, color="red")
                print2('   Possible Reason: General error script', bold=True, color="red")
            elif ": 127" in str(error):
                print2('   Error Code 127 : Shell command not found', bold=True, color="red")
                print2('   Possible Reason: Unknown command, misspelling, or end of line sequence (CRLF/LF)',
                       bold=True,
                       color="red")
            elif ": 2" in str(error):
                print2('   Error Code 2   : No such file exists', bold=True, color="red")
                print2('   Possible Reason: Missing script or command references missing file', bold=True, color="red")
            elif ": 126" in str(error):
                print2('   Error Code 126 : Permission Issue', bold=True, color="red")
                print2('   Possible Reason: Script or command does not have sufficient privileges',
                       bold=True,
                       color="red")
            else:
                print2('   Please see error code: https://www.thegeekstuff.com/2010/10/linux-error-codes/',
                       bold=True,
                       color="red")
            return ''
        logger.debug(
            f'Successfully build image: {self.image_fullname} (Elapsed time: {perf_counter() - start_time:.3f}s)')
        return self.image_fullname

    def _image_remove(self) -> bool:
        """Remove a specified docker image

        Returns:
            True if successful, False otherwise
        """
        logger.debug(f'Removing image: {self.image_fullname} ...')
        try:
            self.docker_client.images.remove(self.image_fullname)
        except DockerException as error:
            logger.debug(f'Failed to remove image: {self.image_fullname}. Exception: {error}')
            return False
        logger.debug(f'Successfully removed image: {self.image_fullname}')
        return True

    def _volumes_create(self) -> list:
        """TODO Docstring

        Details: TODO

        Args:
            TODO

        Returns:
            TODO
        """
        self.volumes_mounts = []
        volume_mounts_names = []

        # Bind Volume Mounts
        for volume_source, volume_target in self.volumes_bind.items():
            logger.debug(f'Adding new local bind volume to mount list: {volume_source} -> {volume_target} ...')
            mount = docker.types.Mount(source=volume_source, target=volume_target, type='bind', read_only=False)
            self.volumes_mounts.append(mount)
            volume_mounts_names.append({'bind': volume_source})

        # Named Volume Mounts
        for volume_name, volume_dir in self.volumes_named.items():
            try:
                volume_handle = self.docker_client.volumes.get(volume_name)
                if self.new_volume:
                    logger.debug(f'Removing found matching/existing named volume: {volume_name} ...')
                    volume_handle.remove(force=True)
                else:
                    logger.debug(f'Using found matching/existing named volume: {volume_name}')
            except:
                logger.debug(f'Creating new named volume: {volume_name}')
                self.docker_client.volumes.create(name=volume_name, driver='local')
                logger.debug('Successfully created!')

            logger.debug(f'Adding named volumes to mount list: {volume_name} ...')
            mount = docker.types.Mount(target=volume_dir, source=volume_name, type='volume', read_only=False)
            self.volumes_mounts.append(mount)
            volume_mounts_names.append({'named': volume_name})

        # Adding Docker unix socket
        logger.debug('Adding bind mount to Docker unix socket: /var/run/docker.sock ...')
        mount = docker.types.Mount(target='/var/run/docker.sock',
                                   source='/var/run/docker.sock',
                                   type='bind',
                                   read_only=False)
        self.volumes_mounts.append(mount)

        logger.debug(f'Number of volumes to be mounted to container: {len(self.volumes_mounts)}')
        return volume_mounts_names

    def _volumes_remove(self) -> bool:
        """TODO Docstring

        Details: TODO

        Args:
            TODO

        Returns:
            TODO
        """
        logger.debug(f'Removing named volumes: {self.volumes_named.keys()}')
        for volume_name in self.volumes_named:
            try:
                volume_named = self.docker_client.volumes.get(volume_name)
                volume_named.remove(force=True)
                logger.debug(f'    - Volume: {volume_name} - REMOVED')
            except DockerException as error:
                logger.debug(f'    - Volume: {volume_name} - FAILED - Exception: {error}')
        return True

    def _container_run(self) -> Tuple[str, str]:
        """TODO Docstring

        Details: TODO

        Args:
            TODO

        Returns:
            TODO
        """
        # Getting docker group id (Unix only)
        if platform.system() != "Windows":
            docker_gid = [getgrnam('docker').gr_gid]
        else:
            docker_gid = None

        logger.debug(f'Local docker service group id found: {docker_gid}')

        logger.debug(f'Creating and running container: {self.container_name} ...')
        try:
            self.docker_client.containers.run(name=self.container_name,
                                              image=self.image_fullname,
                                              environment=self.container_env_vars,
                                              ports=self.container_ports,
                                              mounts=self.volumes_mounts,
                                              restart_policy=self.container_restart_policy,
                                              remove=self.container_remove,
                                              auto_remove=self.container_remove,
                                              detach=True,
                                              group_add=docker_gid)
        except DockerException as error:
            logger.debug(f'Failed to run container: {self.container_name} Exception: {error}')
            return '', ''
        logger.debug(f'Successfully running container: {self.container_name}')
        logger.debug(f'Container "{self.container_name}" is running at this address:')
        logger.debug(f'    --> {self.container_address}')
        return self.container_name, self.container_address

    def _container_stop(self) -> bool:
        """TODO Docstring

        Details: TODO

        Args:
            TODO

        Returns:
            TODO
        """
        logger.debug(f'Stopping container with matching tag: {self.container_name} ...')
        try:
            container_handle = self.docker_client.containers.get(self.container_name)
            container_handle.stop()
            logger.debug('Container is stopped')
        except DockerException as error:
            logger.debug(f'Failed to stop container matching tag: {self.container_name}. Exception: {error}')
            return False
        return True

    def _container_kill(self) -> bool:
        """TODO Docstring

        Details: TODO

        Args:
            TODO

        Returns:
            TODO
        """
        logger.debug(f'Killing container with matching tag: {self.container_name} ...')
        try:
            container_handle = self.docker_client.containers.get(self.container_name)
            container_handle.kill()
            logger.debug('Container is dead')
        except DockerException as error:
            logger.debug(f'Failed to kill container matching tag: {self.container_name}. Exception: {error}')
        return True
