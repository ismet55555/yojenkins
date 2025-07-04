"""Job click sub-command"""
# pylint: skip-file

import click

from yojenkins.__main__ import job
from yojenkins.cli import cli_decorators, cli_job
from yojenkins.cli.cli_utility import set_debug_log_level
from yojenkins.utility.utility import translate_kwargs


@job.command(short_help='\tJob information')
@cli_decorators.debug
@cli_decorators.format_output
@cli_decorators.profile
@click.argument('job', nargs=1, type=str, required=True)
def info(debug, **kwargs):
    """Job information"""
    set_debug_log_level(debug)
    cli_job.info(**translate_kwargs(kwargs))


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
def search(debug, **kwargs):
    """Search jobs by REGEX pattern"""
    set_debug_log_level(debug)
    cli_job.search(**translate_kwargs(kwargs))


@job.command(short_help='\tList all builds for job')
@cli_decorators.debug
@cli_decorators.format_output
@cli_decorators.profile
@click.argument('job', nargs=1, type=str, required=True)
@cli_decorators.list
def list(debug, **kwargs):
    """List all builds for job"""
    set_debug_log_level(debug)
    cli_job.build_list(**translate_kwargs(kwargs))


@job.command(short_help='\tGet next build number')
@cli_decorators.debug
@cli_decorators.profile
@click.argument('job', nargs=1, type=str, required=True)
def next(debug, **kwargs):
    """Get next build number"""
    set_debug_log_level(debug)
    cli_job.build_next(**translate_kwargs(kwargs))


@job.command(short_help='\tGet previous build number')
@cli_decorators.debug
@cli_decorators.profile
@click.argument('job', nargs=1, type=str, required=True)
def last(debug, **kwargs):
    """Get previous build number"""
    set_debug_log_level(debug)
    cli_job.build_last(**translate_kwargs(kwargs))


@job.command(short_help='\tSet the next build number')
@cli_decorators.debug
@cli_decorators.profile
@click.argument('job', nargs=1, type=str, required=True)
@click.argument('build_number', nargs=1, type=int, required=True)
def set(debug, **kwargs):
    """Set the next build number"""
    set_debug_log_level(debug)
    cli_job.build_set(**translate_kwargs(kwargs))


@job.command(short_help='\tCheck if build number exists')
@cli_decorators.debug
@cli_decorators.profile
@click.argument('job', nargs=1, type=str, required=True)
@click.argument('build_number', nargs=1, type=int, required=True)
def build_exist(debug, **kwargs):
    """Check if build number exists"""
    set_debug_log_level(debug)
    cli_job.build_exist(**translate_kwargs(kwargs))


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
@click.option('--follow-logs',
              type=bool,
              required=False,
              is_flag=True,
              help='Wait for build, follow logs when build starts')
def build(debug, **kwargs):
    """Build a job

    EXAMPLES:

    \b
      - yojenkins job build my_job
      - yojenkins job build my_job --parameter MY_PARAM "my param value"
      - yojenkins job build my_job --follow-logs
    """
    set_debug_log_level(debug)
    cli_job.build(**translate_kwargs(kwargs))


@job.command(short_help='\tCheck if this job is in queue')
@cli_decorators.debug
@cli_decorators.format_output
@cli_decorators.profile
@click.argument('job', nargs=1, type=str, required=True)
@click.option('-i', '--id', type=bool, default=False, required=False, is_flag=True, help='Only output queue ID')
def queue_check(debug, **kwargs):
    """Check if this job is in queue"""
    set_debug_log_level(debug)
    cli_job.queue_check(**translate_kwargs(kwargs))


@job.command(short_help='\tCancel this job in queue')
@cli_decorators.debug
@cli_decorators.profile
@click.option('-i', '--id', type=int, default=False, required=True, help='Queue ID')
def queue_cancel(debug, **kwargs):
    """Cancel this job in queue"""
    set_debug_log_level(debug)
    # cli_job.queue_cancel(**translate_kwargs(kwargs))
    click.secho('TODO :-/', fg='yellow')


