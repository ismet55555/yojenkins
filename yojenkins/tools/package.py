"""Project dynamic management"""

import logging
import subprocess
import sys

# Getting the logger reference
logger = logging.getLogger()

# NOTE: Using pip within code with "import pip" is not recommended:
#       https://pip.pypa.io/en/latest/user_guide/#using-pip-from-your-program


class Package():
    """Class managing updating of this software"""

    @staticmethod
    def install(package_name: str = 'yojenkins', upgrade: bool = True, user: bool = True, proxy: str = "") -> bool:
        """TODO Docstring

        Details: TODO

        Args:
            TODO

        Returns:
            TODO
        """
        logger.debug(f'Installing "{package_name}" ...')
        logger.debug(f'    - Upgrade:      {upgrade}')
        logger.debug(f'    - User context: {user}')
        logger.debug(f'    - Proxy:        {proxy if proxy else "None"}')

        upgrade_option = "--upgrade" if upgrade else ""
        user_option = "--user" if user else ""
        proxy_option = proxy if proxy else ""

        arg_list = [sys.executable, "-m", "pip", "install", upgrade_option, user_option, proxy_option, package_name]

        # Remove blanks
        arg_list = [arg_item for arg_item in arg_list if arg_item]

        try:
            subprocess.check_call(arg_list)
        except Exception as error:
            logger.debug(f'Failed to install/upgrade {package_name}. Exception: {error}')
            return False

        return True

    @staticmethod
    def uninstall(package_name: str = 'yojenkins', auto_yes: bool = True) -> bool:
        """TODO Docstring

        Details: TODO

        Args:
            TODO

        Returns:
            TODO
        """
        logger.debug(f'Uninstalling "{package_name}" ...')
        logger.debug(f'    - Auto yes: {auto_yes}')

        auto_yes_option = "--yes" if auto_yes else ""

        arg_list = [sys.executable, "-m", "pip", "uninstall", auto_yes_option, package_name]

        # Remove blanks
        arg_list = [arg_item for arg_item in arg_list if arg_item]

        try:
            subprocess.check_call(arg_list)
        except Exception as error:
            logger.debug(f'Failed to uninstall {package_name}. Exception: {error}')
            return False
        return True
