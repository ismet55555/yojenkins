"""Node class definition"""

import json
import logging
import os
from typing import Tuple

import xmltodict

from yojenkins.utility import utility
from yojenkins.utility.utility import fail_out, print2
from yojenkins.yo_jenkins.jenkins_item_classes import JenkinsItemClasses

# Getting the logger reference
logger = logging.getLogger()


class Node():
    """TODO Node"""

    def __init__(self, rest: object) -> None:
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
            fail_out(f'Failed to find node info for "{node_name}"')

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
            fail_out('Failed to get any nodes')

        if "computer" not in nodes_info:
            fail_out('Failed to find "computer" section in return content')

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
            fail_out('Provided node name contains special characters')

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
        success = self.rest.request(target="computer/doCreateItem", request_type='post', is_endpoint=True,
                                    data=params)[2]
        if not success:
            fail_out('Failed to create permanent node')
        logger.debug('Successfully created permanent node')

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
        success = self.rest.request(target=f"computer/{node_name}/doDelete",
                                    request_type='post',
                                    is_endpoint=True,
                                    json_content=False)[2]
        if not success:
            fail_out(f'Failed to delete node "{node_name}"')

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
        if node_info['offline']:
            print2('Node is already disabled')
            return True

        success = self.rest.request(target=f"computer/{node_name}/toggleOffline?offlineMessage={message}",
                                    request_type='post',
                                    is_endpoint=True,
                                    json_content=False)[2]
        if not success:
            fail_out(f'Failed to disable node "{node_name}"')

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
        if not node_info['offline']:
            print2('Node is already enabled')
            return True

        success = self.rest.request(target=f"computer/{node_name}/toggleOffline?offlineMessage={message}",
                                    request_type='post',
                                    is_endpoint=True,
                                    json_content=False)[2]
        if not success:
            fail_out(f'Failed to enable node "{node_name}"')

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
        if not success:
            fail_out(f'Failed to fetch node configurations for node "{node_name}"')

        if filepath:
            write_success = utility.write_xml_to_file(return_content, filepath, opt_json, opt_yaml, opt_toml)
            if not write_success:
                fail_out('Failed to write node configurations to file')

        return return_content

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
            fail_out('Specified node configuration file does not exist')

        logger.debug(f'Reading configuration file: {config_file} ...')
        try:
            with open(config_file, 'rb') as file:
                node_config = file.read()
            logger.debug('Successfully read configuration file')
        except (OSError, IOError, PermissionError) as error:
            fail_out(f'Failed to open and read node configuration file. Exception: {error}')

        if config_is_json:
            logger.debug('Converting the specified JSON file to XML format ...')
            try:
                node_config = xmltodict.unparse(json.loads(node_config))
            except Exception as error:
                fail_out(f'Failed to convert the specified JSON file to XML format. Exception: {error}')

        success = self.rest.request(target=f"computer/{node_name}/config.xml",
                                    request_type='post',
                                    is_endpoint=True,
                                    data=node_config.encode('utf-8'),
                                    json_content=False)[2]
        if not success:
            fail_out(f'Failed to reconfigure node "{node_name}"')

        return success
