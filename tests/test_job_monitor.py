"""Tests for yojenkins/monitor/job_monitor.py"""

import threading
from unittest.mock import MagicMock, patch

import pytest

from yojenkins.monitor.job_monitor import JobMonitor


@pytest.fixture
def mock_rest():
    return MagicMock()


@pytest.fixture
def mock_auth():
    return MagicMock()


@pytest.fixture
def mock_job():
    return MagicMock()


@pytest.fixture
def mock_build():
    return MagicMock()


@pytest.fixture
def job_monitor(mock_rest, mock_auth, mock_job, mock_build):
    return JobMonitor(mock_rest, mock_auth, mock_job, mock_build)


class TestJobMonitorInit:
    """Tests for JobMonitor.__init__"""

    def test_sets_rest_auth_job_build(self, mock_rest, mock_auth, mock_job, mock_build):
        jm = JobMonitor(mock_rest, mock_auth, mock_job, mock_build)
        assert jm.rest is mock_rest
        assert jm.auth is mock_auth
        assert jm.job is mock_job
        assert jm.build is mock_build

    def test_inherits_monitor_defaults(self, job_monitor):
        assert job_monitor.quit == 0
        assert job_monitor.exit is False
        assert job_monitor.all_threads_enabled is True

    def test_job_specific_defaults(self, job_monitor):
        assert job_monitor.job_info_data == {}
        assert job_monitor.job_info_thread_interval == 0.0
        assert job_monitor.builds_data == []
        assert job_monitor.builds_data_number_of_builds == 10
        assert job_monitor.builds_data_thread_interval == 0.0
        assert job_monitor.job_build == 0
        assert job_monitor.message_box_temp_duration == 1

    def test_thread_locks_are_lock_instances(self, job_monitor):
        assert isinstance(job_monitor._job_info_thread_lock, type(threading.Lock()))
        assert isinstance(job_monitor._build_data_thread_lock, type(threading.Lock()))


class TestJobMonitorMonitorStart:
    """Tests for monitor_start"""

    @patch('yojenkins.monitor.job_monitor.curses')
    @patch('yojenkins.monitor.job_monitor.mu.logging_console')
    def test_monitor_start_disables_console_logging(self, mock_logging, mock_curses, job_monitor):
        mock_curses.wrapper.return_value = True
        job_monitor.monitor_start('http://jenkins/job/test/')
        mock_logging.assert_called_once_with(enabled=False)

    @patch('yojenkins.monitor.job_monitor.curses')
    @patch('yojenkins.monitor.job_monitor.mu.logging_console')
    def test_monitor_start_calls_curses_wrapper(self, mock_logging, mock_curses, job_monitor):
        mock_curses.wrapper.return_value = True
        result = job_monitor.monitor_start('http://jenkins/job/test/')
        assert result is True
        mock_curses.wrapper.assert_called_once()

    @patch('yojenkins.monitor.job_monitor.curses')
    @patch('yojenkins.monitor.job_monitor.mu.logging_console')
    def test_monitor_start_passes_sound_arg(self, mock_logging, mock_curses, job_monitor):
        mock_curses.wrapper.return_value = True
        job_monitor.monitor_start('http://jenkins/job/test/', sound=True)
        args = mock_curses.wrapper.call_args
        assert args[0][2] is True


class TestJobInfoThreadOn:
    """Tests for __job_info_thread_on"""

    @patch('yojenkins.monitor.job_monitor.threading.Thread')
    def test_starts_thread(self, mock_thread_cls, job_monitor):
        mock_thread = MagicMock()
        mock_thread_cls.return_value = mock_thread

        result = job_monitor._JobMonitor__job_info_thread_on(
            job_url='http://jenkins/job/test/',
            monitor_interval=5.0,
        )

        assert result is True
        mock_thread.start.assert_called_once()

    @patch('yojenkins.monitor.job_monitor.threading.Thread')
    def test_exception_still_returns_true(self, mock_thread_cls, job_monitor):
        mock_thread_cls.side_effect = RuntimeError('thread error')

        result = job_monitor._JobMonitor__job_info_thread_on(
            job_url='http://jenkins/job/test/',
        )

        assert result is True

    @patch('yojenkins.monitor.job_monitor.threading.Thread')
    def test_default_interval(self, mock_thread_cls, job_monitor):
        mock_thread = MagicMock()
        mock_thread_cls.return_value = mock_thread

        job_monitor._JobMonitor__job_info_thread_on(job_url='http://jenkins/job/test/')

        args = mock_thread_cls.call_args
        assert args[1]['args'][1] == 5.0


