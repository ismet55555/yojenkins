#!/usr/bin/env python3

import logging
import winsound
import os
import platform

# Creating a message logger
format = f"[%(asctime)s][%(levelname)-10s] %(message)s"
logger = logging.basicConfig(level=logging.INFO, format=format, datefmt="%d-%b-%y %H:%M:%S")
logger = logging.getLogger()

filepath = 'yo_jenkins\sound\positive_alert_notification_musical_short_marimba_process_finished.wav'

try:
    winsound.PlaySound(filepath, winsound.SND_FILENAME | winsound.SND_NODEFAULT)
except RuntimeError as error:
    logger.error(f'Failed to play sound. Exception: {error}')
