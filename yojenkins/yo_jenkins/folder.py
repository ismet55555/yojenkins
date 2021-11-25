"""Folder class definition"""

import json
import logging
import re
from time import perf_counter
from typing import Dict, Tuple

import xmltodict

from yojenkins.utility import utility
from yojenkins.utility.utility import fail_out
from yojenkins.yo_jenkins.jenkins_item_classes import JenkinsItemClasses
from yojenkins.yo_jenkins.jenkins_item_config import JenkinsItemConfig

# Getting the logger reference
logger = logging.getLogger()


class Folder():
    """TODO Folder"""

    def __init__(self, rest, JenkinsSDK) -> None:
        """Object constructor method, called at object creation

        Args:
            None

        Returns:
            None
        """
        self.rest = rest
        self.jenkins_sdk = JenkinsSDK

        # Recursive search results
        self.search_results = []
        self.search_items_count = 0

    def __recursive_search(self, search_pattern: str, search_list: list, level: int, fullname: bool = True) -> None:
        """Recursive search method for folders

        Details: Matched pattern findings are storred in the object: `self.search_results`

        Args:
            search_pattern : REGEX pattern to match for each item
            search_list    : List of items
            level          : Current recursion level
            fullname       : Search the entire path of the item, not just the item name

        Returns:
            None
        """
        # Current directory level
        level += 1

        # Loop through all sub-folders
        for list_item in search_list:
            # print(level, "   " * level, list_item['name'])

            # Check if folder
            if list_item['_class'] in JenkinsItemClasses.FOLDER.value['class_type']:

                # Get fullname if specified and available, else get name
                if fullname:
                    dict_key = "fullname" if "fullname" in list_item else "name"
                else:
                    dict_key = 'name'

                # Match the regex pattern
                try:
                    if re.search(search_pattern, list_item[dict_key], re.IGNORECASE):
                        self.search_results.append(list_item)
                except re.error as error:
                    logger.debug(
                        f'Error while applying REGEX pattern "{search_pattern}" to "{list_item[dict_key]}". Exception: {error}'
                    )
                    break

            # Count items searched for record
            self.search_items_count += 1

            # Check if the item has subitems
            if not 'jobs' in list_item:
                continue

            # Keep searching all sub-items for this item. Call itself for some recursion fun
            self.__recursive_search(search_pattern, list_item['jobs'], level, fullname)

    def search(self,
               search_pattern: str,
               folder_name: str = '',
               folder_url: str = '',
               folder_depth: int = 4,
               fullname: bool = True) -> Tuple[list, list]:
        """Search the server for folders matching REGEX pattern

        Args:
            search_pattern : REGEX search pattern to match
            folder_name    : (Optional) Only look within this folder for matching sub-folder using item name
            folder_url     : (Optional) Only look within this folder for matching sub-folder using item URL
            folder_depth   : Number of levels to look through
            fullname       : Search the entire path of the item, not just the item name

        Returns:
            List of folder found. Both, list of info and list of folder URLs
        """
        # Start a timer to time the search
        start_time = perf_counter()
        logger.debug(f'Folder search pattern: {search_pattern}')

        # Get all the jobs
        if folder_name or folder_url:
            # Only recursively search the specified folder name
            logger.debug(f'Searching folder in sub-folder "{folder_name if folder_name else folder_url}"')
            logger.debug('Folder depth does not apply. Only looking in this specific folder for subfolders')
            items = self.item_list(folder_name=folder_name, folder_url=folder_url)[0]
        else:
            # Search entire Jenkins
            logger.debug(f'Searching folder in ALL Jenkins. Folder depth: "{folder_depth}"')
            items = self.jenkins_sdk.get_all_jobs(folder_depth=folder_depth, folder_depth_per_request=20)

        # Search for any matching folders ("jobs")
        self.search_items_count = 0
        self.search_results = []
        self.__recursive_search(search_pattern=search_pattern, search_list=items, level=0, fullname=fullname)

        # Remove duplicates from list (THANKS GeeksForGeeks.org)
        logger.debug('Removing duplicates if needed ...')
        self.search_results = [i for n, i in enumerate(self.search_results) if i not in self.search_results[n + 1:]]

        # Collect URLs only
        folder_search_results_list = []
        for search_result in self.search_results:
            folder_search_results_list.append(search_result['url'])

        # Output search stats
        logger.debug(
            f'Searched folders: {self.search_items_count}. Search time: {perf_counter() - start_time:.3f} seconds')

        return self.search_results, folder_search_results_list

    def info(self, folder_name: str = '', folder_url: str = '') -> Dict:
        """Get the folder information

        Args:
            folder_name : Folder name to get folder information of
            folder_url  : Folder URL to get the folder information of

        Returns:
            Folder information
        """
        if not folder_name and not folder_url:
            fail_out('Failed to get folder information. No folder name or folder url received')

        if folder_name and not folder_url:
            folder_url = utility.name_to_url(self.rest.get_server_url(), folder_name)

        folder_info, _, success = self.rest.request(folder_url.strip('/') + '/api/json',
                                                    request_type='get',
                                                    is_endpoint=False)
        if not success:
            fail_out(f'Failed to find folder info: {folder_url}')

        # Check if found item type/class
        if folder_info['_class'] not in JenkinsItemClasses.FOLDER.value[
                'class_type'] and JenkinsItemClasses.FOLDER.value['item_type'] not in folder_info:
            fail_out(f'Folder found, but failed to match type/class. This item is "{folder_info["_class"]}"')

        return folder_info

    def subfolder_list(self, folder_name: str = '', folder_url: str = '') -> Tuple[list, list]:
        """Get the list of all sub-folders within the specified folder

        Args:
            folder_name : Folder name to get all its sub-folders
            folder_url  : Folder URL to get all its sub-folders

        Returns:
            List of subfolders, information list and URL list
        """
        logger.debug(f'Getting subfolders for folder name "{folder_name if folder_name else folder_url}" ...')

        # Get the folder information
        folder_info = self.info(folder_name=folder_name, folder_url=folder_url)

        # Extract lists
        sub_folder_list, sub_folder_list_url = utility.item_subitem_list(
            item_info=folder_info,
            get_key_info='url',
            item_type=JenkinsItemClasses.FOLDER.value['item_type'],
            item_class_list=JenkinsItemClasses.FOLDER.value['class_type'])

        logger.debug(f'Number of subfolders found in folder: {len(sub_folder_list)}')
        logger.debug(f'Sub-folders: {sub_folder_list_url}')

        return sub_folder_list, sub_folder_list_url

    def jobs_list(self, folder_name: str = '', folder_url: str = '') -> Tuple[list, list]:
        """Get the list of all jobs within the specified folder

        Args:
            folder_name : Folder name to get all its jobs
            folder_url  : Folder URL to get all its jobs

        Returns:
            List of jobs, information list and URL list
        """
        logger.debug(f'Getting jobs for folder name "{folder_name if folder_name else folder_url}" ...')

        # Get the folder information
        folder_info = self.info(folder_name=folder_name, folder_url=folder_url)

        # Extract lists
        job_list, job_list_url = utility.item_subitem_list(item_info=folder_info,
                                                           get_key_info='url',
                                                           item_type=JenkinsItemClasses.JOB.value['item_type'],
                                                           item_class_list=JenkinsItemClasses.JOB.value['class_type'])

        logger.debug(f'Number of jobs found within folder: {len(job_list)}')
        logger.debug(f'Jobs: {job_list_url}')

        return job_list, job_list_url

    def view_list(self, folder_name: str = '', folder_url: str = '') -> Tuple[list, list]:
        """Get the list of all views within the specified folder

        Args:
            folder_name : Folder name to get all its views
            folder_url  : Folder URL to get all its views

        Returns:
            List of views, information list and URL list
        """
        # Get the folder information
        folder_info = self.info(folder_name=folder_name, folder_url=folder_url)

        logger.debug(f'Getting all view items for folder "{folder_name if folder_name else folder_url}" ...')
        view_list, view_list_url = utility.item_subitem_list(
            item_info=folder_info,
            get_key_info='url',
            item_type=JenkinsItemClasses.VIEW.value['item_type'],
            item_class_list=JenkinsItemClasses.VIEW.value['class_type'])

        logger.debug(f'Number of views found in folder: {len(view_list)}')
        logger.debug(f'Views: {view_list_url}')

        return view_list, view_list_url

    def item_list(self, folder_name: str = '', folder_url: str = '') -> Tuple[list, list]:
        """Get the list of all items within the specified folder

        Args:
            folder_name : Folder name to get all its items
            folder_url  : Folder URL to get all its items

        Returns:
            List of items, information list and URL list
        """
        # TODO: Potentially combine folder_folders_list and folder_jobs_list, folder_view_list with this method

        logger.debug(f'Getting items for folder "{folder_name if folder_name else folder_url}" ...')

        # Get the folder information
        folder_info = self.info(folder_name=folder_name, folder_url=folder_url)

        # Getting all possible Jenkins items listed enum
        all_subitems = [subitem.value for subitem in JenkinsItemClasses]

        # Searching folder info for matches
        all_item_list = []
        all_item_url = []
        for item in all_subitems:
            logger.debug(f'Searching folder for "{item["item_type"]}" items ...')
            item_list, item_list_url = utility.item_subitem_list(item_info=folder_info,
                                                                 get_key_info='url',
                                                                 item_type=item['item_type'],
                                                                 item_class_list=item['class_type'])
            if item_list:
                logger.debug(f'Successfully found {len(item_list)} "{item["item_type"]}" items')
                all_item_list.extend(item_list)
                all_item_url.extend(item_list_url)
            else:
                logger.debug(f'No "{item["item_type"]}" items found in this folder')

        logger.debug(f'Number of folder items found in folder: {len(all_item_list)}')
        logger.debug(f'Items: {all_item_url}')

        return all_item_list, all_item_url

    def browser_open(self, folder_name: str = '', folder_url: str = '') -> bool:
        """Get the list of all items within the specified folder

        Args:
            folder_name : Folder name to get all its items
            folder_url  : Folder URL to get all its items

        Returns:
            True if successfull, else False
        """
        if not folder_name and not folder_url:
            fail_out('Failed to get folder information. No folder name or folder url received')

        if folder_url:
            folder_url = folder_url.strip('/')
        else:
            folder_url = utility.name_to_url(self.rest.get_server_url(), folder_name)

        logger.debug(f'Opening folder in web browser: "{folder_url}" ...')
        success = utility.browser_open(url=folder_url)
        if not success:
            fail_out('Failed to open folder in web browser')
        logger.debug('Successfully opened folder in web browser')

        return success

    def config(self,
               filepath: str = '',
               folder_name: str = '',
               folder_url: str = '',
               opt_json: bool = False,
               opt_yaml: bool = False,
               opt_toml: bool = False) -> str:
        """Get the folder configuration (ie .config.xml)

        Args:
            filepath    : If defined, store fetched data in this file
            folder_name : Folder name to get configurations
            folder_url  : Folder URL to get configurations
            opt_json    : If True, return data as JSON
            opt_yaml    : If True, return data as YAML
            opt_toml    : If True, return data as TOML

        Returns:
            Folder config.xml contents
        """
        if not folder_name and not folder_url:
            fail_out('Failed to get folder information. No folder name or folder url received')

        if folder_url:
            folder_url = folder_url.strip('/')
        else:
            folder_url = utility.name_to_url(self.rest.get_server_url(), folder_name)

        logger.debug(f'Fetching XML configurations for folder: "{folder_url}" ...')
        return_content, _, success = self.rest.request(f'{folder_url.strip("/")}/config.xml',
                                                       'get',
                                                       json_content=False,
                                                       is_endpoint=False)
        if not success:
            fail_out('Failed to get folder configuration')
        logger.debug('Successfully fetched folder configuration')

        if filepath:
            write_success = utility.write_xml_to_file(return_content, filepath, opt_json, opt_yaml, opt_toml)
            if not write_success:
                fail_out('Failed to write configuration file')

        return return_content

    def create(self,
               name: str,
               type: str = 'folder',
               folder_name: str = '',
               folder_url: str = '',
               config: str = 'config.xml',
               config_is_json: bool = False) -> bool:
        """TODO Docstring

        Args:
            TODO

        Returns:
            TODO
        """
        if not folder_name and not folder_url:
            fail_out('Failed to get folder information. No folder name or folder url received')

        if folder_url:
            folder_url = folder_url.strip('/')
        else:
            folder_url = utility.name_to_url(self.rest.get_server_url(), folder_name)

        if not name:
            fail_out('The item name is a blank')
        if utility.has_special_char(name):
            fail_out('The item name contains special characters')

        supported_create_items = ['folder', 'view', 'job']
        if type.strip().lower() not in supported_create_items:
            fail_out(f'Failed to match supported "{type}" items to create: {", ".join(supported_create_items)}')

        if config:
            # Use item configuration from file if provided
            logger.debug(f'Opening and reading "{type}" item configuration file: {config} ...')
            try:
                open_file = open(config, 'rb')
                item_config = open_file.read()
            except (OSError, IOError, PermissionError) as error:
                fail_out(f'Failed to open and read "{type}" item configuration file. Exception: {error}')

            if config_is_json:
                logger.debug('Converting the specified JSON file to XML format ...')
                try:
                    item_config = xmltodict.unparse(json.loads(item_config))
                except ValueError as error:
                    fail_out(f'Failed to convert the specified JSON file to XML format. Exception: {error}')
        else:
            # Use blank item config
            # FIXME: These are not valid XML configs, try json instead
            # FIXME: This does not account for the name of the item
            if type == 'folder':
                endpoint = f'createItem?name={name}'
                item_config = JenkinsItemConfig.FOLDER.value['blank']
                # prefix = JenkinsItemClasses.FOLDER.value['prefix']
            elif type == 'view':
                endpoint = f'createView?name={name}'
                item_config = JenkinsItemConfig.VIEW.value['blank']
                # prefix = JenkinsItemClasses.VIEW.value['prefix']
            elif type == 'job':
                endpoint = f'createItem?name={name}'
                item_config = JenkinsItemConfig.JOB.value['blank']
                # prefix = JenkinsItemClasses.JOB.value['prefix']

        # Checking if the item exists
        if utility.item_exists_in_folder(name, folder_url, type, self.rest):
            fail_out(f'The new "{type}" item "{name}" exists within the folder')

        # Creating the item
        logger.debug(f'Creating "{type}" item "{name}" ...')
        headers = {'Content-Type': 'application/xml; charset=utf-8'}
        success = self.rest.request(f'{folder_url.strip("/")}/{endpoint}',
                                    'post',
                                    data=item_config.encode('utf-8'),
                                    headers=headers,
                                    is_endpoint=False)[2]
        if not success:
            fail_out(f'Failed to create "{type}" item "{name}"')
        logger.debug(f'Successfully created "{type}" item "{name}"')

        # Close the potentially open item configuration file
        try:
            if 'open_file' in locals():
                open_file.close()
        except (OSError, IOError):
            pass

        return success

    def copy(self, original_name: str, new_name: str, folder_name: str = '', folder_url: str = '') -> bool:
        """TODO Docstring

        Args:
            TODO

        Returns:
            TODO
        """
        if not folder_name and not folder_url:
            fail_out('Failed to get folder information. No folder name or folder url received')

        if folder_url:
            folder_url = folder_url.strip('/')
        else:
            folder_url = utility.name_to_url(self.rest.get_server_url(), folder_name)

        if not original_name:
            fail_out('The original folder name is a blank')
        if utility.has_special_char(original_name):
            fail_out('The original folder name contains special characters')

        if not new_name:
            fail_out('New folder name is a blank')
        if utility.has_special_char(new_name):
            fail_out('The new folder name contains special characters')

        if not utility.item_exists_in_folder(original_name, folder_url, "folder", self.rest):
            fail_out(f'The original folder "{original_name}" does not exist')

        logger.debug(f'Copying original item "{original_name}" to new item "{new_name}" ...')
        success = self.rest.request(
            f'{folder_url.strip("/")}/createItem?name={new_name}&mode=copy&from={original_name}',
            'post',
            is_endpoint=False)[2]
        if not success:
            fail_out('Failed to copy folder')
        logger.debug('Successfully copied folder')

        return success

    def delete(self, folder_name: str = '', folder_url: str = '') -> bool:
        """Delete folder

        Args:
            folder_name : Folder name to get all its items
            folder_url  : Folder URL to get all its items

        Returns:
            True if successfull, else False
        """
        if not folder_name and not folder_url:
            fail_out('Failed to get folder information. No folder name or folder url received')

        if folder_url:
            folder_url = folder_url.strip('/')
        else:
            folder_url = utility.name_to_url(self.rest.get_server_url(), folder_name)

        logger.debug(f'Deleting folder: "{folder_url}" ...')
        success = self.rest.request(f'{folder_url.strip("/")}/doDelete', 'post', is_endpoint=False)[2]
        if not success:
            fail_out('Failed to delete folder')
        logger.debug('Successfully deleted folder')

        return success
