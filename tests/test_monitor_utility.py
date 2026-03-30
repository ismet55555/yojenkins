"""Tests for yojenkins/monitor/monitor_utility.py"""

import logging
from unittest.mock import MagicMock, patch


class TestTruncateText:
    """Tests for truncate_text() pure function"""

    def test_short_text_unchanged(self):
        from yojenkins.monitor.monitor_utility import truncate_text

        result = truncate_text('hello', 20)
        assert result == 'hello'

    def test_text_at_limit_gets_truncated(self):
        from yojenkins.monitor.monitor_utility import truncate_text

        result = truncate_text('abcdefghij', 10)
        assert result.endswith('...')
        assert len(result) <= 10

    def test_text_over_limit_gets_truncated(self):
        from yojenkins.monitor.monitor_utility import truncate_text

        result = truncate_text('a' * 50, 20)
        assert result.endswith('...')
        assert len(result) == 20

    def test_empty_text(self):
        from yojenkins.monitor.monitor_utility import truncate_text

        result = truncate_text('', 10)
        assert result == ''

    def test_text_exactly_below_limit(self):
        from yojenkins.monitor.monitor_utility import truncate_text

        # len('abcdef') = 6, limit - 3 = 7, so 6 < 7 => no truncation
        result = truncate_text('abcdef', 10)
        assert result == 'abcdef'


class TestGetMessageBoxSize:
    """Tests for get_message_box_size() pure function"""

    def test_basic_message_box(self):
        from yojenkins.monitor.monitor_utility import get_message_box_size

        lines = ['Hello', 'World']
        height, width, y, x = get_message_box_size(40, 80, lines)
        assert height == len(lines) + 4
        assert width == int(80 / 1.5)
        assert y == 40 // 2 - height // 2
        assert x == 80 // 2 - width // 2

    def test_single_line_message_box(self):
        from yojenkins.monitor.monitor_utility import get_message_box_size

        lines = ['Only one line']
        height, width, y, x = get_message_box_size(30, 100, lines)
        assert height == 5  # 1 + 4

    def test_many_lines_message_box(self):
        from yojenkins.monitor.monitor_utility import get_message_box_size

        lines = [f'Line {i}' for i in range(10)]
        height, width, y, x = get_message_box_size(50, 120, lines)
        assert height == 14  # 10 + 4

    def test_box_centered_vertically(self):
        from yojenkins.monitor.monitor_utility import get_message_box_size

        lines = ['A', 'B']
        height, width, y, x = get_message_box_size(40, 80, lines)
        # y should be roughly centered
        assert y == 40 // 2 - height // 2

    def test_box_centered_horizontally(self):
        from yojenkins.monitor.monitor_utility import get_message_box_size

        lines = ['A']
        height, width, y, x = get_message_box_size(40, 80, lines)
        assert x == 80 // 2 - width // 2


class TestGetProgressBar:
    """Tests for get_progress_bar() pure function"""

    def test_zero_progress(self):
        from yojenkins.monitor.monitor_utility import get_progress_bar

        result = get_progress_bar(0.0, bar_char_width=10)
        # At 0%, only position 0 is filled (i <= 0 * 10 means i <= 0, so index 0)
        assert result[1:] == '-' * 9

    def test_full_progress(self):
        from yojenkins.monitor.monitor_utility import get_progress_bar

        result = get_progress_bar(1.0, bar_char_width=10)
        assert result == '|' * 10

    def test_half_progress(self):
        from yojenkins.monitor.monitor_utility import get_progress_bar

        result = get_progress_bar(0.5, bar_char_width=10)
        assert len(result) == 10
        # Should have some filled and some empty
        assert '|' in result
        assert '-' in result

    def test_custom_chars(self):
        from yojenkins.monitor.monitor_utility import get_progress_bar

        result = get_progress_bar(1.0, bar_char_width=5, bar_char_full='#', bar_char_empty='.')
        assert result == '#####'

    def test_default_width(self):
        from yojenkins.monitor.monitor_utility import get_progress_bar

        result = get_progress_bar(0.5)
        assert len(result) == 60


