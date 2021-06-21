#!/usr/bin/env python3

import logging
import os
import sys
from pprint import pprint
from time import time
from Setup.DockerJenkinsServer import DockerJenkinsServer

# Setup a message logging
log_format = '[%(asctime)s] [%(relativeCreated)-4d] [%(filename)-23s:%(lineno)4s] %(message)s'
logging.basicConfig(level=logging.DEBUG, format=log_format, datefmt='%H:%M:%S')

DJS = DockerJenkinsServer()
DJS.setup()
