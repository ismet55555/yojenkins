#!/usr/bin/env python3

import curses
import logging
import sys
import textwrap
import threading
from pprint import pprint
from time import sleep, time
from typing import Dict, List, Tuple, Type

from YoJenkins import YoJenkins
from YoJenkins.Status import Status, BuildStatus, StageStatus, Color

from . import curses_utility as cu

# Getting the logger reference
logger = logging.getLogger()

class Monitor:
    """This class defines the Monitor class and its function.
    
    The Monitor class enables active Jenkins monitoring
    """
    def __init__(self, YJ:object) -> None:
        """Object constructor method, called at object creation

        Args:
            YJ: YoJenkins object used for monitoring calls

        Returns:
            None
        """
        # Store passed object
        self.YJ:object = YJ

        self.color = {}
        self.decor = {}

        self.halfdelay_screen_refresh:int = 5  # number of 10th of a second

        self.height_limit:int = 35
        self.width_limit:int = 66
        self.terminal_size_good:bool = True

        self.curses_alive:bool = True

        self.monitor_quit:int = 0
        self.monitor_exit:bool = False

        # Build Info Thread
        self.build_info_data:dict = {}
        self.build_info_thread_interval:float = 0.0

        # Build Stages Thread
        self.build_stages_data:dict = {}
        self.build_stages_thread_interval:float = 0.0

        # Server Status
        self.server_status_data:dict = {}
        self.server_status_thread_interval:float = 0.0

        # All threads
        self.all_threads_enabled:bool = True
        self.monitor_paused:bool = False

        self.monitor_help = False


    def __del__(self):
        """ TODO """
        # Just in case turn off all threads
        self.all_threads_off()




    ###########################################################################
    #                         CURSES UTILITY
    ###########################################################################

    def __basic_screen_setup(self, halfdelay:bool) -> None:
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
        self.color, self.decor = cu.load_curses_colors_decor()

        # Turn off echo
        curses.noecho()

        curses.nonl()

        # Screen delay/block for 10th of a second
        if halfdelay:
            curses.halfdelay(self.halfdelay_screen_refresh)
        else:
            curses.halfdelay(255)


    def __check_terminal_size(self, scr) -> None:
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
        KEYS = cu.load_keys()
        while not self.terminal_size_good:
            if k in KEYS['QUIT']:
                self.all_threads_enabled = False
                sys.exit(0)

            # Re-evaluate the screen size
            term_height, term_width = scr.getmaxyx()
            self.terminal_size_good = term_height >= self.height_limit and term_width >= self.width_limit

            message_lines = [
                '',
                'Uh-Oh! Window too small!',
                '',
                '乁( ◔ ౪◔)「    (ಥ⌣ಥ)',
                '',
                f'Current: W:{term_width} x H:{term_height}',
                f'Needed : W:{self.width_limit} x H:{self.height_limit}',
                '',
                'To continue, resize window',
                ''
                'To quit, press "Q" or "ESC"'
                ]
            try:
                for y_2, line in enumerate(message_lines):
                    scr.addstr(1 + y_2, cu.get_center_x(scr, line), line, self.decor['bold'])
            except Exception as e:
                logger.debug(f'Failed to render window. Window size way too small. Needed : W:{self.width_limit} x H:{self.height_limit}')
                self.all_threads_enabled = False
                sys.exit(1)

            scr.refresh()
            k = scr.getch()


    def __status_to_color(self, status_text:str) -> int:
        """
        Given a status text

        Args:
            scr (obj): Handle for curses terminal screen handle
        Returns: 
            None
        """
        for status_item in Status:
            if status_text.strip().upper() in status_item.value:
                return Color.items.value[status_item.name]


    ###########################################################################
    #                         BUILD MONITOR
    ###########################################################################

    def __build_monitor_draw(self, scr, build_url:str) -> bool:
        """
        Draw a the BUILD MONITOR UI on the screen

        Args:
            scr       : Handle for curses terminal screen handle
            build_url : Direct URL to build
        Returns: 
            True if no error, else False
        """

        # Starging data collection threads
        self.__build_info_thread_on(build_url=build_url)
        self.__build_stages_thread_on(build_url=build_url)
        self.__server_status_thread_on()

        # Setting up basic stuff for curses and load keys
        self.__basic_screen_setup(halfdelay=True)
        KEYS = cu.load_keys()

        # User key input (ASCII)
        k = 0

        elapsed_time = 1

        # scr.idcok(False)
        # scr.idlok(False)
        # scr.nodelay(True)
        # scr.timeout(0)
        # scr.immedok(False)
        # scr.leaveok(True)


        # Main Loop
        while True:
            start_time = time()

            # Clearing the screen at each loop iteration before constructing the frame
            scr.clear()
            # scr.erase()

            ########################################################################################

            # Check user keyboard input
            if k in KEYS['QUIT']:
                self.monitor_quit += 1
            elif k in KEYS['RESUME']:
                self.monitor_quit = 0
            elif k in KEYS['PAUSE']:
                self.monitor_paused = not self.monitor_paused
            elif k in KEYS['HELP']:
                self.monitor_help = not self.monitor_help
            elif k in KEYS['OPEN']:
                if build_url:
                    self.YJ.build_browser_open(build_url=build_url)


            ########################################################################################

            # Check terminal size
            term_height, term_width = scr.getmaxyx()
            self.__check_terminal_size(scr)

            # Paint background
            cu.paint_background(scr, self.color['normal'])

            ########################################################################################

            # TOP HEADER
            y = 1

            cu.draw_text(scr, 'BUILD MONITOR', y, center_x=True, color=self.color['grey-light'], decor=self.decor['bold'])
            #cu.draw_text(scr, str(elapsed_time), y, center_x=True, color=self.color['grey-light'], decor=self.decor['bold'])
            # cu.draw_text(scr, str(curses.baudrate()), y, center_x=True, color=self.color['grey-light'], decor=self.decor['bold'])

            y += 1

            # Draw header divider
            cu.draw_horizontal_seperator(scr, y, self.color['grey-dark'])
            y += 2

            # INFO SECTION
            x = [3, 16]
            if self.build_info_data:
                # Get the build_url
                build_url = self.build_info_data['url']

                # INFO
                cu.draw_horizontal_header(scr, y, x[0], term_width - 5, '-', 'INFO', self.color['normal'] | self.decor['bold'])
                y += 1

                build_info_items = {
                    'Job': self.build_info_data['jobFullName'],
                    'Build': self.build_info_data['displayName'],
                    'Folder': self.build_info_data['folderFullName'],
                    'Server': self.build_info_data['serverDomain'],
                    'Executor': self.build_info_data['builtOn'],
                }
                for i, (key, value) in enumerate(build_info_items.items()):
                    # Job Name
                    cu.draw_text(scr, f'{key}:', y, x[0], decor=self.decor['bold'])
                    cu.draw_text(scr, cu.truncate_text(f'{value}', term_width - 5 - 12), y, x[1])
                    y += 1
                y += 1

                # STATUS (FIXME: Redo this mess below)
                cu.draw_horizontal_header(scr, y, x[0], term_width - 5, '-', 'STATUS', self.color['normal'] | self.decor['bold'])
                y += 1

                # Status text color
                status_color = self.__status_to_color(self.build_info_data['resultText'])

                build_info_items = {
                    'Started': [self.build_info_data['startDatetime'], self.color['normal'], self.decor['normal']],
                    'Ended': [self.build_info_data['endDatetime'], self.color['normal'], self.decor['normal']],
                    'Elapsed': [self.build_info_data['elapsedFormatted'], self.color['normal'], self.decor['normal']],
                    'Estimated': [self.build_info_data['estimatedDurationFormatted'], self.color['normal'], self.decor['normal']],
                    'Refresh': [str(self.build_info_thread_interval) + ' sec', self.color['normal'], self.decor['normal']],
                    'Status': [self.build_info_data['resultText'], self.color[status_color], self.decor['bold']]
                }
                for i, (key, value) in enumerate(build_info_items.items()):
                    cu.draw_text(scr, f'{key}:', y, x[0], decor=self.decor['bold'])
                    cu.draw_text(scr, cu.truncate_text(f'{value[0]}', term_width - 5 - 12), y, x[1], color=value[1], decor=value[2])
                    y += 1
            else:
                y += 3
                cu.draw_text(scr, 'NO DATA', y, center_x=True, color=self.color['normal'], decor=self.decor['bold'])
                y += 2
                cu.draw_text(scr, 'ಠ_ಠ  ¯\_(⊙︿⊙)_/¯', y, center_x=True, color=self.color['normal'], decor=self.decor['bold'])
            y += 1

            # FIXME: When no estimated time is available we get this:
            #    Estimated:   -1 day, 23:59:59.999
            #     Fix in YoJenkins.py

            # TODO: Add QUEUED status for build

            # STAGES SECTION
            if self.build_stages_data:
                x = [3, 8, 40, 55]

                # Header
                cu.draw_horizontal_header(scr, y, x[0], term_width - 5, '-', 'STAGE', self.color['normal'] | self.decor['bold'])
                y += 1

                # Loop through all listed stages in build
                for i, build_stage in enumerate(self.build_stages_data):
                    # Stage number
                    try:
                        cu.draw_text(scr, f'{i + 1}.', y, x[0])
                    except:
                        break

                    # Stage name
                    line = cu.truncate_text(build_stage['name'] if 'name' in build_stage else '-', 29)
                    cu.draw_text(scr, line, y, x[1])

                    # Stage Run duration
                    line = build_stage['durationFormatted'] if 'durationFormatted' in build_stage else '-'
                    cu.draw_text(scr, line, y, x[2])

                    # Status text and color
                    result_text = build_stage['status'] if 'status' in build_stage else StageStatus.unknown.value
                    status_color = self.__status_to_color(build_stage['status'])

                    cu.draw_text(scr, result_text, y, x[3], color=self.color[status_color])
                    y += 1
            else:
                # Change the minimum window height limit (no stages section)
                self.height_limit = 17

            # Divider
            y = term_height - 4
            cu.draw_horizontal_seperator(scr, y, self.color['grey-dark'])

            # SERVER STATUS
            y = term_height - 3
            if self.server_status_data:
                auth_status = False if 'auth' not in self.server_status_data else self.server_status_data["auth"]
                reach_status = False if 'reachable' not in self.server_status_data else self.server_status_data["reachable"]
                line = f'Server Status: Reachable: {reach_status}, Authenticated: {auth_status}'
            else:
                line = f'Server Status: NO DATA'
            cu.draw_text(scr, line, y, center_x=True, color=self.color['grey-dark'])

            ########################################################################################

            # User key input instructions
            y = term_height - 2
            cu.draw_text(scr, 'Press "H" for shortcut keymap help', y, center_x=True, color=self.color['grey-dark'])

            ########################################################################################

            # Drawing the screen border
            border_color = 'grey-dark'
            if 'resultText' in self.build_info_data:
                if self.build_info_data['resultText'] in Status.success.value:
                    border_color = 'green'
                elif self.build_info_data['resultText'] in Status.failure.value:
                    border_color = 'red'
                elif self.build_info_data['resultText'] in Status.aborted.value:
                    border_color = 'magenta'
            cu.draw_screen_border(scr, self.color[border_color])

            ########################################################################################

            # Refresh the screen
            scr.refresh()
            # scr.nourefresh()
            # curses.doupdate()

            ########################################################################################

            # Help message box
            if self.monitor_help:
                curses.halfdelay(255)
                message_lines = [
                    'H - Help',
                    'P - Pause (stop requests)',
                    'Q - Quit',
                    'O - Open in web browser'
                    ]
                cu.draw_message_box(scr, message_lines, 'left')
            else:
                curses.halfdelay(self.halfdelay_screen_refresh)


            # Monitor pause message box
            if self.monitor_paused:
                self.monitor_help = False

                curses.halfdelay(255)
                message_lines = [
                    'Monitor paused',
                    'Requests stopped',
                    'To resume press "P"'
                    ]
                cu.draw_message_box(scr, message_lines)
            else:
                curses.halfdelay(self.halfdelay_screen_refresh)


            # Monitor quit message box
            if self.monitor_quit:
                self.monitor_help = False

                curses.halfdelay(255)
                message_lines = ['Are you sure you want to quit?', 'To quit press "Q"', 'To return press "R"']
                cu.draw_message_box(scr, message_lines)
                # Quit Message confirmed (pressed twice)
                if self.monitor_quit > 1:
                    self.all_threads_enabled = False
                    return True
            else:
                curses.halfdelay(self.halfdelay_screen_refresh)

            # Straight exist program
            if self.monitor_exit:
                self.all_threads_enabled = False
                sys.exit(0)

            ########################################################################################

            elapsed_time = time() - start_time
            
            # Get User input
            k = scr.getch()

            curses.napms(10)
            curses.flushinp()


    def build_monitor_start(self, build_url:str, view_option:int=1) -> bool:
        """
        Curses wrapper function for drawing main menu on screen

        Args:
            view_option: TODO
        Returns: 
            menu option (str)  : Selection menu option user selected (ie. quit)
            successfull (bool) : True if no error, else False
        """
        return curses.wrapper(self.__build_monitor_draw, build_url)





    ###########################################################################
    #                      DATA COLLECTION THREADS
    ###########################################################################

    ###########################  BUILD INFO  ##################################

    def __thread_build_info(self, build_url:str, monitor_interval:float) -> None:
        """ TODO """
        logger.debug(f'Thread - Build info - (ID: {threading.get_ident()}) starting (Refresh Interval: {monitor_interval}s) ...')
        
        # Set the monitoring thread flag up
        self.all_threads_enabled = True
        self.build_info_thread_interval = monitor_interval

        # Loop until flags disable it
        while self.all_threads_enabled:
            if not self.monitor_paused:
                # Get the build information
                self.build_info_data = self.YJ.build_info(build_url=build_url)

            # Wait some time before checking again
            start_time = time()
            while time() - start_time <= monitor_interval:
                sleep(0.100)
                if not self.all_threads_enabled:
                    break

        logger.debug(f'Thread - Build info - (ID: {threading.get_ident()}) ended')


    def __build_info_thread_on(self, build_url:str='', monitor_interval:float=8.0) -> bool:
        """ TODO """
        logger.debug(f'Starting thread for build info for "{build_url}" ...')
        try:
            threading.Thread(target=self.__thread_build_info, args=(build_url, monitor_interval,), daemon=False).start()
        except Exception as e:
            # TODO: Specify error
            logger.error(f'Failed to start build info monitoring thread for {build_url}. Exception: {e}. Type: {type(e)}')

        return True



    ###########################  BUILD STAGES  ################################

    def __thread_build_stages(self, build_url:str, monitor_interval:float) -> None:
        """ TODO """
        logger.debug(f'Thread - Build Stages - (ID: {threading.get_ident()}) starting (Refresh Interval: {monitor_interval}s) ...')
        
        # Set the monitoring thread flag up
        self.all_threads_enabled = True
        self.build_stages_thread_interval = monitor_interval

        # Loop until flags disable it
        while self.all_threads_enabled:
            if not self.monitor_paused:
                # Get the build information
                self.build_stages_data = self.YJ.build_stage_list(build_url=build_url)[0]

            # Wait some time before checking again
            start_time = time()
            while time() - start_time <= monitor_interval:
                sleep(0.1)
                if not self.all_threads_enabled:
                    break

        logger.debug(f'Thread - Build Stages - (ID: {threading.get_ident()}) ended')


    def __build_stages_thread_on(self, build_url:str='', monitor_interval:float=10.0) -> bool:
        '''TODO'''
        logger.debug(f'Starting thread for build stages for "{build_url}" ...')
        try:
            threading.Thread(target=self.__thread_build_stages, args=(build_url, monitor_interval,), daemon=False).start()
        except Exception as e:
            # TODO: Specify error
            logger.error(f'Failed to start build info monitoring thread for {build_url}. Exception: {e}. Type: {type(e)}')

        return True



    ###########################  SERVER STATUS  ################################

    def __thread_server_status(self, monitor_interval:float) -> None:
        """ TODO """
        logger.debug(f'Thread - Build Stages - (ID: {threading.get_ident()}) starting (Refresh Interval: {monitor_interval}s) ...')
        
        # Set the monitoring thread flag up
        self.all_threads_enabled = True
        self.server_status_thread_interval = monitor_interval

        # Loop until flags disable it
        while self.all_threads_enabled:
            if not self.monitor_paused:
                # Get the build information
                self.server_status_data['reachable'] = self.YJ.server_is_reachable()
                self.server_status_data['auth'] = self.YJ.auth_verify_auth()

            # Wait some time before checking again
            start_time = time()
            while time() - start_time <= monitor_interval:
                sleep(0.1)
                if not self.all_threads_enabled:
                    break

        logger.debug(f'Thread - Build Stages - (ID: {threading.get_ident()}) ended')


    def __server_status_thread_on(self, monitor_interval:float=5.0) -> bool:
        '''TODO'''
        logger.debug(f'Starting thread for server status ...')
        try:
            threading.Thread(target=self.__thread_server_status, args=(monitor_interval,), daemon=False).start()
        except Exception as e:
            # TODO: Specify error
            logger.error(f'Failed to start server status monitoring thread. Exception: {e}. Type: {type(e)}')

        return True



    ###############################  ALL  #####################################

    def all_threads_off(self) -> bool:
        """ TODO """
        logger.debug(f'Stopping all monitor threads ...')

        # Set the monitoring thread flag down
        self.all_threads_enabled = False

        return True


    def all_threads_pause(self) -> bool:
        """ TODO """
        logger.debug(f'Pausing all monitor threads ...')

        # Set the monitoring thread flag down
        self.monitor_paused = True

        return True
