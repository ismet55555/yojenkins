"""Tests for yojenkins/monitor/build_monitor.py"""

import threading
from unittest.mock import MagicMock, patch

import pytest

from yojenkins.monitor.build_monitor import BuildMonitor


@pytest.fixture
def mock_rest():
    return MagicMock()


@pytest.fixture
def mock_auth():
    return MagicMock()


@pytest.fixture
def mock_build():
    return MagicMock()


@pytest.fixture
def build_monitor(mock_rest, mock_auth, mock_build):
    return BuildMonitor(mock_rest, mock_auth, mock_build)


class TestBuildMonitorInit:
    """Tests for BuildMonitor.__init__"""

    def test_sets_rest_auth_build(self, mock_rest, mock_auth, mock_build):
        bm = BuildMonitor(mock_rest, mock_auth, mock_build)
        assert bm.rest is mock_rest
        assert bm.auth is mock_auth
        assert bm.build is mock_build

    def test_inherits_monitor_defaults(self, build_monitor):
        assert build_monitor.quit == 0
        assert build_monitor.exit is False
        assert build_monitor.all_threads_enabled is True

    def test_build_specific_defaults(self, build_monitor):
        assert build_monitor.build_info_data == {}
        assert build_monitor.build_info_thread_interval == 0.0
        assert build_monitor.build_stages_data == {}
        assert build_monitor.build_stages_thread_interval == 0.0
        assert build_monitor.build_abort == 0
        assert build_monitor.build_logs is False
        assert build_monitor.message_box_temp_duration == 1

    def test_thread_locks_are_lock_instances(self, build_monitor):
        assert isinstance(build_monitor._build_info_thread_lock, type(threading.Lock()))
        assert isinstance(build_monitor._build_stages_thread_lock, type(threading.Lock()))


class TestBuildMonitorStatusMapping:
    """Tests for inherited status_to_color in build monitor context"""

    def test_success_color(self, build_monitor):
        assert build_monitor.status_to_color('SUCCESS') == 'green'

    def test_failure_color(self, build_monitor):
        assert build_monitor.status_to_color('FAILURE') == 'red'

    def test_unstable_color(self, build_monitor):
        assert build_monitor.status_to_color('UNSTABLE') == 'orange'


class TestBuildMonitorMonitorStart:
    """Tests for monitor_start which wraps curses"""

    @patch('yojenkins.monitor.build_monitor.curses')
    @patch('yojenkins.monitor.build_monitor.mu.logging_console')
    def test_monitor_start_disables_console_logging(self, mock_logging, mock_curses, build_monitor):
        mock_curses.wrapper.return_value = True
        build_monitor.monitor_start('http://jenkins/job/test/1/')
        mock_logging.assert_called_once_with(enabled=False)

    @patch('yojenkins.monitor.build_monitor.curses')
    @patch('yojenkins.monitor.build_monitor.mu.logging_console')
    def test_monitor_start_calls_curses_wrapper(self, mock_logging, mock_curses, build_monitor):
        mock_curses.wrapper.return_value = True
        result = build_monitor.monitor_start('http://jenkins/job/test/1/')
        assert result is True
        mock_curses.wrapper.assert_called_once()


class TestBuildMonitorThreadControl:
    """Tests for thread management"""

    def test_all_threads_off_disables(self, build_monitor):
        build_monitor.all_threads_enabled = True
        build_monitor.all_threads_off()
        assert build_monitor.all_threads_enabled is False

    def test_pause_sets_flag(self, build_monitor):
        build_monitor.all_threads_pause()
        assert build_monitor.paused is True


class TestBuildMonitorSoundDirectory:
    """Tests for sound_directory attribute"""

    def test_sound_directory_default_empty(self, build_monitor):
        assert build_monitor.sound_directory == ''


class TestBuildMonitorMonitorStartSound:
    """Tests for monitor_start with sound parameter"""

    @patch('yojenkins.monitor.build_monitor.curses')
    @patch('yojenkins.monitor.build_monitor.mu.logging_console')
    def test_monitor_start_passes_sound_arg(self, mock_logging, mock_curses, build_monitor):
        mock_curses.wrapper.return_value = True
        build_monitor.monitor_start('http://jenkins/job/test/1/', sound=True)
        # Verify wrapper called with sound=True
        args = mock_curses.wrapper.call_args
        assert args[0][2] is True  # third positional arg is sound


