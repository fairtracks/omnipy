import os
import sys
from typing import cast

import rich.console

from omnipy.data.typechecks import is_model_instance
from omnipy.shared.enums.display import DisplayColorSystem
from omnipy.shared.enums.ui import (AutoDetectableUserInterfaceType,
                                    SpecifiedUserInterfaceType,
                                    TerminalOutputUserInterfaceType,
                                    UserInterfaceType)


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


def detect_display_color_system(
        ui_type: SpecifiedUserInterfaceType.Literals) -> DisplayColorSystem.Literals:
    if UserInterfaceType.supports_rgb_color_output(ui_type):
        return DisplayColorSystem.ANSI_RGB
    else:
        console = rich.console.Console(
            color_system=DisplayColorSystem.AUTO,
            force_terminal=UserInterfaceType.is_terminal(detect_ui_type()),
        )
        rich_color_system: str | None = console.color_system
        if rich_color_system is None:
            return DisplayColorSystem.AUTO
        else:
            assert rich_color_system in DisplayColorSystem
            return cast(DisplayColorSystem.Literals, rich_color_system)


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
