"""Monitor parent class"""

import curses
import logging
import platform
import sys
import threading
from time import sleep, time

if platform.system() != "Windows":
    try:
        import simpleaudio
    except:
        pass
else:
    import winsound

from yojenkins.yo_jenkins.status import Color, Sound, Status

from . import monitor_utility as mu

# Getting the logger reference
logger = logging.getLogger()


class Monitor:
    """Parent class for all monitor objects"""

    def __init__(self) -> None:
        """Object constructor method, called at object creation

        Args:
            None

        Returns:
            None
        """
        self.rest = None
        self.auth = None
        self.job = None
        self.build = None

        self.color = {}
        self.decor = {}

        self.halfdelay_screen_refresh = 5  # number of 10th of a second

        self.height_limit = 35
        self.width_limit = 66
        self.terminal_size_good = True

        self.curses_alive = True

        self.quit = 0
        self.exit = False
        self.help = False

        self.server_status_data = {}
        self.server_status_thread_interval = 0.0

        self.playing_sound = False

        self.all_threads_enabled = True
        self.paused = False

        self.server_interaction = False

    def __del__(self):
        """ TODO """
        # Just in case turn off all threads
        self.all_threads_off()

    ###########################################################################
    #                         CURSES UTILITY
    ###########################################################################

    def basic_screen_setup(self, halfdelay: bool) -> None:
        """
        Basic configurations of the current curses terminal screen

        Args:
            halfdely (bool): If True, refresh specified 1/10th of second, else refresh 25.5 seconds
        Returns:
            None
        """
        # Hiding the cursor
        curses.curs_set(0)

        # Load curses colors
        self.color, self.decor = mu.load_curses_colors_decor()

        # Turn off echo
        curses.noecho()
        curses.nonl()

        # Screen delay/block for 10th of a second
        if halfdelay:
            curses.halfdelay(self.halfdelay_screen_refresh)
        else:
            curses.halfdelay(255)

    def check_terminal_size(self, scr) -> None:
        """
        Checking if current terminal size is sufficient, if it is not, display warning.

        Args:
            scr (obj): Handle for curses terminal screen handle
        Returns:
            None
        """
        # Getting the screen height and width
        term_height, term_width = scr.getmaxyx()

        # Check Height and width
        self.terminal_size_good = term_height >= self.height_limit and term_width >= self.width_limit

        # Debug Terminal Size
        if logger.level == logging.DEBUG:
            scr.addstr(1, 1, f"[Terminal Size: W:{term_width}, H:{term_height}]", self.color['grey-light'])

        k = 0
        ui_keys = mu.load_keys()
        while not self.terminal_size_good:
            if k in ui_keys['QUIT']:
                self.all_threads_enabled = False
                sys.exit(0)

            # Re-evaluate the screen size
            term_height, term_width = scr.getmaxyx()
            self.terminal_size_good = term_height >= self.height_limit and term_width >= self.width_limit

            message_lines = [
                '', 'Uh-Oh! Window too small!', '', '乁( ◔ ౪◔)「    (ಥ⌣ಥ)', '',
                f'Current: W:{term_width} x H:{term_height}', f'Needed : W:{self.width_limit} x H:{self.height_limit}',
                '', 'To continue, resize window', ''
                'To quit, press "Q" or "ESC"'
            ]
            try:
                for y_2, line in enumerate(message_lines):
                    scr.addstr(1 + y_2, mu.get_center_x(scr, line), line, self.decor['bold'])
            except Exception:
                logger.debug(
                    f'Failed to render window. Window size way too small. Needed : W:{self.width_limit} x H:{self.height_limit}'
                )
                self.all_threads_enabled = False
                sys.exit(1)

            scr.refresh()
            k = scr.getch()

    def status_to_color(self, status_text: str) -> str:
        """
        Given a status text, get the color for the status

        Args:
            scr (obj): Handle for curses terminal screen handle
        Returns:
            None
        """
        for status_item in Status:
            if status_text.strip().upper() in status_item.value:
                return Color.ITEMS.value[status_item.name]
        return Color.ITEMS.value['UNKNOWN']

    def status_to_sound(self, status_text: str) -> str:
        """
        Given a status sound, get the sound for the status

        Args:
            scr (obj): Handle for curses terminal screen handle

        Returns:
            None
        """
        for status_item in Status:
            if status_text.strip().upper() in status_item.value:
                return Sound.ITEMS.value[status_item.name]
        return Sound.ITEMS.value['UNKNOWN']

    ###########################################################################
    #                         PLAY SOUND EFFECT
    ###########################################################################

    def __thread_play_sound(self, sound_filepath: str) -> None:
        """TODO Docstring

        Args:
            TODO

        Returns:
            TODO
        """
        logger.debug(f'Thread starting - Play sound - (ID: {threading.get_ident()} - Sound: {sound_filepath}s) ...')

        # Load the file and play it
        if platform.system() != "Windows":
            try:
                wave_obj = simpleaudio.WaveObject.from_wave_file(sound_filepath)
                play_obj = wave_obj.play()
            except Exception as error:
                logger.error(f'Failed to play sound. Exception: {error}')
            self.playing_sound = True
            while self.all_threads_enabled:
                if play_obj.is_playing():
                    sleep(0.100)
                    if not self.all_threads_enabled:
                        break
                else:
                    break
        else:
            try:
                winsound.PlaySound(sound_filepath, winsound.SND_FILENAME | winsound.SND_NODEFAULT)
                self.playing_sound = True
            except RuntimeError as error:
                logger.error(f'Failed to play sound. Exception: {error}')
        self.playing_sound = False
        logger.debug(f'Thread stopped - Play sound - (ID: {threading.get_ident()})')

    def play_sound_thread_on(self, sound_filepath: str) -> bool:
        """TODO Docstring

        Args:
            TODO

        Returns:
            TODO
        """
        logger.debug(f'Playing sound file "{sound_filepath}" ...')
        try:
            threading.Thread(target=self.__thread_play_sound, args=(sound_filepath, ), daemon=True).start()
        except Exception as error:
            logger.error(
                f'Failed to start play sound thread for "{sound_filepath}". Exception: {error}. Type: {type(error)}')

        return True

    ###########################################################################
    #                         SERVER STATUS
    ###########################################################################

    def __thread_server_status(self, monitor_interval: float) -> None:
        """TODO Docstring

        Args:
            TODO

        Returns:
            TODO
        """
        logger.debug(
            f'Thread starting - Server Status - (ID: {threading.get_ident()} - Refresh Interval: {monitor_interval}s) ...'
        )

        # Set the monitoring thread flag up
        self.all_threads_enabled = True
        self.server_status_thread_interval = monitor_interval

        # Loop until flags disable it
        while self.all_threads_enabled:
            if not self.paused:
                # Get the build information
                self.server_interaction = True
                self.server_status_data['reachable'] = self.rest.is_reachable()
                self.server_status_data['auth'] = self.auth.verify()

            # Wait some time before checking again
            start_time = time()
            while time() - start_time <= monitor_interval:
                sleep(0.1)
                if not self.all_threads_enabled:
                    break

        logger.debug(f'Thread stopped - Server Status - (ID: {threading.get_ident()})')

    def server_status_thread_on(self, monitor_interval: float = 10.0) -> bool:
        """TODO Docstring

        Args:
            TODO

        Returns:
            TODO
        """
        logger.debug(f'Starting thread for server status ...')
        try:
            threading.Thread(target=self.__thread_server_status, args=(monitor_interval, ), daemon=False).start()
        except Exception as error:
            logger.error(f'Failed to start server status monitoring thread. Exception: {error}. Type: {type(error)}')

        return True

    ###########################################################################
    #                         ALL THREAD CONTROL
    ###########################################################################

    def all_threads_off(self) -> bool:
        """TODO Docstring

        Args:
            TODO

        Returns:
            TODO
        """
        # logger.debug(f'Stopping all monitor threads ...')

        # Set the monitoring thread flag down
        self.all_threads_enabled = False

        return True

    def all_threads_pause(self) -> bool:
        """TODO Docstring

        Args:
            TODO

        Returns:
            TODO
        """
        logger.debug('Pausing all monitor threads ...')

        # Set the monitoring thread flag down
        self.paused = True

        return True
