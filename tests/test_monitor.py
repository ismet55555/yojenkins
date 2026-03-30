"""Tests for yojenkins/monitor/monitor.py (Monitor base class)"""

from time import time
from unittest.mock import MagicMock, patch

import pytest

from yojenkins.monitor.monitor import Monitor


class TestMonitorInit:
    """Tests for Monitor.__init__"""

    def test_default_attributes(self):
        monitor = Monitor()
        assert monitor.rest is None
        assert monitor.auth is None
        assert monitor.job is None
        assert monitor.build is None
        assert monitor.color == {}
        assert monitor.decor == {}
        assert monitor.halfdelay_screen_refresh == 5
        assert monitor.height_limit == 35
        assert monitor.width_limit == 66
        assert monitor.terminal_size_good is True
        assert monitor.curses_alive is True
        assert monitor.quit == 0
        assert monitor.exit is False
        assert monitor.help is False
        assert monitor.playing_sound is False
        assert monitor.all_threads_enabled is True
        assert monitor.paused is False
        assert monitor.server_interaction is False

    def test_server_status_data_empty_dict(self):
        monitor = Monitor()
        assert monitor.server_status_data == {}
        assert monitor.server_status_thread_interval == 0.0


class TestMonitorThreadControl:
    """Tests for thread control methods"""

    def test_all_threads_off_sets_flag(self):
        monitor = Monitor()
        assert monitor.all_threads_enabled is True
        result = monitor.all_threads_off()
        assert result is True
        assert monitor.all_threads_enabled is False

    def test_all_threads_pause_sets_flag(self):
        monitor = Monitor()
        assert monitor.paused is False
        result = monitor.all_threads_pause()
        assert result is True
        assert monitor.paused is True

    def test_all_threads_off_returns_true(self):
        monitor = Monitor()
        assert monitor.all_threads_off() is True


class TestStatusToColor:
    """Tests for Monitor.status_to_color"""

    def test_success_returns_green(self):
        monitor = Monitor()
        assert monitor.status_to_color('SUCCESS') == 'green'

    def test_failure_returns_red(self):
        monitor = Monitor()
        assert monitor.status_to_color('FAILURE') == 'red'

    def test_aborted_returns_magenta(self):
        monitor = Monitor()
        assert monitor.status_to_color('ABORTED') == 'magenta'

    def test_unknown_status_returns_default(self):
        monitor = Monitor()
        result = monitor.status_to_color('NONSENSE_STATUS')
        assert result == 'normal'

    def test_status_with_whitespace(self):
        monitor = Monitor()
        result = monitor.status_to_color('  SUCCESS  ')
        assert result == 'green'

    def test_case_insensitive(self):
        monitor = Monitor()
        assert monitor.status_to_color('success') == 'green'
        assert monitor.status_to_color('Failure') == 'red'


class TestStatusToSound:
    """Tests for Monitor.status_to_sound"""

    def test_success_returns_sound_file(self):
        monitor = Monitor()
        result = monitor.status_to_sound('SUCCESS')
        assert result.endswith('.wav')
        assert 'positive' in result

    def test_failure_returns_sound_file(self):
        monitor = Monitor()
        result = monitor.status_to_sound('FAILURE')
        assert result.endswith('.wav')

    def test_running_returns_empty_string(self):
        monitor = Monitor()
        result = monitor.status_to_sound('RUNNING')
        assert result == ''

    def test_unknown_returns_empty_string(self):
        monitor = Monitor()
        result = monitor.status_to_sound('BOGUS_STATUS')
        assert result == ''


class TestServerStatusThread:
    """Tests for server_status_thread_on with mocked threading"""

    @patch('yojenkins.monitor.monitor.threading.Thread')
    def test_server_status_thread_on_starts_thread(self, mock_thread_cls):
        monitor = Monitor()
        mock_thread_instance = MagicMock()
        mock_thread_cls.return_value = mock_thread_instance

        result = monitor.server_status_thread_on(monitor_interval=5.0)

        assert result is True
        mock_thread_cls.assert_called_once()
        mock_thread_instance.start.assert_called_once()

    @patch('yojenkins.monitor.monitor.threading.Thread')
    def test_server_status_thread_on_failure_returns_false(self, mock_thread_cls):
        monitor = Monitor()
        mock_thread_cls.side_effect = RuntimeError('thread error')

        result = monitor.server_status_thread_on()

        assert result is False


class TestPlaySoundThreadOn:
    """Tests for play_sound_thread_on with mocked threading"""

    @patch('yojenkins.monitor.monitor.threading.Thread')
    def test_play_sound_starts_thread(self, mock_thread_cls):
        monitor = Monitor()
        mock_thread_instance = MagicMock()
        mock_thread_cls.return_value = mock_thread_instance

        result = monitor.play_sound_thread_on('/fake/path/sound.wav')

        assert result is True
        mock_thread_instance.start.assert_called_once()

    @patch('yojenkins.monitor.monitor.threading.Thread')
    def test_play_sound_failure_returns_false(self, mock_thread_cls):
        monitor = Monitor()
        mock_thread_cls.side_effect = RuntimeError('thread error')

        result = monitor.play_sound_thread_on('/fake/path/sound.wav')

        assert result is False


