#!/usr/bin/env python3

import logging
import os
import sys
from pprint import pprint
from urllib.parse import urlparse

import click
import coloredlogs

from cli_groups import (cli_auth, cli_build, cli_folder, cli_job, cli_server,
                        cli_stage, cli_step, cli_decorators)

# Turn off info level logging for jons2xml
logging.getLogger("dicttoxml").setLevel(logging.WARNING)

# Defining the message logger and applying color to the output logs
logger_root = logging.basicConfig(
    format='[%(asctime)s][%(levelname)-8s] [%(filename)-25s:%(lineno)4s] %(message)s',
    datefmt="%H:%M:%S",
    handlers=[logging.StreamHandler(sys.stdout)]
)
coloredlogs.install(
    level=logging.INFO,
    fmt='[%(asctime)s][%(levelname)-8s] [%(filename)-25s:%(lineno)4s] %(message)s',
    datefmt="%H:%M:%S",
    logger=logger_root
)
logger = logging.getLogger()


##############################################################################


MAIN_HELP_TEXT = """
    \t\t\tYO-JENKINS (Version: 0.1.2)

    yo-jenkins is a tool that is focused on interfacing with
    Jenkins server from the comfort of the beloved command line. 
    This tool can also be used as a middleware utility, generating and
    passing Jenkins information or automating tasks.

    Quick Start:

        1. Configure profile: yo-jenkins auth configure

        2. Add a API token: yo-jenkins auth token --profile <PROFILE NAME>

        3. Verify authentication: yo-jenkins auth verify

        4. Explore yo-jenkins
"""


##############################################################################


def set_debug_log_level(debug_flag:bool):
    """Setting the log DEBUG level

    Args:
        debug_flag : Boolean flag, True to set to DEBUG, else INFO

    Returns:
        None
    """
    if debug_flag:
        click.echo(click.style(f'\n[ LOGGING LEVEL ] : DEBUG\n', fg='bright_yellow', bold=True))
        logging_level = logging.DEBUG
    else:
        logging_level = logging.INFO
    logger.setLevel(logging_level)
    for handler in logger.handlers:
        handler.setLevel(logging_level)
    logger.addHandler(logging.FileHandler("yo-jenkins.log"))


##############################################################################


@click.group(help=MAIN_HELP_TEXT)
@click.version_option(
    '0.1.2', "-v", "--version", message="%(version)s".format(version="version"),
    help="Show the version"
)
def main():   
    pass


##############################################################################
#                             AUTHENTICATE
##############################################################################

# @main.group(short_help='\tAuthentication and profile management')
@main.group(short_help='\tManage authentication and profiles')
def auth():
    """
    Top level CLI menu: auth
    """
    pass

@auth.command(short_help='\tConfigure authentication')
@cli_decorators.debug
@click.option('--token', type=str, required=False, is_flag=False, help='Authentication token used for setup profile')
def configure(debug, token):
    set_debug_log_level(debug)
    cli_auth.configure(token)

@auth.command(short_help='\tGenerate authentication API token')
@cli_decorators.debug
@cli_decorators.profile
def token(debug, profile):
    set_debug_log_level(debug)
    cli_auth.token(profile)

@auth.command(short_help='\tShow the local credentials file')
@cli_decorators.debug
@cli_decorators.format_output
def show(debug, pretty, yaml, xml):
    set_debug_log_level(debug)
    cli_auth.show(pretty, yaml, xml)

@auth.command(short_help='\tCheck if credentials can authenticate')
@cli_decorators.debug
@cli_decorators.profile
def verify(debug, profile):
    set_debug_log_level(debug)
    cli_auth.verify(profile)

@auth.command(short_help='\tWipe all credentials for this device')
@cli_decorators.debug
def wipe(debug):
    set_debug_log_level(debug)
    click.echo(click.style('TODO', fg='yellow',))




##############################################################################
#                             SERVER
##############################################################################
@main.group(short_help='\tManage server')
def server():
    """Top level CLI menu: server"""
    pass

@server.command(short_help='\tServer information')
@cli_decorators.debug
@cli_decorators.format_output
@cli_decorators.profile
def info(debug, pretty, yaml, xml, profile):
    set_debug_log_level(debug)
    cli_server.info(pretty, yaml, xml, profile)

@server.command(short_help='\tShow user information')
@cli_decorators.debug
@cli_decorators.format_output
@cli_decorators.profile
def user(debug, pretty, yaml, xml, profile):
    set_debug_log_level(debug)
    cli_server.user(pretty, yaml, xml, profile)

@server.command(short_help='\tShow current build queue')
@cli_decorators.debug
@cli_decorators.format_output
@cli_decorators.profile
@cli_decorators.list
def queue(debug, pretty, yaml, xml, profile, list):
    set_debug_log_level(debug)
    cli_server.queue(pretty, yaml, xml, profile, list)
    # NOTE: Maybe move to "job"?

