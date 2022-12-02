"""Build Menu CLI Entrypoints"""

import logging
import sys

import click

from yojenkins.cli import cli_utility as cu
from yojenkins.cli.cli_utility import log_to_history
from yojenkins.utility.utility import is_complete_build_url, wait_for_build_and_follow_logs
from yojenkins.yo_jenkins.status import Status

# Getting the logger reference
logger = logging.getLogger()


def _verify_build_url_get_job_format(build_url: str, job: str) -> bool:
    """Utility function to verify build url and determine if job is URL or name

    Args:
        build_url: Build URL
        job: Job URL or name

    Returns:
         True if both are valid, False otherwise
    """
    if build_url:
        if not cu.is_full_url(build_url):
            click.secho('The build url not formatted correctly', fg='bright_red', bold=True)
            sys.exit(1)
        valid_url_format = True
    else:
        valid_url_format = cu.is_full_url(job)
    return valid_url_format


@log_to_history
def info(profile: str, token: str, job: str, number: int, url: str, latest: bool, **kwargs) -> None:
    """Fetching build information

    Args:
        profile: The profile/account to use
        token:   API Token for Jenkins server
        job:     The job this build is under
        number:  The build number to get info on
        url:     The build url to get info on
        latest:  Option to get the latest build
    """
    if url is None and job and is_complete_build_url(job):
        url, job = job, None
    elif job and not number and not latest:
        click.echo(
            click.style('INPUT ERROR: For job, either specify --number or --latest. See --help',
                        fg='bright_red',
                        bold=True))
        sys.exit(1)

    yj_obj = cu.config_yo_jenkins(profile, token)

    if _verify_build_url_get_job_format(build_url=url, job=job):
        data = yj_obj.build.info(build_url=url, job_url=job, build_number=number, latest=latest)
    else:
        data = yj_obj.build.info(build_url=url, job_name=job, build_number=number, latest=latest)
    cu.standard_out(data, **kwargs)


@log_to_history
def status(profile: str, token: str, job: str, number: int, url: str, latest: bool) -> None:
    """Build status text/label

    ### FIXME: Verify build number resolution works

    Args:
        profile: The profile/account to use
        token:   API Token for Jenkins server
        job: The job this build is under
        number: The build number to get info on
        url: The build url to get info on
        latest: Option to get the latest build
    """
    if url is None and job and is_complete_build_url(job):
        url, job = job, None
    elif job and not number and not latest:
        click.echo(
            click.style('INPUT ERROR: For job, either specify --number or --latest. See --help',
                        fg='bright_red',
                        bold=True))
        sys.exit(1)

    yj_obj = cu.config_yo_jenkins(profile, token)

    if _verify_build_url_get_job_format(build_url=url, job=job):
        data = yj_obj.build.status_text(build_url=url, job_url=job, build_number=number, latest=latest)
    else:
        data = yj_obj.build.status_text(build_url=url, job_name=job, build_number=number, latest=latest)

    # Color for output
    if data in Status.NONE.value:
        data = "NONE"
        output_fg = 'black'
    elif data.upper() in Status.UNKNOWN.value:
        output_fg = 'black'
    elif data.upper() in Status.QUEUED.value:
        output_fg = 'yellow'
    elif data.upper() in Status.RUNNING.value:
        output_fg = 'blue'
    elif data.upper() in Status.SUCCESS.value:
        output_fg = 'bright_green'
    elif data.upper() in Status.FAILURE.value:
        output_fg = 'bright_red'
    else:
        output_fg = ''
    click.secho(f'{data}', fg=output_fg, bold=True)


@log_to_history
def abort(profile: str, token: str, job: str, number: int, url: str, latest: bool) -> None:
    """Abort build

    Args:
        profile: The profile/account to use
        token:   API Token for Jenkins server
        job: The job this build is under
        number: The build number to get info on
        url: The build url to get info on
        latest: Option to get the latest build
    """
    if url is None and job and is_complete_build_url(job):
        url, job = job, None
    elif job and not number and not latest:
        click.echo(
            click.style('INPUT ERROR: For job, either specify --number or --latest. See --help',
                        fg='bright_red',
                        bold=True))
        sys.exit(1)

    yj_obj = cu.config_yo_jenkins(profile, token)

    if _verify_build_url_get_job_format(build_url=url, job=job):
        yj_obj.build.abort(build_url=url, job_url=job, build_number=number, latest=latest)
    else:
        yj_obj.build.abort(build_url=url, job_name=job, build_number=number, latest=latest)
    click.secho('success', fg='bright_green', bold=True)


