#!/usr/bin/env python3

import logging
import sys

import click

from . import cli_utility as cu

# Getting the logger reference
logger = logging.getLogger()


def info(opt_pretty:bool, opt_yaml:bool, opt_xml:bool, profile:str, folder:str) -> None:
    """TODO Docstring

    Details: TODO

    Args:
        TODO

    Returns:
        TODO
    """
    JY = cu.config_YoJenkins(profile)
    valid_url_format = cu.is_full_url(folder)

    if valid_url_format:
        data = JY.Folder.info(folder_url=folder)
    else:
        data = JY.Folder.info(folder_name=folder)

    if not data:
        click.echo(click.style(f'no folder information', fg='bright_red', bold=True))
        sys.exit(1)
    cu.standard_out(data, opt_pretty, opt_yaml, opt_xml)


def search(opt_pretty:bool, opt_yaml:bool, opt_xml:bool, profile:str, search_pattern:str, search_folder:str, depth:int, fullname:bool, opt_list:bool) -> None:
    """TODO Docstring

    Details: TODO

    Args:
        TODO

    Returns:
        TODO
    """
    JY = cu.config_YoJenkins(profile)
    valid_url_format = cu.is_full_url(search_folder)

    if valid_url_format:
        data, data_list = JY.Folder.search(search_pattern=search_pattern, folder_url=search_folder, folder_depth=depth, fullname=fullname)
    else:
        data, data_list = JY.Folder.search(search_pattern=search_pattern, folder_name=search_folder, folder_depth=depth, fullname=fullname)

    if not data:
        click.echo(click.style(f'"not found', fg='bright_red', bold=True))
        sys.exit(1)
    data = data_list if opt_list else data
    cu.standard_out(data, opt_pretty, opt_yaml, opt_xml)


def subfolders(opt_pretty:bool, opt_yaml:bool, opt_xml:bool, profile:str, folder:str, opt_list:bool) -> None:
    """TODO Docstring

    Details: TODO

    Args:
        TODO

    Returns:
        TODO
    """
    JY = cu.config_YoJenkins(profile)
    valid_url_format = cu.is_full_url(folder)

    if valid_url_format:
        data, data_list = JY.Folder.subfolder_list(folder_url=folder)
    else:
        data, data_list = JY.Folder.subfolder_list(folder_name=folder)

    if not data:
        click.echo(click.style(f'not found or no subfolders', fg='bright_red', bold=True))
        sys.exit(1)
    data = data_list if opt_list else data
    cu.standard_out(data, opt_pretty, opt_yaml, opt_xml)


def jobs(opt_pretty:bool, opt_yaml:bool, opt_xml:bool, profile:str, folder:str, opt_list:bool) -> None:
    """TODO Docstring

    Details: TODO

    Args:
        TODO

    Returns:
        TODO
    """
    JY = cu.config_YoJenkins(profile)
    valid_url_format = cu.is_full_url(folder)

    if valid_url_format:
        data, data_list = JY.Folder.jobs_list(folder_url=folder)
    else:
        data, data_list = JY.Folder.jobs_list(folder_name=folder)

    if not data:
        click.echo(click.style(f'not found', fg='bright_red', bold=True))
        sys.exit(1)
    data = data_list if opt_list else data
    cu.standard_out(data, opt_pretty, opt_yaml, opt_xml)


def views(opt_pretty:bool, opt_yaml:bool, opt_xml:bool, profile:str, folder:str, opt_list:int) -> None:
    """TODO Docstring

    Details: TODO

    Args:
        TODO

    Returns:
        TODO
    """
    JY = cu.config_YoJenkins(profile)
    valid_url_format = cu.is_full_url(folder)

    if valid_url_format:
        data, data_list = JY.Folder.view_list(folder_url=folder)
    else:
        data, data_list = JY.Folder.view_list(folder_name=folder)

    if not data:
        click.echo(click.style(f'not found', fg='bright_red', bold=True))
        sys.exit(1)
    data = data_list if opt_list else data
    cu.standard_out(data, opt_pretty, opt_yaml, opt_xml)


