"""Step Menu CLI Entrypoints"""

import logging
import sys

import click

from yojenkins.cli import cli_utility as cu
from yojenkins.cli.cli_utility import log_to_history

# Getting the logger reference
logger = logging.getLogger()


@log_to_history
def info(profile: str, token: str, url: str, **kwargs) -> None:
    """TODO Docstring

    Details: TODO

    Args:
        TODO
    """
    # Check if URL is ok
    if not cu.is_full_url(url):
        click.secho(f'INPUT ERROR: Step url is not a URL: {url}', fg='bright_red', bold=True)
        sys.exit(1)

    yj_obj = cu.config_yo_jenkins(profile, token)

    # Request the data
    data = yj_obj.step.info(step_url=url)

    if not data:
        click.secho('No step information', fg='bright_red', bold=True)
        sys.exit(1)
    cu.standard_out(data, **kwargs)
