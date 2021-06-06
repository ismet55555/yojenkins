#!/usr/bin/env python3

import logging
import sys

import click
from yo_jenkins.cli import cli_utility as cu
from yo_jenkins.YoJenkins import REST, Auth

# Getting the logger reference
logger = logging.getLogger()


def configure(token:str) -> None:
    """TODO Docstring

    Details: TODO

    Args:
        TODO

    Returns:
        TODO
    """
    # Request the data
    success = Auth().configure(api_token=token)
    if not success:
        click.echo(click.style(f'Failed to configure credentials file', fg='bright_red', bold=True))
        sys.exit(1)

    click.echo(click.style(f'Successfully configured credentials file', fg='bright_green', bold=True))


def token(profile:str) -> None:
    """TODO Docstring

    Details: TODO

    Args:
        TODO

    Returns:
        TODO
    """
    A = Auth()

    if profile:
        # Add/Refresh the newly generated API token for an existing profile
        data = A.profile_add_new_token(profile_name=profile)
    else:
        # Simply display the new API Token
        data = A.generate_token()
    if not data:
        click.echo(click.style(f'Failed to generate API token', fg='bright_red', bold=True))
        sys.exit(1)

    click.echo(click.style(data, fg='bright_green', bold=True))


def show(opt_pretty:bool, opt_yaml:bool, opt_xml:bool) -> None:
    """TODO Docstring

    Details: TODO

    Args:
        TODO

    Returns:
        TODO
    """
    A = Auth()

    data = A.show_local_credentials()
    if not data:
        click.echo(click.style(f'Failed to find or read local configuration file', fg='bright_red', bold=True))
        sys.exit(1)

    cu.standard_out(data, opt_pretty, opt_yaml, opt_xml)


def verify(profile:str) -> None:
    """TODO Docstring

    Details: TODO

    Args:
        TODO

    Returns:
        TODO
    """
    R = REST()
    A = Auth(R)

    # TODO: Rename configurations to credentials

    # Get the credential profile
    if not A.get_configurations(profile):
        click.echo(click.style(f'false', fg='bright_red', bold=True))
        sys.exit(1)

    # Create authentication
    if not A.create_auth():
        click.echo(click.style(f'false', fg='bright_red', bold=True))
        sys.exit(1)

    click.echo(click.style('true', fg='bright_green', bold=True))


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
    data = JY.Auth.user()
    if not data:
        click.echo(click.style(f'failed', fg='bright_red', bold=True))
        sys.exit(1)

    # Console output
    cu.standard_out(data, opt_pretty, opt_yaml, opt_xml)