def items(opt_pretty:bool, opt_yaml:bool, opt_xml:bool, profile:str, folder:str, opt_list:int) -> None:
    """TODO Docstring

    Details: TODO

    Args:
        TODO

    Returns:
        TODO
    """
    JY = cu.config_YoJenkins(profile)
    valid_url_format = cu.is_full_url(folder)

    if valid_url_format:
        data, data_list = JY.Folder.item_list(folder_url=folder)
    else:
        data, data_list = JY.Folder.item_list(folder_name=folder)

    if not data:
        click.echo(click.style(f'not found or no folder items', fg='bright_red', bold=True))
        sys.exit(1)
    data = data_list if opt_list else data
    cu.standard_out(data, opt_pretty, opt_yaml, opt_xml)


def browser(profile:str, folder:str) -> None:
    """TODO Docstring

    Details: TODO

    Args:
        TODO

    Returns:
        TODO
    """
    JY = cu.config_YoJenkins(profile)
    valid_url_format = cu.is_full_url(folder)

    if valid_url_format:
        data= JY.Folder.browser_open(folder_url=folder)
    else:
        data = JY.Folder.browser_open(folder_name=folder)

    if not data:
        click.echo(click.style(f'failed', fg='bright_red', bold=True))
        sys.exit(1)


def config(profile:str, folder:str, filepath:str) -> None:
    """TODO Docstring

    Details: TODO

    Args:
        TODO

    Returns:
        TODO
    """
    JY = cu.config_YoJenkins(profile)
    valid_url_format = cu.is_full_url(folder)

    if valid_url_format:
        data, write_success = JY.Folder.config(filepath=filepath, folder_url=folder)
    else:
        data, write_success = JY.Folder.config(filepath=filepath, folder_name=folder)

    if not data:
        click.echo(click.style(f'failed', fg='bright_red', bold=True))
        sys.exit(1)

    if not write_success:
        click.echo(click.style(f'failed to write', fg='bright_red', bold=True))
        sys.exit(1)



def create(profile:str, folder:str, name:str, type:str, xml_file:str) -> None:
    """TODO Docstring

    Details: TODO

    Args:
        TODO

    Returns:
        TODO
    """
    JY = cu.config_YoJenkins(profile)
    valid_url_format = cu.is_full_url(folder)

    if valid_url_format:
        data = JY.Folder.create(name=name, type=type, xml_file=xml_file, folder_url=folder)
    else:
        data = JY.Folder.create(name=name, type=type, xml_file=xml_file, folder_name=folder)

    if not data:
        click.echo(click.style(f'failed', fg='bright_red', bold=True))
        sys.exit(1)
    click.echo(click.style(f'{data}', fg='bright_green', bold=True))


def copy(profile:str, folder:str, original_name:str, new_name:str) -> None:
    """TODO Docstring

    Details: TODO

    Args:
        TODO

    Returns:
        TODO
    """
    # TODO: Maybe return the newly copied item url

    JY = cu.config_YoJenkins(profile)
    valid_url_format = cu.is_full_url(folder)

    if valid_url_format:
        data = JY.Folder.copy(original_name=original_name, new_name=new_name, folder_url=folder)
    else:
        data = JY.Folder.copy(original_name=original_name, new_name=new_name, folder_name=folder)

    if not data:
        click.echo(click.style(f'failed', fg='bright_red', bold=True))
        sys.exit(1)
    click.echo(click.style(f'{data}', fg='bright_green', bold=True))


def delete(profile:str, folder:str) -> None:
    """TODO Docstring

    Details: TODO

    Args:
        TODO

    Returns:
        TODO
    """
    JY = cu.config_YoJenkins(profile)
    valid_url_format = cu.is_full_url(folder)

    if valid_url_format:
        data= JY.Folder.delete(folder_url=folder)
    else:
        data = JY.Folder.delete(folder_name=folder)

    if not data:
        click.echo(click.style(f'failed', fg='bright_red', bold=True))
        sys.exit(1)