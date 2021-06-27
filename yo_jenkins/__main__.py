#!/usr/bin/env python3

import logging
from pprint import pprint
import sys

import click

from yo_jenkins import __version__
from yo_jenkins.cli import logger_setup
from yo_jenkins.cli import (cli_auth, cli_build, cli_decorators, cli_folder, cli_job, cli_server, cli_stage, cli_step)
from yo_jenkins.cli.cli_utility import set_debug_log_level

logger = logging.getLogger()

if sys.version_info < (3, 7):
    click.echo(click.style('Your Python version ({}.{}) is not supported'.format(sys.version_info.major, sys.version_info.minor), fg='bright_red', bold=True))
    click.echo(click.style('Must have Python 3.7 or higher', fg='bright_red', bold=True))
    sys.exit(1)

##############################################################################

MAIN_HELP_TEXT = f"""
    \t\t\t \033[93m YO-JENKINS (Version: {__version__}) \033[0m

    yo-jenkins is a tool that is focused on interfacing with
    Jenkins server from the comfort of the beloved command line. 
    This tool can also be used as a middleware utility, generating and
    passing Jenkins information or automating tasks.

    QUICK START:

        1. Configure yo profile:  yo-jenkins auth configure

        2. Add yo API token:      yo-jenkins auth token --profile <PROFILE>

        3. Verify yo creds:       yo-jenkins auth verify

        4. Explore yo-jenkins
"""

##############################################################################


@click.group(help=MAIN_HELP_TEXT)
@click.version_option(__version__,
                      "-v",
                      "--version",
                      message="%(version)s".format(version="version"),
                      help="Show the version")
def main():
    pass


##############################################################################
#                             AUTHENTICATE
##############################################################################


