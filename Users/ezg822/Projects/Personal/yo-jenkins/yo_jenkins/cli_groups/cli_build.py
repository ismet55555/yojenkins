#!/usr/bin/env python3

import logging
import sys

import click
from YoJenkins.Status import Status

from . import cli_utility


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

    J = cli_utility.config_auth_server(profile)

    # Differentiate if name or url
    if build_url:
        logger.debug(f'Build URL passed: {build_url}')
        valid_url_format = True
    else:
        valid_url_format = cli_utility.uri_validator(job) if not build_url else True

    # Request the data
    if valid_url_format:
        data = J.build_info(build_url=build_url, job_url=job, build_number=build_number, latest=latest)
    else:
        data = J.build_info(build_url=build_url, job_name=job, build_number=build_number, latest=latest)

    if not data:
        click.echo(click.style(f'No build information', fg='bright_red', bold=True))
        sys.exit(1)
    cli_utility.standard_out(data, opt_pretty, opt_yaml, opt_xml)


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

    J = cli_utility.config_auth_server(profile)

    # Differentiate if name or url
    if build_url:
        logger.debug(f'Build URL passed: {build_url}')
        valid_url_format = True
    else:
        valid_url_format = cli_utility.uri_validator(job) if not build_url else True

    # Request the data
    if valid_url_format:
        data = J.build_status_text(build_url=build_url, job_url=job, build_number=build_number, latest=latest)
    else:
        data = J.build_status_text(build_url=build_url, job_name=job, build_number=build_number, latest=latest)

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

    J = cli_utility.config_auth_server(profile)

    # Differentiate if name or url
    if build_url:
        logger.debug(f'Build URL passed: {build_url}')
        valid_url_format = True
    else:
        valid_url_format = cli_utility.uri_validator(job) if not build_url else True

    # Request the data
    if valid_url_format:
        data = J.build_abort(build_url=build_url, job_url=job, build_number=build_number, latest=latest)
    else:
        data = J.build_abort(build_url=build_url, job_name=job, build_number=build_number, latest=latest)

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

    J = cli_utility.config_auth_server(profile)

    # Differentiate if name or url
    if build_url:
        valid_url_format = True
    else:
        valid_url_format = cli_utility.uri_validator(job) if not build_url else True

    # Request the data
    if valid_url_format:
        data = J.build_delete(build_url=build_url, job_url=job, build_number=build_number, latest=latest)
    else:
        data = J.build_delete(build_url=build_url, job_name=job, build_number=build_number, latest=latest)

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

    J = cli_utility.config_auth_server(profile)

    # Differentiate if name or url
    if build_url:
        valid_url_format = True
    else:
        valid_url_format = cli_utility.uri_validator(job) if not build_url else True

    # Request the data
    if valid_url_format:
        data, data_list = J.build_stage_list(build_url=build_url, job_url=job, build_number=build_number, latest=latest)
    else:
        data, data_list = J.build_stage_list(build_url=build_url, job_name=job, build_number=build_number, latest=latest)

    if not data:
        click.echo(click.style(f'Failed to get build stages', fg='bright_red', bold=True))
        sys.exit(1)

    output = data_list if opt_list else data
    cli_utility.standard_out(output, opt_pretty, opt_yaml, opt_xml)



def log(profile:str, job:str, build_number:int, build_url:str, latest:bool, download:bool) -> None:
    """TODO Docstring

    Args:
        TODO

    Returns:
        TODO
    """
    if job and not build_number and not latest:
        click.echo(click.style(f'INPUT ERROR: For job, either specify --number or --latest. See --help', fg='bright_red', bold=True))
        sys.exit(1)

    J = cli_utility.config_auth_server(profile)

    # Differentiate if name or url
    if build_url:
        valid_url_format = True
    else:
        valid_url_format = cli_utility.uri_validator(job) if not build_url else True

    # Request the data
    if valid_url_format:
        data = J.build_log(build_url=build_url, job_url=job, build_number=build_number, latest=latest, download=download)
    else:
        data = J.build_log(build_url=build_url, job_name=job, build_number=build_number, latest=latest, download=download)

    if not data:
        click.echo(click.style(f'Failed to get logs', fg='bright_red', bold=True))
        sys.exit(1)

    click.echo(click.style(f'end of build logs', fg='bright_green', bold=True))



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

    J = cli_utility.config_auth_server(profile)

    # Differentiate if name or url
    if build_url:
        valid_url_format = True
    else:
        valid_url_format = cli_utility.uri_validator(job) if not build_url else True

    # Request the data
    if valid_url_format:
        data = J.build_browser_open(build_url=build_url, job_url=job, build_number=build_number, latest=latest)
    else:
        data = J.build_browser_open(build_url=build_url, job_name=job, build_number=build_number, latest=latest)

    if not data:
        click.echo(click.style(f'failed', fg='bright_red', bold=True))
        sys.exit(1)



def monitor(profile:str, job:str, build_number:int, build_url:str, latest:bool) -> None:
    """TODO Docstring

    Args:
        TODO

    Returns:
        TODO
    """
    if job and not build_number and not latest:
        click.echo(click.style(f'INPUT ERROR: For job, either specify --number or --latest. See --help', fg='bright_red', bold=True))
        sys.exit(1)

    J = cli_utility.config_auth_server(profile)

    # Differentiate if name or url
    if build_url:
        valid_url_format = True
    else:
        valid_url_format = cli_utility.uri_validator(job) if not build_url else True

    # Request the data
    if valid_url_format:
        data = J.build_monitor(build_url=build_url, job_url=job, build_number=build_number, latest=latest)
    else:
        data = J.build_monitor(build_url=build_url, job_name=job, build_number=build_number, latest=latest)

    if not data:
        click.echo(click.style(f'failed', fg='bright_red', bold=True))
        sys.exit(1)
