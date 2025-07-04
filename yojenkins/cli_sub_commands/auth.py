"""Auth click sub-command"""
# pylint: skip-file

import click
from click_help_colors import HelpColorsCommand

from yojenkins.__main__ import auth
from yojenkins.cli import cli_auth, cli_decorators
from yojenkins.cli.cli_utility import set_debug_log_level
from yojenkins.utility.utility import translate_kwargs


@auth.command(short_help='\tConfigure yojenkins authentication profile(s)',
              cls=HelpColorsCommand,
              help_options_custom_colors={'--token': 'black'})
@cli_decorators.debug
@click.option('--auth-file',
              type=click.Path(file_okay=True, dir_okay=False),
              required=False,
              is_flag=False,
              help='JSON file containing one or more authentication info')
def configure(debug, auth_file):
    """Configure yojenkins authentication profile(s)

    This commnad can be used manually via terminal prompts, or via a JSON
    file containing one or more authentication info using --auth-file.
    Sample format of a "--auth-file" file, with single profile setup:

    \b
    {
        "<PROFILE NAME>": {
            "active": <true|false>,
            "api_token": "<API TOKEN>",
            "jenkins_server_url": "<SERVER BASE URL>",
            "username": "<USERNAME ID>"
        }
    }

    EXAMPLES:

    \b
    - yojenkins auth verify
    - yojenkins auth verify --auth-file my_auths.json
    """
    set_debug_log_level(debug)
    cli_auth.configure(auth_file)


@auth.command(short_help='\tGenerate and/or add server API token')
@cli_decorators.debug
# @cli_decorators.profile
@click.option('--profile',
              type=str,
              required=False,
              is_flag=False,
              help='yojenkins profile name or profile as JSON text')
@click.option('--token', type=str, required=False, help='API token to add to specified --profile')
@click.option('--name', type=str, required=False, help='Name of the generated API token')
@click.option('--server-base-url', type=str, required=False, help='Server base URL address')
@click.option('--username', type=str, required=False, help='Account/User username')
@click.option('--password', type=str, required=False, help='Account/User password')
def token(debug, **kwargs):
    """Generate and/or add a server authentication API token

    EXAMPLES:

    \b
    - yojenkins auth token --profile default
    - yojenkins auth token --profile my-profile --token 115cfc27acFAKE3c3773eaeb087d2aFAKE
    - yojenkins auth token --server-base-url "http://yo.com" --username "yo" --password "cool"
    - yojenkins auth token --profile myProfile5 --name "My Shiny Token"
    """
    set_debug_log_level(debug)
    cli_auth.token(**translate_kwargs(kwargs))


@auth.command(short_help='\tShow the local credentials profiles')
@cli_decorators.debug
@cli_decorators.format_output
def show(debug, **kwargs):
    """Show the local credentials profiles"""
    set_debug_log_level(debug)
    cli_auth.show(**translate_kwargs(kwargs))


@auth.command(short_help='\tCheck if current credentials can authenticate')
@cli_decorators.debug
@cli_decorators.profile
def verify(debug, **kwargs):
    """Check if current credentials can authenticate with server"""
    set_debug_log_level(debug)
    del kwargs['token']
    cli_auth.verify(**translate_kwargs(kwargs))


@auth.command(short_help='\tShow current user information')
@cli_decorators.debug
@cli_decorators.format_output
@cli_decorators.profile
def user(debug, **kwargs):
    """Show current user information"""
    set_debug_log_level(debug)
    cli_auth.user(**translate_kwargs(kwargs))


# @auth.command(short_help='\tWipe all credentials for this device')
# @cli_decorators.debug
# def wipe(debug):
#     """Wipe all credentials for this device"""
#     set_debug_log_level(debug)
#     click.secho('TODO :-/', fg='yellow')
