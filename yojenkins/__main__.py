"""Main entry point for program"""
# pylint: skip-file

import logging
import sys

import click
from click_help_colors import HelpColorsCommand, HelpColorsGroup

from yojenkins import __version__
from yojenkins.cli import logger_setup  # Keep this line, sets up logger
from yojenkins.cli import (
    cli_account,
    cli_auth,
    cli_build,
    cli_credential,
    cli_decorators,
    cli_folder,
    cli_job,
    cli_node,
    cli_server,
    cli_stage,
    cli_step,
    cli_tools,
)
from yojenkins.cli.cli_utility import set_debug_log_level

logger = logging.getLogger()

if sys.version_info < (3, 7):
    click.echo(click.style('Your Python version ({}.{}) is not supported'.format(sys.version_info.major, sys.version_info.minor), fg='bright_red', bold=True))
    click.echo(click.style('Must have Python 3.7 or higher', fg='bright_red', bold=True))
    sys.exit(1)

##############################################################################


MAIN_HELP_TEXT = f"""
    \t\t\t \033[93m YOJENKINS (Version: {__version__}) \033[0m

    yojenkins is a tool that is focused on interfacing with
    Jenkins server from the comfort of the beloved command line.
    This tool can also be used as a middleware utility, generating and
    passing Jenkins information or automating tasks.

    QUICK START:

    \b
      1. Configure yo profile:  yojenkins auth configure
      2. Add yo API token:      yojenkins auth token --profile <PROFILE NAME>
      3. Verify yo creds:       yojenkins auth verify
      4. Explore yojenkins
"""


##############################################################################


@click.group(help=MAIN_HELP_TEXT)
@click.version_option(
    __version__, "-v", "--version", message="%(version)s".format(version="version"),
    help="Show the version"
)
def main():
    pass


##############################################################################
#                             AUTHENTICATE
##############################################################################

@main.group(short_help='\tManage authentication and profiles',
    cls=HelpColorsGroup,
    help_options_custom_colors={
        'wipe': 'black'
        })
def auth():
    """
    AUTHENTICATION AND PROFILE MANAGEMENT
    """
    pass

@auth.command(short_help='\tConfigure authentication', cls=HelpColorsCommand, help_options_custom_colors={'--token': 'black'})
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

@auth.command(short_help='\tShow the local credentials profiles')
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
    click.echo(click.style('TODO :-/', fg='yellow',))

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
@click.option('--force', type=bool, default=False, required=False, is_flag=True, help='Force restart. Without initial quiet mode.')
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
@click.option('--force', type=bool, default=False, required=False, is_flag=True, help='Force shutdown. Without initial quiet mode')
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
@click.option('--config-file', default='config_as_code.yaml', type=click.Path(file_okay=True, dir_okay=False), required=False, help='.yml/.yaml file for custom configuration as code for Jenkins server setup')
@click.option('--plugins-file', default='plugins.txt', type=click.Path(file_okay=True, dir_okay=False), required=False, help='.txt file for custom list of all plugins to be installed on Jenkins server')
@click.option('--protocol-schema', default='http', type=str, required=False, help='Protocol schema for Jenkins, http, https, etc.')
@click.option('--host', default='localhost', type=str, required=False, help='Jenkins server host (localhost, 192.168.0.1, etc.)')
@click.option('--port', default=8080, type=int, required=False, help='Jenkins server port')
@click.option('--image-base', default='jenkins/jenkins', show_default=True, type=str, required=False, help='Base Jenkins server image')
@click.option('--image-rebuild', default=False, type=bool, required=False, is_flag=True, help='If image exists, rebuild existing docker image')
@click.option('--new-volume', default=False, show_default=True, type=bool, required=False, is_flag=True, help='Erase existing Docker data volume from previously created servers')
@click.option('--new-volume-name', default='yojenkins-jenkins', type=str, required=False, help='Name of the resulting Docker volume')
@click.option('--bind-mount-dir', default='', type=click.Path(file_okay=False, dir_okay=True), required=False, help='Path of local directory to be bound inside container "/tmp/my_things" directory')
@click.option('--container-name', default='yojenkins-jenkins', type=str, required=False, help='Name of the resulting Docker container')
@click.option('--registry', default='', type=str, required=False, help='Registry to pull base Jenkins image from')
@click.option('--admin-user', default='admin', show_default=True, type=str, required=False, help='Set username of admin')
@click.option('--password', default='', type=str, required=False, help='Set password for admin account [default: password]')
def server_deploy(debug, config_file, plugins_file, protocol_schema, host, port, image_base, image_rebuild, new_volume, new_volume_name, bind_mount_dir, container_name, registry, admin_user, password):
    """ATTENTION: The resulting Jenkins server is for development and testing purposes only. Enjoy responsibly.

    NOTE: Docker must be installed for this command to function

    BTW: All options have default values and command can be run without any specified options
    """
    set_debug_log_level(debug)
    cli_server.server_deploy(config_file, plugins_file, protocol_schema, host, port, image_base, image_rebuild, new_volume, new_volume_name, bind_mount_dir, container_name, registry, admin_user, password)

