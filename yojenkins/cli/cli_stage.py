"""Stage Menu CLI Entrypoints"""

import logging

from yojenkins.cli import cli_utility as cu
from yojenkins.cli.cli_utility import log_to_history
from yojenkins.utility.utility import fail_out, print2
from yojenkins.yo_jenkins.status import Status

# Getting the logger reference
logger = logging.getLogger()


@log_to_history
def info(opt_pretty: bool, opt_yaml: bool, opt_xml: bool, opt_toml: bool, profile: str, stage_name: str, job: str,
         build_number: int, build_url: str, latest: bool) -> None:
    """TODO Docstring

    Details: TODO

    Args:
        TODO

    Returns:
        TODO
    """
    if job and not build_number and not latest:
        fail_out('INPUT ERROR: For job, either specify --number or --latest. See --help')

    yj_obj = cu.config_yo_jenkins(profile)

    # Differentiate if name or url
    if build_url:
        logger.debug(f'Build URL passed: {build_url}')
        valid_url_format = True
    else:
        valid_url_format = cu.is_full_url(job) if not build_url else True

    # Request the data
    if valid_url_format:
        data = yj_obj.stage.info(stage_name=stage_name,
                                 build_url=build_url,
                                 job_url=job,
                                 build_number=build_number,
                                 latest=latest)
    else:
        data = yj_obj.stage.info(stage_name=stage_name,
                                 build_url=build_url,
                                 job_name=job,
                                 build_number=build_number,
                                 latest=latest)
    cu.standard_out(data, opt_pretty, opt_yaml, opt_xml, opt_toml)


@log_to_history
def status(profile: str, stage_name: str, job: str, build_number: int, build_url: str, latest: bool) -> None:
    """TODO Docstring

    Details: TODO

    Args:
        TODO

    Returns:
        TODO
    """
    if job and not build_number and not latest:
        fail_out('INPUT ERROR: For job, either specify --number or --latest. See --help')

    yj_obj = cu.config_yo_jenkins(profile)

    # Differentiate if name or url
    if build_url:
        logger.debug(f'Build URL passed: {build_url}')
        valid_url_format = True
    else:
        valid_url_format = cu.is_full_url(job) if not build_url else True

    # Request the data
    if valid_url_format:
        data = yj_obj.stage.status_text(stage_name=stage_name,
                                        build_url=build_url,
                                        job_url=job,
                                        build_number=build_number,
                                        latest=latest)
    else:
        data = yj_obj.stage.status_text(stage_name=stage_name,
                                        build_url=build_url,
                                        job_name=job,
                                        build_number=build_number,
                                        latest=latest)

    # Color for output
    if data.upper() in Status.UNKNOWN.value:
        color = 'black'
    elif data.upper() in Status.QUEUED.value:
        color = 'yellow'
    elif data.upper() in Status.RUNNING.value:
        color = 'blue'
    elif data.upper() in Status.SUCCESS.value:
        color = 'green'
    elif data.upper() in Status.FAILURE.value:
        color = 'red'
    else:
        color = ''
    print2(f'{data}', bold=True, color=color)


@log_to_history
def steps(opt_pretty: bool, opt_yaml: bool, opt_xml: bool, opt_toml: bool, profile: str, opt_list: bool,
          stage_name: str, job: str, build_number: int, build_url: str, latest: bool) -> None:
    """TODO Docstring

    Details: TODO

    Args:
        TODO

    Returns:
        TODO
    """
    if job and not build_number and not latest:
        fail_out('INPUT ERROR: For job, either specify --number or --latest. See --help')

    yj_obj = cu.config_yo_jenkins(profile)

    # Differentiate if name or url
    if build_url:
        logger.debug(f'Build URL passed: {build_url}')
        valid_url_format = True
    else:
        valid_url_format = cu.is_full_url(job) if not build_url else True

    # Request the data
    if valid_url_format:
        data, data_list = yj_obj.stage.step_list(stage_name=stage_name,
                                                 build_url=build_url,
                                                 job_url=job,
                                                 build_number=build_number,
                                                 latest=latest)
    else:
        data, data_list = yj_obj.stage.step_list(stage_name=stage_name,
                                                 build_url=build_url,
                                                 job_name=job,
                                                 build_number=build_number,
                                                 latest=latest)
    data = data_list if opt_list else data
    cu.standard_out(data, opt_pretty, opt_yaml, opt_xml, opt_toml)


@log_to_history
def logs(profile: str, stage_name: str, job: str, build_number: int, build_url: str, latest: bool,
         download_dir: bool) -> None:
    """TODO Docstring

    Details: TODO

    Args:
        TODO

    Returns:
        TODO
    """
    if job and not build_number and not latest:
        fail_out('INPUT ERROR: For job, either specify --number or --latest. See --help')

    yj_obj = cu.config_yo_jenkins(profile)

    # Differentiate if name or url
    if build_url:
        logger.debug(f'Build URL passed: {build_url}')
        valid_url_format = True
    else:
        valid_url_format = cu.is_full_url(job) if not build_url else True

    # Request the data
    if valid_url_format:
        yj_obj.stage.logs(stage_name=stage_name,
                          build_url=build_url,
                          job_url=job,
                          build_number=build_number,
                          latest=latest,
                          download_dir=download_dir)
    else:
        yj_obj.stage.logs(stage_name=stage_name,
                          build_url=build_url,
                          job_name=job,
                          build_number=build_number,
                          latest=latest,
                          download_dir=download_dir)
