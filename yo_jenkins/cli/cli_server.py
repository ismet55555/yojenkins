#!/usr/bin/env python3

import json
import logging
from pprint import pprint
import sys
import os

import click
from Setup import DockerJenkinsServer
from YoJenkins import Auth, YoJenkins

from . import cli_utility as cu

# Getting the logger reference
logger = logging.getLogger()


def info(opt_pretty:bool, opt_yaml:bool, opt_xml:bool, profile:str) -> None:
    """TODO Docstring

    Details: TODO

    Args:
        TODO

    Returns:
        TODO
    """
    JY = cu.config_YoJenkins(profile)

    # Request the data
    data = JY.Server.info()
    if not data:
        click.echo(click.style(f'No server information', fg='bright_red', bold=True))
        sys.exit(1)

    # Console output
    cu.standard_out(data, opt_pretty, opt_yaml, opt_xml)


def user(opt_pretty:bool, opt_yaml:bool, opt_xml:bool, profile:str) -> None:
    """TODO Docstring

    Details: TODO

    Args:
        TODO

    Returns:
        TODO
    """
    JY = cu.config_YoJenkins(profile)

    # Request the data
    data = JY.Server.user_info()
    if not data:
        click.echo(click.style(f'No user info found', fg='bright_red', bold=True))
        sys.exit(1)

    # Console output
    cu.standard_out(data, opt_pretty, opt_yaml, opt_xml)


def queue(opt_pretty:bool, opt_yaml:bool, opt_xml:bool, profile:str, opt_list:bool) -> None:
    """TODO Docstring

    Details: TODO

    Args:
        TODO

    Returns:
        TODO
    """
    JY = cu.config_YoJenkins(profile)

    # Request the data
    if opt_list:
        data = JY.Server.queue_list()  # TODO: Combine with server_queue_list adding a list argument
    else:
        data = JY.Server.queue_info()
    if not data:
        click.echo(click.style(f'No build queue found', fg='bright_red', bold=True))
        sys.exit(1)

    # Console output
    cu.standard_out(data, opt_pretty, opt_yaml, opt_xml)


def plugins(opt_pretty:bool, opt_yaml:bool, opt_xml:bool, profile:str, opt_list:bool) -> None:
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

    output = data_list if opt_list else data
    cu.standard_out(output, opt_pretty, opt_yaml, opt_xml)


def browser(profile:str) -> None:
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


def reachable(profile:str, timeout:int) -> None:
    """TODO Docstring

    Details: TODO

    Args:
        TODO

    Returns:
        TODO
    """
    # TODO: Add --timeout as an option

    A = Auth()
    if not A.get_configurations(profile):
        click.echo(click.style(f'Failed to find any credentials', fg='bright_red', bold=True))
        sys.exit(1)
    JY = YoJenkins(Auth_obj=A)
    
    data = JY.REST.is_reachable(A.jenkins_profile['jenkins_server_url'], timeout=timeout)
    if not data:
        click.echo(click.style(f'false', fg='bright_red', bold=True))
        sys.exit(1)

    click.echo(click.style('true', fg='bright_green', bold=True))


def quite():
    """TODO Docstring

    Details: TODO

    Args:
        TODO

    Returns:
        TODO
    """
    pass


def wait_normal():
    """TODO Docstring

    Details: TODO

    Args:
        TODO

    Returns:
        TODO
    """
    pass


def restart():
    """TODO Docstring

    Details: TODO

    Args:
        TODO

    Returns:
        TODO
    """
    pass


def shutdown():
    """TODO Docstring

    Details: TODO

    Args:
        TODO

    Returns:
        TODO
    """
    pass


def server_deploy(config_file: str, plugins_file: str, protocol_schema: str, host: str, port: int, image_base: str, image_rebuild: bool, new_volume: bool, new_volume_name: str, bind_mount_dir: str, container_name: str, registry: str) -> None:
    """TODO Docstring

    Details: TODO

    Args:
        TODO

    Returns:
        TODO
    """
    # Creat object
    DJS = DockerJenkinsServer(
        config_file=config_file,
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
        registry=registry
        )
    
    # Initialize docker client
    if not DJS.docker_client_init():
        click.echo(click.style(f'Failed to connect to local docker client', fg='bright_red', bold=True))
        sys.exit(1)

    # Setup the server
    deployed, success = DJS.setup()
    if not success:
        click.echo(click.style(f'Failed to setup server', fg='bright_red', bold=True))
        click.echo(click.style(f'Items deployed:', fg='bright_red', bold=True))
        click.echo(click.style(deployed, fg='bright_red', bold=True))
        sys.exit(1)

    # Write current server docker attributes to file
    filepath = os.path.join(os.getcwd(), 'yo_jenkins/server_docker_settings/last_deploy_info.json')
    with open(os.path.join(filepath), 'w') as file:
        json.dump(deployed, file)

    volumes_named = [ list(l.values())[0] for l in deployed["volumes"] ]

    click.echo(click.style('Successfully created containerized Jenkins server!', fg='bright_green', bold=True))
    click.echo(click.style(f'   - Docker image:      {deployed["image"]}', fg='bright_green', bold=True))
    click.echo(click.style(f'   - Docker volumes:    {deployed["container"]}', fg='bright_green', bold=True))
    click.echo(click.style(f'   - Docker container:  {", ".join(volumes_named)}', fg='bright_green', bold=True))
    click.echo(click.style(f'   - Server address:    {deployed["address"]}', fg='bright_green', bold=True))



def server_teardown():
    """TODO Docstring

    Details: TODO

    Args:
        TODO

    Returns:
        TODO
    """
    # Load deployment info file with deployment information
    filepath = os.path.join(os.getcwd(), 'yo_jenkins/server_docker_settings/last_deploy_info.json')
    try:
        with open(os.path.join(filepath), 'r') as file:
            deployed = json.load(file)
    except Exception as e:
        click.echo(click.style(f'Failed to detect a previous server deployment', fg='bright_red', bold=True))
        click.echo(click.style(f'If you think there was a successfully deployment, use Docker to remove manually', fg='bright_red', bold=True))
        sys.exit(1)

    # Filter out named volumes only
    volumes_named_only = [ list(l.values())[0] for l in deployed["volumes"] if 'named' in l]

    # Creat object
    DJS = DockerJenkinsServer(
        image_fullname=deployed['image'],
        new_volume_name=volumes_named_only[0],
        container_name=deployed['container']
        )

    # Initialize docker client
    if not DJS.docker_client_init():
        click.echo(click.style(f'Failed to connect to local docker client', fg='bright_red', bold=True))
        sys.exit(1)

    # Remove the resources
    if not DJS.all_clean():
        click.echo(click.style(f'Failed to remove Jenkins server', fg='bright_red', bold=True))
        sys.exit(1)

    # Remove the deployment info file
    os.remove(filepath)

    click.echo(click.style(f'Successfully removed Jenkins server: {deployed["address"]}', fg='bright_green', bold=True))