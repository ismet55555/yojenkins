"""Job Menu CLI Entrypoints"""

import json
import logging
import sys

import click
import xmltodict

from yojenkins.cli import cli_utility as cu
from yojenkins.cli.cli_utility import log_to_history
from yojenkins.utility.utility import print2

# Getting the logger reference
logger = logging.getLogger()


@log_to_history
def info(opt_pretty: bool, opt_yaml: bool, opt_xml: bool, opt_toml: bool, profile: str, job: str) -> None:
    """TODO Docstring

    Args:
        TODO

    Returns:
        None
    """
    yj_obj = cu.config_yo_jenkins(profile)
    if cu.is_full_url(job):
        data = yj_obj.job.info(job_url=job)
    else:
        data = yj_obj.job.info(job_name=job)
    cu.standard_out(data, opt_pretty, opt_yaml, opt_xml, opt_toml)


@log_to_history
def search(opt_pretty: bool, opt_yaml: bool, opt_xml: bool, opt_toml: bool, profile: str, search_pattern: str,
           search_folder: str, depth: int, fullname: bool, opt_list: bool) -> None:
    """TODO Docstring

    Args:
        TODO

    Returns:
        None
    """
    yj_obj = cu.config_yo_jenkins(profile)
    if cu.is_full_url(search_folder):
        data, data_list = yj_obj.job.search(search_pattern=search_pattern,
                                            folder_url=search_folder,
                                            folder_depth=depth,
                                            fullname=fullname)
    else:
        data, data_list = yj_obj.job.search(search_pattern=search_pattern,
                                            folder_name=search_folder,
                                            folder_depth=depth,
                                            fullname=fullname)
    if not data:
        print2("No folders found", color="yellow")
        sys.exit(1)
    data = data_list if opt_list else data
    cu.standard_out(data, opt_pretty, opt_yaml, opt_xml, opt_toml)


@log_to_history
def build_list(opt_pretty: bool, opt_yaml: bool, opt_xml: bool, opt_toml: bool, profile: str, job: str,
               opt_list: bool) -> None:
    """TODO Docstring

    Args:
        TODO

    Returns:
        None
    """
    yj_obj = cu.config_yo_jenkins(profile)
    if cu.is_full_url(job):
        data, data_list = yj_obj.job.build_list(job_url=job)
    else:
        data, data_list = yj_obj.job.build_list(job_name=job)
    data = data_list if opt_list else data
    cu.standard_out(data, opt_pretty, opt_yaml, opt_xml, opt_toml)


@log_to_history
def build_next(profile: str, job: str) -> None:
    """TODO Docstring

    Args:
        TODO

    Returns:
        None
    """
    yj_obj = cu.config_yo_jenkins(profile)
    if cu.is_full_url(job):
        data = yj_obj.job.build_next_number(job_url=job)
    else:
        data = yj_obj.job.build_next_number(job_name=job)
    click.secho(f'{data}', fg='bright_green', bold=True)


@log_to_history
def build_last(profile: str, job: str) -> None:
    """TODO Docstring

    Args:
        TODO

    Returns:
        None
    """
    yj_obj = cu.config_yo_jenkins(profile)
    if cu.is_full_url(job):
        data = yj_obj.job.build_last_number(job_url=job)
    else:
        data = yj_obj.job.build_last_number(job_name=job)
    click.secho(f'{data}', fg='bright_green', bold=True)


@log_to_history
def build_set(profile: str, job: str, build_number: int) -> None:
    """TODO Docstring

    Args:
        TODO

    Returns:
        None
    """
    yj_obj = cu.config_yo_jenkins(profile)
    if cu.is_full_url(job):
        data = yj_obj.job.build_set_next_number(build_number=build_number, job_url=job)
    else:
        data = yj_obj.job.build_set_next_number(build_number=build_number, job_name=job)
    click.secho(f'{build_number}', fg='bright_green', bold=True)


@log_to_history
def build_exist(profile: str, job: str, build_number: int) -> None:
    """TODO Docstring

    Args:
        TODO

    Returns:
        None
    """
    yj_obj = cu.config_yo_jenkins(profile)
    if cu.is_full_url(job):
        data = yj_obj.job.build_number_exist(build_number=build_number, job_url=job)
    else:
        data = yj_obj.job.build_number_exist(build_number=build_number, job_name=job)
    click.secho('true', fg='bright_green', bold=True)


@log_to_history
def build(profile: str, job: str, parameters: tuple) -> None:
    """TODO Docstring

    Args:
        TODO

    Returns:
        None
    """
    yj_obj = cu.config_yo_jenkins(profile)

    # Convert a tuple of tuples to dict
    parameters = dict(list(parameters))

    if cu.is_full_url(job):
        data = yj_obj.job.build_trigger(job_url=job, paramters=parameters)
    else:
        data = yj_obj.job.build_trigger(job_name=job, paramters=parameters)
    click.secho(f'success. queue number: {data}', fg='bright_green', bold=True)


@log_to_history
def queue_check(opt_pretty: bool, opt_yaml: bool, opt_xml: bool, opt_toml: bool, profile: str, job: str,
                opt_id: bool) -> None:
    """TODO Docstring

    Args:
        TODO

    Returns:
        None
    """
    yj_obj = cu.config_yo_jenkins(profile)
    if cu.is_full_url(job):
        data, queue_id = yj_obj.job.in_queue_check(job_url=job)
    else:
        data, queue_id = yj_obj.job.in_queue_check(job_name=job)
    if opt_id:
        click.secho(f'{queue_id}', fg='bright_green', bold=True)
    else:
        cu.standard_out(data, opt_pretty, opt_yaml, opt_xml, opt_toml)


