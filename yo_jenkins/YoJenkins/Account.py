#!/usr/bin/env python3

import json
import logging
import os
import xml.etree.ElementTree as ET
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
        self.script_location = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'account_scripts')

    def _run_groovy_script(self, script_filename: str) -> Tuple[dict, bool]:
        """Run a groovy script and return the response as JSON

        Details:
            The groovy script must return a result in JSON format

        Args:
            script_filename: Name of the groovy script to run

        Returns:
            Response from the script
            Success flag
        """
        # Getting the path to the groovy script
        script_filepath = os.path.join(self.script_location, script_filename)
        try:
            with open(script_filepath, 'r') as open_file:
                script = open_file.read()
        except (FileNotFoundError, IOError) as error:
            logger.debug(f'Failed to find or read specified script file ({script_filepath}). Exception: {error}')
            return {}, False

        # Send the request to the server
        logger.debug(f'Running the following groovy script on server: {script_filepath} ...')
        script_result, _, success = self.REST.request(target='scriptText',
                                                      request_type='post',
                                                      data={'script': script},
                                                      json_content=False)
        if not success:
            logger.debug('Failed to get any account')
            return {}, False

        # Check for script exception
        exception_keywords = ['Exception', 'java:']
        if any(exception_keyword in script_result for exception_keyword in exception_keywords):
            logger.debug(f'Error keyword matched in script response: {exception_keywords}')
            return {}, False

        # Parse script result as JSON
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
        # Run the groovy script
        account_list, success = self._run_groovy_script('list_all.groovy')
        if not success:
            return [], []

        # Get a list of only account names
        account_list_id = [account["id"] for account in account_list if "id" in account]

        logger.debug(f'Number of accounts found: {len(account_list)}')
        logger.debug(f'Found the following account names: {account_list_id}')

        return account_list, account_list_id

    def info(self, account_id: str) -> dict:
        """Get information about an account

        Args:
            account_id: Account ID

        Returns:
            Dictionary of account information
        """
        # Run the groovy script
        account_list, success = self._run_groovy_script(f'list_all.groovy')
        if not success:
            return {}

        for account in account_list:
            if account['id'] == account_id:
                logger.debug(f'Successfully found account: {account_id}')
                return account

        logger.debug(f'Failed to find account: {account_id}')
        return {}
