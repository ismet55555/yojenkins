#!/usr/bin/env python3

import logging
from typing import Dict, List, Tuple

from yo_jenkins.Utility import utility

# Getting the logger reference
logger = logging.getLogger()


class Node():
    """TODO Node"""

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

    def create_permanent(self) -> Dict:
        """TODO Docstring

        Details: TODO

        Args:
            TODO

        Returns:
            TODO
        """
        logger.debug(f'Creating and configuring a new permanent node/agent ...')


        request = "computer/doCreateItem"

        content, headers, success = self.REST.request(
            target=request,
            request_type='post',
            is_endpoint=True)


        # self.jenkins_open(requests.Request(
        #     'POST', self._build_url(CREATE_NODE, locals()), data=params)
        # )