class TestBasicScreenSetup:
    """Tests for Monitor.basic_screen_setup"""

    @patch('yojenkins.monitor.monitor.mu.load_curses_colors_decor')
    @patch('yojenkins.monitor.monitor.curses')
    def test_basic_screen_setup_halfdelay_true(self, mock_curses, mock_load_colors):
        mock_load_colors.return_value = ({'normal': 1}, {'bold': 2})
        monitor = Monitor()
        monitor.basic_screen_setup(halfdelay=True)

        mock_curses.curs_set.assert_called_once_with(0)
        mock_curses.noecho.assert_called_once()
        mock_curses.nonl.assert_called_once()
        mock_curses.halfdelay.assert_called_once_with(monitor.halfdelay_screen_refresh)
        assert monitor.color == {'normal': 1}
        assert monitor.decor == {'bold': 2}

    @patch('yojenkins.monitor.monitor.mu.load_curses_colors_decor')
    @patch('yojenkins.monitor.monitor.curses')
    def test_basic_screen_setup_halfdelay_false(self, mock_curses, mock_load_colors):
        mock_load_colors.return_value = ({'normal': 1}, {'bold': 2})
        monitor = Monitor()
        monitor.basic_screen_setup(halfdelay=False)

        mock_curses.halfdelay.assert_called_once_with(255)


class TestCheckTerminalSize:
    """Tests for Monitor.check_terminal_size"""

    @patch('yojenkins.monitor.monitor.mu.load_keys')
    @patch('yojenkins.monitor.monitor.mu.get_center_x', return_value=10)
    def test_terminal_size_good(self, mock_center_x, mock_load_keys):
        monitor = Monitor()
        monitor.color = {'grey-light': 1}
        monitor.decor = {'bold': 2}
        monitor.height_limit = 35
        monitor.width_limit = 66

        mock_scr = MagicMock()
        mock_scr.getmaxyx.return_value = (50, 100)

        monitor.check_terminal_size(mock_scr)
        assert monitor.terminal_size_good is True

    @patch('yojenkins.monitor.monitor.mu.load_keys')
    @patch('yojenkins.monitor.monitor.mu.get_center_x', return_value=10)
    def test_terminal_size_too_small_height(self, mock_center_x, mock_load_keys):
        monitor = Monitor()
        monitor.color = {'grey-light': 1}
        monitor.decor = {'bold': 2}
        monitor.height_limit = 35
        monitor.width_limit = 66

        mock_scr = MagicMock()
        # First call: too small; second call inside while: large enough
        mock_scr.getmaxyx.side_effect = [(20, 100), (50, 100)]
        mock_scr.getch.return_value = -1  # no key pressed

        mock_load_keys.return_value = {'QUIT': (27, ord('q'), ord('Q'))}

        monitor.check_terminal_size(mock_scr)
        assert monitor.terminal_size_good is True

    @patch('yojenkins.monitor.monitor.mu.load_keys')
    @patch('yojenkins.monitor.monitor.mu.get_center_x', return_value=10)
    def test_terminal_size_too_small_width(self, mock_center_x, mock_load_keys):
        monitor = Monitor()
        monitor.color = {'grey-light': 1}
        monitor.decor = {'bold': 2}
        monitor.height_limit = 35
        monitor.width_limit = 66

        mock_scr = MagicMock()
        # First call: too small width; second call: big enough
        mock_scr.getmaxyx.side_effect = [(50, 30), (50, 100)]
        mock_scr.getch.return_value = -1

        mock_load_keys.return_value = {'QUIT': (27, ord('q'), ord('Q'))}

        monitor.check_terminal_size(mock_scr)
        assert monitor.terminal_size_good is True

    @patch('yojenkins.monitor.monitor.mu.load_keys')
    @patch('yojenkins.monitor.monitor.mu.get_center_x', return_value=10)
    def test_terminal_size_quit_key_exits(self, mock_center_x, mock_load_keys):
        monitor = Monitor()
        monitor.color = {'grey-light': 1}
        monitor.decor = {'bold': 2}
        monitor.height_limit = 35
        monitor.width_limit = 66

        mock_scr = MagicMock()
        mock_scr.getmaxyx.return_value = (20, 30)  # always too small
        mock_scr.getch.return_value = 27  # ESC key

        mock_load_keys.return_value = {'QUIT': (27, ord('q'), ord('Q'))}

        with pytest.raises(SystemExit):
            monitor.check_terminal_size(mock_scr)
        assert monitor.all_threads_enabled is False

    @patch('yojenkins.monitor.monitor.mu.load_keys')
    @patch('yojenkins.monitor.monitor.mu.get_center_x', return_value=10)
    def test_terminal_size_render_failure_exits(self, mock_center_x, mock_load_keys):
        monitor = Monitor()
        monitor.color = {'grey-light': 1}
        monitor.decor = {'bold': 2}
        monitor.height_limit = 35
        monitor.width_limit = 66

        mock_scr = MagicMock()
        mock_scr.getmaxyx.return_value = (20, 30)
        mock_scr.getch.return_value = -1
        mock_scr.addstr.side_effect = Exception('too small')

        mock_load_keys.return_value = {'QUIT': (27, ord('q'), ord('Q'))}

        with pytest.raises(SystemExit):
            monitor.check_terminal_size(mock_scr)


