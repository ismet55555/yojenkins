"""Job Menu CLI Entrypoints"""

import json
import logging
import sys

import click
import xmltodict

from yojenkins.cli import cli_utility as cu
from yojenkins.cli.cli_utility import log_to_history
from yojenkins.utility.utility import print2, wait_for_build_and_follow_logs

# Getting the logger reference
logger = logging.getLogger()


@log_to_history
def info(profile: str, token: str, job: str, **kwargs) -> None:
    """TODO Docstring

    Args:
        TODO
    """
    yj_obj = cu.config_yo_jenkins(profile, token)
    if cu.is_full_url(job):
        data = yj_obj.job.info(job_url=job)
    else:
        data = yj_obj.job.info(job_name=job)
    cu.standard_out(data, **kwargs)


@log_to_history
def search(profile: str, token: str, search_pattern: str, search_folder: str, depth: int, fullname: bool,
           opt_list: bool, **kwargs) -> None:
    """TODO Docstring

    Args:
        TODO
    """
    yj_obj = cu.config_yo_jenkins(profile, token)
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
    cu.standard_out(data, **kwargs)


@log_to_history
def build_list(profile: str, token: str, opt_list: bool, job: str, **kwargs) -> None:
    """TODO Docstring

    Args:
        TODO
    """
    yj_obj = cu.config_yo_jenkins(profile, token)
    if cu.is_full_url(job):
        data, data_list = yj_obj.job.build_list(job_url=job)
    else:
        data, data_list = yj_obj.job.build_list(job_name=job)
    data = data_list if opt_list else data
    cu.standard_out(data, **kwargs)


@log_to_history
def build_next(profile: str, token: str, job: str) -> None:
    """Get last build number for a job

    Args:
        TODO
    """
    yj_obj = cu.config_yo_jenkins(profile, token)
    if cu.is_full_url(job):
        data = yj_obj.job.build_next_number(job_url=job)
    else:
        data = yj_obj.job.build_next_number(job_name=job)
    click.secho(f'{data}', fg='bright_green', bold=True)


@log_to_history
def build_last(profile: str, token: str, job: str) -> None:
    """Get previous build number for a job

    Args:
        TODO
    """
    yj_obj = cu.config_yo_jenkins(profile, token)
    if cu.is_full_url(job):
        data = yj_obj.job.build_last_number(job_url=job)
    else:
        data = yj_obj.job.build_last_number(job_name=job)
    click.secho(f'{data}', fg='bright_green', bold=True)


@log_to_history
def build_set(profile: str, token: str, job: str, build_number: int) -> None:
    """Set the current build number for a job

    Args:
        TODO
    """
    yj_obj = cu.config_yo_jenkins(profile, token)
    if cu.is_full_url(job):
        yj_obj.job.build_set_next_number(build_number=build_number, job_url=job)
    else:
        yj_obj.job.build_set_next_number(build_number=build_number, job_name=job)
    click.secho(f'{build_number}', fg='bright_green', bold=True)


@log_to_history
def build_exist(profile: str, token: str, job: str, build_number: int) -> None:
    """Check if a build number for this job exists

    Args:
        TODO
    """
    yj_obj = cu.config_yo_jenkins(profile, token)
    if cu.is_full_url(job):
        data = yj_obj.job.build_number_exist(build_number, {}, job_url=job)
    else:
        data = yj_obj.job.build_number_exist(build_number, {}, job_name=job)
    if data:
        click.secho('true', fg='bright_green', bold=True)
    else:
        click.secho('false', fg='bright_red', bold=True)


@log_to_history
def build(profile: str, token: str, job: str, parameter: tuple, follow_logs: bool) -> None:
    """Build a job

    Args:
        profile:     The profile/account to use
        token:       API Token for Jenkins server
        job:         The job name under which the build is located
        parameter:   Specify key-value parameter. Can use multiple times. Use once per parameter
        follow_logs: Waits for the job build, then follows resulting logs
    """
    yj_obj = cu.config_yo_jenkins(profile, token)

    # Convert a tuple of tuples to dict
    parameters = dict(list(parameter))

    if cu.is_full_url(job):
        data = yj_obj.job.build_trigger(job_url=job, paramters=parameters)
    else:
        data = yj_obj.job.build_trigger(job_name=job, paramters=parameters)
    if not follow_logs:
        click.secho(f'success. queue number: {data}', fg='bright_green', bold=True)
        return
    wait_for_build_and_follow_logs(yj_obj, data)


@log_to_history
def queue_check(profile: str, token: str, job: str, opt_id: bool, **kwargs) -> None:
    """TODO Docstring

    Args:
        TODO
    """
    yj_obj = cu.config_yo_jenkins(profile, token)
    if cu.is_full_url(job):
        data, queue_id = yj_obj.job.in_queue_check(job_url=job)
    else:
        data, queue_id = yj_obj.job.in_queue_check(job_name=job)
    if opt_id:
        click.secho(f'{queue_id}', fg='bright_green', bold=True)
    else:
        cu.standard_out(data, **kwargs)


