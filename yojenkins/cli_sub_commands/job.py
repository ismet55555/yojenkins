"""Job click sub-command"""
# pylint: skip-file

import click

from yojenkins.__main__ import job
from yojenkins.cli import cli_decorators, cli_job
from yojenkins.cli.cli_utility import set_debug_log_level


@job.command(short_help='\tJob information')
@cli_decorators.debug
@cli_decorators.format_output
@cli_decorators.profile
@click.argument('job', nargs=1, type=str, required=True)
def info(debug, pretty, yaml, xml, toml, profile, job):
    """Job information"""
    set_debug_log_level(debug)
    cli_job.info(pretty, yaml, xml, toml, profile, job)


@job.command(short_help='\tSearch jobs by REGEX pattern')
@cli_decorators.debug
@cli_decorators.format_output
@cli_decorators.profile
@click.argument('search_pattern', nargs=1, type=str, required=True)
@click.option('-sf', '--search-folder', type=str, default='', required=False, help='Folder within which to search')
@click.option('-d', '--depth', type=int, default=4, required=False, help='Search depth from root directory')
@click.option('-fn',
              '--fullname',
              type=bool,
              default=False,
              required=False,
              is_flag=True,
              help='Search entire job path name')
@cli_decorators.list
def search(debug, pretty, yaml, xml, toml, profile, search_pattern, search_folder, depth, fullname, list):
    """Search jobs by REGEX pattern"""
    set_debug_log_level(debug)
    cli_job.search(pretty, yaml, xml, toml, profile, search_pattern, search_folder, depth, fullname, list)


@job.command(short_help='\tList all builds for job')
@cli_decorators.debug
@cli_decorators.format_output
@cli_decorators.profile
@click.argument('job', nargs=1, type=str, required=True)
@cli_decorators.list
def list(debug, pretty, yaml, xml, toml, profile, job, list):
    """List all builds for job"""
    set_debug_log_level(debug)
    cli_job.build_list(pretty, yaml, xml, toml, profile, job, list)


@job.command(short_help='\tGet next build number')
@cli_decorators.debug
@cli_decorators.profile
@click.argument('job', nargs=1, type=str, required=True)
def next(debug, profile, job):
    """Get next build number"""
    set_debug_log_level(debug)
    cli_job.build_next(profile, job)


@job.command(short_help='\tGet previous build number')
@cli_decorators.debug
@cli_decorators.profile
@click.argument('job', nargs=1, type=str, required=True)
def last(debug, profile, job):
    """Get previous build number"""
    set_debug_log_level(debug)
    cli_job.build_last(profile, job)


@job.command(short_help='\tSet the next build number')
@cli_decorators.debug
@cli_decorators.profile
@click.argument('job', nargs=1, type=str, required=True)
@click.argument('build_number', nargs=1, type=int, required=True)
def set(debug, profile, job, build_number):
    """Set the next build number"""
    set_debug_log_level(debug)
    cli_job.build_set(profile, job, build_number)


@job.command(short_help='\tCheck if build number exists')
@cli_decorators.debug
@cli_decorators.profile
@click.argument('job', nargs=1, type=str, required=True)
@click.argument('build_number', nargs=1, type=int, required=True)
def build_exist(debug, profile, job, build_number):
    """Check if build number exists"""
    set_debug_log_level(debug)
    cli_job.build_exist(profile, job, build_number)


@job.command(short_help='\tBuild a job')
@cli_decorators.debug
@cli_decorators.profile
@click.argument('job', nargs=1, type=str, required=True)
@click.option('-p',
              '--parameter',
              nargs=2,
              multiple=True,
              required=False,
              help='Specify key-value parameter. Can use multiple times. Use once per parameter')
def build(debug, profile, job, parameter):
    """Build a job"""
    set_debug_log_level(debug)
    cli_job.build(profile, job, parameter)


@job.command(short_help='\tCheck if this job is in queue')
@cli_decorators.debug
@cli_decorators.format_output
@cli_decorators.profile
@click.argument('job', nargs=1, type=str, required=True)
@click.option('-i', '--id', type=bool, default=False, required=False, is_flag=True, help='Only output queue ID')
def queue_check(debug, pretty, yaml, xml, toml, profile, job, id):
    """Check if this job is in queue"""
    set_debug_log_level(debug)
    cli_job.queue_check(pretty, yaml, xml, toml, profile, job, id)