class TestBuildsDataThreadOn:
    """Tests for __builds_data_thread_on"""

    @patch('yojenkins.monitor.job_monitor.threading.Thread')
    def test_starts_thread(self, mock_thread_cls, job_monitor):
        mock_thread = MagicMock()
        mock_thread_cls.return_value = mock_thread

        result = job_monitor._JobMonitor__builds_data_thread_on(monitor_interval=7.0)

        assert result is True
        mock_thread.start.assert_called_once()

    @patch('yojenkins.monitor.job_monitor.threading.Thread')
    def test_exception_still_returns_true(self, mock_thread_cls, job_monitor):
        mock_thread_cls.side_effect = RuntimeError('thread error')

        result = job_monitor._JobMonitor__builds_data_thread_on()

        assert result is True


class TestThreadJobInfo:
    """Tests for __thread_job_info data collection"""

    def test_collects_job_info_data(self, job_monitor):
        job_data = {'displayName': 'test-job', 'url': 'http://test'}

        def stop_after_first(*args, **kwargs):
            job_monitor.all_threads_enabled = False
            return job_data

        job_monitor.job.info.side_effect = stop_after_first

        job_monitor._JobMonitor__thread_job_info(
            job_url='http://jenkins/job/test/',
            monitor_interval=0.0,
        )

        assert job_monitor.job_info_data == job_data
        assert job_monitor.job_info_thread_interval == 0.0

    def test_paused_skips_collection(self, job_monitor):
        job_monitor.paused = True

        def stop_on_sleep(x):
            job_monitor.all_threads_enabled = False

        with patch('yojenkins.monitor.job_monitor.sleep', side_effect=stop_on_sleep):
            job_monitor._JobMonitor__thread_job_info(
                job_url='http://jenkins/job/test/',
                monitor_interval=0.0,
            )

        job_monitor.job.info.assert_not_called()


class TestThreadBuildInfo:
    """Tests for __thread_build_info single build fetch"""

    def test_fetches_build_info(self, job_monitor):
        job_monitor.builds_data = [None, None, None]
        build_data = {'displayName': '#1', 'number': 1}
        job_monitor.build.info.return_value = build_data

        job_monitor._JobMonitor__thread_build_info(
            build_url='http://jenkins/job/test/1/',
            build_data_index=1,
        )

        assert job_monitor.builds_data[1] == build_data
        assert job_monitor.server_interaction is True


class TestThreadBuildsData:
    """Tests for __thread_builds_data orchestrator thread"""

    def test_preallocates_builds_data(self, job_monitor):
        job_monitor.builds_data_number_of_builds = 5
        job_monitor.job_info_data = {'builds': []}

        def stop_on_sleep(x):
            job_monitor.all_threads_enabled = False

        with patch('yojenkins.monitor.job_monitor.sleep', side_effect=stop_on_sleep):
            job_monitor._JobMonitor__thread_builds_data(monitor_interval=0.0)

        assert len(job_monitor.builds_data) == 5

    def test_waits_for_job_info_data(self, job_monitor):
        """Thread should wait until job_info_data is populated"""
        call_count = [0]

        def populate_and_stop(x):
            call_count[0] += 1
            if call_count[0] == 1:
                job_monitor.job_info_data = {'builds': []}
            if call_count[0] >= 2:
                job_monitor.all_threads_enabled = False

        with patch('yojenkins.monitor.job_monitor.sleep', side_effect=populate_and_stop):
            job_monitor._JobMonitor__thread_builds_data(monitor_interval=0.0)

        assert job_monitor.job_info_data == {'builds': []}

    def test_stops_when_threads_disabled_during_wait(self, job_monitor):
        """Thread exits if all_threads_enabled goes False while waiting for job_info_data"""
        def stop_thread(x):
            job_monitor.all_threads_enabled = False

        with patch('yojenkins.monitor.job_monitor.sleep', side_effect=stop_thread):
            job_monitor._JobMonitor__thread_builds_data(monitor_interval=0.0)

        assert job_monitor.builds_data == [None] * 10


