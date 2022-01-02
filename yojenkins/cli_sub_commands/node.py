"""Node click sub-command"""
# pylint: skip-file

import click

from yojenkins.__main__ import node
from yojenkins.cli import cli_decorators, cli_node
from yojenkins.cli.cli_utility import set_debug_log_level


@node.command(short_help='\tNode information')
@cli_decorators.debug
@cli_decorators.format_output
@cli_decorators.profile
@click.argument('name', nargs=1, type=str, required=True)
@click.option('-d', '--depth', type=int, default=0, required=False, help='Search depth from root directory')
def info(debug, pretty, yaml, xml, toml, profile, name, depth):
    """Node information"""
    set_debug_log_level(debug)
    cli_node.info(pretty, yaml, xml, toml, profile, name, depth)


@node.command(short_help='\tNode status')
@cli_decorators.debug
@cli_decorators.profile
@click.argument('name', nargs=1, type=str, required=True)
def status(debug, profile, name):
    """Node status"""
    set_debug_log_level(debug)
    click.secho('TODO :-/', fg='yellow')


@node.command(short_help='\tList all nodes')
@cli_decorators.debug
@cli_decorators.profile
@cli_decorators.format_output
@cli_decorators.list
@click.option('-d', '--depth', type=int, default=0, required=False, help='Search depth from root directory')
def list(debug, profile, pretty, yaml, xml, toml, list, depth):
    """List all nodes"""
    set_debug_log_level(debug)
    cli_node.list(pretty, yaml, xml, toml, list, profile, depth)


@node.command(short_help='\tPrepare a remote machine to become a node')
@cli_decorators.debug
def prepare(debug):
    """Prepare a remote machine to become a node"""
    set_debug_log_level(debug)
    cli_node.prepare()


@node.command(short_help='\tSetup a local or remote persistent node')
@cli_decorators.debug
@cli_decorators.profile
@click.argument('name', nargs=1, type=str, required=True)
@click.argument('host', nargs=1, type=str, required=True)
@click.argument('credential', nargs=1, type=str, required=True)
@click.option('--description', type=str, required=False, help='Node description')
@click.option('--executors',
              default=1,
              type=click.IntRange(1, 100),
              required=False,
              show_default=True,
              help='Number of executors on node')
@click.option('--labels', type=str, required=False, help='Labels applied to agent [default: NAME]')
@click.option('--mode',
              type=click.Choice(['normal', 'exclusive'], case_sensitive=False),
              default='normal',
              show_default=True,
              required=False,
              help='Available to all or to specified jobs')
@click.option('--remote-java-dir',
              default="/usr/bin/java",
              show_default=True,
              type=str,
              required=False,
              help='Location of Java binary')
@click.option('--remote-root-dir',
              default="/home/jenkins",
              show_default=True,
              type=str,
              required=False,
              help='Directory where node work is kept')
@click.option('--retention',
              type=click.Choice(['always', 'demand'], case_sensitive=False),
              default='always',
              show_default=True,
              required=False,
              help='Always on or offline when not in use')
@click.option('--ssh-port',
              default=22,
              show_default=True,
              type=click.IntRange(1, 64738),
              required=False,
              help='SSH port to target')
@click.option('--ssh-verify',
              type=click.Choice(['known', 'trusted', 'none'], case_sensitive=False),
              default='trusted',
              show_default=True,
              required=False,
              help='SSH verification strategy')
# @click.option('--config-file', type=click.Path(file_okay=True, dir_okay=False), required=False, help='Path to local XML file defining agent')
def create_permanent(debug, profile, **kwargs):
    """
    This command sets up a local or remote node on a virtual machine, container,
    or physical machine, connecting with SSH. The target system must have the following:

    \b
    - A working SSH server installed, running, and accessible from main server
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
    """Setup a local or remote ephemeral/as-needed node"""
    set_debug_log_level(debug)
    click.secho('TODO :-/', fg='yellow')


@node.command(short_help='\tDelete a node')
@cli_decorators.debug
@cli_decorators.profile
@click.argument('name', nargs=1, type=str, required=True)
def delete(debug, profile, name):
    """Delete a node"""
    set_debug_log_level(debug)
    cli_node.delete(profile, name)


@node.command(short_help='\tDisable a node')
@cli_decorators.debug
@cli_decorators.profile
@click.argument('name', nargs=1, type=str, required=True)
@click.option('--message', type=str, required=False, help='Message for disabling node')
def disable(debug, profile, name, message):
    """Disable a node"""
    set_debug_log_level(debug)
    cli_node.disable(profile, name, message)


@node.command(short_help='\tEnable a node')
@cli_decorators.debug
@cli_decorators.profile
@click.argument('name', nargs=1, type=str, required=True)
@click.option('--message', type=str, required=False, help='Message for enabling node')
def enable(debug, profile, name, message):
    """Enable a node"""
    set_debug_log_level(debug)
    cli_node.enable(profile, name, message)


@node.command(short_help='\tGet node configuration')
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
@click.argument('name', nargs=1, type=str, required=True)
@click.option('--filepath',
              type=click.Path(file_okay=True, dir_okay=True),
              required=False,
              help='File/Filepath to write configurations to')
def config(debug, pretty, yaml, xml, toml, json, profile, name, filepath):
    """Get node configuration"""
    set_debug_log_level(debug)
    cli_node.config(pretty, yaml, xml, toml, json, profile, name, filepath)


@node.command(short_help='\tReconfigure the node')
@cli_decorators.debug
@cli_decorators.profile
@click.argument('name', nargs=1, type=str, required=True)
@click.option('--config-file',
              type=click.Path(file_okay=True, dir_okay=True),
              required=True,
              help='Path to local config file defining node')
@click.option('--config-is-json',
              type=bool,
              default=False,
              show_default=True,
              required=False,
              is_flag=True,
              help='The specified file is in JSON format')
def reconfig(debug, profile, name, config_file, config_is_json):
    """Reconfigure the node"""
    set_debug_log_level(debug)
    cli_node.reconfig(profile, name, config_file, config_is_json)


@node.command(short_help='\tNode logs')
@cli_decorators.debug
@cli_decorators.profile
def logs(debug, profile):
    """Node logs"""
    set_debug_log_level(debug)
    click.secho('TODO :-/', fg='yellow')
