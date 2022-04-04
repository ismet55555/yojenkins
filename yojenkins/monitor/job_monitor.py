"""Job monitor"""

import curses
import logging
import sys
import threading
from datetime import datetime
from time import perf_counter, sleep, time

from yojenkins.monitor.monitor import Monitor
from yojenkins.yo_jenkins.status import BuildStatus

from . import monitor_utility as mu

# Getting the logger reference
logger = logging.getLogger()


class JobMonitor(Monitor):
    """This class defines the JobMonitor class and its function.

    The JobMonitor class enables active job monitoring
    """

    def __init__(self, rest, auth, Job, Build) -> None:
        """Object constructor method, called at object creation

        Args:
            Build: Build object

        Returns:
            None
        """
        # Get attributes from super (parent) class
        super().__init__()

        self.rest = rest
        self.auth = auth
        self.job = Job
        self.build = Build

        # Job Info Thread
        self.job_info_data = {}
        self.job_info_thread_interval = 0.0
        self._job_info_thread_lock = threading.Lock()

        # Builds Thread
        self.builds_data = []
        self.builds_data_number_of_builds = 10
        self.builds_data_thread_interval = 0.0
        self._build_data_thread_lock = threading.Lock()

        # Building a job flag
        self.job_build = 0

        # Temporary message box on screen
        self.message_box_temp_duration = 1  # sec

    ###########################################################################
    #                         BUILD MONITOR
    ###########################################################################

    def __monitor_draw(self, scr, job_url: str, sound: bool = False) -> bool:
        """
        Draw a the BUILD MONITOR UI on the screen

        Args:
            scr       : Handle for curses terminal screen handle
            job_url : Direct URL to build
            sound     : Enable sound effects
        Returns:
            True if no error, else False
        """
        # Starting data collection threads
        self.server_status_thread_on()
        self.__job_info_thread_on(job_url=job_url)
        self.__builds_data_thread_on()

        # Setting up basic stuff for curses and load keys
        self.basic_screen_setup(halfdelay=True)
        ui_keys = mu.load_keys()

        # User key input (ASCII value)
        keystroke = 0

        # Debug
        loop_total_time = 0

        # Main Loop
        while True:
            start_time = perf_counter()

            # Clearing the screen at each loop iteration before constructing the frame
            scr.clear()

            ########################################################################################

            # Check user keyboard input
            if keystroke in ui_keys['QUIT']:
                self.quit += 1
            elif keystroke in ui_keys['BUILD']:
                self.job_build += 1
            elif keystroke in ui_keys['RESUME']:
                self.quit = 0
                self.job_build = 0
            elif keystroke in ui_keys['PAUSE']:
                self.paused = not self.paused
            elif keystroke in ui_keys['HELP']:
                self.help = not self.help
            elif keystroke in ui_keys['OPEN']:
                if job_url:
                    self.job.browser_open(job_url=job_url)

            ########################################################################################

            # Check terminal size
            term_height, term_width = scr.getmaxyx()
            self.check_terminal_size(scr)

            # Paint background
            mu.paint_background(scr, self.color['normal'])

            ########################################################################################

            # TOP HEADER
            y_row = 1

            if logger.level < 20:
                pass
            else:
                mu.draw_text(scr,
                             'JOB MONITOR',
                             y_row,
                             center_x=True,
                             color=self.color['grey-light'],
                             decor=self.decor['bold'])

            y_row += 1

            # Draw header divider
            mu.draw_horizontal_seperator(scr, y_row, self.color['grey-dark'])
            y_row += 2

            ########################################################################################

            # INFO SECTION
            x_col = [3, 16]
            if self.job_info_data:
                # Get the job_url
                job_url = self.job_info_data['url']

                # INFO
                mu.draw_horizontal_header(scr, y_row, x_col[0], term_width - 5, '-', 'INFO',
                                          self.color['normal'] | self.decor['bold'])
                y_row += 1

                job_info_items = {
                    'Job': self.job_info_data['displayName'],
                    'Folder': self.job_info_data['folderFullName'],
                    'Server': self.job_info_data['serverURL'],
                }
                for i, (key, value) in enumerate(job_info_items.items()):
                    mu.draw_text(scr, f'{key}:', y_row, x_col[0], decor=self.decor['bold'])
                    mu.draw_text(scr, mu.truncate_text(f'{value}', term_width - 5 - 12), y_row, x_col[1])
                    y_row += 1
                y_row += 1
            else:
                y_row += 3
                mu.draw_text(scr,
                             'NO DATA',
                             y_row,
                             center_x=True,
                             color=self.color['normal'],
                             decor=self.decor['bold'])
                y_row += 2
                mu.draw_text(scr,
                             'ಠ_ಠ  ¯\_(⊙︿⊙)_/¯',
                             y_row,
                             center_x=True,
                             color=self.color['normal'],
                             decor=self.decor['bold'])
            y_row += 1

            ########################################################################################

            # BUILDS SECTION
            if self.job_info_data and self.builds_data:
                x_col = [3, 12, 32, 52]

                # Header
                mu.draw_horizontal_header(scr, y_row, x_col[0], term_width - 5, '-', 'BUILDS',
                                          self.color['normal'] | self.decor['bold'])
                y_row += 1

                # Loop through all listed builds
                for i, build in enumerate(self.builds_data):
                    if not build: break

                    # Build name
                    line = build["displayName"] if "displayName" in build else build["number"]
                    mu.draw_text(scr, f'{build["displayName"]}', y_row, x_col[0])

                    # Datetime
                    line = datetime.fromtimestamp(build['timestamp'] / 1000.0).strftime("%m/%d - %H:%M")
                    mu.draw_text(scr, line, y_row, x_col[1])

                    # Build Run duration
                    if build['durationFormatted'] != None:
                        line = build['durationFormatted']
                    else:
                        line = build['elapsedFormatted']
                    mu.draw_text(scr, line, y_row, x_col[2])

                    # Build Status
                    if 'resultText' in build and build['resultText'] != None:
                        line = build['resultText']
                    else:
                        line = BuildStatus.UNKNOWN.value
                    status_color = self.status_to_color(line)
                    mu.draw_text(scr, line, y_row, x_col[3], color=self.color[status_color])

                    # Return down
                    y_row += 1
            else:
                # Change the minimum window height limit (no stages section)
                self.height_limit = 17

            # Divider
            y_row = term_height - 4
            mu.draw_horizontal_seperator(scr, y_row, self.color['grey-dark'])

            ########################################################################################

            # SERVER STATUS
            y_row = term_height - 3
            if self.server_status_data:
                auth_status = False if 'auth' not in self.server_status_data else self.server_status_data["auth"]
                reach_status = False if 'reachable' not in self.server_status_data else self.server_status_data[
                    "reachable"]
                line = f'Server Status: Reachable: {reach_status}, Authenticated: {auth_status}'
            else:
                line = 'Server Status: NO DATA'
            mu.draw_text(scr, line, y_row, center_x=True, color=self.color['grey-dark'])

            ########################################################################################

            # User key input instructions
            y_row = term_height - 2
            mu.draw_text(scr, 'Press "H" for keyboard shortcuts', y_row, center_x=True, color=self.color['grey-dark'])

            ########################################################################################

            # Drawing the screen border
            border_color = 'grey-dark'
            mu.draw_screen_border(scr, self.color[border_color])

            ########################################################################################

            # Indicate server interaction
            if self.server_interaction:
                mu.draw_text(scr,
                             '(R)',
                             term_height - 2,
                             term_width - 5,
                             color=self.color['grey-dark'],
                             decor=self.decor['bold'])
            self.server_interaction = False

            ########################################################################################

            # Refresh the screen (scr.nourefresh + scr.doupdate)
            scr.refresh()

            ########################################################################################

            halfdelay_normal = False

            # Help message box
            if self.help:
                curses.halfdelay(255)
                message_lines = [
                    'B - Build the job', 'O - Open job in web browser', 'P - Pause Monitor', 'Q - Quit Monitor', ' ',
                    'H - Keyboard shortcuts'
                ]
                mu.draw_message_box(scr, message_lines, 'left')
            else:
                halfdelay_normal = True

            # Pause message box
            if self.paused:
                self.help = False
                curses.halfdelay(255)
                message_lines = ['Monitor paused', 'Requests stopped', 'To resume press "P"']
                mu.draw_message_box(scr, message_lines)
            else:
                halfdelay_normal = True

            # Build the monitored job
            if self.job_build:
                self.help = False
                curses.halfdelay(255)
                message_lines = [
                    'Are you sure you want to build this job?', 'To build press "B"', 'To return press "R"'
                ]
                mu.draw_message_box(scr, message_lines)
                if self.job_build > 1:  # Abort Message confirmed (pressed twice)
                    if job_url:
                        self.server_interaction = True
                        self.job.build_trigger(job_url=job_url)
                    else:
                        pass
                    self.job_build = 0
            else:
                halfdelay_normal = True

            # Quit message box
            if self.quit:
                self.help = False
                curses.halfdelay(255)
                message_lines = ['Are you sure you want to quit?', 'To quit press "Q"', 'To return press "R"']
                mu.draw_message_box(scr, message_lines)
                # Quit Message confirmed (pressed twice)
                if self.quit > 1:
                    self.all_threads_enabled = False
                    return True
            else:
                halfdelay_normal = True

            # Screen refresh/updating to normal
            if halfdelay_normal:
                curses.halfdelay(self.halfdelay_screen_refresh)

            # Straight exist program
            if self.exit:
                self.all_threads_enabled = False
                sys.exit(0)

            ########################################################################################

            loop_total_time = perf_counter() - start_time

            # Get User input
            keystroke = scr.getch()

    def monitor_start(self, job_url: str, sound: bool = False) -> bool:
        """
        Curses wrapper function for drawing main menu on screen

        Args:
            build_url: Server URL of the build
            sound: If True, monitor is started with sound option on

        Returns:
            True, if successful, else False
        """
        # Disable any console output logging
        mu.logging_console(enabled=False)

        return curses.wrapper(self.__monitor_draw, job_url, sound)

    ###########################################################################
    #                      DATA COLLECTION THREADS
    ###########################################################################

    #############################  JOB INFO  ##################################

    def __thread_job_info(self, job_url: str, monitor_interval: float) -> None:
        """
        Independent thread which polls job information

        Args:
            job_url: Server URL of the job
            monitor_interval: Seconds between polling job URL

        Returns:
            None
        """
        logger.debug(
            f'Thread starting - Job info - (ID: {threading.get_ident()} - Refresh Interval: {monitor_interval}s) ...')

        # Set the monitoring thread flag up
        self.all_threads_enabled = True
        self.job_info_thread_interval = monitor_interval

        # Loop until flags disable it
        while self.all_threads_enabled:
            if not self.paused:
                self.server_interaction = True
                with self._job_info_thread_lock:
                    self.job_info_data = self.job.info(job_url=job_url)

            # Wait some time before checking again
            start_time = time()
            while time() - start_time <= monitor_interval:
                sleep(0.100)
                if not self.all_threads_enabled:
                    break

        logger.debug(f'Thread stopped - Job info - (ID: {threading.get_ident()})')

    def __job_info_thread_on(self, job_url: str = '', monitor_interval: float = 5.0) -> bool:
        """
        Trigger to start independent thread that polls job information

        Args:
            job_url: Server URL of the job
            monitor_interval: Seconds between polling build URL

        Returns:
            True if successful, else False
        """
        logger.debug(f'Starting thread for job info for "{job_url}" ...')
        try:
            threading.Thread(target=self.__thread_job_info, args=(
                job_url,
                monitor_interval,
            ), daemon=False).start()
        except Exception as error:
            logger.error(
                f'Failed to start job info monitoring thread for {job_url}. Exception: {error}. Type: {type(error)}')

        return True

    ############################  BUILDS INFO  ################################

    def __thread_build_info(self, build_url: str, build_data_index: int) -> None:
        """
        Independent thread which fetches build information

        Args:
            build_url: Server URL of the build
            build_data_index: Build index within the job info return

        Returns:
            None
        """
        logger.debug(f'Thread starting - Build info (INDEX: {build_data_index}, ID: {threading.get_ident()}) ...')
        self.server_interaction = True
        self.builds_data[build_data_index] = self.build.info(build_url=build_url)
        logger.debug(f'Thread stopped - Build info (INDEX: {build_data_index}, ID: {threading.get_ident()})')

    def __thread_builds_data(self, monitor_interval: float) -> None:
        """
        Independent thread which polls the build data for each build listed in job

        Args:
            monitor_interval: Seconds between polling build URL

        Returns:
            None
        """
        logger.debug(
            f'Thread starting - Builds data - (ID: {threading.get_ident()} - Refresh Interval: {monitor_interval}s) ...'
        )

        # Set the monitoring thread flag up
        self.all_threads_enabled = True
        self.builds_data_thread_interval = monitor_interval

        # Pre-allocate
        self.builds_data = [None] * self.builds_data_number_of_builds

        # Wait for initial batch of job info data
        while not self.job_info_data:
            if not self.all_threads_enabled:
                break
            sleep(0.100)

        # Loop until flags disable it
        while self.all_threads_enabled:
            if not self.paused:
                if 'builds' in self.job_info_data:
                    # Get and store the data in each thread
                    threads = []
                    try:
                        for build_data_index, build in enumerate(
                                self.job_info_data['builds'][:self.builds_data_number_of_builds]):
                            # build_data_index += 1
                            thread = threading.Thread(target=self.__thread_build_info,
                                                      args=(
                                                          build['url'],
                                                          build_data_index,
                                                      ),
                                                      daemon=False)
                            thread.start()
                            threads.append(thread)
                    except Exception as error:
                        logger.debug(f'Failure occurred when starting build data threads. Exception: {error}')

                    try:
                        for thread in threads:
                            thread.join()
                    except Exception as error:
                        logger.debug(f'Failure occurred when ending build data threads. Exception: {error}')
                else:
                    logger.debug('No job info data. Waiting ...')

            # Wait some time before checking again
            start_time = time()
            while time() - start_time <= monitor_interval:
                sleep(0.100)
                if not self.all_threads_enabled:
                    break

        logger.debug(f'Thread stopped - Builds data - (ID: {threading.get_ident()})')

    def __builds_data_thread_on(self, monitor_interval: float = 7.0) -> bool:
        """
        Trigger to start independent thread that polls build information within job

        Args:
            monitor_interval: Seconds between polling build data

        Returns:
            True if successful, else False
        """
        logger.debug('Starting thread for job builds info ...')
        try:
            threading.Thread(target=self.__thread_builds_data, args=(monitor_interval, ), daemon=False).start()
        except Exception as error:
            logger.error(f'Failed to start job builds info monitoring thread. Exception: {error}. Type: {type(error)}')

        return True
