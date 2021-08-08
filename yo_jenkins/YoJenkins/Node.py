#!/usr/bin/env python3

import json
import logging

from yo_jenkins.Utility import utility

# Getting the logger reference
logger = logging.getLogger()


class Node():
    """TODO Node"""

    def __init__(self, REST, Auth) -> None:
        """Object constructor method, called at object creation

        Args:
            None

        Returns:
            None
        """
        self.REST = REST
        self.Auth = Auth

        self.server_base_url = self.Auth.jenkins_profile['jenkins_server_url']

    def exists(self, name: str) -> bool:
        """TODO Docstring

        Details: TODO

        Args:
            name: TODO

        Returns:
            TODO
        """
        logger.debug(f'Checking if node/agent exists: {name}')

        request = "computer/doGetItem"

        params = {'name': name}

        content, headers, success = self.REST.request(target=request,
                                                      request_type='get',
                                                      is_endpoint=True,
                                                      json_content=False,
                                                      data=params)
        return success

    def create_permanent(self, **kwargs) -> bool:
        """TODO Docstring

        Details: TODO

        Args:
            TODO

        Returns:
            TODO
        """
        # TODO: Check if the node already exists. Call exists() method. Need info() method.

        # Checking name for special characters
        if utility.has_special_char(kwargs['name']):
            return False

        # Processing labels
        if kwargs['labels']:
            labels = []
            for label in kwargs['labels'].split(','):
                label = label.strip()
                if utility.has_special_char(label):
                    return False
                labels.append(label)
            labels = " ".join(labels)
        else:
            labels = kwargs['name']

        logger.debug('Creating and configuring a new permanent node/agent ...')
        logger.debug(f'    - Name:       {kwargs["name"]}')
        logger.debug(f'    - Host:       {kwargs["host"]}')
        logger.debug(f'    - Connection: SSH')


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
        _, _, success = self.REST.request(target="computer/doCreateItem",
                                          request_type='post',
                                          is_endpoint=True,
                                          data=params)

        logger.debug('Successfully created node/agent' if success else 'Failed to create node/agent')
        return success
