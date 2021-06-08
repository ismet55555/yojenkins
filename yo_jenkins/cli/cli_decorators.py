#!/usr/bin/env python3

import click
import functools


def format_output(decorated_function):
    """click module options for formatting the output

    Details: This function is a convenience function to use to add click options

    Args:
        decorated_function : Function that is decorated

    Returns:
        None
    """
    @click.option('-p', '--pretty', type=bool, default=False,  required=False, is_flag=True, help='Output in pretty human readable format')
    @click.option('-y', '--yaml', type=bool, default=False, required=False, is_flag=True, help='Output in YAML/YMLS format')
    @click.option('-x', '--xml', type=bool, default=False, required=False, is_flag=True, help='Output in XML format')
    @click.option('-t', '--toml', type=bool, default=False, required=False, is_flag=True, help='Output in TOML format')
    @functools.wraps(decorated_function)
    def wrapper(*args, **kwds):
        return decorated_function(*args, **kwds)
    return wrapper


def debug(decorated_function):
    """click module options for debug level

    Details: This function is a convenience function to use to add click options

    Args:
        decorated_function : Function that is decorated

    Returns:
        None
    """

    # TODO: Just call/move the debug log level update function here

    @click.option('--debug', type=bool, default=False, required=False, is_flag=True, help='Enable debug level log messages')
    @functools.wraps(decorated_function)
    def wrapper(*args, **kwds):
        return decorated_function(*args, **kwds)
    return wrapper


def profile(decorated_function):
    """click module options for selecting the credentials profile to be used with the command

    Details: This function is a convenience function to use to add click options

    Args:
        decorated_function : Function that is decorated

    Returns:
        None
    """
    @click.option('--profile', type=str, required=False, is_flag=False, help='Authentication profile for command')
    @functools.wraps(decorated_function)
    def wrapper(*args, **kwds):
        return decorated_function(*args, **kwds)
    return wrapper



def list(decorated_function):
    """click module options for outputting as a list

    Details: This function is a convenience function to use to add click options

    Args:
        decorated_function : Function that is decorated

    Returns:
        None
    """
    @click.option('-l', '--list', type=bool, default=False, required=False, is_flag=True, help='Output as list')
    @functools.wraps(decorated_function)
    def wrapper(*args, **kwds):
        return decorated_function(*args, **kwds)
    return wrapper

