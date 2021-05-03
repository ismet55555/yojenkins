#!/usr/bin/env python3

import json
import logging
import sys
from pprint import pprint
from urllib.parse import urlparse

import click
import yaml
from json2xml import json2xml
from json2xml.utils import readfromstring
from typing import Type

from YoJenkins import YoJenkins


# Getting the logger reference
logger = logging.getLogger()


def config_auth_server(profile:str) -> Type[YoJenkins]:
    J = YoJenkins()

    # TODO: Rename configurations to credentials

    # Get the credential profile
    if not J.auth_get_configurations(profile):
        click.echo(click.style(f'Failed to find any credentials', fg='bright_red', bold=True))
        sys.exit(1)

    # Create authentication
    if not J.auth_create_auth():
        # click.echo(click.style(f'Failed to create authenticate', fg='bright_red', bold=True))
        sys.exit(1)

    return J


def standard_out(data:dict, opt_pretty:bool=False, opt_yaml:bool=False, opt_xml:bool=False) -> None:
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


def uri_validator(uri:str) -> bool:
    try:
        result = urlparse(uri)
        is_valid_uri = all([result.scheme, result.netloc, result.path])
    except:
        is_valid_uri = False

    logger.debug(f'Is passed value a URL: {is_valid_uri} ({uri})')

    return is_valid_uri



