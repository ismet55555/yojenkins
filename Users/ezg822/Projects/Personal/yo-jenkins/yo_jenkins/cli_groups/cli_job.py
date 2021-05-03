#!/usr/bin/env python3

import logging
import sys

import click
from YoJenkins import YoJenkins

from . import cli_utility


# Getting the logger reference
logger = logging.getLogger()


def info(opt_pretty:bool, opt_yaml:bool, opt_xml:bool, profile:str, job:str) -> None:
    '''
    TODO: Docstring
    '''
    J = cli_utility.config_auth_server(profile)

    # Differentiate if name or url
    valid_url_format = cli_utility.uri_validator(job)

    # Request the data
    if valid_url_format:
        data = J.job_info(job_url=job)
    else:
        data = J.job_info(job_name=job)

    if not data:
        click.echo(click.style(f'not found', fg='bright_red', bold=True))
        sys.exit(1)
    cli_utility.standard_out(data, opt_pretty, opt_yaml, opt_xml)


def search(opt_pretty:bool, opt_yaml:bool, opt_xml:bool, profile:str, search_pattern:str, start_folder:str, depth:int, opt_list:bool) -> None:
    '''
    TODO: Docstring
    '''
    J = cli_utility.config_auth_server(profile)
    
    # Differentiate if name or url
    valid_url_format = cli_utility.uri_validator(start_folder)

    # Request the data
    if valid_url_format:
        data, data_list = J.job_search(search_pattern=search_pattern, folder_url=start_folder, folder_depth=depth)
    else:
        data, data_list = J.job_search(search_pattern=search_pattern, folder_name=start_folder, folder_depth=depth)

    if not data:
        click.echo(click.style(f'not found', fg='bright_red', bold=True))
        sys.exit(1)
    output = data_list if opt_list else data
    cli_utility.standard_out(output, opt_pretty, opt_yaml, opt_xml)


def build_list(opt_pretty:bool, opt_yaml:bool, opt_xml:bool, profile:str, job:str, opt_list:bool) -> None:
    '''
    TODO: Docstring
    '''
    J = cli_utility.config_auth_server(profile)
    
    # Differentiate if name or url
    valid_url_format = cli_utility.uri_validator(job)

    # Request the data
    if valid_url_format:
        data, data_list = J.job_build_list(job_url=job)
    else:
        data, data_list = J.job_build_list(job_name=job)

    if not data:
        click.echo(click.style(f'not found', fg='bright_red', bold=True))
        sys.exit(1)
    output = data_list if opt_list else data
    cli_utility.standard_out(output, opt_pretty, opt_yaml, opt_xml)


def build_next(profile:str, job:str) -> None:
    '''
    TODO: Docstring
    '''
    J = cli_utility.config_auth_server(profile)
    
    # Differentiate if name or url
    valid_url_format = cli_utility.uri_validator(job)

    # Request the data
    if valid_url_format:
        data = J.job_build_next_number(job_url=job)
    else:
        data = J.job_build_next_number(job_name=job)

    if not data:
        click.echo(click.style(f'not found', fg='bright_red', bold=True))
        sys.exit(1)

    click.echo(click.style(f'{data}', fg='bright_green', bold=True))


def build_last(profile:str, job:str) -> None:
    '''
    TODO: Docstring
    '''
    J = cli_utility.config_auth_server(profile)
    
    # Differentiate if name or url
    valid_url_format = cli_utility.uri_validator(job)

    # Request the data
    if valid_url_format:
        data = J.job_build_last_number(job_url=job)
    else:
        data = J.job_build_last_number(job_name=job)

    if not data:
        click.echo(click.style(f'not found', fg='bright_red', bold=True))
        sys.exit(1)

    click.echo(click.style(f'{data}', fg='bright_green', bold=True))


def build_set(profile:str, job:str, build_number:int) -> None:
    '''
    TODO: Docstring
    '''
    J = cli_utility.config_auth_server(profile)
    
    # Differentiate if name or url
    valid_url_format = cli_utility.uri_validator(job)

    # Request the data
    if valid_url_format:
        data = J.job_build_set_next_number(build_number=build_number, job_url=job)
    else:
        data = J.job_build_set_next_number(build_number=build_number, job_name=job)

    if not data:
        click.echo(click.style(f'failed"', fg='bright_red', bold=True))
        sys.exit(1)

    click.echo(click.style(f'{build_number}', fg='bright_green', bold=True))


def build_exist(profile:str, job:str, build_number:int) -> None:
    '''
    TODO: Docstring
    '''
    J = cli_utility.config_auth_server(profile)
    
    # Differentiate if name or url
    valid_url_format = cli_utility.uri_validator(job)

    # Request the data
    if valid_url_format:
        data = J.job_build_number_exist(build_number=build_number, job_url=job)
    else:
        data = J.job_build_number_exist(build_number=build_number, job_name=job)

    if not data:
        click.echo(click.style(f'not found', fg='bright_red', bold=True))
        sys.exit(1)

    click.echo(click.style(f'true', fg='bright_green', bold=True))


def build(profile:str, job:str, parameters:tuple) -> None:
    '''
    TODO: Docstring
    '''
    J = cli_utility.config_auth_server(profile)
    
    # Differentiate if name or url
    valid_url_format = cli_utility.uri_validator(job)

    # Convert a tuple of tuples to dict
    parameters = dict(list(parameters))

    # Request the data
    if valid_url_format:
        data = J.job_build_trigger(job_url=job, paramters=parameters)
    else:
        data = J.job_build_trigger(job_name=job, paramters=parameters)

    if not data:
        parameters_text = " with parameters: {parameters}" if parameters else ""
        click.echo(click.style(f'failed', fg='bright_red', bold=True))
        sys.exit(1)

    click.echo(click.style(f'{data}', fg='bright_green', bold=True))


def queue_check(opt_pretty:bool, opt_yaml:bool, opt_xml:bool, profile:str, job:str, opt_id:bool) -> None:
    '''
    TODO: Docstring
    '''
    J = cli_utility.config_auth_server(profile)
    
    # Differentiate if name or url
    valid_url_format = cli_utility.uri_validator(job)

    # Request the data
    if valid_url_format:
        data, queue_id = J.job_in_queue_check(job_url=job)
    else:
        data, queue_id = J.job_in_queue_check(job_name=job)

    if not data:
        out = '{}' if not opt_id else '0'
        click.echo(click.style(out, fg='bright_red', bold=True))
        sys.exit(1)

    if opt_id:
        click.echo(click.style(f'{queue_id}', fg='bright_green', bold=True))
    else:
        cli_utility.standard_out(data, opt_pretty, opt_yaml, opt_xml)
