"""Account Menu CLI Entrypoints"""

import logging
import sys

import click

from yojenkins.cli import cli_utility as cu
from yojenkins.cli.cli_utility import log_to_history

# Getting the logger reference
logger = logging.getLogger()


@log_to_history
def list(opt_pretty: bool, opt_yaml: bool, opt_xml: bool, opt_toml: bool, opt_list: bool, profile: str) -> None:
    """TODO Docstring

    Details: TODO

    Args:
        TODO

    Returns:
        TODO
    """
    yj_obj = cu.config_yo_jenkins(profile)
    data, data_list = yj_obj.account.list()
    if not data:
        click.echo(click.style('failed', fg='bright_red', bold=True))
        sys.exit(1)
    data = data_list if opt_list else data
    cu.standard_out(data, opt_pretty, opt_yaml, opt_xml, opt_toml)


@log_to_history
def info(opt_pretty: bool, opt_yaml: bool, opt_xml: bool, opt_toml: bool, profile: str, user_id: str) -> None:
    """TODO Docstring

    Details: TODO

    Args:
        TODO

    Returns:
        TODO
    """
    yj_obj = cu.config_yo_jenkins(profile)
    data = yj_obj.account.info(user_id=user_id)
    if not data:
        click.echo(click.style('failed', fg='bright_red', bold=True))
        sys.exit(1)
    cu.standard_out(data, opt_pretty, opt_yaml, opt_xml, opt_toml)


@log_to_history
def create(profile: str, user_id: str, password: str, is_admin: bool, email: str, description: str) -> None:
    """TODO Docstring

    Details: TODO

    Args:
        TODO

    Returns:
        TODO
    """
    yj_obj = cu.config_yo_jenkins(profile)
    data = yj_obj.account.create(user_id=user_id,
                                 password=password,
                                 is_admin=is_admin,
                                 email=email,
                                 description=description)
    if not data:
        click.echo(click.style('failed', fg='bright_red', bold=True))
        sys.exit(1)
    click.echo(click.style('success', fg='bright_green', bold=True))


@log_to_history
def delete(profile: str, user_id: str) -> None:
    """TODO Docstring

    Details: TODO

    Args:
        TODO

    Returns:
        TODO
    """
    yj_obj = cu.config_yo_jenkins(profile)
    data = yj_obj.account.delete(user_id=user_id)
    if not data:
        click.echo(click.style('failed', fg='bright_red', bold=True))
        sys.exit(1)
    click.echo(click.style('success', fg='bright_green', bold=True))


@log_to_history
def permission(profile: str, user_id: str, action: str, permission_id: str) -> None:
    """TODO Docstring

    Details: TODO

    Args:
        TODO

    Returns:
        TODO
    """
    yj_obj = cu.config_yo_jenkins(profile)
    data = yj_obj.account.permission(user_id=user_id, action=action, permission_id=permission_id)
    if not data:
        click.echo(click.style('failed', fg='bright_red', bold=True))
        sys.exit(1)
    click.echo(click.style('success', fg='bright_green', bold=True))


@log_to_history
def permission_list(opt_pretty: bool, opt_yaml: bool, opt_xml: bool, opt_toml: bool, opt_list: bool,
                    profile: str) -> None:
    """TODO Docstring

    Details: TODO

    Args:
        TODO

    Returns:
        TODO
    """
    yj_obj = cu.config_yo_jenkins(profile)
    data, data_list = yj_obj.account.permission_list()
    if not data:
        click.echo(click.style('failed', fg='bright_red', bold=True))
        sys.exit(1)
    data = data_list if opt_list else data
    cu.standard_out(data, opt_pretty, opt_yaml, opt_xml, opt_toml)
