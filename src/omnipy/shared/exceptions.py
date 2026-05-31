"""Shared exceptions used across Omnipy protocols and runtime code."""

import omnipy.util.pydantic as pyd


class JobStateException(Exception):
    """Base exception for job state issues."""

    ...


class ShouldNotOccurException(Exception):
    """Raised when an assumed-impossible condition occurs."""

    ...


class AssumedToBeImplementedException(Exception):
    """
    Used as default implementation for methods in Protocols that are to be
    inherited from in TYPE_CHECKING blocks. This tells type checkers
    that a class should be assumed to implement the protocol, even when
    type checkers cannot verify this. If a Protocol method is just an
    ellipsis or raises NotImplementedError, type checkers will check that
    the class actually implements the method.
    """
    ...


class OmnipyNoneIsNotAllowedError(pyd.NoneIsNotAllowedError):
    """Raised when `None` is invalid for an Omnipy pydantic field."""

    msg_template = '[Omnipy] none is not an allowed value'


class PendingDataError(ValueError):
    """Raised when pending data is used as resolved data."""

    ...


class FailedDataError(ValueError):
    """Raised when failed data is used as resolved data."""

    ...
