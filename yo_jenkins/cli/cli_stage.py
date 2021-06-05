#!/usr/bin/env python3

import logging
import sys

import click
from YoJenkins.Status import Status

from . import cli_utility as cu


# Getting the logger reference
logger = logging.getLogger()

def info(opt_pretty:bool, opt_yaml:bool, opt_xml:bool, profile:str, stage_name:str, job:str, build_number:int, build_url:str, latest:bool) -> None:
    """TODO Docstring

    Details: TODO

    Args:
        TODO

    Returns:
        TODO
    """
    if job and not build_number and not latest:
        click.echo(click.style(
            f'INPUT ERROR: For job, either specify --number or --latest. See --help',
            fg='bright_red',
            bold=True
            ))
        sys.exit(1)

    JY = cu.config_YoJenkins(profile)

    # Differentiate if name or url
    if build_url:
        logger.debug(f'Build URL passed: {build_url}')
        valid_url_format = True
    else:
        valid_url_format = cu.is_full_url(job) if not build_url else True

    # Request the data
    if valid_url_format:
        data = JY.Stage.info(stage_name=stage_name, build_url=build_url, job_url=job, build_number=build_number, latest=latest)
    else:
        data = JY.Stage.info(stage_name=stage_name, build_url=build_url, job_name=job, build_number=build_number, latest=latest)

    if not data:
        click.echo(click.style(f'no stage information', fg='bright_red', bold=True))
        sys.exit(1)
    cu.standard_out(data, opt_pretty, opt_yaml, opt_xml)


def status(profile:str, stage_name: str, job:str, build_number:int, build_url:str, latest:bool) -> None:
    """TODO Docstring

    Details: TODO

    Args:
        TODO

    Returns:
        TODO
    """
    if job and not build_number and not latest:
        click.echo(click.style(f'INPUT ERROR: For job, either specify --number or --latest. See --help', fg='bright_red', bold=True))
        sys.exit(1)

    JY = cu.config_YoJenkins(profile)

    # Differentiate if name or url
    if build_url:
        logger.debug(f'Build URL passed: {build_url}')
        valid_url_format = True
    else:
        valid_url_format = cu.is_full_url(job) if not build_url else True

    # Request the data
    if valid_url_format:
        data = JY.Stage.status_text(stage_name=stage_name, build_url=build_url, job_url=job, build_number=build_number, latest=latest)
    else:
        data = JY.Stage.status_text(stage_name=stage_name, build_url=build_url, job_name=job, build_number=build_number, latest=latest)

    if not data:
        click.echo(click.style(f'no status found', fg='bright_red', bold=True))
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


def steps(opt_pretty: bool, opt_yaml: bool, opt_xml: bool, profile:str, opt_list: bool, stage_name: str, job: str, build_number: int, build_url: str, latest: bool) -> None:
    """TODO Docstring

    Details: TODO

    Args:
        TODO

    Returns:
        TODO
    """
    if job and not build_number and not latest:
        click.echo(click.style(
            f'INPUT ERROR: For job, either specify --number or --latest. See --help', fg='bright_red', bold=True))
        sys.exit(1)

    JY = cu.config_YoJenkins(profile)

    # Differentiate if name or url
    if build_url:
        logger.debug(f'Build URL passed: {build_url}')
        valid_url_format = True
    else:
        valid_url_format = cu.is_full_url(
            job) if not build_url else True

    # Request the data
    if valid_url_format:
        data, data_list = JY.Stage.step_list(
            stage_name=stage_name, build_url=build_url, job_url=job, build_number=build_number, latest=latest)
    else:
        data, data_list = JY.Stage.step_list(
            stage_name=stage_name, build_url=build_url, job_name=job, build_number=build_number, latest=latest)

    if not data:
        click.echo(click.style(f'failed', fg='bright_red', bold=True))
        sys.exit(1)

    output = data_list if opt_list else data
    cu.standard_out(output, opt_pretty, opt_yaml, opt_xml)



def logs(profile:str, stage_name: str, job: str, build_number: int, build_url: str, latest: bool, download_dir:bool) -> None:
    """TODO Docstring

    Details: TODO

    Args:
        TODO

    Returns:
        TODO
    """
    if job and not build_number and not latest:
        click.echo(click.style(
            f'INPUT ERROR: For job, either specify --number or --latest. See --help', fg='bright_red', bold=True))
        sys.exit(1)

    JY = cu.config_YoJenkins(profile)

    # Differentiate if name or url
    if build_url:
        logger.debug(f'Build URL passed: {build_url}')
        valid_url_format = True
    else:
        valid_url_format = cu.is_full_url(
            job) if not build_url else True

    # Request the data
    if valid_url_format:
        data = JY.Stage.logs(
            stage_name=stage_name, build_url=build_url, job_url=job, build_number=build_number, latest=latest, download_dir=download_dir)
    else:
        data = JY.Stage.logs(
            stage_name=stage_name, build_url=build_url, job_name=job, build_number=build_number, latest=latest, download_dir=download_dir)

    if not data:
        click.echo(click.style(f'failed', fg='bright_red', bold=True))
        sys.exit(1)

