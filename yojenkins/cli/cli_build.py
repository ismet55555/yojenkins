"""Build Menu CLI Entrypoints"""

import logging
import sys

import click

from yojenkins.cli import cli_utility as cu
from yojenkins.cli.cli_utility import log_to_history
from yojenkins.yo_jenkins.status import Status

# Getting the logger reference
logger = logging.getLogger()


def _verify_build_url_get_job_format(build_url: str, job: str) -> bool:
    """Utility function to verify buld url and determine if job is URL or name

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
def info(opt_pretty: bool, opt_yaml: bool, opt_xml: bool, opt_toml: bool, profile: str, job: str, build_number: int,
         build_url: str, latest: bool) -> None:
    """TODO Docstring

    Args:
        opt_pretty: Option to pretty print the output
        opt_yaml: Option to output in YAML format
        opt_xml: Option to output in XML format
        opt_toml: Option to output in TOML format
        profile: The profile/account to use
        job: The job this build is under
        build_number: The build number to get info on
        build_url: The build url to get info on
        latest: Option to get the latest build

    Returns:
        None
    """
    if job and not build_number and not latest:
        click.echo(
            click.style('INPUT ERROR: For job, either specify --number or --latest. See --help',
                        fg='bright_red',
                        bold=True))
        sys.exit(1)

    yj_obj = cu.config_yo_jenkins(profile)

    if _verify_build_url_get_job_format(build_url=build_url, job=job):
        data = yj_obj.build.info(build_url=build_url, job_url=job, build_number=build_number, latest=latest)
    else:
        data = yj_obj.build.info(build_url=build_url, job_name=job, build_number=build_number, latest=latest)
    cu.standard_out(data, opt_pretty, opt_yaml, opt_xml, opt_toml)


@log_to_history
def status(profile: str, job: str, build_number: int, build_url: str, latest: bool) -> None:
    """Build status text/label

    Args:
        profile: The profile/account to use
        job: The job this build is under
        build_number: The build number to get info on
        build_url: The build url to get info on
        latest: Option to get the latest build

    Returns:
        None
    """
    if job and not build_number and not latest:
        click.echo(
            click.style('INPUT ERROR: For job, either specify --number or --latest. See --help',
                        fg='bright_red',
                        bold=True))
        sys.exit(1)

    yj_obj = cu.config_yo_jenkins(profile)

    if _verify_build_url_get_job_format(build_url=build_url, job=job):
        data = yj_obj.build.status_text(build_url=build_url, job_url=job, build_number=build_number, latest=latest)
    else:
        data = yj_obj.build.status_text(build_url=build_url, job_name=job, build_number=build_number, latest=latest)

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
def abort(profile: str, job: str, build_number: int, build_url: str, latest: bool) -> None:
    """Abort build

    Args:
        profile: The profile/account to use
        job: The job this build is under
        build_number: The build number to get info on
        build_url: The build url to get info on
        latest: Option to get the latest build

    Returns:
        None
    """
    if job and not build_number and not latest:
        click.echo(
            click.style('INPUT ERROR: For job, either specify --number or --latest. See --help',
                        fg='bright_red',
                        bold=True))
        sys.exit(1)

    yj_obj = cu.config_yo_jenkins(profile)

    if _verify_build_url_get_job_format(build_url=build_url, job=job):
        data = yj_obj.build.abort(build_url=build_url, job_url=job, build_number=build_number, latest=latest)
    else:
        data = yj_obj.build.abort(build_url=build_url, job_name=job, build_number=build_number, latest=latest)
    click.secho('success', fg='bright_green', bold=True)


@log_to_history
def delete(profile: str, job: str, build_number: int, build_url: str, latest: bool) -> None:
    """Delete build

    Args:
        profile: The profile/account to use
        job: The job this build is under
        build_number: The build number to get info on
        build_url: The build url to get info on
        latest: Option to get the latest build

    Returns:
        None
    """
    if job and not build_number and not latest:
        click.echo(
            click.style('INPUT ERROR: For job, either specify --number or --latest. See --help',
                        fg='bright_red',
                        bold=True))
        sys.exit(1)

    yj_obj = cu.config_yo_jenkins(profile)

    if _verify_build_url_get_job_format(build_url=build_url, job=job):
        data = yj_obj.build.delete(build_url=build_url, job_url=job, build_number=build_number, latest=latest)
    else:
        data = yj_obj.build.delete(build_url=build_url, job_name=job, build_number=build_number, latest=latest)
    click.secho('success', fg='bright_green', bold=True)


@log_to_history
def stages(opt_pretty: bool, opt_yaml: bool, opt_xml: bool, opt_toml: bool, profile: str, opt_list: bool, job: str,
           build_number: int, build_url: str, latest: bool) -> None:
    """Get build stages

    Args:
        opt_pretty: Option to pretty print the output
        opt_yaml: Option to output in YAML format
        opt_xml: Option to output in XML format
        opt_toml: Option to output in TOML format
        profile: The profile/account to use
        opt_list: Option to list all stages without details
        job: The job name under which the build is located
        build_number: The build number
        build_url: The build URL
        latest: Option to get the latest build

    Returns:
        None
    """
    if job and not build_number and not latest:
        click.echo(
            click.style('INPUT ERROR: For job, either specify --number or --latest. See --help',
                        fg='bright_red',
                        bold=True))
        sys.exit(1)

    yj_obj = cu.config_yo_jenkins(profile)

    if _verify_build_url_get_job_format(build_url=build_url, job=job):
        data, data_list = yj_obj.build.stage_list(build_url=build_url,
                                                  job_url=job,
                                                  build_number=build_number,
                                                  latest=latest)
    else:
        data, data_list = yj_obj.build.stage_list(build_url=build_url,
                                                  job_name=job,
                                                  build_number=build_number,
                                                  latest=latest)
    data = data_list if opt_list else data
    cu.standard_out(data, opt_pretty, opt_yaml, opt_xml, opt_toml)


@log_to_history
def logs(profile: str, job: str, build_number: int, build_url: str, latest: bool, tail: float, download_dir: bool,
         follow: bool) -> None:
    """Get build logs

    Args:
        profile: The profile/account to use
        job: The job this build is under
        build_number: The build number to get info on
        build_url: The build url to get info on
        latest: Option to get the latest build
        tail: Option to get the last N lines of the log
        download_dir: Option to download the log to a directory
        follow: Option to follow the log

    Returns:
        None
    """
    if job and not build_number and not latest:
        click.echo(
            click.style('INPUT ERROR: For job, either specify --number or --latest. See --help',
                        fg='bright_red',
                        bold=True))
        sys.exit(1)

    yj_obj = cu.config_yo_jenkins(profile)

    if _verify_build_url_get_job_format(build_url=build_url, job=job):
        yj_obj.build.logs(build_url=build_url,
                          job_url=job,
                          build_number=build_number,
                          latest=latest,
                          tail=tail,
                          download_dir=download_dir,
                          follow=follow)
    else:
        yj_obj.build.logs(build_url=build_url,
                          job_name=job,
                          build_number=build_number,
                          latest=latest,
                          tail=tail,
                          download_dir=download_dir,
                          follow=follow)
    if download_dir:
        click.secho('success', fg='bright_green', bold=True)


@log_to_history
def browser(profile: str, job: str, build_number: int, build_url: str, latest: bool) -> None:
    """Open build in web browser

    Args:
        profile: The profile/account to use
        job: The job this build is under
        build_number: The build number to get info on
        build_url: The build url to get info on
        latest: Option to get the latest build

    Returns:
        None
    """
    if job and not build_number and not latest:
        click.echo(
            click.style('INPUT ERROR: For job, either specify --number or --latest. See --help',
                        fg='bright_red',
                        bold=True))
        sys.exit(1)

    yj_obj = cu.config_yo_jenkins(profile)

    if _verify_build_url_get_job_format(build_url=build_url, job=job):
        yj_obj.build.browser_open(build_url=build_url, job_url=job, build_number=build_number, latest=latest)
    else:
        yj_obj.build.browser_open(build_url=build_url, job_name=job, build_number=build_number, latest=latest)


@log_to_history
def monitor(profile: str, job: str, build_number: int, build_url: str, latest: bool, sound: bool) -> None:
    """Start monitor UI

    Args:
        profile: The profile/account to use
        job: The job this build is under
        build_number: The build number to get info on
        build_url: The build url to get info on
        latest: Option to get the latest build
        sound: Option to play a sound when the build status changes

    Returns:
        None
    """
    if job and not build_number and not latest:
        click.echo(
            click.style('INPUT ERROR: For job, either specify --number or --latest. See --help',
                        fg='bright_red',
                        bold=True))
        sys.exit(1)

    yj_obj = cu.config_yo_jenkins(profile)

    if _verify_build_url_get_job_format(build_url=build_url, job=job):
        yj_obj.build.monitor(build_url=build_url, job_url=job, build_number=build_number, latest=latest, sound=sound)
    else:
        yj_obj.build.monitor(build_url=build_url, job_name=job, build_number=build_number, latest=latest, sound=sound)


@log_to_history
def parameters(opt_pretty: bool, opt_yaml: bool, opt_xml: bool, opt_toml: bool, profile: str, opt_list: bool, job: str,
               build_number: int, build_url: str, latest: bool) -> None:
    """Get build parameters

    Args:
        profile: The profile/account to use
        opt_list: Option to list all stages without details
        job: The job name under which the build is located
        build_number: The build number
        build_url: The build URL
        latest: Option to get the latest build

    Returns:
        None
    """
    if job and not build_number and not latest:
        click.echo(
            click.style('INPUT ERROR: For job, either specify --number or --latest. See --help',
                        fg='bright_red',
                        bold=True))
        sys.exit(1)

    yj_obj = cu.config_yo_jenkins(profile)

    if _verify_build_url_get_job_format(build_url=build_url, job=job):
        data, data_list = yj_obj.build.parameters(build_url=build_url,
                                                  job_url=job,
                                                  build_number=build_number,
                                                  latest=latest)
    else:
        data, data_list = yj_obj.build.parameters(build_url=build_url,
                                                  job_name=job,
                                                  build_number=build_number,
                                                  latest=latest)
    data = data_list if opt_list else data
    cu.standard_out(data, opt_pretty, opt_yaml, opt_xml, opt_toml)
