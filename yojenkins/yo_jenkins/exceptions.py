"""Custom exceptions for yo_jenkins business logic.

These replace fail_out()/sys.exit(1) calls so the business logic layer
can be used by both the CLI (which catches and prints errors) and the
web API (which maps exceptions to HTTP status codes).
"""


class YoJenkinsException(Exception):
    """Base exception for all yo_jenkins business logic errors."""


class AuthenticationError(YoJenkinsException):
    """Authentication or authorization failure."""


class NotFoundError(YoJenkinsException):
    """Requested resource was not found."""


class RequestError(YoJenkinsException):
    """General request or operation failure."""


class JenkinsOperationError(YoJenkinsException):
    """A Jenkins API operation failed."""


class ValidationError(YoJenkinsException):
    """Input validation failure."""
