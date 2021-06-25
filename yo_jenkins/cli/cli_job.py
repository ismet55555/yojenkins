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


def info(opt_pretty: bool, opt_yaml: bool, opt_xml: bool, opt_toml: bool, profile: str, job: str) -> None:
    """TODO Docstring

    Args:
        TODO

    Returns:
        TODO
    """
    jy_obj = cu.config_yo_jenkins(profile)
    if cu.is_full_url(job):
        data = jy_obj.Job.info(job_url=job)
    else:
        data = jy_obj.Job.info(job_name=job)

    if not data:
        click.echo(click.style('not found', fg='bright_red', bold=True))
        sys.exit(1)
    cu.standard_out(data, opt_pretty, opt_yaml, opt_xml, opt_toml)


def search(opt_pretty: bool, opt_yaml: bool, opt_xml: bool, opt_toml: bool, profile: str, search_pattern: str,
           search_folder: str, depth: int, fullname: bool, opt_list: bool) -> None:
    """TODO Docstring

    Args:
        TODO

    Returns:
        TODO
    """
    jy_obj = cu.config_yo_jenkins(profile)
    if cu.is_full_url(search_folder):
        data, data_list = jy_obj.Job.search(search_pattern=search_pattern,
                                        folder_url=search_folder,
                                        folder_depth=depth,
                                        fullname=fullname)
    else:
        data, data_list = jy_obj.Job.search(search_pattern=search_pattern,
                                        folder_name=search_folder,
                                        folder_depth=depth,
                                        fullname=fullname)

    if not data:
        click.echo(click.style('not found', fg='bright_red', bold=True))
        sys.exit(1)
    data = data_list if opt_list else data
    cu.standard_out(data, opt_pretty, opt_yaml, opt_xml, opt_toml)


def build_list(opt_pretty: bool, opt_yaml: bool, opt_xml: bool, opt_toml: bool, profile: str, job: str,
               opt_list: bool) -> None:
    """TODO Docstring

    Args:
        TODO

    Returns:
        TODO
    """
    jy_obj = cu.config_yo_jenkins(profile)
    if cu.is_full_url(job):
        data, data_list = jy_obj.Job.build_list(job_url=job)
    else:
        data, data_list = jy_obj.Job.build_list(job_name=job)

    if not data:
        click.echo(click.style('not found', fg='bright_red', bold=True))
        sys.exit(1)
    data = data_list if opt_list else data
    cu.standard_out(data, opt_pretty, opt_yaml, opt_xml, opt_toml)


def build_next(profile: str, job: str) -> None:
    """TODO Docstring

    Args:
        TODO

    Returns:
        TODO
    """
    jy_obj = cu.config_yo_jenkins(profile)
    if cu.is_full_url(job):
        data = jy_obj.Job.build_next_number(job_url=job)
    else:
        data = jy_obj.Job.build_next_number(job_name=job)

    if not data:
        click.echo(click.style('not found', fg='bright_red', bold=True))
        sys.exit(1)

    click.echo(click.style(f'{data}', fg='bright_green', bold=True))


def build_last(profile: str, job: str) -> None:
    """TODO Docstring

    Args:
        TODO

    Returns:
        TODO
    """
    jy_obj = cu.config_yo_jenkins(profile)
    if cu.is_full_url(job):
        data = jy_obj.Job.build_last_number(job_url=job)
    else:
        data = jy_obj.Job.build_last_number(job_name=job)

    if not data:
        click.echo(click.style('not found', fg='bright_red', bold=True))
        sys.exit(1)

    click.echo(click.style(f'{data}', fg='bright_green', bold=True))


def build_set(profile: str, job: str, build_number: int) -> None:
    """TODO Docstring

    Args:
        TODO

    Returns:
        TODO
    """
    jy_obj = cu.config_yo_jenkins(profile)
    if cu.is_full_url(job):
        data = jy_obj.Job.build_set_next_number(build_number=build_number, job_url=job)
    else:
        data = jy_obj.Job.build_set_next_number(build_number=build_number, job_name=job)

    if not data:
        click.echo(click.style('failed"', fg='bright_red', bold=True))
        sys.exit(1)

    click.echo(click.style(f'{build_number}', fg='bright_green', bold=True))