@log_to_history
def delete(profile: str, token: str, job: str, number: int, url: str, latest: bool) -> None:
    """Delete build

    Args:
        profile: The profile/account to use
        token:   API Token for Jenkins server
        job: The job this build is under
        number: The build number to get info on
        url: The build url to get info on
        latest: Option to get the latest build
    """
    if url is None and job and is_complete_build_url(job):
        url, job = job, None
    elif job and not number and not latest:
        click.echo(
            click.style('INPUT ERROR: For job, either specify --number or --latest. See --help',
                        fg='bright_red',
                        bold=True))
        sys.exit(1)

    yj_obj = cu.config_yo_jenkins(profile, token)

    if _verify_build_url_get_job_format(build_url=url, job=job):
        yj_obj.build.delete(build_url=url, job_url=job, build_number=number, latest=latest)
    else:
        yj_obj.build.delete(build_url=url, job_name=job, build_number=number, latest=latest)
    click.secho('success', fg='bright_green', bold=True)


@log_to_history
def stages(profile: str, token: str, opt_list: bool, job: str, number: int, url: str, latest: bool, **kwargs) -> None:
    """Get build stages

    Args:
        profile: The profile/account to use
        token:   API Token for Jenkins server
        opt_list: Option to list all stages without details
        job: The job name under which the build is located
        number: The build number
        url: The build URL
        latest: Option to get the latest build
    """
    if url is None and job and is_complete_build_url(job):
        url, job = job, None
    elif job and not number and not latest:
        click.echo(
            click.style('INPUT ERROR: For job, either specify --number or --latest. See --help',
                        fg='bright_red',
                        bold=True))
        sys.exit(1)

    yj_obj = cu.config_yo_jenkins(profile, token)

    if _verify_build_url_get_job_format(build_url=url, job=job):
        data, data_list = yj_obj.build.stage_list(build_url=url, job_url=job, build_number=number, latest=latest)
    else:
        data, data_list = yj_obj.build.stage_list(build_url=url, job_name=job, build_number=number, latest=latest)
    data = data_list if opt_list else data
    cu.standard_out(data, **kwargs)


@log_to_history
def logs(profile: str, token: str, job: str, number: int, url: str, latest: bool, tail: float, download_dir: str,
         follow: bool) -> None:
    """Get build logs

    Args:
        profile: The profile/account to use
        token:   API Token for Jenkins server
        job: The job this build is under
        number: The build number to get info on
        url: The build url to get info on
        latest: Option to get the latest build
        tail: Option to get the last N lines of the log
        download_dir: Option to download the log to a directory
        follow: Option to follow the log
    """
    if url is None and job and is_complete_build_url(job):
        url, job = job, None
    elif job and not number and not latest:
        click.echo(
            click.style('INPUT ERROR: For job, either specify --number or --latest. See --help',
                        fg='bright_red',
                        bold=True))
        sys.exit(1)

    yj_obj = cu.config_yo_jenkins(profile, token)

    if _verify_build_url_get_job_format(build_url=url, job=job):
        yj_obj.build.logs(build_url=url,
                          job_url=job,
                          build_number=number,
                          latest=latest,
                          tail=tail,
                          download_dir=download_dir,
                          follow=follow)
    else:
        yj_obj.build.logs(build_url=url,
                          job_name=job,
                          build_number=number,
                          latest=latest,
                          tail=tail,
                          download_dir=download_dir,
                          follow=follow)
    if download_dir:
        click.secho('success', fg='bright_green', bold=True)


@log_to_history
def browser(profile: str, token: str, job: str, number: int, url: str, latest: bool) -> None:
    """Open build in web browser

    Args:
        profile: The profile/account to use
        token:   API Token for Jenkins server
        job: The job this build is under
        number: The build number to get info on
        url: The build url to get info on
        latest: Option to get the latest build
    """
    if url is None and job and is_complete_build_url(job):
        url, job = job, None
    elif job and not number and not latest:
        click.echo(
            click.style('INPUT ERROR: For job, either specify --number or --latest. See --help',
                        fg='bright_red',
                        bold=True))
        sys.exit(1)

    yj_obj = cu.config_yo_jenkins(profile, token)

    if _verify_build_url_get_job_format(build_url=url, job=job):
        yj_obj.build.browser_open(build_url=url, job_url=job, build_number=number, latest=latest)
    else:
        yj_obj.build.browser_open(build_url=url, job_name=job, build_number=number, latest=latest)


