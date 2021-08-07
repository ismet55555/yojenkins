#!/usr/bin/env python3

import json
import logging
import os
import sys

import click
from yo_jenkins.Docker import DockerJenkinsServer
from yo_jenkins.Utility.utility import get_project_dir, get_resource_path
from yo_jenkins.YoJenkins import Auth, YoJenkins

from yo_jenkins.cli import cli_utility as cu
from yo_jenkins.cli.cli_utility import log_to_history

# Getting the logger reference
logger = logging.getLogger()


@log_to_history
def prepare() -> None:
    """TODO Docstring

    Details: TODO

    Args:
        TODO

    Returns:
        TODO
    """
    pass



@log_to_history
def create_permanent(profile: str) -> None:
    """TODO Docstring

    Details: TODO

    Args:
        TODO

    Returns:
        TODO
    """
    yj = cu.config_yo_jenkins(profile)
    yj.Node.create_permanent()

