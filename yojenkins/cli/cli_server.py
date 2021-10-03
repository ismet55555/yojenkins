"""Server Menu CLI Entrypoints"""

import json
import logging
import os
import sys

import click

from yojenkins.cli import cli_utility as cu
from yojenkins.cli.cli_utility import log_to_history
from yojenkins.docker_container import DockerJenkinsServer
from yojenkins.utility.utility import get_project_dir, get_resource_path
from yojenkins.yo_jenkins import Auth, YoJenkins

# Getting the logger reference
logger = logging.getLogger()


@log_to_history
def info(opt_pretty: bool, opt_yaml: bool, opt_xml: bool, opt_toml: bool, profile: str) -> None:
    """TODO Docstring

    Details: TODO

    Args:
        TODO

    Returns:
        TODO
    """
    data = cu.config_yo_jenkins(profile).server.info()
    if not data:
        click.echo(click.style('failed', fg='bright_red', bold=True))
        sys.exit(1)
    cu.standard_out(data, opt_pretty, opt_yaml, opt_xml, opt_toml)


@log_to_history
def people(opt_pretty: bool, opt_yaml: bool, opt_xml: bool, opt_toml: bool, profile: str, opt_list: bool) -> None:
    """TODO Docstring

    Details: TODO

    Args:
        TODO

    Returns:
        TODO
    """
    data, data_list = cu.config_yo_jenkins(profile).server.people()
    if not data:
        click.echo(click.style('failed', fg='bright_red', bold=True))
        sys.exit(1)
    data = data_list if opt_list else data
    cu.standard_out(data, opt_pretty, opt_yaml, opt_xml, opt_toml)


@log_to_history
def queue(opt_pretty: bool, opt_yaml: bool, opt_xml: bool, opt_toml: bool, profile: str, opt_list: bool) -> None:
    """TODO Docstring

    Details: TODO

    Args:
        TODO

    Returns:
        TODO
    """
    yj_obj = cu.config_yo_jenkins(profile)
    if opt_list:
        data = yj_obj.server.queue_list()  # TODO: Combine with server_queue_list adding a list argument
    else:
        data = yj_obj.server.queue_info()
    if not data:
        click.echo(click.style('failed', fg='bright_red', bold=True))
        sys.exit(1)
    cu.standard_out(data, opt_pretty, opt_yaml, opt_xml, opt_toml)


@log_to_history
def plugins(opt_pretty: bool, opt_yaml: bool, opt_xml: bool, opt_toml: bool, profile: str, opt_list: bool) -> None:
    """TODO Docstring

    Details: TODO

    Args:
        TODO

    Returns:
        TODO
    """
    data, data_list = cu.config_yo_jenkins(profile).server.plugin_list()
    if not data:
        click.echo(click.style('failed', fg='bright_red', bold=True))
        sys.exit(1)
    data = data_list if opt_list else data
    cu.standard_out(data, opt_pretty, opt_yaml, opt_xml, opt_toml)


@log_to_history
def browser(profile: str) -> None:
    """TODO Docstring

    Args:
        TODO

    Returns:
        TODO
    """
    data = cu.config_yo_jenkins(profile).server.browser_open()
    if not data:
        click.echo(click.style('failed', fg='bright_red', bold=True))
        sys.exit(1)


@log_to_history
def reachable(profile: str, timeout: int) -> None:
    """TODO Docstring

    Details: TODO

    Args:
        TODO

    Returns:
        TODO
    """
    auth = Auth()
    if not auth.get_credentials(profile):
        click.echo(click.style('failed to find any credentials', fg='bright_red', bold=True))
        sys.exit(1)
    if not YoJenkins(auth=auth).rest.is_reachable(auth.jenkins_profile['jenkins_server_url'], timeout=timeout):
        click.echo(click.style('false', fg='bright_red', bold=True))
        sys.exit(1)
    click.echo(click.style('true', fg='bright_green', bold=True))


@log_to_history
def quiet(profile: str, off: bool):
    """TODO Docstring

    Details: TODO

    Args:
        TODO

    Returns:
        TODO
    """
    if not cu.config_yo_jenkins(profile).server.quiet(off=off):
        click.echo(click.style('failed', fg='bright_red', bold=True))
        sys.exit(1)
    click.echo(click.style('success', fg='bright_green', bold=True))


@log_to_history
def restart(profile: str, force: bool):
    """TODO Docstring

    Details: TODO

    Args:
        TODO

    Returns:
        TODO
    """
    if not cu.config_yo_jenkins(profile).server.restart(force=force):
        click.echo(click.style('failed', fg='bright_red', bold=True))
        sys.exit(1)
    click.echo(click.style('success', fg='bright_green', bold=True))


