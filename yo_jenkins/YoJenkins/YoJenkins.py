#!/usr/bin/env python3

import logging
import os
import re
from datetime import datetime, timedelta
from getpass import getpass
from pathlib import Path
from pprint import pprint
from time import sleep, time
from typing import Dict, List, Tuple, Type
from urllib.parse import urlencode, urlparse

import jenkins
import requests
import utility
import yaml
import click
from jenkins import Jenkins as JenkinsSDK
from Monitor import Monitor
from requests.auth import HTTPBasicAuth

from . import colors
from .JenkinsItemClasses import JenkinsItemClasses
from .Status import BuildStatus, StageStatus

# Getting the logger reference
logger = logging.getLogger()


class YoJenkins:
    """This class defines the YoJenkins and its methods.

    The YoJenkins class abstract python-jenkins module and Jenkins server API calls
    """

    def __init__(self) -> None:
        """Object constructor method, called at object creation

        Args:
            None

        Returns:
            None
        """

        # Request session
        self.req_session = requests.Session()

        # Project root directory
        self.ROOT_DIR = os.getcwd()

        # Configuration file name
        self.cred_config_dir = Path.home()
        self.cred_config_filename: str = '.yo-jenkins.conf'

        # Authentication Info
        self.jenkins_profile: dict = {}
        self.jenkins_api_token: str = ''
        self.authenticated: bool = False

        self.profile_env_var: str = 'YOJENKINS_PROFILE'
        self.required_top_level_key: str = 'profiles'

        self.user_info: dict = {}

        # Data
        self.build_temp_console_output: str = ''  # Not used
        self.stage_temp_console_output: str = ''  # Not used

        # Jenkins API object reference
        self.J:Type[JenkinsSDK] = None

        # Recursive search result temp variable
        self.search_items_count: int = 0
        self.search_results: list = []

        # Monitoring
        self.Monitor:Type[Monitor] = None
        self.build_info_monitor_enabled: bool = False
        self.build_info_monitor_data: dict = {}



    ###########################################################################
    #                            UTILITY
    ###########################################################################

    def __REST_request(self, request_url:str, request_type:str='get', json_content:bool=True, auth:Tuple=(), new_session:bool=False, params:dict={}, headers:dict={}) -> Tuple[Dict, Dict, bool]:
        """Utility method for single REST requests

        Args:
            request_url  : Request URL
            request_type : Type of request. Currently `get` and `post` only
            json_content : If True, parse as json/dict, else return raw content text
            auth         : Credentials in (username, password) format
            new_session  : If True, create a new connection sessions, else re-use previous/default session
            params       : Parameters passed with the request
            headers      : Headers passed with the request

        Returns:
            Tuple of return content, return header, return success
        """
        if not auth:
            auth=HTTPBasicAuth(self.jenkins_profile['username'], self.jenkins_api_token)

        # Use a connection session if possible
        if not self.req_session or new_session:
            self.req_session = requests.Session()

        # Making the request
        try:
            elapsed_time = time()
            if request_type.lower() == 'get':
                request_return = self.req_session.get(request_url, params=params, headers=headers, auth=auth, timeout=10)
            elif request_type.lower() == 'post':
                request_return = self.req_session.post(request_url, params=params, headers=headers, auth=auth, timeout=10)
            elif request_type.lower() == 'head':
                request_return = self.req_session.head(request_url, params=params, headers=headers, auth=auth, timeout=10)
            else:
                logger.debug(f'Request type "{request_type}" not recognized')
                return {}, {}, False
        except requests.exceptions.ConnectionError as e:
            logger.debug(f'Failed to make request. Connection Error. Exception: {e}')
            return {}, {}, False
        logger.debug(f'Request elapsed time: {time() - elapsed_time} seconds')
        
        # Check the return status code
        logger.debug(f'Request return status code: {request_return.status_code}')
        if not request_return.ok:
            logger.debug(f'Failed to make {request_type.upper()} request "{request_url}". Server code: {request_return.status_code}')
            return {}, {}, False
        success = True

        # Get the return header
        return_headers: dict = {}
        if request_return.headers:
            return_headers = request_return.headers
            logger.debug(f'Request return headers: {return_headers}')
        else:
            logger.debug(f'No headers received form {request_type.upper()} request: {request_url}')

        # If a head request, only return headers
        if request_type.lower() == 'head':
            return {}, return_headers, success

        # Get the return content and format it
        return_content = {}
        if request_return.content:
            if json_content:
                # Check for json parsing errors
                try:
                    return_content = request_return.json()
                except Exception as e:
                    # TODO: Specify json parse error
                    logger.debug(f"Failed to parse request return as JSON. Possible HTML content. Exception: {e})")
            else:
                return_content = request_return.text
        else:
            logger.debug(f'No content received form {request_type.upper()} request: {request_url}')

        return return_content, return_headers, success


    def __update_profiles(self, profiles:dict) -> bool:
        """Create/Update the current credentials profile file

        Details: This method will overwrite any previous file content.
                 It will also add a file prefix for yaml formats

        Args:
            profiles : All profile info to be written to file

        Returns:
            True if successfull, else False
        """
        # Storing configurations in file
        output_path = os.path.join(self.cred_config_dir, self.cred_config_filename)
        logger.debug(f'Saving new file: "{output_path}" ...')
        with open(os.path.join(output_path), 'w') as file:  # Overwrite previous content
            yaml.dump(profiles, file)

        # Add top file prefix for yaml file format
        lines_new = [
            f'# -*- mode: yaml -*-{os.linesep}',
            f'# vim: set filetype=yaml{os.linesep}',
            f'---{os.linesep * 3}'
        ]
        success = utility.append_lines_to_beginning_of_file(output_path, lines_new)
        if not success:
            return False

        return True


    def __recursive_search(self, search_type:str, search_pattern:str, search_list:list, nested_key:str, level:int) -> None:
        """Recursive search method for folders and jobs

        Details: Matched pattern findings are storred in the object: `self.search_results`

        Args:
            search_type    : What to search. Either `folder` or `job`
            search_pattern : REGEX pattern to match for each item
            search_list    : List of items
            nested_key     : Not used
            level          : Current recursion level

        Returns:
            None
        """
        # Current directory level
        level += 1

        # Loop through all sub-folders
        for list_item in search_list:
            # print(level, "   " * level, list_item['name'])

            if search_type == 'folder':
                # Check if the item is a job
                # If it has "jobs" section, if not, this is a job and not a folder
                if not 'jobs' in list_item or list_item['_class'] in JenkinsItemClasses.job.value['class_type']:
                    continue
            
                # Get fullname, else get name
                dict_key = "fullname" if "fullname" in list_item else "name"
                #dict_key = 'name'

                # Match the regex pattern
                try:
                    if re.search(search_pattern, list_item[dict_key], re.IGNORECASE):
                        self.search_results.append(list_item)
                except re.error as e:
                    logger.debug(f'Error while applying REGEX pattern "{search_pattern}" to "{list_item[dict_key]}". Exception: {e}')
                    break

                # Count items searched for record
                self.search_items_count += 1

            elif search_type == 'job':
                # Check if this is a job
                # Check if the item has "jobs" section, if not, this is a job
                if not 'jobs' in list_item or list_item['_class'] in JenkinsItemClasses.job.value['class_type']:
                    # Pick fullname description if available
                    dict_key = "fullname" if "fullname" in list_item else "name"
                    #dict_key = "name"

                    # Match the regex pattern
                    try:
                        if re.search(search_pattern, list_item[dict_key], re.IGNORECASE):
                            self.search_results.append(list_item)
                    except re.error as e:
                        logger.debug(f'Error while applying REGEX pattern "{search_pattern}" to "{list_item[dict_key]}". Exception: {e}')
                        break

                    # Count items searched for record
                    self.search_items_count += 1

                    # Keep searching, on to next item in search_list
                    continue
            else:
                logger.debug('Search specified a unknown search pattern. Only "folder" and "jobs" supported')
                break
                
            # Keep searching all sub-items for this item. Call itself for some recursion fun
            self.__recursive_search(search_type, search_pattern, list_item['jobs'], nested_key, level)



    ###########################################################################
    #                         AUTHENTICATION
    ###########################################################################

    def auth_generate_token(self, token_name:str='', server_base_url:str='', username:str='', password:str='') -> str:
        """Generate a Jenkins server API token with the specified server/username

        Args:
            token_name      : (Optional) Name of new API token. Will prompt if not passed.
            server_base_url : (Optional) Server base URL. Will prompt if not passed.
            username        : (Optional) Username. Will prompt if not passed.
            password        : (Optional) Password. Will prompt if not passed.

        Returns:
            Server API Token
        """
        # Ask for anything not passed
        if not token_name:
            prompt_text = colors.BOLD + colors.YELLOW + f"Enter desired API TOKEN NAME: " + colors.NORMAL
            token_name = input(prompt_text)
            logger.debug(f'User input: {token_name}')

        if not server_base_url:
            prompt_text = colors.BOLD + colors.YELLOW + f"Enter Jenkins SERVER BASE URL: " + colors.NORMAL
            server_base_url = input(prompt_text)
            logger.debug(f'User input: {server_base_url}')

        if not username:
            prompt_text = colors.BOLD + colors.YELLOW + 'Enter Jenkins server USERNAME: ' + colors.NORMAL
            username = input(prompt_text)
            logger.debug(f'User input: {username}')

        if not password:
            prompt_text = colors.BOLD + colors.YELLOW + f'Enter "{username}" PASSWORD: ' + colors.NORMAL
            password = getpass(prompt=prompt_text, stream=None)
            logger.debug('User entered password')

        # Requesting the Jenkins crumb
        # params = (('xpath', 'concat/(//crumbRequestField,":",//crumb/)'))
        request_return_text, _, success = self.__REST_request(
            request_url=server_base_url.strip('/') + '/crumbIssuer/api/xml',
            request_type='get', 
            json_content=False, 
            auth=(username, password), 
            new_session=True
            )
        if not success:
            return
        crumb_value = re.sub(re.compile('<.*?>|Jenkins-Crumb'), '', request_return_text)
        logger.debug(f'Request crumb value: {crumb_value}')

        # Generating the token
        headers = {'Jenkins-Crumb': crumb_value}
        params = (
            ('newTokenName', token_name),
            ('tree', 'data[tokenValue]'),
        )
        request_return_content, _, success = self.__REST_request(
            request_url=server_base_url.strip('/') + '/me/descriptorByName/jenkins.security.ApiTokenProperty/generateNewToken/api/json', 
            request_type='post',
            json_content=True,
            auth=(username, password),
            new_session=False,
            params=params,
            headers=headers
            )
        if not success: return

        try:
            generated_token = request_return_content['data']['tokenValue']
            logger.debug(f'Successfully generated server API token "{token_name}"!')
        except Exception as e:
            logger.debug('Failed to find "tokenValue" in the POST request return header')
            generated_token = ''

        return generated_token


    def auth_profile_add_new_token(self, profile_name:str) -> str:
        """Update the specified credentials profile with a new server API token

        Args:
            profile_name : Name of the profile as specified in the credentials file

        Returns:
            Server API Token
        """
        # Check if the credential config file exists
        file_exists, file_path = self.auth_detect_configuration_file()
        if not file_exists:
            return

        # Load the current cred config file
        profiles = utility.load_contents_from_local_yaml_file(file_path)
        if not profiles:
            return

        # Check if passed profile is part of the credential config file
        logger.debug(f'Currently listed profile names: {", ".join(list(profiles[self.required_top_level_key].keys()))}')
        if profile_name not in profiles[self.required_top_level_key]:
            logger.debug(f'Failed to find the --profile specified profile name ("{profile_name}") in the credential configuration file')
            return

        profile_info = profiles[self.required_top_level_key][profile_name]
        logger.debug(f'Profile {profile_name} loaded')
        logger.debug(f'Profile info: {profile_info}')

        # Generate a API token name (seen in Jenkins UI)
        token_name = f'yo-jenkins_{datetime.now().strftime("%m-%d-%Y_%I-%M-%S")}'

        # Check if needed information is listed in the profile
        if 'jenkins_server_url' not in profile_info:
            logger.debug(f'No "jenkins_server_url" key listed in profile')
            server_url = ''
        else:
            server_url = profile_info['jenkins_server_url']
        if 'username' not in profile_info:
            logger.debug(f'No "username" key listed in profile')
            username = ''
        else:
            username = profile_info['username']

        # Generate the api token
        api_token = self.auth_generate_token(
            token_name=token_name,
            server_base_url=server_url,
            username=username
        )
        if not api_token:
            return

        # Store the API token
        profiles[self.required_top_level_key][profile_name]['api_token'] = api_token

        success = self.__update_profiles(profiles=profiles)
        if not success:
            logger.debug(f'Failed to add/update new API token to profile {profile_name}')
            return

        return api_token


    def auth_configure(self, api_token:str='') -> bool:
        """Configure/add a new credentials profile

        Details: This method will prompt the user with a series of questions
                 to add a new profile to the credentials profile file

        Args:
            api_token : (Optional) Server API token to be added to the new profile

        Returns:
            This is a description of what is returned.
        """
        # Checking if credential config file exists
        file_exists, file_path = self.auth_detect_configuration_file()
        if file_exists:
            logger.debug(f'Credentials file found in current user home directory: {file_path}')
            logger.debug(f'Loading credentials file: {file_path} ...')
            
            # Load the current cred config file
            profiles = utility.load_contents_from_local_yaml_file(file_path)
            if not profiles:
                return False

            # Check if top level / parent key is in the config cred file
            if self.required_top_level_key not in profiles.keys():
                logger.debug(f'The loaded credentials configuration file does not include a "{self.required_top_level_key}" section')
                return False
            logger.debug(f'Currently listed profile names: {", ".join(list(profiles[self.required_top_level_key].keys()))}')

            # Adding the profile
            print('')
            print(f'Credentials profile file ({self.cred_config_filename}) found in current user home directory')
            print(f'Adding a new profile to the current credentials profile file ...')
            print('Please enter the following information to add a profile:')
            print('')
        else:
            logger.debug(f'Credentials file NOT found in current user home directory')
            logger.debug(f'Creating credentials file in current user home directory: {self.cred_config_filename} ...')

            # Create new profile from scratch
            profiles = {}
            profiles[self.required_top_level_key] = {}

            print('')
            print(f'Credentials profile file ({self.cred_config_filename}) NOT found in current user home directory')
            print('Creating a new credentials profile file ...')
            print('Please enter the following information to create your first profile:')
            print('')

        # Prompting user for details
        profile_name = input(
            colors.BOLD + colors.YELLOW + f'[ OPTIONAL ] Enter PROFILE NAME (default):  ' + colors.NORMAL
            )
        profile_name = 'default' if not profile_name else profile_name
        if profile_name in profiles[self.required_top_level_key]:
            print('')
            print(f'WARNING : You are about to overwrite the current profile "{profile_name}"')
            print('')
        profiles['profiles'][profile_name] = {}
        profiles['profiles'][profile_name]['jenkins_server_url'] = input(
            colors.BOLD + colors.YELLOW + f'[ REQUIRED ] Enter Jenkins SERVER BASE URL:  ' + colors.NORMAL
            )
        profiles['profiles'][profile_name]['username']           = input(
            colors.BOLD + colors.YELLOW + f'[ REQUIRED ] Enter USERNAME:  ' + colors.NORMAL
            )
        if not api_token:
            profiles['profiles'][profile_name]['api_token']       = input(
                colors.BOLD + colors.YELLOW + f'[ OPTIONAL ] Enter API TOKEN:  ' + colors.NORMAL
                )
        else:
            print('')
            print(colors.BOLD + 'WARNING: Adding provided API token to this profile' + colors.NORMAL)
            print('')
            profiles['profiles'][profile_name]['api_token'] = api_token
        profiles['profiles'][profile_name]['active'] = True 

        return self.__update_profiles(profiles=profiles)


    def auth_detect_configuration_file(self) -> Tuple[bool, str]:
        """Detect/find the credentials profile file in the home directory

        Args:
            None

        Returns:
            Success, File path of the credentials profile file
        """
        # Defining directories to look for
        files_in_home_dir = [f for f in os.listdir(Path.home()) if os.path.isfile(os.path.join(Path.home(), f))]

        # Seeing if configuration file is in specified directories
        if self.cred_config_filename  in files_in_home_dir:
            # Check if file exists in user home directory
            logger.debug(f'Configuration file "{self.cred_config_filename }" found in user home directory: {Path.home()}')
            config_filepath = os.path.join(Path.home(), self.cred_config_filename )
            return True, config_filepath
        else:
            logger.debug(f'Configuration file "{self.cred_config_filename }" NOT found in home directory')
            return False


    def auth_get_configurations(self, profile:str='') -> Dict:
        """Get the contents of the credentials profiles file

        Details: The order (preference) of specified profile credentials to get are the following:
            - Passed `profile` argument
            - Environmental Variable as specified in `self.profile_env_var`
            - Profile listed as `default` in the credentials profile file
            - Any other / first profile set to active

        Args:
            profile : (Optional) Only get the configuration for particular profile

        Returns:
            The credential information of the specified credentials profile
        """
        success, config_filepath = self.auth_detect_configuration_file()
        if not success:
            # If no configuration file found, configure one
            logger.debug(f'No credentials file found. Configuring one ...')
            success, config_filepath, self.auth_configure()
            if not success:
                return {}
        else:
            # Loading configurations file
            configs = utility.load_contents_from_local_yaml_file(config_filepath)
            if not configs:
                return {}

        # Check if top level parent profile section is there
        profile_top_key_name = ''
        required_top_level_key = ['prof', 'profile', 'profiles', 'creds', 'credential', 'credentials', 'stuff']
        for top_key_name in required_top_level_key:
            if top_key_name in list(configs.keys()):
                profile_top_key_name = top_key_name
                break
        if not profile_top_key_name:
            logger.critical(f'Failed to find the following top level key in configuration file: {required_top_level_key}')
            return {}
        logger.debug(f'Successfully found top level section key in the configuration file: "{profile_top_key_name}"')

        # Get the listed profiles
        profile_items_all = configs[profile_top_key_name]
        logger.debug(f'Number of listed profiles found: {len(profile_items_all)}')

        # Filter out the profiles that are misconfigured (missing keys)
        profile_items = {}
        required_profile_items = ['jenkins_server_url', 'username']
        logger.debug(f'Ignoring profiles that do not have at least the following keys: {required_profile_items} ...')
        for i, (profile_key, profile_values) in enumerate(profile_items_all.items()):
            if all(item in list(profile_values.keys()) for item in required_profile_items): 
                logger.debug(f'    - Profile {i+1} of {len(profile_items_all)}: "{profile_key}" - OK')
                profile_items[profile_key] = profile_values
            else:
                logger.debug(f'    - Profile {i+1} of {len(profile_items_all)}: "{profile_key}" - IGNORED')
        if not profile_items:
            logger.debug('Failed to find any valid profiles in the configuration file')
            return {}

        # Select the credential profile
        profile_selected = {}

        # 1 - Argument --profile
        if profile:
            if profile in profile_items:
                profile_selected = profile_items[profile]
                profile_selected['profile'] = profile
                logger.debug(f'Successfully matched specified --profile "{profile}"')
            else:
                logger.debug(f'Failed to find the profile specified with --profile "{profile}" in the profiles loaded')
                return {}
        else:
            logger.debug(f'Argument "--profile" was not specified')

        # 2 - Environmental Variable
        if not profile_selected:
            if self.profile_env_var in os.environ:
                profile = os.getenv(self.profile_env_var)
                if profile in profile_items:
                    profile_selected = profile_items[profile]
                    profile_selected['profile'] = profile
                    logger.debug(f'Successfully matched set {self.profile_env_var } environmental variable value "{profile}"')
                else:
                    logger.debug(f'Failed to find the set environmental variable {self.profile_env_var} "{profile}" in the profiles loaded')
                    return {}
            else:
                logger.debug(f'Environmental Variable "{self.profile_env_var}" not set')

        #3 - "default" profile
        if not profile_selected:
            profile = 'default'
            if profile in profile_items:
                profile_selected = profile_items[profile]
                profile_selected['profile'] = profile
                logger.debug(f'Successfully found "default" profile in the configuration file')
            else:
                logger.debug(f'Default profile "default" not found')

        #4 - Any other active one
        if not profile_selected:
            logger.debug('Selecting the first listed active profile ...')
            for profile, profile_values in profile_items.items():
                if 'active' in profile_values:
                    if profile_values['active'] == True:
                        profile_selected = profile_items[profile]
                        profile_selected['profile'] = profile
                        logger.debug(f'Successfully selected active profile: "{profile}"')
                        break

        if not profile_selected:
            logger.debug('No active profiles found')
            return {}

        # Show the partial info of the loaded profile
        self.jenkins_profile = profile_selected

        logger.debug(f'The following profile has been loaded (partial info shown):')
        logger.debug(f'   Profile:             {self.jenkins_profile["profile"]}')
        logger.debug(f'   Jenkins Server URL:  {self.jenkins_profile["jenkins_server_url"]}')
        logger.debug(f'   Username:            {self.jenkins_profile["username"]}')

        return profile_selected


    def auth_create_auth(self, profile_info:dict={}) -> bool:
        """Authenticate with the Jenkins server

        Details: If not server API token in the profile used, ask for token/password

        Args:
            profile_info : (Optional) Credentials profile information

        Returns:
            True if successfully authenticated, else False
        """
        # If the profile information is passed, use it
        if profile_info:
            self.jenkins_profile = profile_info

        if not self.jenkins_profile:
            logger.debug(f'No credential profile loaded')
            return False

        # Verify if the passed server URL is in correct format
        if not utility.uri_validator(self.jenkins_profile['jenkins_server_url']):
            logger.debug(f'The server URL "{self.jenkins_profile["jenkins_server_url"]}" is not in a valid format')
            return False

        # Check if password is listed, if not, ask for it
        if 'api_token' not in self.jenkins_profile or not self.jenkins_profile['api_token']:
            print('')
            prompt_text = colors.BOLD + colors.YELLOW + f'Profile {self.jenkins_profile["profile"]} does not contain a "api_token" key' + colors.NORMAL
            print(prompt_text)
            prompt_text = colors.BOLD + colors.YELLOW + f"Enter Jenkins password or server API Token for user {self.jenkins_profile['username']}: " + colors.NORMAL
            self.jenkins_profile['api_token'] = getpass(prompt=prompt_text, stream=None, )
            print('')
            # if len(self.jenkins_profile['api_token']) < 8:
            #     logger.debug(f'The entered API Token has a length of {len(self.jenkins_profile["api_token"])}, which is too short')
            #     return False

            # FIXME: Do not pass the prompt text to standard out of command. Pipling the result won't work!

        # Load the token or password
        self.jenkins_api_token = self.jenkins_profile['api_token']
        
        hidden_token = ''.join([ "*" for i in self.jenkins_api_token[:-6]]) + self.jenkins_api_token[-6:]
        # hidden_token = ''.join([ "*" for i in self.jenkins_profile['api_token'] ])
        logger.debug(f'   API Token:           {hidden_token}')

        # Connecting to Jenkins (Exception handling: jenkins.JenkinsException)
        logger.debug(f'Authenticating to Jenkins server: {urlparse(self.jenkins_profile["jenkins_server_url"]).netloc} ...')
        try:
            self.J = JenkinsSDK(
                url=self.jenkins_profile['jenkins_server_url'],
                username=self.jenkins_profile['username'],
                password=self.jenkins_profile['api_token'],
                timeout=5
                )
        except Exception as e:
            logger.debug(f'Failed to create Jenkins object. Exception: {e}')
            return False

        # Check network connection
        logger.debug(f'Checking if server is reachable ...')
        if not self.server_is_reachable():
            click.echo(click.style(f'Jenkins server connection failed (Server: {self.jenkins_profile["jenkins_server_url"]})', fg='bright_red', bold=True))
            click.echo(click.style(f'Possible causes:', fg='bright_red', bold=True))
            click.echo(click.style(f'  - Wrong Jenkins server URL: {self.jenkins_profile["jenkins_server_url"]}', fg='bright_red', bold=True))
            click.echo(click.style(f'  - Network/Internet is down', fg='bright_red', bold=True))
            click.echo(click.style('Possible solutions:', fg='bright_red', bold=True))
            click.echo(click.style('   - Fix yo network connection to server', fg='bright_red', bold=True))
            return False

        # Checking authentication
        logger.debug(f'Checking authentication to server ...')
        if not self.auth_verify_auth():
            # TODO: Move this message to cli_auth.py, only return bool
            click.echo(click.style(f'Jenkins server authentication failed (Username: {self.jenkins_profile["username"]})', fg='bright_red', bold=True))
            click.echo(click.style(f'Possible causes:', fg='bright_red', bold=True))
            click.echo(click.style(f'  - Wrong Jenkins server URL: {self.jenkins_profile["jenkins_server_url"]}', fg='bright_red', bold=True))
            click.echo(click.style(f'  - Incorrect username: {self.jenkins_profile["username"]}', fg='bright_red', bold=True))
            click.echo(click.style(f'  - Incorrect, removed, or expired API Token', fg='bright_red', bold=True))
            click.echo(click.style(f'  - Username, {self.jenkins_profile["username"]}, does not have permission', fg='bright_red', bold=True))
            click.echo(click.style('Possible solutions:', fg='bright_red', bold=True))
            click.echo(click.style('   - yo-jenkins auth token', fg='bright_red', bold=True))
            click.echo(click.style('   - yo-jenkins auth configure', fg='bright_red', bold=True))
            click.echo(click.style('   - Manually create or update credentials file in home directory', fg='bright_red', bold=True))
            click.echo(click.style('   - Go to Jenkins Web UI and check user configurations', fg='bright_red', bold=True))
            return False

        return True


    def auth_show_local_credentials(self) -> Dict:
        """Output/Display the credentials profile file

        Args:
            None

        Returns:
            Contents of the credentials profile file
        """
        success, config_filepath = self.auth_detect_configuration_file()
        if not success:
            # If no configuration file found
            return {}

        # Loading configurations file
        return utility.load_contents_from_local_yaml_file(config_filepath)


    def auth_verify_auth(self) -> bool:
        """Verify/Check if current credentials can authenticate with server

        Args:
            None

        Returns:
            True if successfully authenticated, else False
        """
        logger.debug(f'Verifying server authentication by requesting user information ...')
        request_url = self.jenkins_profile['jenkins_server_url'].strip('/') + "/me/api/json"
        _, _, request_success = self.__REST_request(request_url, 'head')
        if not request_success:
            logger.debug(f'Failed server authentication')
            return False
        logger.debug(f'Successfully authenticated')
        return True


    ###########################################################################
    #                               SERVER
    ###########################################################################

    def server_info(self) -> Dict:
        """Get the server information

        Details: Targeting the server that is specified in the selected profile

        Args:
            None

        Returns:
            Server information
        """
        return self.__REST_request(request_url=f'{self.jenkins_profile["jenkins_server_url"]}/api/json', request_type='get')[0]


    def server_user_info(self) -> Dict:
        """Get user information

        Details: Targeting the user that is specified in the selected profile

        Args:
            None

        Returns:
            User information
        """
        return self.__REST_request(request_url=f'{self.jenkins_profile["jenkins_server_url"]}/me/api/json')[0]


    def server_queue_info(self) -> Dict:
        """Get all the jobs stuck in the server queue

        (Potentially move to jobs or build section)

        Args:
            None

        Returns:
            Server queue information
        """
        # TODO: Replace requests call with jenkins-python module method
        # TODO: Combine with server_queue_list adding a list argument

        logger.debug(f'Requesting build queue info for "{self.jenkins_profile["jenkins_server_url"]}" ...')

        # Making the request
        request_url = f'{self.jenkins_profile["jenkins_server_url"]}/queue/api/json'
        return_content = self.__REST_request(request_url=request_url, request_type='get')[0]
        if not return_content:
            logger.debug('Failed to get server queue info. Check access and permissions for this endpoint')
        return return_content


    def server_queue_list(self) -> List[str]:
        """Get all list of all the jobs stuck in the server queue

        (Potentially move to jobs or build section)

        Args:
            None

        Returns:
            List of urls of jobs stuck in server queue
        """
        queue_info = self.server_queue_info()

        queue_list = []
        queue_job_url_list = []
        for queue_item in queue_info['items']:
            queue_list.append(queue_item)
            if 'url' in queue_item['task']:
                queue_job_url_list.append(queue_item['task']['url'])

        return queue_list


    def server_plugin_list(self) -> Tuple[list, list]:
        """Get the list of plugins installed on the server

        Args:
            None

        Returns:
            List of plugins, information list and URL list
        """
        logger.debug(f'Getting all installed server plugins for "{self.jenkins_profile["jenkins_server_url"]}" ...')

        try:
            plugin_info = self.J.get_plugins()
        except jenkins.JenkinsException as e:
            error_no_html = e.args[0].split("\n")[0]
            logger.debug(f'Failed to get server plugin information. Exception: {error_no_html}')
            return [], []

        pprint(plugin_info)

        plugin_info_list = ['TODO']

        return plugin_info, plugin_info_list


    def server_is_reachable(self) -> bool:
        """Check if the server is reachable

        Args:
            None

        Returns:
            True if reachable, else False
        """
        logger.debug(f'Checking if server is reachable: "{self.jenkins_profile["jenkins_server_url"]}" ...')

        # Use a connection session if possible
        if not self.req_session:
            self.req_session = requests.Session()

        # Make a simple get request
        return_success = False
        try:
            return_success = self.req_session.get(self.jenkins_profile['jenkins_server_url']).ok
        except Exception as e:
            logger.debug(f'Server request response exception. Exception: {e}')

        if return_success:
            logger.debug('Server is reachable')
        else:
            logger.debug('Server cannot be reached or is offline')
        return return_success



    ###########################################################################
    #                               FOLDER
    ###########################################################################

    def folder_search(self, search_pattern:str, folder_name:str='', folder_url:str='', folder_depth:int=4) -> Tuple[list, list]:
        """Search the server for folders matching REGEX pattern

        Args:
            search_pattern : REGEX search pattern to match
            folder_name    : (Optional) Only look within this folder for matching sub-folder using item name
            folder_url     : (Optional) Only look within this folder for matching sub-folder using item URL
            folder_depth   : Number of levels to look through

        Returns:
            List of folder found. Both, list of info and list of folder URLs
        """
        # TODO: "fullpath" option that looks at the entire path and not just the name of the item

        # Start a timer to time the search
        start_time = time()
        logger.debug(f'Folder search pattern: {search_pattern}')

        # Get all the jobs
        if folder_name or folder_url:
            # Only recursively search the specified folder name
            logger.debug(f'Searching folder in sub-folder "{folder_name if folder_name else folder_url}"')
            logger.debug(f'Folder depth does not apply. Only looking in this specific folder for subfolders')
            items = self.folder_item_list(folder_name=folder_name, folder_url=folder_url)[0]
        else:
            # Search entire Jenkins
            logger.debug(f'Searching folder in ALL Jenkins. Folder depth: "{folder_depth}"')
            items = self.J.get_all_jobs(folder_depth=folder_depth, folder_depth_per_request=20)

        # Search for any matching folders ("jobs")
        self.search_items_count = 0
        self.search_results = []
        self.__recursive_search(search_type='folder', search_pattern=search_pattern, search_list=items, nested_key='jobs', level=0)

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


    def folder_info(self, folder_name:str='', folder_url:str='') -> Dict:
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

        if folder_url and not folder_name:
            logger.debug('Folder url passed')
            folder_name = utility.url_to_name(url=folder_url)

        # Format name
        folder_name = utility.format_name(name=folder_name)

        logger.debug(f'Getting information for folder: {folder_name}')

        try:
            folder_info_dict = self.J.get_job_info(name=folder_name, fetch_all_builds=True)
        except jenkins.JenkinsException as e:
            logger.debug(f'Failed to get information for folder "{folder_name}". Exception: {e}')
            return {}

        # Check if folder by class or by having jobs
        if folder_info_dict['_class'] not in JenkinsItemClasses.folder.value['class_type'] and JenkinsItemClasses.folder.value['item_type'] not in folder_info_dict:
            logger.debug(f'Specified folder name or folder url found, however "{folder_name}" is not a folder')
            return {}

        return folder_info_dict


    def folder_subfolder_list(self, folder_name:str='', folder_url:str='') -> Tuple[list, list]:
        """Get the list of all sub-folders within the specified folder

        Args:
            folder_name : Folder name to get all its sub-folders
            folder_url  : Folder URL to get all its sub-folders

        Returns:
            List of subfolders, information list and URL list
        """
        logger.debug(f'Getting subfolders for folder name "{folder_name if folder_name else folder_url}" ...')

        # Get the folder information
        folder_info = self.folder_info(folder_name=folder_name, folder_url=folder_url)
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


    def folder_jobs_list(self, folder_name:str='', folder_url:str='') -> Tuple[list, list]:
        """Get the list of all jobs within the specified folder

        Args:
            folder_name : Folder name to get all its jobs
            folder_url  : Folder URL to get all its jobs

        Returns:
            List of jobs, information list and URL list
        """
        logger.debug(f'Getting jobs for folder name "{folder_name if folder_name else folder_url}" ...')

        # Get the folder information
        folder_info = self.folder_info(folder_name=folder_name, folder_url=folder_url)
        if not folder_info:
            return []

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


    def folder_view_list(self, folder_name:str='', folder_url:str='') -> Tuple[list, list]:
        """Get the list of all views within the specified folder

        Args:
            folder_name : Folder name to get all its views
            folder_url  : Folder URL to get all its views

        Returns:
            List of views, information list and URL list
        """
        # Get the folder information
        folder_info = self.folder_info(folder_name=folder_name, folder_url=folder_url)
        if not folder_info:
            return []

        view_list, view_list_url = utility.item_subitem_list(
            item_info=folder_info, get_key_info='name',
            item_type=JenkinsItemClasses.view.value['item_type'],
            item_class_list=JenkinsItemClasses.view.value['class_type']
            )

        logger.debug(f'Number of views found: {len(view_list)}')
        logger.debug(f'Views: {view_list_url}')

        return view_list, view_list_url


    def folder_item_list(self, folder_name:str='', folder_url:str='') -> Tuple[list, list]:
        """Get the list of all items within the specified folder

        Args:
            folder_name : Folder name to get all its items
            folder_url  : Folder URL to get all its items

        Returns:
            List of items, information list and URL list
        """
        # TODO: Potentially combine folder_folders_list and folder_jobs_list, folder_view_list with this method

        logger.debug(f'Getting items for folder name "{folder_name if folder_name else folder_url}" ...')

        # Get the folder information
        folder_info = self.folder_info(folder_name=folder_name, folder_url=folder_url)
        if not folder_info:
            return []

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



    ###########################################################################
    #                                 JOB
    ###########################################################################

    def job_search(self, search_pattern:str, folder_name:str='', folder_url:str='', folder_depth:int=4) -> Tuple[list, list]:
        """TODO Docstring

        Args:
            arg 1 : DESCRIPTION
            arg 2 : DESCRIPTION

        Returns:
            TODO
        """
        # Finding the job by REGEX pattern
        # NOTE: 
        #   - Criteria of jobs is that jobs do not have any sub-folders, only views and jobs

        # Start a timer to time the search
        start_time = time()

        logger.debug(f'Job search pattern: {search_pattern}')

        # Get all the jobs
        if folder_name or folder_url:
            # Only recursively search the specified folder name
            logger.debug(f'Searching jobs in sub-folder "{folder_name if folder_name else folder_url}"')
            logger.debug(f'Folder depth does not apply. Only looking in this specific folder for job')
            items = self.folder_item_list(folder_name=folder_name, folder_url=folder_url)[0]
        else:
            # Search entire Jenkins
            logger.debug(f'Searching jobs in ALL Jenkins. Folder depth: "{folder_depth}"')
            try:
                items = self.J.get_all_jobs(folder_depth=folder_depth)
            except jenkins.JenkinsException as e:
                error_no_html = e.args[0].split("\n")[0]
                logger.debug(f'Error while getting all items. Exception: {error_no_html}')

                # TODO: Catch authentication error "[401]: Unauthorized"
                return [], []

        # Search for any matching folders ("jobs")
        self.search_results = []
        self.search_items_count = 0
        self.__recursive_search(search_type='job', search_pattern=search_pattern, search_list=items, nested_key='jobs', level=0)

        # Remove duplicates from list (THANKS GeeksForGeeks.org)
        logger.debug('Removing duplicates if needed ...')
        self.search_results = [i for n, i in enumerate(self.search_results) if i not in self.search_results[n + 1:]] 

        # Collect URLs only
        job_search_results_list = []
        for search_result in self.search_results:
            job_search_results_list.append(search_result['url'])

        # Output search stats
        logger.debug(f'Searched jobs: {self.search_items_count}. Search time: {time() - start_time} seconds')

        return self.search_results, job_search_results_list


    def job_info(self, job_name:str='', job_url:str='') -> Dict:
        """TODO Docstring

        Args:
            TODO

        Returns:
            TODO
        """
        if not job_name and not job_url:
            logger.debug('Failed to get job information. No job name or job url received')
            return {}

        if job_url:
            logger.debug(f'Job url passed: {job_url}')
            job_info, _, success = self.__REST_request(job_url.strip('/') + '/api/json', 'get')
            if not success:
                return {}

        if job_name:
            # Format name
            job_name = utility.format_name(name=job_name)
            logger.debug(f'Getting information for job: {job_name} ...')

            try:
                job_info = self.J.get_job_info(name=job_name, fetch_all_builds=True)
            except jenkins.JenkinsException as e:
                logger.debug(f'Failed to get information for job "{job_name}". Exception: {e}')
                return {}

            # Check if folder by class or by having jobs
            if job_info['_class'] not in JenkinsItemClasses.job.value['class_type'] and JenkinsItemClasses.job.value['item_type'] not in job_info_dict:
                logger.warning(f'Specified job name or job url found, however "{job_name}" is not a job')
                return {}

        return job_info


    def job_build_list(self, job_name:str='', job_url:str='') -> Tuple[list, list]:
        """TODO Docstring

        Args:
            TODO

        Returns:
            TODO
        """
        # Get the job information
        job_info = self.job_info(job_name=job_name, job_url=job_url)
        if not job_info:
            return [], []

        # Get all the past builds
        build_list, build_url_list = utility.item_subitem_list(
            item_info=job_info, get_key_info='url',
            item_type=JenkinsItemClasses.build.value['item_type'],
            item_class_list=JenkinsItemClasses.build.value['class_type']
            )

        return build_list, build_url_list


    def job_build_next_number(self, job_name:str='', job_url:str='') -> int:
        """TODO Docstring

        Args:
            TODO

        Returns:
            TODO
        """
        # Get the job information
        job_info = self.job_info(job_name=job_name, job_url=job_url)
        if not job_info:
            return None

        # TODO: Check if nextBuildNumber is even part of the info

        return job_info['nextBuildNumber']


    def job_build_last_number(self, job_name:str='', job_url:str='', job_info:dict={}) -> int:
        """TODO Docstring

        Args:
            TODO

        Returns:
            TODO
        """
        # TODO: Return a url of the build instead just the number

        # Get the job information
        if not job_info:
            # If the job info is not passed, request it from server
            job_info = self.job_info(job_name=job_name, job_url=job_url)
            if not job_info:
                return 0

        if 'lastBuild' not in job_info:
            logger.debug('Failed to find "lastBuild" key in job info')
            return 0
        if 'number' not in job_info['lastBuild']:
            logger.debug('Failed to find "number" key in "lastBuild" section of job info')
            return 0

        return job_info['lastBuild']['number']


    def job_build_set_next_number(self, build_number:int, job_name:str='', job_url:str='') -> int:
        """TODO Docstring

        Args:
            TODO

        Returns:
            TODO
        """
        if not job_name and not job_url:
            logger.debug('Failed to set job next build number. No job name or job url received')
            return 
        if job_url and not job_name:
            job_name = utility.url_to_name(url=job_url)
        # Format name
        job_name = utility.format_name(name=job_name)

        logger.debug(f'Setting next build number for job "{job_name}" to {build_number} ...')

        try:
            # TODO: Use requests instead of jenkins-python
            response = self.J.set_next_build_number(job_name, build_number)
        except jenkins.JenkinsException as e:
            error_no_html = e.args[0].split("\n")[0]
            logger.debug(f'Failed to set next build number for job "{job_name}" to {build_number}. Exception: {error_no_html}')
            return

        return build_number


    def job_build_number_exist(self, build_number:int, job_info:dict={}, job_name:str='', job_url:str='') -> bool:
        """TODO Docstring

        Args:
            TODO

        Returns:
            TODO
        """
        if not job_info:
            # Getting job information
            job_info = self.job_info(job_name=job_name, job_url=job_url)
            if not job_info:
                logger.debug(f'Failed to find job "{job_name if job_name else job_url}"')
                return None

        if 'builds' not in job_info:
            logger.debug('Failed to get build list from job. "builds" key missing in job information')
            logger.debug(f'Job info: {job_info}')
            return None

        # Iterate through all listed builds
        for build in job_info['builds']:
            if build_number == build['number']:
                return True

        return False


    def job_build_trigger(self, job_name:str='', job_url:str='', paramters:Dict={}, token:str='') -> int:
        """TODO Docstring

        Args:
            TODO

        Returns:
            TODO
        """
        # NOTE: The jenkins-python module build_job() does not work. Using requests instead

        if not job_name and not job_url:
            logger.debug('Failed to get trigger job build. No job name or job url received')
            return 0, ''

        logger.debug(f'Job reference passed: {job_name if job_name else job_url}')

        # Need both the job name and the job URL
        if job_url and not job_name:
            job_name = utility.url_to_name(url=job_url)
        elif job_name and not job_url:
            job_url = self.J.build_job_url(name=job_name).strip('build')
        job_url = job_url.strip('/')

        next_build_number = self.job_build_next_number(job_name=job_name, job_url=job_url)
        logger.debug(f'Triggering job "{job_url}", build {next_build_number} ...')

        if paramters:
            # Use the paramters passed
            logger.debug(f'Triggering with job paramters: {paramters}')
            post_url = f'{job_url}/buildWithParameters?{urlencode(paramters)}'
        else:
            # No paramters passed
            post_url = f'{job_url}/build'

        logger.debug(f'POST url: {post_url}')

        # Posting to Jenkins
        return_headers= self.__REST_request(request_url=post_url, request_type='post')[1]

        # Parse the queue location of the build
        if return_headers:
            build_queue_url = return_headers['Location']
            if build_queue_url.endswith('/'):
                queue_location = build_queue_url[:-1]
            parts = queue_location.split('/')
            build_queue_number = int(parts[-1])
            logger.debug(f'Build queue URL: {queue_location}')
            logger.debug(f'Build queue ID: {build_queue_number}')
        else:
            return 0

        return build_queue_number


    def job_wipeout_workspace(self, job_name:str='', job_url:str='') -> bool:
        """TODO Docstring

        Args:
            TODO

        Returns:
            TODO
        """
        # TODO
        pass


    def job_in_queue_check(self, job_name:str='', job_url:str='') -> Tuple[dict, int]:
        """TODO Docstring

        Args:
            TODO

        Returns:
            TODO
        """
        if not job_name and not job_url:
            logger.warning('Failed to get job information. No job name or job url received')
            return {}

        if job_url and not job_name:
            job_name = utility.url_to_name(url=job_url)

        # Requesting queue information from server
        jenkins_server_queue = self.server_queue_info()
        if not jenkins_server_queue:
            return {}, 0
        logger.debug(f"Number of queued items: {len(jenkins_server_queue['items'])}")

        # Look over each item in the queue if it matches the job name
        queue_info = {}
        for i, queue_item in enumerate(jenkins_server_queue['items']):
            # Check if the queued item is a job
            if queue_item['task']['_class'] not in JenkinsItemClasses.job.value['class_type']:
                logger.debug(f"[ITEM {i+1}/{len(jenkins_server_queue['items'])}] Queued item not a job. Item class: {queue_item['task']['_class']}")
                continue

            queue_job_url = queue_item['task']['url']
            logger.debug(f"[ITEM {i+1}/{len(jenkins_server_queue['items'])}] Queue job item: {queue_job_url}")

            queue_job_name = utility.url_to_name(url=queue_job_url)

            # Check if the job name matches
            # NOTE: May have more than one queued item maybe?
            if queue_job_name == job_name:
                logger.debug(f'Successfully found job "{job_name}" Jenkins server build queue')
                logger.debug(f'Search stopped')
                queue_info = queue_item
                break
                # return queue_item, queue_item['id']

        # Adding additional parameters
        if queue_info:
            queue_info['inQueueSinceFormatted'] = str(timedelta(seconds=queue_info['inQueueSince']/1000.0))[:-3]
            queue_info['fullUrl'] = self.jenkins_profile['jenkins_server_url'].strip('/') + '/' + queue_info['url']
            queue_info['jobUrl'] = queue_info['task']['url']
            queue_info['jobFullName'] = utility.url_to_name(queue_info['jobUrl'])
            queue_info['folderUrl'] = utility.build_url_to_other_url(queue_info['fullUrl'], target_url='folder')
            queue_info['folderFullName'] = utility.url_to_name(queue_info['folderUrl'])
            queue_info['serverURL'] = utility.item_url_to_server_url(queue_info['fullUrl'])
            queue_info['serverDomain'] = utility.item_url_to_server_url(queue_info['fullUrl'], False)
        else:
            logger.debug(f'Failed to find job "{job_name}" Jenkins server build queue')
            return {}, 0

        return queue_info, queue_info['id']



    ###########################################################################
    #                                 BUILD
    ###########################################################################


    def build_info(self, build_url:str='', job_name:str='', job_url:str='', build_number:int=None, latest:bool=False) -> Dict:
        """TODO Docstring

        Args:
            TODO

        Returns:
            TODO
        """
        # 1. Build URL
        # 2. Job with Latest Flag
        # 3. Job with Build number

        if build_url:
            # Making a direct request using the passed url
            request_url = f"{build_url.strip('/')}/api/json"
            build_info = self.__REST_request(request_url=request_url, request_type='get')[0]
            if not build_info:
                logger.debug('Failed to get build info')
                return {}
        else:
            if not job_name and not job_url:
                logger.debug('Failed to pass parameters that describe the build')
                return {}

            # Getting job information
            job_info = self.job_info(job_name=job_name, job_url=job_url)
            if not job_info:
                logger.debug(f'Failed to find job "{job_name if job_name else job_url}"')
                return {}

            # Getting last build number and checking if valid
            job_last_build_number = self.job_build_last_number(job_info=job_info)

            # If not build number is passed, get the latest build
            if not build_number and latest:
                # Build number not passed and latest flag is not set
                logger.debug('No build number passed and latest flag set')
                logger.debug(f'Using latest build number for this job: {job_last_build_number}')
                build_number = job_last_build_number
            elif not build_number and not latest:
                logger.debug('No build number passed and latest flag not set. Cannot specify build')
                return {}
            else:
                # Build number is passed
                if build_number > job_last_build_number:
                    logger.debug('Build number exceeds last build number for this job')
                    return {}

            logger.debug(f'Getting build info for job "{job_info["fullName"]}, build {build_number} ...')
            try:
                # TODO: For session conservation consider using own REST method here with:
                #       build_url, or job_url and build_number
                #       '%(folder_url)sjob/%(short_name)s/%(number)d/api/json?depth=%(depth)s'
                build_info = self.J.get_build_info(name=job_info['fullName'], number=build_number)
            except jenkins.JenkinsException as e:
                logger.debug(f'Failed to request build information. Exception: {e}')
                return {}

        # Add additional derived information
        if 'timestamp' in build_info:
            build_info['startDatetime'] = datetime.fromtimestamp(build_info['timestamp']/1000.0).strftime("%A, %B %d, %Y %I:%M:%S")
            build_info['estimatedDurationFormatted'] = str(timedelta(seconds=build_info["estimatedDuration"]/1000.0))[:-3]

            # Check if results are in
            if 'result' in build_info:
                if build_info['result']:
                    build_info['resultText'] = build_info['result']
                    build_info['durationFormatted'] = str(timedelta(seconds=build_info['duration']/1000.0))[:-3]
                    build_info['endDatetime'] = datetime.fromtimestamp((build_info['timestamp'] + build_info['duration'])/1000.0).strftime("%A, %B %d, %Y %I:%M:%S")
                    build_info['elapsedFormatted'] = build_info['durationFormatted']
                else:
                    build_info['resultText'] = BuildStatus.running.value
                    build_info['durationFormatted'] = None
                    build_info['endDatetime'] = None
                    build_info['elapsedFormatted'] = str(timedelta(seconds=(time() - (build_info['timestamp']/1000.0))))[:-3]
            else:
                build_info['resultText'] = BuildStatus.unknown.value

        if 'url' in build_info:
            build_info['fullName'] = utility.url_to_name(build_info['url'])
            build_info['jobUrl'] = utility.build_url_to_other_url(build_info['url'], target_url='job')
            build_info['jobFullName'] = utility.url_to_name(build_info['jobUrl'])
            build_info['folderUrl'] = utility.build_url_to_other_url(build_info['url'], target_url='folder')
            build_info['folderFullName'] = utility.url_to_name(build_info['folderUrl'])
            build_info['serverURL'] = utility.item_url_to_server_url(build_info['url'])
            build_info['serverDomain'] = utility.item_url_to_server_url(build_info['url'], False)

        if 'builtOn' not in build_info:
            build_info['builtOn'] = 'N/A'

        return build_info


    def build_status_text(self, build_url:str='', job_name:str='', job_url:str='', build_number:int=None, latest:bool=False) -> str:
        """TODO Docstring

        Args:
            TODO

        Returns:
            TODO
        """
        # Get the build info
        build_info = self.build_info(
            build_url=build_url,
            job_name=job_name,
            job_url=job_url,
            build_number=build_number,
            latest=latest)

        # If nothing is returned, check if job is queued on server
        if not build_info:
            logger.debug('The specified build was not found')
            logger.debug('Looking for build in the server build queue ...')
            logger.debug('Finding job name ...')
            if build_url:
                job_url = utility.build_url_to_other_url(build_url)
                job_name = utility.url_to_name(job_url)
            elif job_name:
                pass
            elif job_url:
                job_name = utility.url_to_name(job_url)
            else:
                logger.debug('Failed to find build status text. Specify build url, job name, or job url')
                return ""
            logger.debug(f'Job name: {job_name}')
            queue_item, queue_number = self.job_in_queue_check(job_name=job_name)
            if not queue_item:
                logger.debug('Build not found in queue')
                return BuildStatus.not_found.value
            else:
                logger.debug(f'Build found in queue. Queue number {queue_number}')
                return BuildStatus.queued.value

        # FIXME: resultText is returned in build info. Maybe move queue check to build_info??

        # Check if in process (build is there but results not posted)
        if 'result' not in build_info:
            logger.debug('Build was found running/building, however no results are posted')
            return BuildStatus.running.value
        else:
            # FIXME: Get "No status found" when "yo-jenkins build status --url" on build that is "RUNNING" (result: Null)
            logger.debug('Build found, but has concluded or stopped with result')
            return build_info['result']


    def build_abort(self, build_url:str='', job_name:str='', job_url:str='', build_number:int=None, latest:bool=False) -> int:
        """TODO Docstring

        Args:
            TODO

        Returns:
            TODO
        """
        if build_url:
            logger.debug(f'Build URL passed: {build_url}')
            url = build_url
        else:
            logger.debug('NO build URL passed. Getting build information ...')
            # Get build info request
            build_info = self.build_info(build_url, job_name, job_url, build_number, latest)
            if not build_info:
                logger.debug(f'Failed to abort build. Build does not exist or may be queued')
                return 0
            url = build_info['url']

        # Making a direct request using the passed url
        logger.debug(f'Aborting build: {url} ...')
        request_url = f"{url.strip('/')}/stop"
        if not self.__REST_request(request_url=request_url, request_type='post')[2]:
            logger.debug(f'Failed to abort build. Build may not exist or is queued')
            return 0

        logger.debug(f'Successfully aborted build')

        return utility.build_url_to_build_number(build_url=url)


    def build_delete(self, build_url:str='', job_name:str='', job_url:str='', build_number:int=None, latest:bool=False) -> int:
        """TODO Docstring

        Args:
            TODO

        Returns:
            TODO
        """
        # TODO: Pass a list of build numbers
        if build_url:
            logger.debug(f'Build URL passed: {build_url}')
            url = build_url
        else:
            logger.debug('NO build URL passed. Getting build information ...')
            # Get build info request
            build_info = self.build_info(build_url, job_name, job_url, build_number, latest)
            if not build_info:
                logger.debug(f'Build does not exist or may be queued')
                return 0
            url = build_info['url']

        # Making a direct request using the passed url
        logger.debug(f'Deleting build: {url} ...')
        request_url = f"{url.strip('/')}/doDelete"
        if not self.__REST_request(request_url=request_url, request_type='post')[2]:
            logger.debug(f'Failed to delete build. Build may not exist or is queued')
            return 0

        return utility.build_url_to_build_number(build_url=url)


    def build_stage_list(self, build_url:str='', job_name:str='', job_url:str='', build_number:int=None, latest:bool=False) -> Tuple[list, list]:
        """TODO Docstring

        Args:
            TODO

        Returns:
            TODO
        """
        # FIXME: yo-jenkins build stages --url https://retailjenkins.cloud.capitalone.com/job/Non-PAR/job/Non-Prod-Jobs/job/Accenture/job/test_job/46/ 
        #        yields 404 in running build. Maybe issue with formatting of the url to name?

        # TODO: Pass a list of build numbers
        if not build_url:
            logger.debug('NO build URL passed. Getting build information ...')
            # Get build info request
            build_info = self.build_info(build_url, job_name, job_url, build_number, latest)
            if not build_info:
                logger.debug(f'Build does not exist or may be queued')
                return [], []
            build_url = build_info['url']

        # # Check if Workflow run (https://github.com/jenkinsci/pipeline-stage-view-plugin/blob/master/rest-api/README.md)
        # # TODO: Check if this is the only class supported for staged builds
        # staged_build_classes = ["org.jenkinsci.plugins.workflow.job.WorkflowRun"]
        # if build_info['_class'] not in staged_build_classes :
        #     logger.debug(f'This build is not a staged build')
        #     logger.debug(f'This build class is "{build_info["_class"]}", however should be:')
        #     for build_class in staged_build_classes:
        #         logger.debug(f'   - {build_class}')
        #     return [], []

        # Making a direct request using the passed url
        logger.debug(f'Getting build stages for: {build_url} ...')
        request_url = f"{build_url.strip('/')}/wfapi/describe"
        return_content, _, return_success = self.__REST_request(request_url=request_url, request_type='get')
        if not return_success or not return_content:
            logger.debug(f'Failed to get build stages. Build may not exist, is queued, or is not a staged build')
            return [], []

        # Getting the stage items
        # FIXME: When --url <job> and no build number is passed, it will just get the job describe, not build info
        if 'stages' in return_content:
            build_stage_list = return_content['stages']
        else:
            logger.debug('No "stages" key found in return content. May not be a staged build')
            return [], []

        # Add additional derived information for each step
        for stage_info in build_stage_list:
            stage_info['startDatetime'] = datetime.fromtimestamp(stage_info["startTimeMillis"]/1000.0).strftime("%A, %B %d, %Y %I:%M:%S")
            stage_info['durationFormatted'] = str(timedelta(seconds=stage_info["durationMillis"]/1000.0))[:-3]
            stage_info['pauseDurationFormatted'] = str(timedelta(seconds=stage_info["pauseDurationMillis"]/1000.0))
            stage_info['url'] = stage_info['_links']['self']['href']

        # Getting only the names of the stages
        build_stage_name_list = []
        for stage in build_stage_list:
            build_stage_name_list.append(stage['name'])

        return build_stage_list, build_stage_name_list


    def build_artifact_list(self, build_url:str='', job_name:str='', job_url:str='', build_number:int=None) -> List[dict]:
        """TODO Docstring

        Args:
            TODO

        Returns:
            TODO
        """
        # Test on build with artifacts
        return self.build_info(build_url=build_url, job_name=job_name, job_url=job_url, build_number=build_number)['artifacts']


    def build_artifact_download(self):
        """TODO Docstring

        Args:
            TODO

        Returns:
            TODO
        """
        # TODO: Test on build with artifacts
        pass


    def build_log(self, build_url:str='', job_name:str='', job_url:str='', build_number:int=None, latest:bool=False, download:bool=False) -> bool:
        """TODO Docstring

        Args:
            TODO

        Returns:
            TODO
        """
        # TODO: Pass a list of build numbers
        if build_url:
            logger.debug(f'Build URL passed: {build_url}')
            url = build_url
        else:
            logger.debug('NO build URL passed. Getting build information ...')
            # Get build info request
            build_info = self.build_info(build_url, job_name, job_url, build_number, latest)
            if not build_info:
                logger.debug(f'Build does not exist or may be queued')
                return False
            url = build_info['url']

        # Making a direct request using the passed url
        logger.debug(f'Deleting build: {url} ...')
        request_url = f"{url.strip('/')}/consoleText"
        return_content, _, return_success = self.__REST_request(request_url=request_url, request_type='get', json_content=False)
        if not return_success or not return_content:
            logger.debug(f'Failed to get console logs. Build may not exist or is queued')
            return False

        # Getting every line in a list item
        # names_list = [y for y in (x.strip() for x in self.build_temp_console_output.splitlines()) if y]

        if download:
            # Download the complete logs
            # TODO: Download only last X number of logs, last X percent of the logs
            # NOTE: Maybe save if as a temp file? Move this to own function?
            pass
        else:
            # Print to console
            print(return_content)

        return True


    def build_queue_info(self, build_queue_number:int=0, build_queue_url:str='') -> Dict:
        """TODO Docstring

        Args:
            TODO

        Returns:
            TODO
        """
        logger.info(f'Getting information for build queue "{build_queue_number}" ...')

        # Make the request URL
        if build_queue_number:
            request_url = f'{self.jenkins_profile["jenkins_server_url"]}/queue/item/{build_queue_number}/api/json'
        elif build_queue_url:
            request_url = f'{self.jenkins_profile["jenkins_server_url"]}/{build_queue_url}api/json'
        else:
            logger.error('No build queue number or build queue url passed')
            return {}
        queue_info = self.__REST_request(request_url=request_url, request_type='get')[0]

        # Adding additional parameters
        if queue_info:
            queue_info['isQueuedItem'] = True
            queue_info['fullUrl'] = self.jenkins_profile['jenkins_server_url'].strip('/') + '/' + queue_info['url']
            queue_info['jobUrl'] = queue_info['task']['url']
            queue_info['jobFullName'] = utility.url_to_name(queue_info['jobUrl'])
            queue_info['folderUrl'] = utility.build_url_to_other_url(queue_info['fullUrl'], target_url='folder')
            queue_info['folderFullName'] = utility.url_to_name(queue_info['folderUrl'])
            queue_info['serverURL'] = utility.item_url_to_server_url(queue_info['url'])
            queue_info['serverDomain'] = utility.item_url_to_server_url(queue_info['url'], False)

        return queue_info


    def build_queue_abort(self, build_queue_number:int) -> bool:
        """TODO Docstring

        Args:
            TODO

        Returns:
            TODO
        """
        logger.debug(f'Aborting build queue "{build_queue_number}" ...')

        if not build_queue_number:
            logger.error('No build queue number passed')
            return False

        # Make the request URL
        request_url = f'{self.jenkins_profile["jenkins_server_url"]}queue/cancelItem?id={build_queue_number}'
        return_content = self.__REST_request(request_url=request_url, request_type='post')[0]

        if not return_content:
            logger.error('Failed to abort build queue. Specified build queue number may be wrong or build may have already started')
            logger.error('The following jobs are currently in queue:')
            queue_list = self.server_queue_list()
            for i, queue_item in enumerate(queue_list):
                logger.error(f'  {i+1}. Queue ID: {queue_item["id"]} - Job URL: {queue_item["task"]["url"]}')

            return False

        return True


    def build_browser_open(self, build_url:str='', job_name:str='', job_url:str='', build_number:int=None, latest:bool=False) -> bool:
        """TODO Docstring

        Args:
            TODO

        Returns:
            TODO
        """
        if build_url:
            logger.debug(f'Build URL passed: {build_url}')
            url = build_url
        else:
            logger.debug('NO build URL passed. Getting build information ...')
            # Get build info request
            build_info = self.build_info(build_url, job_name, job_url, build_number, latest)
            if not build_info:
                logger.debug(f'Build does not exist or may be queued')
                return 0
            url = build_info['url']

        # Open the build in browser
        logger.debug(f'Opening build in web browser: "{url}" ...')
        success = utility.browser_open(url=url)
        if success:
            logger.debug('Successfully opened in web browser')
        else:
            logger.debug('Failed to open in web browser')
        return success


    def build_monitor(self, build_url:str='', job_name:str='', job_url:str='', build_number:int=None, latest:bool=False) -> bool:
        """TODO Docstring

        Args:
            TODO

        Returns:
            TODO
        """
        if build_url:
            logger.debug(f'Build URL passed: {build_url}')
            url = build_url
        else:
            logger.debug('NO build URL passed. Getting build information ...')
            # Get build info request
            build_info = self.build_info(build_url, job_name, job_url, build_number, latest)
            if not build_info:
                logger.debug(f'Build does not exist or may be queued')
                return 0
            url = build_info['url']

        logger.debug(f'Starting monitor for: "{url}" ...')
        M = Monitor(YJ=self)
        success = M.build_monitor_start(build_url=url)
        if success:
            logger.debug('Successfully opened monitor')
        else:
            logger.debug('Failed to open monitor for build')
        return success






    ###########################################################################
    #                                 STAGE
    ###########################################################################


    def stage_info(self, stage_name:str, build_url:str='', job_name:str='', job_url:str='', build_number:int=None, latest:bool=False) -> Dict:
        """Get the stage information for specified stage

        Details: Ways of specifying the build:
            - Build URL only
            - Job URL only
            - Job name with build number or latest flag

        Args:
            stage_name   : Name of the stage
            build_url    : Direct URL of the build
            job_name     : Name of the Job
            job_url      : URL of the Job
            build_number : Build number for the Job
            latest       : Latest build

        Returns:
            Stage information
        """
        # Getting all stages
        build_stage_list, build_stage_name_list = self.build_stage_list(build_url, job_name, job_url, build_number, latest)
        if not build_stage_name_list:
            return {}
        logger.debug(f'Stages found: {build_stage_name_list}')

        # Formate stage name form user input
        logger.debug(f'Formatting stage name "{stage_name}": Lower case, strip spaces')
        stage_name = stage_name.lower().strip()

        # Check if lowercase stage name is in list of stages in this build
        if not stage_name in [x.lower() for x in build_stage_name_list]:
            logger.debug(f'Failed to find stage name "{stage_name}" among listed stages')
            return {}

        # Getting the right stage item
        logger.debug('Getting stage URL from build information ...')
        build_stage_item = next(item for item in build_stage_list if item["name"].lower() == stage_name)

        # Making the request to get stage info
        request_url = f'{self.jenkins_profile["jenkins_server_url"]}/{build_stage_item["url"]}'
        return_content = self.__REST_request(request_url=request_url, request_type='get')[0]
        if not return_content:
            return {}

        # Add additional derived information for stage
        return_content['startDatetime'] = datetime.fromtimestamp(return_content["startTimeMillis"]/1000.0).strftime("%A, %B %d, %Y %I:%M:%S")
        return_content['durationFormatted'] = str(timedelta(seconds=return_content["durationMillis"]/1000.0))[:-3]
        return_content['pauseDurationFormatted'] = str(timedelta(seconds=return_content["pauseDurationMillis"]/1000.0))
        return_content['numberOfSteps'] = len(return_content['stageFlowNodes'])

        # Add additional derived information for each step
        if "stageFlowNodes" in return_content:
            # Accounting for no stage step command
            for step_info in return_content['stageFlowNodes']:
                step_info['startDatetime'] = datetime.fromtimestamp(step_info["startTimeMillis"]/1000.0).strftime("%A, %B %d, %Y %I:%M:%S")
                step_info['durationFormatted'] = str(timedelta(seconds=step_info["durationMillis"]/1000.0))[:-3]
                step_info['pauseDurationFormatted'] = str(timedelta(seconds=step_info["pauseDurationMillis"]/1000.0))

                # Adding the urls to the item
                step_info['url'] = step_info['_links']['self']['href']
                step_info['url_log'] = step_info['_links']['log']['href']
                step_info['url_console'] = step_info['_links']['console']['href']
                step_info['url_full'] = f'{self.jenkins_profile["jenkins_server_url"]}{step_info["url"]}'

        # TODO: Make utility function for additional derived info

        return return_content


    def stage_status_text(self, stage_name:str, build_url:str='', job_name:str='', job_url:str='', build_number:int=None, latest:bool=False) -> str:
        """Get the status text of the specified stage

        Details: Ways of specifying the build:
            - Build URL only
            - Job URL only
            - Job name with build number or latest flag

        Args:
            stage_name   : Name of the stage
            build_url    : Direct URL of the build
            job_name     : Name of the Job
            job_url      : URL of the Job
            build_number : Build number for the Job
            latest       : Latest build

        Returns:
            Stage status text
        """
        # Get the stage info
        stage_info = self.stage_info(
            stage_name=stage_name,
            build_url=build_url,
            job_name=job_name,
            job_url=job_url,
            build_number=build_number,
            latest=latest)

        if not stage_info:
            return StageStatus.not_found.value

        # Check if in process (build is there but results not posted)
        if not stage_info['status']:
            logger.debug('Stage was found running/building, however no results are posted')
            return StageStatus.unknown.value
        else:
            logger.debug('Stage found, but has concluded or stopped with result')
            return stage_info['status']


    def stage_step_list(self, stage_name=str, build_url:str='', job_name:str='', job_url:str='', build_number:int=None, latest:bool=False) -> Tuple[list, list]:
        """List of steps for this stage

        Details: Ways of specifying the build:
            - Build URL only
            - Job URL only
            - Job name with build number or latest flag

        Args:
            stage_name   : Name of the stage
            build_url    : Direct URL of the build
            job_name     : Name of the Job
            job_url      : URL of the Job
            build_number : Build number for the Job
            latest       : Latest build

        Returns:
            List of steps, information and URL list
        """
        # Getting the stage info
        stage_info = self.stage_info(stage_name=stage_name, build_url=build_url, job_name=job_name, job_url=job_url, build_number=build_number, latest=latest)
        if not stage_info:
            return [], []

        # Check if there are steps in this stage
        if "stageFlowNodes" not in stage_info:
            logger.debug('Failed to get stage step information. No stage steps listed')
            return [], []

        # Accounting for no stage step command
        for step_info in stage_info['stageFlowNodes']:
            if not 'parameterDescription' in step_info:
                step_info['parameterDescription'] = "No command parameters listed"

        # Getting the stage items
        step_list = stage_info['stageFlowNodes']

        # Getting only the names/labels of the stages
        step_name_list = []
        for step_info in step_list:
            step_name_list.append(step_info['name'])

        return step_list, step_name_list


    def stage_log(self, stage_name=str, build_url:str='', job_name:str='', job_url:str='', build_number:int=None, latest:bool=False, download:bool=False) -> bool:
        """Prints out the console log for this specified stage

        Details: Ways of specifying the build:
            - Build URL only
            - Job URL only
            - Job name with build number or latest flag

        Args:
            stage_name   : Name of the stage
            build_url    : Direct URL of the build
            job_name     : Name of the Job
            job_url      : URL of the Job
            build_number : Build number for the Job
            latest       : Latest build

        Returns:
            True if console log has been printed out, else False
        """
        # Getting all stage step information
        stage_step_list = self.stage_step_list(stage_name=stage_name, build_url=build_url, job_name=job_name, job_url=job_url, build_number=build_number, latest=latest)[0]
        if not stage_step_list:
            return '', []

        # TODO: Add progress bar for step to end of steps - tqdm, alive-progress

        stage_log_list = []
        for i, stage_step in enumerate(stage_step_list):
            # FIXME: This is way too slow!
            #        Add concurrent requests (threding, asynio, grequests, etc)
            #        https://stackoverflow.com/questions/2632520/what-is-the-fastest-way-to-send-100-000-http-requests-in-python

            # Getting step information
            return_content = self.step_info(step_url=stage_step['url_log'])
            if not return_content:
                continue

            logger.debug(f"---> {i+1}/{len(stage_step_list)} - {stage_step['name']}")
            if 'parameterDescription' in stage_step:
                parameter = stage_step['parameterDescription']
            else:
                parameter = 'None'

            # Check if there is any log text to this stage step
            if 'text' in return_content or not return_content['length'] == 0:
                # Clean up all HTML tags from return, keep only raw text
                log_text = utility.html_clean(return_content['text'])

                # Also convert to list
                log_list = [y for y in (x.strip() for x in log_text.splitlines()) if y]

                # Add extra step info to each line of log
                log_list = [f"[STEP: {i+1}/{len(stage_step_list)}] " + s  for s in log_list]

                # Add intro to the logs of this step
                log_list.insert(0, f"[STEP: {i+1}/{len(stage_step_list)}] [STEP] : {stage_step['name']} - PARAMETER: {parameter}")
                # log_list.insert(0, f"---------------  STEP: {i+1}/{len(stage_step_list)}  ---------------")
                # log_list.insert(0, "----------------------------------------------------")

                stage_log_list.extend(log_list)
            else:
                # If no logs in step, still add step command
                # stage_log_list.append("----------------------------------------------------")
                # stage_log_list.append(f"---------------  STEP: {i+1}/{len(stage_step_list)}  ---------------")
                stage_log_list.append(f"[STEP: {i+1}/{len(stage_step_list)}] [STEP] : {stage_step['name']} - PARAMETER: {parameter}")

        # Make the list to continuos step, with newline in between them
        stage_log_text = os.linesep.join(stage_log_list)
        print(stage_log_text)

        return True
        # return stage_log_text #, stage_log_list



    ###########################################################################
    #                                 STEP
    ###########################################################################

    def step_info(self, step_url=str) -> Dict:
        """Get the information of the specified step

        Details: Step URL can be gotten with stage_step_list.
                 Format: <SERVER URL>/<step_url>

        Args:
            step_url : The direct URL of the step

        Returns:
            Step information
        """
        # Making the request
        request_url = f'{self.jenkins_profile["jenkins_server_url"]}/{step_url.strip("/")}'
        return_content = self.__REST_request(request_url=request_url, request_type='get')[0]
        if not return_content:
            logger.debug(f'Failed to get step info for: {request_url}')
            return {}

        return return_content
