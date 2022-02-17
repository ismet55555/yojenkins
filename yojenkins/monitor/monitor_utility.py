"""Utility functions for monitors"""

import curses
import logging
from math import floor
from typing import Tuple, Type

# Getting the logger reference
logger = logging.getLogger()


def logging_console(enabled: bool = True) -> None:
    """
    Disable logger standard out in terminal, only keep log file output

    Args:
        None

    Returns:
        None
    """
    # FIXME: Instead of blindly indexing a handler, find/match the right one

    # [ handler.setLevel(logging.FATAL) for handler in logger.handlers if isinstance(handler, logging.StreamHandler) ]
    # for handler in logger.handlers:
    #     if isinstance(handler, logging.StreamHandler):
    #         handler.setLevel(logging.FATAL)

    logger.debug('Logging handler status:')
    for i, handler in enumerate(logger.handlers):
        logger.debug(f'    {i + 1}. {type(handler)} - Logging Level: {logging.getLevelName(handler.level)}')

    if enabled:
        logger.debug('*******************************************')
        logger.debug('***  LOGGING TO CONSOLE OUTPUT ENABLED  ***')
        logger.debug('*******************************************')
        stream_handler = logger.handlers[1]
        stream_handler.setLevel(logging.DEBUG)
    else:
        logger.debug('**********************************************************************')
        logger.debug('***  LOGGING TO CONSOLE OUTPUT DISABLED. ONLY LOGGING TO LOG FILE  ***')
        logger.debug('**********************************************************************')
        stream_handler = logger.handlers[1]
        stream_handler.setLevel(logging.FATAL)

    logger.debug('Logging handler status:')
    for i, handler in enumerate(logger.handlers):
        logger.debug(f'    {i + 1}. {type(handler)} - Logging Level: {logging.getLevelName(handler.level)}')


def load_curses_colors_decor() -> Tuple[dict, dict]:
    """
    Load curses colors and decorations and load them in a usable
    dictionary for reference.

    Usage: self.colors("green")
        self.decor("blink")
        scr.addstr(y, x, "hello", self.color['blue'] | self.decor['bold'])

    Args:
        None

    Returns:
        color (dict): Curses color references
        decor (dict): Curses decoration/style references
    """
    # Start colors in curses
    curses.start_color()

    # Default background color
    bkgrd_color = 0

    # Defining colors [foreground/font, background]
    color_definition = {
        'normal': [curses.COLOR_WHITE, bkgrd_color],  # FIXME: Rename to "normal" to match decor
        'red': [curses.COLOR_RED, bkgrd_color],
        'green': [curses.COLOR_GREEN, bkgrd_color],
        'blue': [curses.COLOR_BLUE, bkgrd_color],
        'yellow': [curses.COLOR_YELLOW, bkgrd_color],
        'orange': [209, bkgrd_color],
        'cyan': [curses.COLOR_CYAN, bkgrd_color],
        'magenta': [curses.COLOR_MAGENTA, bkgrd_color],
        'grey-dark': [240, bkgrd_color],
        'grey-light': [248, bkgrd_color],
        'black-white': [curses.COLOR_BLACK, curses.COLOR_WHITE],
        'white-red': [curses.COLOR_WHITE, curses.COLOR_RED]
    }

    # If terminal does not support colors, reset everything to white
    if not curses.has_colors() or not curses.can_change_color():
        for color in color_definition:
            color_definition[color] = [curses.COLOR_WHITE, bkgrd_color]

    # Initiating curses color and saving for quick reference
    color = {}
    for index, (key, value) in enumerate(color_definition.items()):
        try:
            curses.init_pair(index + 1, value[0], value[1])
        except:
            curses.init_pair(index + 1, 0, 0)
        color[key] = curses.color_pair(index + 1)

    # Defining font decorations
    decoration_definition = {
        'normal': curses.A_NORMAL,  # Normal display (no highlight)
        'standout': curses.A_STANDOUT,  # Best highlighting mode of the terminal
        'underline': curses.A_UNDERLINE,  # Underlining
        'reverse': curses.A_REVERSE,  # Reverse video
        'blink': curses.A_BLINK,  # Blinking
        'dim': curses.A_DIM,  # Half bright
        'bold': curses.A_BOLD,  # Extra bright or bold
        'protect': curses.A_PROTECT,  # Protected mode
        'invisible': curses.A_INVIS,  # Invisible or blank mode
        'alt-char': curses.A_ALTCHARSET,  # Alternate character set
        'char':
            curses.A_CHARTEXT  # Bit-mask to extract a character
    }

    # Initiating curses color and saving for quick reference
    decor = {}
    for key, value in decoration_definition.items():
        decor[key] = value

    return color, decor