class TestLoadKeys:
    """Tests for load_keys() -- returns key mappings (uses curses constants but they are ints)"""

    def test_returns_dict(self):
        from yojenkins.monitor.monitor_utility import load_keys

        keys = load_keys()
        assert isinstance(keys, dict)

    def test_contains_expected_keys(self):
        from yojenkins.monitor.monitor_utility import load_keys

        keys = load_keys()
        expected = ['QUIT', 'HELP', 'PAUSE', 'RESUME', 'ABORT', 'BUILD', 'OPEN', 'SOUND', 'LOGS']
        for key in expected:
            assert key in keys, f'Missing key: {key}'

    def test_quit_contains_escape_and_q(self):
        from yojenkins.monitor.monitor_utility import load_keys

        keys = load_keys()
        # ESC = 27, q = 113, Q = 81
        assert 27 in keys['QUIT']
        assert ord('q') in keys['QUIT']
        assert ord('Q') in keys['QUIT']

    def test_all_keys_are_tuples(self):
        from yojenkins.monitor.monitor_utility import load_keys

        keys = load_keys()
        for key_name, key_values in keys.items():
            assert isinstance(key_values, tuple), f'{key_name} should be a tuple'

    def test_additional_keys_present(self):
        from yojenkins.monitor.monitor_utility import load_keys

        keys = load_keys()
        for key in ['UP', 'DOWN', 'LEFT', 'RIGHT', 'ENTER', 'SPACE']:
            assert key in keys, f'Missing key: {key}'


class TestGetCenterX:
    """Tests for get_center_x() function"""

    def test_center_x_basic(self):
        from yojenkins.monitor.monitor_utility import get_center_x

        mock_scr = MagicMock()
        mock_scr.getmaxyx.return_value = (40, 80)
        result = get_center_x(mock_scr, 'hello')
        # 80 // 2 - 5 // 2 = 40 - 2 = 38
        assert result == 38

    def test_center_x_empty_string(self):
        from yojenkins.monitor.monitor_utility import get_center_x

        mock_scr = MagicMock()
        mock_scr.getmaxyx.return_value = (40, 80)
        result = get_center_x(mock_scr, '')
        assert result == 40

    def test_center_x_full_width(self):
        from yojenkins.monitor.monitor_utility import get_center_x

        mock_scr = MagicMock()
        mock_scr.getmaxyx.return_value = (40, 80)
        result = get_center_x(mock_scr, 'x' * 80)
        assert result == 0


class TestGetCenterY:
    """Tests for get_center_y() function"""

    def test_center_y_basic(self):
        from yojenkins.monitor.monitor_utility import get_center_y

        mock_scr = MagicMock()
        mock_scr.getmaxyx.return_value = (40, 80)
        result = get_center_y(mock_scr)
        assert result == 20

    def test_center_y_odd_height(self):
        from yojenkins.monitor.monitor_utility import get_center_y

        mock_scr = MagicMock()
        mock_scr.getmaxyx.return_value = (41, 80)
        result = get_center_y(mock_scr)
        assert result == 20


class TestDrawScreenBorder:
    """Tests for draw_screen_border()"""

    def test_draw_screen_border_calls_attron_border_attroff(self):
        from yojenkins.monitor.monitor_utility import draw_screen_border

        mock_scr = MagicMock()
        color = 42
        draw_screen_border(mock_scr, color)
        mock_scr.attron.assert_called_once_with(color)
        mock_scr.border.assert_called_once_with(0)
        mock_scr.attroff.assert_called_once_with(color)


class TestDrawHorizontalSeperator:
    """Tests for draw_horizontal_seperator()"""

    def test_draws_line_within_bounds(self):
        from yojenkins.monitor.monitor_utility import draw_horizontal_seperator

        mock_scr = MagicMock()
        mock_scr.getmaxyx.return_value = (40, 80)
        draw_horizontal_seperator(mock_scr, 10, color=1)
        mock_scr.addstr.assert_called_once()
        args = mock_scr.addstr.call_args
        assert args[0][0] == 10  # row
        assert args[0][1] == 1   # col
        assert len(args[0][2]) == 80  # full width line

    def test_does_not_draw_at_boundary_row(self):
        from yojenkins.monitor.monitor_utility import draw_horizontal_seperator

        mock_scr = MagicMock()
        mock_scr.getmaxyx.return_value = (40, 80)
        # row 38 is term_height - 2, should not draw
        draw_horizontal_seperator(mock_scr, 38)
        mock_scr.addstr.assert_not_called()

    def test_does_not_draw_at_row_1(self):
        from yojenkins.monitor.monitor_utility import draw_horizontal_seperator

        mock_scr = MagicMock()
        mock_scr.getmaxyx.return_value = (40, 80)
        draw_horizontal_seperator(mock_scr, 1)
        mock_scr.addstr.assert_not_called()

    def test_draws_with_text(self):
        from yojenkins.monitor.monitor_utility import draw_horizontal_seperator

        mock_scr = MagicMock()
        mock_scr.getmaxyx.return_value = (40, 80)
        draw_horizontal_seperator(mock_scr, 10, text='HELLO')
        mock_scr.addstr.assert_called_once()
        line = mock_scr.addstr.call_args[0][2]
        assert 'HELLO' in line

    def test_draws_with_custom_symbol(self):
        from yojenkins.monitor.monitor_utility import draw_horizontal_seperator

        mock_scr = MagicMock()
        mock_scr.getmaxyx.return_value = (40, 80)
        draw_horizontal_seperator(mock_scr, 10, symbol='=')
        line = mock_scr.addstr.call_args[0][2]
        assert '=' in line


