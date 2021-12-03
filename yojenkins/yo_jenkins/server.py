"""Server class definition"""

import logging
from typing import Dict, List, Tuple

from yojenkins.utility import utility
from yojenkins.utility.utility import fail_out

# Getting the logger reference
logger = logging.getLogger()


class Server():
    """TODO Server"""

    def __init__(self, rest: object, auth: object) -> None:
        """Object constructor method, called at object creation

        Args:
            None

        Returns:
            None
        """
        self.rest = rest
        self.auth = auth

        self.server_base_url = auth.jenkins_profile['jenkins_server_url']

    def info(self) -> Dict:
        """Get the server information

        Details: Targeting the server that is specified in the selected profile

        Args:
            None

        Returns:
            Server information
        """
        server_info, _, success = self.rest.request('api/json', 'get')
        if not success:
            fail_out('Failed to fetch server information')

        return server_info

    def people(self) -> Tuple[list, list]:
        """Get the list of people/accounts on the server

        Args:
            None

        Returns:
            List of users/accounts, list of usernames
        """
        logger.debug(f'Getting all people/users for "{self.server_base_url}" ...')

        people_info, _, success = self.rest.request('asynchPeople/api/json?depth=1', 'get', is_endpoint=True)
        if not success:
            fail_out('Failed to fetch server people/users information')

        try:
            people_info = people_info['users']
            people_info_list = [f"{p['user']['fullName']}" for p in people_info]
        except KeyError as error:
            fail_out(f'Failed to parse server people/users information. Specific keys not found: {error}')

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
        server_queue_info, _, success = self.rest.request('queue/api/json', 'get')
        if not success:
            fail_out('Failed to get server queue info')

        return server_queue_info

    def queue_list(self) -> List[str]:
        """Get all list of all the jobs stuck in the server queue

        (Potentially move to jobs or build section)

        Args:
            None

        Returns:
            List of urls of jobs stuck in server queue
        """
        server_queue_info = self.queue_info()

        queue_list = []
        queue_job_url_list = []
        for queue_item in server_queue_info['items']:
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

        plugins_info, _, success = self.rest.request('pluginManager/api/json?depth=2', 'get', is_endpoint=True)
        if not success:
            fail_out('Failed to fetch server plugin information')

        try:
            plugins_info = plugins_info['plugins']
            plugin_info_list = [f"{p['longName']} - {p['shortName']} - {p['version']}" for p in plugins_info]
        except KeyError as error:
            fail_out(f'Failed to parse server plugin information. Specific keys not found: {error}')

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
        if not success:
            fail_out('Failed to open server home page in browser')
        logger.debug('Successfully opened in web browser')

        return success

    def restart(self, force: bool = True) -> bool:
        """TODO Docstring

        Args:
            TODO

        Returns:
            TODO
        """
        logger.debug("Initiating server force restart ..." if force else "Initiating server safe restart ...")
        success = self.rest.request('restart' if force else 'safeRestart',
                                    'post',
                                    is_endpoint=True,
                                    json_content=True,
                                    allow_redirect=False)[2]
        if not success:
            fail_out('Failed to initiate server restart')

        return success

    def shutdown(self, force: bool = True) -> bool:
        """TODO Docstring

        Args:
            TODO

        Returns:
            TODO
        """
        logger.debug("Initiating server force shutdown ..." if force else "Initiating server safe shutdown ...")
        success = self.rest.request('exit' if force else 'safeExit',
                                    'post',
                                    is_endpoint=True,
                                    json_content=False,
                                    allow_redirect=False)[2]
        if not success:
            fail_out('Failed to initiate server shutdown')

        return success

    def quiet(self, off: bool = False) -> bool:
        """TODO Docstring

        Args:
            TODO

        Returns:
            TODO
        """
        logger.debug("Disabeling server quiet mode ..." if off else "Enabling server quiet mode ...")
        success = self.rest.request('cancelQuietDown' if off else 'quietDown',
                                    'post',
                                    is_endpoint=True,
                                    json_content=True,
                                    allow_redirect=False)[2]
        if not success:
            fail_out(f'Failed to {"disable" if off else "enable"} server quiet mode')

        return success
