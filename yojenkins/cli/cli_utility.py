"""Utility/Tools Menu CLI Entrypoints"""

import json
import logging
import os
import platform
import sys
from datetime import datetime
from inspect import getfullargspec
from pathlib import Path
from shlex import quote
from typing import Callable, Dict, List, Union

import click
import toml
import yaml
from json2xml import json2xml
from json2xml.utils import readfromstring
from urllib3.util import parse_url

from yojenkins import __version__
from yojenkins.yo_jenkins.auth import Auth
from yojenkins.yo_jenkins.rest import Rest
from yojenkins.yo_jenkins.yojenkins import YoJenkins

from yojenkins.utility.utility import iter_data_empty_item_stripper, load_contents_from_local_file, am_i_inside_docker, am_i_bundled, print2, create_new_history_file  # isort:skip

# Getting the logger reference
logger = logging.getLogger()

CONFIG_DIR_NAME = '.yojenkins'
HISTORY_FILE_NAME = 'history'
COMMAND_HISTORY_FORMAT = 'json'
DEFAULT_PROFILE_NAME = 'default'
MAX_PROFILE_HISTORY_LENGTH = 1000

CLI_CMD_PATH = sys.argv[0]
CLI_CMD_ARGS = ' '.join([quote(arg) for arg in sys.argv[1:]])


def set_debug_log_level(debug_flag: bool) -> None:
    """Setting the log DEBUG level

    Args:
        debug_flag : Boolean flag, True to set to DEBUG, else INFO

    Returns:
        None
    """
    if debug_flag:
        logging_level = logging.DEBUG
        click.secho('\n[ LOGGING LEVEL ] : DEBUG\n', fg='bright_yellow', bold=True)
        line = '[  TIME  ] [ MS ] [FILENAME              :  LN] MESSAGE'
        click.secho(line, fg='bright_yellow', bold=True)
        line = '---------------------------------------------------------------------------'
        click.secho(line, fg='bright_yellow', bold=True)
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
    """Display (Console out) current system and program information
    """
    python_rev = f'(REV:{platform.python_revision()})' if platform.python_revision() else ''

    # System information
    logger.debug('System information:')
    logger.debug(f'    - System:    {platform.system()}')
    logger.debug(f'    - Release:   {platform.uname().release}')
    logger.debug(f'    - Version:   {platform.version()}')
    logger.debug(f'    - Machine:   {platform.uname().machine}')
    logger.debug(f'    - Processor: {platform.uname().processor}')
    logger.debug(f'    - Python:    {platform.python_version()} {python_rev}')
    logger.debug(f'    - In Docker: {am_i_inside_docker()}')
    logger.debug(f'    - Bundled:   {am_i_bundled()}')


def config_yo_jenkins(profile: str, token: str) -> YoJenkins:
    """Initialize/Prepare YoJenkins object using the appropriate
    authentication information


    Args:
        profile: Name of the yojenkins authentication profile
        token:   API token to override profile value

    Returns:
        Initialized YoJenkins object
    """
    auth = Auth(Rest())

    # Get the credential profile
    if not auth.get_credentials(profile):
        click.secho('Failed to find any credentials', fg='bright_red', bold=True)
        sys.exit(1)

    # Create authentication
    if not auth.create_auth(token=token):
        click.secho('Failed authentication', fg='bright_red', bold=True)
        sys.exit(1)

    return YoJenkins(auth)