@server.command(short_help='\tRemove a local development server')
@click.option('--remove-volume', default=False, show_default=True, type=bool, required=False, is_flag=True, help='Also remove the Docker volume used for current server')
@click.option('--remove-image', default=False, show_default=True, type=bool, required=False, is_flag=True, help='Also remove the Docker image used for current server')
@cli_decorators.debug
def server_teardown(debug, remove_volume, remove_image):
    set_debug_log_level(debug)
    cli_server.server_teardown(remove_volume, remove_image)

# @server.command(short_help='\tCheck if a locally deployed development server is running')
# @cli_decorators.debug
# def server_check(debug):
#     set_debug_log_level(debug)
#     click.echo(click.style('TODO :-/', fg='yellow',))



##############################################################################
#                             NODE
##############################################################################
@main.group(short_help='\tManage nodes',
    cls=HelpColorsGroup,
    help_options_custom_colors={
        'prepare': 'black',
        'status': 'black',
        'create-ephemeral': 'black',
        'logs': 'black',
        })
def node():
    """NODE MANAGEMENT"""
    pass

@node.command(short_help='\tNode information')
@cli_decorators.debug
@cli_decorators.format_output
@cli_decorators.profile
@click.argument('name', nargs=1, type=str, required=True)
@click.option('-d', '--depth', type=int, default=0, required=False, help='Search depth from root directory')
def info(debug, pretty, yaml, xml, toml, profile, name, depth):
    set_debug_log_level(debug)
    cli_node.info(pretty, yaml, xml, toml, profile, name, depth)

@node.command(short_help='\tNode status')
@cli_decorators.debug
@cli_decorators.profile
@click.argument('name', nargs=1, type=str, required=True)
def status(debug, profile, name):
    set_debug_log_level(debug)
    click.echo(click.style('TODO :-/', fg='yellow',))

@node.command(short_help='\tList all all nodes')
@cli_decorators.debug
@cli_decorators.profile
@cli_decorators.format_output
@cli_decorators.list
@click.option('-d', '--depth', type=int, default=0, required=False, help='Search depth from root directory')
def list(debug, profile, pretty, yaml, xml, toml, list, depth):
    set_debug_log_level(debug)
    cli_node.list(pretty, yaml, xml, toml, list, profile, depth)

@node.command(short_help='\tPrepare a remote machine to become a node')
@cli_decorators.debug
def prepare(debug):
    set_debug_log_level(debug)
    cli_node.prepare()