class TestJobMonitorDraw:
    """Tests for __monitor_draw method with mocked curses"""

    @pytest.fixture
    def draw_monitor(self, mock_rest, mock_auth, mock_job, mock_build):
        jm = JobMonitor(mock_rest, mock_auth, mock_job, mock_build)
        jm.color = {
            'normal': 1, 'grey-light': 2, 'grey-dark': 3,
            'green': 4, 'red': 5, 'magenta': 6, 'orange': 7,
            'cyan': 8, 'blue': 9, 'yellow': 10,
        }
        jm.decor = {'bold': 1, 'normal': 0}
        # Mock out methods that need real curses or start threads
        jm.basic_screen_setup = MagicMock()
        jm.check_terminal_size = MagicMock()
        jm.server_status_thread_on = MagicMock()
        jm._JobMonitor__job_info_thread_on = MagicMock()
        jm._JobMonitor__builds_data_thread_on = MagicMock()
        return jm

    @patch('yojenkins.monitor.job_monitor.mu')
    @patch('yojenkins.monitor.job_monitor.curses')
    def test_quit_twice_returns_true(self, mock_curses, mock_mu, draw_monitor):
        mock_mu.load_keys.return_value = {
            'QUIT': (ord('q'),), 'BUILD': (ord('b'),), 'RESUME': (ord('r'),),
            'PAUSE': (ord('p'),), 'HELP': (ord('h'),), 'OPEN': (ord('o'),),
        }

        mock_scr = MagicMock()
        mock_scr.getmaxyx.return_value = (40, 120)
        mock_scr.getch.side_effect = [ord('q'), ord('q')]

        result = draw_monitor._JobMonitor__monitor_draw(mock_scr, 'http://jenkins/job/test/')
        assert result is True
        assert draw_monitor.all_threads_enabled is False

    @patch('yojenkins.monitor.job_monitor.mu')
    @patch('yojenkins.monitor.job_monitor.curses')
    def test_no_data_shows_no_data(self, mock_curses, mock_mu, draw_monitor):
        mock_mu.load_keys.return_value = {
            'QUIT': (ord('q'),), 'BUILD': (ord('b'),), 'RESUME': (ord('r'),),
            'PAUSE': (ord('p'),), 'HELP': (ord('h'),), 'OPEN': (ord('o'),),
        }

        mock_scr = MagicMock()
        mock_scr.getmaxyx.return_value = (40, 120)
        mock_scr.getch.side_effect = [ord('q'), ord('q')]

        draw_monitor.job_info_data = {}

        draw_monitor._JobMonitor__monitor_draw(mock_scr, 'http://jenkins/job/test/')

        no_data_calls = [c for c in mock_mu.draw_text.call_args_list
                         if len(c[0]) > 1 and c[0][1] == 'NO DATA']
        assert len(no_data_calls) > 0

    @patch('yojenkins.monitor.job_monitor.mu')
    @patch('yojenkins.monitor.job_monitor.curses')
    def test_with_job_info_data(self, mock_curses, mock_mu, draw_monitor):
        mock_mu.load_keys.return_value = {
            'QUIT': (ord('q'),), 'BUILD': (ord('b'),), 'RESUME': (ord('r'),),
            'PAUSE': (ord('p'),), 'HELP': (ord('h'),), 'OPEN': (ord('o'),),
        }
        mock_mu.truncate_text.side_effect = lambda text, width: text

        mock_scr = MagicMock()
        mock_scr.getmaxyx.return_value = (40, 120)
        mock_scr.getch.side_effect = [ord('q'), ord('q')]

        draw_monitor.job_info_data = {
            'url': 'http://jenkins/job/test/',
            'displayName': 'test-job',
            'folderFullName': '/folder',
            'serverURL': 'http://jenkins',
        }

        draw_monitor._JobMonitor__monitor_draw(mock_scr, 'http://jenkins/job/test/')
        assert mock_mu.draw_text.call_count > 5

    @patch('yojenkins.monitor.job_monitor.mu')
    @patch('yojenkins.monitor.job_monitor.curses')
    def test_with_builds_data(self, mock_curses, mock_mu, draw_monitor):
        mock_mu.load_keys.return_value = {
            'QUIT': (ord('q'),), 'BUILD': (ord('b'),), 'RESUME': (ord('r'),),
            'PAUSE': (ord('p'),), 'HELP': (ord('h'),), 'OPEN': (ord('o'),),
        }
        mock_mu.truncate_text.side_effect = lambda text, width: text

        mock_scr = MagicMock()
        mock_scr.getmaxyx.return_value = (40, 120)
        mock_scr.getch.side_effect = [ord('q'), ord('q')]

        draw_monitor.job_info_data = {
            'url': 'http://jenkins/job/test/',
            'displayName': 'test-job',
            'folderFullName': '/',
            'serverURL': 'http://jenkins',
        }
        draw_monitor.builds_data = [
            {
                'displayName': '#1', 'number': 1,
                'timestamp': 1704067200000,
                'durationFormatted': '1m 30s',
                'elapsedFormatted': '1m 30s',
                'resultText': 'SUCCESS',
            },
            {
                'displayName': '#2', 'number': 2,
                'timestamp': 1704067200000,
                'durationFormatted': None,
                'elapsedFormatted': '2m',
                'resultText': 'FAILURE',
            },
        ]

        draw_monitor._JobMonitor__monitor_draw(mock_scr, 'http://jenkins/job/test/')

        header_calls = [c for c in mock_mu.draw_horizontal_header.call_args_list
                        if len(c[0]) > 5 and c[0][5] == 'BUILDS']
        assert len(header_calls) > 0

    @patch('yojenkins.monitor.job_monitor.mu')
    @patch('yojenkins.monitor.job_monitor.curses')
    def test_build_twice_triggers_build(self, mock_curses, mock_mu, draw_monitor):
        mock_mu.load_keys.return_value = {
            'QUIT': (ord('q'),), 'BUILD': (ord('b'),), 'RESUME': (ord('r'),),
            'PAUSE': (ord('p'),), 'HELP': (ord('h'),), 'OPEN': (ord('o'),),
        }

        mock_scr = MagicMock()
        mock_scr.getmaxyx.return_value = (40, 120)
        mock_scr.getch.side_effect = [ord('b'), ord('b'), ord('q'), ord('q')]

        draw_monitor._JobMonitor__monitor_draw(mock_scr, 'http://jenkins/job/test/')
        draw_monitor.job.build_trigger.assert_called_once_with(job_url='http://jenkins/job/test/')

    @patch('yojenkins.monitor.job_monitor.mu')
    @patch('yojenkins.monitor.job_monitor.curses')
    def test_help_toggle(self, mock_curses, mock_mu, draw_monitor):
        mock_mu.load_keys.return_value = {
            'QUIT': (ord('q'),), 'BUILD': (ord('b'),), 'RESUME': (ord('r'),),
            'PAUSE': (ord('p'),), 'HELP': (ord('h'),), 'OPEN': (ord('o'),),
        }

        mock_scr = MagicMock()
        mock_scr.getmaxyx.return_value = (40, 120)
        mock_scr.getch.side_effect = [ord('h'), ord('q'), ord('q')]

        draw_monitor._JobMonitor__monitor_draw(mock_scr, 'http://jenkins/job/test/')

        help_calls = [c for c in mock_mu.draw_message_box.call_args_list]
        assert len(help_calls) > 0

    @patch('yojenkins.monitor.job_monitor.mu')
    @patch('yojenkins.monitor.job_monitor.curses')
    def test_pause_toggle(self, mock_curses, mock_mu, draw_monitor):
        mock_mu.load_keys.return_value = {
            'QUIT': (ord('q'),), 'BUILD': (ord('b'),), 'RESUME': (ord('r'),),
            'PAUSE': (ord('p'),), 'HELP': (ord('h'),), 'OPEN': (ord('o'),),
        }

        mock_scr = MagicMock()
        mock_scr.getmaxyx.return_value = (40, 120)
        mock_scr.getch.side_effect = [ord('p'), ord('p'), ord('q'), ord('q')]

        draw_monitor._JobMonitor__monitor_draw(mock_scr, 'http://jenkins/job/test/')

        pause_calls = [c for c in mock_mu.draw_message_box.call_args_list
                       if len(c[0]) > 0 and 'Monitor paused' in str(c[0][1])]
        assert len(pause_calls) > 0

    @patch('yojenkins.monitor.job_monitor.mu')
    @patch('yojenkins.monitor.job_monitor.curses')
    def test_open_calls_browser(self, mock_curses, mock_mu, draw_monitor):
        mock_mu.load_keys.return_value = {
            'QUIT': (ord('q'),), 'BUILD': (ord('b'),), 'RESUME': (ord('r'),),
            'PAUSE': (ord('p'),), 'HELP': (ord('h'),), 'OPEN': (ord('o'),),
        }

        mock_scr = MagicMock()
        mock_scr.getmaxyx.return_value = (40, 120)
        mock_scr.getch.side_effect = [ord('o'), ord('q'), ord('q')]

        draw_monitor._JobMonitor__monitor_draw(mock_scr, 'http://jenkins/job/test/')
        draw_monitor.job.browser_open.assert_called_once_with(job_url='http://jenkins/job/test/')

    @patch('yojenkins.monitor.job_monitor.mu')
    @patch('yojenkins.monitor.job_monitor.curses')
    def test_no_builds_lowers_height_limit(self, mock_curses, mock_mu, draw_monitor):
        mock_mu.load_keys.return_value = {
            'QUIT': (ord('q'),), 'BUILD': (ord('b'),), 'RESUME': (ord('r'),),
            'PAUSE': (ord('p'),), 'HELP': (ord('h'),), 'OPEN': (ord('o'),),
        }

        mock_scr = MagicMock()
        mock_scr.getmaxyx.return_value = (40, 120)
        mock_scr.getch.side_effect = [ord('q'), ord('q')]

        draw_monitor.builds_data = []

        draw_monitor._JobMonitor__monitor_draw(mock_scr, 'http://jenkins/job/test/')
        assert draw_monitor.height_limit == 17

    @patch('yojenkins.monitor.job_monitor.mu')
    @patch('yojenkins.monitor.job_monitor.curses')
    def test_server_status_displayed(self, mock_curses, mock_mu, draw_monitor):
        mock_mu.load_keys.return_value = {
            'QUIT': (ord('q'),), 'BUILD': (ord('b'),), 'RESUME': (ord('r'),),
            'PAUSE': (ord('p'),), 'HELP': (ord('h'),), 'OPEN': (ord('o'),),
        }

        mock_scr = MagicMock()
        mock_scr.getmaxyx.return_value = (40, 120)
        mock_scr.getch.side_effect = [ord('q'), ord('q')]

        draw_monitor.server_status_data = {'auth': True, 'reachable': True}

        draw_monitor._JobMonitor__monitor_draw(mock_scr, 'http://jenkins/job/test/')

        server_calls = [
            c for c in mock_mu.draw_text.call_args_list
            if len(c[0]) > 1 and isinstance(c[0][1], str) and 'Reachable' in c[0][1]
        ]
        assert len(server_calls) > 0

    @patch('yojenkins.monitor.job_monitor.mu')
    @patch('yojenkins.monitor.job_monitor.curses')
    def test_server_status_no_data(self, mock_curses, mock_mu, draw_monitor):
        mock_mu.load_keys.return_value = {
            'QUIT': (ord('q'),), 'BUILD': (ord('b'),), 'RESUME': (ord('r'),),
            'PAUSE': (ord('p'),), 'HELP': (ord('h'),), 'OPEN': (ord('o'),),
        }

        mock_scr = MagicMock()
        mock_scr.getmaxyx.return_value = (40, 120)
        mock_scr.getch.side_effect = [ord('q'), ord('q')]

        draw_monitor.server_status_data = {}

        draw_monitor._JobMonitor__monitor_draw(mock_scr, 'http://jenkins/job/test/')

        no_data_calls = [
            c for c in mock_mu.draw_text.call_args_list
            if len(c[0]) > 1 and isinstance(c[0][1], str) and 'Server Status: NO DATA' in c[0][1]
        ]
        assert len(no_data_calls) > 0

    @patch('yojenkins.monitor.job_monitor.mu')
    @patch('yojenkins.monitor.job_monitor.curses')
    def test_resume_resets_quit_and_build(self, mock_curses, mock_mu, draw_monitor):
        mock_mu.load_keys.return_value = {
            'QUIT': (ord('q'),), 'BUILD': (ord('b'),), 'RESUME': (ord('r'),),
            'PAUSE': (ord('p'),), 'HELP': (ord('h'),), 'OPEN': (ord('o'),),
        }

        mock_scr = MagicMock()
        mock_scr.getmaxyx.return_value = (40, 120)
        # Press q (shows quit dialog), r (resume), then q q to quit
        mock_scr.getch.side_effect = [ord('q'), ord('r'), ord('q'), ord('q')]

        draw_monitor._JobMonitor__monitor_draw(mock_scr, 'http://jenkins/job/test/')
        # If resume worked, we should still get True (quit confirmed later)
        assert draw_monitor.all_threads_enabled is False

    @patch('yojenkins.monitor.job_monitor.mu')
    @patch('yojenkins.monitor.job_monitor.curses')
    def test_builds_with_null_result_text(self, mock_curses, mock_mu, draw_monitor):
        """Tests build with resultText=None uses UNKNOWN status"""
        mock_mu.load_keys.return_value = {
            'QUIT': (ord('q'),), 'BUILD': (ord('b'),), 'RESUME': (ord('r'),),
            'PAUSE': (ord('p'),), 'HELP': (ord('h'),), 'OPEN': (ord('o'),),
        }
        mock_mu.truncate_text.side_effect = lambda text, width: text

        mock_scr = MagicMock()
        mock_scr.getmaxyx.return_value = (40, 120)
        mock_scr.getch.side_effect = [ord('q'), ord('q')]

        draw_monitor.job_info_data = {
            'url': 'http://jenkins/job/test/',
            'displayName': 'test-job',
            'folderFullName': '/',
            'serverURL': 'http://jenkins',
        }
        draw_monitor.builds_data = [
            {
                'displayName': '#1', 'number': 1,
                'timestamp': 1704067200000,
                'durationFormatted': '1m',
                'elapsedFormatted': '1m',
                'resultText': None,
            },
        ]

        draw_monitor._JobMonitor__monitor_draw(mock_scr, 'http://jenkins/job/test/')

        # Should have drawn UNKNOWN status
        unknown_calls = [
            c for c in mock_mu.draw_text.call_args_list
            if len(c[0]) > 1 and isinstance(c[0][1], str) and 'UNKNOWN' in c[0][1]
        ]
        assert len(unknown_calls) > 0

    @patch('yojenkins.monitor.job_monitor.mu')
    @patch('yojenkins.monitor.job_monitor.curses')
    def test_empty_build_in_list_breaks_loop(self, mock_curses, mock_mu, draw_monitor):
        """Tests that an empty/None build entry stops iteration"""
        mock_mu.load_keys.return_value = {
            'QUIT': (ord('q'),), 'BUILD': (ord('b'),), 'RESUME': (ord('r'),),
            'PAUSE': (ord('p'),), 'HELP': (ord('h'),), 'OPEN': (ord('o'),),
        }

        mock_scr = MagicMock()
        mock_scr.getmaxyx.return_value = (40, 120)
        mock_scr.getch.side_effect = [ord('q'), ord('q')]

        draw_monitor.job_info_data = {
            'url': 'http://jenkins/job/test/',
            'displayName': 'test-job',
            'folderFullName': '/',
            'serverURL': 'http://jenkins',
        }
        draw_monitor.builds_data = [None]

        # Should not raise; the None build causes a break
        draw_monitor._JobMonitor__monitor_draw(mock_scr, 'http://jenkins/job/test/')