@job.command(short_help='\tCancel this job in queue')
@cli_decorators.debug
@cli_decorators.profile
@click.option('-i', '--id', type=int, default=False, required=True, help='Queue ID')
def queue_cancel(debug, profile, id):
    """Cancel this job in queue"""
    set_debug_log_level(debug)
    # cli_job.queue_cancel(profile, id)
    click.secho('TODO :-/', fg='yellow')


@job.command(short_help='\tOpen job in web browser')
@cli_decorators.debug
@cli_decorators.profile
@click.argument('job', nargs=1, type=str, required=True)
def browser(debug, profile, job):
    """Open job in web browser"""
    set_debug_log_level(debug)
    cli_job.browser(profile, job)


@job.command(short_help='\tGet job configuration')
@cli_decorators.debug
@cli_decorators.format_output
@click.option('-j',
              '--json',
              type=bool,
              default=False,
              required=False,
              is_flag=True,
              help='Output config in JSON format')
@cli_decorators.profile
@click.argument('job', nargs=1, type=str, required=True)
@click.option('--filepath',
              type=click.Path(file_okay=True, dir_okay=False),
              required=False,
              help='Filepath to write configurations to')
def config(debug, pretty, yaml, xml, toml, json, profile, job, filepath):
    """Get job configuration"""
    set_debug_log_level(debug)
    cli_job.config(pretty, yaml, xml, toml, json, profile, job, filepath)


@job.command(short_help='\tDisable job')
@cli_decorators.debug
@cli_decorators.profile
@click.argument('job', nargs=1, type=str, required=True)
def disable(debug, profile, job):
    """Disable job"""
    set_debug_log_level(debug)
    cli_job.disable(profile, job)


@job.command(short_help='\tEnable job')
@cli_decorators.debug
@cli_decorators.profile
@click.argument('job', nargs=1, type=str, required=True)
def enable(debug, profile, job):
    """Enable job"""
    set_debug_log_level(debug)
    cli_job.enable(profile, job)


@job.command(short_help='\tRename job')
@cli_decorators.debug
@cli_decorators.profile
@click.argument('job', nargs=1, type=str, required=True)
@click.argument('name', nargs=1, type=str, required=True)
def rename(debug, profile, job, name):
    """Rename job"""
    set_debug_log_level(debug)
    cli_job.rename(profile, job, name)


@job.command(short_help='\tDelete job')
@cli_decorators.debug
@cli_decorators.profile
@click.argument('job', nargs=1, type=str, required=True)
def delete(debug, profile, job):
    """Delete job"""
    set_debug_log_level(debug)
    cli_job.delete(profile, job)


@job.command(short_help='\tWipe job workspace')
@cli_decorators.debug
@cli_decorators.profile
@click.argument('job', nargs=1, type=str, required=True)
def wipe(debug, profile, job):
    """Wipe job workspace"""
    set_debug_log_level(debug)
    cli_job.wipe(profile, job)


@job.command(short_help='\tStart monitor UI')
@cli_decorators.debug
@cli_decorators.profile
@click.argument('job', nargs=1, type=str, required=False)
@click.option('-s', '--sound', type=bool, required=False, is_flag=True, help='Enable sound effects')
def monitor(debug, profile, job, sound):
    """Start monitor UI"""
    set_debug_log_level(debug)
    cli_job.monitor(profile, job, sound)


@job.command(short_help='\tCreate a job')
@cli_decorators.debug
@cli_decorators.profile
@click.argument('name', nargs=1, type=str, required=True)
@click.argument('folder', nargs=1, type=str, required=True)
@click.option('--config-file',
              default='',
              type=click.Path(file_okay=True, dir_okay=False),
              required=False,
              help='Path to local config file defining job')
@click.option('--config-is-json',
              type=bool,
              default=False,
              required=False,
              is_flag=True,
              help='The specified file is in JSON format')
def create(debug, profile, name, folder, config_file, config_is_json):
    """Create a job"""
    set_debug_log_level(debug)
    cli_job.create(profile, name, folder, config_file, config_is_json)


@job.command(short_help='\tGet job parameters')
@cli_decorators.debug
@cli_decorators.format_output
@cli_decorators.profile
@click.argument('job', nargs=1, type=str, required=False)
@cli_decorators.list
def parameters(debug, pretty, yaml, xml, toml, profile, job, list):
    """Get job's build parameters

    Build parameters are the parameters to be used when building a job.
    """
    set_debug_log_level(debug)
    cli_job.parameters(pretty, yaml, xml, toml, profile, job, list)
