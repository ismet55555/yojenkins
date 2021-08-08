#!/usr/bin/env python3

import logging
import sys

import click

from yo_jenkins.cli import cli_utility as cu
from yo_jenkins.cli.cli_utility import log_to_history

# Getting the logger reference
logger = logging.getLogger()


@log_to_history
def create_permanent(profile: str, **kwargs) -> None:
    """TODO Docstring

    Details: TODO

    Args:
        TODO

    Returns:
        TODO
    """
    yj = cu.config_yo_jenkins(profile)
    if not yj.Node.create_permanent(**kwargs):
        click.echo(click.style('failed', fg='bright_red', bold=True))
        sys.exit(1)
    click.echo(click.style('success', fg='bright_green', bold=True))
