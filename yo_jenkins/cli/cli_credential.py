#!/usr/bin/env python3

import logging
import sys

import click
from yo_jenkins.cli import cli_utility as cu
from yo_jenkins.cli.cli_utility import log_to_history

# Getting the logger reference
logger = logging.getLogger()


@log_to_history
def list(opt_pretty: bool, opt_yaml: bool, opt_xml: bool, opt_toml: bool, opt_list: bool, profile: str, folder: str,
         store: str, domain: str, keys: str) -> None:
    """TODO Docstring

    Details: TODO

    Args:
        TODO

    Returns:
        TODO
    """
    yj = cu.config_yo_jenkins(profile)
    if cu.is_full_url(folder):
        data, data_list = yj.Credential.list(folder_url=folder, store=store, domain=domain, keys=keys)
    else:
        data, data_list = yj.Credential.list(folder_name=folder, store=store, domain=domain, keys=keys)

    if not data:
        click.echo(click.style('failed', fg='bright_red', bold=True))
        sys.exit(1)
    data = data_list if opt_list else data
    cu.standard_out(data, opt_pretty, opt_yaml, opt_xml, opt_toml)
