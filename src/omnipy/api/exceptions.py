from pydantic import NoneIsNotAllowedError


class JobStateException(Exception):
    ...


class ShouldNotOccurException(Exception):
    ...


class OmnipyNoneIsNotAllowedError(NoneIsNotAllowedError):
    msg_template = '[Omnipy] none is not an allowed value'