def load_keys() -> dict:
    """
    Load all keyboard keys available to user in program

    Usage: ui_keys['DOWN']

    Args:
        None
    Returns:
        ui_keys (dict): Dictionary of references to curses keys
    """
    ui_keys = {
        "ABORT": (ord('a'), ord('A')),
        "BUILD": (ord('b'), ord('B')),
        "DOWN": (curses.KEY_DOWN, ord('j')),
        "ENTER": (curses.KEY_ENTER, ord('\n'), ord('\r')),
        "HELP": (ord('h'), ord('H')),
        "LEFT": (curses.KEY_LEFT, ord('h')),
        "LOGS": (ord('l'), ord('L')),
        "OPEN": (ord('o'), ord('O')),
        "PAUSE": (ord('p'), ord('P')),
        "QUIT": (27, ord('q'), ord('Q')),
        "RESUME": (ord('r'), ord('R')),
        "RIGHT": (curses.KEY_RIGHT, ord('l')),
        "SOUND": (ord('s'), ord('S')),
        "SPACE": (32, ord(' ')),
        "UP": (curses.KEY_UP, ord('k'))
    }
    return ui_keys


def get_center_x(scr, line: str) -> int:
    """
    Find the horizontal center position of the given text line

    Args:
        display_width (int) : The character width of the screen/space/display
        line (int)          : Line of text
    Returns:
        (int): Horizontal character number
    """
    # Getting the screen height and width
    _, term_width = scr.getmaxyx()
    return term_width // 2 - len(line) // 2


def get_center_y(scr) -> int:
    """
    Find the vertical center position of given screen/space/display

    Args:
        display_width (int) : The character height of the screen/space/display
    Returns:
        (int): Vertical character number
    """
    # Getting the screen height and width
    term_height, _ = scr.getmaxyx()
    return term_height // 2


def truncate_text(text: str, length_limit: int) -> str:
    """
    Truncating/shortening of text given a length limit.
    Will add "..." to truncated text.

    Args:
        text (str)         : The character height of the screen/space/display
        length_limit (int) : Length limit of the text
    Returns:
        truncated_text (str): The truncated line of text
    """
    truncated_text = text
    if len(text) >= length_limit - 3:
        truncated_text = text[0:length_limit - 3] + '...'

    return truncated_text


def get_message_box_size(term_height: int, term_width: int, message_lines: list) -> Tuple[int, int, int, int]:
    """
    Given a message box list with each item being a message box line/row,
    this method find the right size and position of the message box for
    the given terminal size

    Args:
        term_height (int)    : Number of rows/lines in terminal
        term_width (int)     : Number of columns in terminal
        message_lines (list) : Lines of text in each list item
    Returns:
        box_height (int) : Height of message box (rows/lines)
        box_width (int)  : Width of message box (columns)
        box_y (int)      : Vertical position of box in terminal
        box_x (int)      : Horizontal position of box in terminal
    """
    box_height = len(message_lines) + 4
    box_width = int(term_width / 1.5)  # Alternative: len(max(message_lines, key=len)) + 12
    box_y = term_height // 2 - box_height // 2
    box_x = term_width // 2 - box_width // 2

    return box_height, box_width, box_y, box_x


def get_progress_bar(exam_progress: float, bar_char_width=60, bar_char_full='|', bar_char_empty='-') -> str:
    """
    Make a progress bar with specified parameters

    Args:
        exam_progress (float) : Exam progress from 0 to 1 (ie. 0.45 is 45%)
        bar_char_width (int)  : Total width of progress bar, columns of text
        bar_char_full (str)   : Symbol for filled
        bar_char_empty (str)  : Symbol for empty
    Returns:
        (str) : Progress bar as text
    """
    # TODO: Different colors for different parts of the progress bar somehow

    progress_str = []
    for i in range(bar_char_width):

        if i <= exam_progress * bar_char_width:
            progress_str.append(bar_char_full)
        else:
            progress_str.append(bar_char_empty)

    progress_str = "".join(progress_str)
    return progress_str


def draw_screen_border(scr, color: list) -> None:
    """
    Draw a border around entire terminal screen with specified color

    Parameters:
        scr (obj)   : Handle for curses terminal screen handle
        color (list): Foreground and background color (ie. [250, 0])
    Returns:
        None
    """
    scr.attron(color)
    scr.border(0)
    scr.attroff(color)


