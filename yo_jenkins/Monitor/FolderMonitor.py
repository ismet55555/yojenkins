#!/usr/bin/env python3

import curses
import logging
import os
import sys
import textwrap
import threading
from pprint import pprint
from time import sleep, time
from typing import Dict, List, Tuple, Type

from yo_jenkins.YoJenkins.Status import BuildStatus, Color, Sound, StageStatus, Status

# from Monitor.Monitor import Monitor
from yo_jenkins.Monitor.Monitor import Monitor

from . import monitor_utility as mu

# Getting the logger reference
logger = logging.getLogger()


class FolderMonitor(Monitor):
    """This class defines the BuildMonitor class and its function.
    
    The FolderMonitor class enables active folder monitoring
    """

    def __init__(self, Build) -> None:
        """Object constructor method, called at object creation

        Args:
            Build: Build object

        Returns:
            None
        """
        # Get attributes form super (parent) class
        super().__init__()
