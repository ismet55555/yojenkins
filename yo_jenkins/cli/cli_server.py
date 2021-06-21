#!/usr/bin/env python3

import json
import logging
from pprint import pprint
import sys
import os

import click
from yo_jenkins.Setup import DockerJenkinsServer
from yo_jenkins.YoJenkins import Auth, YoJenkins
from yo_jenkins.Utility.utility import get_resource_path, get_resource_dir

from . import cli_utility as cu

# Getting the logger reference
logger = logging.getLogger()









def info(opt_pretty: bool, opt_yaml: bool, opt_xml: bool, opt_toml: bool, profile: str) -> None:
    """TODO Docstring

    Details: TODO

    Args:
        TODO

    Returns:
        TODO
    """
    JY = cu.config_YoJenkins(profile)
    data = JY.Server.info()
    if not data:
        click.echo(click.style(f'No server information', fg='bright_red', bold=True))
        sys.exit(1)
    cu.standard_out(data, opt_pretty, opt_yaml, opt_xml, opt_toml)


def people(opt_pretty: bool, opt_yaml: bool, opt_xml: bool, opt_toml: bool, profile: str, opt_list: bool) -> None:
    """TODO Docstring

    Details: TODO

    Args:
        TODO

    Returns:
        TODO
    """
    JY = cu.config_YoJenkins(profile)
    data, data_list = JY.Server.people()
    if not data:
        click.echo(click.style(f'failed', fg='bright_red', bold=True))
        sys.exit(1)
    data = data_list if opt_list else data
    cu.standard_out(data, opt_pretty, opt_yaml, opt_xml, opt_toml)


def queue(opt_pretty: bool, opt_yaml: bool, opt_xml: bool, opt_toml: bool, profile: str, opt_list: bool) -> None:
    """TODO Docstring

    Details: TODO

    Args:
        TODO

    Returns:
        TODO
    """
    JY = cu.config_YoJenkins(profile)
    if opt_list:
        data = JY.Server.queue_list()  # TODO: Combine with server_queue_list adding a list argument
    else:
        data = JY.Server.queue_info()
    if not data:
        click.echo(click.style(f'No build queue found', fg='bright_red', bold=True))
        sys.exit(1)
    cu.standard_out(data, opt_pretty, opt_yaml, opt_xml, opt_toml)


def plugins(opt_pretty: bool, opt_yaml: bool, opt_xml: bool, opt_toml: bool, profile: str, opt_list: bool) -> None:
    """TODO Docstring

    Details: TODO

    Args:
        TODO

    Returns:
        TODO
    """
    JY = cu.config_YoJenkins(profile)
    data, data_list = JY.Server.plugin_list()
    if not data:
        click.echo(click.style(f'No server plugin info found', fg='bright_red', bold=True))
        sys.exit(1)

    data = data_list if opt_list else data
    cu.standard_out(data, opt_pretty, opt_yaml, opt_xml, opt_toml)


def browser(profile: str) -> None:
    """TODO Docstring

    Args:
        TODO

    Returns:
        TODO
    """
    JY = cu.config_YoJenkins(profile)
    data = JY.Server.browser_open()
    if not data:
        click.echo(click.style(f'failed', fg='bright_red', bold=True))
        sys.exit(1)


def reachable(profile: str, timeout: int) -> None:
    """TODO Docstring

    Details: TODO

    Args:
        TODO

    Returns:
        TODO
    """
    A = Auth()
    if not A.get_configurations(profile):
        click.echo(click.style(f'Failed to find any credentials', fg='bright_red', bold=True))
        sys.exit(1)
    JY = YoJenkins(Auth_obj=A)
    if not JY.REST.is_reachable(A.jenkins_profile['jenkins_server_url'], timeout=timeout):
        click.echo(click.style(f'false', fg='bright_red', bold=True))
        sys.exit(1)
    click.echo(click.style('true', fg='bright_green', bold=True))


