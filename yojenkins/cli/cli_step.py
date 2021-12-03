"""Step Menu CLI Entrypoints"""

import logging
import sys

import click

from yojenkins.cli import cli_utility as cu
from yojenkins.cli.cli_utility import log_to_history

# Getting the logger reference
logger = logging.getLogger()


@log_to_history
def info(opt_pretty: bool, opt_yaml: bool, opt_xml: bool, opt_toml: bool, profile: str, step_url: str) -> None:
    """TODO Docstring

    Details: TODO

    Args:
        TODO

    Returns:
        TODO
    """
    # Check if URL is ok
    if not cu.is_full_url(step_url):
        click.secho(f'INPUT ERROR: Step url is not a URL: {step_url}', fg='bright_red', bold=True)
        sys.exit(1)

    yj_obj = cu.config_yo_jenkins(profile)

    # Request the data
    data = yj_obj.step.info(step_url=step_url)

    if not data:
        click.secho('No step information', fg='bright_red', bold=True)
        sys.exit(1)
    cu.standard_out(data, opt_pretty, opt_yaml, opt_xml, opt_toml)
