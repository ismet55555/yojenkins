#!/usr/bin/env python3

import logging
import sys

import click
from YoJenkins import YoJenkins

from . import cli_utility

# Getting the logger reference
logger = logging.getLogger()


def info(opt_pretty:bool, opt_yaml:bool, opt_xml:bool, step_url:str) -> None:
    '''
    TODO: Docstring
        1. Pass build url
        2. Pass job and build number
    '''
    J = YoJenkins()

    # Authenticate with server
    # TODO: Which server in configs are we talking about? Profiles? Pass value?
    auth_success = J.authenticate()
    if not auth_success:
        # TODO: User message here with no debug
        sys.exit(1)

    # Differentiate if name or url
    if not cli_utility.uri_validator(step_url):
        click.echo(click.style(
            f'INPUT ERROR: Step url is not a URL: {step_url}', fg='bright_red', bold=True))
        sys.exit(1)

    # Request the data
    data = J.step_info(step_url=step_url)

    if not data:
        click.echo(click.style(f'No step information', fg='bright_red', bold=True))
        sys.exit(1)
    cli_utility.standard_out(data, opt_pretty, opt_yaml, opt_xml)
