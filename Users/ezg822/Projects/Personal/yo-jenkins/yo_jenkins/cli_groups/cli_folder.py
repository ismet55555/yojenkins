#!/usr/bin/env python3

import logging
import sys

import click
from YoJenkins import YoJenkins

from . import cli_utility

# Getting the logger reference
logger = logging.getLogger()


def info(opt_pretty:bool, opt_yaml:bool, opt_xml:bool, profile:str, folder:str) -> None:
    '''
    TODO: Docstring
    '''
    J = cli_utility.config_auth_server(profile)

    # Differentiate if name or url
    valid_url_format = cli_utility.uri_validator(folder)

    # Request the data
    if valid_url_format:
        data = J.folder_info(folder_url=folder)
    else:
        data = J.folder_info(folder_name=folder)

    if not data:
        click.echo(click.style(f'No folder information', fg='bright_red', bold=True))
        sys.exit(1)
    cli_utility.standard_out(data, opt_pretty, opt_yaml, opt_xml)


def search(opt_pretty:bool, opt_yaml:bool, opt_xml:bool, profile:str, search_pattern:str, start_folder:str, depth:int, opt_list:bool) -> None:
    '''
    TODO: Docstring
    '''
    J = cli_utility.config_auth_server(profile)
    
    # Differentiate if name or url
    valid_url_format = cli_utility.uri_validator(start_folder)

    # Request the data
    if valid_url_format:
        data, data_list = J.folder_search(search_pattern=search_pattern, folder_url=start_folder, folder_depth=depth)
    else:
        data, data_list = J.folder_search(search_pattern=search_pattern, folder_name=start_folder, folder_depth=depth)

    if not data:
        click.echo(click.style(f'"{search_pattern}" not found', fg='bright_red', bold=True))
        sys.exit(1)
    data = data_list if opt_list else data
    cli_utility.standard_out(data, opt_pretty, opt_yaml, opt_xml)


def subfolders(opt_pretty:bool, opt_yaml:bool, opt_xml:bool, profile:str, folder:str, opt_list:bool) -> None:
    '''
    TODO: Docstring
    '''
    J = cli_utility.config_auth_server(profile)
    
    # Differentiate if name or url
    valid_url_format = cli_utility.uri_validator(folder)

    # Request the data
    if valid_url_format:
        data, data_list = J.folder_subfolder_list(folder_url=folder)
    else:
        data, data_list = J.folder_subfolder_list(folder_name=folder)

    if not data:
        click.echo(click.style(f'Not found or no subfolders', fg='bright_red', bold=True))
        sys.exit(1)
    data = data_list if opt_list else data
    cli_utility.standard_out(data, opt_pretty, opt_yaml, opt_xml)


def jobs(opt_pretty:bool, opt_yaml:bool, opt_xml:bool, profile:str, folder:str, opt_list:bool) -> None:
    '''
    TODO: Docstring
    '''
    J = cli_utility.config_auth_server(profile)
    
    # Differentiate if name or url
    valid_url_format = cli_utility.uri_validator(folder)

    # Request the data
    if valid_url_format:
        data, data_list = J.folder_jobs_list(folder_url=folder)
    else:
        data, data_list = J.folder_jobs_list(folder_name=folder)

    if not data:
        click.echo(click.style(f'"{folder}" not found', fg='bright_red', bold=True))
        sys.exit(1)
    data = data_list if opt_list else data
    cli_utility.standard_out(data, opt_pretty, opt_yaml, opt_xml)


def views(opt_pretty:bool, opt_yaml:bool, opt_xml:bool, profile:str, folder:str, opt_list:int) -> None:
    '''
    TODO: Docstring
    '''
    J = cli_utility.config_auth_server(profile)
    
    # Differentiate if name or url
    valid_url_format = cli_utility.uri_validator(folder)

    # Request the data
    if valid_url_format:
        data, data_list = J.folder_view_list(folder_url=folder)
    else:
        data, data_list = J.folder_view_list(folder_name=folder)

    if not data:
        click.echo(click.style(f'"{folder}" not found', fg='bright_red', bold=True))
        sys.exit(1)
    data = data_list if opt_list else data
    cli_utility.standard_out(data, opt_pretty, opt_yaml, opt_xml)


def items(opt_pretty:bool, opt_yaml:bool, opt_xml:bool, profile:str, folder:str, opt_list:int) -> None:
    '''
    TODO: Docstring
    '''
    J = cli_utility.config_auth_server(profile)
    
    # Differentiate if name or url
    valid_url_format = cli_utility.uri_validator(folder)

    # Request the data
    if valid_url_format:
        data, data_list = J.folder_item_list(folder_url=folder)
    else:
        data, data_list = J.folder_item_list(folder_name=folder)

    if not data:
        click.echo(click.style(f'Folder not found or no folder items found', fg='bright_red', bold=True))
        sys.exit(1)
    data = data_list if opt_list else data
    cli_utility.standard_out(data, opt_pretty, opt_yaml, opt_xml)