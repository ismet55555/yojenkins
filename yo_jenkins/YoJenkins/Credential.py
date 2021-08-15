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

    @staticmethod
    def _get_folder_store(folder: str) -> Tuple[str, str]:
        """Utility method to get credential folder name and domain"""
        if folder and utility.is_full_url(folder):
            folder = utility.url_to_name(folder)
            store = 'folder'
            logger.debug(f'Credential folder name or url passed. Using effective store: "{store}"')
        if folder in ['root', '.', 'base']:
            folder = '.'
            store = 'system'
            logger.debug(f'Using effective credential folder name: "" = "{folder}"')
        else:
            if "job/" not in folder:
                folder = f"job/{folder}"
            store = 'folder'
        return folder, store

    @staticmethod
    def _get_domain(domain: str) -> str:
        """Utility method to get credential domain name"""
        domain_effective = domain
        if domain == "global":
            domain_effective = "_"
            logger.debug(f'Credential domain passed: "{domain}". Using effective domain: "{domain_effective}"')
        return domain_effective

    def list(self, domain: str, keys: str, folder: str = None) -> Tuple[list, list]:
        """List all credentials for the specified folder and domain

        Details:
            - Available credentials key may change over time
            - May use the Web UI to get a sense what the domain is for a credential

        Args:
            domain: Credential domain name
            keys: Credential keys to list
            folder: Credential folder name

        Returns:
            List of credentials in dictionary format and a list of credential names
        """
        folder, store = self._get_folder_store(folder)
        domain = self._get_domain(domain)

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

        target = f'{folder}/credentials/store/{store}/domain/{domain}/api/json?tree=credentials[{keys}]'
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
        logger.debug(f'Found the following credential names: {credential_list_name}')

        return credential_list, credential_list_name

    def info(self, credential: str, folder: str, domain: str) -> Dict:
        """Getting credential info

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
            folder_original = folder
            folder, store = self._get_folder_store(folder)
            domain = self._get_domain(domain)

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

            target = f'{folder}/credentials/store/{store}/domain/{domain}/credential/{credential}/api/json'

        credential_info, _, success = self.REST.request(target=target,
                                                        request_type='get',
                                                        is_endpoint=is_endpoint,
                                                        json_content=True)
        if not success:
            logger.debug('Failed to get credential information')
            return [], []

        return credential_info

    def config(self,
               credential: str,
               folder: str = None,
               domain: str = None,
               filepath: str = None,
               opt_json: bool = False,
               opt_yaml: bool = False,
               opt_toml: bool = False) -> Tuple[str, bool]:
        """Get the folder configuration (ie .config.xml)

        Args:
            credential: Credential name, url, or ID
            folder: Credential folder name or url
            domain: Credential domain name
            filepath: Path to the file to be written
            opt_json: Write in JSON format
            opt_yaml: Write in YAML format
            opt_toml: Write in TOML format

        Returns:
            Folder config.xml contents
            True if configuration written to file, else False
        """
        folder, store = self._get_folder_store(folder)
        domain = self._get_domain(domain)

        # `<SERVER>/credentials/store/<STORE>/domain/<DOMAIN>/credential/<CRED ID>/config.xml`
        credential_info = self.info(credential=credential, folder=folder, domain=domain)
        if not credential_info:
            logger.debug('Failed to get credential information. No folder name or folder url received')
            return '', False

        credential_id = credential_info.get('id')
        if not credential_id:
            logger.debug('Failed to find "id" key within credential information')
            return '', False

        target = f'{folder}/credentials/store/{store}/domain/{domain}/credential/{credential_id}/config.xml'
        logger.debug(f'Fetching XML configurations for credential: "{credential_id}" ...')
        return_content, _, success = self.REST.request(target=target,
                                                       request_type='get',
                                                       json_content=False,
                                                       is_endpoint=True)
        logger.debug('Successfully fetched XML configurations' if success else 'Failed to fetch XML configurations')

        if filepath:
            write_success = utility.write_xml_to_file(return_content, filepath, opt_json, opt_yaml, opt_toml)
            if not write_success:
                return "", False

        return return_content, True
