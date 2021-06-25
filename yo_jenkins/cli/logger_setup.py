#!/usr/bin/env python3

import logging
import sys
from logging.handlers import RotatingFileHandler

import coloredlogs

# Turn off info level logging for jons2xml
logging.getLogger("dicttoxml").setLevel(logging.ERROR)

# Setting up log file handler
file_handler = RotatingFileHandler(filename='yo-jenkins.log', mode='w', maxBytes=5000000, backupCount=0)

# Also include any sys.stdout in logs
stdout_handler = logging.StreamHandler(sys.stdout)

# Defining the logger
# NOTE: More items: https://docs.python.org/3/library/logging.html#logrecord-attributes
# NOTE: Excluding %(levelname)-8s
LOG_FORMAT = '[%(asctime)s] [%(relativeCreated)-4d] [%(filename)-22s:%(lineno)4s] %(message)s'

# Basic Configurations
logging.basicConfig(level=logging.INFO,
                    format=LOG_FORMAT,
                    datefmt='%H:%M:%S',
                    handlers=[file_handler, stdout_handler])

# Applying color to the output logs
coloredlogs.install(fmt=LOG_FORMAT, datefmt='%H:%M:%S')
