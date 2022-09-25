"""Build click sub-command"""
# pylint: skip-file

import click

from yojenkins.__main__ import build
from yojenkins.cli import cli_build, cli_decorators
from yojenkins.cli.cli_utility import set_debug_log_level
from yojenkins.utility.utility import translate_kwargs


@build.command(short_help='\tBuild information')
@cli_decorators.debug
@cli_decorators.format_output
@cli_decorators.profile
@click.argument('job', nargs=1, type=str, required=False)
@click.option('-n', '--number', type=int, required=False, help='Build number')
@click.option('-u', '--url', type=str, required=False, help='Build URL (No job info needed)')
@click.option('--latest', type=bool, required=False, is_flag=True, help='Latest build (Replaces --number)')
@click.pass_context
def info(ctx, debug, **kwargs):
    """Build information"""
    set_debug_log_level(debug)
    if kwargs.get("job") or kwargs.get("url"):
        cli_build.info(**translate_kwargs(kwargs))
    else:
        click.echo(ctx.get_help())


@build.command(short_help='\tBuild status text/label')
@cli_decorators.debug
@cli_decorators.profile
@click.argument('job', nargs=1, type=str, required=False)
@click.option('-n', '--number', type=int, required=False, help='Build number', metavar='INT')
@click.option('-u', '--url', type=str, required=False, help='Build URL (No job info needed)')
@click.option('--latest', type=bool, required=False, is_flag=True, help='Latest build (Replaces --number)')
@click.pass_context
def status(ctx, debug, **kwargs):
    """Build status text/label"""
    set_debug_log_level(debug)
    if kwargs.get("job") or kwargs.get("url"):
        cli_build.status(**translate_kwargs(kwargs))
    else:
        click.echo(ctx.get_help())
    # FIXME: Showing running for job, seems not to have picked the right build ... when url to job is used!


@build.command(short_help='\tAbort build')
@cli_decorators.debug
@cli_decorators.profile
@click.argument('job', nargs=1, type=str, required=False)
@click.option('-n', '--number', type=int, required=False, help='Build number')
@click.option('-u', '--url', type=str, required=False, help='Build URL (No job info needed)')
@click.option('--latest', type=str, required=False, is_flag=True, help='Latest build (Replaces --number)')
@click.pass_context
def abort(ctx, debug, **kwargs):
    """Abort build"""
    set_debug_log_level(debug)
    if kwargs.get("job") or kwargs.get("url"):
        cli_build.abort(**translate_kwargs(kwargs))
    else:
        click.echo(ctx.get_help())


@build.command(short_help='\tDelete build')
@cli_decorators.debug
@cli_decorators.profile
@click.argument('job', nargs=1, type=str, required=False)
@click.option('-n', '--number', type=int, required=False, help='Build number')
@click.option('-u', '--url', type=str, required=False, help='Build URL (No job info needed)')
@click.option('--latest', type=str, required=False, is_flag=True, help='Latest build (Replaces --number)')
@click.pass_context
def delete(ctx, debug, **kwargs):
    """Delete build"""
    # TODO: Pass a list of build numbers
    set_debug_log_level(debug)
    if kwargs.get("job") or kwargs.get("url"):
        cli_build.delete(**translate_kwargs(kwargs))
    else:
        click.echo(ctx.get_help())


@build.command(short_help='\tGet build stages')
@cli_decorators.debug
@cli_decorators.format_output
@cli_decorators.profile
@cli_decorators.list
@click.argument('job', nargs=1, type=str, required=False)
@click.option('-n', '--number', type=int, required=False, help='Build number')
@click.option('-u', '--url', type=str, required=False, help='Build URL (No job info needed)')
@click.option('--latest', type=str, required=False, is_flag=True, help='Latest build (Replaces --number)')
@click.pass_context
def stages(ctx, debug, **kwargs):
    """Get build stages"""
    set_debug_log_level(debug)
    if kwargs.get("job") or kwargs.get("url"):
        cli_build.stages(**translate_kwargs(kwargs))
    else:
        click.echo(ctx.get_help())


