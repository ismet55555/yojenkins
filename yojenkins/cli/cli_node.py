"""Node Menu CLI Entrypoints"""

import json
import logging

import click
import xmltodict

from yojenkins.cli import cli_utility as cu
from yojenkins.cli.cli_utility import log_to_history

# Getting the logger reference
logger = logging.getLogger()


@log_to_history
def info(profile: str, token: str, name: str, depth: int, **kwargs) -> None:
    """TODO Docstring

    Details: TODO

    Args:
        TODO
    """
    yj_obj = cu.config_yo_jenkins(profile, token)
    data = yj_obj.node.info(name, depth)
    cu.standard_out(data, **kwargs)


@log_to_history
def list(profile: str, token: str, opt_list: bool, depth: int, **kwargs) -> None:
    """TODO Docstring

    Details: TODO

    Args:
        TODO
    """
    yj_obj = cu.config_yo_jenkins(profile, token)
    data, data_list = yj_obj.node.list(depth)
    data = data_list if opt_list else data
    cu.standard_out(data, **kwargs)


@log_to_history
def create_permanent(profile: str, token: str, **kwargs) -> None:
    """TODO Docstring

    Details: TODO

    Args:
        TODO
    """
    yj_obj = cu.config_yo_jenkins(profile, token)
    yj_obj.node.create_permanent(**kwargs)
    click.secho('success', fg='bright_green', bold=True)


@log_to_history
def delete(profile: str, token: str, name: str) -> None:
    """TODO Docstring

    Details: TODO

    Args:
        TODO
    """
    yj_obj = cu.config_yo_jenkins(profile, token)
    yj_obj.node.delete(name)
    click.secho('success', fg='bright_green', bold=True)


@log_to_history
def disable(profile: str, token: str, name: str, message: str) -> None:
    """TODO Docstring

    Details: TODO

    Args:
        TODO
    """
    yj_obj = cu.config_yo_jenkins(profile, token)
    yj_obj.node.disable(name, message)
    click.secho('success', fg='bright_green', bold=True)


@log_to_history
def enable(profile: str, token: str, name: str, message: str) -> None:
    """TODO Docstring

    Details: TODO

    Args:
        TODO
    """
    yj_obj = cu.config_yo_jenkins(profile, token)
    yj_obj.node.enable(name, message)
    click.secho('success', fg='bright_green', bold=True)


@log_to_history
def config(profile: str, token: str, opt_pretty: bool, opt_yaml: bool, opt_xml: bool, opt_toml: bool, opt_json: bool,
           name: str, filepath: str) -> None:
    """TODO Docstring

    Details: TODO

    Args:
        TODO
    """
    yj_obj = cu.config_yo_jenkins(profile, token)
    data = yj_obj.node.config(filepath=filepath,
                              node_name=name,
                              opt_json=opt_json,
                              opt_yaml=opt_yaml,
                              opt_toml=opt_toml)
    opt_xml = not any([opt_json, opt_yaml, opt_toml])
    data = data if opt_xml else json.loads(json.dumps(xmltodict.parse(data)))
    cu.standard_out(data, opt_pretty, opt_yaml, opt_xml, opt_toml)


@log_to_history
def reconfig(profile: str, token: str, name: str, config_file: str, config_is_json: bool) -> None:
    """TODO Docstring

    Details: TODO

    Args:
        TODO
    """
    yj_obj = cu.config_yo_jenkins(profile, token)
    yj_obj.node.reconfig(config_file=config_file, node_name=name, config_is_json=config_is_json)
    click.secho('success', fg='bright_green', bold=True)
