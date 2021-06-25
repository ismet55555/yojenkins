#!/usr/bin/env python3

import json
import logging
import sys
from pprint import pprint

import click
import xmltodict

from . import cli_utility as cu

# Getting the logger reference
logger = logging.getLogger()


def info(opt_pretty: bool, opt_yaml: bool, opt_xml: bool, opt_toml: bool, profile: str, folder: str) -> None:
    """TODO Docstring

    Details: TODO

    Args:
        TODO

    Returns:
        TODO
    """
    jy_obj = cu.config_yo_jenkins(profile)
    if cu.is_full_url(folder):
        data = jy_obj.Folder.info(folder_url=folder)
    else:
        data = jy_obj.Folder.info(folder_name=folder)

    if not data:
        click.echo(click.style('no folder information', fg='bright_red', bold=True))
        sys.exit(1)
    cu.standard_out(data, opt_pretty, opt_yaml, opt_xml, opt_toml)


def search(opt_pretty: bool, opt_yaml: bool, opt_xml: bool, opt_toml: bool, profile: str, search_pattern: str,
           search_folder: str, depth: int, fullname: bool, opt_list: bool) -> None:
    """TODO Docstring

    Details: TODO

    Args:
        TODO

    Returns:
        TODO
    """
    jy_obj = cu.config_yo_jenkins(profile)
    if cu.is_full_url(search_folder):
        data, data_list = jy_obj.Folder.search(search_pattern=search_pattern,
                                           folder_url=search_folder,
                                           folder_depth=depth,
                                           fullname=fullname)
    else:
        data, data_list = jy_obj.Folder.search(search_pattern=search_pattern,
                                           folder_name=search_folder,
                                           folder_depth=depth,
                                           fullname=fullname)

    if not data:
        click.echo(click.style('"not found', fg='bright_red', bold=True))
        sys.exit(1)
    data = data_list if opt_list else data
    cu.standard_out(data, opt_pretty, opt_yaml, opt_xml, opt_toml)


def subfolders(opt_pretty: bool, opt_yaml: bool, opt_xml: bool, opt_toml: bool, profile: str, folder: str,
               opt_list: bool) -> None:
    """TODO Docstring

    Details: TODO

    Args:
        TODO

    Returns:
        TODO
    """
    jy_obj = cu.config_yo_jenkins(profile)
    if cu.is_full_url(folder):
        data, data_list = jy_obj.Folder.subfolder_list(folder_url=folder)
    else:
        data, data_list = jy_obj.Folder.subfolder_list(folder_name=folder)

    if not data:
        click.echo(click.style('not found or no subfolders', fg='bright_red', bold=True))
        sys.exit(1)
    data = data_list if opt_list else data
    cu.standard_out(data, opt_pretty, opt_yaml, opt_xml, opt_toml)


def jobs(opt_pretty: bool, opt_yaml: bool, opt_xml: bool, opt_toml: bool, profile: str, folder: str,
         opt_list: bool) -> None:
    """TODO Docstring

    Details: TODO

    Args:
        TODO

    Returns:
        TODO
    """
    jy_obj = cu.config_yo_jenkins(profile)
    if cu.is_full_url(folder):
        data, data_list = jy_obj.Folder.jobs_list(folder_url=folder)
    else:
        data, data_list = jy_obj.Folder.jobs_list(folder_name=folder)

    if not data:
        click.echo(click.style('not found', fg='bright_red', bold=True))
        sys.exit(1)
    data = data_list if opt_list else data
    cu.standard_out(data, opt_pretty, opt_yaml, opt_xml, opt_toml)


def views(opt_pretty: bool, opt_yaml: bool, opt_xml: bool, opt_toml: bool, profile: str, folder: str,
          opt_list: int) -> None:
    """TODO Docstring

    Details: TODO

    Args:
        TODO

    Returns:
        TODO
    """
    jy_obj = cu.config_yo_jenkins(profile)
    if cu.is_full_url(folder):
        data, data_list = jy_obj.Folder.view_list(folder_url=folder)
    else:
        data, data_list = jy_obj.Folder.view_list(folder_name=folder)

    if not data:
        click.echo(click.style('not found', fg='bright_red', bold=True))
        sys.exit(1)
    data = data_list if opt_list else data
    cu.standard_out(data, opt_pretty, opt_yaml, opt_xml, opt_toml)