@log_to_history
def monitor(profile: str, token: str, job: str, number: int, url: str, latest: bool, sound: bool) -> None:
    """Start monitor UI

    Args:
        profile: The profile/account to use
        token:   API Token for Jenkins server
        job: The job this build is under
        number: The build number to get info on
        url: The build url to get info on
        latest: Option to get the latest build
        sound: Option to play a sound when the build status changes
    """
    if url is None and job and is_complete_build_url(job):
        url, job = job, None
    elif job and not number and not latest:
        click.echo(
            click.style('INPUT ERROR: For job, either specify --number or --latest. See --help',
                        fg='bright_red',
                        bold=True))
        sys.exit(1)

    yj_obj = cu.config_yo_jenkins(profile, token)

    if _verify_build_url_get_job_format(build_url=url, job=job):
        yj_obj.build.monitor(build_url=url, job_url=job, build_number=number, latest=latest, sound=sound)
    else:
        yj_obj.build.monitor(build_url=url, job_name=job, build_number=number, latest=latest, sound=sound)


@log_to_history
def parameters(profile: str, token: str, opt_list: bool, job: str, number: int, url: str, latest: bool,
               **kwargs) -> None:
    """Get build parameters

    Args:
        profile: The profile/account to use
        token:   API Token for Jenkins server
        opt_list: Option to list all stages without details
        job: The job name under which the build is located
        number: The build number
        url: The build URL
        latest: Option to get the latest build
    """
    if url is None and job and is_complete_build_url(job):
        url, job = job, None
    elif job and not number and not latest:
        click.echo(
            click.style('INPUT ERROR: For job, either specify --number or --latest. See --help',
                        fg='bright_red',
                        bold=True))
        sys.exit(1)

    yj_obj = cu.config_yo_jenkins(profile, token)

    if _verify_build_url_get_job_format(build_url=url, job=job):
        data, data_list = yj_obj.build.parameters(build_url=url, job_url=job, build_number=number, latest=latest)
    else:
        data, data_list = yj_obj.build.parameters(build_url=url, job_name=job, build_number=number, latest=latest)
    data = data_list if opt_list else data
    cu.standard_out(data, **kwargs)


@log_to_history
def rebuild(profile: str, token: str, job: str, number: int, url: str, latest: bool, follow_logs: bool) -> None:
    """Rebuild a build with same setup/parameters

    Args:
        profile: The profile/account to use
        token:   API Token for Jenkins server
        job:     The job name under which the build is located
        number:  The build number
        url:     The build URL
        latest:  Option to get the latest build
        follow_logs: Waits for the job build, then follows resulting logs
    """

    if url is None and job and is_complete_build_url(job):
        url, job = job, None
    elif job and not number and not latest:
        click.echo(
            click.style('INPUT ERROR: For job, either specify --number or --latest. See --help',
                        fg='bright_red',
                        bold=True))
        sys.exit(1)

    yj_obj = cu.config_yo_jenkins(profile, token)

    if _verify_build_url_get_job_format(build_url=url, job=job):
        data = yj_obj.build.rebuild(build_url=url, job_url=job, build_number=number, latest=latest)
    else:
        data = yj_obj.build.rebuild(build_url=url, job_name=job, build_number=number, latest=latest)

    if not follow_logs:
        click.secho(f'success. queue number: {data}', fg='bright_green', bold=True)
        return
    wait_for_build_and_follow_logs(yj_obj, data)


@log_to_history
def diff(profile: str, token: str, build_url_1: str, build_url_2: str, logs: bool, char_ignore: int, no_color: bool,
         diff_only: bool, diff_guide: bool) -> None:
    """Get the diff comparison for two builds

    Args:
        profile:     The profile/account to use
        token:       API Token for Jenkins server
        build_url_1: First build for comparison
        build_url_2: Second build for comparison
        logs:        Compare build logs
        char_ignore: Number of characters to ignore at start of each line
        no_color:    Output diff with no color
        diff_only:   Only show the lines that have changed
        diff_guide:  Show diff guide, showing where exactly difference is in line
    """
    yj_obj = cu.config_yo_jenkins(profile, token)
    yj_obj.build.diff(build_url_1, build_url_2, logs, char_ignore, no_color, diff_only, diff_guide)
