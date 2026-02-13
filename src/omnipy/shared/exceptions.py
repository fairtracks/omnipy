import omnipy.util._pydantic as pyd


class JobStateException(Exception):
    ...


class ShouldNotOccurException(Exception):
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
    msg_template = '[Omnipy] none is not an allowed value'


class PendingDataError(ValueError):
    ...


class FailedDataError(ValueError):
    ...
