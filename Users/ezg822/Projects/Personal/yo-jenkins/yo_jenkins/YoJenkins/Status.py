#!/usr/bin/env python3

from enum import Enum


class Status(Enum):
    """Enum of Jenkins statuses

    Usage Examples: 
        - `BuildStatus.running.value`
        - `if some_text in Status.running.value:`
    """
    running = ['RUNNING', 'IN_PROGRESS']
    success = ['SUCCESS']
    failure = ['FAILURE', 'FAILED', 'FAIL']
    queued = ['QUEUED']
    aborted = ['ABORTED']
    not_found = ['NOT FOUND OR STARTED']
    none = [None]
    unknown = ['UNKNOWN']


class BuildStatus(Enum):
    """Enum of Jenkins status for build

    Details: This enum references Status enum above and
             picks the status text that belongs to it

    Usage Examples:  `BuildStatus.running.value`
    """
    running = Status.running.value[0]
    success = Status.success.value[0]
    failure = Status.failure.value[0]
    queued = Status.queued.value[0]
    aborted = Status.aborted.value[0]
    not_found = Status.not_found.value[0]
    none = Status.none.value[0]
    unknown = Status.unknown.value[0]


class StageStatus(Enum):
    """Enum of Jenkins status for stage

    Details: This enum references Status enum above and
             picks the status text that belongs to it

    Usage Examples:  `StageStatus.running.value`
    """
    running = Status.running.value[1]
    success = Status.success.value[0]
    failure = Status.failure.value[0]
    queued = Status.queued.value[0]
    aborted = Status.aborted.value[0]
    not_found = Status.not_found.value[0]
    none = Status.none.value[0]
    unknown = Status.unknown.value[0]


class Color(Enum):
    """Enum of Jenkins status color

    Usage Examples:  `Color.running.value`
    """
    items = {
        'running': 'normal',
        'success': 'green',
        'failure': 'red',
        'queued': 'normal',
        'aborted': 'magenta',
        'not_found': 'normal',
        'none': 'normal',
        'unknown': 'normal'
    }