def build_exist(profile: str, job: str, build_number: int) -> None:
    """TODO Docstring

    Args:
        TODO

    Returns:
        TODO
    """
    jy_obj = cu.config_yo_jenkins(profile)
    if cu.is_full_url(job):
        data = jy_obj.Job.build_number_exist(build_number=build_number, job_url=job)
    else:
        data = jy_obj.Job.build_number_exist(build_number=build_number, job_name=job)

    if not data:
        click.echo(click.style('not found', fg='bright_red', bold=True))
        sys.exit(1)

    click.echo(click.style('true', fg='bright_green', bold=True))


def build(profile: str, job: str, parameters: tuple) -> None:
    """TODO Docstring

    Args:
        TODO

    Returns:
        TODO
    """
    jy_obj = cu.config_yo_jenkins(profile)

    # Convert a tuple of tuples to dict
    parameters = dict(list(parameters))

    if cu.is_full_url(job):
        data = jy_obj.Job.build_trigger(job_url=job, paramters=parameters)
    else:
        data = jy_obj.Job.build_trigger(job_name=job, paramters=parameters)

    if not data:
        click.echo(click.style('failed', fg='bright_red', bold=True))
        sys.exit(1)

    click.echo(click.style(f'success. queue number: {data}', fg='bright_green', bold=True))


def queue_check(opt_pretty: bool, opt_yaml: bool, opt_xml: bool, opt_toml: bool, profile: str, job: str,
                opt_id: bool) -> None:
    """TODO Docstring

    Args:
        TODO

    Returns:
        TODO
    """
    jy_obj = cu.config_yo_jenkins(profile)
    if cu.is_full_url(job):
        data, queue_id = jy_obj.Job.in_queue_check(job_url=job)
    else:
        data, queue_id = jy_obj.Job.in_queue_check(job_name=job)

    if not data:
        out = '{}' if not opt_id else '0'
        click.echo(click.style(out, fg='bright_red', bold=True))
        sys.exit(1)

    if opt_id:
        click.echo(click.style(f'{queue_id}', fg='bright_green', bold=True))
    else:
        cu.standard_out(data, opt_pretty, opt_yaml, opt_xml, opt_toml)


def browser(profile: str, job: str) -> None:
    """TODO Docstring

    Args:
        TODO

    Returns:
        TODO
    """
    jy_obj = cu.config_yo_jenkins(profile)
    if cu.is_full_url(job):
        data = jy_obj.Job.browser_open(job_url=job)
    else:
        data = jy_obj.Job.browser_open(job_name=job)

    if not data:
        click.echo(click.style('failed', fg='bright_red', bold=True))
        sys.exit(1)


def config(opt_pretty: bool, opt_yaml: bool, opt_xml: bool, opt_toml: bool, opt_json: bool, profile: str, job: str,
           filepath: str) -> None:
    """TODO Docstring

    Args:
        TODO

    Returns:
        TODO
    """
    jy_obj = cu.config_yo_jenkins(profile)
    if cu.is_full_url(job):
        data, write_success = jy_obj.Job.config(filepath=filepath,
                                            job_url=job,
                                            opt_json=opt_json,
                                            opt_yaml=opt_yaml,
                                            opt_toml=opt_toml)
    else:
        data, write_success = jy_obj.Job.config(filepath=filepath,
                                            job_name=job,
                                            opt_json=opt_json,
                                            opt_yaml=opt_yaml,
                                            opt_toml=opt_toml)

    if not data:
        click.echo(click.style('failed', fg='bright_red', bold=True))
        sys.exit(1)

    if not write_success:
        click.echo(click.style('failed to write to file', fg='bright_red', bold=True))
        sys.exit(1)

    # Converting XML to dict
    # data = json.loads(json.dumps(xmltodict.parse(data)))

    opt_xml = False if any([opt_json, opt_yaml, opt_toml]) else True
    data = data if opt_xml else json.loads(json.dumps(xmltodict.parse(data)))
    cu.standard_out(data, opt_pretty, opt_yaml, opt_xml, opt_toml)


