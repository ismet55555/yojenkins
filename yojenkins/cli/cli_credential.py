"""Credential Menu CLI Entrypoints"""

import json
import logging
import sys

import click
import xmltodict

from yojenkins.cli import cli_utility as cu
from yojenkins.cli.cli_utility import log_to_history

# Getting the logger reference
logger = logging.getLogger()


@log_to_history
def list(opt_pretty: bool, opt_yaml: bool, opt_xml: bool, opt_toml: bool, opt_list: bool, profile: str, folder: str,
         domain: str, keys: str) -> None:
    """TODO Docstring

    Details: TODO

    Args:
        TODO

    Returns:
        TODO
    """
    yj_obj = cu.config_yo_jenkins(profile)
    data, data_list = yj_obj.credential.list(folder=folder, domain=domain, keys=keys)

    if not data:
        click.echo(click.style('failed', fg='bright_red', bold=True))
        sys.exit(1)
    data = data_list if opt_list else data
    cu.standard_out(data, opt_pretty, opt_yaml, opt_xml, opt_toml)


@log_to_history
def info(opt_pretty: bool, opt_yaml: bool, opt_xml: bool, opt_toml: bool, profile: str, credential: str, folder: str,
         domain: str) -> None:
    """TODO Docstring

    Details: TODO

    Args:
        TODO

    Returns:
        TODO
    """
    yj_obj = cu.config_yo_jenkins(profile)
    data = yj_obj.credential.info(credential=credential, folder=folder, domain=domain)
    if not data:
        click.echo(click.style('no credential information', fg='bright_red', bold=True))
        sys.exit(1)
    cu.standard_out(data, opt_pretty, opt_yaml, opt_xml, opt_toml)


@log_to_history
def config(opt_pretty: bool, opt_yaml: bool, opt_xml: bool, opt_toml: bool, opt_json: bool, profile: str,
           credential: str, folder: str, domain: str, filepath: str) -> None:
    """TODO Docstring

    Details: TODO

    Args:
        TODO

    Returns:
        TODO
    """
    yj_obj = cu.config_yo_jenkins(profile)
    data, write_success = yj_obj.credential.config(credential=credential,
                                                   folder=folder,
                                                   domain=domain,
                                                   opt_json=opt_json,
                                                   opt_yaml=opt_yaml,
                                                   opt_toml=opt_toml,
                                                   filepath=filepath)
    if not data:
        click.echo(click.style('failed', fg='bright_red', bold=True))
        sys.exit(1)

    if not write_success:
        click.echo(click.style('failed to write', fg='bright_red', bold=True))
        sys.exit(1)

    opt_xml = not any([opt_json, opt_yaml, opt_toml])
    data = data if opt_xml else json.loads(json.dumps(xmltodict.parse(data)))
    cu.standard_out(data, opt_pretty, opt_yaml, opt_xml, opt_toml)


@log_to_history
def get_template(opt_pretty: bool, opt_yaml: bool, opt_xml: bool, opt_toml: bool, opt_json: bool, profile: str,
                 cred_type: str, filepath: str) -> None:
    """TODO Docstring

    Details: TODO

    Args:
        TODO

    Returns:
        TODO
    """
    yj_obj = cu.config_yo_jenkins(profile)
    data, write_success = yj_obj.credential.get_template(cred_type=cred_type,
                                                         opt_json=opt_json,
                                                         opt_yaml=opt_yaml,
                                                         opt_toml=opt_toml,
                                                         filepath=filepath)
    if not data:
        click.echo(click.style('failed', fg='bright_red', bold=True))
        sys.exit(1)

    if not write_success:
        click.echo(click.style('failed to write', fg='bright_red', bold=True))
        sys.exit(1)

    opt_xml = not any([opt_json, opt_yaml, opt_toml])
    data = data if opt_xml else json.loads(json.dumps(xmltodict.parse(data)))
    cu.standard_out(data, opt_pretty, opt_yaml, opt_xml, opt_toml)


@log_to_history
def create(profile: str, config_file: str, folder: str, domain: str) -> None:
    """TODO Docstring

    Details: TODO

    Args:
        TODO

    Returns:
        TODO
    """
    yj_obj = cu.config_yo_jenkins(profile)
    data = yj_obj.credential.create(config_file=config_file, folder=folder, domain=domain)
    if not data:
        click.echo(click.style('failed', fg='bright_red', bold=True))
        sys.exit(1)
    click.echo(click.style('success', fg='bright_green', bold=True))


@log_to_history
def delete(profile: str, credential: str, folder: str, domain: str) -> None:
    """TODO Docstring

    Details: TODO

    Args:
        TODO

    Returns:
        TODO
    """
    yj_obj = cu.config_yo_jenkins(profile)
    data = yj_obj.credential.delete(credential=credential, folder=folder, domain=domain)
    if not data:
        click.echo(click.style('failed', fg='bright_red', bold=True))
        sys.exit(1)
    click.echo(click.style('success', fg='bright_green', bold=True))
