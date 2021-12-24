"""Stage click sub-command"""
# pylint: skip-file

import click

from yojenkins.__main__ import stage
from yojenkins.cli import cli_decorators, cli_stage
from yojenkins.cli.cli_utility import set_debug_log_level


@stage.command(short_help='\tStage information')
@cli_decorators.debug
@cli_decorators.format_output
@cli_decorators.profile
@click.argument('name', nargs=1, type=str, required=True)
@click.option('-j', '--job', type=str, required=False, help='Job name or URL')
@click.option('-n', '--number', type=int, required=False, help='Build number')
@click.option('-u', '--url', type=str, required=False, help='Build URL (No job info needed)')
@click.option('--latest', type=bool, required=False, is_flag=True, help='Latest build (Replaces --number)')
@click.pass_context
def info(ctx, debug, pretty, yaml, xml, toml, profile, name, job, number, url, latest):
    """Stage information"""
    set_debug_log_level(debug)
    if job or url:
        cli_stage.info(pretty, yaml, xml, toml, profile, name, job, number, url, latest)
    else:
        click.echo(ctx.get_help())


@stage.command(short_help='\tStage status text')
@cli_decorators.debug
@cli_decorators.profile
@click.argument('name', nargs=1, type=str, required=True)
@click.option('-j', '--job', type=str, required=False, help='Job name or URL')
@click.option('-n', '--number', type=int, required=False, help='Build number')
@click.option('-u', '--url', type=str, required=False, help='Build URL (No job info needed)')
@click.option('--latest', type=bool, required=False, is_flag=True, help='Latest build (Replaces --number)')
@click.pass_context
def status(ctx, debug, profile, name, job, number, url, latest):
    """Stage status text"""
    set_debug_log_level(debug)
    if job or url:
        cli_stage.status(profile, name, job, number, url, latest)
    else:
        click.echo(ctx.get_help())


@stage.command(short_help='\tGet stage steps')
@cli_decorators.debug
@cli_decorators.format_output
@cli_decorators.profile
@cli_decorators.list
@click.argument('name', nargs=1, type=str, required=True)
@click.option('-j', '--job', type=str, required=False, help='Job name or URL')
@click.option('-n', '--number', type=int, required=False, help='Build number')
@click.option('-u', '--url', type=str, required=False, help='Build URL (No job info needed)')
@click.option('--latest', type=bool, required=False, is_flag=True, help='Latest build (Replaces --number)')
@click.pass_context
def steps(ctx, debug, pretty, yaml, xml, toml, profile, list, name, job, number, url, latest):
    """Get stage steps"""
    set_debug_log_level(debug)
    if job or url:
        cli_stage.steps(pretty, yaml, xml, toml, profile, list, name, job, number, url, latest)
    else:
        click.echo(ctx.get_help())


@stage.command(short_help='\tStage steps')
@cli_decorators.debug
@cli_decorators.profile
@click.argument('name', nargs=1, type=str, required=True)
@click.option('-j', '--job', type=str, required=False, help='Job name or URL')
@click.option('-n', '--number', type=int, required=False, help='Build number')
@click.option('-u', '--url', type=str, required=False, help='Build URL (No job info needed)')
@click.option('--latest', type=bool, required=False, is_flag=True, help='Latest build (Replaces --number)')
@click.option('-dd',
              '--download_dir',
              type=click.Path(file_okay=False, dir_okay=True),
              required=False,
              is_flag=False,
              help='Download logs to directory')
@click.pass_context
def logs(ctx, debug, profile, name, job, number, url, latest, download_dir):
    """Stage logs"""
    set_debug_log_level(debug)
    if job or url:
        cli_stage.logs(profile, name, job, number, url, latest, download_dir)
    else:
        click.echo(ctx.get_help())
