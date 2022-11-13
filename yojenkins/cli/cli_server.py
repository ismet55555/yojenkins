"""Server Menu CLI Entrypoints"""

import json
import logging
import os
from pathlib import Path

import click
from yaspin import yaspin
from yaspin.spinners import Spinners

from yojenkins.cli import cli_utility as cu
from yojenkins.cli.cli_utility import log_to_history
from yojenkins.docker_container import DockerJenkinsServer
from yojenkins.utility.utility import fail_out, failures_out, print2
from yojenkins.yo_jenkins import Auth, YoJenkins

# Getting the logger reference
logger = logging.getLogger()

# TODO: Find centralized location for these static values
CONFIG_DIR_NAME = '.yojenkins'


@log_to_history
def info(profile: str, token: str, **kwargs) -> None:
    """Get the server information

    Details: Targeting the server that is specified in the selected profile
    """
    data = cu.config_yo_jenkins(profile, token).server.info()
    cu.standard_out(data, **kwargs)


@log_to_history
def people(profile: str, token: str, opt_list: bool, **kwargs) -> None:
    """TODO Docstring

    Details: TODO

    Args:
        TODO
    """
    data, data_list = cu.config_yo_jenkins(profile, token).server.people()
    data = data_list if opt_list else data
    cu.standard_out(data, **kwargs)


@log_to_history
def queue(profile: str, token: str, opt_list: bool, **kwargs) -> None:
    """TODO Docstring

    Details: TODO

    Args:
        TODO
    """
    yj_obj = cu.config_yo_jenkins(profile, token)
    if opt_list:
        data = yj_obj.server.queue_list()  # TODO: Combine with server_queue_list adding a list argument
    else:
        data = yj_obj.server.queue_info()
    cu.standard_out(data, **kwargs)


@log_to_history
def plugins(profile: str, token: str, opt_list: bool, **kwargs) -> None:
    """TODO Docstring

    Details: TODO

    Args:
        TODO
    """
    data, data_list = cu.config_yo_jenkins(profile, token).server.plugin_list()
    data = data_list if opt_list else data
    cu.standard_out(data, **kwargs)


@log_to_history
def browser(profile: str, token: str) -> None:
    """TODO Docstring

    Details: TODO

    Args:
        TODO
    """
    cu.config_yo_jenkins(profile, token).server.browser_open()


@log_to_history
def reachable(profile: str, timeout: int) -> None:
    """TODO Docstring

    Details: TODO

    Args:
        TODO
    """
    auth = Auth()
    auth.get_credentials(profile)
    data = YoJenkins(auth=auth).rest.is_reachable(auth.jenkins_profile['jenkins_server_url'], timeout=timeout)
    if data:
        click.secho('true', fg='bright_green', bold=True)
    else:
        click.secho('false', fg='bright_red', bold=True)


@log_to_history
def quiet(profile: str, token: str, off: bool) -> None:
    """TODO Docstring

    Details: TODO

    Args:
        TODO
    """
    cu.config_yo_jenkins(profile, token).server.quiet(off=off)
    click.secho('success', fg='bright_green', bold=True)


@log_to_history
def restart(profile: str, token: str, force: bool) -> None:
    """TODO Docstring

    Details: TODO

    Args:
        TODO
    """
    cu.config_yo_jenkins(profile, token).server.restart(force=force)
    click.secho('success', fg='bright_green', bold=True)


@log_to_history
def shutdown(profile: str, token: str, force: bool) -> None:
    """TODO Docstring

    Details: TODO

    Args:
        TODO
    """
    cu.config_yo_jenkins(profile, token).server.shutdown(force=force)
    click.secho('success', fg='bright_green', bold=True)


