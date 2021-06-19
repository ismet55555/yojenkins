#!/usr/bin/env python3

import json
import logging
import platform
import sys
from pprint import pprint
from typing import Type

import click
import toml
import yaml
from json2xml import json2xml
from json2xml.utils import readfromstring
from urllib3.util import parse_url
from yo_jenkins.YoJenkins import REST, Auth, YoJenkins
from yo_jenkins.Utility.utility import iter_data_empty_item_stripper
from yo_jenkins import __version__

# Getting the logger reference
logger = logging.getLogger()


def set_debug_log_level(debug_flag:bool) -> None:
    """Setting the log DEBUG level

    Args:
        debug_flag : Boolean flag, True to set to DEBUG, else INFO

    Returns:
        None
    """
    if debug_flag:
        logging_level = logging.DEBUG
        click.echo(click.style(f'\n[ LOGGING LEVEL ] : DEBUG\n', fg='bright_yellow', bold=True))
        line = '[  TIME  ] [ MS ] [FILENAME              :  LN] MESSAGE'
        click.echo(click.style(line, fg='bright_yellow', bold=True))
        line = '---------------------------------------------------------------------------'
        click.echo(click.style(line, fg='bright_yellow', bold=True))
    else:
        logging_level = logging.INFO
    logger.setLevel(logging_level)
    for handler in logger.handlers:
        handler.setLevel(logging_level)

    # Program version
    logger.debug(f'Tool version: {__version__}')

    # Show system information
    platform_information()


def platform_information() -> None:
    """TODO Docstring

    Args:
        TODO

    Returns:
        TODO
    """
    python_rev = f'(REV:{platform.python_revision()})' if platform.python_revision() else ''

    # System information
    logger.debug(f'System information:')
    logger.debug(f'    - System:    {platform.system()}')
    logger.debug(f'    - Release:   {platform.uname().release}')
    logger.debug(f'    - Version:   {platform.version()}')
    logger.debug(f'    - Machine:   {platform.uname().machine}')
    logger.debug(f'    - Processor: {platform.uname().processor}')
    logger.debug(f'    - Python:    {platform.python_version()} {python_rev}')



def config_YoJenkins(profile:str) -> Type[YoJenkins]:
    """TODO Docstring

    Args:
        TODO

    Returns:
        TODO
    """
    Auth_obj = Auth(REST())

    # TODO: Rename configurations to credentials

    # Get the credential profile
    if not Auth_obj.get_configurations(profile):
        click.echo(click.style(f'Failed to find any credentials', fg='bright_red', bold=True))
        sys.exit(1)

    # Create authentication
    if not Auth_obj.create_auth():
        click.echo(click.style(f'Failed authentication', fg='bright_red', bold=True))
        sys.exit(1)

    return YoJenkins(Auth_obj)


def standard_out(data:dict, opt_pretty:bool=False, opt_yaml:bool=False, opt_xml:bool=False, opt_toml:bool=False) -> None:
    """TODO Docstring

    Args:
        TODO

    Returns:
        TODO
    """
    # Strip away any empty items in the iterable data
    logger.debug(f'Removing all empty items in iterable data ...')
    data = iter_data_empty_item_stripper(data)

    if opt_pretty:
        logger.debug('"PRETTY" (human readable) output was enabled')

    if opt_xml:
        logger.debug('Outputting XML format ...')
        if isinstance(data, dict):
            data = readfromstring(json.dumps(data))
            data_xml = json2xml.Json2xml(data, pretty=opt_pretty).to_xml()
            print(data_xml) if opt_pretty else print(data_xml.decode())
        else:
            # When configs are fetched in XML format
            print(data)
        return

    if opt_yaml:
        # YAML format
        logger.debug('Outputting YAML format ...')
        print(yaml.safe_dump(data, default_flow_style=False, indent=2))
    elif opt_toml:
        # TOML format
        data = {'item': data} if isinstance(data, list) else data
        logger.debug('Outputting TOML format ...')
        print(toml.dumps(data))
    else:
        # JSON format
        logger.debug('Outputting JSON format ...')
        if opt_pretty:
            print(json.dumps(data, indent=4, sort_keys=True))
        else:
            print(json.dumps(data))




def is_full_url(url:str) -> bool:
    """TODO Docstring

    Args:
        TODO

    Returns:
        TODO
    """
    parsed_url = parse_url(url)
    if all([parsed_url.scheme, parsed_url.netloc, parsed_url.path]):
        is_valid_url = True
    else:
        is_valid_url = False
    logger.debug(f'Is valid URL format: {is_valid_url} - {url}')
    logger.debug(f'    - scheme:  {parsed_url.scheme} - {"OK" if parsed_url.scheme else "MISSING"}')
    logger.debug(f'    - netloc:  {parsed_url.netloc} - {"OK" if parsed_url.netloc else "MISSING"}')
    logger.debug(f'    - path:    {parsed_url.path} - {"OK" if parsed_url.path else "MISSING"}')

    return is_valid_url


def server_target_check(target:str) -> bool:
    pass
