#!/usr/bin/env python3

import logging
from pprint import pprint
from typing import Dict

# Getting the logger reference
logger = logging.getLogger()


class Step():
    """TODO Step"""

    def __init__(self, R) -> None:
        """Object constructor method, called at object creation

        Args:
            None

        Returns:
            None
        """

        # REST Request object
        self.R = R

    def info(self, step_url=str) -> Dict:
        """Get the information of the specified step

        Details: Step URL can be gotten with stage_step_list.
                 Format: <SERVER URL>/<step_url>

        Args:
            step_url : The direct URL of the step

        Returns:
            Step information
        """
        # Making the request
        request_url = f'{step_url.strip("/")}'
        return_content = self.R.request(request_url, 'get', is_endpoint=True)[0]
        if not return_content:
            logger.debug(f'Failed to get step info for: {request_url}')
            return {}

        return return_content
