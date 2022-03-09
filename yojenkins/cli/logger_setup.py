""""Logger Setup"""

# TODO: Move to utilities

import logging
import sys
from logging.handlers import RotatingFileHandler

import coloredlogs

# Turn off INFO level logging for python package "jons2xml"
logging.getLogger("dicttoxml").setLevel(logging.ERROR)
logging.getLogger("urllib3").setLevel(logging.WARNING)

# Setting up log file handler
file_handler = RotatingFileHandler(filename='yojenkins.log',
                                   mode='a',
                                   maxBytes=5000000,
                                   backupCount=0,
                                   delay=True,
                                   encoding="utf-8")

# Also include any sys.stdout in logs
stdout_handler = logging.StreamHandler(sys.stdout)

# Defining the logger
# NOTE: More items: https://docs.python.org/3/library/logging.html#logrecord-attributes
# NOTE: Excluding %(levelname)-8s
LOG_FORMAT = '[%(asctime)s] [%(relativeCreated)-4d] [%(filename)-24s:%(lineno)4s] %(message)s'

# Basic Configurations
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT, datefmt='%H:%M:%S', handlers=[file_handler, stdout_handler])

# Applying color to the output logs
coloredlogs.install(fmt=LOG_FORMAT, datefmt='%H:%M:%S')
