#!/usr/bin/env python3

import logging
from pprint import pprint
from typing import Dict, List, Tuple

import jenkins
import utility

# Getting the logger reference
logger = logging.getLogger()


class Server():
    """TODO Server"""

    def __init__(self, REST, Auth) -> None:
        """Object constructor method, called at object creation

        Args:
            None

        Returns:
            None
        """
        self.REST = REST
        self.Auth = Auth

        self.server_base_url = self.Auth.jenkins_profile['jenkins_server_url']


    def info(self) -> Dict:
        """Get the server information

        Details: Targeting the server that is specified in the selected profile

        Args:
            None

        Returns:
            Server information
        """
        return self.REST.request('api/json', 'get')[0]

    # TODO: MOVE TO AUTH
    # def user_info(self) -> Dict:
    #     """Get user information

    #     Details: Targeting the user that is specified in the selected profile

    #     Args:
    #         None

    #     Returns:
    #         User information
    #     """
    #     return self.REST.request('me/api/json', 'get')[0]


    def people(self) -> Tuple[list, list]:
        """Get the list of plugins installed on the server

        Args:
            None

        Returns:
            List of plugins, information list and URL list
        """
        logger.debug(f'Getting all installed server plugins for "{self.server_base_url}" ...')

        people_info, _, success = self.REST.request(
            'asynchPeople/api/json?depth=1',
            'get',
            is_endpoint=True
            )
        if not success:
            logger.debug(f'Failed to fetch server plugin information')
            return [], []
        people_info = people_info['users']
        people_info_list = [ f"{p['user']['fullName']}" for p in people_info ]
        return people_info, people_info_list


    def queue_info(self) -> Dict:
        """Get all the jobs stuck in the server queue

        (Potentially move to jobs or build section)

        Args:
            None

        Returns:
            Server queue information
        """
        # TODO: Combine with server_queue_list adding a list argument

        logger.debug(f'Requesting build queue info for "{self.server_base_url}" ...')

        # Making the request
        return_content = self.REST.request('queue/api/json', 'get')[0]
        if not return_content:
            logger.debug('Failed to get server queue info. Check access and permissions for this endpoint')
        return return_content


    def queue_list(self) -> List[str]:
        """Get all list of all the jobs stuck in the server queue

        (Potentially move to jobs or build section)

        Args:
            None

        Returns:
            List of urls of jobs stuck in server queue
        """
        queue_info = self.queue_info()

        queue_list = []
        queue_job_url_list = []
        for queue_item in queue_info['items']:
            queue_list.append(queue_item)
            if 'url' in queue_item['task']:
                queue_job_url_list.append(queue_item['task']['url'])

        return queue_list


    def plugin_list(self) -> Tuple[list, list]:
        """Get the list of plugins installed on the server

        Args:
            None

        Returns:
            List of plugins, information list and URL list
        """
        logger.debug(f'Getting all installed server plugins for "{self.server_base_url}" ...')

        plugins_info, _, success = self.REST.request(
            'pluginManager/api/json?depth=2',
            'get',
            is_endpoint=True
            )
        if not success:
            logger.debug(f'Failed to fetch server plugin information')
            return [], []

        plugins_info = plugins_info['plugins']
        plugin_info_list = [ f"{p['longName']} - {p['shortName']} - {p['version']}" for p in plugins_info ]
        return plugins_info, plugin_info_list


    def browser_open(self) -> bool:
        """TODO Docstring

        Args:
            TODO

        Returns:
            TODO
        """
        logger.debug(f'Opening in server home page in browser: "{self.server_base_url}" ...')
        success = utility.browser_open(url=self.server_base_url)
        logger.debug('Successfully opened in web browser' if success else 'Failed to open in web browser')
        return success



    def restart(self, force:bool=True) -> bool:
        """TODO Docstring

        Args:
            TODO
            (jenkins_url)/safeRestart - Allows all running jobs to complete. New jobs will remain in the queue to run after the restart is complete.
            (jenkins_url)/restart - Forces a restart without waiting for builds to complete.

        Returns:
            TODO
        """
        logger.debug("Initiating server force restart ..." if force else "Initiating server safe restart ...")
        _, _, success = self.REST.request(
            'restart' if force else 'safeRestart',
            'post',
            is_endpoint=True,
            json_content=True,
            allow_redirect=False)
        if not success:
            logger.debug(f'Failed to initiate server restart')
            return [], []
        return success