class TestDrawHorizontalHeader:
    """Tests for draw_horizontal_header()"""

    def test_draws_header_with_text(self):
        from yojenkins.monitor.monitor_utility import draw_horizontal_header

        mock_scr = MagicMock()
        mock_scr.getmaxyx.return_value = (40, 80)
        draw_horizontal_header(mock_scr, 10, 3, 60, '-', 'INFO', color=1)
        mock_scr.addstr.assert_called_once()
        line = mock_scr.addstr.call_args[0][2]
        assert 'INFO' in line

    def test_draws_header_without_text(self):
        from yojenkins.monitor.monitor_utility import draw_horizontal_header

        mock_scr = MagicMock()
        mock_scr.getmaxyx.return_value = (40, 80)
        draw_horizontal_header(mock_scr, 10, 3, 60, '-', '', color=1)
        mock_scr.addstr.assert_called_once()
        line = mock_scr.addstr.call_args[0][2]
        assert line == '-' * 60

    def test_does_not_draw_outside_bounds(self):
        from yojenkins.monitor.monitor_utility import draw_horizontal_header

        mock_scr = MagicMock()
        mock_scr.getmaxyx.return_value = (40, 80)
        # row at boundary
        draw_horizontal_header(mock_scr, 38, 3, 60)
        mock_scr.addstr.assert_not_called()

    def test_does_not_draw_when_text_too_wide(self):
        from yojenkins.monitor.monitor_utility import draw_horizontal_header

        mock_scr = MagicMock()
        mock_scr.getmaxyx.return_value = (40, 80)
        draw_horizontal_header(mock_scr, 10, 3, 10, text='THIS IS TOO LONG')
        mock_scr.addstr.assert_not_called()

    def test_does_not_draw_when_width_exceeds_terminal(self):
        from yojenkins.monitor.monitor_utility import draw_horizontal_header

        mock_scr = MagicMock()
        mock_scr.getmaxyx.return_value = (40, 80)
        draw_horizontal_header(mock_scr, 10, 3, 100)
        mock_scr.addstr.assert_not_called()


class TestDrawMessageBox:
    """Tests for draw_message_box()"""

    @patch('yojenkins.monitor.monitor_utility.curses')
    def test_creates_newwin_and_refreshes(self, mock_curses):
        from yojenkins.monitor.monitor_utility import draw_message_box

        mock_scr = MagicMock()
        mock_scr.getmaxyx.return_value = (40, 80)
        mock_box = MagicMock()
        mock_curses.newwin.return_value = mock_box

        draw_message_box(mock_scr, ['Hello', 'World'])

        mock_curses.newwin.assert_called_once()
        mock_box.box.assert_called_once()
        mock_box.border.assert_called_once()
        mock_box.refresh.assert_called_once()

    @patch('yojenkins.monitor.monitor_utility.curses')
    def test_adds_text_lines(self, mock_curses):
        from yojenkins.monitor.monitor_utility import draw_message_box

        mock_scr = MagicMock()
        mock_scr.getmaxyx.return_value = (40, 80)
        mock_box = MagicMock()
        mock_curses.newwin.return_value = mock_box

        lines = ['Line 1', 'Line 2', 'Line 3']
        draw_message_box(mock_scr, lines)

        assert mock_box.addstr.call_count == 3

    @patch('yojenkins.monitor.monitor_utility.curses')
    def test_left_justify(self, mock_curses):
        from yojenkins.monitor.monitor_utility import draw_message_box

        mock_scr = MagicMock()
        mock_scr.getmaxyx.return_value = (40, 80)
        mock_box = MagicMock()
        mock_curses.newwin.return_value = mock_box

        draw_message_box(mock_scr, ['Short', 'A longer line here'], justify='left')
        assert mock_box.addstr.call_count == 2


