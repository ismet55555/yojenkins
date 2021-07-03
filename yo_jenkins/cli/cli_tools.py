#!/usr/bin/env python3

import logging
import sys

import click
from yo_jenkins.Utility.utility import browser_open
from yo_jenkins.Tools import Package

# Getting the logger reference
logger = logging.getLogger()

BUG_REPORT_URL = "https://github.com/ismet55555/yo-jenkins/issues/new?assignees=&labels=&template=bug_report.md&title="
FEATURE_REQUEST_URL = "https://github.com/ismet55555/yo-jenkins/issues/new?assignees=&labels=&template=feature_request.md&title="


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
        Package.uninstall()


def bug_report() -> None:
    """TODO Docstring

    Details: TODO

    Args:
        TODO

    Returns:
        TODO
    """
    logger.debug(f'Opening bug report webpage in web browser: "{BUG_REPORT_URL}" ...')
    success = browser_open(url=BUG_REPORT_URL)
    if success:
        logger.debug('Successfully opened in web browser')
    else:
        logger.debug('Failed to open in web browser')
    return success


def feature_request() -> None:
    """TODO Docstring

    Details: TODO

    Args:
        TODO

    Returns:
        TODO
    """
    logger.debug(f'Opening feature request webpage in web browser: "{FEATURE_REQUEST_URL}" ...')
    success = browser_open(url=FEATURE_REQUEST_URL)
    if success:
        logger.debug('Successfully opened in web browser')
    else:
        logger.debug('Failed to open in web browser')
    return success
