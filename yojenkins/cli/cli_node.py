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
def info(opt_pretty: bool, opt_yaml: bool, opt_xml: bool, opt_toml: bool, profile: str, node_name: str,
         depth: int) -> None:
    """TODO Docstring

    Details: TODO

    Args:
        TODO

    Returns:
        TODO
    """
    yj_obj = cu.config_yo_jenkins(profile)
    data = yj_obj.node.info(node_name, depth)
    cu.standard_out(data, opt_pretty, opt_yaml, opt_xml, opt_toml)


@log_to_history
def list(opt_pretty: bool, opt_yaml: bool, opt_xml: bool, opt_toml: bool, opt_list: bool, profile: str,
         depth: int) -> None:
    """TODO Docstring

    Details: TODO

    Args:
        TODO

    Returns:
        TODO
    """
    yj_obj = cu.config_yo_jenkins(profile)
    data, data_list = yj_obj.node.list(depth)
    data = data_list if opt_list else data
    cu.standard_out(data, opt_pretty, opt_yaml, opt_xml, opt_toml)


@log_to_history
def create_permanent(profile: str, **kwargs) -> None:
    """TODO Docstring

    Details: TODO

    Args:
        TODO

    Returns:
        TODO
    """
    yj_obj = cu.config_yo_jenkins(profile)
    yj_obj.node.create_permanent(**kwargs)
    click.secho('success', fg='bright_green', bold=True)


@log_to_history
def delete(profile: str, node_name: str) -> None:
    """TODO Docstring

    Details: TODO

    Args:
        TODO

    Returns:
        TODO
    """
    yj_obj = cu.config_yo_jenkins(profile)
    yj_obj.node.delete(node_name)
    click.secho('success', fg='bright_green', bold=True)


@log_to_history
def disable(profile: str, node_name: str, message: str) -> None:
    """TODO Docstring

    Details: TODO

    Args:
        TODO

    Returns:
        TODO
    """
    yj_obj = cu.config_yo_jenkins(profile)
    yj_obj.node.disable(node_name, message)
    click.secho('success', fg='bright_green', bold=True)


@log_to_history
def enable(profile: str, node_name: str, message: str) -> None:
    """TODO Docstring

    Details: TODO

    Args:
        TODO

    Returns:
        TODO
    """
    yj_obj = cu.config_yo_jenkins(profile)
    yj_obj.node.enable(node_name, message)
    click.secho('success', fg='bright_green', bold=True)


@log_to_history
def config(opt_pretty: bool, opt_yaml: bool, opt_xml: bool, opt_toml: bool, opt_json: bool, profile: str,
           node_name: str, filepath: str) -> None:
    """TODO Docstring

    Details: TODO

    Args:
        TODO

    Returns:
        TODO
    """
    yj_obj = cu.config_yo_jenkins(profile)
    data = yj_obj.node.config(filepath=filepath,
                              node_name=node_name,
                              opt_json=opt_json,
                              opt_yaml=opt_yaml,
                              opt_toml=opt_toml)
    opt_xml = not any([opt_json, opt_yaml, opt_toml])
    data = data if opt_xml else json.loads(json.dumps(xmltodict.parse(data)))
    cu.standard_out(data, opt_pretty, opt_yaml, opt_xml, opt_toml)


@log_to_history
def reconfig(profile: str, node_name: str, config_file: str, config_is_json: str) -> None:
    """TODO Docstring

    Details: TODO

    Args:
        TODO

    Returns:
        TODO
    """
    yj_obj = cu.config_yo_jenkins(profile)
    yj_obj.node.reconfig(config_file=config_file, node_name=node_name, config_is_json=config_is_json)
    click.secho('success', fg='bright_green', bold=True)
