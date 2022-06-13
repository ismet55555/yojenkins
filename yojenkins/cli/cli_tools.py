"""Tools Menu CLI Entrypoints"""

import json
import logging
import os
import sys
from pathlib import Path
from typing import NoReturn, Union

import click

from yojenkins.cli import cli_utility as cu
from yojenkins.cli.cli_utility import log_to_history
from yojenkins.tools import Package, SharedLibrary
from yojenkins.utility.utility import (
    browser_open,
    fail_out,
    html_clean,
    load_contents_from_local_file,
    print2,
)

# Getting the logger reference
logger = logging.getLogger()

# TODO: Move all these configs to a central config file
BUG_REPORT_URL = "https://github.com/ismet55555/yojenkins/issues/new?assignees=ismet55555&labels=bug%2Ctriage&template=bug_report.yml&title=%5BBug%5D%3A+"
FEATURE_REQUEST_URL = "https://github.com/ismet55555/yojenkins/issues/new?assignees=ismet55555&labels=feature-request&template=feature_request.yml&title=%5BFeature-Request%5D%3A+"
DOCS_URL = "https://www.yojenkins.com/"


@log_to_history
def documentation() -> None:
    """TODO Docstring

    Details: TODO

    Args:
        TODO
    """
    logger.debug(f'Opening documentation in web browser: "{DOCS_URL}" ...')
    success = browser_open(url=DOCS_URL)
    if success:
        logger.debug('Successfully opened in web browser')
    else:
        logger.debug('Failed to open in web browser')


@log_to_history
def upgrade(user: bool, proxy: str) -> None:
    """TODO Docstring

    Details: TODO

    Args:
        TODO
    """
    if not Package.install(user=user, proxy=proxy):
        click.secho('failed to upgrade', fg='bright_red', bold=True)
        sys.exit(1)
    click.secho('successfully upgraded', fg='bright_green', bold=True)


@log_to_history
def remove() -> None:
    """TODO Docstring

    Details: TODO

    Args:
        TODO
    """
    if click.confirm('Are you sure you want to remove yojenkins?'):
        Package.uninstall()


@log_to_history
def bug_report() -> None:
    """TODO Docstring

    Details: TODO

    Args:
        TODO
    """
    logger.debug(f'Opening bug report webpage in web browser: "{BUG_REPORT_URL}" ...')
    success = browser_open(url=BUG_REPORT_URL)
    if success:
        logger.debug('Successfully opened in web browser')
    else:
        logger.debug('Failed to open in web browser')


@log_to_history
def feature_request() -> None:
    """TODO Docstring

    Details: TODO

    Args:
        TODO
    """
    logger.debug(f'Opening feature request webpage in web browser: "{FEATURE_REQUEST_URL}" ...')
    success = browser_open(url=FEATURE_REQUEST_URL)
    if success:
        logger.debug('Successfully opened in web browser')
    else:
        logger.debug('Failed to open in web browser')


def history(profile: str, clear: bool) -> None:
    """Displaying the command history and clearing the history file if requested.

    ### TODO: Ability to clear only for a specific profile.

    Args:
        profile: The name of the profile to to filter history with
        clear:   Clearing the history file
    """
    # Load contents from history file
    history_file_path = os.path.join(os.path.join(Path.home(), cu.CONFIG_DIR_NAME), cu.HISTORY_FILE_NAME)
    contents = load_contents_from_local_file('json', history_file_path)
    if not contents:
        click.secho('No history found', fg='bright_red', bold=True)
        sys.exit(1)

    # Clearing the history file if requested
    if clear:
        logger.debug(f'Removing history file: {history_file_path} ...')
        try:
            os.remove(history_file_path)
        except (OSError, IOError, PermissionError) as error:
            fail_out(f'Failed to clear history file. Exception: {error}')
        logger.debug('Successfully cleared history file')
        click.secho('success', fg='bright_green', bold=True)
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
            fail_out(f'No history found for profile: {profile}')
    else:
        for profile_name in contents:
            output_history_to_console(contents[profile_name], profile_name)


@log_to_history
def rest_request(profile: str, token: str, request_text: str, request_type: str, raw: bool, clean_html: bool) -> None:
    """Send a generic REST request to Jenkins Server using the loaded credentials

    Args:
        profile: The name of the credentials profile
        token:   API token for Jenkins server
        request_text: The text of the request to send
        request_type: The type of request to send
        raw: Whether to return the raw response or formatted JSON
        clean_html: Whether to clean the HTML tags from the response
    """
    yj_obj = cu.config_yo_jenkins(profile, token)
    request_text = request_text.strip('/')
    content, header, success = yj_obj.rest.request(
        target=request_text,
        request_type=request_type,
        json_content=(not raw),
    )

    if not success:
        fail_out('Failed to make request')

    if request_type == 'HEAD':
        print2(header)
        sys.exit(0)

    if content:
        if clean_html:
            try:
                print2(html_clean(content))
            except Exception:
                print2(content)
        else:
            try:
                print2(json.dumps(content, indent=4))
            except Exception:
                print2(content)
    else:
        fail_out('Content returned, however possible HTML content. Try --raw.')


@log_to_history
def run_script(profile: str, token: str, text: str, file: str, output: str) -> Union[NoReturn, None]:
    """TODO

    Details: TODO:

    Args:
        TODO
    """
    yj_obj = cu.config_yo_jenkins(profile, token)

    # Prepare the commands/script
    script = ''
    if text:
        text = text.strip().replace('  ', ' ')
        script = text
    elif file:
        logger.debug(f'Loading specified script from file: {file} ...')
        try:
            with open(os.path.join(file), 'r') as open_file:
                script = open_file.read()
            script_size = os.path.getsize(file)
            logger.debug(f'Successfully loaded script file ({script_size} Bytes)')
        except FileNotFoundError as error:
            fail_out(f'Failed to find specified script file ({file})')
        except (OSError, IOError, PermissionError) as error:
            fail_out(f'Failed to read specified script file ({file}). Exception: {error}')

    # Send the request to the server
    content, _, success = yj_obj.rest.request(target='scriptText',
                                              request_type='post',
                                              data={'script': script},
                                              json_content=False)

    if not success:
        fail_out('Failed to make script run request')

    # Save script result to file
    if output:
        logger.debug(f'Saving script result into file: {output} ...')
        try:
            with open(output, 'w+') as open_file:
                open_file.write(content)
            logger.debug('Successfully wrote script result to file')
        except (OSError, IOError, PermissionError) as error:
            fail_out(f"Failed to write script output to file. Exception: {error}")

    click.echo(content)


@log_to_history
def shared_lib_setup(profile: str, token: str, **kwargs) -> Union[NoReturn, None]:
    """Sets up a shared library on the Jenkins Server

    Args:
        profile: The name of the credentials profile
        token:   API Token for Jenkins server

    Returns:
        True if the setup was successful, else False
    """
    yj_obj = cu.config_yo_jenkins(profile, token)
    data = SharedLibrary().setup(yj_obj.rest, **kwargs)
    if not data:
        fail_out('failed')
    click.secho('success', fg='bright_green', bold=True)
