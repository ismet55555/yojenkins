#!/usr/bin/env python3

import logging
from typing import Dict, Tuple

from yo_jenkins.Utility import utility

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

    def list(self, domain: str, keys: str, folder: str = None) -> Tuple[list, list]:
        """TODO Docstring

        Details: TODO

        Args:
            name: TODO

        Returns:
            TODO
        """
        # Get folder name and store name
        if folder and utility.is_full_url(folder):
            folder = utility.url_to_name(folder)
            store = 'folder'
            logger.debug(f'Credential folder name or url passed. Using effective store: "{store}"')
        if folder in ['root', '.', 'base']:
            folder = '.'
            store = 'system'
            logger.debug(f'Using effective credential folder name: "" = "{folder}"')
        else:
            folder = f"job/{folder}"
            store = 'folder'

        # Get domain
        domain_effective = domain
        if domain == "global":
            domain_effective = "_"
            logger.debug(f'Credential domain passed: "{domain}". Using effective domain: "{domain_effective}"')

        # Get return keys
        if keys in ["all", "*", "full"]:
            keys = "*"
        else:
            keys = utility.parse_and_check_input_string_list(keys, ',')

        logger.debug('Getting all credentials for the following:')
        logger.debug(f'   - Folder: {folder}')
        logger.debug(f'   - Store:  {store}')
        logger.debug(f'   - Domain: {domain}')
        logger.debug(f'   - Keys:   {keys}')

        target = f'{folder}/credentials/store/{store}/domain/{domain_effective}/api/json?tree=credentials[{keys}]'
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

    def info(self, credential: str, folder: str, domain: str) -> Dict:
        """TODO Docstring

        Details: TODO

        Args:
            credential: credential name, url, or ID
            folder: folder name or url
            store: store name
            domain: domain name

        Returns:
            Credential inforamation in dictionary format
        """
        is_endpoint = True
        if utility.is_full_url(credential):
            logger.debug(f'Using direct credential URL passed ...')
            target = f'{credential.strip("/")}/api/json'
            is_endpoint = False
        else:
            # Get folder name and store name
            if folder and utility.is_full_url(folder):
                folder = utility.url_to_name(folder)
                store = 'folder'
                logger.debug(f'Credential folder name or url passed. Using effective store: "{store}"')
            if folder in ['root', '.', 'base']:
                folder = '.'
                store = 'system'
                logger.debug(f'Using effective credential folder name: "" = "{folder}"')
            else:
                folder_original = folder
                folder = f"job/{folder}"
                store = 'folder'

            # Get domain
            domain_effective = domain
            if domain == "global":
                domain_effective = "_"
                logger.debug(f'Credential domain passed: "{domain}". Using effective domain: "{domain_effective}"')

            # Get credential ID if the name of credential is given
            if not utility.is_credential_id(credential):
                credentials_list, _ = self.list(domain=domain, keys="displayName,id", folder=folder_original)
                credential_ids_match = []
                for credential_item in credentials_list:
                    if credential_item['displayName'].lower() == credential.lower():
                        credential_ids_match.append(credential_item['id'])
                        logger.debug(f'Successfully found credential matching '
                                     f'display name "{credential}" ({credential_item["id"]})')

                if not credential_ids_match:
                    logger.debug(f'Failed to find any credentials matching display name: {credential}')
                    return {}

                if len(credential_ids_match) > 1:
                    logger.debug(f'More than one matching credential found. '
                                 f'Using the first one: {credential_ids_match[0]}')
                credential = credential_ids_match[0]

            logger.debug('Getting all credential info with the following info:')
            logger.debug(f'   - Folder:     {folder}')
            logger.debug(f'   - Store:      {store}')
            logger.debug(f'   - Domain:     {domain}')
            logger.debug(f'   - Credential: {credential}')

            target = f'{folder}/credentials/store/{store}/domain/{domain_effective}/credential/{credential}/api/json'

        credential_info, _, success = self.REST.request(target=target,
                                                        request_type='get',
                                                        is_endpoint=is_endpoint,
                                                        json_content=True)
        if not success:
            logger.debug('Failed to get any credentials')
            return [], []

        return credential_info
