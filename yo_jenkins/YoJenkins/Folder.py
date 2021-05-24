#!/usr/bin/env python3

import logging
import re
from pprint import pprint
from time import time
from typing import Dict, List, Tuple, Type

import jenkins
import utility

from .JenkinsItemClasses import JenkinsItemClasses


# Getting the logger reference
logger = logging.getLogger()

class Folder():
    """TODO Folder"""

    def __init__(self, REST, JenkinsSDK) -> None:
        """Object constructor method, called at object creation

        Args:
            None

        Returns:
            None
        """
        self.REST = REST
        self.JenkinsSDK = JenkinsSDK

        # Recursive search results
        self.search_results = []
        self.search_items_count = 0

        self.EMPTY_VIEW_CONFIG_XML = '''<?xml version="1.0" encoding="UTF-8"?>
        <hudson.model.ListView>
        <name>EMPTY</name>
        <filterExecutors>false</filterExecutors>
        <filterQueue>false</filterQueue>
        <properties class="hudson.model.View$PropertyList"/>
        <jobNames>
            <comparator class="hudson.util.CaseInsensitiveComparator"/>
        </jobNames>
        <jobFilters/>
        <columns>
            <hudson.views.StatusColumn/>
            <hudson.views.WeatherColumn/>
            <hudson.views.JobColumn/>
            <hudson.views.LastSuccessColumn/>
            <hudson.views.LastFailureColumn/>
            <hudson.views.LastDurationColumn/>
            <hudson.views.BuildButtonColumn/>
        </columns>
        </hudson.model.ListView>'''


    def __recursive_search(self, search_pattern:str, search_list:list, level:int, fullname:bool=True) -> None:
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
            if list_item['_class'] in JenkinsItemClasses.folder.value['class_type']:

                # Get fullname if specified and available, else get name
                if fullname:
                    dict_key = "fullname" if "fullname" in list_item else "name"
                else:
                    dict_key = 'name'

                # Match the regex pattern
                try:
                    if re.search(search_pattern, list_item[dict_key], re.IGNORECASE):
                        self.search_results.append(list_item)
                except re.error as e:
                    logger.debug(f'Error while applying REGEX pattern "{search_pattern}" to "{list_item[dict_key]}". Exception: {e}')
                    break

            # Count items searched for record
            self.search_items_count += 1

            # Check if the item has subitems
            if not 'jobs' in list_item:
                continue

            # Keep searching all sub-items for this item. Call itself for some recursion fun
            self.__recursive_search(search_pattern, list_item['jobs'], level, fullname)


    def search(self, search_pattern:str, folder_name:str='', folder_url:str='', folder_depth:int=4, fullname:bool=True) -> Tuple[list, list]:
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
        start_time = time()
        logger.debug(f'Folder search pattern: {search_pattern}')

        # Get all the jobs
        if folder_name or folder_url:
            # Only recursively search the specified folder name
            logger.debug(f'Searching folder in sub-folder "{folder_name if folder_name else folder_url}"')
            logger.debug(f'Folder depth does not apply. Only looking in this specific folder for subfolders')
            items = self.item_list(folder_name=folder_name, folder_url=folder_url)[0]
        else:
            # Search entire Jenkins
            logger.debug(f'Searching folder in ALL Jenkins. Folder depth: "{folder_depth}"')
            items = self.JenkinsSDK.get_all_jobs(folder_depth=folder_depth, folder_depth_per_request=20)

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
        logger.debug(f'Searched folders: {self.search_items_count}. Search time: {time() - start_time} seconds')

        return self.search_results, folder_search_results_list


    def info(self, folder_name:str='', folder_url:str='') -> Dict:
        """Get the folder information

        Args:
            folder_name : Folder name to get folder information of
            folder_url  : Folder URL to get the folder information of

        Returns:
            Folder information
        """
        if not folder_name and not folder_url:
            logger.debug('Failed to get folder information. No folder name or folder url received')
            return {}

        if folder_name and not folder_url:
            folder_url = utility.name_to_url(self.REST.get_server_url(), folder_name)

        folder_info, _, success = self.REST.request(
            folder_url.strip('/') + '/api/json',
            'get',
            is_endpoint=False
            )
        if not success:
            logger.debug(f'Failed to find folder info: {folder_url}')
            return {}

        # Check if found item type/class
        if folder_info['_class'] not in JenkinsItemClasses.folder.value['class_type'] and JenkinsItemClasses.folder.value['item_type'] not in folder_info:
            logger.warning(f'Failed to match type/class. This item is "{folder_info["_class"]}"')
            return {}

        return folder_info


    def subfolder_list(self, folder_name:str='', folder_url:str='') -> Tuple[list, list]:
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
        if not folder_info:
            return [], []

        # Extract lists
        sub_folder_list, sub_folder_list_url = utility.item_subitem_list(
            item_info=folder_info, 
            get_key_info='url', 
            item_type=JenkinsItemClasses.folder.value['item_type'], 
            item_class_list=JenkinsItemClasses.folder.value['class_type']
            )

        logger.debug(f'Number of subfolders found: {len(sub_folder_list)}')
        logger.debug(f'Sub-folders: {sub_folder_list_url}')

        return sub_folder_list, sub_folder_list_url


    def jobs_list(self, folder_name:str='', folder_url:str='') -> Tuple[list, list]:
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
        if not folder_info:
            return [], []

        # Extract lists
        job_list, job_list_url = utility.item_subitem_list(
            item_info=folder_info,
            get_key_info='url',
            item_type=JenkinsItemClasses.job.value['item_type'],
            item_class_list=JenkinsItemClasses.job.value['class_type']
            )

        logger.debug(f'Number of jobs found: {len(job_list)}')
        logger.debug(f'Jobs: {job_list_url}')

        return job_list, job_list_url


    def view_list(self, folder_name:str='', folder_url:str='') -> Tuple[list, list]:
        """Get the list of all views within the specified folder

        Args:
            folder_name : Folder name to get all its views
            folder_url  : Folder URL to get all its views

        Returns:
            List of views, information list and URL list
        """
        # Get the folder information
        folder_info = self.info(folder_name=folder_name, folder_url=folder_url)
        if not folder_info:
            return [], []

        logger.debug(f'Getting all view items for folder "{folder_name if folder_name else folder_url}" ...')

        view_list, view_list_url = utility.item_subitem_list(
            item_info=folder_info,
            get_key_info='url',
            item_type=JenkinsItemClasses.view.value['item_type'],
            item_class_list=JenkinsItemClasses.view.value['class_type']
            )

        logger.debug(f'Number of views found: {len(view_list)}')
        logger.debug(f'Views: {view_list_url}')

        return view_list, view_list_url


    def item_list(self, folder_name:str='', folder_url:str='') -> Tuple[list, list]:
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
        if not folder_info:
            return [], []

        # Getting all possible Jenkins items listed enum
        all_subitems = [e.value for e in JenkinsItemClasses]

        # Searching folder info for matches
        all_item_list = []
        all_item_url = []
        for item in all_subitems:
            logger.debug(f'Searching folder for "{item["item_type"]}" items ...')
            item_list, item_list_url = utility.item_subitem_list(
                item_info=folder_info,
                get_key_info='url',
                item_type=item['item_type'],
                item_class_list=item['class_type']
                )
            if item_list:
                logger.debug(f'Successfully found {len(item_list)} "{item["item_type"]}" items')
                all_item_list.extend(item_list)
                all_item_url.extend(item_list_url)
            else:
                logger.debug(f'No "{item["item_type"]}" items found in this folder')

        logger.debug(f'Number of folder items found: {len(all_item_list)}')
        logger.debug(f'Items: {all_item_url}')

        return all_item_list, all_item_url


    def browser_open(self, folder_name:str='', folder_url:str='') -> bool:
        """Get the list of all items within the specified folder

        Args:
            folder_name : Folder name to get all its items
            folder_url  : Folder URL to get all its items

        Returns:
            True if successfull, else False
        """
        if not folder_name and not folder_url:
            logger.debug('Failed to get folder information. No folder name or folder url received')
            return False

        if folder_url:
            folder_url = folder_url.strip('/')
        else:
            folder_url = utility.name_to_url(self.REST.get_server_url(), folder_name)

        logger.debug(f'Opening in web browser: "{folder_url}" ...')
        success = utility.browser_open(url=folder_url)
        logger.debug('Successfully opened in web browser' if success else 'Failed to open in web browser')
        return success


    def config(self, filepath:str='', folder_name:str='', folder_url:str='') -> Tuple[str, bool]:
        """Get the folder XML configuration (config.xml)

        Args:
            filepath    : If defined, store fetched data in this file
            folder_name : Folder name to get configurations
            folder_url  : Folder URL to get configurations

        Returns:
            Folder config.xml contents
            True if configuration written to file, else False
        """
        if not folder_name and not folder_url:
            logger.debug('Failed to get folder information. No folder name or folder url received')
            return '', False

        if folder_url:
            folder_url = folder_url.strip('/')
        else:
            folder_url = utility.name_to_url(self.REST.get_server_url(), folder_name)

        logger.debug(f'Fetching XML configurations for folder: "{folder_url}" ...')
        return_content, _, success = self.REST.request(
            f'{folder_url.strip("/")}/config.xml',
            'get',
            json_content=False,
            is_endpoint=False)
        logger.debug('Successfully fetched XML configurations' if success else 'Failed to fetch XML configurations')

        if filepath:
            logger.debug(f'Writing fetched configuration to "{filepath}" ...')
            try:
                with open(filepath, 'w+') as file:
                    file.write(return_content)
                logger.debug(f'Successfully wrote configurations to file')
            except Exception as e:
                logger.debug('Failed to write configurations to file. Exception: {e}')
                return return_content, False 

        return return_content, True


    def create(self, name:str, type:str='folder', xml_file:str='config.xml', folder_name:str='', folder_url:str='') -> bool:
        """TODO Docstring

        Args:
            TODO

        Returns:
            TODO
        """
        if not folder_name and not folder_url:
            logger.debug('Failed to get folder information. No folder name or folder url received')
            return False

        if folder_url:
            folder_url = folder_url.strip('/')
        else:
            folder_url = utility.name_to_url(self.REST.get_server_url(), folder_name)

        if not name:
            logger.debug('Item name is a blank')
            return False
        if utility.has_special_char(name):
            return False

        supported_create_items = ['folder', 'view', 'job']
        if type.strip().lower() not in supported_create_items:
            logger.debug(f'Failed to match supported items to create: {supported_create_items}')
            return False

        if type == 'folder':
            endpoint = f'createItem?name={name}'
            data = {
                "name": name,
                "mode": "com.cloudbees.hudson.plugins.folder.Folder"
            }
            headers = {}
        elif type == 'view':
            endpoint = f'createView?name={name}'
            data = self.EMPTY_VIEW_CONFIG_XML.encode('utf-8')
            headers={'Content-Type': 'text/xml; charset=utf-8'}
        elif type == 'job':
            endpoint = f'createItem?name={name}'
            data = {}
            headers={}
            # TODO

        logger.debug(f'Creating "{type}" item "{name}" ...')
        return_content, return_header, success = self.REST.request(
            f'{folder_url.strip("/")}/{endpoint}',
            'post',
            data=data,
            headers=headers,
            is_endpoint=False)
        logger.debug(f'Successfully created item "{name}"' if success else f'Failed to create item "{name}"')
        return success


    def copy(self, original_name:str, new_name:str, folder_name:str='', folder_url:str='') -> bool:
        """TODO Docstring

        Args:
            TODO

        Returns:
            TODO
        """
        if not folder_name and not folder_url:
            logger.debug('Failed to get folder information. No folder name or folder url received')
            return False

        if folder_url:
            folder_url = folder_url.strip('/')
        else:
            folder_url = utility.name_to_url(self.REST.get_server_url(), folder_name)

        if not original_name:
            logger.debug('Original item name is a blank')
            return False
        if utility.has_special_char(original_name):
            return False

        if not new_name:
            logger.debug('New item name is a blank')
            return False
        if utility.has_special_char(new_name):
            return False

        logger.debug(f'Copying original item "{original_name}" to new item "{new_name}" ...')
        success = self.REST.request(f'{folder_url.strip("/")}/createItem?name={new_name}&mode=copy&from={original_name}', 'post', is_endpoint=False)[2]
        logger.debug('Successfully copied item' if success else 'Failed to copy item')
        return success


    def delete(self, folder_name:str='', folder_url:str='') -> bool:
        """Delete folder

        Args:
            folder_name : Folder name to get all its items
            folder_url  : Folder URL to get all its items

        Returns:
            True if successfull, else False
        """
        if not folder_name and not folder_url:
            logger.debug('Failed to get folder information. No folder name or folder url received')
            return False

        if folder_url:
            folder_url = folder_url.strip('/')
        else:
            folder_url = utility.name_to_url(self.REST.get_server_url(), folder_name)

        logger.debug(f'Deleting folder: "{folder_url}" ...')
        success = self.REST.request(f'{folder_url.strip("/")}/doDelete', 'post', is_endpoint=False)[2]
        logger.debug('Successfully deleted folder' if success else 'Failed to delete folder')
        return success