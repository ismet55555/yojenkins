#!/usr/bin/env python3

import logging
import sys

import click
from yo_jenkins.Cli import cli_utility as cu
from yo_jenkins.YoJenkins import REST, Auth

# Getting the logger reference
logger = logging.getLogger()


def configure(api_token: str) -> None:
    """TODO Docstring

    Details: TODO

    Args:
        TODO

    Returns:
        TODO
    """
    # Request the data
    if not Auth().configure(api_token=api_token):
        click.echo(click.style('Failed to configure credentials file', fg='bright_red', bold=True))
        sys.exit(1)
    click.echo(click.style('Successfully configured credentials file', fg='bright_green', bold=True))


def token(profile: str) -> None:
    """TODO Docstring

    Details: TODO

    Args:
        TODO

    Returns:
        TODO
    """
    auth = Auth()

    if profile:
        # Add/Refresh the newly generated API token for an existing profile
        data = auth.profile_add_new_token(profile_name=profile)
    else:
        # Simply display the new API Token
        data = auth.generate_token()
    if not data:
        click.echo(click.style('Failed to generate API token', fg='bright_red', bold=True))
        sys.exit(1)
    click.echo(click.style(data, fg='bright_green', bold=True))


def show(opt_pretty: bool, opt_yaml: bool, opt_xml: bool, opt_toml: bool) -> None:
    """TODO Docstring

    Details: TODO

    Args:
        TODO

    Returns:
        TODO
    """
    data = Auth().show_local_credentials()
    if not data:
        click.echo(click.style('Failed to find or read local configuration file', fg='bright_red', bold=True))
        sys.exit(1)

    cu.standard_out(data, opt_pretty, opt_yaml, opt_xml, opt_toml)


def verify(profile: str) -> None:
    """TODO Docstring

    Details: TODO

    Args:
        TODO

    Returns:
        TODO
    """
    auth = Auth(REST())

    # Get the credential profile
    if not auth.get_configurations(profile):
        click.echo(click.style('failed', fg='bright_red', bold=True))
        sys.exit(1)

    # Create authentication
    if not auth.create_auth():
        click.echo(click.style('failed', fg='bright_red', bold=True))
        sys.exit(1)

    click.echo(click.style('success', fg='bright_green', bold=True))


def user(opt_pretty: bool, opt_yaml: bool, opt_xml: bool, opt_toml: bool, profile: str) -> None:
    """TODO Docstring

    Details: TODO

    Args:
        TODO

    Returns:
        TODO
    """
    # Request the data
    data = cu.config_yo_jenkins(profile).Auth.user()
    if not data:
        click.echo(click.style('failed', fg='bright_red', bold=True))
        sys.exit(1)

    # Console output
    cu.standard_out(data, opt_pretty, opt_yaml, opt_xml, opt_toml)
