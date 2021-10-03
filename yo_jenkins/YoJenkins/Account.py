"""Account class definition"""

import logging
import os
from typing import Tuple

from yo_jenkins.Utility import utility

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
        self.groovy_script_directory = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'groovy_scripts')

    def list(self) -> Tuple[list, list]:
        """List all accounts for the server

        Args:
            None

        Returns:
            List of credentials in dictionary format and a list of credential names
        """
        script_filepath = os.path.join(self.groovy_script_directory, 'user_list.groovy')
        account_list, success = utility.run_groovy_script(script_filepath=script_filepath,
                                                          json_return=True,
                                                          REST=self.REST)
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
        script_filepath = os.path.join(self.groovy_script_directory, 'user_list.groovy')
        user_list, success = utility.run_groovy_script(script_filepath=script_filepath,
                                                       json_return=True,
                                                       REST=self.REST)
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
        kwargs = {
            'user_id': user_id,
            'password': password,
            'is_admin': 'true' if is_admin else 'false',
            'email': '' if not email else email,
            'description': '' if not description else description
        }
        script_filepath = os.path.join(self.groovy_script_directory, 'user_create.groovy')
        _, success = utility.run_groovy_script(script_filepath=script_filepath,
                                               json_return=False,
                                               REST=self.REST,
                                               **kwargs)
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
        kwargs = {'user_id': user_id}
        script_filepath = os.path.join(self.groovy_script_directory, 'user_delete.groovy')
        _, success = utility.run_groovy_script(script_filepath=script_filepath,
                                               json_return=False,
                                               REST=self.REST,
                                               **kwargs)
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

        script_filepath = os.path.join(self.groovy_script_directory, 'user_permission_add_remove.groovy')
        _, success = utility.run_groovy_script(script_filepath=script_filepath,
                                               json_return=False,
                                               REST=self.REST,
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
        script_filepath = os.path.join(self.groovy_script_directory, 'user_permission_list.groovy')
        permission_list, success = utility.run_groovy_script(script_filepath=script_filepath,
                                                             json_return=True,
                                                             REST=self.REST)
        if not success:
            return [], []

        # Get a list of only permission ids
        permission_list_id = [permission["id"] for permission in permission_list if "id" in permission]

        logger.debug(f'Number of permission found: {len(permission_list)}')
        logger.debug(f'Found the following permission ids: {permission_list_id}')

        return permission_list, permission_list_id
