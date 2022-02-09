"""Account click sub-command"""
# pylint: skip-file

import click

from yojenkins.__main__ import account
from yojenkins.cli import cli_account, cli_decorators
from yojenkins.cli.cli_utility import set_debug_log_level


@account.command(short_help='\tList all users')
@cli_decorators.debug
@cli_decorators.format_output
@cli_decorators.list
@cli_decorators.profile
def list(debug, pretty, yaml, xml, toml, list, profile):
    """List all users"""
    set_debug_log_level(debug)
    cli_account.list(pretty, yaml, xml, toml, list, profile)


@account.command(short_help='\tGet user information')
@cli_decorators.debug
@cli_decorators.format_output
@cli_decorators.profile
@click.argument('user-id', nargs=1, type=str, required=True)
def info(debug, pretty, yaml, xml, toml, profile, user_id):
    """Get user information"""
    set_debug_log_level(debug)
    cli_account.info(pretty, yaml, xml, toml, profile, user_id)


@account.command(short_help='\tCreate a user account')
@cli_decorators.debug
@cli_decorators.profile
@click.argument('user-id', nargs=1, type=str, required=True)
@click.argument('password', nargs=1, type=str, required=True)
@click.option('--is-admin',
              type=bool,
              default=False,
              required=False,
              is_flag=True,
              help='User has administrator control')
@click.option('--email', type=str, required=False, help='User email address')
@click.option('--description', type=str, required=False, help='User description')
def create(debug, profile, user_id, password, is_admin, email, description):
    """Create a user account"""
    set_debug_log_level(debug)
    cli_account.create(profile, user_id, password, is_admin, email, description)


@account.command(short_help='\tDelete a user account')
@cli_decorators.debug
@cli_decorators.profile
@click.argument('user-id', nargs=1, type=str, required=True)
def delete(debug, profile, user_id):
    """Delete a user account"""
    set_debug_log_level(debug)
    cli_account.delete(profile, user_id)


@account.command(short_help='\tAdd or remove user permission')
@cli_decorators.debug
@cli_decorators.profile
@click.argument('user_id', nargs=1, type=str, required=True)
@click.option('--action',
              type=click.Choice(['add', 'remove'], case_sensitive=False),
              required=True,
              help='Add or remove permission action')
@click.option('--permission-id', type=str, required=True, help='ID(s) of permission (comma separated)')
def permission(debug, profile, user_id, action, permission_id):
    """
    Add or remove user permission

    \b
    IMPORTANT:
      - Permission IDs must have correct capitalization or naming!
      - If permission is not found, read class docs, or try variation.

    \b
    EXAMPLES:
      - Will not work/match:  hudson.model.View.Create
      - Will work/match:      hudson.model.View.CREATE
    \b
      - Will not work/match:  hudson.security.Permission.GenericCreate
      - Will work/match:      hudson.security.Permission.CREATE
    """
    set_debug_log_level(debug)
    cli_account.permission(profile, user_id, action, permission_id)


@account.command(short_help='\tList all available permissions')
@cli_decorators.debug
@cli_decorators.format_output
@cli_decorators.list
@cli_decorators.profile
def permission_list(debug, pretty, yaml, xml, toml, list, profile):
    """List all available permissions

    \b
    IMPORTANT:
      - Permission IDs may not have correct capitalization!
      - If permission is not found, read class docs, or try variation.

    \b
    EXAMPLE:
      - Not Correct:  hudson.model.View.Create
      - Correct:      hudson.model.View.CREATE
    \b
      - Will not work/match:  hudson.security.Permission.GenericCreate
      - Will work/match:      hudson.security.Permission.CREATE
    """
    set_debug_log_level(debug)
    cli_account.permission_list(pretty, yaml, xml, toml, list, profile)


@account.command(short_help='\tReset a user password')
@cli_decorators.debug
@cli_decorators.profile
def password_reset(debug, profile):
    """Reset a user password"""
    set_debug_log_level(debug)
    click.secho('TODO :-/', fg='yellow')
