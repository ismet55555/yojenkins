"""Status class definition"""

from enum import Enum


class Status(Enum):
    """Enum of Jenkins statuses as described by Jenkins return

    Usage Examples:
        - `BuildStatus.RUNNING.value`
        - `if some_text in Status.RUNNING.value:`
    """
    RUNNING = ['RUNNING', 'IN_PROGRESS']
    SUCCESS = ['SUCCESS', 'SUCCEEDED']
    FAILURE = ['FAILURE', 'FAILED', 'FAIL']
    QUEUED = ['QUEUED']
    ABORTED = ['ABORTED']
    UNSTABLE = ['UNSTABLE']
    PAUSED_INPUT = ['PAUSED_PENDING_INPUT']
    NOT_FOUND = ['NOT FOUND OR STARTED']
    NOT_RUN = ['NOT_EXECUTED', 'NOT_RUN']
    NONE = [None]
    UNKNOWN = ['UNKNOWN']


class BuildStatus(Enum):
    """Enum of Jenkins status for build

    Details: This enum references Status enum above and
             picks the status text that belongs to it

    Usage Examples:  `BuildStatus.RUNNING.value`
    """
    RUNNING = Status.RUNNING.value[0]
    SUCCESS = Status.SUCCESS.value[0]
    FAILURE = Status.FAILURE.value[0]
    QUEUED = Status.QUEUED.value[0]
    ABORTED = Status.ABORTED.value[0]
    UNSTABLE = Status.UNSTABLE.value[0]
    PAUSED_INPUT = Status.PAUSED_INPUT.value[0]
    NOT_FOUND = Status.NOT_FOUND.value[0]
    NOT_RUN = Status.NOT_RUN.value[0]
    NONE = Status.NONE.value[0]
    UNKNOWN = Status.UNKNOWN.value[0]


class StageStatus(Enum):
    """Enum of Jenkins status for stage

    Details: This enum references Status enum above and
             picks the status text that belongs to it

    Usage Examples:  `StageStatus.RUNNING.value`
    """
    RUNNING = Status.RUNNING.value[1]  # <-- Note 1
    SUCCESS = Status.SUCCESS.value[0]
    FAILURE = Status.FAILURE.value[0]
    QUEUED = Status.QUEUED.value[0]
    ABORTED = Status.ABORTED.value[0]
    UNSTABLE = Status.UNSTABLE.value[0]
    PAUSED_INPUT = Status.PAUSED_INPUT.value[0]
    NOT_FOUND = Status.NOT_FOUND.value[0]
    NOT_RUN = Status.NOT_RUN.value[0]
    NONE = Status.NONE.value[0]
    UNKNOWN = Status.UNKNOWN.value[0]


class Color(Enum):
    """Enum of Jenkins status color name

    Usage Examples:  `Color.RUNNING.value`
    """
    ITEMS = {
        'RUNNING': 'normal',
        'SUCCESS': 'green',
        'FAILURE': 'red',
        'QUEUED': 'normal',
        'ABORTED': 'magenta',
        'UNSTABLE': 'orange',
        'PAUSED_INPUT': 'cyan',
        'NOT_FOUND': 'normal',
        'NOT_RUN': 'grey-dark',
        'NONE': 'normal',
        'UNKNOWN': 'normal'
    }


class Sound(Enum):
    """Enum of local sound filename matching Jenkins status

    Details:
        - Sound source: https://www.zapsplat.com/

    Usage Examples:  `Sound.RUNNING.value`
    """
    ITEMS = {
        'RUNNING': '',
        'SUCCESS': 'positive_alert_notification_musical_short_marimba_process_finished.wav',
        'FAILURE': 'negative_ui_ping_chime_mallet_like_error.wav',
        'QUEUED': '',
        'ABORTED': 'negative_ui_ping_chime_mallet_like.wav',
        'UNSTABLE': 'negative_notification_mallet_wooden_short_alert.wav',
        'PAUSED_INPUT': 'positive_alert_mallet_wood_simple_musical_003.wav',
        'NOT_FOUND': '',
        'NOT_RUN': '',
        'NONE': '',
        'UNKNOWN': ''
    }