@node.command(short_help='\tSetup a local or remote persistant node')
@cli_decorators.debug
@cli_decorators.profile
@click.argument('name', nargs=1, type=str, required=True)
@click.argument('host', nargs=1, type=str, required=True)
@click.argument('credential', nargs=1, type=str, required=True)
@click.option('--description', type=str, required=False, help='Node description')
@click.option('--executors', default=1, type=click.IntRange(1, 100), required=False, show_default=True, help='Number of executors on node')
@click.option('--labels', type=str, required=False, help='Labels applied to agent [default: NAME]')
@click.option('--mode', type=click.Choice(['normal', 'exclusive'], case_sensitive=False), default='normal', show_default=True, required=False, help='Available to all or to specified jobs')
@click.option('--remote-java-dir', default="/usr/bin/java", show_default=True, type=str, required=False, help='Location of Java binary')
@click.option('--remote-root-dir', default="/home/jenkins", show_default=True, type=str, required=False, help='Directory where node work is kept')
@click.option('--retention', type=click.Choice(['always', 'demand'], case_sensitive=False), default='always', show_default=True, required=False, help='Always on or offline when not in use')
@click.option('--ssh-port', default=22, show_default=True, type=click.IntRange(1, 64738), required=False, help='SSH port to target')
@click.option('--ssh-verify', type=click.Choice(['known', 'trusted', 'none'], case_sensitive=False), default='trusted', show_default=True, required=False, help='SSH verification strategy')
# @click.option('--config-file', type=click.Path(file_okay=True, dir_okay=False), required=False, help='Path to local XML file defining agent')
def create_permanent(debug, profile, **kwargs):
    """
    This command sets up a local or remote node on a virtual machine, container,
    or physical machine, connecting with SSH. The target system must have the following:

    \b
    - A working SSH server installed, running, and accessible form main server
    - Java installed

    This command only sets the node up, but it does not monitor to see if the agent
    has successfully connected. You will either need to manually check the node in the Jenkins UI,
    or you can use: "yojenkins node status NAME"

    ARGUMENTS:

    \b
      NAME:        Name of the node
      HOST:        Hostname or IP address of the node
      CREDENTIAL:  SSH type credential in Jenkins

    EXAMPLES:

    \b
    - yojenkins node create-permanent my-node 192.168.0.23 my-cred --description "Yo new node"
    - yojenkins node create-permanent my-node 192.168.0.23 15ad1f93-dc24-4f71-b92b-18ae9b13b1d0
    - yojenkins node create-permanent "Node 1" ey-yo.com my-cred --labels label1,label2,label3
    """
    set_debug_log_level(debug)
    cli_node.create_permanent(profile, **kwargs)

@node.command(short_help='\tSetup a local or remote ephemeral/as-needed node')
@cli_decorators.debug
def create_ephemeral(debug):
    set_debug_log_level(debug)
    click.echo(click.style('TODO :-/', fg='yellow',))

@node.command(short_help='\tDelete a node')
@cli_decorators.debug
@cli_decorators.profile
@click.argument('name', nargs=1, type=str, required=True)
def delete(debug, profile, name):
    set_debug_log_level(debug)
    cli_node.delete(profile, name)

@node.command(short_help='\tDisable a node')
@cli_decorators.debug
@cli_decorators.profile
@click.argument('name', nargs=1, type=str, required=True)
@click.option('--message', type=str, required=False, help='Message for disabling node')
def disable(debug, profile, name, message):
    set_debug_log_level(debug)
    cli_node.disable(profile, name, message)

@node.command(short_help='\tEnable a node')
@cli_decorators.debug
@cli_decorators.profile
@click.argument('name', nargs=1, type=str, required=True)
@click.option('--message', type=str, required=False, help='Message for enabling node')
def enable(debug, profile, name, message):
    set_debug_log_level(debug)
    cli_node.enable(profile, name, message)

@node.command(short_help='\tGet node configuration')
@cli_decorators.debug
@cli_decorators.format_output
@click.option('-j', '--json', type=bool, default=False, required=False, is_flag=True, help='Output config in JSON format')
@cli_decorators.profile
@click.argument('name', nargs=1, type=str, required=True)
@click.option('--filepath', type=click.Path(file_okay=True, dir_okay=True), required=False, help='File/Filepath to write configurations to')
def config(debug, pretty, yaml, xml, toml, json, profile, name, filepath):
    set_debug_log_level(debug)
    cli_node.config(pretty, yaml, xml, toml, json, profile, name, filepath)

@node.command(short_help='\tReconfigure the node')
@cli_decorators.debug
@cli_decorators.profile
@click.argument('name', nargs=1, type=str, required=True)
@click.option('--config-file', type=click.Path(file_okay=True, dir_okay=True), required=True, help='Path to local config file defining node')
@click.option('--config-is-json', type=bool, default=False, show_default=True, required=False, is_flag=True, help='The specified file is in JSON format')
def reconfig(debug, profile, name, config_file, config_is_json):
    set_debug_log_level(debug)
    cli_node.reconfig(profile, name, config_file, config_is_json)

@node.command(short_help='\tNode logs')
@cli_decorators.debug
@cli_decorators.profile
def logs(debug, profile):
    set_debug_log_level(debug)
    click.echo(click.style('TODO :-/', fg='yellow',))



