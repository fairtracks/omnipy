import os
import sys

from rich._cell_widths import CELL_WIDTHS
from rich.cells import _is_single_cell_widths

from omnipy.shared.enums import DisplayType
from omnipy.util.range_lookup import RangeLookup


class UnicodeCharWidthMap:
    def __init__(self) -> None:
        width_0_ranges = []
        width_2_ranges = []

        for start, stop_inclusive, width in CELL_WIDTHS:
            cur_range = range(start, stop_inclusive + 1)
            if width <= 0:
                width_0_ranges.append(cur_range)
            elif width == 2:
                width_2_ranges.append(cur_range)

        self._chars_with_width_0 = RangeLookup(width_0_ranges)
        self._chars_with_width_2 = RangeLookup(width_2_ranges)

    def __getitem__(self, char: str) -> int:
        unicode_index = ord(char)
        if unicode_index in self._chars_with_width_0:
            return 0
        if unicode_index in self._chars_with_width_2:
            return 2
        return 1

    @staticmethod
    def only_single_width_chars(line: str) -> bool:
        return _is_single_cell_widths(line)

    def __hash__(self) -> int:
        # No state, so we can use a constant hash
        return hash('UnicodeCharWidthMap')


def soft_wrap_words(words: list[str], max_width: int) -> list[str]:
    """Wrap words into lines that don't exceed max_width.

    Distributes words across multiple lines ensuring that each line doesn't
    exceed the specified maximum width. Single words longer than max_width
    are not split and will appear on their own line.

    Args:
        words: List of words to be wrapped
        max_width: Maximum width (in characters) for each line

    Returns:
        List of strings, where each string is a wrapped line of text
    """
    lines: list[list[str]] = []
    current_line: list[str] = []
    current_width = 0

    for word in words:
        # Add word to current line
        space_width = 1 if current_line else 0
        current_width += len(word) + space_width
        current_line.append(word)

        # If line has more than one word and exceeds max_width,
        # move last word to new line
        if len(current_line) > 1 and current_width > max_width:
            lines.append(current_line[:-1])
            current_line = [word]
            current_width = len(word)

    # Add the final line
    if current_line:
        lines.append(current_line)

    # Add spaces and return
    return [' '.join(line) for line in lines]


def running_in_ipython_terminal() -> bool:
    try:
        ipython = get_ipython()  # type: ignore[name-defined]
        return ipython.__class__.__name__ == 'TerminalInteractiveShell'
    except NameError:
        return False


def running_in_ipython_pycharm() -> bool:
    try:
        ipython = get_ipython()  # type: ignore[name-defined]
        return ipython.__class__.__name__ == 'PyDevTerminalInteractiveShell'
    except NameError:
        return False


def running_in_jupyter() -> bool:
    try:
        ipython = get_ipython()  # type: ignore[name-defined]
        return ipython.__class__.__name__ == 'ZMQInteractiveShell'
    except NameError:
        return False


def running_in_pycharm_console() -> bool:
    return os.getenv('PYCHARM_HOSTED') is not None


def running_in_atty_terminal() -> bool:
    return sys.stdout.isatty()


def detect_display_type() -> DisplayType:
    if running_in_jupyter():
        return DisplayType.JUPYTER
    elif running_in_ipython_terminal():
        return DisplayType.IPYTHON
    elif running_in_pycharm_console():
        if running_in_ipython_pycharm():
            return DisplayType.PYCHARM_IPYTHON
        else:
            return DisplayType.PYCHARM_TERMINAL
    elif running_in_atty_terminal():
        return DisplayType.TERMINAL
    else:
        return DisplayType.UNKNOWN


def display_type_is_any_terminal(display_type: DisplayType) -> bool:
    """
    Check if the display_type refers to any terminal environment. If display
    type is unknown, we still assume it is a terminal.
    """
    return display_type in (DisplayType.TERMINAL,
                            DisplayType.IPYTHON,
                            DisplayType.PYCHARM_TERMINAL,
                            DisplayType.PYCHARM_IPYTHON,
                            DisplayType.UNKNOWN)