@log_to_history
def browser(profile: str, job: str) -> None:
    """TODO Docstring

    Args:
        TODO

    Returns:
        None
    """
    yj_obj = cu.config_yo_jenkins(profile)
    if cu.is_full_url(job):
        yj_obj.job.browser_open(job_url=job)
    else:
        yj_obj.job.browser_open(job_name=job)


@log_to_history
def config(opt_pretty: bool, opt_yaml: bool, opt_xml: bool, opt_toml: bool, opt_json: bool, profile: str, job: str,
           filepath: str) -> None:
    """TODO Docstring

    Args:
        TODO

    Returns:
        None
    """
    yj_obj = cu.config_yo_jenkins(profile)
    if cu.is_full_url(job):
        data = yj_obj.job.config(filepath=filepath,
                                 job_url=job,
                                 opt_json=opt_json,
                                 opt_yaml=opt_yaml,
                                 opt_toml=opt_toml)
    else:
        data = yj_obj.job.config(filepath=filepath,
                                 job_name=job,
                                 opt_json=opt_json,
                                 opt_yaml=opt_yaml,
                                 opt_toml=opt_toml)

    # Converting XML to dict
    # data = json.loads(json.dumps(xmltodict.parse(data)))

    opt_xml = not any([opt_json, opt_yaml, opt_toml])
    data = data if opt_xml else json.loads(json.dumps(xmltodict.parse(data)))
    cu.standard_out(data, opt_pretty, opt_yaml, opt_xml, opt_toml)


@log_to_history
def disable(profile: str, job: str) -> None:
    """TODO Docstring

    Args:
        TODO

    Returns:
        None
    """
    yj_obj = cu.config_yo_jenkins(profile)
    if cu.is_full_url(job):
        data = yj_obj.job.disable(job_url=job)
    else:
        data = yj_obj.job.disable(job_name=job)
    click.secho('success', fg='bright_green', bold=True)


@log_to_history
def enable(profile: str, job: str) -> None:
    """TODO Docstring

    Args:
        TODO

    Returns:
        None
    """
    yj_obj = cu.config_yo_jenkins(profile)
    if cu.is_full_url(job):
        data = yj_obj.job.enable(job_url=job)
    else:
        data = yj_obj.job.enable(job_name=job)
    click.secho('success', fg='bright_green', bold=True)


@log_to_history
def rename(profile: str, job: str, new_name: str) -> None:
    """TODO Docstring

    Args:
        TODO

    Returns:
        None
    """
    yj_obj = cu.config_yo_jenkins(profile)
    if cu.is_full_url(job):
        data = yj_obj.job.rename(new_name=new_name, job_url=job)
    else:
        data = yj_obj.job.rename(new_name=new_name, job_name=job)
    click.secho('success', fg='bright_green', bold=True)


@log_to_history
def delete(profile: str, job: str) -> None:
    """TODO Docstring

    Args:
        TODO

    Returns:
        None
    """
    yj_obj = cu.config_yo_jenkins(profile)
    if cu.is_full_url(job):
        data = yj_obj.job.delete(job_url=job)
    else:
        data = yj_obj.job.delete(job_name=job)
    click.secho('success', fg='bright_green', bold=True)


@log_to_history
def wipe(profile: str, job: str) -> None:
    """TODO Docstring

    Args:
        TODO

    Returns:
        None
    """
    yj_obj = cu.config_yo_jenkins(profile)
    if cu.is_full_url(job):
        data = yj_obj.job.wipe_workspace(job_url=job)
    else:
        data = yj_obj.job.wipe_workspace(job_name=job)
    click.secho('success', fg='bright_green', bold=True)


@log_to_history
def monitor(profile: str, job: str, sound: bool) -> None:
    """TODO Docstring

    Args:
        TODO

    Returns:
        None
    """
    yj_obj = cu.config_yo_jenkins(profile)
    if cu.is_full_url(job):
        yj_obj.job.monitor(job_url=job, sound=sound)
    else:
        yj_obj.job.monitor(job_name=job, sound=sound)


@log_to_history
def create(profile: str, name: str, folder: str, config_file: str, config_is_json: bool) -> None:
    """TODO Docstring

    Args:
        TODO

    Returns:
        None
    """
    yj_obj = cu.config_yo_jenkins(profile)
    if cu.is_full_url(folder):
        data = yj_obj.job.create(name=name, folder_url=folder, config_file=config_file, config_is_json=config_is_json)
    else:
        data = yj_obj.job.create(name=name, folder_name=folder, config_file=config_file, config_is_json=config_is_json)
    click.secho('success', fg='bright_green', bold=True)


@log_to_history
def parameters(opt_pretty: bool, opt_yaml: bool, opt_xml: bool, opt_toml: bool, profile: str, job: str,
               opt_list: bool) -> None:
    """TODO Docstring

    Args:
        TODO

    Returns:
        None
    """
    yj_obj = cu.config_yo_jenkins(profile)
    if cu.is_full_url(job):
        data, data_list = yj_obj.job.parameters(job_url=job)
    else:
        data, data_list = yj_obj.job.parameters(job_name=job)
    data = data_list if opt_list else data
    cu.standard_out(data, opt_pretty, opt_yaml, opt_xml, opt_toml)
