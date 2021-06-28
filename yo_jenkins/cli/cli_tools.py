#!/usr/bin/env python3

import logging
import sys

import click
from yo_jenkins.cli import cli_utility as cu
from yo_jenkins.Tools import Package

# Getting the logger reference
logger = logging.getLogger()


def upgrade(user: bool, proxy: str) -> None:
    """TODO Docstring

    Details: TODO

    Args:
        TODO

    Returns:
        TODO
    """
    if not Package.install(user=user, proxy=proxy):
        click.echo(click.style('failed to upgrade', fg='bright_red', bold=True))
        sys.exit(1)
    click.echo(click.style('successfully upgraded', fg='bright_green', bold=True))


def remove() -> None:
    """TODO Docstring

    Details: TODO

    Args:
        TODO

    Returns:
        TODO
    """
    if click.confirm('Are you sure you want to remove yo-jenkins?'):
        if not Package.uninstall():
            click.echo(click.style('failed to remove', fg='bright_red', bold=True))
            sys.exit(1)
        click.echo(click.style('successfully removed', fg='bright_green', bold=True))
