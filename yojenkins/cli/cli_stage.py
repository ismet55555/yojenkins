"""Stage Menu CLI Entrypoints"""

import logging

from yojenkins.cli import cli_utility as cu
from yojenkins.cli.cli_utility import log_to_history
from yojenkins.utility.utility import fail_out, print2
from yojenkins.yo_jenkins.status import Status

# Getting the logger reference
logger = logging.getLogger()


@log_to_history
def info(profile: str, token: str, name: str, job: str, number: int, url: str, latest: bool, **kwargs) -> None:
    """TODO Docstring

    Details: TODO

    Args:
        TODO
    """
    if job and not number and not latest:
        fail_out('INPUT ERROR: For job, either specify --number or --latest. See --help')

    yj_obj = cu.config_yo_jenkins(profile, token)

    # Differentiate if name or url
    if url:
        logger.debug(f'Build URL passed: {url}')
        valid_url_format = True
    else:
        valid_url_format = cu.is_full_url(job) if not url else True

    # Request the data
    if valid_url_format:
        data = yj_obj.stage.info(stage_name=name, build_url=url, job_url=job, build_number=number, latest=latest)
    else:
        data = yj_obj.stage.info(stage_name=name, build_url=url, job_name=job, build_number=number, latest=latest)
    cu.standard_out(data, **kwargs)


@log_to_history
def status(profile: str, token: str, name: str, job: str, number: int, url: str, latest: bool) -> None:
    """TODO Docstring

    Details: TODO

    Args:
        TODO
    """
    if job and not number and not latest:
        fail_out('INPUT ERROR: For job, either specify --number or --latest. See --help')

    yj_obj = cu.config_yo_jenkins(profile, token)

    # Differentiate if name or url
    if url:
        logger.debug(f'Build URL passed: {url}')
        valid_url_format = True
    else:
        valid_url_format = cu.is_full_url(job) if not url else True

    # Request the data
    if valid_url_format:
        data = yj_obj.stage.status_text(stage_name=name,
                                        build_url=url,
                                        job_url=job,
                                        build_number=number,
                                        latest=latest)
    else:
        data = yj_obj.stage.status_text(stage_name=name,
                                        build_url=url,
                                        job_name=job,
                                        build_number=number,
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
def steps(profile: str, token: str, opt_list: bool, name: str, job: str, number: int, url: str, latest: bool,
          **kwargs) -> None:
    """TODO Docstring

    Details: TODO

    Args:
        TODO
    """
    if job and not number and not latest:
        fail_out('INPUT ERROR: For job, either specify --number or --latest. See --help')

    yj_obj = cu.config_yo_jenkins(profile, token)

    # Differentiate if name or url
    if url:
        logger.debug(f'Build URL passed: {url}')
        valid_url_format = True
    else:
        valid_url_format = cu.is_full_url(job) if not url else True

    # Request the data
    if valid_url_format:
        data, data_list = yj_obj.stage.step_list(stage_name=name,
                                                 build_url=url,
                                                 job_url=job,
                                                 build_number=number,
                                                 latest=latest)
    else:
        data, data_list = yj_obj.stage.step_list(stage_name=name,
                                                 build_url=url,
                                                 job_name=job,
                                                 build_number=number,
                                                 latest=latest)
    data = data_list if opt_list else data
    cu.standard_out(data, **kwargs)


@log_to_history
def logs(profile: str, token: str, name: str, job: str, number: int, url: str, latest: bool,
         download_dir: bool) -> None:
    """TODO Docstring

    Details: TODO

    Args:
        TODO
    """
    if job and not number and not latest:
        fail_out('INPUT ERROR: For job, either specify --number or --latest. See --help')

    yj_obj = cu.config_yo_jenkins(profile, token)

    # Differentiate if name or url
    if url:
        logger.debug(f'Build URL passed: {url}')
        valid_url_format = True
    else:
        valid_url_format = cu.is_full_url(job) if not url else True

    # Request the data
    if valid_url_format:
        yj_obj.stage.logs(stage_name=name,
                          build_url=url,
                          job_url=job,
                          build_number=number,
                          latest=latest,
                          download_dir=download_dir)
    else:
        yj_obj.stage.logs(stage_name=name,
                          build_url=url,
                          job_name=job,
                          build_number=number,
                          latest=latest,
                          download_dir=download_dir)
