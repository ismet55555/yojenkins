#!/usr/bin/env python3

import logging
import os

from yo_jenkins.Utility import utility

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


    def setup(self, REST: object, lib_name: str, repo_owner: str, repo_name: str, repo_url: str, repo_branch: str, implicit: bool, credential_id: str) -> bool:
        """TODO Docstring

        Details: TODO

        Args:
            TODO

        Returns:
            TODO
        """
        # print(lib_name)
        # print(repo_owner)
        # print(repo_name)
        # print(repo_url)
        # print(repo_branch) 
        # print(implicit)
        # print(credential_id)

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
        script_result, success = utility.run_groovy_script(script_filepath=script_filepath,
                                               json_return=False,
                                               REST=REST,
                                               **kwargs)
        if not success:
            return False
        return True
