#!/usr/bin/env python3

import logging
import sys

import click

from yo_jenkins.cli import cli_utility as cu
from yo_jenkins.cli.cli_utility import log_to_history
from yo_jenkins.YoJenkins.Status import Status

# Getting the logger reference
logger = logging.getLogger()


@log_to_history
def info(opt_pretty: bool, opt_yaml: bool, opt_xml: bool, opt_toml: bool, profile: str, stage_name: str, job: str,
         build_number: int, build_url: str, latest: bool) -> None:
    """TODO Docstring

    Details: TODO

    Args:
        TODO

    Returns:
        TODO
    """
    if job and not build_number and not latest:
        click.echo(
            click.style('INPUT ERROR: For job, either specify --number or --latest. See --help',
                        fg='bright_red',
                        bold=True))
        sys.exit(1)

    jy_obj = cu.config_yo_jenkins(profile)

    # Differentiate if name or url
    if build_url:
        logger.debug(f'Build URL passed: {build_url}')
        valid_url_format = True
    else:
        valid_url_format = cu.is_full_url(job) if not build_url else True

    # Request the data
    if valid_url_format:
        data = jy_obj.Stage.info(stage_name=stage_name,
                                 build_url=build_url,
                                 job_url=job,
                                 build_number=build_number,
                                 latest=latest)
    else:
        data = jy_obj.Stage.info(stage_name=stage_name,
                                 build_url=build_url,
                                 job_name=job,
                                 build_number=build_number,
                                 latest=latest)

    if not data:
        click.echo(click.style('no stage information', fg='bright_red', bold=True))
        sys.exit(1)
    cu.standard_out(data, opt_pretty, opt_yaml, opt_xml, opt_toml)


@log_to_history
def status(profile: str, stage_name: str, job: str, build_number: int, build_url: str, latest: bool) -> None:
    """TODO Docstring

    Details: TODO

    Args:
        TODO

    Returns:
        TODO
    """
    if job and not build_number and not latest:
        click.echo(
            click.style('INPUT ERROR: For job, either specify --number or --latest. See --help',
                        fg='bright_red',
                        bold=True))
        sys.exit(1)

    jy_obj = cu.config_yo_jenkins(profile)

    # Differentiate if name or url
    if build_url:
        logger.debug(f'Build URL passed: {build_url}')
        valid_url_format = True
    else:
        valid_url_format = cu.is_full_url(job) if not build_url else True

    # Request the data
    if valid_url_format:
        data = jy_obj.Stage.status_text(stage_name=stage_name,
                                        build_url=build_url,
                                        job_url=job,
                                        build_number=build_number,
                                        latest=latest)
    else:
        data = jy_obj.Stage.status_text(stage_name=stage_name,
                                        build_url=build_url,
                                        job_name=job,
                                        build_number=build_number,
                                        latest=latest)

    if not data:
        click.echo(click.style('no status found', fg='bright_red', bold=True))
        sys.exit(1)

    # Color for output
    if data.upper() in Status.unknown.value:
        output_fg = 'black'
    elif data.upper() in Status.queued.value:
        output_fg = 'yellow'
    elif data.upper() in Status.running.value:
        output_fg = 'blue'
    elif data.upper() in Status.success.value:
        output_fg = 'bright_green'
    elif data.upper() in Status.failure.value:
        output_fg = 'bright_red'
    else:
        output_fg = ''
    click.echo(click.style(f'{data}', fg=output_fg, bold=True))


@log_to_history
def steps(opt_pretty: bool, opt_yaml: bool, opt_xml: bool, opt_toml: bool, profile: str, opt_list: bool,
          stage_name: str, job: str, build_number: int, build_url: str, latest: bool) -> None:
    """TODO Docstring

    Details: TODO

    Args:
        TODO

    Returns:
        TODO
    """
    if job and not build_number and not latest:
        click.echo(
            click.style('INPUT ERROR: For job, either specify --number or --latest. See --help',
                        fg='bright_red',
                        bold=True))
        sys.exit(1)

    jy_obj = cu.config_yo_jenkins(profile)

    # Differentiate if name or url
    if build_url:
        logger.debug(f'Build URL passed: {build_url}')
        valid_url_format = True
    else:
        valid_url_format = cu.is_full_url(job) if not build_url else True

    # Request the data
    if valid_url_format:
        data, data_list = jy_obj.Stage.step_list(stage_name=stage_name,
                                                 build_url=build_url,
                                                 job_url=job,
                                                 build_number=build_number,
                                                 latest=latest)
    else:
        data, data_list = jy_obj.Stage.step_list(stage_name=stage_name,
                                                 build_url=build_url,
                                                 job_name=job,
                                                 build_number=build_number,
                                                 latest=latest)

    if not data:
        click.echo(click.style('failed', fg='bright_red', bold=True))
        sys.exit(1)

    data = data_list if opt_list else data
    cu.standard_out(data, opt_pretty, opt_yaml, opt_xml, opt_toml)


@log_to_history
def logs(profile: str, stage_name: str, job: str, build_number: int, build_url: str, latest: bool,
         download_dir: bool) -> None:
    """TODO Docstring

    Details: TODO

    Args:
        TODO

    Returns:
        TODO
    """
    if job and not build_number and not latest:
        click.echo(
            click.style('INPUT ERROR: For job, either specify --number or --latest. See --help',
                        fg='bright_red',
                        bold=True))
        sys.exit(1)

    jy_obj = cu.config_yo_jenkins(profile)

    # Differentiate if name or url
    if build_url:
        logger.debug(f'Build URL passed: {build_url}')
        valid_url_format = True
    else:
        valid_url_format = cu.is_full_url(job) if not build_url else True

    # Request the data
    if valid_url_format:
        data = jy_obj.Stage.logs(stage_name=stage_name,
                                 build_url=build_url,
                                 job_url=job,
                                 build_number=build_number,
                                 latest=latest,
                                 download_dir=download_dir)
    else:
        data = jy_obj.Stage.logs(stage_name=stage_name,
                                 build_url=build_url,
                                 job_name=job,
                                 build_number=build_number,
                                 latest=latest,
                                 download_dir=download_dir)

    if not data:
        click.echo(click.style('failed', fg='bright_red', bold=True))
        sys.exit(1)