@log_to_history
def browser(profile: str, token: str, job: str) -> None:
    """TODO Docstring

    Args:
        TODO
    """
    yj_obj = cu.config_yo_jenkins(profile, token)
    if cu.is_full_url(job):
        yj_obj.job.browser_open(job_url=job)
    else:
        yj_obj.job.browser_open(job_name=job)


@log_to_history
def config(profile: str, token: str, opt_pretty: bool, opt_yaml: bool, opt_xml: bool, opt_toml: bool, opt_json: bool,
           job: str, filepath: str) -> None:
    """TODO Docstring

    Args:
        TODO
    """
    yj_obj = cu.config_yo_jenkins(profile, token)
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

    # data = json.loads(json.dumps(xmltodict.parse(data)))  # Converting XML to dict
    opt_xml = not any([opt_json, opt_yaml, opt_toml])
    data = data if opt_xml else json.loads(json.dumps(xmltodict.parse(data)))
    cu.standard_out(data, opt_pretty, opt_yaml, opt_xml, opt_toml)


@log_to_history
def disable(profile: str, token: str, job: str) -> None:
    """TODO Docstring

    Args:
        TODO
    """
    yj_obj = cu.config_yo_jenkins(profile, token)
    if cu.is_full_url(job):
        yj_obj.job.disable(job_url=job)
    else:
        yj_obj.job.disable(job_name=job)
    click.secho('success', fg='bright_green', bold=True)


@log_to_history
def enable(profile: str, token: str, job: str) -> None:
    """TODO Docstring

    Args:
        TODO
    """
    yj_obj = cu.config_yo_jenkins(profile, token)
    if cu.is_full_url(job):
        yj_obj.job.enable(job_url=job)
    else:
        yj_obj.job.enable(job_name=job)
    click.secho('success', fg='bright_green', bold=True)


@log_to_history
def rename(profile: str, token: str, job: str, name: str) -> None:
    """TODO Docstring

    Args:
        TODO
    """
    yj_obj = cu.config_yo_jenkins(profile, token)
    if cu.is_full_url(job):
        yj_obj.job.rename(new_name=name, job_url=job)
    else:
        yj_obj.job.rename(new_name=name, job_name=job)
    click.secho('success', fg='bright_green', bold=True)


@log_to_history
def delete(profile: str, token: str, job: str) -> None:
    """TODO Docstring

    Args:
        TODO
    """
    yj_obj = cu.config_yo_jenkins(profile, token)
    if cu.is_full_url(job):
        yj_obj.job.delete(job_url=job)
    else:
        yj_obj.job.delete(job_name=job)
    click.secho('success', fg='bright_green', bold=True)


@log_to_history
def wipe(profile: str, token: str, job: str) -> None:
    """TODO Docstring

    Args:
        TODO
    """
    yj_obj = cu.config_yo_jenkins(profile, token)
    if cu.is_full_url(job):
        yj_obj.job.wipe_workspace(job_url=job)
    else:
        yj_obj.job.wipe_workspace(job_name=job)
    click.secho('success', fg='bright_green', bold=True)


@log_to_history
def monitor(profile: str, token: str, job: str, sound: bool) -> None:
    """TODO Docstring

    Args:
        TODO
    """
    yj_obj = cu.config_yo_jenkins(profile, token)
    if cu.is_full_url(job):
        yj_obj.job.monitor(job_url=job, sound=sound)
    else:
        yj_obj.job.monitor(job_name=job, sound=sound)


@log_to_history
def create(profile: str, token: str, name: str, folder: str, config_file: str, config_is_json: bool) -> None:
    """TODO Docstring

    Args:
        TODO
    """
    yj_obj = cu.config_yo_jenkins(profile, token)
    if cu.is_full_url(folder):
        yj_obj.job.create(name=name, folder_url=folder, config_file=config_file, config_is_json=config_is_json)
    else:
        yj_obj.job.create(name=name, folder_name=folder, config_file=config_file, config_is_json=config_is_json)
    click.secho('success', fg='bright_green', bold=True)


@log_to_history
def parameters(profile: str, token: str, job: str, opt_list: bool, **kwargs) -> None:
    """TODO Docstring

    Args:
        TODO
    """
    yj_obj = cu.config_yo_jenkins(profile, token)
    if cu.is_full_url(job):
        data, data_list = yj_obj.job.parameters(job_url=job)
    else:
        data, data_list = yj_obj.job.parameters(job_name=job)
    data = data_list if opt_list else data
    cu.standard_out(data, **kwargs)


@log_to_history
def diff(profile: str, token: str, job_1: str, job_2: str, no_color: bool, diff_only: bool, diff_guide: bool) -> None:
    """Get the diff comparison for two jobs

    Args:
        profile:     The profile/account to use
        token:       API Token for Jenkins server
        job_1:       First job for comparison (name or url)
        job_2:       Second job for comparison (name or url)
        no_color:    Output diff with no color
        diff_only:   Only show the lines that have changed
        diff_guide:  Show diff guide, showing where exactly difference is in line
    """
    yj_obj = cu.config_yo_jenkins(profile, token)
    yj_obj.job.diff(job_1, job_2, no_color, diff_only, diff_guide)