@build.command(short_help='\tGet build logs')
@cli_decorators.debug
@cli_decorators.profile
@click.argument('job', nargs=1, type=str, required=False)
@click.option('-n', '--number', type=int, required=False, help='Build number')
@click.option('-u', '--url', type=str, required=False, help='Build URL (No job info needed)')
@click.option('--latest', type=str, required=False, is_flag=True, help='Latest build (Replaces --number)')
@click.option('--tail', type=float, required=False, help='Last of logs. If < 1 then %, else number of lines')
@click.option('-dd',
              '--download-dir',
              type=click.Path(file_okay=False, dir_okay=True),
              required=False,
              is_flag=False,
              help='Download logs to directory')
@click.option('--follow',
              default=False,
              type=str,
              required=False,
              is_flag=True,
              help='Follow/Stream the logs as they are generated')
@click.pass_context
def logs(ctx, debug, **kwargs):
    """Get build logs"""
    set_debug_log_level(debug)
    if kwargs.get("job") or kwargs.get("url"):
        cli_build.logs(**translate_kwargs(kwargs))
    else:
        click.echo(ctx.get_help())


@build.command(short_help='\tOpen build in web browser')
@cli_decorators.debug
@cli_decorators.profile
@click.argument('job', nargs=1, type=str, required=False)
@click.option('-n', '--number', type=int, required=False, help='Build number')
@click.option('-u', '--url', type=str, required=False, help='Build URL (No job info needed)')
@click.option('--latest', type=str, required=False, is_flag=True, help='Latest build (Replaces --number)')
@click.pass_context
def browser(ctx, debug, **kwargs):
    """Open build in web browser"""
    # TODO: Pass a list of build numbers
    set_debug_log_level(debug)
    if kwargs.get("job") or kwargs.get("url"):
        cli_build.browser(**translate_kwargs(kwargs))
    else:
        click.echo(ctx.get_help())


@build.command(short_help='\tStart monitor UI')
@cli_decorators.debug
@cli_decorators.profile
@click.argument('job', nargs=1, type=str, required=False)
@click.option('-n', '--number', type=int, required=False, help='Build number')
@click.option('-u', '--url', type=str, required=False, help='Build URL (No job info needed)')
@click.option('--latest', type=str, required=False, is_flag=True, help='Latest build (Replaces --number)')
@click.option('-s', '--sound', type=bool, required=False, is_flag=True, help='Enable sound effects')
@click.pass_context
def monitor(ctx, debug, **kwargs):
    """Start monitor UI"""
    # TODO: Pass a list of build numbers
    set_debug_log_level(debug)
    if kwargs.get("job") or kwargs.get("url"):
        cli_build.monitor(**translate_kwargs(kwargs))
    else:
        click.echo(ctx.get_help())


@build.command(short_help='\tGet build parameters')
@cli_decorators.debug
@cli_decorators.format_output
@cli_decorators.profile
@cli_decorators.list
@click.argument('job', nargs=1, type=str, required=False)
@click.option('-n', '--number', type=int, required=False, help='Build number')
@click.option('-u', '--url', type=str, required=False, help='Build URL (No job info needed)')
@click.option('--latest', type=str, required=False, is_flag=True, help='Latest build (Replaces --number)')
@click.pass_context
def parameters(ctx, debug, **kwargs):
    """Get build parameters

    Build parameters are the parameters that were used to start the build.
    """
    set_debug_log_level(debug)
    if kwargs.get("job") or kwargs.get("url"):
        cli_build.parameters(**translate_kwargs(kwargs))
    else:
        click.echo(ctx.get_help())


@build.command(short_help='\tRebuild build')
@cli_decorators.debug
@cli_decorators.profile
@click.argument('job', nargs=1, type=str, required=False)
@click.option('-n', '--number', type=int, required=False, help='Build number')
@click.option('-u', '--url', type=str, required=False, help='Build URL (No job info needed)')
@click.option('--latest', type=str, required=False, is_flag=True, help='Latest build (Replaces --number)')
@click.pass_context
def rebuild(ctx, debug, **kwargs):
    """Get build parameters

    Rebuild the specified build exactly as it ran
    """
    set_debug_log_level(debug)
    if kwargs.get("job") or kwargs.get("url"):
        cli_build.rebuild(**translate_kwargs(kwargs))
    else:
        click.echo(ctx.get_help())