@job.command(short_help='\tOpen job in web browser')
@cli_decorators.debug
@cli_decorators.profile
@click.argument('job', nargs=1, type=str, required=True)
def browser(debug, **kwargs):
    """Open job in web browser"""
    set_debug_log_level(debug)
    cli_job.browser(**translate_kwargs(kwargs))


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
def config(debug, **kwargs):
    """Get job configuration"""
    set_debug_log_level(debug)
    cli_job.config(**translate_kwargs(kwargs))


@job.command(short_help='\tDisable job')
@cli_decorators.debug
@cli_decorators.profile
@click.argument('job', nargs=1, type=str, required=True)
def disable(debug, **kwargs):
    """Disable job"""
    set_debug_log_level(debug)
    cli_job.disable(**translate_kwargs(kwargs))


@job.command(short_help='\tEnable job')
@cli_decorators.debug
@cli_decorators.profile
@click.argument('job', nargs=1, type=str, required=True)
def enable(debug, **kwargs):
    """Enable job"""
    set_debug_log_level(debug)
    cli_job.enable(**translate_kwargs(kwargs))


@job.command(short_help='\tRename job')
@cli_decorators.debug
@cli_decorators.profile
@click.argument('job', nargs=1, type=str, required=True)
@click.argument('name', nargs=1, type=str, required=True)
def rename(debug, **kwargs):
    """Rename job"""
    set_debug_log_level(debug)
    cli_job.rename(**translate_kwargs(kwargs))


@job.command(short_help='\tDelete job')
@cli_decorators.debug
@cli_decorators.profile
@click.argument('job', nargs=1, type=str, required=True)
def delete(debug, **kwargs):
    """Delete job"""
    set_debug_log_level(debug)
    cli_job.delete(**translate_kwargs(kwargs))


@job.command(short_help='\tWipe job workspace')
@cli_decorators.debug
@cli_decorators.profile
@click.argument('job', nargs=1, type=str, required=True)
def wipe(debug, **kwargs):
    """Wipe job workspace"""
    set_debug_log_level(debug)
    cli_job.wipe(**translate_kwargs(kwargs))


@job.command(short_help='\tStart monitor UI')
@cli_decorators.debug
@cli_decorators.profile
@click.argument('job', nargs=1, type=str, required=False)
@click.option('-s', '--sound', type=bool, required=False, is_flag=True, help='Enable sound effects')
def monitor(debug, **kwargs):
    """Start monitor UI"""
    set_debug_log_level(debug)
    cli_job.monitor(**translate_kwargs(kwargs))


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
def create(debug, **kwargs):
    """Create a job"""
    set_debug_log_level(debug)
    cli_job.create(**translate_kwargs(kwargs))


@job.command(short_help='\tGet job parameters')
@cli_decorators.debug
@cli_decorators.format_output
@cli_decorators.profile
@click.argument('job', nargs=1, type=str, required=False)
@cli_decorators.list
def parameters(debug, **kwargs):
    """Get job's build parameters

    Build parameters are the parameters to be used when building a job.
    """
    set_debug_log_level(debug)
    cli_job.parameters(**translate_kwargs(kwargs))


@job.command(short_help='\tFind difference between two jobs')
@cli_decorators.debug
@cli_decorators.profile
@click.argument('job-1', nargs=1, type=str, required=True)
@click.argument('job-2', nargs=1, type=str, required=True)
@click.option('--no-color', type=bool, default=False, required=False, is_flag=True, help='Show output without color')
@click.option('--diff-only',
              type=bool,
              default=False,
              required=False,
              is_flag=True,
              help='Show only lines that are different')
@click.option('--diff-guide',
              type=bool,
              default=False,
              required=False,
              is_flag=True,
              help='Show where the difference is in line')
def diff(debug, **kwargs):
    """Get the diff comparison for two jobs

    EXAMPLES:

    \b
    - yojenkins build diff "myFolder/myJob" "myFolder/myJob"
    - yojenkins build diff "myJob" "myJob" --diff-guide
    - yojenkins build diff "myJob" "yourJob" --diff-only

    """
    set_debug_log_level(debug)
    cli_job.diff(**translate_kwargs(kwargs))
