"""Auth Menu CLI Entrypoints"""

import logging

import click

from yojenkins.cli import cli_utility as cu
from yojenkins.cli.cli_utility import log_to_history
from yojenkins.yo_jenkins import Auth, Rest

# Getting the logger reference
logger = logging.getLogger()


@log_to_history
def configure(auth_file: str) -> None:
    """Configure yojenkins authentication profile(s)

    Args:
        auth_file: (Optional) Path to the the authentication setup JSON file
    """
    Auth().configure(auth_file)
    click.secho('Successfully configured credentials file', fg='bright_green', bold=True)


# @log_to_history
# def remove(profile: str) -> None:
#     """Remove yojenkins authentication profile(s)
#
#     Args:
#         profile: The yojenkins profile name to remove from credentials
#     """
#     Auth().remove(profile_name=profile)
#     click.secho('Successfully removed credentials profile', fg='bright_green', bold=True)


@log_to_history
def token(profile: str, token: str, name: str, server_base_url: str, username: str, password: str) -> None:
    """Generate authentication API token

    Args:
        profile: The profile/account to use
        token:   API Token for Jenkins server
        name: Name of the generated token
        server_base_url: Server base URL address
        username: Account username
        password: User password to use to generate API token
    """
    auth = Auth()

    if profile:
        # Add/Refresh the newly generated API token for an existing profile
        data = auth.profile_add_new_token(profile_name=profile, token=token, password=password)
    else:
        # Simply display/output the newly generated API Token
        if token:
            click.secho('Ignoring --token. Must be specfied with --profile', fg="yellow")
            print()
        data = auth.generate_token(token_name=name,
                                   server_base_url=server_base_url,
                                   username=username,
                                   password=password)
    if profile:
        click.secho('success', fg='bright_green', bold=True)
    else:
        click.secho(data, fg='bright_green', bold=True)


@log_to_history
def show(**kwargs) -> None:
    """Show the local credentials profiles

    Args:
        kwargs: Various CLI options
    """
    data = Auth().show_local_credentials()
    cu.standard_out(data, **kwargs)


@log_to_history
def verify(profile: str) -> None:
    """Check if credentials can authenticate

    Args:
        profile: The profile/account to use
    """
    auth = Auth(Rest())
    auth.get_credentials(profile)
    auth.create_auth()
    click.secho('success', fg='bright_green', bold=True)


@log_to_history
def user(profile: str, token: str, **kwargs) -> None:
    """Show current user information

    Args:
        profile: The profile/account to use
        token:   API token for Jenkins server
    """
    data = cu.config_yo_jenkins(profile, token).auth.user()
    cu.standard_out(data, **kwargs)