@log_to_history
def server_deploy(config_file: str, plugins_file: str, protocol_schema: str, host: str, port: int, image_base: str,
                  extra_setup_script: str, image_rebuild: bool, new_volume: bool, new_volume_name: str,
                  bind_mount_dir: str, container_name: str, registry: str, admin_user: str, password: str) -> None:
    """TODO Docstring

    Details: TODO

    Args:
        TODO
    """
    msg = "Setting up a local Jenkins development server. Hold tight, this may take a minute ..."
    if logger.level > 10:
        spinner = yaspin(spinner=getattr(Spinners, "bouncingBar"), attrs=["bold"], text=msg)
        spinner.start()
    else:
        click.echo(msg)

    # TODO: Check if the docker server deployment file is there. If so, show that it is being renewed.

    # Creat object
    djs = DockerJenkinsServer(config_file=config_file,
                              plugins_file=plugins_file,
                              protocol_schema=protocol_schema,
                              host=host,
                              port=port,
                              image_base=image_base,
                              extra_setup_script=extra_setup_script,
                              image_rebuild=image_rebuild,
                              new_volume=new_volume,
                              new_volume_name=new_volume_name,
                              bind_mount_dir=bind_mount_dir,
                              container_name=container_name,
                              registry=registry,
                              admin_user=admin_user,
                              password=password if password else "password")

    # Initialize docker client
    if not djs.docker_client_init():
        if logger.level > 10:
            spinner.stop()
        fail_out('Failed to connect to local docker client')

    # Setup the server
    deployed, success = djs.setup()

    if logger.level > 10:
        spinner.stop()

    if not success:
        failures = ['Failed to setup containerized server']
        if deployed:
            failures.append('Items deployed for partial deployment:')
            failures.append(deployed)
        failures_out(failures)

    # Write current server docker attributes to file
    filepath = os.path.join(Path.home(), CONFIG_DIR_NAME, 'last_deploy_info.json')
    if not filepath:
        fail_out('Failed to find yojenkins module included data directory')
    logger.debug(f'Writing server deploy information to file: {filepath}')
    try:
        with open(os.path.join(filepath), 'w') as file:
            json.dump(deployed, file, indent=4, sort_keys=True)
    except (IOError, PermissionError) as error:
        failures = [f'Server deployed, however failed to write server deploy information to file: {error}']
        failures.append('yojenkins resources may have been installed under root or a restricted account')
        failures_out(failures)

    volumes_named = [list(l.values())[0] for l in deployed["volumes"]]

    print2('Successfully created containerized Jenkins server!', bold=True, color='green')
    print2(f'   - Docker image:      {deployed["image"]}', bold=True, color='green')
    print2(f'   - Docker volumes:    {deployed["container"]}', bold=True, color='green')
    print2(f'   - Docker container:  {", ".join(volumes_named)}', bold=True, color='green')
    print2(f'   - Deployment file:   {filepath}', bold=True, color='green')
    click.echo()
    print2(f'Address:  {deployed["address"]}', bold=True, color='green')
    print2(f'Username: {admin_user}', bold=True, color='green')
    print2(f'Password: {"*************" if password else "password (default)"}', bold=True, color='green')


@log_to_history
def server_teardown(remove_volume: bool, remove_image: bool) -> None:
    """TODO Docstring

    Details: TODO

    Args:
        TODO
    """
    # Load deployment info file with deployment information
    filepath = os.path.join(Path.home(), CONFIG_DIR_NAME, 'last_deploy_info.json')
    logger.debug(f'Detecting server deployment info file: {filepath} ...')
    deployed = {}
    try:
        with open(os.path.join(filepath), 'r') as file:
            deployed = json.load(file)
        logger.debug(f'Successfully found and loaded server deployment info file: {deployed}')
    except (FileNotFoundError, FileExistsError):
        failures = ['Failed to find server deployment info file']
        failures.append('If you think there was a previously successfull deployment, use Docker to remove it manually')
        failures_out(failures)
    except (IOError, PermissionError) as error:
        fail_out(f'Failed to load previous server deployment info file: {error}')

    # Filter out named volumes only
    volumes_named_only = [list(l.values())[0] for l in deployed["volumes"] if 'named' in l]

    # Create object
    djs = DockerJenkinsServer(image_fullname=deployed['image'],
                              new_volume_name=volumes_named_only[0],
                              container_name=deployed['container'])

    # Initialize docker client
    if not djs.docker_client_init():
        print2('Failed to connect to local docker client')

    # Remove the resources
    if not djs.clean(remove_volume, remove_image):
        fail_out('Failed to remove Jenkins server')

    # Remove the deployment info file
    os.remove(filepath)

    print2(f'Successfully removed Jenkins server: {deployed["address"]}', bold=True, color='green')
