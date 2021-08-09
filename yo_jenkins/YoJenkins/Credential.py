#!/usr/bin/env python3

import json
import logging
import os
from typing import Tuple

import toml
import xmltodict
import yaml
from yo_jenkins.Utility import utility
from yo_jenkins.YoJenkins.JenkinsItemClasses import JenkinsItemClasses

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
        node_info, _, success = self.REST.request(target=f"computer/{node_name}/api/json?depth={depth}",
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

        nodes_info, _, success = self.REST.request(target=f"computer/api/json?depth={depth}",
                                                   request_type='get',
                                                   is_endpoint=True,
                                                   json_content=True)
        if not success:
            logger.debug('Failed to get any nodes ...')
            return {}

        if "computer" not in nodes_info:
            logger.debug('Failed to find "computer" section in return content')
            return False

        node_list, node_list_name = utility.item_subitem_list(
            item_info=nodes_info,
            get_key_info='displayName',
            item_type=JenkinsItemClasses.node.value['item_type'],
            item_class_list=JenkinsItemClasses.node.value['class_type'])

        logger.debug(f'Number of nodes found: {len(node_list)}')
        logger.debug(f'Node names: {node_list_name}')

        return node_list, node_list_name

    def create(self, **kwargs) -> bool:
        """TODO Docstring

        Details: TODO

        Args:
            TODO

        Returns:
            TODO
        """
        pass

    def delete(self, node_name: str) -> bool:
        """TODO Docstring

        Details: TODO

        Args:
            name: TODO

        Returns:
            TODO
        """
        logger.debug(f'Deleting node: {node_name}')
        _, _, success = self.REST.request(target=f"computer/{node_name}/doDelete",
                                          request_type='post',
                                          is_endpoint=True,
                                          json_content=False)
        logger.debug('Successfully deleted node' if success else 'Failed to delete node')
        return success
