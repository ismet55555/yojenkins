#!/usr/bin/env python3

import logging
import os
import re
from datetime import datetime
from getpass import getpass
from pathlib import Path
from pprint import pprint
from typing import Dict, Tuple

import click
import yaml
from jenkins import Jenkins as JenkinsSDK
from yo_jenkins.Utility import utility
from yo_jenkins.YoJenkins.REST import REST

from . import colors

# Getting the logger reference
logger = logging.getLogger()


class Auth:
    """Handeling of authentication and profile management functionality"""

    def __init__(self, REST_obj=None) -> None:
        """Object constructor method, called at object creation

        Args:
            None

        Returns:
            None
        """
        # Request object
        if not REST_obj:
            # If not provided, make a new object
            self.REST: object = REST()
        else:
            self.REST: object = REST_obj

        # JenkinsSDK object - Instantiated in create_auth()
        self.JenkinsSDK = None

        # TODO: Refer to configuration file as credentials file

        self._cred_config_dir = Path.home()
        self._cred_config_filename = '.yo-jenkins.conf'

        self._profile_env_var = 'YOJENKINS_PROFILE'
        self._required_top_level_key = 'profiles'

        self.jenkins_profile = {}
        self.jenkins_username = ''
        self.jenkins_api_token = ''
        self.authenticated = False

    def __update_profiles(self, profiles: dict) -> bool:
        """Create/Update the current credentials profile file

        Details: This method will overwrite any previous file content.
                 It will also add a file prefix for yaml formats

        Args:
            profiles : All profile info to be written to file

        Returns:
            True if successfull, else False
        """
        # Storing configurations in file
        output_path = os.path.join(self._cred_config_dir, self._cred_config_filename)
        logger.debug(f'Saving new file: "{output_path}" ...')
        with open(os.path.join(output_path), 'w') as file:  # Overwrite previous content
            yaml.dump(profiles, file)

        # Add top file prefix for yaml file format
        lines_new = [
            f'# -*- mode: yaml -*-{os.linesep}', f'# vim: set filetype=yaml{os.linesep}', f'---{os.linesep * 3}'
        ]
        success = utility.append_lines_to_beginning_of_file(output_path, lines_new)
        if not success:
            return False

        return True

    def get_REST(self):
        """TODO Docstring

        Args:
            TODO

        Returns:
            TODO
        """
        return self.REST

    def generate_token(self,
                       token_name: str = '',
                       server_base_url: str = '',
                       username: str = '',
                       password: str = '') -> str:
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
            prompt_text = colors.BOLD + colors.YELLOW + "Enter desired API TOKEN NAME: " + colors.NORMAL
            token_name = input(prompt_text)
            logger.debug(f'User input: {token_name}')

        if not server_base_url:
            prompt_text = colors.BOLD + colors.YELLOW + "Enter Jenkins SERVER BASE URL: " + colors.NORMAL
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
        request_return_text, _, success = self.REST.request(target=server_base_url.strip('/') + '/crumbIssuer/api/xml',
                                                            is_endpoint=False,
                                                            request_type='get',
                                                            json_content=False,
                                                            auth=(username, password),
                                                            new_session=True)
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
        request_return_content, _, success = self.REST.request(
            target=server_base_url.strip('/') +
            '/me/descriptorByName/jenkins.security.ApiTokenProperty/generateNewToken/api/json',
            is_endpoint=False,
            request_type='post',
            json_content=True,
            auth=(username, password),
            new_session=False,
            params=params,
            headers=headers)
        if not success: return

        try:
            generated_token = request_return_content['data']['tokenValue']
            logger.debug(f'Successfully generated server API token "{token_name}"!')
        except Exception:
            logger.debug('Failed to find "tokenValue" in the POST request return header')
            generated_token = ''

        return generated_token

    def profile_add_new_token(self, profile_name: str) -> str:
        """Update the specified credentials profile with a new server API token

        Args:
            profile_name : Name of the profile as specified in the credentials file

        Returns:
            Server API Token
        """
        # Check if the credential config file exists
        file_exists, file_path = self.detect_configuration_file()
        if not file_exists:
            return

        # Load the current cred config file
        profiles = utility.load_contents_from_local_yaml_file(file_path)
        if not profiles:
            return

        # Check if passed profile is part of the credential config file
        logger.debug(
            f'Currently listed profile names: {", ".join(list(profiles[self._required_top_level_key].keys()))}')
        if profile_name not in profiles[self._required_top_level_key]:
            logger.debug(
                f'Failed to find the --profile specified profile name ("{profile_name}") in the credential configuration file'
            )
            return

        profile_info = profiles[self._required_top_level_key][profile_name]
        logger.debug(f'Profile {profile_name} loaded')
        logger.debug(f'Profile info: {profile_info}')

        # Generate a API token name (seen in Jenkins UI)
        token_name = f'yo-jenkins_{datetime.now().strftime("%m-%d-%Y_%I-%M-%S")}'

        # Check if needed information is listed in the profile
        if 'jenkins_server_url' not in profile_info:
            logger.debug('No "jenkins_server_url" key listed in profile')
            server_url = ''
        else:
            server_url = profile_info['jenkins_server_url']
        if 'username' not in profile_info:
            logger.debug('No "username" key listed in profile')
            username = ''
        else:
            username = profile_info['username']

        # Generate the api token
        api_token = self.generate_token(token_name=token_name, server_base_url=server_url, username=username)
        if not api_token:
            return

        # Store the API token
        profiles[self._required_top_level_key][profile_name]['api_token'] = api_token

        success = self.__update_profiles(profiles=profiles)
        if not success:
            logger.debug(f'Failed to add/update new API token to profile {profile_name}')
            return

        return api_token

    def configure(self, api_token: str = '') -> bool:
        """Configure/add a new credentials profile

        Details: This method will prompt the user with a series of questions
                 to add a new profile to the credentials profile file

        Args:
            api_token : (Optional) Server API token to be added to the new profile

        Returns:
            This is a description of what is returned.
        """
        # Checking if credential config file exists
        file_exists, file_path = self.detect_configuration_file()
        if file_exists:
            logger.debug(f'Credentials file found in current user home directory: {file_path}')
            logger.debug(f'Loading credentials file: {file_path} ...')

            # Load the current cred config file
            profiles = utility.load_contents_from_local_yaml_file(file_path)
            if not profiles:
                return False

            # Check if top level / parent key is in the config cred file
            if self._required_top_level_key not in profiles.keys():
                logger.debug(
                    f'The loaded credentials configuration file does not include a "{self._required_top_level_key}" section'
                )
                return False
            logger.debug(
                f'Currently listed profile names: {", ".join(list(profiles[self._required_top_level_key].keys()))}')

            # Adding the profile
            print('')
            print(f'Credentials profile file found in current user home directory: {file_path}')
            print('Adding a new profile to the current credentials profile file ...')
            print('Please enter the following information to add a profile:')
            print('')
        else:
            logger.debug('Credentials file NOT found in current user home directory')
            logger.debug(f'Creating credentials file in current user home directory: {self._cred_config_filename} ...')

            # Create new profile from scratch
            profiles = {}
            profiles[self._required_top_level_key] = {}

            print('')
            print(f'Credentials profile file ({self._cred_config_filename}) NOT found in current user home directory')
            print(
                f'Creating a new credentials profile file: {os.path.join(file_path, self._cred_config_filename)} ...')
            print('Please enter the following information to create your first profile:')
            print('')

        # Prompting user for details
        profile_name = input(colors.BOLD + colors.YELLOW + '[ OPTIONAL ] Enter PROFILE NAME (default):  ' +
                             colors.NORMAL)
        profile_name = 'default' if not profile_name else profile_name
        if profile_name in profiles[self._required_top_level_key]:
            print('')
            print(f'WARNING : You are about to overwrite the current profile "{profile_name}"')
            print('')
        profiles['profiles'][profile_name] = {}
        profiles['profiles'][profile_name]['jenkins_server_url'] = input(
            colors.BOLD + colors.YELLOW + '[ REQUIRED ] Enter Jenkins SERVER BASE URL:  ' + colors.NORMAL)
        profiles['profiles'][profile_name]['username'] = input(colors.BOLD + colors.YELLOW +
                                                               '[ REQUIRED ] Enter USERNAME:  ' + colors.NORMAL)
        if not api_token:
            profiles['profiles'][profile_name]['api_token'] = input(colors.BOLD + colors.YELLOW +
                                                                    '[ OPTIONAL ] Enter API TOKEN:  ' + colors.NORMAL)
        else:
            print('')
            print(colors.BOLD + 'WARNING: Adding provided API token to this profile' + colors.NORMAL)
            print('')
            profiles['profiles'][profile_name]['api_token'] = api_token
        profiles['profiles'][profile_name]['active'] = True

        return self.__update_profiles(profiles=profiles)

    def detect_configuration_file(self) -> Tuple[bool, str]:
        """Detect/find the credentials profile file in the home directory

        Args:
            None

        Returns:
            Success, File path of the credentials profile file
        """
        # Defining directories to look for
        files_in_home_dir = [f for f in os.listdir(Path.home()) if os.path.isfile(os.path.join(Path.home(), f))]

        # Seeing if configuration file is in specified directories
        if self._cred_config_filename in files_in_home_dir:
            # Check if file exists in user home directory
            logger.debug(
                f'Configuration file "{self._cred_config_filename }" found in user home directory: {Path.home()}')
            config_filepath = os.path.join(Path.home(), self._cred_config_filename)
            return True, config_filepath
        else:
            logger.debug(f'Configuration file "{self._cred_config_filename }" NOT found in home directory')
            return False, ''

    def get_configurations(self, profile: str = '') -> Dict:
        """Get the contents of the credentials profiles file

        Details: The order (preference) of specified profile credentials to get are the following:
            - Passed `profile` argument
            - Environmental Variable as specified in `self._profile_env_var`
            - Profile listed as `default` in the credentials profile file
            - Any other / first profile set to active

        Args:
            profile : (Optional) Only get the configuration for particular profile

        Returns:
            The credential information of the specified credentials profile
        """
        success, config_filepath = self.detect_configuration_file()
        if not success:
            # If no configuration file found, configure one
            logger.debug('No credentials file found. Configuring one ...')
            success = self.configure()
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
            logger.debug(f'Failed to find the following top level key in configuration file: {required_top_level_key}')
            return {}
        logger.debug(f'Successfully found top level section key in the configuration file: "{profile_top_key_name}"')

        # Get the listed profiles
        profile_items_all = configs[profile_top_key_name]
        logger.debug(f'Number of listed profiles found: {len(profile_items_all)}')

        # Filter out the profiles that are misconfigured (missing keys)
        profile_items = {}
        required_profile_items = ['jenkins_server_url', 'username']
        logger.debug(
            f'Ignoring profiles that do not have at least the following keys: {", ".join(required_profile_items)} ...')
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

        # PRIORITY 1 - Argument --profile
        if profile:
            if profile in profile_items:
                profile_selected = profile_items[profile]
                profile_selected['profile'] = profile
                logger.debug(f'Successfully matched specified --profile "{profile}"')
            else:
                logger.debug(f'Failed to find the profile specified with --profile "{profile}" in the profiles loaded')
                return {}
        else:
            logger.debug('Argument "--profile" was not specified')

        # PRIORITY 2 - Environmental Variable
        if not profile_selected:
            if self._profile_env_var in os.environ:
                profile = os.getenv(self._profile_env_var)
                if profile in profile_items:
                    profile_selected = profile_items[profile]
                    profile_selected['profile'] = profile
                    logger.debug(
                        f'Successfully matched set {self._profile_env_var } environmental variable value "{profile}"')
                else:
                    logger.debug(
                        f'Failed to find the set environmental variable {self._profile_env_var} "{profile}" in the profiles loaded'
                    )
                    return {}
            else:
                logger.debug(f'Environmental Variable "{self._profile_env_var}" not set')

        # PRIORITY 3 - "default" profile
        if not profile_selected:
            profile = 'default'
            if profile in profile_items:
                profile_selected = profile_items[profile]
                profile_selected['profile'] = profile
                logger.debug('Successfully found "default" profile in the configuration file')
            else:
                logger.debug('Default profile "default" not found')

        # PRIORITY 4 - Any other active one
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

        logger.debug('The following profile has been loaded:')
        logger.debug(f'    - Profile:             {self.jenkins_profile["profile"]}')
        logger.debug(f'    - Jenkins Server URL:  {self.jenkins_profile["jenkins_server_url"]}')
        logger.debug(f'    - Username:            {self.jenkins_profile["username"]}')

        return profile_selected

    def create_auth(self, profile_info: dict = {}) -> bool:
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
            logger.debug('No credential profile loaded')
            return False

        # Check if server url has a protocol schema
        url_protocol_schema = re.findall('(\w+)://', self.jenkins_profile["jenkins_server_url"])
        if not url_protocol_schema:
            logger.debug(
                f'Failed to find a valid server URL protocol schema (ie. http://, https://, etc) in the loaded profile server url: "{self.jenkins_profile["jenkins_server_url"]}"'
            )
            return False

        # Check if password is listed, if not, ask for it
        if 'api_token' not in self.jenkins_profile or not self.jenkins_profile['api_token']:
            print('')
            prompt_text = colors.BOLD + colors.YELLOW + f'Profile {self.jenkins_profile["profile"]} does not contain a "api_token" key' + colors.NORMAL
            print(prompt_text)
            prompt_text = colors.BOLD + colors.YELLOW + f"Enter Jenkins password or server API Token for user {self.jenkins_profile['username']}: " + colors.NORMAL
            self.jenkins_profile['api_token'] = getpass(
                prompt=prompt_text,
                stream=None,
            )
            print('')

            # # Check length of the api_token
            # if len(self.jenkins_profile['api_token']) < 5:
            #     logger.debug(f'The entered API Token has a length of {len(self.jenkins_profile["api_token"])}, which is too short')
            #     return False

            # FIXME: DO NOT pass the prompt text to standard out of command. As a result piping the result WILL NOT work!

        # Load the token or password
        self.jenkins_api_token = self.jenkins_profile['api_token']
        self.jenkins_username = self.jenkins_profile['username']

        # hidden_token = ''.join([ "*" for i in self.jenkins_api_token[:-6]]) + self.jenkins_api_token[-6:]
        hidden_token = ''.join(["*" for i in self.jenkins_profile['api_token']])
        logger.debug(f'    - API Token:           {hidden_token}')

        # Creating Jenkins SDK object(Exception handling: jenkins.JenkinsException)
        try:
            self.JenkinsSDK = JenkinsSDK(url=self.jenkins_profile['jenkins_server_url'],
                                         username=self.jenkins_profile['username'],
                                         password=self.jenkins_profile['api_token'],
                                         timeout=10)
        except Exception as e:
            logger.debug(f'Failed to create Jenkins object. Exception: {e}')
            return False

        # Update the credentials in REST object
        self.REST.set_credentials(username=self.jenkins_profile['username'],
                                  api_token=self.jenkins_profile['api_token'],
                                  server_url=self.jenkins_profile['jenkins_server_url'])

        # Check network connection
        if not self.REST.is_reachable():
            click.echo(
                click.style(f'Jenkins server connection failed (Server: {self.jenkins_profile["jenkins_server_url"]})',
                            fg='bright_red',
                            bold=True))
            click.echo(click.style('Possible causes:', fg='bright_red'))
            click.echo(
                click.style(f'  - Wrong Jenkins server URL: {self.jenkins_profile["jenkins_server_url"]}',
                            fg='bright_red'))
            click.echo(click.style('  - Network/Internet is down', fg='bright_red'))
            click.echo(click.style('Possible solutions:', fg='bright_red'))
            click.echo(click.style('   - Fix yo network connection to server', fg='bright_red'))
            return False

        # Checking authentication
        logger.debug(f'Checking authentication to Jenkins server: {self.jenkins_profile["jenkins_server_url"]} ...')
        if not self.verify():
            # TODO: Move this message to cli_auth.py, only return bool
            click.echo(
                click.style(f'Jenkins server authentication failed (Username: {self.jenkins_profile["username"]})',
                            fg='bright_red',
                            bold=True))
            click.echo(click.style('Possible causes:', fg='bright_red'))
            click.echo(
                click.style(f'    - Wrong Jenkins server URL: {self.jenkins_profile["jenkins_server_url"]}',
                            fg='bright_red'))
            click.echo(click.style(f'    - Incorrect username: {self.jenkins_profile["username"]}', fg='bright_red'))
            click.echo(click.style('    - Incorrect, removed, or expired API Token', fg='bright_red'))
            click.echo(
                click.style(f'    - Username, {self.jenkins_profile["username"]}, does not have permission',
                            fg='bright_red'))
            click.echo(click.style('    - Jenkins server is still in the process of starting up', fg='bright_red'))
            click.echo(click.style('Possible solutions:', fg='bright_red'))
            click.echo(click.style('    - yo-jenkins auth token', fg='bright_red'))
            click.echo(click.style('    - yo-jenkins auth configure', fg='bright_red'))
            click.echo(
                click.style('    - Manually create or update credentials file in home directory', fg='bright_red'))
            click.echo(click.style('    - Go to Jenkins Web UI and check user configurations', fg='bright_red'))
            click.echo(click.style('    - Give Jenkins server a little to start up', fg='bright_red'))
            return False

        return True

    def show_local_credentials(self) -> Dict:
        """Output/Display the credentials profile file

        Args:
            None

        Returns:
            Contents of the credentials profile file
        """
        success, config_filepath = self.detect_configuration_file()
        if not success:
            # If no configuration file found
            return {}

        # Loading configurations file
        return utility.load_contents_from_local_yaml_file(config_filepath)

    def verify(self) -> bool:
        """Verify/Check if current credentials can authenticate with server

        Args:
            None

        Returns:
            True if successfully authenticated, else False
        """
        logger.debug('Verifying server authentication by requesting user information ...')
        try:
            request_url = self.jenkins_profile['jenkins_server_url'].strip('/') + "/me/api/json"
        except:
            logger.debug('Failed to find jenkins_server_url. Profile may not have loaded correctly')
            return False
        request_success = self.REST.request(target=request_url, is_endpoint=False, request_type='head')[2]
        if not request_success:
            logger.debug('Failed server authentication')
            return False
        logger.debug('Successfully authenticated')
        return True

    def user(self) -> Dict:
        """Get current user information

        Details: Targeting the user that is specified in the selected profile

        Args:
            None

        Returns:
            User information
        """
        return self.REST.request('me/api/json', 'get')[0]
