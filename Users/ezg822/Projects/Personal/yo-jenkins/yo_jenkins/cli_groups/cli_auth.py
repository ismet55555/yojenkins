#!/usr/bin/env python3

import logging
import sys

import click
from YoJenkins import YoJenkins

from . import cli_utility

# Getting the logger reference
logger = logging.getLogger()


def configure(token:str) -> None:
    '''
    TODO: Docstring
    '''
    J = YoJenkins()

    # Request the data
    success = J.auth_configure(api_token=token)
    if not success:
        click.echo(click.style(f'Failed to configure credentials file', fg='bright_red', bold=True))
        sys.exit(1)

    click.echo(click.style(f'Successfully configured credentials file', fg='bright_green', bold=True))


def token(profile:str) -> None:
    '''
    TODO: Docstring
    '''
    J = YoJenkins()

    if profile:
        # Add/Refresh the newly generated API token for an existing profile
        data = J.auth_profile_add_new_token(profile_name=profile)
    else:
        # Simply display the new API Token
        data = J.auth_generate_token()
    if not data:
        click.echo(click.style(f'Failed to generate API token', fg='bright_red', bold=True))
        sys.exit(1)

    click.echo(click.style(data, fg='bright_green', bold=True))


def show(opt_pretty:bool, opt_yaml:bool, opt_xml:bool) -> None:
    '''
    TODO: Docstring
    '''
    J = YoJenkins()

    data = J.auth_show_local_credentials()
    if not data:
        click.echo(click.style(f'Failed to find or read local configuration file', fg='bright_red', bold=True))
        sys.exit(1)

    cli_utility.standard_out(data, opt_pretty, opt_yaml, opt_xml)


def verify(profile:str) -> None:
    '''
    TODO: Docstring
    '''
    J = cli_utility.config_auth_server(profile)

    # Add/Refresh the newly generated API token for an existing profile
    data = J.auth_verify_auth()
    if not data:
        click.echo(click.style(f'false', fg='bright_red', bold=True))
        sys.exit(1)

    click.echo(click.style('true', fg='bright_green', bold=True))