def quiet(profile: str, off: bool):
    """TODO Docstring

    Details: TODO

    Args:
        TODO

    Returns:
        TODO
    """
    JY = cu.config_YoJenkins(profile)
    if not JY.Server.quiet(off=off):
        click.echo(click.style(f'failed', fg='bright_red', bold=True))
        sys.exit(1)
    click.echo(click.style('success', fg='bright_green', bold=True))


def restart(profile: str, force: bool):
    """TODO Docstring

    Details: TODO

    Args:
        TODO

    Returns:
        TODO
    """
    JY = cu.config_YoJenkins(profile)
    if not JY.Server.restart(force=force):
        click.echo(click.style(f'failed', fg='bright_red', bold=True))
        sys.exit(1)
    click.echo(click.style('success', fg='bright_green', bold=True))


def shutdown(profile: str, force: bool):
    """TODO Docstring

    Details: TODO

    Args:
        TODO

    Returns:
        TODO
    """
    JY = cu.config_YoJenkins(profile)
    if not JY.Server.shutdown(force=force):
        click.echo(click.style(f'failed', fg='bright_red', bold=True))
        sys.exit(1)
    click.echo(click.style('success', fg='bright_green', bold=True))


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
    click.echo(f'Setting up a local Jenkins development server. Hold tight, this may take a minute ...')

    # TODO: Check if the docker server deployment file is there. If so, show that it is being renewed.

    # Creat object
    DJS = DockerJenkinsServer(config_file=config_file,
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
    if not DJS.docker_client_init():
        click.echo(click.style(f'Failed to connect to local docker client', fg='bright_red', bold=True))
        sys.exit(1)

    # Setup the server
    deployed, success = DJS.setup()
    if not success:
        click.echo(click.style(f'Failed to setup server', fg='bright_red', bold=True))
        click.echo(click.style(f'Items deployed for partial deployment:', fg='bright_red', bold=True))
        if deployed:
            click.echo(click.style(deployed, fg='bright_red', bold=True))
        sys.exit(1)

    # Write current server docker attributes to file
    filepath = os.path.join(get_resource_dir(), 'server_docker_settings', 'last_deploy_info.json')
    if not filepath:
        click.echo(click.style(f'Failed to find yo-jenkins included data directory', fg='bright_red', bold=True))
        sys.exit(1)
    logger.debug(f'Writing server deploy information to file: {filepath}')
    with open(os.path.join(filepath), 'w') as file:
        json.dump(deployed, file, indent=4, sort_keys=True)

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


def server_teardown(remove_volume: bool, remove_image: bool):
    """TODO Docstring

    Details: TODO

    Args:
        TODO

    Returns:
        TODO
    """
    # Load deployment info file with deployment information
    filepath = get_resource_path(os.path.join('server_docker_settings', 'last_deploy_info.json'))
    logger.debug(f'Detecting server deployment info file: {filepath} ...')
    try:
        with open(os.path.join(filepath), 'r') as file:
            deployed = json.load(file)
        logger.debug(f'Successfully found and loaded server deployment info file: {deployed}')
    except Exception as e:
        click.echo(click.style(f'Failed to detect a previous server deployment', fg='bright_red', bold=True))
        click.echo(
            click.style(
                f'If you think there was a previously successfull deployment, use Docker to remove it manually',
                fg='bright_red',
                bold=True))
        sys.exit(1)

    # Filter out named volumes only
    volumes_named_only = [list(l.values())[0] for l in deployed["volumes"] if 'named' in l]

    # Creat object
    DJS = DockerJenkinsServer(image_fullname=deployed['image'],
                              new_volume_name=volumes_named_only[0],
                              container_name=deployed['container'])

    # Initialize docker client
    if not DJS.docker_client_init():
        click.echo(click.style(f'Failed to connect to local docker client', fg='bright_red', bold=True))
        sys.exit(1)

    # Remove the resources
    if not DJS.clean(remove_volume, remove_image):
        click.echo(click.style(f'Failed to remove Jenkins server', fg='bright_red', bold=True))
        sys.exit(1)

    # Remove the deployment info file
    os.remove(filepath)

    click.echo(click.style(f'Successfully removed Jenkins server: {deployed["address"]}', fg='bright_green',
                           bold=True))
