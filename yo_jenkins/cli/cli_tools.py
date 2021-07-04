#!/usr/bin/env python3

import logging
import os
import sys
from pathlib import Path

import click
from yo_jenkins.cli.cli_utility import (COMMAND_HISTORY_FORMAT, CONFIG_DIR_NAME, HISTORY_FILE_NAME, log_to_history)
from yo_jenkins.Tools import Package
from yo_jenkins.Utility.utility import (browser_open, load_contents_from_local_file)

# Getting the logger reference
logger = logging.getLogger()

BUG_REPORT_URL = "https://github.com/ismet55555/yo-jenkins/issues/new?assignees=&labels=&template=bug_report.md&title="
FEATURE_REQUEST_URL = "https://github.com/ismet55555/yo-jenkins/issues/new?assignees=&labels=&template=feature_request.md&title="


@log_to_history
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


@log_to_history
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


@log_to_history
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


@log_to_history
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


def history(profile: str, clear: bool) -> None:
    """Displaying the command history and clearing the history file if requested.

    # TODO: Ability to clear only for a specific profile.

    Args:
        profile (str): The name of the profile to to filter history with
        clear (bool):  Clearing the history file

    Returns:
        None
    """
    # Load contents form history file
    history_file_path = os.path.join(os.path.join(Path.home(), CONFIG_DIR_NAME), HISTORY_FILE_NAME)
    contents = load_contents_from_local_file('json', history_file_path)
    if not contents:
        click.echo(click.style('No history found', fg='bright_red', bold=True))
        sys.exit(1)

    # Clearing the history file if requested
    if clear:
        logger.debug(f'Removing history file: {history_file_path} ...')
        try:
            os.remove(history_file_path)
        except OSError:
            logger.debug('Failed to clear history file')
            click.echo(click.style('failed', fg='bright_red', bold=True))
        else:
            logger.debug('Successfully cleared history file')
            click.echo(click.style('successfully cleared', fg='bright_green', bold=True))
            sys.exit(0)

    # Displaying the command history
    logger.debug(f'Displaying command history for profile "{profile}" ...')

    def output_history_to_console(command_list: list, profile_name: str) -> None:
        """Helper function to format and output to console"""
        for command_info in command_list:
            profile_str = f'{click.style("[" + profile_name + "]", fg="yellow", bold=True)}'
            datetime_str = f'{click.style("[" + command_info["datetime"] + "]", fg="green", bold=False)}'
            tool_version = f'{click.style("[" + "v" + command_info["tool_version"] + "]", fg="green", bold=False)}'

            command_info = f'{profile_str} {datetime_str} {tool_version} - {command_info["tool_path"]} {command_info["arguments"]}'
            click.echo(command_info)

    if profile:
        if profile in contents:
            output_history_to_console(contents[profile], profile)
        else:
            click.echo(click.style('No history found for profile: ' + profile, fg='bright_red', bold=True))
    else:
        for profile_name in contents:
            output_history_to_console(contents[profile_name], profile_name)
