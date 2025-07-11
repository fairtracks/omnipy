import os
import sys

from rich._cell_widths import CELL_WIDTHS
from rich.cells import _is_single_cell_widths

from omnipy.data.typechecks import is_model_instance
from omnipy.shared.enums.ui import (AutoDetectableUserInterfaceType,
                                    TerminalOutputUserInterfaceType,
                                    UserInterfaceType)
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

    Parameters:
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


def running_in_any_jupyter() -> bool:
    try:
        ipython = get_ipython()  # type: ignore[name-defined]
        return ipython.__class__.__name__ == 'ZMQInteractiveShell'
    except NameError:
        return False


def running_in_jupyter_in_browser() -> bool:
    return running_in_any_jupyter() and not running_in_jupyter_in_pycharm()


def running_in_jupyter_in_pycharm() -> bool:
    return running_in_any_jupyter() and 'pydev_jupyter_utils' in sys.modules


def running_in_pycharm_console() -> bool:
    return os.getenv('PYCHARM_HOSTED') is not None


def running_in_atty_terminal() -> bool:
    return sys.stdout.isatty()


def detect_ui_type() -> AutoDetectableUserInterfaceType.Literals:
    if running_in_jupyter_in_pycharm():
        return UserInterfaceType.PYCHARM_JUPYTER
    elif running_in_jupyter_in_browser():
        return UserInterfaceType.JUPYTER
    elif running_in_ipython_terminal():
        return UserInterfaceType.IPYTHON
    elif running_in_pycharm_console():
        if running_in_ipython_pycharm():
            return UserInterfaceType.PYCHARM_IPYTHON
        else:
            return UserInterfaceType.PYCHARM_TERMINAL
    elif running_in_atty_terminal():
        return UserInterfaceType.TERMINAL
    else:
        return UserInterfaceType.UNKNOWN


def get_terminal_prompt_height(
    ui_type: TerminalOutputUserInterfaceType.Literals,
) -> int:  # pyright: ignore [reportReturnType]
    """
    Get the height of the terminal prompt (including blank lines) based on
    the display type.
    """
    match ui_type:
        case x if UserInterfaceType.is_plain_terminal(x):
            return 2
        case x if UserInterfaceType.is_ipython_terminal(x):
            return 3
        case x if UserInterfaceType.is_jupyter_embedded(x):
            return 0


def setup_displayhook_if_plain_terminal() -> None:
    """
    Sets up the display hook for plain terminal environments to ensure that
    the output is displayed correctly.
    """
    from omnipy.data.dataset import Dataset

    ui_type = detect_ui_type()

    if UserInterfaceType.is_plain_terminal(ui_type):

        def _omnipy_displayhook(obj: object) -> None:
            """
            Custom display hook for plain terminal environments.
            """
            import builtins

            if obj is not None:
                if is_model_instance(obj) or isinstance(obj, Dataset):
                    print(obj._default_repr())
                    builtins._ = obj  # type: ignore[attr-defined]
                else:
                    sys.__displayhook__(obj)

        sys.displayhook = _omnipy_displayhook


def setup_css_if_running_in_jupyter_in_browser() -> None:
    """
    Displays the CSS styles for Jupyter Notebook or JupyterLab, given that
    the Jupyter environment is detected.
    """
    if running_in_jupyter_in_browser():
        from IPython.display import display, HTML
        display(
            HTML("""
            Note: Some CSS styling related to Solara/Vuetify was added by
            Omnipy to Jupyter Notebook or JupyterLab.
        <style>
        /*
        Workaround for an issue where cells that are far out of view
        lose their padding. This causes issues with panels resizing
        when scrolling quickly.
        */
        .jp-Cell {
            padding: var(--jp-cell-padding) !important;
        }

        /*
        Workaround to remove horizontal spacing for vuetify code elements
        */
        :where(.vuetify-styles) .v-application code:after,
        :where(.vuetify-styles) .v-application code:before,
        :where(.vuetify-styles) .v-application kbd:after,
        :where(.vuetify-styles) .v-application kbd:before {
            content: none;
            letter-spacing: 0px;
        }

        /*
        Remove Vuetify background color in order to support
        transparent-background=True
        */
        :where(.vuetify-styles) .v-application code {
            background-color: unset;
        }
        :where(.vuetify-styles) .theme--dark.v-sheet {
            background-color: unset;
        }
        :where(.vuetify-styles) .theme--light.v-sheet {
            background-color: unset;
        }
        </style>
        """))
