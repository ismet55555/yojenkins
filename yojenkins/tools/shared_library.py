"""Jenkins Shared Library Management"""

import logging
import os

from yojenkins.utility import utility

# Getting the logger reference
logger = logging.getLogger()


class SharedLibrary():
    """Class managing a Jenkins Shared Library"""

    def __init__(self) -> None:
        """Object constructor method, called at object creation

        Args:
            None

        Returns:
            None
        """
        self.groovy_script_directory = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'groovy_scripts')

    def setup(self, rest: object, lib_name: str, repo_owner: str, repo_name: str, repo_url: str, repo_branch: str,
              implicit: bool, credential_id: str) -> bool:
        """TODO Docstring

        Details: TODO

        Args:
            TODO

        Returns:
            TODO
        """
        if not repo_url and not repo_owner and not repo_name:
            logger.error('Either git repository URL OR owner and name are required')
            return False

        if not repo_url:
            if repo_owner and not repo_name:
                logger.debug("Git repository name is missing")
                return False
            elif repo_name and not repo_owner:
                logger.debug("Git repository owner is missing")
                return False
            logger.debug("Using git owner/organization")
        else:
            logger.debug("Using git repository URL")

        logger.debug("Setting up shared library ...")
        logger.debug(f"   - Name:              {lib_name}")
        logger.debug(f"   - Repository URL:    {repo_url}")
        logger.debug(f"   - Repository Owner:  {repo_owner}")
        logger.debug(f"   - Repository Name:   {repo_name}")
        logger.debug(f"   - Repository Branch: {repo_branch}")
        logger.debug(f"   - Implicit Loading:  {implicit}")
        logger.debug(f"   - Credential ID:     {credential_id}")

        kwargs = {
            'lib_name': lib_name,
            'repo_owner': repo_owner,
            'repo_name': repo_name,
            'repo_url': repo_url,
            'repo_branch': repo_branch,
            'implicit': 'true' if implicit else 'false',
            'credential_id': credential_id
        }
        script_filepath = os.path.join(self.groovy_script_directory, 'shared_lib_setup.groovy')
        _, success, error = utility.run_groovy_script(script_filepath=script_filepath,
                                                      json_return=False,
                                                      rest=rest,
                                                      **kwargs)
        if not success:
            logger.debug(f"Failed to setup Jenkins shared library. {error}")
            return False
        return True
