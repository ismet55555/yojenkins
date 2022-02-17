"""Folder click sub-command"""
# pylint: skip-file

import click

from yojenkins.__main__ import folder
from yojenkins.cli import cli_decorators, cli_folder
from yojenkins.cli.cli_utility import set_debug_log_level


@folder.command(short_help='\tFolder information')
@cli_decorators.debug
@cli_decorators.format_output
@cli_decorators.profile
@click.argument('folder', nargs=1, type=str, required=True)
def info(debug, pretty, yaml, xml, toml, profile, folder):
    """Folder information"""
    set_debug_log_level(debug)
    cli_folder.info(pretty, yaml, xml, toml, profile, folder)


@folder.command(short_help='\tSearch folders by REGEX pattern')
@cli_decorators.debug
@cli_decorators.format_output
@cli_decorators.profile
@click.argument('search_pattern', nargs=1, type=str, required=True)
@click.option('-sf', '--search-folder', type=str, default='', required=False, help='Folder within which to search')
@click.option('-d', '--depth', type=int, default=4, required=False, help='Search depth from root directory')
@click.option('-fn',
              '--fullname',
              type=bool,
              default=False,
              required=False,
              is_flag=True,
              help='Search entire folder path name')
@cli_decorators.list
def search(debug, pretty, yaml, xml, toml, profile, search_pattern, search_folder, depth, fullname, list):
    """Search folders by REGEX pattern"""
    set_debug_log_level(debug)
    cli_folder.search(pretty, yaml, xml, toml, profile, search_pattern, search_folder, depth, fullname, list)


@folder.command(short_help='\tList all subfolders in folder')
@cli_decorators.debug
@cli_decorators.format_output
@cli_decorators.profile
@click.argument('folder', nargs=1, type=str, required=True)
@cli_decorators.list
def subfolders(debug, pretty, yaml, xml, toml, profile, folder, list):
    """List all subfolders in folder"""
    set_debug_log_level(debug)
    cli_folder.subfolders(pretty, yaml, xml, toml, profile, folder, list)


@folder.command(short_help='\tList all jobs in folder')
@cli_decorators.debug
@cli_decorators.format_output
@cli_decorators.profile
@click.argument('folder', nargs=1, type=str, required=True)
@cli_decorators.list
def jobs(debug, pretty, yaml, xml, toml, profile, folder, list):
    """List all jobs in folder"""
    set_debug_log_level(debug)
    cli_folder.jobs(pretty, yaml, xml, toml, profile, folder, list)


@folder.command(short_help='\tList all views in folder')
@cli_decorators.debug
@cli_decorators.format_output
@cli_decorators.profile
@click.argument('folder', nargs=1, type=str, required=True)
@cli_decorators.list
def views(debug, pretty, yaml, xml, toml, profile, folder, list):
    """List all views in folder"""
    set_debug_log_level(debug)
    cli_folder.views(pretty, yaml, xml, toml, profile, folder, list)


@folder.command(short_help='\tList all items in folder')
@cli_decorators.debug
@cli_decorators.format_output
@cli_decorators.profile
@click.argument('folder', nargs=1, type=str, required=True)
@cli_decorators.list
def items(debug, pretty, yaml, xml, toml, profile, folder, list):
    """List all items in folder"""
    set_debug_log_level(debug)
    cli_folder.items(pretty, yaml, xml, toml, profile, folder, list)


@folder.command(short_help='\tOpen folder in web browser')
@cli_decorators.debug
@cli_decorators.profile
@click.argument('folder', nargs=1, type=str, required=True)
def browser(debug, profile, folder):
    """Open folder in web browser"""
    set_debug_log_level(debug)
    cli_folder.browser(profile, folder)


@folder.command(short_help='\tGet folder configuration')
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
@click.argument('folder', nargs=1, type=str, required=True)
@click.option('--filepath',
              type=click.Path(file_okay=True, dir_okay=True),
              required=False,
              help='File/Filepath to write configurations to')
def config(debug, pretty, yaml, xml, toml, json, profile, folder, filepath):
    """Get folder configuration"""
    set_debug_log_level(debug)
    cli_folder.config(pretty, yaml, xml, toml, json, profile, folder, filepath)


@folder.command(short_help='\tCreate an item [folder, view, job]')
@cli_decorators.debug
@cli_decorators.profile
@click.argument('name', nargs=1, type=str, required=True)
@click.argument('folder', nargs=1, type=str, required=True)
@click.option('--type',
              type=click.Choice(['folder', 'view', 'job'], case_sensitive=False),
              default='folder',
              show_default=True,
              required=False,
              help='Item type created')
@click.option('--config-file',
              type=click.Path(file_okay=True, dir_okay=False),
              required=False,
              help='Path to local file defining item')
@click.option('--config-is-json',
              type=bool,
              default=False,
              required=False,
              is_flag=True,
              help='The specified file is in JSON format')
def create(debug, profile, name, folder, type, config_file, config_is_json):
    """Create an item [folder, view, job]"""
    set_debug_log_level(debug)
    cli_folder.create(profile, name, folder, type, config_file, config_is_json)


@folder.command(short_help='\tCopy an existing item')
@cli_decorators.debug
@cli_decorators.profile
@click.argument('folder', nargs=1, type=str, required=True)
@click.argument('original', nargs=1, type=str, required=True)
@click.argument('new', nargs=1, type=str, required=True)
def copy(debug, profile, folder, original, new):
    """Copy an existing item"""
    set_debug_log_level(debug)
    cli_folder.copy(profile, folder, original, new)


@folder.command(short_help='\tDelete folder or view')
@cli_decorators.debug
@cli_decorators.profile
@click.argument('folder', nargs=1, type=str, required=True)
def delete(debug, profile, folder):
    """Delete folder or view"""
    set_debug_log_level(debug)
    cli_folder.delete(profile, folder)
