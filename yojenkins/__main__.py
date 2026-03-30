"""Main entry point for program"""


import logging
import sys

import click
from click_help_colors import HelpColorsGroup

from yojenkins import __version__
from yojenkins.cli import logger_setup
from yojenkins.cli.cli_utility import set_debug_log_level

logger = logging.getLogger()

if sys.version_info < (3, 7):
    click.secho('Your Python version ({}.{}) is not supported'.format(sys.version_info.major, sys.version_info.minor), fg='bright_red', bold=True)
    click.secho('Must have Python 3.7 or higher', fg='bright_red', bold=True)
    sys.exit(1)

##############################################################################


MAIN_HELP_TEXT = f"""
    \t\t\t \033[93m YOJENKINS (Version: {__version__}) \033[0m

    yojenkins is a flexible tool that is focused on interfacing with
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

# -----------------------------------------------------------------------------
@main.group(short_help='\tManage authentication and profiles',
    cls=HelpColorsGroup,
    help_options_custom_colors={
        'wipe': 'black'
        })
def auth():
    """Authentication And Profile Management"""
    pass
from yojenkins.cli_sub_commands import auth


# -----------------------------------------------------------------------------
@main.group(short_help='\tManage server')
def server():
    """Server Management"""
    pass
from yojenkins.cli_sub_commands import server


# -----------------------------------------------------------------------------
@main.group(short_help='\tManage nodes',
    cls=HelpColorsGroup,
    help_options_custom_colors={
        'prepare': 'black',
        'status': 'black',
        'create-ephemeral': 'black',
        'logs': 'black',
        })
def node():
    """Node Management"""
    pass
from yojenkins.cli_sub_commands import node


# -----------------------------------------------------------------------------
@main.group(short_help='\tManage user accounts',
cls=HelpColorsGroup,
    help_options_custom_colors={
        'password-reset': 'black',
        })
def account():
    """Account/User Management"""
    pass
from yojenkins.cli_sub_commands import account


# -----------------------------------------------------------------------------
@main.group(short_help='\tManage credentials',
cls=HelpColorsGroup,
    help_options_custom_colors={
        'update': 'black',
        'move': 'black'
        })
def credential():
    """Credentials Management"""
    pass
from yojenkins.cli_sub_commands import credential


# -----------------------------------------------------------------------------
@main.group(short_help='\tManage folders')
def folder():
    """Folder Management"""
    pass
from yojenkins.cli_sub_commands import folder


# -----------------------------------------------------------------------------
@main.group(short_help='\tManage jobs',
    cls=HelpColorsGroup,
    help_options_custom_colors={
        'queue_cancel': 'black'
        })
def job():
    """Job Management"""
    pass
from yojenkins.cli_sub_commands import job


# -----------------------------------------------------------------------------
@main.group(short_help='\tManage builds')
def build():
    """Build Management"""
    pass
from yojenkins.cli_sub_commands import build


# -----------------------------------------------------------------------------
@main.group(short_help='\tManage build stages')
def stage():
    """Stage Management"""
    pass
from yojenkins.cli_sub_commands import stage


# -----------------------------------------------------------------------------
@main.group(short_help='\tManage stage steps')
def step():
    """Step Management"""
    pass
from yojenkins.cli_sub_commands import step


# -----------------------------------------------------------------------------
@main.group(short_help='\tTools and more')
def tools():
    """Utility And More"""
    pass
from yojenkins.cli_sub_commands import tools

# -----------------------------------------------------------------------------
@main.command(short_help='\tStart the web application server')
@click.option('--host', type=str, default='127.0.0.1', show_default=True, help='Host to bind to')
@click.option('--port', type=int, default=8090, show_default=True, help='Port to bind to')
@click.option('--reload', is_flag=True, default=False, help='Enable auto-reload for development')
@click.option('--no-frontend', is_flag=True, default=False, help='API-only mode, skip frontend serving')
@click.option('--build', is_flag=True, default=False, help='Force rebuild the frontend')
def serve(host, port, reload, no_frontend, build):
    """Start the yojenkins web application server"""
    import os
    import shutil
    import subprocess
    from pathlib import Path

    try:
        import uvicorn
    except ImportError:
        click.secho('uvicorn is not installed. Install web dependencies:', fg='bright_red', bold=True)
        click.secho('  pip install yojenkins[web]', fg='yellow')
        click.secho('  # or: pip install -r requirements-web.txt', fg='yellow')
        sys.exit(1)

    static_dir = None
    if not no_frontend:
        webapp_dir = _find_webapp_dir()
        if webapp_dir:
            dist_dir = webapp_dir / 'dist'
            # index.html in dist/ marks a successful production build.
            # Vite always emits it; if missing, frontend needs building.
            if build or not (dist_dir / 'index.html').exists():
                _build_frontend(webapp_dir)
            if (dist_dir / 'index.html').exists():
                static_dir = str(dist_dir)
                click.secho(f'Serving frontend from {dist_dir}', fg='cyan')
            else:
                click.secho('Frontend not available. Running API-only mode.', fg='yellow')
                click.secho('Install Node.js and re-run, or use --no-frontend', fg='yellow')

    if static_dir:
        os.environ['YOJENKINS_STATIC_DIR'] = static_dir

    click.secho(f'Starting yojenkins web server on {host}:{port}', fg='bright_green', bold=True)
    if static_dir:
        click.secho(f'Open http://{host}:{port} in your browser', fg='cyan')
    click.secho(f'API docs at http://{host}:{port}/docs', fg='cyan')
    uvicorn.run('yojenkins.api.app:app', host=host, port=port, reload=reload)


def _find_webapp_dir():
    """Locate the webapp directory."""
    from pathlib import Path

    candidates = [
        Path.cwd() / 'webapp',
        Path(__file__).resolve().parent.parent / 'webapp',
    ]
    for candidate in candidates:
        if (candidate / 'package.json').exists():
            return candidate
    return None


def _build_frontend(webapp_dir):
    """Build the frontend using npm. Fails gracefully."""
    import shutil
    import subprocess
    from pathlib import Path

    npm_cmd = shutil.which('npm')
    if not npm_cmd:
        click.secho('Node.js/npm not found. Cannot build frontend.', fg='bright_red', bold=True)
        click.secho('Install Node.js from https://nodejs.org/', fg='yellow')
        return

    click.secho('Building frontend (first time may take a minute)...', fg='cyan')
    try:
        if not (webapp_dir / 'node_modules').exists():
            click.secho('Installing npm dependencies...', fg='cyan')
            # Prefer `npm ci` with lockfile for reproducible installs;
            # fall back to `npm install` for first-time setup.
            lock_file = webapp_dir / 'package-lock.json'
            install_cmd = [npm_cmd, 'ci'] if lock_file.exists() else [npm_cmd, 'install']
            subprocess.run(install_cmd, cwd=str(webapp_dir), check=True)

        subprocess.run([npm_cmd, 'run', 'build'], cwd=str(webapp_dir), check=True)
        click.secho('Frontend build complete!', fg='bright_green')
    except subprocess.CalledProcessError as exc:
        click.secho(f'Frontend build failed: {exc}', fg='bright_red')
        click.secho('Continuing in API-only mode.', fg='yellow')

##############################################################################
##############################################################################
##############################################################################
if __name__ == "__main__":
    """Main entry point to the entire program"""
    main()