class TestBuildInfoThreadOn:
    """Tests for __build_info_thread_on"""

    @patch('yojenkins.monitor.build_monitor.threading.Thread')
    def test_build_info_thread_on_starts_thread(self, mock_thread_cls, build_monitor):
        mock_thread = MagicMock()
        mock_thread_cls.return_value = mock_thread

        result = build_monitor._BuildMonitor__build_info_thread_on(
            build_url='http://jenkins/job/test/1/',
            monitor_interval=5.0,
        )

        assert result is True
        mock_thread.start.assert_called_once()

    @patch('yojenkins.monitor.build_monitor.threading.Thread')
    def test_build_info_thread_on_exception_still_returns_true(self, mock_thread_cls, build_monitor):
        mock_thread_cls.side_effect = RuntimeError('thread error')

        result = build_monitor._BuildMonitor__build_info_thread_on(
            build_url='http://jenkins/job/test/1/',
        )

        assert result is True

    @patch('yojenkins.monitor.build_monitor.threading.Thread')
    def test_build_info_thread_on_default_interval(self, mock_thread_cls, build_monitor):
        mock_thread = MagicMock()
        mock_thread_cls.return_value = mock_thread

        build_monitor._BuildMonitor__build_info_thread_on(build_url='http://jenkins/job/test/1/')

        args = mock_thread_cls.call_args
        assert args[1]['args'][1] == 7.0  # default monitor_interval


class TestBuildStagesThreadOn:
    """Tests for __build_stages_thread_on"""

    @patch('yojenkins.monitor.build_monitor.threading.Thread')
    def test_build_stages_thread_on_starts_thread(self, mock_thread_cls, build_monitor):
        mock_thread = MagicMock()
        mock_thread_cls.return_value = mock_thread

        result = build_monitor._BuildMonitor__build_stages_thread_on(
            build_url='http://jenkins/job/test/1/',
            monitor_interval=9.0,
        )

        assert result is True
        mock_thread.start.assert_called_once()

    @patch('yojenkins.monitor.build_monitor.threading.Thread')
    def test_build_stages_thread_on_exception_still_returns_true(self, mock_thread_cls, build_monitor):
        mock_thread_cls.side_effect = RuntimeError('thread error')

        result = build_monitor._BuildMonitor__build_stages_thread_on(
            build_url='http://jenkins/job/test/1/',
        )

        assert result is True


class TestThreadBuildInfo:
    """Tests for __thread_build_info data collection"""

    def test_collects_build_info_data(self, build_monitor):
        build_monitor.build.info.return_value = {'jobName': 'test', 'url': 'http://test'}

        def stop_after_first(*args, **kwargs):
            build_monitor.all_threads_enabled = False
            return {'jobName': 'test', 'url': 'http://test'}

        build_monitor.build.info.side_effect = stop_after_first

        build_monitor._BuildMonitor__thread_build_info(
            build_url='http://jenkins/job/test/1/',
            monitor_interval=0.0,
        )

        assert build_monitor.build_info_data == {'jobName': 'test', 'url': 'http://test'}
        assert build_monitor.build_info_thread_interval == 0.0

    def test_paused_skips_data_collection(self, build_monitor):
        build_monitor.paused = True

        def stop_on_sleep(x):
            build_monitor.all_threads_enabled = False

        with patch('yojenkins.monitor.build_monitor.sleep', side_effect=stop_on_sleep):
            build_monitor._BuildMonitor__thread_build_info(
                build_url='http://jenkins/job/test/1/',
                monitor_interval=0.0,
            )

        build_monitor.build.info.assert_not_called()


class TestThreadBuildStages:
    """Tests for __thread_build_stages data collection"""

    def test_non_staged_build_returns_early(self, build_monitor):
        build_monitor.rest.request.return_value = (None, None, False)

        build_monitor._BuildMonitor__thread_build_stages(
            build_url='http://jenkins/job/test/1/',
            monitor_interval=0.0,
        )

        # Should return without entering the main loop
        assert build_monitor.build_stages_data == {}

    def test_staged_build_collects_stages(self, build_monitor):
        build_monitor.rest.request.return_value = ({'stages': []}, {}, True)

        stages = [{'name': 'Build', 'status': 'SUCCESS', 'durationFormatted': '1m 30s'}]
        build_monitor.build.stage_list.return_value = (stages,)

        def stop_after_first(*args, **kwargs):
            build_monitor.all_threads_enabled = False
            return (stages,)

        build_monitor.build.stage_list.side_effect = stop_after_first

        build_monitor._BuildMonitor__thread_build_stages(
            build_url='http://jenkins/job/test/1/',
            monitor_interval=0.0,
        )

        assert build_monitor.build_stages_data == stages


