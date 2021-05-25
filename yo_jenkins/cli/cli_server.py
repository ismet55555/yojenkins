#!/usr/bin/env python3

import logging
import sys
from YoJenkins import YoJenkins
from YoJenkins import Auth
import click

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


def plugin(opt_pretty:bool, opt_yaml:bool, opt_xml:bool, profile:str, opt_list:bool) -> None:
    """TODO Docstring

    Details: TODO

    Args:
        TODO

    Returns:
        TODO
    """
    JY = cu.config_YoJenkins(profile)

    # TODO: Test on server with permission
    
    data, data_list = JY.Server.plugin_list()
    if not data:
        click.echo(click.style(f'No server plugin info found', fg='bright_red', bold=True))
        sys.exit(1)

    output = data_list if opt_list else data
    cu.standard_out(output, opt_pretty, opt_yaml, opt_xml)


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
    click

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

def server_make():
    """TODO Docstring

    Details: TODO

    Args:
        TODO

    Returns:
        TODO
    """
    pass

def server_remove():
    """TODO Docstring

    Details: TODO

    Args:
        TODO

    Returns:
        TODO
    """
    pass