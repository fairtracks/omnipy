import os
import sys
from typing import cast, TYPE_CHECKING

import rich.console

from omnipy.data._display.integrations.jupyter.components import ReactiveBgColorUpdater
from omnipy.data.typechecks import is_model_instance
from omnipy.shared.enums.display import DisplayColorSystem
from omnipy.shared.enums.ui import (AutoDetectableUserInterfaceType,
                                    SpecifiedUserInterfaceType,
                                    TerminalOutputUserInterfaceType,
                                    UserInterfaceType)
from omnipy.shared.protocols.config import IsColorConfig

if TYPE_CHECKING:
    from .runtime import Runtime


def detect_and_setup_user_interface(runtime: 'Runtime') -> None:
    """
    Detects the user interface type based on the current environment and
    sets up the default configuration for that user interface type. This
    includes setting up color systems, display hooks, and CSS styles and
    other functionality as needed.
    """
    ui_type: AutoDetectableUserInterfaceType.Literals = detect_ui_type()
    runtime.config.data.ui.detected_type = ui_type

    ui_type_data_config = runtime.config.data.ui.get_ui_type_config(ui_type)
    ui_type_data_config.color.system = detect_display_color_system(ui_type)
    if UserInterfaceType.supports_dark_terminal_bg_detection(ui_type):
        ui_type_data_config.color.dark_background = detect_dark_terminal_background()

    match ui_type:
        case _ui_type if UserInterfaceType.is_jupyter_in_browser(_ui_type):
            setup_css_if_running_in_jupyter_in_browser(ui_type_data_config.color)
        case _ui_type if UserInterfaceType.is_plain_terminal(_ui_type):
            setup_displayhook_if_plain_terminal(_ui_type)


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
            force_terminal=UserInterfaceType.is_terminal(ui_type),
        )
        rich_color_system: str | None = console.color_system
        if rich_color_system is None:
            return DisplayColorSystem.AUTO
        else:
            assert rich_color_system in DisplayColorSystem
            return cast(DisplayColorSystem.Literals, rich_color_system)


def detect_dark_terminal_background() -> bool:
    from term_background import is_dark_background

    color_fg_bg = os.environ.get('COLORFGBG', None)
    if color_fg_bg is not None:
        dark_from_color_fg_bg = _is_dark_from_color_fg_bg_nuanced(color_fg_bg)
        if dark_from_color_fg_bg is not None:
            return dark_from_color_fg_bg

    return is_dark_background()


def _is_dark_from_color_fg_bg_nuanced(color_fg_bg: str) -> bool | None:
    # COLORFGBG is set, use it to determine the background color
    try:
        parts = color_fg_bg.split(';')
        fg = int(parts[0])
        bg = int(parts[-1])
        # Dark background if bg is less than foreground
        # term_background.py only considers values 0 and 15
        return bg < fg
    except ValueError:
        return None


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


def setup_displayhook_if_plain_terminal(ui_type: TerminalOutputUserInterfaceType.Literals) -> None:
    """
    Sets up the display hook for plain terminal environments to ensure that
    Model instances, Datasets, and ConfigBase objects are displayed using
    Omnipy's syntax highlighting and formatting.
    """
    from omnipy.config import ConfigBase
    from omnipy.data.dataset import Dataset

    def _omnipy_displayhook(obj: object) -> None:
        """
        Custom display hook for plain terminal environments.
        """
        import builtins

        if obj is not None:
            if (is_model_instance(obj) or isinstance(obj, Dataset) or isinstance(obj, ConfigBase)):
                print(obj.default_repr_to_terminal_str(ui_type))
                builtins._ = obj  # type: ignore[attr-defined]
            else:
                sys.__displayhook__(obj)

    sys.displayhook = _omnipy_displayhook


def setup_css_if_running_in_jupyter_in_browser(jupyter_color_config: IsColorConfig) -> None:
    """
    Displays the CSS styles for Jupyter Notebook or JupyterLab. Also adds
    a reactive background color updater to monitor changes in the web page
    background color and update the UI accordingly.
    """
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
    display(ReactiveBgColorUpdater(jupyter_color_config))
