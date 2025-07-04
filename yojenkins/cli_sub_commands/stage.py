"""Stage click sub-command"""
# pylint: skip-file

import click

from yojenkins.__main__ import stage
from yojenkins.cli import cli_decorators, cli_stage
from yojenkins.cli.cli_utility import set_debug_log_level
from yojenkins.utility.utility import translate_kwargs


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
def info(ctx, debug, **kwargs):
    """Stage information

    USAGE NOTES:

    \b
        - You must either sepcify the job with its build number
          or the direct URl to the build

    EXAMPLE:

    \b
    - yojenkins stage info my-build-stage --job my-job --latest
    - yojenkins stage info stage-name --build_url http://localhost:8080/job/my-job/3/ --pretty
    """
    set_debug_log_level(debug)
    if kwargs.get("job") or kwargs.get("url"):
        cli_stage.info(**translate_kwargs(kwargs))
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
def status(ctx, debug, **kwargs):
    """Stage status text"""
    set_debug_log_level(debug)
    if kwargs.get("job") or kwargs.get("url"):
        cli_stage.status(**translate_kwargs(kwargs))
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
def steps(ctx, debug, **kwargs):
    """Get stage steps"""
    set_debug_log_level(debug)
    if kwargs.get("job") or kwargs.get("url"):
        cli_stage.steps(**translate_kwargs(kwargs))
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
def logs(ctx, debug, **kwargs):
    """Stage logs"""
    set_debug_log_level(debug)
    if kwargs.get("job") or kwargs.get("url"):
        cli_stage.logs(**translate_kwargs(kwargs))
    else:
        click.echo(ctx.get_help())
