"""Tools click sub-command"""
# pylint: skip-file

import click

from yojenkins.__main__ import tools
from yojenkins.cli import cli_decorators, cli_tools
from yojenkins.cli.cli_utility import set_debug_log_level
from yojenkins.utility.utility import translate_kwargs


@tools.command(short_help='\tOpen browser to the documentation page')
@cli_decorators.debug
def docs(debug):
    """Open browser to the documentation"""
    set_debug_log_level(debug)
    cli_tools.documentation()


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
def bug_report(debug):
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
def history(debug, **kwargs):
    """Show detailed command usage history"""
    set_debug_log_level(debug)
    cli_tools.history(**kwargs)


@tools.command(short_help='\tSend a generic Rest request to server')
@cli_decorators.debug
@cli_decorators.profile
@click.argument('request_text', nargs=1, type=str, required=True)
@click.option('--request-type',
              type=click.Choice(['GET', 'POST', 'HEAD'], case_sensitive=False),
              default='GET',
              show_default=True,
              required=False,
              help='Type of Rest request')
@click.option('--raw', type=bool, required=False, default=False, is_flag=True, help='Return raw return text')
@click.option('--clean-html',
              type=bool,
              required=False,
              default=False,
              is_flag=True,
              help='Clean any HTML tags from return')
def rest_request(debug, **kwargs):
    """Use this command to send Rest calls to the server.
    The request will be send with the proper authentication from your profile.
    This can be useful if yojenkins does not have the functionality you need.

    EXAMPLE:

      - yojenkins tools rest-request "me/api/json"
    """
    set_debug_log_level(debug)
    cli_tools.rest_request(**kwargs)


@tools.command(short_help='\tRun Groovy script on server, return result')
@cli_decorators.debug
@cli_decorators.profile
@click.option('--text', type=str, required=False, help='Command(s) to run entered as text')
@click.option('--file',
              type=click.Path(file_okay=True, dir_okay=False),
              required=False,
              is_flag=False,
              help='File containing command(s) to run')
@click.option('--output',
              type=click.Path(file_okay=True, dir_okay=False),
              required=False,
              is_flag=False,
              help='Save the result to this file')
@click.pass_context
def run_script(ctx, debug, **kwargs):
    """Use this command to execute a Groovy script, as text or in a file,
    on the Jenkins server and return the output

    EXAMPLES:

    \b
      - yojenkins tools script --text "println('hello you')"
      - yojenkins tools script --file ./my_script.groovy
    """
    set_debug_log_level(debug)
    if kwargs.get("text") or kwargs.get("file"):
        cli_tools.run_script(**translate_kwargs(kwargs))
    else:
        click.echo(ctx.get_help())


@tools.command(short_help='\tSet up a Jenkins shared library')
@cli_decorators.debug
@cli_decorators.profile
@click.option('--lib-name', type=str, required=True, help='Name of library, to be used in the @Library annotation')
@click.option('--repo-owner', type=str, required=False, help='Owner/Organization of git repository')
@click.option('--repo-name', type=str, required=False, help='Name of git repository')
@click.option('--repo-url', type=str, required=False, help='URL of git repository. Same syntax as git clone command')
@click.option('--repo-branch',
              type=str,
              required=False,
              default='main',
              show_default=True,
              help='Branch of the git repository')
@click.option('--implicit',
              type=bool,
              required=False,
              default=False,
              show_default=True,
              is_flag=True,
              help='Automatically allow pipelines to use libraries without @Library')
@click.option('--credential-id',
              type=str,
              required=False,
              help='ID of your git credentials in Jenkins credentials database')
def shared_lib_setup(debug, **kwargs):
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
    cli_tools.shared_lib_setup(**translate_kwargs(kwargs))
