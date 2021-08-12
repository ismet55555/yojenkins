#!/usr/bin/env python3

import json
import logging
import os
from typing import Tuple

import toml
import xmltodict
import yaml
from yo_jenkins.Utility import utility
from yo_jenkins.YoJenkins.JenkinsItemClasses import JenkinsItemClasses

# Getting the logger reference
logger = logging.getLogger()


class Credential():
    """TODO Credential"""

    def __init__(self, REST) -> None:
        """Object constructor method, called at object creation

        Args:
            None

        Returns:
            None
        """
        self.REST = REST

    def list(self, store: str, domain: str, keys: str, folder_name: str = None, folder_url: str = None) -> bool:
        """TODO Docstring

        Details: TODO

        Args:
            name: TODO

        Returns:
            TODO
        """
        # Get folder name
        folder_name_effective = "555"
        if (not folder_name and not folder_url) or folder_name == "root":
            folder_name_effective = '.'
            logger.debug(f'No or root folder passed. Using effective folder name: "{folder_name}"')
        else:
            if folder_url:
                folder_name = utility.url_to_name(folder_url)
            folder_name_effective = f"job/{folder_name}"
            store = 'folder'
            logger.debug(f'Folder name or url passed. Using effective store: "{store}"')

        # Get domain
        domain_effective = domain
        if domain == "global":
            domain_effective = "_"
            logger.debug(f'"{domain}" domain passed. Using effective domain: "{domain_effective}"')

        # Get return keys
        if keys in ["all", "*", "full"]:
            keys = "*"
        else:
            keys = utility.parse_and_check_input_string_list(keys, ',')

        logger.debug('Getting all credentials for the following:')
        logger.debug(f'   - Folder: {folder_name if folder_name else folder_url}')
        logger.debug(f'   - Store:  {store}')
        logger.debug(f'   - Domain: {domain}')
        logger.debug(f'   - Keys:   {keys}')

        target = f'{folder_name_effective}/credentials/store/{store}/domain/{domain_effective}/api/json?tree=credentials[{keys}]'
        credentials_info, _, success = self.REST.request(target=target,
                                                         request_type='get',
                                                         is_endpoint=True,
                                                         json_content=True)
        if not success:
            logger.debug('Failed to get any credentials')
            return [], []

        if "credentials" not in credentials_info:
            logger.debug('Failed to find "credentials" section in return content')
            return [], []
        credential_list = credentials_info["credentials"]
        if not any(credential_list):
            logger.debug('No credentials listed')
            return [], []

        # Get a list of only credentail names
        credential_list_name = [
            credential["displayName"] for credential in credential_list if "displayName" in credential
        ]

        logger.debug(f'Number of credentials found: {len(credential_list)}')
        logger.debug(f'Credentials ids: {credential_list_name}')

        return credential_list, credential_list_name