##############################################################################
#                             ACCOUNT
##############################################################################
@main.group(short_help='\tManage user accounts',
cls=HelpColorsGroup,
    help_options_custom_colors={
        'password-reset': 'black',
        })
def account():
    """ACCOUNT MANAGEMENT"""
    pass

@account.command(short_help='\tList all users')
@cli_decorators.debug
@cli_decorators.format_output
@cli_decorators.list
@cli_decorators.profile
def list(debug, pretty, yaml, xml, toml, list, profile):
    set_debug_log_level(debug)
    cli_account.list(pretty, yaml, xml, toml, list, profile)

@account.command(short_help='\tGet user information')
@cli_decorators.debug
@cli_decorators.format_output
@cli_decorators.profile
@click.argument('user-id', nargs=1, type=str, required=True)
def info(debug, pretty, yaml, xml, toml, profile, user_id):
    set_debug_log_level(debug)
    cli_account.info(pretty, yaml, xml, toml, profile, user_id)

@account.command(short_help='\tCreate a user account')
@cli_decorators.debug
@cli_decorators.profile
@click.argument('user-id', nargs=1, type=str, required=True)
@click.argument('password', nargs=1, type=str, required=True)
@click.option('--is-admin', type=bool, default=False, required=False, is_flag=True, help='User has administrator control')
@click.option('--email', type=str, required=False, help='User email address')
@click.option('--description', type=str, required=False, help='User description')
def create(debug, profile, user_id, password, is_admin, email, description):
    set_debug_log_level(debug)
    cli_account.create(profile, user_id, password, is_admin, email, description)

@account.command(short_help='\tDelete a user account')
@cli_decorators.debug
@cli_decorators.profile
@click.argument('user-id', nargs=1, type=str, required=True)
def delete(debug, profile, user_id):
    set_debug_log_level(debug)
    cli_account.delete(profile, user_id)

@account.command(short_help='\tAdd or remove user permission')
@cli_decorators.debug
@cli_decorators.profile
@click.argument('user_id', nargs=1, type=str, required=True)
@click.option('--action', type=click.Choice(['add', 'remove'], case_sensitive=False), required=True, help='Add or remove permission action')
@click.option('--permission-id', type=str, required=True, help='ID(s) of permission (comma separated)')
def permission(debug, profile, user_id, action, permission_id):
    set_debug_log_level(debug)
    cli_account.permission(profile, user_id, action, permission_id)

@account.command(short_help='\tList all available permissions')
@cli_decorators.debug
@cli_decorators.format_output
@cli_decorators.list
@cli_decorators.profile
def permission_list(debug, pretty, yaml, xml, toml, list, profile):
    set_debug_log_level(debug)
    cli_account.permission_list(pretty, yaml, xml, toml, list, profile)

@account.command(short_help='\tReset a user password')
@cli_decorators.debug
@cli_decorators.profile
def password_reset(debug, profile):
    set_debug_log_level(debug)
    click.echo(click.style('TODO :-/', fg='yellow',))



##############################################################################
#                             CREDENTIAL
##############################################################################
@main.group(short_help='\tManage credentials',
cls=HelpColorsGroup,
    help_options_custom_colors={
        'update': 'black',
        'move': 'black'
        })
def credential():
    """CREDENTIALS MANAGEMENT"""
    pass

@credential.command(short_help='\tList credentials')
@cli_decorators.debug
@cli_decorators.format_output
@cli_decorators.list
@cli_decorators.profile
# @click.argument('folder', nargs=1, type=str, default="root", required=False)
@click.option('--folder', type=str, default="root", show_default=True, required=False, help='Credentials folder')
@click.option('--domain', type=str, default="global", show_default=True, required=False, help='Credentials domain')
@click.option('--keys', type=str, default="all", show_default=True, required=False, help='Credential info keys to return [ie. displayName,id,etc]')
def list(debug, pretty, yaml, xml, toml, list, profile, folder, domain, keys):
    set_debug_log_level(debug)
    cli_credential.list(pretty, yaml, xml, toml, list, profile, folder, domain, keys)

@credential.command(short_help='\tCredential information')
@cli_decorators.debug
@cli_decorators.format_output
@cli_decorators.profile
@click.argument('credential', nargs=1, type=str, required=True)
@click.option('--folder', type=str, default="root", show_default=True, required=False, help='Credential folder')
@click.option('--domain', type=str, default="global", show_default=True, required=False, help='Credential domain')
def info(debug, pretty, yaml, xml, toml, profile, credential, folder, domain):
    set_debug_log_level(debug)
    cli_credential.info(pretty, yaml, xml, toml, profile, credential, folder, domain)