@server.command(short_help='\tShow plugin information')
@cli_decorators.debug
@cli_decorators.format_output
@cli_decorators.profile
@cli_decorators.list
def plugin(debug, pretty, yaml, xml, profile, list):
    set_debug_log_level(debug)
    cli_server.plugin(pretty, yaml, xml, profile, list)

@server.command(short_help='\tCheck if sever is reachable')
@cli_decorators.debug
@cli_decorators.profile
def reachable(debug, profile):
    set_debug_log_level(debug)
    cli_server.reachable(profile)

@server.command(short_help='\tQuite/Un-quite server')
@cli_decorators.debug
@click.option('-o', '--off', type=bool, default=False, required=False, is_flag=True, help='Undo quite down mode')
def quite(debug, off):
    set_debug_log_level(debug)
    click.echo(click.style('TODO', fg='yellow',))
    # TODO: Confirmation yes, also ability to pass auto approve --yes

@server.command(short_help='\tWait for Jenkins server to resume normal operations')
@cli_decorators.debug
def wait_normal(debug):
    set_debug_log_level(debug)
    click.echo(click.style('TODO', fg='yellow',))

@server.command(short_help='\tRestart / Reboot')
@cli_decorators.debug
def restart(debug):
    set_debug_log_level(debug)
    click.echo(click.style('TODO', fg='yellow',))

@server.command(short_help='\tShutdown')
@cli_decorators.debug
def shutdown(debug):
    set_debug_log_level(debug)
    click.echo(click.style('TODO', fg='yellow',))



##############################################################################
#                             NODE
##############################################################################
@main.group(short_help='\tManage Node')
def node():
    """Top level CLI menu: node"""
    pass
    click.echo(click.style('TODO', fg='yellow',))

@node.command(short_help='\tServer information')
@cli_decorators.debug
@cli_decorators.profile
def info(debug, profile):
    set_debug_log_level(debug)
    click.echo(click.style('TODO', fg='yellow',))

# TODO:
#   - Info
#   - List
#   - Delete
#   - Type
#   - Toggle offline/online



##############################################################################
#                             FOLDER
##############################################################################
@main.group(short_help='\tManage folders')
def folder():
    """Top level CLI menu: folder"""
    pass

@folder.command(short_help='\tFolder information')
@cli_decorators.debug
@cli_decorators.format_output
@cli_decorators.profile
@click.argument('folder', nargs=1, type=str, required=True)
def info(debug, pretty, yaml, xml, profile, folder):
    set_debug_log_level(debug)
    cli_folder.info(pretty, yaml, xml, profile, folder)

@folder.command(short_help='\tSearch folders by REGEX pattern')
@cli_decorators.debug
@cli_decorators.format_output
@cli_decorators.profile
@click.argument('search_pattern', nargs=1, type=str, required=True)
@click.option('-sf', '--start-folder', type=str, default='', required=False, help='Folder within which to start searching')
@click.option('-d', '--depth', type=int, default=4, required=False, help='Search depth from root directory')
@cli_decorators.list
def search(debug, pretty, yaml, xml, profile, search_pattern, start_folder, depth, list):
    set_debug_log_level(debug)
    cli_folder.search(pretty, yaml, xml, profile, search_pattern, start_folder, depth, list)
    # TODO: Add a -fn --fullname option to look into full path instead of name

@folder.command(short_help='\tList subfolders')
@cli_decorators.debug
@cli_decorators.format_output
@cli_decorators.profile
@click.argument('folder', nargs=1, type=str, required=True)
@cli_decorators.list
def subfolders(debug, pretty, yaml, xml, profile, folder, list):
    set_debug_log_level(debug)
    cli_folder.subfolders(pretty, yaml, xml, profile, folder, list)

@folder.command(short_help='\tList jobs')
@cli_decorators.debug
@cli_decorators.format_output
@cli_decorators.profile
@click.argument('folder', nargs=1, type=str, required=True)
@cli_decorators.list
def jobs(debug, pretty, yaml, xml, profile, folder, list):
    set_debug_log_level(debug)
    cli_folder.jobs(pretty, yaml, xml, profile, folder, list)

@folder.command(short_help='\tList views')
@cli_decorators.debug
@cli_decorators.format_output
@cli_decorators.profile
@click.argument('folder', nargs=1, type=str, required=True)
@cli_decorators.list
def views(debug, pretty, yaml, xml, profile, folder, list):
    set_debug_log_level(debug)
    cli_folder.views(pretty, yaml, xml, profile, folder, list)

@folder.command(short_help='\tList all items in folder')
@cli_decorators.debug
@cli_decorators.format_output
@cli_decorators.profile
@click.argument('folder', nargs=1, type=str, required=True)
@cli_decorators.list
def items(debug, pretty, yaml, xml, profile, folder, list):
    set_debug_log_level(debug)
    cli_folder.items(pretty, yaml, xml, profile, folder, list)