def standard_out(data: Union[Dict, List],
                 opt_pretty: bool = False,
                 opt_yaml: bool = False,
                 opt_xml: bool = False,
                 opt_toml: bool = False) -> None:
    """Outputting the resulting data to the console.
    This funciton handles a variety of output formats.

    Args:
        TODO
    """
    # Strip away any empty items in the iterable data
    logger.debug('Removing all empty items in iterable data ...')
    data = iter_data_empty_item_stripper(data)

    if opt_pretty:
        logger.debug('"PRETTY" (human readable) output was enabled')

    if opt_xml:
        logger.debug('Outputting XML format ...')
        if isinstance(data, dict) or isinstance(data, list):
            data = readfromstring(json.dumps(data))
            data_xml = json2xml.Json2xml(data, pretty=opt_pretty, wrapper=None, attr_type=False).to_xml()
            if opt_pretty:
                print2(data_xml)
            else:
                print2(data_xml.decode())
        else:
            # When configs are fetched in XML format
            print2(data)
        return

    if opt_yaml:
        # YAML format
        logger.debug('Outputting YAML format ...')
        print2(yaml.safe_dump(data, default_flow_style=False, indent=2))
    elif opt_toml:
        # TOML format
        data = {'item': data} if isinstance(data, list) else data
        logger.debug('Outputting TOML format ...')
        print2(toml.dumps(data))
    else:
        # JSON format
        logger.debug('Outputting JSON format ...')
        if opt_pretty:
            print2(json.dumps(data, indent=4, sort_keys=True))
        else:
            print2(json.dumps(data))


def is_full_url(url: str) -> bool:
    """Check if the provided url is a full and valide URL

    ### DUPLICATE: See yojenkins.utility.utility

    Args:
        url: The URL to check

    Returns:
        True if full and valid, else False
    """
    # TODO: Remove this function from this file
    #       Do url check within the class, not within the cli to not keep repeating it
    #       In classes use yojenkins.utility.utility.is_full_url()

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


def server_target_check(target: str) -> bool:
    """TODO"""
    pass


def log_to_history(decorated_function) -> Callable:
    """This function decorates a function that is a cli command.
    The function will log the CLI command and its info to the command history.

    Details: Add this function like "@log_to_history" to a function

    Args:
        decorated_function : Function that is decorated

    Returns:
        None
    """
    # Get the profile argument index
    argspec = getfullargspec(decorated_function)
    try:
        arg_index = argspec.args.index('profile')
    except ValueError:
        arg_index = -1

    def wrapper(*args, **kwargs) -> None:
        # Get the profile name for the command
        if 'profile' in kwargs:
            profile_name = kwargs['profile']
        elif arg_index >= 0:
            profile_name = args[arg_index]
        else:
            # If no profile is used by the decorated function, use the default profile name
            profile_name = DEFAULT_PROFILE_NAME

        if profile_name is None:
            # If function has profile argument, but none was passed, use the default profile name
            profile_name = DEFAULT_PROFILE_NAME

        # Check if history file exists
        history_file_path = os.path.join(os.path.join(Path.home(), CONFIG_DIR_NAME), HISTORY_FILE_NAME)
        if not os.path.isfile(history_file_path):
            create_new_history_file(history_file_path)

        # Load the history file content
        file_contents = load_contents_from_local_file(COMMAND_HISTORY_FORMAT, history_file_path)
        if not file_contents:
            logger.debug("Command history file is blank")

        # If profile history length is too long, remove the oldest history item
        if profile_name in file_contents:
            if len(file_contents[profile_name]) > MAX_PROFILE_HISTORY_LENGTH:
                file_contents[profile_name].pop(0)

        # Add the command to the history file
        logger.debug(f'Logging command to command history file: "{history_file_path}" ...')
        if profile_name not in file_contents:
            file_contents[profile_name] = []

        command_info = {
            'tool_path': CLI_CMD_PATH,
            'arguments': CLI_CMD_ARGS,
            'timestamp': datetime.now().timestamp(),
            'datetime': datetime.now().strftime("%A, %B %d, %Y %I:%M:%S"),
            'tool_version': __version__
        }
        file_contents[profile_name].append(command_info)

        # Add to file, overwritting entire file
        try:
            with open(history_file_path, 'w') as outfile:
                json.dump(file_contents, outfile, indent=4)
        except Exception as error:
            logger.debug(f'Failed to write command history file: {error}')

        return decorated_function(*args, **kwargs)

    return wrapper