@credential.command(short_help='\tGet credential configuration')
@cli_decorators.debug
@cli_decorators.format_output
@click.option('-j', '--json', type=bool, default=False, required=False, is_flag=True, help='Output config in JSON format')
@cli_decorators.profile
@click.argument('credential', nargs=1, type=str, required=True)
@click.option('--folder', type=str, default="root", show_default=True, required=False, help='Credential folder')
@click.option('--domain', type=str, default="global", show_default=True, required=False, help='Credential domain')
@click.option('--filepath', type=click.Path(file_okay=True, dir_okay=True), required=False, help='File/Filepath to write configurations to')
def config(debug, pretty, yaml, xml, toml, json, profile, credential, folder, domain, filepath):
    set_debug_log_level(debug)
    cli_credential.config(pretty, yaml, xml, toml, json, profile, credential, folder, domain, filepath)

@credential.command(short_help='\tCredential type template to create a credential')
@cli_decorators.debug
@cli_decorators.format_output
@click.option('-j', '--json', type=bool, default=False, required=False, is_flag=True, help='Output config in JSON format')
@cli_decorators.profile
@click.argument('type', type=click.Choice(['user-pass', 'ssh-key', 'secret-text'], case_sensitive=False), default='user-pass', required=True)
@click.option('--filepath', type=click.Path(file_okay=True, dir_okay=True), required=False, help='File/Filepath to write template to')
def get_template(debug, pretty, yaml, xml, toml, json, profile, type, filepath):
    set_debug_log_level(debug)
    cli_credential.get_template(pretty, yaml, xml, toml, json, profile, type, filepath)

@credential.command(short_help='\tCreate new credentials')
@cli_decorators.debug
@cli_decorators.profile
# @click.argument('name', nargs=1, type=str, required=True)
@click.argument('config-file', nargs=1, type=click.Path(exists=True), required=True)
@click.option('--folder', type=str, default="root", show_default=True, required=False, help='Credential folder')
@click.option('--domain', type=str, default="global", show_default=True, required=False, help='Credential domain')
def create(debug, profile, config_file, folder, domain):
    set_debug_log_level(debug)
    cli_credential.create(profile, config_file, folder, domain)

@credential.command(short_help='\tRemove credentials')
@cli_decorators.debug
@cli_decorators.profile
@click.argument('credential', nargs=1, type=str, required=True)
@click.option('--folder', type=str, default="root", show_default=True, required=False, help='Credential folder')
@click.option('--domain', type=str, default="global", show_default=True, required=False, help='Credential domain')
def delete(debug, profile, credential, folder, domain):
    set_debug_log_level(debug)
    cli_credential.delete(profile, credential, folder, domain)

@credential.command(short_help='\tReconfigure existing credentials')
@cli_decorators.debug
def update(debug):
    set_debug_log_level(debug)
    click.echo(click.style('TODO :-/', fg='yellow',))

@credential.command(short_help='\tMove a credential to another folder/domain')
@cli_decorators.debug
def move(debug):
    set_debug_log_level(debug)
    click.echo(click.style('TODO :-/', fg='yellow',))


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
@click.option('-fn', '--fullname', type=bool, default=False, required=False, is_flag=True, help='Search entire folder path name')
@cli_decorators.list
def search(debug, pretty, yaml, xml, toml, profile, search_pattern, search_folder, depth, fullname, list):
    set_debug_log_level(debug)
    cli_folder.search(pretty, yaml, xml, toml, profile, search_pattern, search_folder, depth, fullname, list)

@folder.command(short_help='\tList all subfolders in folder')
@cli_decorators.debug
@cli_decorators.format_output
@cli_decorators.profile
@click.argument('folder', nargs=1, type=str, required=True)
@cli_decorators.list
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