@main.group(short_help='\tManage authentication and profiles')
def auth():
    """
    AUTHENTICATION AND PROFILE MANAGEMENT
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
def show(debug, pretty, yaml, xml, toml):
    set_debug_log_level(debug)
    cli_auth.show(pretty, yaml, xml, toml)


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
    click.echo(click.style(
        'TODO',
        fg='yellow',
    ))


@auth.command(short_help='\tShow current user information')
@cli_decorators.debug
@cli_decorators.format_output
@cli_decorators.profile
def user(debug, pretty, yaml, xml, toml, profile):
    set_debug_log_level(debug)
    cli_auth.user(pretty, yaml, xml, toml, profile)


##############################################################################
#                             SERVER
##############################################################################
@main.group(short_help='\tManage server')
def server():
    """SERVER MANAGEMENT"""
    pass


@server.command(short_help='\tServer information')
@cli_decorators.debug
@cli_decorators.format_output
@cli_decorators.profile
def info(debug, pretty, yaml, toml, xml, profile):
    set_debug_log_level(debug)
    cli_server.info(pretty, yaml, xml, toml, profile)


@server.command(short_help='\tShow all people/users on server')
@cli_decorators.debug
@cli_decorators.format_output
@cli_decorators.profile
@cli_decorators.list
def people(debug, pretty, yaml, xml, toml, profile, list):
    set_debug_log_level(debug)
    cli_server.people(pretty, yaml, xml, toml, profile, list)


@server.command(short_help='\tShow current job build queues on server')
@cli_decorators.debug
@cli_decorators.format_output
@cli_decorators.profile
@cli_decorators.list
def queue(debug, pretty, yaml, xml, toml, profile, list):
    set_debug_log_level(debug)
    cli_server.queue(pretty, yaml, xml, toml, profile, list)
    # NOTE: Maybe move to "job"?


@server.command(short_help='\tShow plugin information')
@cli_decorators.debug
@cli_decorators.format_output
@cli_decorators.profile
@cli_decorators.list
def plugins(debug, pretty, yaml, xml, toml, profile, list):
    set_debug_log_level(debug)
    cli_server.plugins(pretty, yaml, xml, toml, profile, list)


@server.command(short_help='\tOpen server home page in web browser')
@cli_decorators.debug
@cli_decorators.profile
def browser(debug, profile):
    set_debug_log_level(debug)
    cli_server.browser(profile)


@server.command(short_help='\tCheck if server is reachable')
@cli_decorators.debug
@cli_decorators.profile
@click.option('--timeout', type=int, default=10, required=False, is_flag=False, help='Request timeout value')
def reachable(debug, profile, timeout):
    set_debug_log_level(debug)
    cli_server.reachable(profile, timeout)


@server.command(short_help='\tServer quite mode enable/disable')
@cli_decorators.debug
@cli_decorators.profile
@click.option('--off', type=bool, default=False, required=False, is_flag=True, help='Undo quiet down mode')
def quiet(debug, profile, off):
    """
    NOTE: A server with quiet mode enabled does not allow any new jobs to be build.
    This may be needed prior to server maintenance, restarts, or shutdowns
    """
    set_debug_log_level(debug)
    cli_server.quiet(profile, off)












@server.command(short_help='\tRestart the server')
@cli_decorators.debug
@cli_decorators.profile
@click.option('--force',
              type=bool,
              default=False,
              required=False,
              is_flag=True,
              help='Force restart. Without initial quiet mode.')
def restart(debug, profile, force):
    """
    NOTE: By default this will put Jenkins into the quiet mode, wait for existing builds to be completed, and then restart Jenkins.
    Use --force to skip quiet mode.
    """
    set_debug_log_level(debug)
    cli_server.restart(profile, force)


@server.command(short_help='\tShut down the server')
@cli_decorators.debug
@cli_decorators.profile
@click.option('--force',
              type=bool,
              default=False,
              required=False,
              is_flag=True,
              help='Force shutdown. Without initial quiet mode')
def shutdown(debug, profile, force):
    """
    NOTE: By default this will put Jenkins in a quiet mode, in preparation for a shutdown.
    In that mode Jenkins does not start any new builds.
    Use --force to skip quiet mode.
    """
    set_debug_log_level(debug)
    cli_server.shutdown(profile, force)


@server.command(short_help='\tCreate a local development server using Docker')
@cli_decorators.debug
@click.option('--config-file',
              default='config_as_code.yaml',
              type=click.Path(file_okay=True, dir_okay=False),
              required=False,
              help='.yml/.yaml file for custom configuration as code for Jenkins server setup')
@click.option('--plugins-file',
              default='plugins.txt',
              type=click.Path(file_okay=True, dir_okay=False),
              required=False,
              help='.txt file for custom list of all plugins to be installed on Jenkins server')
@click.option('--protocol-schema',
              default='http',
              type=str,
              required=False,
              help='Protocol schema for Jenkins, http, https, etc.')
@click.option('--host',
              default='localhost',
              type=str,
              required=False,
              help='Jenkins server host (localhost, 192.168.0.1, etc.)')
@click.option('--port', default=8080, type=int, required=False, help='Jenkins server port')
@click.option('--image-base',
              default='jenkins/jenkins',
              type=str,
              required=False,
              help='Base Jenkins server image (default: jenkins/jenkins)')
@click.option('--image-rebuild',
              default=False,
              type=bool,
              required=False,
              is_flag=True,
              help='If image exists, rebuild existing docker image')
@click.option('--new-volume',
              default=False,
              type=bool,
              required=False,
              is_flag=True,
              help='Erase existing Docker data volume from previously created servers (default: off)')
@click.option('--new-volume-name',
              default='yo-jenkins-jenkins',
              type=str,
              required=False,
              help='Name of the resulting Docker volume')
@click.option('--bind-mount-dir',
              default='',
              type=click.Path(file_okay=False, dir_okay=True),
              required=False,
              help='Path of local directory to be bound inside container "/tmp/my_things" directory')
@click.option('--container-name',
              default='yo-jenkins-jenkins',
              type=str,
              required=False,
              help='Name of the resulting Docker container')
@click.option('--registry', default='', type=str, required=False, help='Registry to pull base Jenkins image from')
@click.option('--admin-user', default='admin', type=str, required=False, help='Set username of admin (default: admin)')
@click.option('--password',
              default='',
              type=str,
              required=False,
              help='Set password for admin account (default: password)')
def server_deploy(debug, config_file, plugins_file, protocol_schema, host, port, image_base, image_rebuild, new_volume,
                  new_volume_name, bind_mount_dir, container_name, registry, admin_user, password):
    """ATTENTION: The resulting Jenkins server is for development and testing purposes only. Enjoy responsibly.
    
    NOTE: Docker must be installed for this command to function

    BTW: All options have default values and command can be run without any specified options
    """
    set_debug_log_level(debug)
    cli_server.server_deploy(config_file, plugins_file, protocol_schema, host, port, image_base, image_rebuild,
                             new_volume, new_volume_name, bind_mount_dir, container_name, registry, admin_user,
                             password)


@server.command(short_help='\tRemove a local development server')
@click.option('--remove-volume',
              default=False,
              type=bool,
              required=False,
              is_flag=True,
              help='Also remove the Docker volume used for current server (default: off)')
@click.option('--remove-image',
              default=False,
              type=bool,
              required=False,
              is_flag=True,
              help='Also remove the Docker image used for current server (default: off)')
@cli_decorators.debug
def server_teardown(debug, remove_volume, remove_image):
    set_debug_log_level(debug)
    cli_server.server_teardown(remove_volume, remove_image)


# @server.command(short_help='\tCheck if a locally deployed development server is running')
# @cli_decorators.debug
# def server_check(debug):
#     set_debug_log_level(debug)
#     click.echo(click.style('TODO', fg='yellow',))


##############################################################################
#                             NODE
##############################################################################
@main.group(short_help='\tManage nodes')
def node():
    """NODE MANAGEMENT"""
    pass


@node.command(short_help='\tServer information')
@cli_decorators.debug
@cli_decorators.profile
def info(debug, profile):
    set_debug_log_level(debug)
    click.echo(click.style(
        'TODO',
        fg='yellow',
    ))


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
    """FOLDER MANAGEMENT"""
    pass


@folder.command(short_help='\tFolder information')
@cli_decorators.debug
@cli_decorators.format_output
@cli_decorators.profile
@click.argument('folder', nargs=1, type=str, required=True)
def info(debug, pretty, yaml, xml, toml, profile, folder):
    set_debug_log_level(debug)
    cli_folder.info(pretty, yaml, xml, toml, profile, folder)


@folder.command(short_help='\tSearch folders by REGEX pattern')
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
              help='Search entire folder path name')
@cli_decorators.list
def search(debug, pretty, yaml, xml, toml, profile, search_pattern, search_folder, depth, fullname, list):
    set_debug_log_level(debug)
    cli_folder.search(pretty, yaml, xml, toml, profile, search_pattern, search_folder, depth, fullname, list)


@folder.command(short_help='\tList all subfolders in folder')
@cli_decorators.debug
@cli_decorators.format_output
@cli_decorators.profile
@click.argument('folder', nargs=1, type=str, required=True)
def subfolders(debug, pretty, yaml, xml, toml, profile, folder, list):
    set_debug_log_level(debug)
    cli_folder.subfolders(pretty, yaml, xml, toml, profile, folder, list)


@folder.command(short_help='\tList all jobs in folder')
@cli_decorators.debug
@cli_decorators.format_output
@cli_decorators.profile
@click.argument('folder', nargs=1, type=str, required=True)
@cli_decorators.list
def jobs(debug, pretty, yaml, xml, toml, profile, folder, list):
    set_debug_log_level(debug)
    cli_folder.jobs(pretty, yaml, xml, toml, profile, folder, list)


@folder.command(short_help='\tList all views in folder')
@cli_decorators.debug
@cli_decorators.format_output
@cli_decorators.profile
@click.argument('folder', nargs=1, type=str, required=True)
@cli_decorators.list
def views(debug, pretty, yaml, xml, toml, profile, folder, list):
    set_debug_log_level(debug)
    cli_folder.views(pretty, yaml, xml, toml, profile, folder, list)


@folder.command(short_help='\tList all items in folder')
@cli_decorators.debug
@cli_decorators.format_output
@cli_decorators.profile
@click.argument('folder', nargs=1, type=str, required=True)
@cli_decorators.list
def items(debug, pretty, yaml, xml, toml, profile, folder, list):
    set_debug_log_level(debug)
    cli_folder.items(pretty, yaml, xml, toml, profile, folder, list)


@folder.command(short_help='\tOpen folder in web browser')
@cli_decorators.debug
@cli_decorators.profile
@click.argument('folder', nargs=1, type=str, required=True)
def browser(debug, profile, folder):
    set_debug_log_level(debug)
    cli_folder.browser(profile, folder)


@folder.command(short_help='\tFolder XML configuration')
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
@click.argument('folder', nargs=1, type=str, required=True)
@click.option('--filepath',
              type=click.Path(file_okay=True, dir_okay=True),
              required=False,
              help='File/Filepath to write configurations to')
def config(debug, pretty, yaml, xml, toml, json, profile, folder, filepath):
    set_debug_log_level(debug)
    cli_folder.config(pretty, yaml, xml, toml, json, profile, folder, filepath)


@folder.command(short_help='\tCreate an item (folder, view, job)')
@cli_decorators.debug
@cli_decorators.profile
@click.argument('name', nargs=1, type=str, required=True)
@click.argument('folder', nargs=1, type=str, required=True)
@click.option('--type',
              type=click.Choice(['folder', 'view', 'job'], case_sensitive=False),
              default='folder',
              required=False,
              help='Item type created [default: folder]')
@click.option('-cf',
              '--config-file',
              type=click.Path(file_okay=True, dir_okay=False),
              required=False,
              help='Path to local XML file defining item')
def create(debug, profile, name, folder, type, config_file):
    set_debug_log_level(debug)
    cli_folder.create(profile, name, folder, type, config_file)


@folder.command(short_help='\tCopy an existing item')
@cli_decorators.debug
@cli_decorators.profile
@click.argument('folder', nargs=1, type=str, required=True)
@click.argument('original', nargs=1, type=str, required=True)
@click.argument('new', nargs=1, type=str, required=True)
def copy(debug, profile, folder, original, new):
    set_debug_log_level(debug)
    cli_folder.copy(profile, folder, original, new)


@folder.command(short_help='\tDelete folder or view')
@cli_decorators.debug
@cli_decorators.profile
@click.argument('folder', nargs=1, type=str, required=True)
def delete(debug, profile, folder):
    set_debug_log_level(debug)
    cli_folder.delete(profile, folder)


##############################################################################
#                             JOB
##############################################################################
@main.group(short_help='\tManage jobs')
def job():
    """JOB MANAGEMENT"""
    pass


@job.command(short_help='\tJob information')
@cli_decorators.debug
@cli_decorators.format_output
@cli_decorators.profile
@click.argument('job', nargs=1, type=str, required=True)
def info(debug, pretty, yaml, xml, toml, profile, job):
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
    set_debug_log_level(debug)
    cli_job.search(pretty, yaml, xml, toml, profile, search_pattern, search_folder, depth, fullname, list)


@job.command(short_help='\tList all builds for job')
@cli_decorators.debug
@cli_decorators.format_output
@cli_decorators.profile
@click.argument('job', nargs=1, type=str, required=True)
@cli_decorators.list
def list(debug, pretty, yaml, xml, toml, profile, job, list):
    set_debug_log_level(debug)
    cli_job.build_list(pretty, yaml, xml, toml, profile, job, list)


@job.command(short_help='\tGet next build number')
@cli_decorators.debug
@cli_decorators.profile
@click.argument('job', nargs=1, type=str, required=True)
def next(debug, profile, job):
    set_debug_log_level(debug)
    cli_job.build_next(profile, job)


@job.command(short_help='\tGet previous build number')
@cli_decorators.debug
@cli_decorators.profile
@click.argument('job', nargs=1, type=str, required=True)
def last(debug, profile, job):
    set_debug_log_level(debug)
    cli_job.build_last(profile, job)


@job.command(short_help='\tSet the next build number')
@cli_decorators.debug
@cli_decorators.profile
@click.argument('job', nargs=1, type=str, required=True)
@click.argument('build_number', nargs=1, type=int, required=True)
def set(debug, profile, job, build_number):
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
@click.option('-p',
              '--parameter',
              nargs=2,
              multiple=True,
              required=False,
              help='Specify key-value parameter. Can use multiple times. Use once per parameter')
def build(debug, profile, job, parameter):
    set_debug_log_level(debug)
    cli_job.build(profile, job, parameter)


@job.command(short_help='\tCheck if this job is in queue')
@cli_decorators.debug
@cli_decorators.format_output
@cli_decorators.profile
@click.argument('job', nargs=1, type=str, required=True)
@click.option('-i', '--id', type=bool, default=False, required=False, is_flag=True, help='Only output queue ID')
def queue_check(debug, pretty, yaml, xml, toml, profile, job, id):
    set_debug_log_level(debug)
    cli_job.queue_check(pretty, yaml, xml, toml, profile, job, id)


@job.command(short_help='\tCancel this job in queue')
@cli_decorators.debug
@cli_decorators.profile
@click.option('-i', '--id', type=int, default=False, required=True, help='Queue ID')
def queue_cancel(debug, profile, id):
    set_debug_log_level(debug)
    # cli_job.queue_cancel(profile, id)
    click.echo(click.style(
        'TODO',
        fg='yellow',
    ))


@job.command(short_help='\tOpen job in web browser')
@cli_decorators.debug
@cli_decorators.profile
@click.argument('job', nargs=1, type=str, required=True)
def browser(debug, profile, job):
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
    set_debug_log_level(debug)
    cli_job.config(pretty, yaml, xml, toml, json, profile, job, filepath)


@job.command(short_help='\tDisable job')
@cli_decorators.debug
@cli_decorators.profile
@click.argument('job', nargs=1, type=str, required=True)
def disable(debug, profile, job):
    set_debug_log_level(debug)
    cli_job.disable(profile, job)


@job.command(short_help='\tEnable job')
@cli_decorators.debug
@cli_decorators.profile
@click.argument('job', nargs=1, type=str, required=True)
def enable(debug, profile, job):
    set_debug_log_level(debug)
    cli_job.enable(profile, job)


@job.command(short_help='\tRename job')
@cli_decorators.debug
@cli_decorators.profile
@click.argument('job', nargs=1, type=str, required=True)
@click.argument('name', nargs=1, type=str, required=True)
def rename(debug, profile, job, name):
    set_debug_log_level(debug)
    cli_job.rename(profile, job, name)


@job.command(short_help='\tDelete job')
@cli_decorators.debug
@cli_decorators.profile
@click.argument('job', nargs=1, type=str, required=True)
def delete(debug, profile, job):
    set_debug_log_level(debug)
    cli_job.delete(profile, job)


@job.command(short_help='\tWipe job workspace')
@cli_decorators.debug
@cli_decorators.profile
@click.argument('job', nargs=1, type=str, required=True)
def wipe(debug, profile, job):
    set_debug_log_level(debug)
    cli_job.wipe(profile, job)


@job.command(short_help='\tStart monitor UI')
@cli_decorators.debug
@cli_decorators.profile
@click.argument('job', nargs=1, type=str, required=False)
@click.option('-s', '--sound', type=bool, required=False, is_flag=True, help='Enable sound effects')
def monitor(debug, profile, job, sound):
    set_debug_log_level(debug)
    cli_job.monitor(profile, job, sound)


@job.command(short_help='\tCreate a job')
@cli_decorators.debug
@cli_decorators.profile
@click.argument('name', nargs=1, type=str, required=True)
@click.argument('folder', nargs=1, type=str, required=True)
@click.option('--config',
              default='',
              type=click.Path(file_okay=True, dir_okay=False),
              required=False,
              help='Config file defining the job')
def create(debug, profile, name, folder, config):
    set_debug_log_level(debug)
    cli_job.create(profile, name, folder, config)


##############################################################################
#                             BUILD
##############################################################################
@main.group(short_help='\tManage builds')
def build():
    """BUILD MANAGEMENT"""
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
def info(ctx, debug, pretty, yaml, xml, toml, profile, job, number, url, latest):
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
def stages(ctx, debug, pretty, yaml, xml, toml, profile, list, job, number, url, latest):
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
    # TODO: Pass a list of build numbers
    set_debug_log_level(debug)
    if job or url:
        cli_build.monitor(profile, job, number, url, latest, sound)
    else:
        click.echo(ctx.get_help())


# TODO:
#   - Build test report


##############################################################################
#                             STAGE
##############################################################################
@main.group(short_help='\tManage build stages')
def stage():
    """STAGE MANAGEMENT"""
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
def info(ctx, debug, pretty, yaml, xml, toml, profile, name, job, number, url, latest):
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
    set_debug_log_level(debug)
    if job or url:
        cli_stage.logs(profile, name, job, number, url, latest, download_dir)
    else:
        click.echo(ctx.get_help())


##############################################################################
#                             STEP
##############################################################################
@main.group(short_help='\tManage stage steps')
def step():
    """STEP MANAGEMENT"""
    pass


@step.command(short_help='\tStep information')
@cli_decorators.debug
@cli_decorators.format_output
@cli_decorators.profile
@click.argument('url', nargs=1, type=str, required=True)
@click.pass_context
def info(ctx, debug, pretty, yaml, xml, toml, profile, url):
    set_debug_log_level(debug)
    if job or url:
        cli_step.info(pretty, yaml, xml, toml, profile, url)
    else:
        click.echo(ctx.get_help())


##############################################################################
#                             UTILITY
##############################################################################
@main.group(short_help='\tUtility and more')
def utility():
    """UTILITY AND MORE"""
    pass

@utility.command(short_help='\tShow the manual')
@cli_decorators.debug
def manual(ctx, debug):
    set_debug_log_level(debug)
    click.echo(click.style('TODO', fg='yellow',))


@utility.command(short_help='\tUpdate yo-jenkins')
@cli_decorators.debug
def update(ctx, debug):
    set_debug_log_level(debug)
    click.echo(click.style('TODO', fg='yellow',))

@utility.command(short_help='\tReport a bug')
@cli_decorators.debug
def bug_report(ctx, debug):
    set_debug_log_level(debug)
    click.echo(click.style('TODO', fg='yellow',))

@utility.command(short_help='\tRequest a feature')
@cli_decorators.debug
def feature_request(ctx, debug):
    set_debug_log_level(debug)
    click.echo(click.style('TODO', fg='yellow',))

@utility.command(short_help='\tShow the command history for each profile')
@cli_decorators.debug
@cli_decorators.profile
def history(ctx, debug, profile):
    set_debug_log_level(debug)
    click.echo(click.style('TODO', fg='yellow',))

@utility.command(short_help='\tSend a generic REST request to server')
@cli_decorators.debug
@cli_decorators.profile
def rest_request(ctx, debug, profile):
    set_debug_log_level(debug)
    click.echo(click.style('TODO', fg='yellow',))




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
    # try:
    main()
    # except Exception as e:
    #     click.echo(click.style(f"Uh-Oh, something is not right. yo-jenkins crashed!\n", fg='red'))

    #     exc_type, exc_obj, exc_tb = sys.exc_info()
    #     fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]

    #     click.echo(click.style(f"  - ERROR:   {e}", fg='red'))
    #     click.echo(click.style(f"  - TYPE:    {exc_type}", fg='red'))
    #     click.echo(click.style(f"  - FILE:    {fname}", fg='red'))
    #     click.echo(click.style(f"  - LINE:    {exc_tb.tb_lineno}\n", fg='red'))