def draw_horizontal_header(scr,
                           row: int,
                           col: int,
                           width: int,
                           symbol: str = '-',
                           text: str = '',
                           color: list = []) -> None:
    """
    Draw a horizontal header on the screen
    Example:  `---------  HELLO  -------------`

    Args:
        scr    : Handle for curses terminal screen handle
        col    : What character start the seperator along the horizontal
        row    : The line/row number from top of the screen
        width  : Total width of the header
        symbol : (Optional) The symbol used on each side of the text (default: `-`)
        text   : (Optional) Text in center of seperator. Must be smaller than `width` (default: None)
        color  : (Optional) Foreground and background color (ie. `[250, 0]`)

    Returns:
        None
    """
    # Getting the screen height and width
    term_height, term_width = scr.getmaxyx()

    # Check text size and header width size
    if len(text) > width - 2 or width > term_width:
        return

    # Check if drawing within boundaries and if text is smaller than the width and some padding
    if row < term_height - 2 and row > 1:
        if text:
            # Get one half of the seperator
            seperator_half = symbol * (floor((width - len(text)) / 2) - 2)
            line = seperator_half + '  ' + text + '  ' + seperator_half
        else:
            line = symbol * width
        scr.addstr(row, col, line, color)


def draw_horizontal_seperator(scr, row: int, color: list = [], symbol: str = '-', text: str = '') -> None:
    """
    Draw a horizontal line accross the terminal screen at specified height
    and with specified color

    Args:
        scr (obj)   : Handle for curses terminal screen handle
        row (int)   : The line/row number from top of the screen
        color       : (Optional) Foreground and background color (ie. [250, 0])
        symbol      : (Optional) The symbol used as the seperator
        text        : (Optional) Text in center of seperator
    Returns:
        None
    """
    # Getting the screen height and width
    term_height, term_width = scr.getmaxyx()

    # Check if drawing within boundaries
    if row < term_height - 2 and row > 1:
        if text:
            # Get one half of the seperator
            seperator_half = symbol * (floor((term_width - len(text)) / 2) - 2)
            line = seperator_half + '  ' + text + '  ' + seperator_half
        else:
            line = symbol * term_width
        scr.addstr(row, 1, line, color)


def draw_vertical_seperator(scr, x: int, color: list) -> None:
    """
    Draw a vertical line accross the terminal screen at specified character
    column and with specified color

    Args:
        scr (obj)   : Handle for curses terminal screen handle
        x (int)     : The column number from left of the screen
        color (list): Foreground and background color (ie. [250, 0])
    Returns:
        None
    """
    # TODO: Currently unused but may come in handy


def draw_message_box(scr, message_lines: list, justify: str = 'center') -> None:
    """
    Draw a message box in the middle of the terminal screen

    Args:
        scr (obj)            : Handle for curses terminal screen handle
        message_lines (list) : Lines of text in each list item
        justify              : Text justification. `center`, `left`
    Returns:
        None
    """
    term_height, term_width = scr.getmaxyx()

    # Getting the message box size and position and creating the message box
    height, width, y, x = get_message_box_size(term_height, term_width, message_lines)
    message_box = curses.newwin(height, width, y, x)
    message_box.box()
    message_box.border()

    # Find the longest line of text
    max_line_len = len(max(message_lines, key=len))

    for l, line in enumerate(message_lines):
        # Getting the horizontal starting point
        if justify == 'center':
            x = width // 2 - len(line) // 2
        elif justify == 'left':
            x = width // 2 - max_line_len // 2

        # Add text each line to box (Text is relative to box -> y, x)
        y = l + 2
        message_box.addstr(y, x, line)

    # Refresh the message box
    message_box.refresh()


def draw_text(scr,
              text: str = None,
              y: int = None,
              x: int = None,
              color: list = None,
              decor: int = None,
              center_y: bool = False,
              center_x: bool = False) -> None:
    """
    Draw a text on screen.
    This is a wrapper for `addstr`

    Args:
        scr      : Handle for curses terminal screen handle
        text     : Lines of text in each list item
        y        : Starting character row in terminal
        x        : Starting character column in terminal
        color    : Color of text (0 - 255)
        decor    : Decoration of text
        center_y : Vertically center the text on screen
        center_x : Horizontally center the text on screen
    Returns:
        None
    """
    # Set to default color and decor if not passed
    if not color or not decor:
        color_preset, decor_preset = load_curses_colors_decor()
    color = color_preset['normal'] if not color else color
    decor = decor_preset['normal'] if not decor else decor

    # Check for NoneType
    if text == None:
        text = 'N/A'

    # Get center of screen if specified
    if center_x and not x:
        x = get_center_x(scr, text)
    if center_y and not y:
        y = get_center_y(scr)

    # Draw
    scr.addstr(y, x, text, color | decor)

    # Update but don't write yet
    scr.noutrefresh()


def paint_background(scr, color: int = 0) -> None:
    """
    Paint the background of the terminal window with one color

    Args:
        scr   : Handle for curses terminal screen handle
        color : Color index (0 - 255) (default: 0 - black)
    Returns:
        None
    """
    # Getting the screen height and width
    term_height, term_width = scr.getmaxyx()

    # Paint it
    for start_y in range(1, term_height - 1):
        line = term_width * ' '
        scr.addstr(start_y, 1, line, color)

    # Update but don't write yet
    scr.noutrefresh()
