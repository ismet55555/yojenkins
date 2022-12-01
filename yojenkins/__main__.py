"""Main entry point for program"""
# pylint: skip-file

import logging
import sys

import click
from click_help_colors import HelpColorsGroup

from yojenkins import __version__
from yojenkins.cli import logger_setup
from yojenkins.cli.cli_utility import set_debug_log_level

logger = logging.getLogger()

if sys.version_info < (3, 7):
    click.secho('Your Python version ({}.{}) is not supported'.format(sys.version_info.major, sys.version_info.minor), fg='bright_red', bold=True)
    click.secho('Must have Python 3.7 or higher', fg='bright_red', bold=True)
    sys.exit(1)

##############################################################################


MAIN_HELP_TEXT = f"""
    \t\t\t \033[93m YOJENKINS (Version: {__version__}) \033[0m

    yojenkins is a flexible tool that is focused on interfacing with
    Jenkins server from the comfort of the beloved command line.
    This tool can also be used as a middleware utility, generating and
    passing Jenkins information or automating tasks.

    QUICK START:

    \b
      1. Configure yo profile:  yojenkins auth configure
      2. Add yo API token:      yojenkins auth token --profile <PROFILE NAME>
      3. Verify yo creds:       yojenkins auth verify
      4. Explore yojenkins
"""


##############################################################################


@click.group(help=MAIN_HELP_TEXT)
@click.version_option(
    __version__, "-v", "--version", message="%(version)s".format(version="version"),
    help="Show the version"
)
def main():
    pass

# -----------------------------------------------------------------------------
@main.group(short_help='\tManage authentication and profiles',
    cls=HelpColorsGroup,
    help_options_custom_colors={
        'wipe': 'black'
        })
def auth():
    """Authentication And Profile Management"""
    pass
from yojenkins.cli_sub_commands import auth


# -----------------------------------------------------------------------------
@main.group(short_help='\tManage server')
def server():
    """Server Management"""
    pass
from yojenkins.cli_sub_commands import server


# -----------------------------------------------------------------------------
@main.group(short_help='\tManage nodes',
    cls=HelpColorsGroup,
    help_options_custom_colors={
        'prepare': 'black',
        'status': 'black',
        'create-ephemeral': 'black',
        'logs': 'black',
        })
def node():
    """Node Management"""
    pass
from yojenkins.cli_sub_commands import node


# -----------------------------------------------------------------------------
@main.group(short_help='\tManage user accounts',
cls=HelpColorsGroup,
    help_options_custom_colors={
        'password-reset': 'black',
        })
def account():
    """Account/User Management"""
    pass
from yojenkins.cli_sub_commands import account


# -----------------------------------------------------------------------------
@main.group(short_help='\tManage credentials',
cls=HelpColorsGroup,
    help_options_custom_colors={
        'update': 'black',
        'move': 'black'
        })
def credential():
    """Credentials Management"""
    pass
from yojenkins.cli_sub_commands import credential


# -----------------------------------------------------------------------------
@main.group(short_help='\tManage folders')
def folder():
    """Folder Management"""
    pass
from yojenkins.cli_sub_commands import folder


# -----------------------------------------------------------------------------
@main.group(short_help='\tManage jobs',
    cls=HelpColorsGroup,
    help_options_custom_colors={
        'queue_cancel': 'black'
        })
def job():
    """Job Management"""
    pass
from yojenkins.cli_sub_commands import job


# -----------------------------------------------------------------------------
@main.group(short_help='\tManage builds')
def build():
    """Build Management"""
    pass
from yojenkins.cli_sub_commands import build


# -----------------------------------------------------------------------------
@main.group(short_help='\tManage build stages')
def stage():
    """Stage Management"""
    pass
from yojenkins.cli_sub_commands import stage


# -----------------------------------------------------------------------------
@main.group(short_help='\tManage stage steps')
def step():
    """Step Management"""
    pass
from yojenkins.cli_sub_commands import step


# -----------------------------------------------------------------------------
@main.group(short_help='\tTools and more')
def tools():
    """Utility And More"""
    pass
from yojenkins.cli_sub_commands import tools

##############################################################################
##############################################################################
##############################################################################
if __name__ == "__main__":
    """Main entry point to the entire program"""
    main()
