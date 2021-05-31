#!/usr/bin/env python3

import logging
import sys

import click
from YoJenkins.Status import Status

from . import cli_utility as cu


# Getting the logger reference
logger = logging.getLogger()

def info(opt_pretty:bool, opt_yaml:bool, opt_xml:bool, profile:str, job:str, build_number:int, build_url:str, latest:bool) -> None:
    """TODO Docstring

    Args:
        TODO

    Returns:
        TODO
    """
    if job and not build_number and not latest:
        click.echo(click.style(f'INPUT ERROR: For job, either specify --number or --latest. See --help', fg='bright_red', bold=True))
        sys.exit(1)

    JY = cu.config_YoJenkins(profile)

    # Verify URLs
    if build_url:
        if not cu.is_full_url(build_url):
            click.echo(click.style(f'build url not formatted correctly', fg='bright_red', bold=True))
            sys.exit(1)
        valid_url_format = True
    else:
        valid_url_format = cu.is_full_url(job)

    # Request the data
    if valid_url_format:
        data = JY.Build.info(build_url=build_url, job_url=job, build_number=build_number, latest=latest)
    else:
        data = JY.Build.info(build_url=build_url, job_name=job, build_number=build_number, latest=latest)

    if not data:
        click.echo(click.style(f'No build information', fg='bright_red', bold=True))
        sys.exit(1)
    cu.standard_out(data, opt_pretty, opt_yaml, opt_xml)


def status(profile:str, job:str, build_number:int, build_url:str, latest:bool) -> None:
    """TODO Docstring

    Args:
        TODO

    Returns:
        TODO
    """
    if job and not build_number and not latest:
        click.echo(click.style(f'INPUT ERROR: For job, either specify --number or --latest. See --help', fg='bright_red', bold=True))
        sys.exit(1)

    JY = cu.config_YoJenkins(profile)

    # Verify URLs
    if build_url:
        if not cu.is_full_url(build_url):
            click.echo(click.style(f'build url not formatted correctly', fg='bright_red', bold=True))
            sys.exit(1)
        valid_url_format = True
    else:
        valid_url_format = cu.is_full_url(job)

    # Request the data
    if valid_url_format:
        data = JY.Build.status_text(build_url=build_url, job_url=job, build_number=build_number, latest=latest)
    else:
        data = JY.Build.status_text(build_url=build_url, job_name=job, build_number=build_number, latest=latest)

    if not data:
        click.echo(click.style(f'No status found', fg='bright_red', bold=True))
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


def abort(profile:str, job:str, build_number:int, build_url:str, latest:bool) -> None:
    """TODO Docstring

    Args:
        TODO

    Returns:
        TODO
    """
    if job and not build_number and not latest:
        click.echo(click.style(f'INPUT ERROR: For job, either specify --number or --latest. See --help', fg='bright_red', bold=True))
        sys.exit(1)

    JY = cu.config_YoJenkins(profile)

    # Verify URLs
    if build_url:
        if not cu.is_full_url(build_url):
            click.echo(click.style(f'build url not formatted correctly', fg='bright_red', bold=True))
            sys.exit(1)
        valid_url_format = True
    else:
        valid_url_format = cu.is_full_url(job)

    # Request the data
    if valid_url_format:
        data = JY.Build.abort(build_url=build_url, job_url=job, build_number=build_number, latest=latest)
    else:
        data = JY.Build.abort(build_url=build_url, job_name=job, build_number=build_number, latest=latest)

    if not data:
        click.echo(click.style(f'Failed to abort build', fg='bright_red', bold=True))
        sys.exit(1)

    click.echo(click.style(f'{data}', fg='bright_green', bold=True))



def delete(profile:str, job:str, build_number:int, build_url:str, latest:bool) -> None:
    """TODO Docstring

    Args:
        TODO

    Returns:
        TODO
    """
    if job and not build_number and not latest:
        click.echo(click.style(f'INPUT ERROR: For job, either specify --number or --latest. See --help', fg='bright_red', bold=True))
        sys.exit(1)

    JY = cu.config_YoJenkins(profile)

    # Verify URLs
    if build_url:
        if not cu.is_full_url(build_url):
            click.echo(click.style(f'build url not formatted correctly', fg='bright_red', bold=True))
            sys.exit(1)
        valid_url_format = True
    else:
        valid_url_format = cu.is_full_url(job)

    # Request the data
    if valid_url_format:
        data = JY.Build.delete(build_url=build_url, job_url=job, build_number=build_number, latest=latest)
    else:
        data = JY.Build.delete(build_url=build_url, job_name=job, build_number=build_number, latest=latest)

    if not data:
        click.echo(click.style(f'Failed to delete build', fg='bright_red', bold=True))
        sys.exit(1)

    click.echo(click.style(f'{data}', fg='bright_green', bold=True))