class TestDrawText:
    """Tests for draw_text()"""

    @patch('yojenkins.monitor.monitor_utility.load_curses_colors_decor')
    def test_draw_text_basic(self, mock_load_colors):
        from yojenkins.monitor.monitor_utility import draw_text

        mock_load_colors.return_value = (
            {'normal': 1, 'green': 2},
            {'normal': 0, 'bold': 1},
        )
        mock_scr = MagicMock()
        draw_text(mock_scr, 'hello', y=5, x=10, color=3, decor=1)
        mock_scr.addstr.assert_called_once_with(5, 10, 'hello', 3 | 1)
        mock_scr.noutrefresh.assert_called_once()

    @patch('yojenkins.monitor.monitor_utility.load_curses_colors_decor')
    def test_draw_text_none_becomes_na(self, mock_load_colors):
        from yojenkins.monitor.monitor_utility import draw_text

        mock_load_colors.return_value = (
            {'normal': 1},
            {'normal': 0},
        )
        mock_scr = MagicMock()
        draw_text(mock_scr, None, y=5, x=10, color=1, decor=1)
        assert mock_scr.addstr.call_args[0][2] == 'N/A'

    @patch('yojenkins.monitor.monitor_utility.load_curses_colors_decor')
    def test_draw_text_center_x(self, mock_load_colors):
        from yojenkins.monitor.monitor_utility import draw_text

        mock_load_colors.return_value = (
            {'normal': 1},
            {'normal': 0},
        )
        mock_scr = MagicMock()
        mock_scr.getmaxyx.return_value = (40, 80)
        draw_text(mock_scr, 'test', y=5, center_x=True)
        # x should be centered: 80//2 - 4//2 = 38
        assert mock_scr.addstr.call_args[0][1] == 38

    @patch('yojenkins.monitor.monitor_utility.load_curses_colors_decor')
    def test_draw_text_center_y(self, mock_load_colors):
        from yojenkins.monitor.monitor_utility import draw_text

        mock_load_colors.return_value = (
            {'normal': 1},
            {'normal': 0},
        )
        mock_scr = MagicMock()
        mock_scr.getmaxyx.return_value = (40, 80)
        draw_text(mock_scr, 'test', x=5, center_y=True)
        # y should be centered: 40//2 = 20
        assert mock_scr.addstr.call_args[0][0] == 20

    @patch('yojenkins.monitor.monitor_utility.load_curses_colors_decor')
    def test_draw_text_defaults_color_and_decor(self, mock_load_colors):
        from yojenkins.monitor.monitor_utility import draw_text

        mock_load_colors.return_value = (
            {'normal': 99},
            {'normal': 0},
        )
        mock_scr = MagicMock()
        # color=None and decor=None should trigger defaults
        draw_text(mock_scr, 'hi', y=1, x=1)
        assert mock_scr.addstr.call_args[0][3] == 99 | 0


class TestPaintBackground:
    """Tests for paint_background()"""

    def test_paints_all_interior_rows(self):
        from yojenkins.monitor.monitor_utility import paint_background

        mock_scr = MagicMock()
        mock_scr.getmaxyx.return_value = (10, 20)
        paint_background(mock_scr, color=5)
        # Should paint rows 1 through 8 (range(1, 9))
        assert mock_scr.addstr.call_count == 8
        mock_scr.noutrefresh.assert_called_once()

    def test_paint_default_color(self):
        from yojenkins.monitor.monitor_utility import paint_background

        mock_scr = MagicMock()
        mock_scr.getmaxyx.return_value = (5, 10)
        paint_background(mock_scr)
        # Default color is 0
        for c in mock_scr.addstr.call_args_list:
            assert c[0][2] == ' ' * 10
            assert c[0][3] == 0


