"""Server click sub-command"""
# pylint: skip-file

import click

from yojenkins.__main__ import server
from yojenkins.cli import cli_decorators, cli_server
from yojenkins.cli.cli_utility import set_debug_log_level


@server.command(short_help='\tServer information')
@cli_decorators.debug
@cli_decorators.format_output
@cli_decorators.profile
def info(debug, pretty, yaml, toml, xml, profile):
    """Server information"""
    set_debug_log_level(debug)
    cli_server.info(pretty, yaml, xml, toml, profile)


@server.command(short_help='\tShow all people/users on server')
@cli_decorators.debug
@cli_decorators.format_output
@cli_decorators.profile
@cli_decorators.list
def people(debug, pretty, yaml, xml, toml, profile, list):
    """Show all people/users on server"""
    set_debug_log_level(debug)
    cli_server.people(pretty, yaml, xml, toml, profile, list)


@server.command(short_help='\tShow current job build queues on server')
@cli_decorators.debug
@cli_decorators.format_output
@cli_decorators.profile
@cli_decorators.list
def queue(debug, pretty, yaml, xml, toml, profile, list):
    """Show current job build queues on server"""
    set_debug_log_level(debug)
    cli_server.queue(pretty, yaml, xml, toml, profile, list)
    # NOTE: Maybe move to "job"?


@server.command(short_help='\tShow plugin information')
@cli_decorators.debug
@cli_decorators.format_output
@cli_decorators.profile
@cli_decorators.list
def plugins(debug, pretty, yaml, xml, toml, profile, list):
    """Show plugin information"""
    set_debug_log_level(debug)
    cli_server.plugins(pretty, yaml, xml, toml, profile, list)


@server.command(short_help='\tOpen server home page in web browser')
@cli_decorators.debug
@cli_decorators.profile
def browser(debug, profile):
    """Open server home page in web browser"""
    set_debug_log_level(debug)
    cli_server.browser(profile)


@server.command(short_help='\tCheck if server is reachable')
@cli_decorators.debug
@cli_decorators.profile
@click.option('--timeout', type=int, default=10, required=False, is_flag=False, help='Request timeout value')
def reachable(debug, profile, timeout):
    """Check if server is reachable"""
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
              show_default=True,
              type=str,
              required=False,
              help='Base Jenkins server image')
@click.option('--extra-setup-script',
              default='',
              type=click.Path(file_okay=True, dir_okay=False),
              required=False,
              help='Local path of additional setup shell script to be executed at image build')
@click.option('--image-rebuild',
              default=False,
              type=bool,
              required=False,
              is_flag=True,
              help='If image exists, rebuild existing docker image')
@click.option('--new-volume',
              default=False,
              show_default=True,
              type=bool,
              required=False,
              is_flag=True,
              help='Erase existing Docker data volume from previously created servers')
@click.option('--new-volume-name',
              default='yojenkins-jenkins',
              type=str,
              required=False,
              help='Name of the resulting Docker volume')
@click.option('--bind-mount-dir',
              default='',
              type=click.Path(file_okay=False, dir_okay=True),
              required=False,
              help='Path of local directory to be bound inside container "/tmp/my_things" directory')
@click.option('--container-name',
              default='yojenkins-jenkins',
              type=str,
              required=False,
              help='Name of the resulting Docker container')
@click.option('--registry', default='', type=str, required=False, help='Registry to pull base Jenkins image from')
@click.option('--admin-user',
              default='admin',
              show_default=True,
              type=str,
              required=False,
              help='Set username of admin')
@click.option('--password',
              default='',
              type=str,
              required=False,
              help='Set password for admin account [default: password]')
def server_deploy(debug, config_file, plugins_file, protocol_schema, host, port, image_base, extra_setup_script,
                  image_rebuild, new_volume, new_volume_name, bind_mount_dir, container_name, registry, admin_user,
                  password):
    """Create a local development server using Docker

    \b
    ATTENTION:
        - The resulting Jenkins server is for development and testing purposes only. Enjoy responsibly.

    \b
    NOTES:
        - Docker must be installed for this command to function
        - All options have default values and command can be run without any specified options

    \b
    EXAMPLES:
        - yojenkins server server-deploy
        - yojenkins server server-deploy --admin-user user_1 --password 123456
        - yojenkins server server-deploy --image-base jenkinsci/blueocean
        - yojenkins server server-deploy --plugins-file my_plugins.txt
        - yojenkins server server-deploy --extra_setup_script /home/ismet/project/setup.sh
    """
    set_debug_log_level(debug)
    cli_server.server_deploy(config_file, plugins_file, protocol_schema, host, port, image_base, extra_setup_script,
                             image_rebuild, new_volume, new_volume_name, bind_mount_dir, container_name, registry,
                             admin_user, password)


@server.command(short_help='\tRemove a local development server')
@click.option('--remove-volume',
              default=False,
              show_default=True,
              type=bool,
              required=False,
              is_flag=True,
              help='Also remove the Docker volume used for current server')
@click.option('--remove-image',
              default=False,
              show_default=True,
              type=bool,
              required=False,
              is_flag=True,
              help='Also remove the Docker image used for current server')
@cli_decorators.debug
def server_teardown(debug, remove_volume, remove_image):
    """Remove a local development server"""
    set_debug_log_level(debug)
    cli_server.server_teardown(remove_volume, remove_image)


# @server.command(short_help='\tCheck if a locally deployed development server is running')
# @cli_decorators.debug
# def server_check(debug):
#     set_debug_log_level(debug)
#     click.secho('TODO :-/', fg='yellow')
