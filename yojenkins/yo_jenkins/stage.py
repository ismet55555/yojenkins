"""Stage class definition"""

import logging
import os
import threading
from datetime import datetime, timedelta
from typing import Dict, Tuple

from yojenkins.utility import utility
from yojenkins.utility.utility import fail_out, print2
from yojenkins.yo_jenkins.status import StageStatus

# Getting the logger reference
logger = logging.getLogger()


class Stage():
    """Handeling of Jenkins stage functionality"""

    def __init__(self, rest: object, build: object, step: object) -> None:
        """Object constructor method, called at object creation

        Args:
            None

        Returns:
            None
        """
        self.rest = rest
        self.build = build
        self.step = step

        self.build_logs_extension = '.log'

        self._stage_log_list_thread_lock = threading.Lock()
        self.stage_log_dict = {}

    def info(self,
             stage_name: str,
             build_url: str = '',
             job_name: str = '',
             job_url: str = '',
             build_number: int = None,
             latest: bool = False) -> Dict:
        """Get the stage information for specified stage

        Details: Ways of specifying the build:
            - Build URL only
            - Job URL only
            - Job name with build number or latest flag

        Args:
            stage_name   : Name of the stage
            build_url    : Direct URL of the build
            job_name     : Name of the Job
            job_url      : URL of the Job
            build_number : Build number for the Job
            latest       : Latest build

        Returns:
            Stage information
        """
        # Getting all stages
        build_stage_list, build_stage_name_list = self.build.stage_list(build_url, job_name, job_url, build_number,
                                                                        latest)
        logger.debug(f'Stages found: {build_stage_name_list}')

        # Formate stage name from user input
        logger.debug(f'Formatting stage name "{stage_name}": Lower case, strip spaces')
        stage_name = stage_name.lower().strip()

        # Check if lowercase stage name is in list of stages in this build
        if not stage_name in [x.lower() for x in build_stage_name_list]:
            fail_out(f'Failed to find stage name "{stage_name}" among listed stages')

        # Getting the right stage item
        logger.debug('Getting stage URL from build information ...')
        build_stage_item = next(item for item in build_stage_list if item["name"].lower() == stage_name)

        # Making the request to get stage info
        endpoint = f'{build_stage_item["url"]}'
        return_content = self.rest.request(endpoint, 'get', is_endpoint=True)[0]
        if not return_content:
            fail_out(f'Failed to fetch stage information for "{stage_name}"')

        # Add additional derived information for stage
        return_content['startDatetime'] = datetime.fromtimestamp(return_content["startTimeMillis"] /
                                                                 1000.0).strftime("%A, %B %d, %Y %I:%M:%S")
        return_content['durationFormatted'] = str(timedelta(seconds=return_content["durationMillis"] / 1000.0))[:-3]
        return_content['pauseDurationFormatted'] = str(
            timedelta(seconds=return_content["pauseDurationMillis"] / 1000.0))
        return_content['numberOfSteps'] = len(return_content['stageFlowNodes'])

        # Add additional derived information for each step
        if "stageFlowNodes" in return_content:
            # Accounting for no stage step command
            for step_info in return_content['stageFlowNodes']:
                step_info['startDatetime'] = datetime.fromtimestamp(step_info["startTimeMillis"] /
                                                                    1000.0).strftime("%A, %B %d, %Y %I:%M:%S")
                step_info['durationFormatted'] = str(timedelta(seconds=step_info["durationMillis"] / 1000.0))[:-3]
                step_info['pauseDurationFormatted'] = str(timedelta(seconds=step_info["pauseDurationMillis"] / 1000.0))

                # Adding the urls to the item
                step_info['url'] = step_info['_links']['self']['href']
                step_info['url_log'] = step_info['_links']['log']['href']
                step_info['url_console'] = step_info['_links']['console']['href']
                step_info['url_full'] = f'{self.rest.get_server_url()}{step_info["url"]}'

        # TODO: Make utility function for additional derived info

        return return_content

    def status_text(self,
                    stage_name: str,
                    build_url: str = '',
                    job_name: str = '',
                    job_url: str = '',
                    build_number: int = None,
                    latest: bool = False) -> str:
        """Get the status text of the specified stage

        Details: Ways of specifying the build:
            - Build URL only
            - Job URL only
            - Job name with build number or latest flag

        Args:
            stage_name   : Name of the stage
            build_url    : Direct URL of the build
            job_name     : Name of the Job
            job_url      : URL of the Job
            build_number : Build number for the Job
            latest       : Latest build

        Returns:
            Stage status text
        """
        # Get the stage info
        stage_info = self.info(stage_name=stage_name,
                               build_url=build_url,
                               job_name=job_name,
                               job_url=job_url,
                               build_number=build_number,
                               latest=latest)

        if not stage_info:
            return StageStatus.NOT_FOUND.value

        # Check if in process (build is there but results not posted)
        if not stage_info['status']:
            logger.debug('Stage was found running/building, however no results are posted')
            return StageStatus.UNKNOWN.value
        else:
            logger.debug('Stage found, but has concluded or stopped with result')
            return stage_info['status']

    def step_list(self,
                  stage_name=str,
                  build_url: str = '',
                  job_name: str = '',
                  job_url: str = '',
                  build_number: int = None,
                  latest: bool = False) -> Tuple[list, list]:
        """List of steps for this stage

        Details: Ways of specifying the build:
            - Build URL only
            - Job URL only
            - Job name with build number or latest flag

        Args:
            stage_name   : Name of the stage
            build_url    : Direct URL of the build
            job_name     : Name of the Job
            job_url      : URL of the Job
            build_number : Build number for the Job
            latest       : Latest build

        Returns:
            List of steps, information and URL list
        """
        # Getting the stage info
        stage_info = self.info(stage_name=stage_name,
                               build_url=build_url,
                               job_name=job_name,
                               job_url=job_url,
                               build_number=build_number,
                               latest=latest)

        # Check if there are steps in this stage
        if "stageFlowNodes" not in stage_info:
            fail_out('Failed to get stage step information. No stage steps listed')

        # Accounting for no stage step command
        for step_info in stage_info['stageFlowNodes']:
            if not 'parameterDescription' in step_info:
                step_info['parameterDescription'] = "No command parameters listed"

        # Getting the stage items, and getting only the names/labels of the stages
        try:
            step_list = stage_info['stageFlowNodes']
            step_name_list = [s['name'] for s in step_list]
        except KeyError as error:
            fail_out(f'Failed to parse stage information. Specific keys not found: {error}')

        return step_list, step_name_list

    def _thread_step_info(self, step_index: int, total_steps: int, step: dict) -> None:
        """TODO

        Details: TODO

        Args:
            TODO

        Returns: None
        """
        logger.debug(f'Thread starting - Step Info - (ID: {threading.get_ident()} - INDEX: {step_index}) ...')

        # Getting step information
        return_content = self.step.info(step_url=step['url_log'])

        logger.debug(f"---> {step_index+1}/{total_steps} - {step['name']}")
        if 'parameterDescription' in step:
            parameter = step['parameterDescription']
        else:
            parameter = 'None'

        # Check if there is any log text to this stage step
        if 'text' in return_content or not return_content['length'] == 0:
            # Clean up all HTML tags from return, keep only raw text
            log_text = utility.html_clean(return_content['text'])

            # Also convert to list
            log_list = [y for y in (x.strip() for x in log_text.splitlines()) if y]

            # Add extra step info to each line of log
            log_list = [f"[STEP: {step_index+1}/{total_steps}] " + s for s in log_list]

            # Add intro to the logs of this step
            log_list.insert(0,
                            f"[STEP: {step_index+1}/{total_steps}] [STEP] : {step['name']} - PARAMETER: {parameter}")
        else:
            # If no logs in step, still add step command
            log_list = [f"[STEP: {step_index+1}/{total_steps}] [STEP] : {step['name']} - PARAMETER: {parameter}"]

        with self._stage_log_list_thread_lock:
            self.stage_log_dict[step_index] = log_list

        logger.debug(f'Thread stopped - Step Info - (ID: {threading.get_ident()} - INDEX: {step_index}) ...')

    def logs(self,
             stage_name=str,
             build_url: str = '',
             job_name: str = '',
             job_url: str = '',
             build_number: int = None,
             latest: bool = False,
             download_dir: bool = False) -> bool:
        """Prints out the console log for this specified stage

        Details: Ways of specifying the build:
            - Build URL only
            - Job URL only
            - Job name with build number or latest flag

        Args:
            stage_name   : Name of the stage
            build_url    : Direct URL of the build
            job_name     : Name of the Job
            job_url      : URL of the Job
            build_number : Build number for the Job
            latest       : Latest build
            download_dir : When specified, will download logs to file in this direcotry

        Returns:
            True if success, else False
        """
        # Getting all stage step information
        stage_step_list = self.step_list(stage_name=stage_name,
                                         build_url=build_url,
                                         job_name=job_name,
                                         job_url=job_url,
                                         build_number=build_number,
                                         latest=latest)[0]

        logger.debug(
            f'Downloading logs for {len(stage_step_list)} step in the stage using {len(stage_step_list)} threads ...')
        self.stage_log_dict = {}
        threads = []
        for i, stage_step in enumerate(stage_step_list):
            thread = threading.Thread(target=self._thread_step_info,
                                      args=(
                                          i,
                                          len(stage_step_list),
                                          stage_step,
                                      ),
                                      daemon=False)
            thread.start()
            threads.append(thread)
        for thread in threads:
            thread.join()

        # Convert dict to index sorted list
        stage_log_list = []
        for _, stage_logs in sorted(self.stage_log_dict.items()):
            stage_log_list.extend(stage_logs)

        # Make the list to continuos step, with newline in between them
        stage_log_text = os.linesep.join(stage_log_list)

        if download_dir:
            # Save logs to local file
            filename = f'build-logs_{datetime.now().strftime("%m-%d-%Y_%I-%M-%S")}{self.build_logs_extension}'
            logger.debug(f'Saving console text logs to local file "{filename}" ...')
            try:
                with open(os.path.join(download_dir, filename), 'w+') as file:
                    file.write(stage_log_text)
                logger.debug('Successfully write build logs to file')
            except (IOError, PermissionError) as error:
                fail_out(f'Failed to write logs to file. Exception: {error}')
        else:
            # Output to console
            logger.debug('Printing out console text logs ...')
            print2(stage_log_text)
        stage_log_text = None

        return True
