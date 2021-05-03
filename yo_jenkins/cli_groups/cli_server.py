#!/usr/bin/env python3

import logging
import sys
from YoJenkins import YoJenkins
import click

from . import cli_utility

# Getting the logger reference
logger = logging.getLogger()


def info(opt_pretty:bool, opt_yaml:bool, opt_xml:bool, profile:str) -> None:
    '''
    TODO: Docstring
    '''
    J = cli_utility.config_auth_server(profile)

    # Request the data
    data = J.server_info()
    if not data:
        click.echo(click.style(f'No server information', fg='bright_red', bold=True))
        sys.exit(1)

    # Console output
    cli_utility.standard_out(data, opt_pretty, opt_yaml, opt_xml)


def user(opt_pretty:bool, opt_yaml:bool, opt_xml:bool, profile:str) -> None:
    '''
    TODO: Docstring
    '''
    J = cli_utility.config_auth_server(profile)

    # Request the data
    data = J.server_user_info()
    if not data:
        click.echo(click.style(f'No user info found', fg='bright_red', bold=True))
        sys.exit(1)

    # Console output
    cli_utility.standard_out(data, opt_pretty, opt_yaml, opt_xml)


def queue(opt_pretty:bool, opt_yaml:bool, opt_xml:bool, profile:str, opt_list:bool) -> None:
    '''
    TODO: Docstring
    '''
    J = cli_utility.config_auth_server(profile)

    # Request the data
    if opt_list:
        data = J.server_queue_list()  # TODO: Combine with server_queue_list adding a list argument
    else:
        data = J.server_queue_info()
    if not data:
        click.echo(click.style(f'No build queue found', fg='bright_red', bold=True))
        sys.exit(1)

    # Console output
    cli_utility.standard_out(data, opt_pretty, opt_yaml, opt_xml)


def plugin(opt_pretty:bool, opt_yaml:bool, opt_xml:bool, profile:str, opt_list:bool) -> None:
    '''
    TODO: Docstring
    '''
    J = cli_utility.config_auth_server(profile)

    # TODO: Test on server with permission
    
    data, data_list = J.server_plugin_list()
    if not data:
        click.echo(click.style(f'No server plugin info found', fg='bright_red', bold=True))
        sys.exit(1)

    output = data_list if opt_list else data
    cli_utility.standard_out(output, opt_pretty, opt_yaml, opt_xml)


def reachable(profile:str) -> None:
    '''
    TODO: Docstring
    '''
    J = YoJenkins()
    if not J.auth_get_configurations(profile):
        click.echo(click.style(f'Failed to find any credentials', fg='bright_red', bold=True))
        sys.exit(1)
    
    data = J.server_is_reachable()
    if not data:
        click.echo(click.style(f'false', fg='bright_red', bold=True))
        sys.exit(1)
    click

    click.echo(click.style('true', fg='bright_green', bold=True))


def quite():
    '''
    TODO: Docstring
    '''
    pass


def wait_normal():
    '''
    TODO: Docstring
    '''
    pass


def restart():
    '''
    TODO: Docstring
    '''
    pass


def shutdown():
    '''
    TODO: Docstring
    '''
    pass
