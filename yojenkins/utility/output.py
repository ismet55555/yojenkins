"""Click-dependent output functions for user-facing messages."""

import sys

from click import echo, style


class TextStyle:
    """Text style definitions."""

    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    NORMAL = '\033[0m'


def print2(message: str, bold: bool = False, color: str = 'reset') -> None:
    """Print a message to the console using click.

    Details:
        - Colors: `black` (might be a gray), `red`, `green`, `yellow` (might be an orange), `blue`,
          `magenta`, `cyan`, `white` (might be light gray), `reset` (reset the color code only)

    Example Usage:
        - `print2("Hey there!", bold=True, color="green")`

    Args:
        message: Message to print to console
        bold   : Whether to bold the message
        color  : Color to use for the message ()
    """
    echo(style(message, fg=color, bold=bold))


def fail_out(message: str) -> None:
    """Output one failure message to the console, then exit.

    Example Usage:
        - `fail_out("Something went wrong!")`

    Args:
        message: Message to output to console
    """
    echo(style(message, fg='bright_red', bold=True))
    sys.exit(1)


def failures_out(messages: list) -> None:
    """Output multiple failure messages to the console, then exit.

    Example Usage:
        - `failures_out(["Oh no!", "This is not good!"])`

    Args:
        message: Multiple messages to output to console
    """
    for message in messages:
        echo(style(message, fg='bright_red', bold=True))
    sys.exit(1)
