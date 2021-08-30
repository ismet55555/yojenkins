#!/usr/bin/env python3

import json
import logging
import os
from json.decoder import JSONDecodeError
from typing import Dict, Tuple

from json2xml import json2xml
from urllib3.util import parse_url

from yo_jenkins.Utility import utility
from yo_jenkins.YoJenkins.JenkinsItemTemplate import JenkinsItemTemplate

# Getting the logger reference
logger = logging.getLogger()


class Account():
    """TODO Account"""

    def __init__(self, REST) -> None:
        """Object constructor method, called at object creation

        Args:
            None

        Returns:
            None
        """
        self.REST = REST
        self.script_location = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'groovy_scripts')

    def _run_groovy_script(self, script_filename: str, json_return: bool, **kwargs) -> Tuple[dict, bool]:
        """Run a Groovy script and return the response as JSON

        Details:
            A failed Groovy script execution will return a list/array in the following format:
            `['yo-jenkins groovy script failed', '<GROOVY EXCEPTION>', '<CUSTOM ERROR MESSAGE>']`

        Args:
            script_filename: Name of the Groovy script to run
            json_return: Anticipate and format script return as JSON
            kwargs (dict): Any variables to be inserted into the script text

        Returns:
            Response from the script
            Success flag
        """
        # Getting the path to the Groovy script, load as text
        script_filepath = os.path.join(self.script_location, script_filename)
        logger.debug(f'Loading Groovy script: {script_filepath}')
        try:
            with open(script_filepath, 'r') as open_file:
                script = open_file.read()
        except (FileNotFoundError, IOError) as error:
            logger.debug(f'Failed to find or read specified script file ({script_filepath}). Exception: {error}')
            return {}, False

        # Apply passed kwargs to the string template
        if kwargs:
            script = utility.template_apply(string_template=script, is_json=False, **kwargs)
            if not script:
                return {}, False

        # Send the request to the server
        logger.debug(f'Running the following Groovy script on server: {script_filepath} ...')
        script_result, _, success = self.REST.request(target='scriptText',
                                                      request_type='post',
                                                      data={'script': script},
                                                      json_content=False)
        if not success:
            logger.debug('Failed server REST request for Groovy script execution')
            return {}, False

        # print(script_result)

        # Check for yo-jenkins Groovy script error flag
        if "yo-jenkins groovy script failed" in script_result:
            groovy_return = eval(script_result.strip(os.linesep))
            logger.debug(f'Failed to execute Groovy script')
            logger.debug(f'Groovy Exception: {groovy_return[1]}')
            logger.debug(groovy_return[2])
            return {}, False

        # Check for script exception
        exception_keywords = ['Exception', 'java:']
        if any(exception_keyword in script_result for exception_keyword in exception_keywords):
            logger.debug(f'Error keyword matched in script response: {exception_keywords}')
            return {}, False

        # Parse script result as JSON
        if json_return:
            try:
                script_result = json.loads(script_result)
            except JSONDecodeError as error:
                logger.debug(f'Failed to parse response to JSON format')
                return {}, False

        return script_result, True

    def list(self) -> Tuple[list, list]:
        """List all accounts for the server

        Args:
            None

        Returns:
            List of credentials in dictionary format and a list of credential names
        """
        account_list, success = self._run_groovy_script(script_filename='user_list.groovy', json_return=True)
        if not success:
            return [], []

        # Get a list of only account ids
        account_list_id = [account["id"] for account in account_list if "id" in account]

        logger.debug(f'Number of user accounts found: {len(account_list)}')
        logger.debug(f'Found the following user account ids: {account_list_id}')

        return account_list, account_list_id

    def info(self, user_id: str) -> dict:
        """Get information about an account

        Args:
            user_id: User account ID

        Returns:
            Dictionary of account information
        """
        user_list, success = self._run_groovy_script(script_filename='user_list.groovy', json_return=True)
        if not success:
            return {}

        for user in user_list:
            if user['id'] == user_id:
                logger.debug(f'Successfully found account: {user_id}')
                return user

        logger.debug(f'Failed to find account: {user_id}')
        return {}

    def create(self, user_id: str, password: str, is_admin: str, email: str, description: str) -> bool:
        """Create a new user account

        Args:
            user_id: Username
            password: Password
            is_admin: Is admin
            email: Email
            description: Description

        Returns:
            True if the account was created, False otherwise
        """
        # Must use Groovy type boolean and null
        is_admin = 'true' if is_admin else 'false'
        email = '' if not email else email
        description = '' if not description else description

        # Create kwargs
        kwargs = {
            'user_id': user_id,
            'password': password,
            'is_admin': is_admin,
            'email': email,
            'description': description
        }

        _, success = self._run_groovy_script(script_filename='user_create.groovy', json_return=False, **kwargs)
        if not success:
            return False
        return True

    def delete(self, user_id: str) -> bool:
        """Delete a user account

        Args:
            user_id: Username of account to be deleted

        Returns:
            True if the account was deleted, False otherwise
        """
        # Create kwargs
        kwargs = {'user_id': user_id}

        _, success = self._run_groovy_script(script_filename='user_delete.groovy', json_return=False, **kwargs)
        if not success:
            return False
        return True

    def permission(self, user_id: str, action: str, permission_id: str) -> bool:
        """Add or remove user account permissions

        Details:
            The permission name can be a comma separated list of permission names

        Args:
            user_id: Username of account to be deleted
            action: Action to perform, either 'add' or 'remove'
            permission_id: Permission name to add or remove (can be a comma separated list)

        Returns:
            True if the permissions were added, False otherwise
        """
        # Parse comma seperated string
        permission_list = utility.parse_and_check_input_string_list(permission_id, join_back_char=', ')
        permission_groovy_list = "[" + permission_list + "]"

        if action == 'add':
            logger.debug(f'Adding the following permissions to user "{user_id}": {permission_list}')
            kwargs = {
                'user_id': user_id,
                'permission_groovy_list': permission_groovy_list,
                'permission_enabled': 'true'
            }
        elif action == 'remove':
            logger.debug(f'Removing the following permissions from user "{user_id}": {permission_list}')
            kwargs = {
                'user_id': user_id,
                'permission_groovy_list': permission_groovy_list,
                'permission_enabled': 'false'
            }
        else:
            logger.debug(f'Invalid permission action specified: {action}')
            return False

        _, success = self._run_groovy_script(script_filename='user_permission_add_remove.groovy',
                                             json_return=False,
                                             **kwargs)
        if not success:
            return False
        return True

    def permission_list(self) -> Tuple[list, list]:
        """Get all the available permissions and descriptions

        Args:
            None

        Returns:
            Dictionary of availabe permissions and descriptions
        """
        permission_list, success = self._run_groovy_script(script_filename='user_permission_list.groovy',
                                                           json_return=True)
        if not success:
            return {}

        # Get a list of only permission ids
        permission_list_id = [permission["id"] for permission in permission_list if "id" in permission]

        logger.debug(f'Number of permission found: {len(permission_list)}')
        logger.debug(f'Found the following permission ids: {permission_list_id}')

        return permission_list, permission_list_id