class TestBuildMonitorDraw:
    """Tests for __monitor_draw method with mocked curses"""

    @pytest.fixture
    def draw_monitor(self, mock_rest, mock_auth, mock_build):
        bm = BuildMonitor(mock_rest, mock_auth, mock_build)
        bm.color = {
            'normal': 1, 'grey-light': 2, 'grey-dark': 3,
            'green': 4, 'red': 5, 'magenta': 6, 'orange': 7,
            'cyan': 8, 'blue': 9, 'yellow': 10,
        }
        bm.decor = {'bold': 1, 'normal': 0}
        # Mock out methods that need real curses or start threads
        bm.basic_screen_setup = MagicMock()
        bm.check_terminal_size = MagicMock()
        bm.server_status_thread_on = MagicMock()
        bm._BuildMonitor__build_info_thread_on = MagicMock()
        bm._BuildMonitor__build_stages_thread_on = MagicMock()
        return bm

    @patch('yojenkins.monitor.build_monitor.mu')
    @patch('yojenkins.monitor.build_monitor.curses')
    def test_monitor_draw_quit_twice_returns_true(self, mock_curses, mock_mu, draw_monitor):
        mock_mu.load_keys.return_value = {
            'QUIT': (ord('q'),), 'ABORT': (ord('a'),), 'RESUME': (ord('r'),),
            'PAUSE': (ord('p'),), 'HELP': (ord('h'),), 'OPEN': (ord('o'),),
            'SOUND': (ord('s'),), 'LOGS': (ord('l'),),
        }

        mock_scr = MagicMock()
        mock_scr.getmaxyx.return_value = (40, 120)
        # First getch: q (quit), second getch: q (confirm quit)
        mock_scr.getch.side_effect = [ord('q'), ord('q')]

        result = draw_monitor._BuildMonitor__monitor_draw(mock_scr, 'http://jenkins/job/test/1/')
        assert result is True
        assert draw_monitor.all_threads_enabled is False

    @patch('yojenkins.monitor.build_monitor.mu')
    @patch('yojenkins.monitor.build_monitor.curses')
    def test_monitor_draw_logs_returns_true(self, mock_curses, mock_mu, draw_monitor):
        mock_mu.load_keys.return_value = {
            'QUIT': (ord('q'),), 'ABORT': (ord('a'),), 'RESUME': (ord('r'),),
            'PAUSE': (ord('p'),), 'HELP': (ord('h'),), 'OPEN': (ord('o'),),
            'SOUND': (ord('s'),), 'LOGS': (ord('l'),),
        }

        mock_scr = MagicMock()
        mock_scr.getmaxyx.return_value = (40, 120)
        mock_scr.getch.side_effect = [ord('l')]

        result = draw_monitor._BuildMonitor__monitor_draw(mock_scr, 'http://jenkins/job/test/1/')
        assert result is True
        assert draw_monitor.build_logs is True

    @patch('yojenkins.monitor.build_monitor.mu')
    @patch('yojenkins.monitor.build_monitor.curses')
    def test_monitor_draw_no_data_shows_no_data(self, mock_curses, mock_mu, draw_monitor):
        mock_mu.load_keys.return_value = {
            'QUIT': (ord('q'),), 'ABORT': (ord('a'),), 'RESUME': (ord('r'),),
            'PAUSE': (ord('p'),), 'HELP': (ord('h'),), 'OPEN': (ord('o'),),
            'SOUND': (ord('s'),), 'LOGS': (ord('l'),),
        }

        mock_scr = MagicMock()
        mock_scr.getmaxyx.return_value = (40, 120)
        mock_scr.getch.side_effect = [ord('q'), ord('q')]

        draw_monitor.build_info_data = {}
        draw_monitor._BuildMonitor__monitor_draw(mock_scr, 'http://jenkins/job/test/1/')

        # Verify 'NO DATA' was drawn
        no_data_calls = [c for c in mock_mu.draw_text.call_args_list if len(c[0]) > 1 and c[0][1] == 'NO DATA']
        assert len(no_data_calls) > 0

    @patch('yojenkins.monitor.build_monitor.mu')
    @patch('yojenkins.monitor.build_monitor.curses')
    def test_monitor_draw_with_build_info_data(self, mock_curses, mock_mu, draw_monitor):
        mock_mu.load_keys.return_value = {
            'QUIT': (ord('q'),), 'ABORT': (ord('a'),), 'RESUME': (ord('r'),),
            'PAUSE': (ord('p'),), 'HELP': (ord('h'),), 'OPEN': (ord('o'),),
            'SOUND': (ord('s'),), 'LOGS': (ord('l'),),
        }
        mock_mu.truncate_text.side_effect = lambda text, width: text

        mock_scr = MagicMock()
        mock_scr.getmaxyx.return_value = (40, 120)
        mock_scr.getch.side_effect = [ord('q'), ord('q')]

        draw_monitor.build_info_data = {
            'url': 'http://jenkins/job/test/1/',
            'jobName': 'test-job',
            'displayName': '#1',
            'folderFullName': '/folder',
            'serverURL': 'http://jenkins',
            'builtOn': 'master',
            'startDatetime': '2024-01-01',
            'endDatetime': '2024-01-01',
            'elapsedFormatted': '1m 30s',
            'estimatedDurationFormatted': '2m',
            'resultText': 'SUCCESS',
        }

        draw_monitor._BuildMonitor__monitor_draw(mock_scr, 'http://jenkins/job/test/1/')

        # Verify draw_text was called multiple times with build info
        assert mock_mu.draw_text.call_count > 5

    @patch('yojenkins.monitor.build_monitor.mu')
    @patch('yojenkins.monitor.build_monitor.curses')
    def test_monitor_draw_abort_twice_triggers_abort(self, mock_curses, mock_mu, draw_monitor):
        mock_mu.load_keys.return_value = {
            'QUIT': (ord('q'),), 'ABORT': (ord('a'),), 'RESUME': (ord('r'),),
            'PAUSE': (ord('p'),), 'HELP': (ord('h'),), 'OPEN': (ord('o'),),
            'SOUND': (ord('s'),), 'LOGS': (ord('l'),),
        }

        mock_scr = MagicMock()
        mock_scr.getmaxyx.return_value = (40, 120)
        # abort, abort (confirm), then quit, quit
        mock_scr.getch.side_effect = [ord('a'), ord('a'), ord('q'), ord('q')]

        draw_monitor._BuildMonitor__monitor_draw(mock_scr, 'http://jenkins/job/test/1/')
        draw_monitor.build.abort.assert_called_once_with(build_url='http://jenkins/job/test/1/')

    @patch('yojenkins.monitor.build_monitor.mu')
    @patch('yojenkins.monitor.build_monitor.curses')
    def test_monitor_draw_with_stages(self, mock_curses, mock_mu, draw_monitor):
        mock_mu.load_keys.return_value = {
            'QUIT': (ord('q'),), 'ABORT': (ord('a'),), 'RESUME': (ord('r'),),
            'PAUSE': (ord('p'),), 'HELP': (ord('h'),), 'OPEN': (ord('o'),),
            'SOUND': (ord('s'),), 'LOGS': (ord('l'),),
        }
        mock_mu.truncate_text.side_effect = lambda text, width: text

        mock_scr = MagicMock()
        mock_scr.getmaxyx.return_value = (40, 120)
        mock_scr.getch.side_effect = [ord('q'), ord('q')]

        draw_monitor.build_info_data = {
            'url': 'http://jenkins/job/test/1/',
            'jobName': 'test-job',
            'displayName': '#1',
            'folderFullName': '/folder',
            'serverURL': 'http://jenkins',
            'builtOn': 'master',
            'startDatetime': '2024-01-01',
            'endDatetime': '2024-01-01',
            'elapsedFormatted': '1m',
            'estimatedDurationFormatted': '2m',
            'resultText': 'SUCCESS',
        }
        draw_monitor.build_stages_data = [
            {'name': 'Build', 'status': 'SUCCESS', 'durationFormatted': '30s'},
            {'name': 'Test', 'status': 'FAILURE', 'durationFormatted': '1m'},
        ]

        draw_monitor._BuildMonitor__monitor_draw(mock_scr, 'http://jenkins/job/test/1/')

        # Verify stages header was drawn
        header_calls = [c for c in mock_mu.draw_horizontal_header.call_args_list
                        if len(c[0]) > 5 and c[0][5] == 'STAGES']
        assert len(header_calls) > 0

    @patch('yojenkins.monitor.build_monitor.mu')
    @patch('yojenkins.monitor.build_monitor.curses')
    def test_monitor_draw_border_color_success(self, mock_curses, mock_mu, draw_monitor):
        mock_mu.load_keys.return_value = {
            'QUIT': (ord('q'),), 'ABORT': (ord('a'),), 'RESUME': (ord('r'),),
            'PAUSE': (ord('p'),), 'HELP': (ord('h'),), 'OPEN': (ord('o'),),
            'SOUND': (ord('s'),), 'LOGS': (ord('l'),),
        }
        mock_mu.truncate_text.side_effect = lambda text, width: text

        mock_scr = MagicMock()
        mock_scr.getmaxyx.return_value = (40, 120)
        mock_scr.getch.side_effect = [ord('q'), ord('q')]

        draw_monitor.build_info_data = {
            'url': 'http://jenkins/job/test/1/',
            'jobName': 'test', 'displayName': '#1',
            'folderFullName': '/', 'serverURL': 'http://j',
            'builtOn': 'master', 'startDatetime': '',
            'endDatetime': '', 'elapsedFormatted': '',
            'estimatedDurationFormatted': '',
            'resultText': 'SUCCESS',
        }

        draw_monitor._BuildMonitor__monitor_draw(mock_scr, 'http://jenkins/job/test/1/')

        # Verify draw_screen_border was called with green color
        border_call = mock_mu.draw_screen_border.call_args
        assert border_call[0][1] == draw_monitor.color['green']

    @patch('yojenkins.monitor.build_monitor.mu')
    @patch('yojenkins.monitor.build_monitor.curses')
    def test_monitor_draw_border_color_failure(self, mock_curses, mock_mu, draw_monitor):
        mock_mu.load_keys.return_value = {
            'QUIT': (ord('q'),), 'ABORT': (ord('a'),), 'RESUME': (ord('r'),),
            'PAUSE': (ord('p'),), 'HELP': (ord('h'),), 'OPEN': (ord('o'),),
            'SOUND': (ord('s'),), 'LOGS': (ord('l'),),
        }
        mock_mu.truncate_text.side_effect = lambda text, width: text

        mock_scr = MagicMock()
        mock_scr.getmaxyx.return_value = (40, 120)
        mock_scr.getch.side_effect = [ord('q'), ord('q')]

        draw_monitor.build_info_data = {
            'url': 'http://jenkins/job/test/1/',
            'jobName': 'test', 'displayName': '#1',
            'folderFullName': '/', 'serverURL': 'http://j',
            'builtOn': 'master', 'startDatetime': '',
            'endDatetime': '', 'elapsedFormatted': '',
            'estimatedDurationFormatted': '',
            'resultText': 'FAILURE',
        }

        draw_monitor._BuildMonitor__monitor_draw(mock_scr, 'http://jenkins/job/test/1/')

        border_call = mock_mu.draw_screen_border.call_args
        assert border_call[0][1] == draw_monitor.color['red']

    @patch('yojenkins.monitor.build_monitor.mu')
    @patch('yojenkins.monitor.build_monitor.curses')
    def test_monitor_draw_server_status_displayed(self, mock_curses, mock_mu, draw_monitor):
        mock_mu.load_keys.return_value = {
            'QUIT': (ord('q'),), 'ABORT': (ord('a'),), 'RESUME': (ord('r'),),
            'PAUSE': (ord('p'),), 'HELP': (ord('h'),), 'OPEN': (ord('o'),),
            'SOUND': (ord('s'),), 'LOGS': (ord('l'),),
        }

        mock_scr = MagicMock()
        mock_scr.getmaxyx.return_value = (40, 120)
        mock_scr.getch.side_effect = [ord('q'), ord('q')]

        draw_monitor.server_status_data = {'auth': True, 'reachable': True}

        draw_monitor._BuildMonitor__monitor_draw(mock_scr, 'http://jenkins/job/test/1/')

        # Find draw_text call with server status text
        server_calls = [
            c for c in mock_mu.draw_text.call_args_list
            if len(c[0]) > 1 and isinstance(c[0][1], str) and 'Reachable' in c[0][1]
        ]
        assert len(server_calls) > 0

    @patch('yojenkins.monitor.build_monitor.mu')
    @patch('yojenkins.monitor.build_monitor.curses')
    def test_monitor_draw_help_toggle(self, mock_curses, mock_mu, draw_monitor):
        mock_mu.load_keys.return_value = {
            'QUIT': (ord('q'),), 'ABORT': (ord('a'),), 'RESUME': (ord('r'),),
            'PAUSE': (ord('p'),), 'HELP': (ord('h'),), 'OPEN': (ord('o'),),
            'SOUND': (ord('s'),), 'LOGS': (ord('l'),),
        }

        mock_scr = MagicMock()
        mock_scr.getmaxyx.return_value = (40, 120)
        # Press h (help), then q twice to quit
        mock_scr.getch.side_effect = [ord('h'), ord('q'), ord('q')]

        draw_monitor._BuildMonitor__monitor_draw(mock_scr, 'http://jenkins/job/test/1/')

        # Verify draw_message_box was called for help
        help_calls = [c for c in mock_mu.draw_message_box.call_args_list]
        assert len(help_calls) > 0

    @patch('yojenkins.monitor.build_monitor.mu')
    @patch('yojenkins.monitor.build_monitor.curses')
    def test_monitor_draw_pause_toggle(self, mock_curses, mock_mu, draw_monitor):
        mock_mu.load_keys.return_value = {
            'QUIT': (ord('q'),), 'ABORT': (ord('a'),), 'RESUME': (ord('r'),),
            'PAUSE': (ord('p'),), 'HELP': (ord('h'),), 'OPEN': (ord('o'),),
            'SOUND': (ord('s'),), 'LOGS': (ord('l'),),
        }

        mock_scr = MagicMock()
        mock_scr.getmaxyx.return_value = (40, 120)
        # pause, then unpause, then quit twice
        mock_scr.getch.side_effect = [ord('p'), ord('p'), ord('q'), ord('q')]

        draw_monitor._BuildMonitor__monitor_draw(mock_scr, 'http://jenkins/job/test/1/')

        pause_calls = [c for c in mock_mu.draw_message_box.call_args_list
                       if len(c[0]) > 0 and 'Monitor paused' in str(c[0][1])]
        assert len(pause_calls) > 0

    @patch('yojenkins.monitor.build_monitor.mu')
    @patch('yojenkins.monitor.build_monitor.curses')
    def test_monitor_draw_open_calls_browser(self, mock_curses, mock_mu, draw_monitor):
        mock_mu.load_keys.return_value = {
            'QUIT': (ord('q'),), 'ABORT': (ord('a'),), 'RESUME': (ord('r'),),
            'PAUSE': (ord('p'),), 'HELP': (ord('h'),), 'OPEN': (ord('o'),),
            'SOUND': (ord('s'),), 'LOGS': (ord('l'),),
        }

        mock_scr = MagicMock()
        mock_scr.getmaxyx.return_value = (40, 120)
        mock_scr.getch.side_effect = [ord('o'), ord('q'), ord('q')]

        draw_monitor._BuildMonitor__monitor_draw(mock_scr, 'http://jenkins/job/test/1/')
        draw_monitor.build.browser_open.assert_called_once_with(build_url='http://jenkins/job/test/1/')

    @patch('yojenkins.monitor.build_monitor.mu')
    @patch('yojenkins.monitor.build_monitor.curses')
    def test_monitor_draw_no_stages_lowers_height_limit(self, mock_curses, mock_mu, draw_monitor):
        mock_mu.load_keys.return_value = {
            'QUIT': (ord('q'),), 'ABORT': (ord('a'),), 'RESUME': (ord('r'),),
            'PAUSE': (ord('p'),), 'HELP': (ord('h'),), 'OPEN': (ord('o'),),
            'SOUND': (ord('s'),), 'LOGS': (ord('l'),),
        }

        mock_scr = MagicMock()
        mock_scr.getmaxyx.return_value = (40, 120)
        mock_scr.getch.side_effect = [ord('q'), ord('q')]

        draw_monitor.build_stages_data = {}  # no stages

        draw_monitor._BuildMonitor__monitor_draw(mock_scr, 'http://jenkins/job/test/1/')
        assert draw_monitor.height_limit == 17