@folder.command(short_help='\tGet folder configuration')
@cli_decorators.debug
@cli_decorators.format_output
@click.option('-j', '--json', type=bool, default=False, required=False, is_flag=True, help='Output config in JSON format')
@cli_decorators.profile
@click.argument('folder', nargs=1, type=str, required=True)
@click.option('--filepath', type=click.Path(file_okay=True, dir_okay=True), required=False, help='File/Filepath to write configurations to')
def config(debug, pretty, yaml, xml, toml, json, profile, folder, filepath):
    set_debug_log_level(debug)
    cli_folder.config(pretty, yaml, xml, toml, json, profile, folder, filepath)

@folder.command(short_help='\tCreate an item [folder, view, job]')
@cli_decorators.debug
@cli_decorators.profile
@click.argument('name', nargs=1, type=str, required=True)
@click.argument('folder', nargs=1, type=str, required=True)
@click.option('--type', type=click.Choice(['folder', 'view', 'job'], case_sensitive=False), default='folder', show_default=True, required=False, help='Item type created')
@click.option('--config-file', type=click.Path(file_okay=True, dir_okay=False), required=False, help='Path to local file defining item')
@click.option('--config-is-json', type=bool, default=False, required=False, is_flag=True, help='The specified file is in JSON format')
def create(debug, profile, name, folder, type, config_file, config_is_json):
    set_debug_log_level(debug)
    cli_folder.create(profile, name, folder, type, config_file, config_is_json)

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
@main.group(short_help='\tManage jobs',
    cls=HelpColorsGroup,
    help_options_custom_colors={
        'queue_cancel': 'black'
        })
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
@click.option('-fn', '--fullname', type=bool, default=False, required=False, is_flag=True, help='Search entire job path name')
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
    click.echo(click.style('TODO :-/', fg='yellow',))

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
@click.option('-j', '--json', type=bool, default=False, required=False, is_flag=True, help='Output config in JSON format')
@cli_decorators.profile
@click.argument('job', nargs=1, type=str, required=True)
@click.option('--filepath', type=click.Path(file_okay=True, dir_okay=False), required=False, help='Filepath to write configurations to')
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
@click.option('--config-file', default='', type=click.Path(file_okay=True, dir_okay=False), required=False, help='Path to local config file defining job')
@click.option('--config-is-json', type=bool, default=False, required=False, is_flag=True, help='The specified file is in JSON format')
def create(debug, profile, name, folder, config_file, config_is_json):
    set_debug_log_level(debug)
    cli_job.create(profile, name, folder, config_file, config_is_json)



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
@click.option('-dd', '--download-dir', type=click.Path(file_okay=False, dir_okay=True), required=False, is_flag=False, help='Download logs to directory')
@click.option('--follow', default=False, type=str, required=False, is_flag=True, help='Follow/Stream the logs as they are generated')
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
@click.option('-dd', '--download_dir', type=click.Path(file_okay=False, dir_okay=True), required=False, is_flag=False, help='Download logs to directory')
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
#                             TOOLS
##############################################################################
@main.group(short_help='\tTools and more',
    cls=HelpColorsGroup,
    help_options_custom_colors={
        'docs': 'black'
        })
def tools():
    """UTILITY AND MORE"""
    pass

@tools.command(short_help='\tOpen browser to the documentation')
@cli_decorators.debug
def docs(debug):
    set_debug_log_level(debug)
    click.echo(click.style('TODO :-/', fg='yellow',))

# @tools.command(short_help='\tUpgrade yojenkins')
# @cli_decorators.debug
# @click.option('--user', type=bool, required=False, is_flag=True, help='Install to the Python user install directory for your platform')
# @click.option('--proxy', type=str, required=False, help='Specify a proxy in the form [user:passwd@]proxy.server:port')
# def upgrade(debug, user, proxy):
#     """Install the latest version of yojenkins. This is a thin wrapper to 'pip install'"""
#     set_debug_log_level(debug)
#     cli_tools.upgrade(user, proxy)

# @tools.command(short_help='\tRemove yojenkins')
# @cli_decorators.debug
# def remove(debug):
#     """Uninstall yojenkins using pip"""
#     set_debug_log_level(debug)
#     cli_tools.remove()

@tools.command(short_help='\tReport a bug')
@cli_decorators.debug
def bug_report( debug):
    """This command will open a web browser to report a bug"""
    set_debug_log_level(debug)
    cli_tools.bug_report()

@tools.command(short_help='\tRequest a feature')
@cli_decorators.debug
def feature_request(debug):
    """This command will open a web browser to request a feature"""
    set_debug_log_level(debug)
    cli_tools.feature_request()

