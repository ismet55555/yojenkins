"""Step class definition"""

import logging
from typing import Dict

# Getting the logger reference
logger = logging.getLogger()


class Step():
    """TODO Step"""

    def __init__(self, rest) -> None:
        """Object constructor method, called at object creation

        Args:
            None

        Returns:
            None
        """
        self.rest = rest

    def info(self, step_url=str) -> Dict:
        """Get the information of the specified step

        Details: Step URL can be gotten with stage_step_list.
                 Format: <SERVER URL>/<step_url>

        Args:
            step_url : The direct URL of the step

        Returns:
            Step information
        """
        request_url = f'{step_url.strip("/")}'
        return_content = self.rest.request(request_url, 'get', is_endpoint=True)[0]
        if not return_content:
            logger.debug(f'Failed to get step info for: {request_url}')
            return {}

        return return_content