class TestLoggingConsole:
    """Tests for logging_console()"""

    def test_logging_console_disable(self):
        from yojenkins.monitor.monitor_utility import logging_console

        # Set up logger with two handlers
        test_logger = logging.getLogger()
        original_handlers = test_logger.handlers[:]

        # Need at least 2 handlers for this function
        mock_handler_0 = logging.FileHandler('/dev/null')
        mock_handler_1 = logging.StreamHandler()
        mock_handler_1.setLevel(logging.DEBUG)

        test_logger.handlers = [mock_handler_0, mock_handler_1]
        try:
            logging_console(enabled=False)
            assert mock_handler_1.level == logging.FATAL
        finally:
            test_logger.handlers = original_handlers
            mock_handler_0.close()

    def test_logging_console_enable(self):
        from yojenkins.monitor.monitor_utility import logging_console

        test_logger = logging.getLogger()
        original_handlers = test_logger.handlers[:]

        mock_handler_0 = logging.FileHandler('/dev/null')
        mock_handler_1 = logging.StreamHandler()
        mock_handler_1.setLevel(logging.FATAL)

        test_logger.handlers = [mock_handler_0, mock_handler_1]
        try:
            logging_console(enabled=True)
            assert mock_handler_1.level == logging.DEBUG
        finally:
            test_logger.handlers = original_handlers
            mock_handler_0.close()


class TestLoadCursesColorsDecor:
    """Tests for load_curses_colors_decor()"""

    @patch('yojenkins.monitor.monitor_utility.curses')
    def test_returns_color_and_decor_dicts(self, mock_curses):
        from yojenkins.monitor.monitor_utility import load_curses_colors_decor

        mock_curses.has_colors.return_value = True
        mock_curses.can_change_color.return_value = True
        mock_curses.color_pair.side_effect = lambda x: x
        mock_curses.COLOR_WHITE = 7
        mock_curses.COLOR_RED = 1
        mock_curses.COLOR_GREEN = 2
        mock_curses.COLOR_BLUE = 4
        mock_curses.COLOR_YELLOW = 3
        mock_curses.COLOR_CYAN = 6
        mock_curses.COLOR_MAGENTA = 5
        mock_curses.COLOR_BLACK = 0
        mock_curses.A_NORMAL = 0
        mock_curses.A_STANDOUT = 1
        mock_curses.A_UNDERLINE = 2
        mock_curses.A_REVERSE = 4
        mock_curses.A_BLINK = 8
        mock_curses.A_DIM = 16
        mock_curses.A_BOLD = 32
        mock_curses.A_PROTECT = 64
        mock_curses.A_INVIS = 128
        mock_curses.A_ALTCHARSET = 256
        mock_curses.A_CHARTEXT = 512

        color, decor = load_curses_colors_decor()

        assert isinstance(color, dict)
        assert isinstance(decor, dict)
        assert 'normal' in color
        assert 'red' in color
        assert 'green' in color
        assert 'bold' in decor
        assert 'normal' in decor
        mock_curses.start_color.assert_called_once()

    @patch('yojenkins.monitor.monitor_utility.curses')
    def test_no_color_support_resets_to_white(self, mock_curses):
        from yojenkins.monitor.monitor_utility import load_curses_colors_decor

        mock_curses.has_colors.return_value = False
        mock_curses.can_change_color.return_value = False
        mock_curses.color_pair.side_effect = lambda x: x
        mock_curses.COLOR_WHITE = 7
        mock_curses.COLOR_RED = 1
        mock_curses.COLOR_GREEN = 2
        mock_curses.COLOR_BLUE = 4
        mock_curses.COLOR_YELLOW = 3
        mock_curses.COLOR_CYAN = 6
        mock_curses.COLOR_MAGENTA = 5
        mock_curses.COLOR_BLACK = 0
        mock_curses.A_NORMAL = 0
        mock_curses.A_STANDOUT = 1
        mock_curses.A_UNDERLINE = 2
        mock_curses.A_REVERSE = 4
        mock_curses.A_BLINK = 8
        mock_curses.A_DIM = 16
        mock_curses.A_BOLD = 32
        mock_curses.A_PROTECT = 64
        mock_curses.A_INVIS = 128
        mock_curses.A_ALTCHARSET = 256
        mock_curses.A_CHARTEXT = 512

        color, decor = load_curses_colors_decor()

        # All init_pair calls should use COLOR_WHITE (7) as foreground
        for c in mock_curses.init_pair.call_args_list:
            assert c[0][1] == 7  # COLOR_WHITE
