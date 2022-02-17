"""Build click sub-command"""
# pylint: skip-file

import click

from yojenkins.__main__ import build
from yojenkins.cli import cli_build, cli_decorators
from yojenkins.cli.cli_utility import set_debug_log_level


@build.command(short_help='\tBuild information')
@cli_decorators.debug
@cli_decorators.format_output
@cli_decorators.profile
@click.argument('job', nargs=1, type=str, required=False)
@click.option('-n', '--number', type=int, required=False, help='Build number')
@click.option('-u', '--url', type=str, required=False, help='Build URL (No job info needed)')
@click.option('--latest', type=bool, required=False, is_flag=True, help='Latest build (Replaces --number)')
@click.pass_context
def info(ctx, debug, pretty, yaml, xml, toml, profile, job, number, url, latest):
    """Build information"""
    set_debug_log_level(debug)
    if job or url:
        cli_build.info(pretty, yaml, xml, toml, profile, job, number, url, latest)
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
def status(ctx, debug, profile, job, number, url, latest):
    """Build status text/label"""
    set_debug_log_level(debug)
    if job or url:
        cli_build.status(profile, job, number, url, latest)
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
def abort(ctx, debug, profile, job, number, url, latest):
    """Abort build"""
    set_debug_log_level(debug)
    if job or url:
        cli_build.abort(profile, job, number, url, latest)
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
def delete(ctx, debug, profile, job, number, url, latest):
    """Delete build"""
    # TODO: Pass a list of build numbers
    set_debug_log_level(debug)
    if job or url:
        cli_build.delete(profile, job, number, url, latest)
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
def stages(ctx, debug, pretty, yaml, xml, toml, profile, list, job, number, url, latest):
    """Get build stages"""
    set_debug_log_level(debug)
    if job or url:
        cli_build.stages(pretty, yaml, xml, toml, profile, list, job, number, url, latest)
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
def logs(ctx, debug, profile, job, number, url, latest, tail, download_dir, follow):
    """Get build logs"""
    set_debug_log_level(debug)
    if job or url:
        cli_build.logs(profile, job, number, url, latest, tail, download_dir, follow)
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
def browser(ctx, debug, profile, job, number, url, latest):
    """Open build in web browser"""
    # TODO: Pass a list of build numbers
    set_debug_log_level(debug)
    if job or url:
        cli_build.browser(profile, job, number, url, latest)
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
def monitor(ctx, debug, profile, job, number, url, latest, sound):
    """Start monitor UI"""
    # TODO: Pass a list of build numbers
    set_debug_log_level(debug)
    if job or url:
        cli_build.monitor(profile, job, number, url, latest, sound)
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
def parameters(ctx, debug, pretty, yaml, xml, toml, profile, list, job, number, url, latest):
    """Get build parameters

    Build parameters are the parameters that were used to start the build.
    """
    set_debug_log_level(debug)
    if job or url:
        cli_build.parameters(pretty, yaml, xml, toml, profile, list, job, number, url, latest)
    else:
        click.echo(ctx.get_help())
