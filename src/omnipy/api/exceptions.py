import omnipy.util.pydantic as pyd

__all__ = ['JobStateException']


class JobStateException(Exception):
    ...


class ShouldNotOccurException(Exception):
    ...


class OmnipyNoneIsNotAllowedError(pyd.NoneIsNotAllowedError):
    msg_template = '[Omnipy] none is not an allowed value'


class PendingDataError(Exception):
    ...


class FailedDataError(Exception):
    ...
