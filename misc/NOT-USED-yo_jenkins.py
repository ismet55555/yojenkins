
#!/usr/bin/env python3

import logging
import os

# from . import YoJenkins
# import YoJenkins
from YoJenkins import YoJenkins

logger = logging.getLogger()


def yo_jenkins() -> int:
    """
    Beginning of program. Called from __main__.py
    """
    current_working_dir = os.getcwd()
    logger.debug(f"Current directory: {current_working_dir}")

    # Create the YoJenkins object and start
    out = YoJenkins()

    return 0