class TestMonitorDestructor:
    """Tests for Monitor.__del__"""

    def test_destructor_calls_all_threads_off(self):
        monitor = Monitor()
        monitor.all_threads_enabled = True
        monitor.__del__()
        assert monitor.all_threads_enabled is False


class TestStatusToColorParametrized:
    """Additional parametrized tests for status_to_color"""

    @pytest.mark.parametrize(
        'status,expected_color',
        [
            ('RUNNING', 'normal'),
            ('IN_PROGRESS', 'normal'),
            ('SUCCEEDED', 'green'),
            ('FAILED', 'red'),
            ('FAIL', 'red'),
            ('QUEUED', 'normal'),
            ('UNSTABLE', 'orange'),
            ('PAUSED_PENDING_INPUT', 'cyan'),
            ('NOT_EXECUTED', 'grey-dark'),
            ('NOT_RUN', 'grey-dark'),
        ],
    )
    def test_status_color_mapping(self, status, expected_color):
        monitor = Monitor()
        assert monitor.status_to_color(status) == expected_color


class TestStatusToSoundParametrized:
    """Additional parametrized tests for status_to_sound"""

    @pytest.mark.parametrize(
        'status,expected_contains',
        [
            ('SUCCESS', 'positive'),
            ('FAILURE', 'negative'),
            ('ABORTED', 'negative'),
            ('UNSTABLE', 'negative'),
            ('PAUSED_PENDING_INPUT', 'positive'),
        ],
    )
    def test_status_sound_mapping(self, status, expected_contains):
        monitor = Monitor()
        result = monitor.status_to_sound(status)
        assert expected_contains in result

    @pytest.mark.parametrize('status', ['RUNNING', 'QUEUED', 'NOT_FOUND', 'NOT_EXECUTED'])
    def test_status_sound_empty(self, status):
        monitor = Monitor()
        result = monitor.status_to_sound(status)
        assert result == ''


class TestTempMessageBox:
    """Tests for show_temp_message / get_temp_message"""

    def test_show_and_get_within_duration(self):
        monitor = Monitor()
        monitor.show_temp_message(['Hello', 'World'], duration=5.0)
        result = monitor.get_temp_message()
        assert result == ['Hello', 'World']

    def test_message_expires_after_duration(self):
        monitor = Monitor()
        monitor.show_temp_message(['Expired'], duration=0.5)
        # Manually set start time in the past
        monitor._temp_message_start = time() - 1.0
        result = monitor.get_temp_message()
        assert result == []
        assert monitor._temp_message_active is False

    def test_get_temp_message_empty_when_inactive(self):
        monitor = Monitor()
        result = monitor.get_temp_message()
        assert result == []

    def test_default_duration_uses_class_attribute(self):
        monitor = Monitor()
        monitor.message_box_temp_duration = 2
        monitor.show_temp_message(['Test'])
        assert monitor._temp_message_duration == 2

    def test_custom_duration_overrides_default(self):
        monitor = Monitor()
        monitor.message_box_temp_duration = 2
        monitor.show_temp_message(['Test'], duration=10.0)
        assert monitor._temp_message_duration == 10.0

    def test_new_message_replaces_old(self):
        monitor = Monitor()
        monitor.show_temp_message(['Old'], duration=5.0)
        monitor.show_temp_message(['New'], duration=5.0)
        assert monitor.get_temp_message() == ['New']


class TestServerStatusThreadLogic:
    """Tests for __thread_server_status data collection logic"""

    def test_thread_server_status_collects_data(self):
        monitor = Monitor()
        monitor.rest = MagicMock()
        monitor.auth = MagicMock()
        monitor.rest.is_reachable.return_value = True
        monitor.auth.verify.return_value = True

        # Run the thread method directly but make it stop after one iteration
        def stop_after_first(*args, **kwargs):
            monitor.all_threads_enabled = False
            return True

        monitor.rest.is_reachable.side_effect = stop_after_first

        # Access the name-mangled private method
        monitor._Monitor__thread_server_status(monitor_interval=0.0)

        assert monitor.server_status_data['reachable'] is True
        assert monitor.server_interaction is True

    def test_thread_server_status_paused_skips_collection(self):
        monitor = Monitor()
        monitor.rest = MagicMock()
        monitor.auth = MagicMock()
        monitor.paused = True

        def stop_on_sleep(x):
            monitor.all_threads_enabled = False

        with patch('yojenkins.monitor.monitor.sleep', side_effect=stop_on_sleep):
            monitor._Monitor__thread_server_status(monitor_interval=0.0)

        monitor.rest.is_reachable.assert_not_called()
        monitor.auth.verify.assert_not_called()