def stages(opt_pretty:bool, opt_yaml:bool, opt_xml:bool, profile:str, opt_list:bool, job:str, build_number:int, build_url:str, latest:bool) -> None:
    """TODO Docstring

    Args:
        TODO

    Returns:
        TODO
    """
    if job and not build_number and not latest:
        click.echo(click.style(f'INPUT ERROR: For job, either specify --number or --latest. See --help', fg='bright_red', bold=True))
        sys.exit(1)

    JY = cu.config_YoJenkins(profile)

    # Verify URLs
    if build_url:
        if not cu.is_full_url(build_url):
            click.echo(click.style(f'build url not formatted correctly', fg='bright_red', bold=True))
            sys.exit(1)
        valid_url_format = True
    else:
        valid_url_format = cu.is_full_url(job)

    # Request the data
    if valid_url_format:
        data, data_list = JY.Build.stage_list(build_url=build_url, job_url=job, build_number=build_number, latest=latest)
    else:
        data, data_list = JY.Build.stage_list(build_url=build_url, job_name=job, build_number=build_number, latest=latest)

    if not data:
        click.echo(click.style(f'Failed to get build stages', fg='bright_red', bold=True))
        sys.exit(1)

    output = data_list if opt_list else data
    cu.standard_out(output, opt_pretty, opt_yaml, opt_xml)



def logs(profile:str, job:str, build_number:int, build_url:str, latest:bool, download_dir:bool, follow:bool) -> None:
    """TODO Docstring

    Args:
        TODO

    Returns:
        TODO
    """
    if job and not build_number and not latest:
        click.echo(click.style(f'INPUT ERROR: For job, either specify --number or --latest. See --help', fg='bright_red', bold=True))
        sys.exit(1)

    JY = cu.config_YoJenkins(profile)

    # Verify URLs
    if build_url:
        if not cu.is_full_url(build_url):
            click.echo(click.style(f'build url not formatted correctly', fg='bright_red', bold=True))
            sys.exit(1)
        valid_url_format = True
    else:
        valid_url_format = cu.is_full_url(job)

    # Request the data
    if valid_url_format:
        data = JY.Build.logs(build_url=build_url, job_url=job, build_number=build_number, latest=latest, download_dir=download_dir, follow=follow)
    else:
        data = JY.Build.logs(build_url=build_url, job_name=job, build_number=build_number, latest=latest, download_dir=download_dir, follow=follow)

    if not data:
        click.echo(click.style(f'failed', fg='bright_red', bold=True))
        sys.exit(1)



def browser(profile:str, job:str, build_number:int, build_url:str, latest:bool) -> None:
    """TODO Docstring

    Args:
        TODO

    Returns:
        TODO
    """
    if job and not build_number and not latest:
        click.echo(click.style(f'INPUT ERROR: For job, either specify --number or --latest. See --help', fg='bright_red', bold=True))
        sys.exit(1)

    JY = cu.config_YoJenkins(profile)

    # Verify URLs
    if build_url:
        if not cu.is_full_url(build_url):
            click.echo(click.style(f'build url not formatted correctly', fg='bright_red', bold=True))
            sys.exit(1)
        valid_url_format = True
    else:
        valid_url_format = cu.is_full_url(job)

    # Request the data
    if valid_url_format:
        data = JY.Build.browser_open(build_url=build_url, job_url=job, build_number=build_number, latest=latest)
    else:
        data = JY.Build.browser_open(build_url=build_url, job_name=job, build_number=build_number, latest=latest)

    if not data:
        click.echo(click.style(f'failed', fg='bright_red', bold=True))
        sys.exit(1)



def monitor(profile:str, job:str, build_number:int, build_url:str, latest:bool, sound:bool) -> None:
    """TODO Docstring

    Args:
        TODO

    Returns:
        TODO
    """
    if job and not build_number and not latest:
        click.echo(click.style(f'INPUT ERROR: For job, either specify --number or --latest. See --help', fg='bright_red', bold=True))
        sys.exit(1)

    JY = cu.config_YoJenkins(profile)

    # Verify URLs
    if build_url:
        if not cu.is_full_url(build_url):
            click.echo(click.style(f'build url not formatted correctly', fg='bright_red', bold=True))
            sys.exit(1)
        valid_url_format = True
    else:
        valid_url_format = cu.is_full_url(job)

    # Request the data
    if valid_url_format:
        data = JY.Build.monitor(
            build_url=build_url,
            job_url=job,
            build_number=build_number,
            latest=latest,
            sound=sound)
    else:
        data = JY.Build.monitor(
            build_url=build_url,
            job_name=job,
            build_number=build_number,
            latest=latest,
            sound=sound)

    if not data:
        click.echo(click.style(f'failed', fg='bright_red', bold=True))
        sys.exit(1)
