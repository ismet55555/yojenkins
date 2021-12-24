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
@click.option('--token', type=str, required=False, is_flag=False, help='Authentication token used for setup profile')
def configure(debug, token):
    """Configure authentication"""
    set_debug_log_level(debug)
    cli_auth.configure(token)


@auth.command(short_help='\tGenerate authentication API token')
@cli_decorators.debug
@cli_decorators.profile
def token(debug, profile):
    """Generate authentication API token"""
    set_debug_log_level(debug)
    cli_auth.token(profile)


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
