"""Step click sub-command"""
# pylint: skip-file

import click

from yojenkins.__main__ import step
from yojenkins.cli import cli_decorators, cli_step
from yojenkins.cli.cli_utility import set_debug_log_level
from yojenkins.utility.utility import translate_kwargs


@step.command(short_help='\tStep information')
@cli_decorators.debug
@cli_decorators.format_output
@cli_decorators.profile
@click.argument('url', nargs=1, type=str, required=True)
def info(debug, **kwargs):
    """Step information"""
    set_debug_log_level(debug)
    cli_step.info(**translate_kwargs(kwargs))
