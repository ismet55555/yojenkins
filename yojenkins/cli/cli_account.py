"""Account Menu CLI Entrypoints"""

import logging

import click

from yojenkins.cli import cli_utility as cu
from yojenkins.cli.cli_utility import log_to_history

# Getting the logger reference
logger = logging.getLogger()


@log_to_history
def list(profile: str, token: str, opt_list: bool, **kwargs) -> None:
    """List all users

    Args:
        profile: The profile/account to use
        token:   API token for Jenkins server
        opt_list: Option to list the available profiles
    """
    yj_obj = cu.config_yo_jenkins(profile, token)
    data, data_list = yj_obj.account.list()
    data = data_list if opt_list else data
    cu.standard_out(data, **kwargs)


@log_to_history
def info(profile: str, token: str, user_id: str, **kwargs) -> None:
    """Get user information

    Args:
        profile: The profile/account to use
        token:   API token for Jenkins server
        opt_list: Option to list the available profiles
        user_id: The user id to look up
    """
    yj_obj = cu.config_yo_jenkins(profile, token)
    data = yj_obj.account.info(user_id=user_id)
    cu.standard_out(data, **kwargs)


@log_to_history
def create(profile: str, token: str, user_id: str, password: str, is_admin: bool, email: str,
           description: str) -> None:
    """Delete a user account

    Args:
        profile: The profile/account to use
        token:   API token for Jenkins server
        user_id: The user id to look up
        password: The password to set for this user
        is_admin: Is this user an admin
        email: The email address for this user
        description: The description for this user
    """
    yj_obj = cu.config_yo_jenkins(profile, token)
    yj_obj.account.create(user_id=user_id, password=password, is_admin=is_admin, email=email, description=description)
    click.secho('success', fg='bright_green', bold=True)


@log_to_history
def delete(profile: str, token: str, user_id: str) -> None:
    """Delete a user account

    Args:
        profile: The profile/account to use
        token:   API token for Jenkins server
        user_id: The user id to look up
    """
    yj_obj = cu.config_yo_jenkins(profile, token)
    yj_obj.account.delete(user_id=user_id)
    click.secho('success', fg='bright_green', bold=True)


@log_to_history
def permission(profile: str, token: str, user_id: str, action: str, permission_id: str) -> None:
    """Add or remove user permission

    Args:
        profile: The profile/account to use
        token:   API token for Jenkins server
        user_id: The user id to look up
        action: The action to perform ("add" or "remove")
        permission_id: The permission to add or remove to action
    """
    yj_obj = cu.config_yo_jenkins(profile, token)
    yj_obj.account.permission(user_id=user_id, action=action, permission_id=permission_id)
    click.secho('success', fg='bright_green', bold=True)


@log_to_history
def permission_list(profile: str, token: str, opt_list: bool, **kwargs) -> None:
    """List all available permissions

    Args:
        profile: The profile/account to use
        token:   API token for Jenkins server
        opt_list: Option to list the available profiles
    """
    yj_obj = cu.config_yo_jenkins(profile, token)
    data, data_list = yj_obj.account.permission_list()
    data = data_list if opt_list else data
    cu.standard_out(data, **kwargs)