##############################################################################
#                             JOB
##############################################################################
@main.group(short_help='\tManage jobs')
def job():
    """Top level CLI menu: job"""
    pass

@job.command(short_help='\tJob information')
@cli_decorators.debug
@cli_decorators.format_output
@cli_decorators.profile
@click.argument('job', nargs=1, type=str, required=True)
def info(debug, pretty, yaml, xml, profile, job):
    set_debug_log_level(debug)
    cli_job.info(pretty, yaml, xml, profile, job)

@job.command(short_help='\tSearch jobs by REGEX pattern')
@cli_decorators.debug
@cli_decorators.format_output
@cli_decorators.profile
@click.argument('search_pattern', nargs=1, type=str, required=True)
@click.option('-sf', '--start-folder', type=str, default='', required=False, help='Folder within which to start searching')
@click.option('-d', '--depth', type=int, default=4, required=False, help='Search depth from root directory')
@cli_decorators.list
def search(debug, pretty, yaml, xml, profile, search_pattern, start_folder, depth, list):
    set_debug_log_level(debug)
    cli_job.search(pretty, yaml, xml, profile, search_pattern, start_folder, depth, list)
    # TODO: Add a -fn --fullname option to look into full path instead of name

@job.command(short_help='\tList builds for job')
@cli_decorators.debug
@cli_decorators.format_output
@cli_decorators.profile
@click.argument('job', nargs=1, type=str, required=True)
@cli_decorators.list
def build_list(debug, pretty, yaml, xml, profile, job, list):
    set_debug_log_level(debug)
    cli_job.build_list(pretty, yaml, xml, profile, job, list)

@job.command(short_help='\tGet the next build number')
@cli_decorators.debug
@cli_decorators.profile
@click.argument('job', nargs=1, type=str, required=True)
def build_next(debug, profile, job):
    set_debug_log_level(debug)
    cli_job.build_next(profile, job)

@job.command(short_help='\tGet the previous build number')
@cli_decorators.debug
@cli_decorators.profile
@click.argument('job', nargs=1, type=str, required=True)
def build_last(debug, profile, job):
    set_debug_log_level(debug)
    cli_job.build_last(profile, job)

@job.command(short_help='\tSet the next build number')
@cli_decorators.debug
@cli_decorators.profile
@click.argument('job', nargs=1, type=str, required=True)
@click.argument('build_number', nargs=1, type=int, required=True)
def build_set(debug, profile, job, build_number):
    set_debug_log_level(debug)
    cli_job.build_set(profile, job, build_number)

@job.command(short_help='\tCheck if build number exists')
@cli_decorators.debug
@cli_decorators.profile
@click.argument('job', nargs=1, type=str, required=True)
@click.argument('build_number', nargs=1, type=int, required=True)
def build_exist(debug, profile, job, build_number):
    set_debug_log_level(debug)
    cli_job.build_exist(profile, job, build_number)

@job.command(short_help='\tBuild a job')
@cli_decorators.debug
@cli_decorators.profile
@click.argument('job', nargs=1, type=str, required=True)
@click.option('-p', '--parameter', nargs=2, multiple=True, required=False, help='Specify key-value parameter. Can use multiple times. Use once per parameter')
def build(debug, profile, job, parameter):
    set_debug_log_level(debug)
    cli_job.build(profile, job, parameter)

@job.command(short_help='\tCheck if this job is in queue')
@cli_decorators.debug
@cli_decorators.format_output
@cli_decorators.profile
@click.argument('job', nargs=1, type=str, required=True)
@click.option('-i', '--id', type=bool, default=False, required=False, is_flag=True, help='Only output queue ID')
def queue_check(debug, pretty, yaml, xml, profile, job, id):
    set_debug_log_level(debug)
    cli_job.queue_check(pretty, yaml, xml, profile, job, id)

@job.command(short_help='\tCancel this job in queue')
@cli_decorators.debug
@cli_decorators.profile
@click.option('-i', '--id', type=int, default=False, required=True, help='Queue ID')
def queue_cancel(debug, profile, id):
    set_debug_log_level(debug)
    # cli_job.queue_cancel(profile, id)
    click.echo(click.style('TODO', fg='yellow',))

# TODO:
#   - Delete Job
#   - Disable Job
#   - Enable Job
#   - Rename Job
#   - Wipe Job workspace



##############################################################################
#                             BUILD
##############################################################################
@main.group(short_help='\tManage builds')
def build():
    """Top level CLI menu: build"""
    pass