def disable(profile: str, job: str) -> None:
    """TODO Docstring

    Args:
        TODO

    Returns:
        TODO
    """
    jy_obj = cu.config_yo_jenkins(profile)
    if cu.is_full_url(job):
        data = jy_obj.Job.disable(job_url=job)
    else:
        data = jy_obj.Job.disable(job_name=job)

    if not data:
        click.echo(click.style('failed', fg='bright_red', bold=True))
        sys.exit(1)
    click.echo(click.style('success', fg='bright_green', bold=True))


def enable(profile: str, job: str) -> None:
    """TODO Docstring

    Args:
        TODO

    Returns:
        TODO
    """
    jy_obj = cu.config_yo_jenkins(profile)
    if cu.is_full_url(job):
        data = jy_obj.Job.enable(job_url=job)
    else:
        data = jy_obj.Job.enable(job_name=job)

    if not data:
        click.echo(click.style('failed', fg='bright_red', bold=True))
        sys.exit(1)
    click.echo(click.style('success', fg='bright_green', bold=True))


def rename(profile: str, job: str, new_name: str) -> None:
    """TODO Docstring

    Args:
        TODO

    Returns:
        TODO
    """
    jy_obj = cu.config_yo_jenkins(profile)
    if cu.is_full_url(job):
        data = jy_obj.Job.rename(new_name=new_name, job_url=job)
    else:
        data = jy_obj.Job.rename(new_name=new_name, job_name=job)

    if not data:
        click.echo(click.style('failed', fg='bright_red', bold=True))
        sys.exit(1)
    click.echo(click.style('success', fg='bright_green', bold=True))


def delete(profile: str, job: str) -> None:
    """TODO Docstring

    Args:
        TODO

    Returns:
        TODO
    """
    jy_obj = cu.config_yo_jenkins(profile)
    if cu.is_full_url(job):
        data = jy_obj.Job.delete(job_url=job)
    else:
        data = jy_obj.Job.delete(job_name=job)

    if not data:
        click.echo(click.style('failed', fg='bright_red', bold=True))
        sys.exit(1)
    click.echo(click.style('success', fg='bright_green', bold=True))


def wipe(profile: str, job: str) -> None:
    """TODO Docstring

    Args:
        TODO

    Returns:
        TODO
    """
    jy_obj = cu.config_yo_jenkins(profile)
    if cu.is_full_url(job):
        data = jy_obj.Job.wipe_workspace(job_url=job)
    else:
        data = jy_obj.Job.wipe_workspace(job_name=job)

    if not data:
        click.echo(click.style('failed', fg='bright_red', bold=True))
        sys.exit(1)
    click.echo(click.style('success', fg='bright_green', bold=True))


def monitor(profile: str, job: str, sound: bool) -> None:
    """TODO Docstring

    Args:
        TODO

    Returns:
        TODO
    """
    jy_obj = cu.config_yo_jenkins(profile)
    if cu.is_full_url(job):
        data = jy_obj.Job.monitor(job_url=job, sound=sound)
    else:
        data = jy_obj.Job.monitor(job_name=job, sound=sound)

    if not data:
        click.echo(click.style('failed', fg='bright_red', bold=True))
        sys.exit(1)


def create(profile: str, name: str, folder: str, config: str) -> None:
    """TODO Docstring

    Args:
        TODO

    Returns:
        TODO
    """
    jy_obj = cu.config_yo_jenkins(profile)
    if cu.is_full_url(folder):
        data = jy_obj.Job.create(name=name, folder_url=folder, config=config)
    else:
        data = jy_obj.Job.create(name=name, folder_name=folder, config=config)

    if not data:
        click.echo(click.style('failed', fg='bright_red', bold=True))
        sys.exit(1)
    click.echo(click.style('success', fg='bright_green', bold=True))
