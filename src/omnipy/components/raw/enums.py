from typing import Literal

from omnipy.util.literal_enum import LiteralEnum


class NewLine(LiteralEnum[str]):
    """Enum for newline characters."""
    Literals = Literal['\n', '\r\n', '\r', '']

    LF: Literal['\n'] = '\n'
    CRLF: Literal['\r\n'] = '\r\n'
    CR: Literal['\r'] = '\r'
    UNIVERSAL: Literal[''] = ''
