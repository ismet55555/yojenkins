"""Credential class definition"""

import json
import logging
import os
import xml.etree.ElementTree as ET
from json.decoder import JSONDecodeError
from typing import Dict, Tuple

from json2xml import json2xml
from urllib3.util import parse_url

from yojenkins.utility import utility
from yojenkins.utility.utility import fail_out
from yojenkins.yo_jenkins.jenkins_item_template import JenkinsItemTemplate

# Getting the logger reference
logger = logging.getLogger()


class Credential():
    """Credential class"""

    def __init__(self, rest) -> None:
        """Object constructor method, called at object creation

        Args:
            None

        Returns:
            None
        """
        self.rest = rest

    @staticmethod
    def _get_folder_store(folder: str) -> Tuple[str, str]:
        """Utility method to get credential folder name and domain

        Args:
            folder: folder name or url

        Returns:
            Folder nae and store name
        """
        if folder and utility.is_full_url(folder):
            folder = utility.url_to_name(folder)
            store = 'folder'
            logger.debug(f'Credential folder name or url passed. Using effective store: "{store}"')
        if folder in ['root', '.']:
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
        """Utility method to get credential domain name

        Args:
            domain: Credential domain name

        Returns:
            Effective domain name
        """
        domain_effective = domain
        if domain in ["global"]:
            domain_effective = "_"
            logger.debug(f'Credential domain passed: "{domain}". Using effective domain: "{domain_effective}"')
        return domain_effective

    @staticmethod
    def _get_folder_store_domain_from_url(credential_url: str) -> Tuple[str, str, str]:
        """Utility method to get folder name, store name and domain from a credential URL

        Details:
            Example credential_url formats:
                - /job/my-folder/credentials/store/folder/domain/_/credential/<CRED-ID>/
                - /credentials/store/system/domain/_/credential/<CRED-ID>
                - /./credentials/store/folder/domain/_/credential/<CRED-ID>/

        Args:
            credential_url: Credential url

        Returns:
            Folder name, store name and domain
        """
        parsed_path = parse_url(credential_url).path.strip('/').split('/')
        key_words = ['credentials', 'store', 'domain']
        if any(x in parsed_path for x in key_words):
            # Folder
            credential_index = parsed_path.index('credentials')
            if credential_index > 2:
                logger.debug('Failed to parse the credential URL. "credentials" keyword in URL in wrong position')
                return "", "", ""
            elif credential_index == 2:
                folder = "job/" + parsed_path[credential_index - 1]
            else:
                folder = "."

            # Store
            store_index = parsed_path.index('store')
            store = parsed_path[store_index + 1]

            # Domain
            domain_index = parsed_path.index('domain')
            domain = parsed_path[domain_index + 1]
        else:
            logger.debug(
                f'The credential URL "{credential_url}" path does not contain any of the expected keywords: {key_words}'
            )
            return "", "", ""
        logger.debug(
            f'Successfully parsed the credential URL. Folder: "{folder}", Store: "{store}", Domain: "{domain}"')

        return folder, store, domain

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
        credentials_info, _, success = self.rest.request(target=target,
                                                         request_type='get',
                                                         is_endpoint=True,
                                                         json_content=True)
        if not success:
            fail_out('Failed to get any credentials')

        if "credentials" not in credentials_info:
            fail_out('Failed to find "credentials" section in request return content')
        credential_list = credentials_info["credentials"]
        if not any(credential_list):
            fail_out('No credentials listed for the specified folder or domain')

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
        logger.debug(f"Getting credential info for: {credential} ...")
        is_endpoint = True

        # Check if credential is a url or name/ID
        if utility.is_full_url(credential):
            logger.debug('Using direct credential URL ...')
            target = f'{credential.strip("/")}/api/json'
            is_endpoint = False

            folder, store, domain = self._get_folder_store_domain_from_url(credential)
            credential_url = credential
        else:
            folder_original = folder
            folder, store = self._get_folder_store(folder)
            domain = self._get_domain(domain)

            credentials_list, _ = self.list(domain=domain, keys="displayName,id", folder=folder_original)
            credential_ids_match = []
            for credential_item in credentials_list:
                for key_name in ['displayName', 'id', 'fullName']:
                    if credential_item.get(key_name) == credential.lower():
                        credential_ids_match.append(credential_item["id"])
                        logger.debug(f'Successfully found credential matching '
                                     f'{key_name} "{credential}" ({credential_item["id"]})')

            if not credential_ids_match:
                fail_out(f'Failed to find any credentials matching display name or ID: {credential}')
            if len(credential_ids_match) > 1:
                logger.debug(f'More than one matching credential found. '
                             f'Using the first one: {credential_ids_match[0]}')
            target = f'{folder}/credentials/store/{store}/domain/{domain}/credential/{credential_ids_match[0]}/api/json'
            credential_url = f'{self.rest.server_url}{folder}/credentials/store/{store}/domain/{domain}/credential/{credential_ids_match[0]}'

        logger.debug('Getting all credential info with the following info:')
        logger.debug(f'   - Folder:     {folder}')
        logger.debug(f'   - Store:      {store}')
        logger.debug(f'   - Domain:     {domain}')
        logger.debug(f'   - Credential: {credential}')

        # Get credential info
        credential_info, _, success = self.rest.request(target=target,
                                                        request_type='get',
                                                        is_endpoint=is_endpoint,
                                                        json_content=True)
        if not success:
            fail_out('Failed to get credential information')

        # Add URL to the credential info
        credential_info['url'] = credential_url

        return credential_info

    def config(self,
               credential: str,
               folder: str = None,
               domain: str = None,
               filepath: str = None,
               opt_json: bool = False,
               opt_yaml: bool = False,
               opt_toml: bool = False) -> str:
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
        """
        folder, store = self._get_folder_store(folder)
        domain = self._get_domain(domain)

        credential_info = self.info(credential=credential, folder=folder, domain=domain)
        credential_id = credential_info.get('id')
        if not credential_id:
            fail_out('Failed to find "id" key within credential information')

        # If URL passed, parse out folder and domain
        if utility.is_full_url(credential):
            folder, store, domain = self._get_folder_store_domain_from_url(credential)

        target = f'{folder}/credentials/store/{store}/domain/{domain}/credential/{credential_id}/config.xml'
        logger.debug(f'Fetching XML configurations for credential: "{credential_id}" ...')
        return_content, _, success = self.rest.request(target=target,
                                                       request_type='get',
                                                       json_content=False,
                                                       is_endpoint=True)
        logger.debug('Successfully fetched XML configurations' if success else 'Failed to fetch XML configurations')

        if filepath:
            write_success = utility.write_xml_to_file(return_content, filepath, opt_json, opt_yaml, opt_toml)
            if not write_success:
                fail_out('Failed to write configuration file')

        return return_content

    def get_template(self,
                     cred_type: str,
                     filepath: str = None,
                     opt_json: bool = False,
                     opt_yaml: bool = False,
                     opt_toml: bool = False) -> str:
        """Get the template file for a credential type

        Args:
            cred_type: Credential type
            filepath: Path to the template to be written
            opt_json: Write in JSON format
            opt_yaml: Write in YAML format
            opt_toml: Write in TOML format

        Returns:
            Template string and file write success
        """
        # Get the template file
        template = JenkinsItemTemplate.CREDENTIAL.value[cred_type]
        template = template.strip(os.linesep)

        if filepath:
            write_success = utility.write_xml_to_file(template, filepath, opt_json, opt_yaml, opt_toml)
            if not write_success:
                fail_out('Failed to write configuration file')

        return template

    def create(self, config_file: str, folder: str, domain: str) -> bool:
        """Create a credential

        Args:
            config_file: Local path to file of the credential configuration
            folder: folder name or url
            store: store name
            domain: domain name

        Returns:
            True if credential created, else False
        """
        logger.debug(f'Opening and reading file: {config_file} ...')
        try:
            with open(config_file, 'rb') as open_file:
                credential_config = open_file.read()
        except (OSError, IOError, PermissionError) as error:
            fail_out(f'Failed to open and read file: {config_file}  Exception: {error}')

        try:
            cred_config_dict = json.loads(credential_config)
            logger.debug('Configuration file passed is in JSON format')
            logger.debug('Converting JSON file to XML format ...')

            # Convert to XML, remove root XML tag, and converting to string
            credential_config_xml = json2xml.Json2xml(cred_config_dict, pretty=False, wrapper="root",
                                                      attr_type=False).to_xml()
            credential_config_xml = list(ET.fromstring(credential_config_xml))[0]
            credential_config_xml = ET.tostring(credential_config_xml,
                                                encoding='utf8',
                                                method='xml',
                                                xml_declaration=False)
        except JSONDecodeError as error:
            logger.debug('Configuration file passed is in XML format')
            credential_config_xml = credential_config

        folder, store = self._get_folder_store(folder)
        domain = self._get_domain(domain)

        # # TEMPLATE WORK
        # test = utility.template_apply(string_template=CRED_USER_PASS, is_json=True,
        #                             domain=domain,
        #                             username='some-username',
        #                             password='MYPASSWORD',
        #                             description=description)
        # print(test)

        target = f'{folder}/credentials/store/{store}/domain/{domain}/createCredentials'
        _, _, success = self.rest.request(target=target,
                                          request_type='post',
                                          json_content=False,
                                          is_endpoint=True,
                                          headers={'Content-Type': 'application/xml; charset=utf-8'},
                                          data=credential_config_xml)
        if not success:
            fail_out('Failed to create credential')
        logger.debug('Successfully created credential')

        return success

    def delete(self, credential: str, folder: str = None, domain: str = None) -> bool:
        """Delete a credential

        Args:
            credential: Credential name, url, or ID
            folder: Credential folder name or url
            domain: Credential domain name

        Returns:
            True if credential deleted, else False
        """
        folder, store = self._get_folder_store(folder)
        domain = self._get_domain(domain)

        credential_info = self.info(credential=credential, folder=folder, domain=domain)
        if not credential_info:
            fail_out('Failed to get credential information. No folder name or folder url received')

        credential_id = credential_info.get('id')
        if not credential_id:
            fail_out('Failed to find "id" key within credential information')

        target = f'{folder}/credentials/store/{store}/domain/{domain}/credential/{credential_id}/config.xml'
        _, _, success = self.rest.request(target=target, request_type='delete', is_endpoint=True)
        if not success:
            fail_out('Failed to delete credential')
        logger.debug('Successfully deleted credential')

        return success