@tools.command(short_help='\tShow detailed command usage history')
@cli_decorators.debug
@click.option('--profile', type=str, required=False, is_flag=False, help='Filter by profile name')
@click.option('--clear', type=bool, required=False, default=False, is_flag=True, help='Clear the history file')
def history(debug, profile, clear):
    set_debug_log_level(debug)
    cli_tools.history(profile, clear)

@tools.command(short_help='\tSend a generic Rest request to server')
@cli_decorators.debug
@cli_decorators.profile
@click.argument('request_text', nargs=1, type=str, required=True)
@click.option('--request-type', type=click.Choice(['GET', 'POST', 'HEAD'], case_sensitive=False), default='GET', show_default=True, required=False, help='Type of Rest request')
@click.option('--raw', type=bool, required=False, default=False, is_flag=True, help='Return raw return text')
@click.option('--clean-html', type=bool, required=False, default=False, is_flag=True, help='Clean any HTML tags from return')
def rest_request(debug, profile, request_text, request_type, raw, clean_html):
    """Use this command to send Rest calls to the server.
    The request will be send with the proper authentication form your profile.
    This can be useful if yojenkins does not have the functionality you need.

    EXAMPLE:

      - yojenkins tools rest-request "me/api/json"
    """
    set_debug_log_level(debug)
    cli_tools.rest_request(profile, request_text, request_type, raw, clean_html)


@tools.command(short_help='\tRun Groovy script on server, return result')
@cli_decorators.debug
@cli_decorators.profile
@click.option('--text', type=str, required=False, help='Command(s) to run entered as text')
@click.option('--file', type=click.Path(file_okay=True, dir_okay=False), required=False, is_flag=False, help='File containing command(s) to run')
@click.option('--output', type=click.Path(file_okay=True, dir_okay=False), required=False, is_flag=False, help='Save the result to this file')
@click.pass_context
def run_script(ctx, debug, profile, text, file, output):
    """Use this command to execute a Groovy script, as text or in a file,
    on the Jenkins server and return the output

    EXAMPLES:

    \b
      - yojenkins tools script --text "println('hello you')"
      - yojenkins tools script --file ./my_script.groovy
    """
    set_debug_log_level(debug)
    if text or file:
        cli_tools.run_script(profile, text, file, output)
    else:
        click.echo(ctx.get_help())

@tools.command(short_help='\tSet up a Jenkins shared library')
@cli_decorators.debug
@cli_decorators.profile
@click.option('--lib-name', type=str, required=True, help='Name of library, to be used in the @Library annotation')
@click.option('--repo-owner', type=str, required=False, help='Owner/Organization of git repository')
@click.option('--repo-name', type=str, required=False, help='Name of git repository')
@click.option('--repo-url', type=str, required=False, help='URL of git repository. Same syntax as git clone command')
@click.option('--repo-branch', type=str, required=False, default='main', show_default=True, help='Branch of the git repository')
@click.option('--implicit', type=bool, required=False, default=False, show_default=True, is_flag=True, help='Automatically allow pipelines to use libraries without @Library')
@click.option('--credential-id', type=str, required=False, help='ID of your git credentials in Jenkins credentials database')
def shared_lib_setup(debug, profile, lib_name, repo_owner, repo_name, repo_url, repo_branch, implicit, credential_id):
    """This sets up the Jenkins Shared Library, referencing a GitHub git repository.

    WARNING:

        Sharable libraries available to any Pipeline jobs running on this system.
        These libraries will be fully trusted, meaning theyrun without “sandbox” restrictions and may use @Grab.

    USAGE NOTES:

    \b
        - As of now, only GitHub repositories are supported
        - Use with --repo-owner and --repo-name [OR] --repo-url
        - Using the same --lib-name will overwrite currently defined library

    EXAMPLE:

    \b
        yojenkins tools shared-lib-setup \\
            --lib-name SHARED-LIB-NAME \\
            --repo-url https://github.com/ORG/REPO-NAME.git \\
            --repo-branch main \\
            --implicit \\
            --credential-id my-jenkins-cred-id


    """
    set_debug_log_level(debug)
    cli_tools.shared_lib_setup(profile, lib_name, repo_owner, repo_name, repo_url, repo_branch, implicit, credential_id)


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
    main()