def items(opt_pretty: bool, opt_yaml: bool, opt_xml: bool, opt_toml: bool, profile: str, folder: str,
          opt_list: int) -> None:
    """TODO Docstring

    Details: TODO

    Args:
        TODO

    Returns:
        TODO
    """
    jy_obj = cu.config_yo_jenkins(profile)
    if cu.is_full_url(folder):
        data, data_list = jy_obj.Folder.item_list(folder_url=folder)
    else:
        data, data_list = jy_obj.Folder.item_list(folder_name=folder)

    if not data:
        click.echo(click.style('not found or no folder items', fg='bright_red', bold=True))
        sys.exit(1)
    data = data_list if opt_list else data
    cu.standard_out(data, opt_pretty, opt_yaml, opt_xml, opt_toml)


def browser(profile: str, folder: str) -> None:
    """TODO Docstring

    Details: TODO

    Args:
        TODO

    Returns:
        TODO
    """
    jy_obj = cu.config_yo_jenkins(profile)
    if cu.is_full_url(folder):
        data = jy_obj.Folder.browser_open(folder_url=folder)
    else:
        data = jy_obj.Folder.browser_open(folder_name=folder)

    if not data:
        click.echo(click.style('failed', fg='bright_red', bold=True))
        sys.exit(1)


def config(opt_pretty: bool, opt_yaml: bool, opt_xml: bool, opt_toml: bool, opt_json: bool, profile: str, folder: str,
           filepath: str) -> None:
    """TODO Docstring

    Details: TODO

    Args:
        TODO

    Returns:
        TODO
    """
    jy_obj = cu.config_yo_jenkins(profile)
    if cu.is_full_url(folder):
        data, write_success = jy_obj.Folder.config(filepath=filepath,
                                               folder_url=folder,
                                               opt_json=opt_json,
                                               opt_yaml=opt_yaml,
                                               opt_toml=opt_toml)
    else:
        data, write_success = jy_obj.Folder.config(filepath=filepath,
                                               folder_name=folder,
                                               opt_json=opt_json,
                                               opt_yaml=opt_yaml,
                                               opt_toml=opt_toml)

    if not data:
        click.echo(click.style('failed', fg='bright_red', bold=True))
        sys.exit(1)

    if not write_success:
        click.echo(click.style('failed to write', fg='bright_red', bold=True))
        sys.exit(1)

    # Converting XML to dict
    # data = json.loads(json.dumps(xmltodict.parse(data)))

    opt_xml = False if any([opt_json, opt_yaml, opt_toml]) else True
    data = data if opt_xml else json.loads(json.dumps(xmltodict.parse(data)))
    cu.standard_out(data, opt_pretty, opt_yaml, opt_xml, opt_toml)


def create(profile: str, name: str, folder: str, type: str, config: str) -> None:
    """TODO Docstring

    Details: TODO

    Args:
        TODO

    Returns:
        TODO
    """
    jy_obj = cu.config_yo_jenkins(profile)
    if cu.is_full_url(folder):
        data = jy_obj.Folder.create(name=name, type=type, config=config, folder_url=folder)
    else:
        data = jy_obj.Folder.create(name=name, type=type, config=config, folder_name=folder)

    if not data:
        click.echo(click.style('failed', fg='bright_red', bold=True))
        sys.exit(1)
    click.echo(click.style('success', fg='bright_green', bold=True))


def copy(profile: str, folder: str, original_name: str, new_name: str) -> None:
    """TODO Docstring

    Details: TODO

    Args:
        TODO

    Returns:
        TODO
    """
    # TODO: Maybe return the newly copied item url

    jy_obj = cu.config_yo_jenkins(profile)
    if cu.is_full_url(folder):
        data = jy_obj.Folder.copy(original_name=original_name, new_name=new_name, folder_url=folder)
    else:
        data = jy_obj.Folder.copy(original_name=original_name, new_name=new_name, folder_name=folder)

    if not data:
        click.echo(click.style('failed', fg='bright_red', bold=True))
        sys.exit(1)
    click.echo(click.style('success', fg='bright_green', bold=True))


def delete(profile: str, folder: str) -> None:
    """TODO Docstring

    Details: TODO

    Args:
        TODO

    Returns:
        TODO
    """
    jy_obj = cu.config_yo_jenkins(profile)
    if cu.is_full_url(folder):
        data = jy_obj.Folder.delete(folder_url=folder)
    else:
        data = jy_obj.Folder.delete(folder_name=folder)

    if not data:
        click.echo(click.style('failed', fg='bright_red', bold=True))
        sys.exit(1)
    click.echo(click.style('success', fg='bright_green', bold=True))
