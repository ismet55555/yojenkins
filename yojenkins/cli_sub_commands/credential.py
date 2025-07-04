"""Credential click sub-command"""
# pylint: skip-file

import click

from yojenkins.__main__ import credential
from yojenkins.cli import cli_credential, cli_decorators
from yojenkins.cli.cli_utility import set_debug_log_level
from yojenkins.utility.utility import translate_kwargs


@credential.command(short_help='\tList credentials')
@cli_decorators.debug
@cli_decorators.format_output
@cli_decorators.list
@cli_decorators.profile
# @click.argument('folder', nargs=1, type=str, default="root", required=False)
@click.option('--folder', type=str, default="root", show_default=True, required=False, help='Credentials folder')
@click.option('--domain', type=str, default="global", show_default=True, required=False, help='Credentials domain')
@click.option('--keys',
              type=str,
              default="all",
              show_default=True,
              required=False,
              help='Credential info keys to return [ie. displayName,id,etc]')
def list(debug, **kwargs):
    """List credentials"""
    set_debug_log_level(debug)
    cli_credential.list(**translate_kwargs(kwargs))


@credential.command(short_help='\tCredential information')
@cli_decorators.debug
@cli_decorators.format_output
@cli_decorators.profile
@click.argument('credential', nargs=1, type=str, required=True)
@click.option('--folder', type=str, default="root", show_default=True, required=False, help='Credential folder')
@click.option('--domain', type=str, default="global", show_default=True, required=False, help='Credential domain')
def info(debug, **kwargs):
    """Credential information"""
    set_debug_log_level(debug)
    cli_credential.info(**translate_kwargs(kwargs))


@credential.command(short_help='\tGet credential configuration')
@cli_decorators.debug
@cli_decorators.format_output
@click.option('-j',
              '--json',
              type=bool,
              default=False,
              required=False,
              is_flag=True,
              help='Output config in JSON format')
@cli_decorators.profile
@click.argument('credential', nargs=1, type=str, required=True)
@click.option('--folder', type=str, default="root", show_default=True, required=False, help='Credential folder')
@click.option('--domain', type=str, default="global", show_default=True, required=False, help='Credential domain')
@click.option('--filepath',
              type=click.Path(file_okay=True, dir_okay=True),
              required=False,
              help='File/Filepath to write configurations to')
def config(debug, **kwargs):
    """Get credential configuration"""
    set_debug_log_level(debug)
    cli_credential.config(**translate_kwargs(kwargs))


@credential.command(short_help='\tCredential type template to create a credential')
@cli_decorators.debug
@cli_decorators.format_output
@click.option('-j',
              '--json',
              type=bool,
              default=False,
              required=False,
              is_flag=True,
              help='Output config in JSON format')
@cli_decorators.profile
@click.argument('type',
                type=click.Choice(['user-pass', 'ssh-key', 'secret-text'], case_sensitive=False),
                default='user-pass',
                required=True)
@click.option('--filepath',
              type=click.Path(file_okay=True, dir_okay=True),
              required=False,
              help='File/Filepath to write template to')
def get_template(debug, **kwargs):
    """Credential type template to create a credential"""
    set_debug_log_level(debug)
    cli_credential.get_template(**translate_kwargs(kwargs))


@credential.command(short_help='\tCreate new credentials')
@cli_decorators.debug
@cli_decorators.profile
# @click.argument('name', nargs=1, type=str, required=True)
@click.argument('config-file', nargs=1, type=click.Path(exists=True), required=True)
@click.option('--folder', type=str, default="root", show_default=True, required=False, help='Credential folder')
@click.option('--domain', type=str, default="global", show_default=True, required=False, help='Credential domain')
def create(debug, **kwargs):
    """Create new credentials"""
    set_debug_log_level(debug)
    cli_credential.create(**translate_kwargs(kwargs))


@credential.command(short_help='\tRemove credentials')
@cli_decorators.debug
@cli_decorators.profile
@click.argument('credential', nargs=1, type=str, required=True)
@click.option('--folder', type=str, default="root", show_default=True, required=False, help='Credential folder')
@click.option('--domain', type=str, default="global", show_default=True, required=False, help='Credential domain')
def delete(debug, **kwargs):
    """Remove credentials"""
    set_debug_log_level(debug)
    cli_credential.delete(**translate_kwargs(kwargs))


@credential.command(short_help='\tReconfigure existing credentials')
@cli_decorators.debug
def update(debug):
    """Reconfigure existing credentials"""
    set_debug_log_level(debug)
    click.secho('TODO :-/', fg='yellow')


@credential.command(short_help='\tMove a credential to another folder/domain')
@cli_decorators.debug
def move(debug):
    """Move a credential to another folder/domain"""
    set_debug_log_level(debug)
    click.secho('TODO :-/', fg='yellow')
