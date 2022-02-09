"""Folder monitor"""

# import curses
import logging

from yojenkins.monitor.monitor import Monitor

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
        # Get attributes from super (parent) class
        super().__init__()

        pass
