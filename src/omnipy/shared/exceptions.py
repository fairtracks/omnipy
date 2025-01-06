import omnipy.util._pydantic as pyd


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
