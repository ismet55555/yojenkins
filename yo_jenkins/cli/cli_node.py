#!/usr/bin/env python3

import json
import logging
import os
import sys

import click
from yo_jenkins.Docker import DockerJenkinsServer
from yo_jenkins.Utility.utility import get_project_dir, get_resource_path
from yo_jenkins.YoJenkins import Auth, YoJenkins

from yo_jenkins.cli import cli_utility as cu
from yo_jenkins.cli.cli_utility import log_to_history

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
    # TODO
    pass


@log_to_history
def node_deploy() -> None:
    """TODO Docstring

    Details: TODO

    Args:
        TODO

    Returns:
        TODO
    """
    click.echo('Setting up a local node/agent server. Hold tight, this may take a minute ...')

    sys.exit(0)

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
        click.echo(click.style('Failed to find yo-jenkins included data directory', fg='bright_red', bold=True))
        sys.exit(1)
    logger.debug(f'Writing server deploy information to file: {filepath}')
    try:
        with open(os.path.join(filepath), 'w') as file:
            json.dump(deployed, file, indent=4, sort_keys=True)
    except PermissionError as error:
        logger.error(f'Server deployed, however failed to write server deploy information to file: {error}')
        logger.error('yo-jenkins resources may have been installed under root or a restricted account')
        sys.exit(1)

    volumes_named = [list(l.values())[0] for l in deployed["volumes"]]
