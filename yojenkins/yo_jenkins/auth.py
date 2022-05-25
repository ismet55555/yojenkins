"""Auth class definition"""

import logging
import os
import re
import sys
from datetime import datetime
from getpass import getpass
from pathlib import Path
from typing import Any, Dict, Tuple

import toml
from jenkins import Jenkins as JenkinsSDK

from yojenkins.utility import utility
from yojenkins.utility.utility import TextStyle, fail_out, failures_out, print2
from yojenkins.yo_jenkins.rest import Rest

# Getting the logger reference
logger = logging.getLogger()

# TODO: Find centralized location for these static values
CONFIG_DIR_NAME = '.yojenkins'
CREDS_FILE_NAME = 'credentials'
PROFILE_ENV_VAR = 'YOJENKINS_PROFILE'

REQUIRED_PROFILE_KEYS = ['jenkins_server_url', 'username']
ALLOWED_PROFILE_KEYS = ['jenkins_server_url', 'username', 'api_token', 'active']


class Auth:
    """Handeling of authentication and profile management functionality"""

    def __init__(self, rest=None) -> None:
        """Object constructor method, called at object creation

        Args:
            None

        Returns:
            None
        """
        # Request object
        if not rest:
            # If not provided, make a new object
            self.rest: object = Rest()
        else:
            self.rest: object = rest

        # JenkinsSDK object - Instantiated in create_auth()
        self.jenkins_sdk = None

        self.jenkins_profile: Dict[str, Any] = {}
        self.jenkins_username = ''
        self.jenkins_api_token = ''
        self.authenticated = False

    def _update_profiles(self, profiles: dict) -> bool:
        """Create/Update the current credentials profile file

        Details: This method will overwrite any previous file content.
                 It will also add a file prefix for TOML formats

        Args:
            profiles : All profile info to be written to file

        Returns:
            True if successfull, else False
        """
        # Storing configurations in file
        output_path = os.path.join(Path.home(), CONFIG_DIR_NAME, CREDS_FILE_NAME)
        logger.debug(f'Saving new file (TOML format): "{output_path}" ...')
        with open(os.path.join(output_path), 'w') as file:  # Overwrite previous content
            toml.dump(profiles, file)

        # Add top file prefix for TOML file format
        lines_new = [f'# -*- mode: toml -*-{os.linesep}', f'# vim: set filetype=toml{os.linesep}']
        success = utility.append_lines_to_file(output_path, lines_new, 'beginning')
        if not success:
            return False

        return True

    def get_rest(self) -> object:
        """Convenience method to return the REST object

        Args:
            None

        Returns:
            Rest Object
        """
        return self.rest

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
            prompt_text = TextStyle.BOLD + TextStyle.YELLOW + "Enter desired API TOKEN NAME: " + TextStyle.NORMAL
            token_name = input(prompt_text)
            logger.debug(f'User input: {token_name}')

        if not server_base_url:
            prompt_text = TextStyle.BOLD + TextStyle.YELLOW + "Enter Jenkins SERVER BASE URL: " + TextStyle.NORMAL
            server_base_url = input(prompt_text)
            logger.debug(f'User input: {server_base_url}')

        if not username:
            prompt_text = TextStyle.BOLD + TextStyle.YELLOW + 'Enter Jenkins server USERNAME: ' + TextStyle.NORMAL
            username = input(prompt_text)
            logger.debug(f'User input: {username}')

        if not password:
            prompt_text = TextStyle.BOLD + TextStyle.YELLOW + f'Enter "{username}" PASSWORD: ' + TextStyle.NORMAL
            password = getpass(prompt=prompt_text, stream=None)
            logger.debug('User entered password')

        # Requesting the Jenkins crumb
        request_return_text, _, success = self.rest.request(target=server_base_url.strip('/') + '/crumbIssuer/api/xml',
                                                            is_endpoint=False,
                                                            request_type='get',
                                                            json_content=False,
                                                            auth=(username, password),
                                                            new_session=True)
        if not success:
            fail_out('Failed to generate API token. Crumb issuer failed. '
                     'Check server base URL, username, or password.')
        crumb_value = re.sub(re.compile('<.*?>|Jenkins-Crumb'), '', request_return_text)
        logger.debug(f'Request crumb value: {crumb_value}')

        # Generating the token
        headers = {'Jenkins-Crumb': crumb_value}
        params = (
            ('newTokenName', token_name),
            ('tree', 'data[tokenValue]'),
        )
        request_return_content, _, success = self.rest.request(
            target=server_base_url.strip('/') +
            '/me/descriptorByName/jenkins.security.ApiTokenProperty/generateNewToken/api/json',
            is_endpoint=False,
            request_type='post',
            json_content=True,
            auth=(username, password),
            new_session=False,
            params=params,
            headers=headers)
        if not success:
            fail_out('Failed to generate API token. Request failed')

        try:
            generated_token = request_return_content['data']['tokenValue']
            logger.debug(f'Successfully generated server API token "{token_name}"!')
        except KeyError:
            fail_out('Failed to generate API token. Failed to find "tokenValue" in the POST request return header')

        return generated_token

    def profile_add_new_token(self, profile_name: str) -> str:
        """Update the specified credentials profile with a new server API token

        Args:
            profile_name : Name of the profile as specified in the credentials file

        Returns:
            Server API Token
        """
        # Check if the credential config file exists
        file_exists, file_path = self._detect_creds_file()
        if not file_exists:
            fail_out('Credential configuration ')

        # Load the current cred config file
        profiles = utility.load_contents_from_local_file("toml", file_path)
        if not profiles:
            return ''

        # Check if the profile exists
        if profile_name not in profiles:
            fail_out(f'Profile "{profile_name}" does not exist in the credentials file')

        profile_info = profiles[profile_name]
        logger.debug(f'Profile "{profile_name}" loaded')
        logger.debug(f'Profile info: {profile_info}')

        # Generate a API token name (seen in Jenkins UI)
        token_name = f'yojenkins_{datetime.now().strftime("%m-%d-%Y_%I-%M-%S")}'

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

        # Generate and store the API token
        api_token = self.generate_token(token_name=token_name, server_base_url=server_url, username=username)
        profiles[profile_name]['api_token'] = api_token

        success = self._update_profiles(profiles=profiles)
        if not success:
            fail_out(f'Failed to add new API token to profile "{profile_name}"')

        return api_token

    def configure(self, auth_file: str = '') -> bool:
        """Configure/add a new credentials profile

        Details: This method will prompt the user with a series of questions
                 to add a new profile to the credentials profile file

        Args:
            auth_file : (Optional) Path to the the authentication setup JSON file

        Returns:
            This is a description of what is returned.
        """
        config_dir_abs_path = os.path.join(Path.home(), CONFIG_DIR_NAME)

        # Checking if credential config file exists
        file_exists, file_path = self._detect_creds_file()
        if file_exists:
            logger.debug(f'Credentials file found in current user home directory: {file_path}')
            logger.debug(f'Loading credentials file: {file_path} ...')

            # Load the current cred config file
            profiles = utility.load_contents_from_local_file("toml", file_path)
            logger.debug(f'Currently listed profile names: {", ".join(list(profiles.keys()))}')

            logger.debug(f'Credentials profile file found in current user home directory: {file_path}')
        else:
            creds_file_abs_path = os.path.join(config_dir_abs_path, CREDS_FILE_NAME)

            logger.debug('Credentials file NOT found in current user configuration directory')
            logger.debug(f'Creating credentials file: {creds_file_abs_path} ...')

            # Create new profile from scratch
            profiles = {}

            logger.debug(f'Credentials profile file NOT found: "{creds_file_abs_path}"')
            logger.debug(f'Creating a new credentials file ...')

        # Check if user passed authentication info file
        if auth_file:
            # Load the authentication setup JSON file
            setup_info = utility.load_contents_from_local_file("json", auth_file)
            if not setup_info:
                fail_out(f'Failed to load authentication setup JSON info file: {auth_file}')

            print2(f'Adding {len(setup_info)} authentication profile(s) specified in file "{auth_file}" ...')

            # Check each provided authentication setup profile
            # FIXME: Implement JSON Schema validation !!!!
            for index, (setup_profile_name, setup_profile_info) in enumerate(setup_info.items()):
                print2('')
                print2(f'[{index + 1} of {len(setup_info)}] Adding profile: {setup_profile_name} ...')

                failed_to_add = False

                # Check allowed keys
                keys_to_remove = []
                for key in setup_profile_info.keys():
                    if key not in ALLOWED_PROFILE_KEYS:
                        logger.debug(f'  - Invalid key:  {key} - IGNORING')
                        keys_to_remove.append(key)
                [setup_profile_info.pop(key, None) for key in keys_to_remove]

                # Check required keys to setup a new profile
                for required_key in REQUIRED_PROFILE_KEYS:
                    if required_key not in setup_profile_info.keys():
                        print2(f'  - Required key: {required_key} - NOT FOUND', color='red')
                        print2(f'Failed to add authentication profile: {setup_profile_name}', color='red')
                        failed_to_add = True
                    else:
                        logger.debug(f'  - Required key: {required_key} - FOUND')

                        # Check if required key value is not empty
                        if not setup_profile_info[required_key]:
                            print2(f'  - Required key: {required_key} - EMPTY VALUE', color='red')
                            failed_to_add = True
                        else:
                            logger.debug(f'  - Required key: {required_key} - HAS VALUE')

                if failed_to_add:
                    print2(f'Failed to add authentication profile: {setup_profile_name}', color='red')
                    continue

                # Check if the profile already exists
                if setup_profile_name in profiles:
                    print2(f'  - Profile "{setup_profile_name}" already exists in the credentials file. Replacing ...',
                           color="yellow")

                # If API token is not there, add a blank for it
                if 'api_token' not in setup_profile_info:
                    setup_profile_info['api_token'] = ''

                # Set to active if not specified
                if 'active' not in setup_profile_info:
                    setup_profile_info['active'] = True

                # Add to profiles to add
                profiles[setup_profile_name] = setup_profile_info
        else:
            # Prompting user for details
            print2('Please enter the following information to create your first profile entry')
            print2(f'This information will be stored in "{creds_file_abs_path}"')
            print2('')
            profile_name = input(TextStyle.BOLD + TextStyle.YELLOW + '[ OPTIONAL ] Enter PROFILE NAME (default):  ' +
                                 TextStyle.NORMAL)
            profile_name = 'default' if not profile_name else profile_name
            if profile_name in profiles:
                print2('')
                print2(f'WARNING : You are about to overwrite the current profile "{profile_name}"')
                print2('')
            profiles[profile_name] = {}
            profiles[profile_name]['jenkins_server_url'] = input(TextStyle.BOLD + TextStyle.YELLOW +
                                                                 '[ REQUIRED ] Enter Jenkins SERVER BASE URL:  ' +
                                                                 TextStyle.NORMAL)
            profiles[profile_name]['username'] = input(TextStyle.BOLD + TextStyle.YELLOW +
                                                       '[ REQUIRED ] Enter USERNAME:  ' + TextStyle.NORMAL)

            # If set up manually, set as active by default
            profiles[profile_name]['active'] = True

        return self._update_profiles(profiles=profiles)

    def _detect_config_dir(self) -> Tuple[bool, str]:
        """Detect/find the configuration directory in the home directory

        Args:
            None

        Returns:
            Success, Directory path of the credentials profile file
        """
        home_dir = Path.home()
        if not os.path.exists(home_dir):
            logger.debug(f'Home directory does not exist: {home_dir}')
            return False, ''
        config_dir_abs_path = os.path.join(home_dir, CONFIG_DIR_NAME)
        if not os.path.exists(config_dir_abs_path):
            logger.debug(f'Configuration directory does not exist: {config_dir_abs_path}')
            return False, ''
        return True, config_dir_abs_path

    def _detect_creds_file(self) -> Tuple[bool, str]:
        """Detect/find the credentials profile file in the home directory

        Args:
            None

        Returns:
            Success, File path of the credentials profile file
        """
        if not self._detect_config_dir()[0]:
            return False, ''
        config_dir_abs_path = os.path.join(Path.home(), CONFIG_DIR_NAME)

        # Seeing if configuration file is in specified directories
        if os.path.exists(os.path.join(config_dir_abs_path, CREDS_FILE_NAME)):
            logger.debug(f'Successfully found credential file "{CREDS_FILE_NAME}" found in user '
                         f'configuration directory: {config_dir_abs_path}')
            config_filepath = os.path.join(config_dir_abs_path, CREDS_FILE_NAME)
            return True, config_filepath
        else:
            logger.debug(f'Failed to find credential file "{CREDS_FILE_NAME}" in user '
                         f'configuration directory: {config_dir_abs_path}')
            return False, ''

    def get_credentials(self, profile: str = '') -> Dict:
        """Get the contents of the credentials profiles file

        Details: The order (preference) of specified profile credentials to get are the following:
            - Passed `profile` argument
            - Environmental Variable as specified in `PROFILE_ENV_VAR`
            - Profile listed as `default` in the credentials profile file
            - Any other / first profile set to active

        Args:
            profile : (Optional) Only get the configuration for particular profile

        Returns:
            The credential information of the specified credentials profile
        """
        creds_file_abs_path = os.path.join(Path.home(), CONFIG_DIR_NAME, CREDS_FILE_NAME)
        if not self._detect_creds_file()[0]:
            # If no configuration file found, configure one
            logger.debug('No credentials file found. Configuring one ...')
            self.configure()

        # Loading configurations file
        creds_info = utility.load_contents_from_local_file("toml", creds_file_abs_path)
        if not creds_info:
            fail_out(f'Failed to load credentials file: {creds_file_abs_path}')

        # Get the listed profiles
        profile_items_all = creds_info
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
            failures_out([
                'Failed to find any valid profiles in the configuration file',
                f'A valid profile must have at least the follwing keys: {", ".join(required_profile_items)}'
            ])

        # Select the credential profile
        profile_selected = {}

        # PRIORITY 1 - Argument --profile
        if profile:
            if profile in profile_items:
                profile_selected = profile_items[profile]
                profile_selected['profile'] = profile
                logger.debug(f'Successfully matched specified --profile "{profile}"')
            else:
                fail_out(f'Failed to find the profile "{profile}" within all loaded '
                         f'profiles: {", ".join(list(profile_items.keys()))}')
        else:
            logger.debug('Argument "--profile" was not specified')

        # PRIORITY 2 - Environmental Variable
        if not profile_selected:
            if PROFILE_ENV_VAR in os.environ:
                profile = os.getenv(PROFILE_ENV_VAR)
                if profile in profile_items:
                    profile_selected = profile_items[profile]
                    profile_selected['profile'] = profile
                    logger.debug(
                        f'Successfully matched set {PROFILE_ENV_VAR} environmental variable value "{profile}"')
                else:
                    fail_out(f'Failed to find the set environmental variable {PROFILE_ENV_VAR} "{profile}" '
                             'in the profiles loaded')
            else:
                logger.debug(f'Environmental Variable "{PROFILE_ENV_VAR}" not set')

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
            fail_out('No active user profiles found. If no profile was set up, please configure one')

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
            fail_out('No credential profile loaded')

        # Check if server url has a protocol schema
        url_protocol_schema = re.findall('(\w+)://', self.jenkins_profile["jenkins_server_url"])
        if not url_protocol_schema:
            fail_out('Failed to find a valid server URL protocol schema (ie. http://, https://, etc) '
                     f'in the loaded profile server url: "{self.jenkins_profile["jenkins_server_url"]}"')

        # Check if password is listed, if not, ask for it
        if 'api_token' not in self.jenkins_profile or not self.jenkins_profile['api_token']:
            print2('')
            prompt_text = f'Profile {self.jenkins_profile["profile"]} does not contain a "api_token" key'
            print2(prompt_text, bold=True, color='yellow')
            prompt_text = TextStyle.BOLD + TextStyle.YELLOW + f"Enter Jenkins password or server API Token for user {self.jenkins_profile['username']}: " + TextStyle.NORMAL
            self.jenkins_profile['api_token'] = getpass(
                prompt=prompt_text,
                stream=None,
            )
            print2('')

            # # Check length of the api_token
            # if len(self.jenkins_profile['api_token']) < 5:
            #     logger.debug(f'The entered API Token has a length of {len(self.jenkins_profile["api_token"])}, which is too short')
            #     return False

            # FIXME: DO NOT pass the prompt text to standard out of command. As a result, piping the result WILL NOT work!

        # Load the token or password
        self.jenkins_api_token = self.jenkins_profile['api_token']
        self.jenkins_username = self.jenkins_profile['username']

        # hidden_token = ''.join([ "*" for i in self.jenkins_api_token[:-6]]) + self.jenkins_api_token[-6:]
        hidden_token = ''.join(["*" for i in self.jenkins_profile['api_token']])
        logger.debug(f'    - API Token:           {hidden_token}')

        # Creating Jenkins SDK object(Exception handling: jenkins.JenkinsException)
        try:
            self.jenkins_sdk = JenkinsSDK(url=self.jenkins_profile['jenkins_server_url'],
                                          username=self.jenkins_profile['username'],
                                          password=self.jenkins_profile['api_token'],
                                          timeout=10)
        except Exception as error:
            fail_out(f'Internal Error: Failed to create Jenkins object. Exception: {error}')

        # Update the credentials in Rest object
        self.rest.set_credentials(username=self.jenkins_profile['username'],
                                  api_token=self.jenkins_profile['api_token'],
                                  server_url=self.jenkins_profile['jenkins_server_url'])

        # Check network connection
        if not self.rest.is_reachable():
            print2(f'Jenkins server connection failed (Server: {self.jenkins_profile["jenkins_server_url"]})',
                   bold=True,
                   color='red')
            print2('Possible causes:', bold=True, color='red')
            print2(f'  - Wrong Jenkins server URL: {self.jenkins_profile["jenkins_server_url"]}',
                   bold=True,
                   color='red')
            print2('  - Network/Internet is down', bold=True, color='red')
            print2('  - Server container is down', bold=True, color='red')
            print2('Possible solutions:', bold=True, color='red')
            print2('   - Fix yo network connection to server', bold=True, color='red')
            print2('   - Check if the server container or container engine is up and running', bold=True, color='red')
            sys.exit(1)

        # Checking authentication
        logger.debug(f'Checking authentication to Jenkins server: {self.jenkins_profile["jenkins_server_url"]} ...')
        if not self.verify():
            # TODO: Move this message to cli_auth.py, only return bool
            print2(f'Jenkins server authentication failed (Username: {self.jenkins_profile["username"]})',
                   bold=True,
                   color='red')
            print2('Possible causes:', bold=True, color='red')
            print2(f'    - Wrong Jenkins server URL: {self.jenkins_profile["jenkins_server_url"]}',
                   bold=True,
                   color='red')
            print2(f'    - Incorrect username: {self.jenkins_profile["username"]}', bold=True, color='red')
            print2('    - Incorrect, removed, or expired API Token', bold=True, color='red')
            print2(f'    - Username, {self.jenkins_profile["username"]}, does not have permission',
                   bold=True,
                   color='red')
            print2('    - Jenkins server is still in the process of starting up', bold=True, color='red')
            print2('Possible solutions:', bold=True, color='red')
            print2('    - yojenkins auth token', bold=True, color='red')
            print2('    - yojenkins auth configure', bold=True, color='red')
            print2('    - Manually create or update credentials file in home directory', bold=True, color='red')
            print2('    - Go to Jenkins Web UI and check user configurations', bold=True, color='red')
            print2('    - Give Jenkins server a little to start up', bold=True, color='red')
            sys.exit(1)

        return True

    def show_local_credentials(self) -> Dict:
        """Output/Display the credentials profile file

        Args:
            None

        Returns:
            Contents of the credentials profile file
        """
        success, config_filepath = self._detect_creds_file()
        if not success:
            # If no configuration file found
            fail_out(f'Failed to find a valid credentials file')

        # Loading configurations file
        return utility.load_contents_from_local_file("toml", config_filepath)

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
        except KeyError:
            fail_out('Failed to find profile key "jenkins_server_url". Profile may not have loaded correctly')
        request_success = self.rest.request(target=request_url, is_endpoint=False, request_type='head')[2]
        if not request_success:
            fail_out('Failed server authentication with specified user credentials')
        logger.debug('Successfully authenticated with specified user credentials')

        return True

    def user(self) -> Dict:
        """Get current user information

        Details: Targeting the user that is specified in the selected profile

        Args:
            None

        Returns:
            User information
        """
        data = self.rest.request('me/api/json', 'get')[0]
        if not data:
            fail_out('Failed to get user information')
        return data
