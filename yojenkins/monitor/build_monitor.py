"""Build monitor"""

import curses
import logging
import sys
import threading
from pathlib import Path

#  from pprint import pprint
from time import perf_counter, sleep, time

from yojenkins.monitor.monitor import Monitor
from yojenkins.utility.utility import get_resource_path
from yojenkins.yo_jenkins.status import Color, Sound, StageStatus, Status

from . import monitor_utility as mu

# Getting the logger reference
logger = logging.getLogger()


class BuildMonitor(Monitor):
    """This class defines the BuildMonitor class and its function.

    The BuildMonitor class enables active build monitoring
    """

    def __init__(self, rest, auth, Build) -> None:
        """Object constructor method, called at object creation

        Args:
            Build: Build objects

        Returns:
            None
        """
        # Get attributes from super (parent) class
        super().__init__()

        self.rest = rest
        self.auth = auth
        self.build = Build

        # Build Info Thread
        self.build_info_data = {}
        self.build_info_thread_interval = 0.0
        self._build_info_thread_lock = threading.Lock()

        # Build Stages Thread
        self.build_stages_data = {}
        self.build_stages_thread_interval = 0.0
        self._build_stages_thread_lock = threading.Lock()

        # Aborting build flag
        self.build_abort = 0

        # Skip sound on first draw cycle (avoid playing sound at startup)
        self._initial_draw = True

        # Output build logs to console
        self.build_logs = False

        self.sound_directory = ''

        # Track whether PAUSED_PENDING_INPUT sound has been played for current pause
        self._stage_paused_sound_played = False

    ###########################################################################
    #                         BUILD MONITOR
    ###########################################################################

    def __monitor_draw(self, scr, build_url: str, sound: bool = False) -> bool:
        """
        Draw a the BUILD MONITOR UI on the screen

        Args:
            scr       : Handle for curses terminal screen handle
            build_url : Direct URL to build
            sound     : Enable sound effects
        Returns:
            True if no error, else False
        """
        # Starting data collection threads
        self.server_status_thread_on()
        self.__build_info_thread_on(build_url=build_url)
        self.__build_stages_thread_on(build_url=build_url)

        # Setting up basic stuff for curses and load keys
        self.basic_screen_setup(halfdelay=True)
        ui_keys = mu.load_keys()

        # Sound effect related
        sound_path = get_resource_path(str(Path('resources') / 'sound'))
        self.sound_directory = Path(sound_path) if sound_path else ''
        status_sound_last = ''

        # User key input (ASCII value)
        keystroke = 0

        # Debug stuff
        # loop_total_time = 0

        # Main Loop
        while True:
            start_time = perf_counter()

            # Clearing the screen at each loop iteration before constructing the frame
            scr.clear()

            ########################################################################################

            # Check user keyboard input
            if keystroke in ui_keys['QUIT']:
                self.quit += 1
            elif keystroke in ui_keys['ABORT']:
                self.build_abort += 1
            elif keystroke in ui_keys['RESUME']:
                self.quit = 0
                self.build_abort = 0
            elif keystroke in ui_keys['PAUSE']:
                self.paused = not self.paused
            elif keystroke in ui_keys['HELP']:
                self.help = not self.help
            elif keystroke in ui_keys['OPEN']:
                if build_url:
                    self.build.browser_open(build_url=build_url)
            elif keystroke in ui_keys['SOUND']:
                sound = not sound
                state = 'ON' if sound else 'OFF'
                self.show_temp_message([f'Sound notification {state}'])
            elif keystroke in ui_keys['LOGS']:
                self.build_logs = True

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
                # mu.draw_text(scr, f"{loop_total_time:.4f}", y_row, center_x=True, color=self.color['grey-light'], decor=self.decor['bold'])
                # mu.draw_text(scr, str(curses.baudrate()), y_row, center_x=True, color=self.color['grey-light'], decor=self.decor['bold'])
                mu.draw_text(
                    scr,
                    str(sound) + ' ' + str(self._temp_message_active),
                    y_row,
                    center_x=True,
                    color=self.color['grey-light'],
                    decor=self.decor['bold'],
                )
            else:
                mu.draw_text(
                    scr,
                    'BUILD MONITOR',
                    y_row,
                    center_x=True,
                    color=self.color['grey-light'],
                    decor=self.decor['bold'],
                )
            y_row += 1

            # Draw header divider
            mu.draw_horizontal_seperator(scr, y_row, self.color['grey-dark'])
            y_row += 2

            ########################################################################################

            # INFO SECTION
            x_col = [3, 16]
            if self.build_info_data:
                # Get the build_url
                build_url = self.build_info_data['url']

                # INFO
                mu.draw_horizontal_header(
                    scr, y_row, x_col[0], term_width - 5, '-', 'INFO', self.color['normal'] | self.decor['bold']
                )
                y_row += 1

                build_info_items = {
                    'Job': self.build_info_data['jobName'],
                    'Build': self.build_info_data['displayName'],
                    'Folder': self.build_info_data['folderFullName'],
                    'Server': self.build_info_data['serverURL'],
                    'Executor': self.build_info_data['builtOn'],
                }
                for i, (key, value) in enumerate(build_info_items.items()):
                    # Job Name
                    mu.draw_text(scr, f'{key}:', y_row, x_col[0], decor=self.decor['bold'])
                    mu.draw_text(scr, mu.truncate_text(f'{value}', term_width - 5 - 12), y_row, x_col[1])
                    y_row += 1
                y_row += 1

                mu.draw_horizontal_header(
                    scr, y_row, x_col[0], term_width - 5, '-', 'STATUS', self.color['normal'] | self.decor['bold']
                )
                y_row += 1

                # Play a sound on job status change
                if sound:
                    mu.draw_text(
                        scr, '( fx )', 1, term_width - 8, color=self.color['grey-dark'], decor=self.decor['bold']
                    )
                if sound and not self.playing_sound and not self._initial_draw:
                    # Get the sound file name
                    status_sound = self.status_to_sound(self.build_info_data['resultText'])
                    if status_sound_last != status_sound and status_sound:
                        # FIXME: Only check file names, not status text
                        self.play_sound_thread_on(str(self.sound_directory / status_sound))
                        status_sound_last = status_sound
                if self._initial_draw and self.build_info_data:
                    status_sound_last = self.status_to_sound(self.build_info_data['resultText'])
                    self._initial_draw = False

                # Status text color
                status_color = self.status_to_color(self.build_info_data['resultText'])

                build_info_items = {
                    'Started': [self.build_info_data['startDatetime'], self.color['normal'], self.decor['normal']],
                    'Ended': [self.build_info_data['endDatetime'], self.color['normal'], self.decor['normal']],
                    'Elapsed': [self.build_info_data['elapsedFormatted'], self.color['normal'], self.decor['normal']],
                    'Estimated': [
                        self.build_info_data['estimatedDurationFormatted'],
                        self.color['normal'],
                        self.decor['normal'],
                    ],
                    'Refresh': [
                        str(self.build_info_thread_interval) + ' sec',
                        self.color['normal'],
                        self.decor['normal'],
                    ],
                    'Status': [self.build_info_data['resultText'], self.color[status_color], self.decor['bold']],
                }
                for i, (key, value) in enumerate(build_info_items.items()):
                    mu.draw_text(scr, f'{key}:', y_row, x_col[0], decor=self.decor['bold'])
                    mu.draw_text(
                        scr,
                        mu.truncate_text(f'{value[0]}', term_width - 5 - 12),
                        y_row,
                        x_col[1],
                        color=value[1],
                        decor=value[2],
                    )
                    y_row += 1
            else:
                y_row += 3
                mu.draw_text(
                    scr, 'NO DATA', y_row, center_x=True, color=self.color['normal'], decor=self.decor['bold']
                )
                y_row += 2
                mu.draw_text(
                    scr,
                    r'ಠ_ಠ  ¯\_(⊙︿⊙)_/¯',
                    y_row,
                    center_x=True,
                    color=self.color['normal'],
                    decor=self.decor['bold'],
                )
            y_row += 1

            ########################################################################################

            # TODO: Add QUEUED status for build status

            # STAGES SECTION
            if self.build_stages_data:
                x_col = [3, 8, 40, 55]

                # Header
                mu.draw_horizontal_header(
                    scr, y_row, x_col[0], term_width - 5, '-', 'STAGES', self.color['normal'] | self.decor['bold']
                )
                y_row += 1

                # Loop through all listed stages in build
                for i, build_stage in enumerate(self.build_stages_data):
                    # Stage number
                    try:
                        mu.draw_text(scr, f'{i + 1}.', y_row, x_col[0])
                    except curses.error:
                        break

                    # Stage name
                    line = mu.truncate_text(build_stage['name'] if 'name' in build_stage else '-', 29)
                    mu.draw_text(scr, line, y_row, x_col[1])

                    # Stage Run duration
                    line = build_stage['durationFormatted'] if 'durationFormatted' in build_stage else '-'
                    mu.draw_text(scr, line, y_row, x_col[2])

                    # Status text and color
                    result_text = build_stage['status'] if 'status' in build_stage else StageStatus.UNKNOWN.value
                    status_color = self.status_to_color(build_stage['status'])

                    mu.draw_text(scr, result_text.replace('_', ' '), y_row, x_col[3], color=self.color[status_color])
                    y_row += 1

                # Play sound when any stage is stuck in PAUSED_PENDING_INPUT
                if sound and not self.playing_sound:
                    has_paused_stage = any(
                        stage.get('status') == StageStatus.PAUSED_INPUT.value
                        for stage in self.build_stages_data
                    )
                    if has_paused_stage and not self._stage_paused_sound_played:
                        sound_file = Sound.ITEMS.value['PAUSED_INPUT']
                        if sound_file:
                            self.play_sound_thread_on(str(self.sound_directory / sound_file))
                            self._stage_paused_sound_played = True
                    elif not has_paused_stage:
                        self._stage_paused_sound_played = False
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
                auth_status = False if 'auth' not in self.server_status_data else self.server_status_data['auth']
                reach_status = (
                    False if 'reachable' not in self.server_status_data else self.server_status_data['reachable']
                )
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
            if 'resultText' in self.build_info_data:
                if self.build_info_data['resultText'] in Status.SUCCESS.value:
                    border_color = Color.ITEMS.value['SUCCESS']
                elif self.build_info_data['resultText'] in Status.FAILURE.value:
                    border_color = Color.ITEMS.value['FAILURE']
                elif self.build_info_data['resultText'] in Status.ABORTED.value:
                    border_color = Color.ITEMS.value['ABORTED']
                elif self.build_info_data['resultText'] in Status.UNSTABLE.value:
                    border_color = Color.ITEMS.value['UNSTABLE']

            mu.draw_screen_border(scr, self.color[border_color])

            ########################################################################################

            # Indicate server interaction with icon
            if self.server_interaction:
                mu.draw_text(
                    scr,
                    '(R)',
                    term_height - 2,
                    term_width - 5,
                    color=self.color['grey-dark'],
                    decor=self.decor['bold'],
                )
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
                    'A - Abort build',
                    'L - Output build logs',
                    'O - Open build in web browser',
                    'P - Pause Monitor',
                    'Q - Quit Monitor',
                    'S - Sound notification on/off',
                    ' ',
                    'H - Keyboard shortcuts',
                ]
                mu.draw_message_box(scr, message_lines, 'left')
            else:
                halfdelay_normal = True

            # Temporary message box (e.g., sound toggle notification)
            temp_msg = self.get_temp_message()
            if temp_msg:
                mu.draw_message_box(scr, temp_msg)

            # Pause message box
            if self.paused:
                self.help = False
                curses.halfdelay(255)
                message_lines = ['Monitor paused', 'Requests stopped', 'To resume press "P"']
                mu.draw_message_box(scr, message_lines)
            else:
                halfdelay_normal = True

            # Abort message box
            if self.build_abort:
                self.help = False
                curses.halfdelay(255)
                message_lines = ['Are you sure you want to abort build?', 'To abort press "A"', 'To return press "R"']
                mu.draw_message_box(scr, message_lines)
                if self.build_abort > 1:  # Abort Message confirmed (pressed twice)
                    if build_url:
                        self.server_interaction = True
                        self.build.abort(build_url=build_url)
                    else:
                        # TODO: Show UI error message for missing build_url
                        pass
                    self.build_abort = 0
            else:
                halfdelay_normal = True

            # Show the build logs
            if self.build_logs:
                self.help = False
                self.all_threads_off()
                curses.echo(True)
                curses.nl(True)
                curses.endwin()
                if build_url:
                    self.server_interaction = True
                    self.build.logs(build_url=build_url)
                return True

            # Quit message box
            if self.quit:
                self.help = False
                curses.halfdelay(255)
                message_lines = ['Are you sure you want to quit?', 'To quit press "Q"', 'To return press "R"']
                mu.draw_message_box(scr, message_lines)
                # Quit Message confirmed (pressed twice)
                if self.quit > 1:
                    self.all_threads_off()
                    return True
            else:
                halfdelay_normal = True

            # Screen refresh/updating to normal
            if halfdelay_normal:
                curses.halfdelay(self.halfdelay_screen_refresh)

            # Straight exit program
            if self.exit:
                self.all_threads_off()
                sys.exit(0)

            ########################################################################################

            perf_counter() - start_time

            # Get User input
            keystroke = scr.getch()

    def monitor_start(self, build_url: str, sound: bool = False) -> bool:
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

        return curses.wrapper(self.__monitor_draw, build_url, sound)

    ###########################################################################
    #                      DATA COLLECTION THREADS
    ###########################################################################

    ###########################  BUILD INFO  ##################################

    def __thread_build_info(self, build_url: str, monitor_interval: float) -> None:
        """
        Independent thread which polls build information

        Args:
            build_url: Server URL of the build
            monitor_interval: Seconds between polling build URL

        Returns:
            None
        """
        logger.debug(
            f'Thread starting - Build info - (ID: {threading.get_ident()} - Refresh Interval: {monitor_interval}s) ...'
        )

        # Set the monitoring thread flag up
        self.all_threads_enabled = True
        self.build_info_thread_interval = monitor_interval

        # Loop until flags disable it
        while self.all_threads_enabled:
            if not self.paused:
                self.server_interaction = True
                try:
                    with self._build_info_thread_lock:
                        self.build_info_data = self.build.info(build_url=build_url)
                except RuntimeError:
                    break

            # Wait some time before checking again
            start_time = time()
            while time() - start_time <= monitor_interval:
                sleep(0.100)
                if not self.all_threads_enabled:
                    break

        logger.debug(f'Thread stopped - Build info - (ID: {threading.get_ident()})')

    def __build_info_thread_on(self, build_url: str = '', monitor_interval: float = 7.0) -> bool:
        """
        Trigger to start independent thread that polls build information

        Args:
            build_url: Server URL of the build
            monitor_interval: Seconds between polling build URL

        Returns:
            True if successful, else False
        """
        logger.debug(f'Starting thread for build info for "{build_url}" ...')
        try:
            t = threading.Thread(
                target=self.__thread_build_info,
                args=(
                    build_url,
                    monitor_interval,
                ),
                daemon=True,
            )
            t.start()
            self._threads.append(t)
        except Exception as error:
            logger.error(
                f'Failed to start build info monitoring thread for {build_url}. Exception: {error}. Type: {type(error)}'
            )

        return True

    ###########################  BUILD STAGES  ################################

    def __thread_build_stages(self, build_url: str, monitor_interval: float) -> None:
        """
        Independent thread that polls build stages

        Args:
            build_url: Server URL of the build
            monitor_interval: Seconds between polling build URL

        Returns:
            None
        """
        logger.debug(
            f'Thread starting - Build Stages - (ID: {threading.get_ident()} - Refresh Interval: {monitor_interval}s) ...'
        )

        # Set the monitoring thread flag up
        self.all_threads_enabled = True
        self.build_stages_thread_interval = monitor_interval

        # Check if this is a staged build
        logger.debug('Checking if build is a staged build ...')
        request_url = f'{build_url.strip("/")}/wfapi/describe'
        return_content, _, return_success = self.rest.request(request_url, 'get', is_endpoint=False)
        if not return_success or not return_content:
            logger.debug('Failed to get build stages. This may not be a staged build')
            return

        # Loop until flags disable it
        while self.all_threads_enabled:
            if not self.paused:
                self.server_interaction = True
                try:
                    with self._build_stages_thread_lock:
                        self.build_stages_data = self.build.stage_list(build_url=build_url)[0]
                except RuntimeError:
                    break

            # Wait some time before checking again
            start_time = time()
            while time() - start_time <= monitor_interval:
                sleep(0.1)
                if not self.all_threads_enabled:
                    break

        logger.debug(f'Thread stopped - Build Stages - (ID: {threading.get_ident()})')

    def __build_stages_thread_on(self, build_url: str = '', monitor_interval: float = 9.0) -> bool:
        """
        Trigger to start independent thread that polls build stages

        Args:
            build_url: Server URL of the build
            monitor_interval: Seconds between polling build URL

        Returns:
            True if successful, else False
        """
        logger.debug(f'Starting thread for build stages for "{build_url}" ...')
        try:
            t = threading.Thread(
                target=self.__thread_build_stages,
                args=(
                    build_url,
                    monitor_interval,
                ),
                daemon=True,
            )
            t.start()
            self._threads.append(t)
        except Exception as error:
            logger.error(
                f'Failed to start build info monitoring thread for {build_url}. Exception: {error}. Type: {type(error)}'
            )

        return True