@build.command(short_help='\tBuild information')
@cli_decorators.debug
@cli_decorators.format_output
@cli_decorators.profile
@click.argument('job', nargs=1, type=str, required=False)
@click.option('-n', '--number', type=int, required=False, help='Build number')
@click.option('-u', '--url', type=str, required=False, help='Build URL (No job info needed)')
@click.option('--latest', type=bool, required=False, is_flag=True, help='Latest build (Replaces --number)')
@click.pass_context
def info(ctx, debug, pretty, yaml, xml, profile, job, number, url, latest):
    set_debug_log_level(debug)
    if job or url:
        cli_build.info(pretty, yaml, xml, profile, job, number, url, latest)
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
def stages(ctx, debug, pretty, yaml, xml, profile, list, job, number, url, latest):
    set_debug_log_level(debug)
    if job or url:
        cli_build.stages(pretty, yaml, xml, profile, list, job, number, url, latest)
    else:
        click.echo(ctx.get_help())

@build.command(short_help='\tGet build logs')
@cli_decorators.debug
@cli_decorators.profile
@click.argument('job', nargs=1, type=str, required=False)
@click.option('-n', '--number', type=int, required=False, help='Build number')
@click.option('-u', '--url', type=str, required=False, help='Build URL (No job info needed)')
@click.option('--latest', type=str, required=False, is_flag=True, help='Latest build (Replaces --number)')
@click.option('-d', '--download', type=str, required=False, is_flag=True, help='Download the logs')
@click.pass_context
def log(ctx, debug, profile, job, number, url, latest, download):
    set_debug_log_level(debug)
    if job or url:
        cli_build.log(profile, job, number, url, latest, download)
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
    # TODO: Pass a list of build numbers
    set_debug_log_level(debug)
    if job or url:
        cli_build.browser(profile, job, number, url, latest)
    else:
        click.echo(ctx.get_help())

@build.command(short_help='\tMonitor UI')
@cli_decorators.debug
@cli_decorators.profile
@click.argument('job', nargs=1, type=str, required=False)
@click.option('-n', '--number', type=int, required=False, help='Build number')
@click.option('-u', '--url', type=str, required=False, help='Build URL (No job info needed)')
@click.option('--latest', type=str, required=False, is_flag=True, help='Latest build (Replaces --number)')
@click.pass_context
def monitor(ctx, debug, profile, job, number, url, latest):
    # TODO: Pass a list of build numbers
    set_debug_log_level(debug)
    if job or url:
        cli_build.monitor(profile, job, number, url, latest)
    else:
        click.echo(ctx.get_help())

# TODO:
#   - Build test report



##############################################################################
#                             STAGE
##############################################################################
@main.group(short_help='\tManage build stages')
def stage():
    """Top level CLI menu: stage"""
    pass

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
def info(ctx, debug, pretty, yaml, xml, profile, name, job, number, url, latest):
    set_debug_log_level(debug)
    if job or url:
        cli_stage.info(pretty, yaml, xml, profile, name, job, number, url, latest)
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
def steps(ctx, debug, pretty, yaml, xml, profile, list, name, job, number, url, latest):
    set_debug_log_level(debug)
    if job or url:
        cli_stage.steps(pretty, yaml, xml, profile, list, name, job, number, url, latest)
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
@click.option('-d', '--download', type=str, required=False, is_flag=True, help='Download the logs')
@click.pass_context
def log(ctx, debug, profile, name, job, number, url, latest, download):
    set_debug_log_level(debug)
    if job or url:
        cli_stage.log(profile, name, job, number, url, latest, download)
    else:
        click.echo(ctx.get_help())



##############################################################################
#                             STEP
##############################################################################
@main.group(short_help='\tManage stage steps')
def step():
    """Top level CLI menu: step"""
    pass

@step.command(short_help='\tStep information')
@cli_decorators.debug
@cli_decorators.format_output
@cli_decorators.profile
@click.argument('url', nargs=1, type=str, required=True)
@click.pass_context
def info(ctx, debug, pretty, yaml, xml, profile, url):
    set_debug_log_level(debug)
    if job or url:
        cli_step.info(pretty, yaml, xml, profile, url)
    else:
        click.echo(ctx.get_help())



##############################################################################
##############################################################################
##############################################################################
if __name__ == "__main__":
    """Main entry point to the entire program

    Details: This file and this function will be called when running the CLI command

    Args:
        None

    Returns:
        None
    """
    try:
        main()
    except Exception as e:
        click.echo(click.style(f"Uh-Oh, something is not right. yo-jenkins crashed!\n", fg='red'))

        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]

        click.echo(click.style(f"  - ERROR:   {e}", fg='red'))
        click.echo(click.style(f"  - TYPE:    {exc_type}", fg='red'))
        click.echo(click.style(f"  - FILE:    {fname}", fg='red'))
        click.echo(click.style(f"  - LINE:    {exc_tb.tb_lineno}\n", fg='red'))

