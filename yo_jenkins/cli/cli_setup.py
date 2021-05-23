#!/usr/bin/env python3

import logging
import sys
from Setup import JenkinsServerSetup
import click

from . import cli_utility as cu

# Getting the logger reference
logger = logging.getLogger()


def server() -> None:
    """TODO Docstring

    Details: TODO

    Args:
        TODO

    Returns:
        TODO
    """

    JSS = JenkinsServerSetup()
    JSS.test()
    

    data = True
    if not data:
        click.echo(click.style(f'false', fg='bright_red', bold=True))
        sys.exit(1)
    click

    click.echo(click.style('true', fg='bright_green', bold=True))