@log_to_history
def shutdown(profile: str, force: bool):
    """TODO Docstring

    Details: TODO

    Args:
        TODO

    Returns:
        TODO
    """
    if not cu.config_yo_jenkins(profile).server.shutdown(force=force):
        click.echo(click.style('failed', fg='bright_red', bold=True))
        sys.exit(1)
    click.echo(click.style('success', fg='bright_green', bold=True))


@log_to_history
def server_deploy(config_file: str, plugins_file: str, protocol_schema: str, host: str, port: int, image_base: str,
                  image_rebuild: bool, new_volume: bool, new_volume_name: str, bind_mount_dir: str,
                  container_name: str, registry: str, admin_user: str, password: str) -> None:
    """TODO Docstring

    Details: TODO

    Args:
        TODO

    Returns:
        TODO
    """
    click.echo('Setting up a local Jenkins development server. Hold tight, this may take a minute ...')

    # TODO: Check if the docker server deployment file is there. If so, show that it is being renewed.

    # Creat object
    djs = DockerJenkinsServer(config_file=config_file,
                              plugins_file=plugins_file,
                              protocol_schema=protocol_schema,
                              host=host,
                              port=port,
                              image_base=image_base,
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
        click.echo(click.style('Failed to connect to local docker client', fg='bright_red', bold=True))
        sys.exit(1)

    # Setup the server
    deployed, success = djs.setup()
    if not success:
        click.echo(click.style('Failed to setup server', fg='bright_red', bold=True))
        click.echo(click.style('Items deployed for partial deployment:', fg='bright_red', bold=True))
        if deployed:
            click.echo(click.style(deployed, fg='bright_red', bold=True))
        sys.exit(1)

    # Write current server docker attributes to file
    filepath = os.path.join(get_project_dir(), 'resources', 'server_docker_settings', 'last_deploy_info.json')
    if not filepath:
        click.echo(click.style('Failed to find yojenkins included data directory', fg='bright_red', bold=True))
        sys.exit(1)
    logger.debug(f'Writing server deploy information to file: {filepath}')
    try:
        with open(os.path.join(filepath), 'w') as file:
            json.dump(deployed, file, indent=4, sort_keys=True)
    except PermissionError as error:
        logger.error(f'Server deployed, however failed to write server deploy information to file: {error}')
        logger.error('yojenkins resources may have been installed under root or a restricted account')
        sys.exit(1)

    volumes_named = [list(l.values())[0] for l in deployed["volumes"]]

    click.echo(click.style('Successfully created containerized Jenkins server!', fg='bright_green', bold=True))
    click.echo(click.style(f'   - Docker image:      {deployed["image"]}', fg='bright_green', bold=True))
    click.echo(click.style(f'   - Docker volumes:    {deployed["container"]}', fg='bright_green', bold=True))
    click.echo(click.style(f'   - Docker container:  {", ".join(volumes_named)}', fg='bright_green', bold=True))
    click.echo()
    click.echo(click.style(f'Address:  {deployed["address"]}', fg='bright_green', bold=True))
    click.echo(click.style(f'Username: {admin_user}', fg='bright_green', bold=True))
    click.echo(
        click.style(f'Password: {"*************" if password else "password (default)"}', fg='bright_green',
                    bold=True))


@log_to_history
def server_teardown(remove_volume: bool, remove_image: bool):
    """TODO Docstring

    Details: TODO

    Args:
        TODO

    Returns:
        TODO
    """
    # Load deployment info file with deployment information
    filepath = get_resource_path(os.path.join('resources', 'server_docker_settings', 'last_deploy_info.json'))
    logger.debug(f'Detecting server deployment info file: {filepath} ...')
    try:
        with open(os.path.join(filepath), 'r') as file:
            deployed = json.load(file)
        logger.debug(f'Successfully found and loaded server deployment info file: {deployed}')
    except Exception:
        click.echo(click.style('Failed to detect a previous server deployment', fg='bright_red', bold=True))
        click.echo(
            click.style('If you think there was a previously successfull deployment, use Docker to remove it manually',
                        fg='bright_red',
                        bold=True))
        sys.exit(1)

    # Filter out named volumes only
    volumes_named_only = [list(l.values())[0] for l in deployed["volumes"] if 'named' in l]

    # Creat object
    djs = DockerJenkinsServer(image_fullname=deployed['image'],
                              new_volume_name=volumes_named_only[0],
                              container_name=deployed['container'])

    # Initialize docker client
    if not djs.docker_client_init():
        click.echo(click.style('Failed to connect to local docker client', fg='bright_red', bold=True))
        sys.exit(1)

    # Remove the resources
    if not djs.clean(remove_volume, remove_image):
        click.echo(click.style('Failed to remove Jenkins server', fg='bright_red', bold=True))
        sys.exit(1)

    # Remove the deployment info file
    os.remove(filepath)

    click.echo(click.style(f'Successfully removed Jenkins server: {deployed["address"]}', fg='bright_green',
                           bold=True))
