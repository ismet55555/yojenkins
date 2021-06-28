#!/usr/bin/env python3

import logging
from pprint import pprint
from yo_jenkins.Docker.DockerJenkinsServer import DockerJenkinsServer

# Setup a message logging
log_format = '[%(asctime)s] [%(relativeCreated)-4d] [%(filename)-23s:%(lineno)4s] %(message)s'
logging.basicConfig(level=logging.DEBUG, format=log_format, datefmt='%H:%M:%S')

DJS = DockerJenkinsServer()
DJS.setup()
