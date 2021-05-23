#!/usr/bin/env python3

import json
import logging
import sys
from pprint import pprint
from typing import Type
from urllib3.util import parse_url

import click
import yaml
from json2xml import json2xml
from json2xml.utils import readfromstring
from YoJenkins import REST, Auth, YoJenkins

# Getting the logger reference
logger = logging.getLogger()


def set_debug_log_level(debug_flag:bool):
    """Setting the log DEBUG level

    Args:
        debug_flag : Boolean flag, True to set to DEBUG, else INFO

    Returns:
        None
    """
    if debug_flag:
        logging_level = logging.DEBUG
        click.echo(click.style(f'\n[ LOGGING LEVEL ] : DEBUG\n', fg='bright_yellow', bold=True))
        line = '[  TIME  ] [ MS ] [FILENAME               :  LN] MESSAGE'
        click.echo(click.style(line, fg='bright_yellow', bold=True))
        line = '---------------------------------------------------------------------------'
        click.echo(click.style(line, fg='bright_yellow', bold=True))
    else:
        logging_level = logging.INFO
    logger.setLevel(logging_level)
    for handler in logger.handlers:
        handler.setLevel(logging_level)


def config_YoJenkins(profile:str) -> Type[YoJenkins]:
    """TODO Docstring

    Args:
        TODO

    Returns:
        TODO
    """
    R = REST()
    A = Auth(R)

    # TODO: Rename configurations to credentials

    # Get the credential profile
    if not A.get_configurations(profile):
        click.echo(click.style(f'Failed to find any credentials', fg='bright_red', bold=True))
        sys.exit(1)

    # Create authentication
    if not A.create_auth():
        click.echo(click.style(f'Failed authentication', fg='bright_red', bold=True))
        sys.exit(1)

    return YoJenkins(A, R)


def standard_out(data:dict, opt_pretty:bool=False, opt_yaml:bool=False, opt_xml:bool=False) -> None:
    """TODO Docstring

    Args:
        TODO

    Returns:
        TODO
    """
    if opt_pretty:
        logger.debug('"PRETTY" (human readable) output was enabled')

    if opt_yaml:
        # YAML format
        logger.debug('Outputting YAML format ...')
        print(yaml.safe_dump(data, default_flow_style=False, indent=2))
    elif opt_xml:
        # XML format
        logger.debug('Outputting XML format ...')
        data = readfromstring(json.dumps(data))
        print(json2xml.Json2xml(data, pretty=opt_pretty).to_xml())
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
