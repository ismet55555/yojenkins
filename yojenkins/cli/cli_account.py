"""Account Menu CLI Entrypoints"""

import logging

import click

from yojenkins.cli import cli_utility as cu
from yojenkins.cli.cli_utility import log_to_history

# Getting the logger reference
logger = logging.getLogger()


@log_to_history
def list(opt_pretty: bool, opt_yaml: bool, opt_xml: bool, opt_toml: bool, opt_list: bool, profile: str) -> None:
    """List all users

    Args:
        opt_pretty: Option to pretty print the output
        opt_yaml: Option to output in YAML format
        opt_xml: Option to output in XML format
        opt_toml: Option to output in TOML format
        opt_list: Option to list the available profiles
        profile: The profile/account to use

    Returns:
        None
    """
    yj_obj = cu.config_yo_jenkins(profile)
    data, data_list = yj_obj.account.list()
    data = data_list if opt_list else data
    cu.standard_out(data, opt_pretty, opt_yaml, opt_xml, opt_toml)


@log_to_history
def info(opt_pretty: bool, opt_yaml: bool, opt_xml: bool, opt_toml: bool, profile: str, user_id: str) -> None:
    """Get user information

    Args:
        opt_pretty: Option to pretty print the output
        opt_yaml: Option to output in YAML format
        opt_xml: Option to output in XML format
        opt_toml: Option to output in TOML format
        opt_list: Option to list the available profiles
        profile: The profile/account to use
        user_id: The user id to look up

    Returns:
        None
    """
    yj_obj = cu.config_yo_jenkins(profile)
    data = yj_obj.account.info(user_id=user_id)
    cu.standard_out(data, opt_pretty, opt_yaml, opt_xml, opt_toml)


@log_to_history
def create(profile: str, user_id: str, password: str, is_admin: bool, email: str, description: str) -> None:
    """Delete a user account

    Args:
        profile: The profile/account to use
        user_id: The user id to look up
        password: The password to set for this user
        is_admin: Is this user an admin
        email: The email address for this user
        description: The description for this user

    Returns:
        None
    """
    yj_obj = cu.config_yo_jenkins(profile)
    data = yj_obj.account.create(user_id=user_id,
                                 password=password,
                                 is_admin=is_admin,
                                 email=email,
                                 description=description)
    click.secho('success', fg='bright_green', bold=True)


@log_to_history
def delete(profile: str, user_id: str) -> None:
    """Delete a user account

    Args:
        profile: The profile/account to use
        user_id: The user id to look up

    Returns:
        None
    """
    yj_obj = cu.config_yo_jenkins(profile)
    data = yj_obj.account.delete(user_id=user_id)
    click.secho('success', fg='bright_green', bold=True)


@log_to_history
def permission(profile: str, user_id: str, action: str, permission_id: str) -> None:
    """Add or remove user permission

    Args:
        profile: The profile/account to use
        user_id: The user id to look up
        action: The action to perform ("add" or "remove")
        permission_id: The permission to add or remove to action

    Returns:
        None
    """
    yj_obj = cu.config_yo_jenkins(profile)
    data = yj_obj.account.permission(user_id=user_id, action=action, permission_id=permission_id)
    click.secho('success', fg='bright_green', bold=True)


@log_to_history
def permission_list(opt_pretty: bool, opt_yaml: bool, opt_xml: bool, opt_toml: bool, opt_list: bool,
                    profile: str) -> None:
    """List all available permissions

    Args:
        opt_pretty: Option to pretty print the output
        opt_yaml: Option to output in YAML format
        opt_xml: Option to output in XML format
        opt_toml: Option to output in TOML format
        opt_list: Option to list the available profiles
        profile: The profile/account to use

    Returns:
        None
    """
    yj_obj = cu.config_yo_jenkins(profile)
    data, data_list = yj_obj.account.permission_list()
    data = data_list if opt_list else data
    cu.standard_out(data, opt_pretty, opt_yaml, opt_xml, opt_toml)
