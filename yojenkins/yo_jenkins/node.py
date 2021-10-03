"""Node class definition"""

import json
import logging
import os
from typing import Tuple

import xmltodict

from yojenkins.utility import utility
from yojenkins.yo_jenkins.jenkins_item_classes import JenkinsItemClasses

# Getting the logger reference
logger = logging.getLogger()


class Node():
    """TODO Node"""

    def __init__(self, rest) -> None:
        """Object constructor method, called at object creation

        Args:
            None

        Returns:
            None
        """
        self.rest = rest

    def info(self, node_name: str, depth: int = 0) -> Tuple[list, list]:
        """TODO Docstring

        Details: TODO

        Args:
            node_name: TODO
            depth: TODO

        Returns:
            TODO
        """
        logger.debug(f'Getting info for node: {node_name} ...')
        node_name = "(master)" if node_name == 'master' else node_name  # Special case
        node_info, _, success = self.rest.request(target=f"computer/{node_name}/api/json?depth={depth}",
                                                  request_type='get',
                                                  is_endpoint=True,
                                                  json_content=True)
        if not success:
            logger.debug(f'Failed to find folder info: {node_info}')
            return {}
        return node_info

    def list(self, depth: int = 0) -> bool:
        """TODO Docstring

        Details: TODO

        Args:
            name: TODO

        Returns:
            TODO
        """
        logger.debug('Getting a list of all nodes ...')

        nodes_info, _, success = self.rest.request(target=f"computer/api/json?depth={depth}",
                                                   request_type='get',
                                                   is_endpoint=True,
                                                   json_content=True)
        if not success:
            logger.debug('Failed to get any nodes')
            return {}

        if "computer" not in nodes_info:
            logger.debug('Failed to find "computer" section in return content')
            return False

        node_list, node_list_name = utility.item_subitem_list(
            item_info=nodes_info,
            get_key_info='displayName',
            item_type=JenkinsItemClasses.NODE.value['item_type'],
            item_class_list=JenkinsItemClasses.NODE.value['class_type'])

        logger.debug(f'Number of nodes found: {len(node_list)}')
        logger.debug(f'Node names: {node_list_name}')

        return node_list, node_list_name

    def create_permanent(self, **kwargs) -> bool:
        """TODO Docstring

        Details: TODO

        Args:
            TODO

        Returns:
            TODO
        """
        # TODO: Check if the node already exists. Call exists() method. Need info() method.
        # TODO: Check if credentials exists on server. Check type being SSH

        # Checking name for special characters
        if utility.has_special_char(kwargs['name']):
            return False

        # Processing labels
        if kwargs['labels']:
            labels = utility.parse_and_check_input_string_list(kwargs['labels'], " ")
            if not labels:
                return False
        else:
            # If not list passed, use the node name as label
            labels = kwargs['name']

        logger.debug('Creating and configuring a new permanent node/agent ...')
        logger.debug(f'    - Name:       {kwargs["name"]}')
        logger.debug(f'    - Host:       {kwargs["host"]}')
        logger.debug('    - Connection: SSH')

        # SSH Connection verification strategy
        if kwargs['ssh_verify'] == 'known':
            ssh_verify = {"stapler-class": "hudson.plugins.sshslaves.verifiers.KnownHostsFileKeyVerificationStrategy"}
        elif kwargs['ssh_verify'] == 'trusted':
            ssh_verify = {"stapler-class": "hudson.plugins.sshslaves.verifiers.ManuallyTrustedKeyVerificationStrategy"}
        elif kwargs['ssh_verify'] == 'provided':
            ssh_verify = {
                "stapler-class": "hudson.plugins.sshslaves.verifiers.ManuallyProvidedKeyVerificationStrategy"
            }
        elif kwargs['ssh_verify'] == 'none':
            ssh_verify = {"stapler-class": "hudson.plugins.sshslaves.verifiers.NonVerifyingKeyVerificationStrategy"}

        ssh_launcher = {
            "stapler-class": "hudson.plugins.sshslaves.SSHLauncher",
            "host": kwargs['host'],
            "includeUser": False,
            "credentialsId": kwargs['credential'],
            "sshHostKeyVerificationStrategy": ssh_verify,
            "port": kwargs['ssh_port'],
            "javaPath": kwargs['remote_java_dir'],
            "jvmOptions": "",
            "prefixStartSlaveCmd": "",
            "suffixStartSlaveCmd": "",
            "launchTimeoutSeconds": 60,
            "maxNumRetries": 5,
            "retryWaitTime": 15,
            "tcpNoDelay": True,
            "workDir": ""
        }

        json_params = {
            'nodeDescription': kwargs['description'],
            'numExecutors': kwargs['executors'],
            'remoteFS': kwargs['remote_root_dir'],
            'labelString': labels,
            'mode': kwargs['mode'].upper(),
            'retentionStrategy': {
                'stapler-class': f'hudson.slaves.RetentionStrategy${kwargs["retention"].capitalize()}'
            },
            'nodeProperties': {
                'stapler-class-bag': True
            },
            'launcher': ssh_launcher
        }

        params = {
            'name': kwargs['name'],
            'type': "hudson.slaves.DumbSlave$DescriptorImpl",
            'json': json.dumps(json_params)
        }

        # Send the request to the server
        _, _, success = self.rest.request(target="computer/doCreateItem",
                                          request_type='post',
                                          is_endpoint=True,
                                          data=params)

        logger.debug('Successfully created node' if success else 'Failed to create node')
        return success

    def delete(self, node_name: str) -> bool:
        """TODO Docstring

        Details: TODO

        Args:
            name: TODO

        Returns:
            TODO
        """
        logger.debug(f'Deleting node: {node_name}')
        _, _, success = self.rest.request(target=f"computer/{node_name}/doDelete",
                                          request_type='post',
                                          is_endpoint=True,
                                          json_content=False)
        logger.debug('Successfully deleted node' if success else 'Failed to delete node')
        return success

    def disable(self, node_name: str, message: str = None) -> bool:
        """TODO Docstring

        Details: TODO

        Args:
            name: TODO

        Returns:
            TODO
        """
        logger.debug(f'Disabling node: {node_name}')
        logger.debug(f'Message for disabling node: "{message}"')

        # Check if node is disabled already
        node_info = self.info(node_name=node_name)
        if not node_info:
            return False

        if node_info['offline']:
            logger.debug('Node is already disabled')
            return True

        _, _, success = self.rest.request(target=f"computer/{node_name}/toggleOffline?offlineMessage={message}",
                                          request_type='post',
                                          is_endpoint=True,
                                          json_content=False)
        logger.debug('Successfully disabled node' if success else 'Failed to disable node')
        return success

    def enable(self, node_name: str, message: str = None) -> bool:
        """TODO Docstring

        Details: TODO

        Args:
            name: TODO

        Returns:
            TODO
        """
        logger.debug(f'Enabling node: {node_name}')
        logger.debug(f'Message for enabling node: "{message}"')

        # Check if node is disabled already
        node_info = self.info(node_name=node_name)
        if not node_info:
            return False

        if not node_info['offline']:
            logger.debug('Node is already enabled')
            return True

        _, _, success = self.rest.request(target=f"computer/{node_name}/toggleOffline?offlineMessage={message}",
                                          request_type='post',
                                          is_endpoint=True,
                                          json_content=False)
        logger.debug('Successfully enabled node' if success else 'Failed to enabled node')
        return success

    def config(self,
               filepath: str = '',
               node_name: str = '',
               folder_url: str = '',
               opt_json: bool = False,
               opt_yaml: bool = False,
               opt_toml: bool = False) -> Tuple[str, bool]:
        """TODO Docstring

        Details: TODO

        Args:
            name: TODO

        Returns:
            TODO
        """
        logger.debug(f'Fetching XML configurations for node: {node_name} ...')
        node_name = "(master)" if node_name == 'master' else node_name  # Special case
        return_content, _, success = self.rest.request(f'computer/{node_name}/config.xml',
                                                       'get',
                                                       json_content=False,
                                                       is_endpoint=True)
        logger.debug('Successfully fetched XML configurations' if success else 'Failed to fetch XML configurations')

        if filepath:
            write_success = utility.write_xml_to_file(return_content, filepath, opt_json, opt_yaml, opt_toml)
            if not write_success:
                return "", False

        return return_content, True

    def reconfig(self, node_name: str, config_file: str = None, config_is_json: bool = False) -> bool:
        """TODO Docstring

        Details: TODO

        Args:
            name: TODO

        Returns:
            TODO
        """
        logger.debug(f'Reconfiguring node: {node_name} ...')
        logger.debug(f'Using the following specified configuration file: {config_file}')

        logger.debug(f'Checking if file exists: {config_file} ...')
        if not os.path.isfile(config_file):
            logger.debug('Specified configuration file does not exist')
            return False

        logger.debug(f'Reading configuration file: {config_file} ...')
        try:
            with open(config_file, 'rb') as file:
                node_config = file.read()
            logger.debug('Successfully read configuration file')
        except Exception as error:
            logger.debug(f'Failed to read configuration file. Exception: {error}')
            return False

        if config_is_json:
            logger.debug('Converting the specified JSON file to XML format ...')
            try:
                node_config = xmltodict.unparse(json.loads(node_config))
            except Exception as error:
                logger.debug(f'Failed to convert the specified JSON file to XML format. Exception: {error}')
                return False

        _, _, success = self.rest.request(target=f"computer/{node_name}/config.xml",
                                          request_type='post',
                                          is_endpoint=True,
                                          data=node_config.encode('utf-8'),
                                          json_content=False)
        logger.debug('Successfully reconfigured node' if success else 'Failed to reconfigure node')
        return success
