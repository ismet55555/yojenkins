#!/usr/bin/env python3

from enum import Enum


class Status(Enum):
    """Enum of Jenkins statuses

    Usage Examples: 
        - `BuildStatus.running.value`
        - `if some_text in Status.running.value:`
    """
    running = ['RUNNING', 'IN_PROGRESS']
    success = ['SUCCESS', 'SUCCEEDED']
    failure = ['FAILURE', 'FAILED', 'FAIL']
    queued = ['QUEUED']
    aborted = ['ABORTED']
    unstable = ['UNSTABLE']
    paused_input = ['PAUSED_PENDING_INPUT']
    not_found = ['NOT FOUND OR STARTED']
    not_run = ['NOT_EXECUTED', 'NOT_RUN']
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
    unstable = Status.unstable.value[0]
    paused_input = Status.paused_input.value[0]
    not_found = Status.not_found.value[0]
    not_run = Status.not_run.value[0]
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
    unstable = Status.unstable.value[0]
    paused_input = Status.paused_input.value[0]
    not_found = Status.not_found.value[0]
    not_run = Status.not_run.value[0]
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
        'unstable': 'orange',
        'paused_input': 'cyan',
        'not_found': 'normal',
        'not_run': 'grey-dark',
        'none': 'normal',
        'unknown': 'normal'
    }

class Sound(Enum):
    """Enum of Jenkins status sound filename

    Usage Examples:  `Color.running.value`
    """
    items = {
        'running': '',
        'success': 'positive_alert_notification_musical_short_marimba_process_finished.wav',
        'failure': 'negative_ui_ping_chime_mallet_like_error.wav',
        'queued': '',
        'aborted': 'negative_ui_ping_chime_mallet_like.wav',
        'unstable': '',
        'paused_input': '',
        'not_found': '',
        'not_run': '',
        'none': '',
        'unknown': ''
    }
