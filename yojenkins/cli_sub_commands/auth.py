"""Auth click sub-command"""
# pylint: skip-file

import click
from click_help_colors import HelpColorsCommand

from yojenkins.__main__ import auth
from yojenkins.cli import cli_auth, cli_decorators
from yojenkins.cli.cli_utility import set_debug_log_level


@auth.command(short_help='\tConfigure authentication',
              cls=HelpColorsCommand,
              help_options_custom_colors={'--token': 'black'})
@cli_decorators.debug
@click.option('--auth-file',
              type=click.Path(file_okay=True, dir_okay=False),
              required=False,
              is_flag=False,
              help='JSON file containing one or more authentication info')
def configure(debug, auth_file):
    """Configure authentication

    This command will setup authentication profile(s). Note that this
    commnad can be used manually via terminal prompts, or via a JSON
    file containing one or more authentication info.

    Example --auth-file file, with single profile setup

    \b
    {
        "<PROFILE NAME>": {
            "active": <true|false>,
            "api_token": "<API TOKEN>",
            "jenkins_server_url": "<SERVER BASE URL>",
            "username": "<USERNAME ID>"
        }
    }
    """
    set_debug_log_level(debug)
    cli_auth.configure(auth_file)


@auth.command(short_help='\tGenerate authentication API token')
@cli_decorators.debug
@cli_decorators.profile
@click.option('--token-name', type=str, required=False, help='Name of the generated API token')
@click.option('--server-base-url', type=str, required=False, help='Server base URL address')
@click.option('--username', type=str, required=False, help='Account username')
@click.option('--password', type=str, required=False, help='Account password')
def token(debug, profile, token_name, server_base_url, username, password):
    """Generate authentication API token

    NOTE: To generate an API token and automatically add it to the
    an existing authentication profile, use the --profile option.
    """
    set_debug_log_level(debug)
    cli_auth.token(profile, token_name, server_base_url, username, password)


@auth.command(short_help='\tShow the local credentials profiles')
@cli_decorators.debug
@cli_decorators.format_output
def show(debug, pretty, yaml, xml, toml):
    """Show the local credentials profiles"""
    set_debug_log_level(debug)
    cli_auth.show(pretty, yaml, xml, toml)


@auth.command(short_help='\tCheck if credentials can authenticate')
@cli_decorators.debug
@cli_decorators.profile
def verify(debug, profile):
    """Check if credentials can authenticate"""
    set_debug_log_level(debug)
    cli_auth.verify(profile)


@auth.command(short_help='\tWipe all credentials for this device')
@cli_decorators.debug
def wipe(debug):
    """Wipe all credentials for this device"""
    set_debug_log_level(debug)
    click.secho('TODO :-/', fg='yellow')


@auth.command(short_help='\tShow current user information')
@cli_decorators.debug
@cli_decorators.format_output
@cli_decorators.profile
def user(debug, pretty, yaml, xml, toml, profile):
    """Show current user information"""
    set_debug_log_level(debug)
    cli_auth.user(pretty, yaml, xml, toml, profile)
