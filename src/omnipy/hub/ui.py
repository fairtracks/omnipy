"""User-interface detection and Jupyter display setup helpers.

This module detects the active execution environment and provides the
user-facing ``setup_jupyter_ui()`` helper for enabling Omnipy's richer
notebook display integration.
"""

import builtins
import os
import sys
from textwrap import dedent
from typing import cast

import rich.console

from omnipy.shared.constants import DEFAULT_DARK_BACKGROUND
from omnipy.shared.enums.display import DisplayColorSystem
from omnipy.shared.enums.ui import (AutoDetectableUserInterfaceType,
                                    JupyterUserInterfaceType,
                                    SpecifiedUserInterfaceType,
                                    TerminalOutputUserInterfaceType,
                                    UserInterfaceType)
from omnipy.shared.protocols.config import IsJupyterUserInterfaceConfig
from omnipy.shared.typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .runtime import Runtime


def detect_and_setup_user_interface(runtime: 'Runtime') -> None:
    """Detect the active user interface and configure runtime display defaults.

    Args:
        runtime: Runtime whose UI configuration should be updated.
    """
    ui_type: AutoDetectableUserInterfaceType.Literals = detect_ui_type()
    runtime.config.data.ui.detected_type = ui_type

    ui_type_data_config = runtime.config.data.ui.get_ui_type_config(ui_type)
    ui_type_data_config.color.system = detect_display_color_system(ui_type)
    ui_type_data_config.color.dark_background = detect_dark_background(ui_type)

    match ui_type:
        case _ui_type if UserInterfaceType.is_jupyter(_ui_type):
            assert isinstance(ui_type_data_config, IsJupyterUserInterfaceConfig)
            display_jupyter_setup_note(_ui_type)
        case _ui_type if UserInterfaceType.is_plain_terminal(_ui_type):
            setup_displayhook_if_plain_terminal(_ui_type)


def running_in_ipython_terminal() -> bool:
    """Return whether the current session is running in an IPython terminal.

    Returns:
        ``True`` when running inside ``TerminalInteractiveShell``, else ``False``.

    Notes:
        Depends on the active Python execution environment.
    """
    try:
        ipython = get_ipython()  # type: ignore[name-defined]
        return ipython.__class__.__name__ == 'TerminalInteractiveShell'
    except NameError:
        return False


def running_in_ipython_pycharm() -> bool:
    """Return whether the current session is running in PyCharm's IPython console.

    Returns:
        ``True`` when running inside ``PyDevTerminalInteractiveShell``, else ``False``.

    Notes:
        Depends on the active Python execution environment.
    """
    try:
        ipython = get_ipython()  # type: ignore[name-defined]
        return ipython.__class__.__name__ == 'PyDevTerminalInteractiveShell'
    except NameError:
        return False


def running_in_any_jupyter() -> bool:
    """Return whether the current session is running in any Jupyter kernel.

    Returns:
        ``True`` when running inside ``ZMQInteractiveShell``, else ``False``.

    Notes:
        Depends on the active Python execution environment.
    """
    try:
        ipython = get_ipython()  # type: ignore[name-defined]
        return ipython.__class__.__name__ == 'ZMQInteractiveShell'
    except NameError:
        return False


def running_in_jupyter_in_browser() -> bool:
    """Return whether the current session is running in browser-hosted Jupyter.

    Returns:
        ``True`` when running in a browser-hosted Jupyter session, else ``False``.

    Notes:
        Depends on the active Python execution environment.
    """
    return running_in_any_jupyter() and not running_in_jupyter_in_pycharm()


def running_in_jupyter_in_pycharm() -> bool:
    """Return whether the current session is running in PyCharm-hosted Jupyter.

    Returns:
        ``True`` when running in a PyCharm-hosted Jupyter session, else ``False``.

    Notes:
        Depends on the active Python execution environment.
    """
    return running_in_any_jupyter() and 'pydev_jupyter_utils' in sys.modules


def running_in_pycharm_console() -> bool:
    """Return whether the current process is hosted by a PyCharm console.

    Returns:
        ``True`` when the ``PYCHARM_HOSTED`` environment variable is set.

    Notes:
        Depends on the active process environment variables.
    """
    return os.getenv('PYCHARM_HOSTED') is not None


def running_in_atty_terminal() -> bool:
    """Return whether standard output is attached to an interactive terminal.

    Returns:
        ``True`` when ``sys.stdout`` is attached to a TTY, else ``False``.

    Notes:
        Depends on the active standard-output stream.
    """
    return sys.stdout.isatty()


def detect_ui_type() -> AutoDetectableUserInterfaceType.Literals:
    """Detect the current Omnipy user-interface type from the execution environment.

    Returns:
        The detected user-interface type literal.
    """
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
    """Detect the display color system available for a specific UI type.

    Args:
        ui_type: User-interface type to inspect.

    Returns:
        The detected display color system.
    """
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


def detect_dark_background(ui_type: UserInterfaceType.Literals) -> bool:
    """Detect whether the active UI should be treated as using a dark background.

    Args:
        ui_type: User-interface type to inspect.

    Returns:
        ``True`` if the background should be treated as dark, otherwise ``False``.
    """
    if UserInterfaceType.supports_dark_terminal_bg_detection(ui_type):
        return detect_dark_terminal_background()
    else:
        return DEFAULT_DARK_BACKGROUND


def detect_dark_terminal_background() -> bool:
    """Detect whether the current terminal background is dark.

    Returns:
        ``True`` if the terminal background is detected as dark, otherwise ``False``.

    Raises:
        ModuleNotFoundError: If the optional ``term_background`` dependency is unavailable.

    Notes:
        Detection depends on terminal capabilities and environment variables.
    """
    from term_background import is_dark_background

    color_fg_bg = os.environ.get('COLORFGBG', None)
    if color_fg_bg is not None:
        dark_from_color_fg_bg = _is_dark_from_color_fg_bg_nuanced(color_fg_bg)
        if dark_from_color_fg_bg is not None:
            return dark_from_color_fg_bg

    return is_dark_background()


def _is_dark_from_color_fg_bg_nuanced(color_fg_bg: str) -> bool | None:
    """Infer dark background status from a ``COLORFGBG`` environment value.

    Args:
        color_fg_bg: Semicolon-separated foreground/background color indexes.

    Returns:
        ``True`` if parsed background index is lower than foreground index,
        ``False`` otherwise, or ``None`` when parsing fails.

    Examples:
        >>> _is_dark_from_color_fg_bg_nuanced('15;0')
        True
    """
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
    """Return the prompt height for a terminal-oriented UI type.

    Args:
        ui_type: Terminal-oriented user-interface type.

    Returns:
        The prompt height in rendered terminal rows.
    """
    match ui_type:
        case x if UserInterfaceType.is_plain_terminal(x):
            return 2
        case x if UserInterfaceType.is_ipython_terminal(x):
            return 3
        case x if UserInterfaceType.is_jupyter_embedded(x):
            return 0


def setup_displayhook_if_plain_terminal(ui_type: TerminalOutputUserInterfaceType.Literals) -> None:
    """Install Omnipy's display hook for plain-terminal environments.

    Args:
        ui_type: Terminal-oriented user-interface type for rendering output.
    """
    from omnipy.config import ConfigBase
    from omnipy.data.dataset import Dataset
    from omnipy.data.model import is_model_instance

    def _omnipy_displayhook(obj: object) -> None:
        """Render supported Omnipy objects with terminal-aware formatting.

        Args:
            obj: Object produced by expression evaluation.
        """

        if obj is not None:
            if (is_model_instance(obj) or isinstance(obj, Dataset) or isinstance(obj, ConfigBase)):
                print(obj.default_repr_to_terminal_str(ui_type))
                builtins._ = obj  # type: ignore[attr-defined]  # part of displayhook contract
            else:
                sys.__displayhook__(obj)

    sys.displayhook = _omnipy_displayhook


def note_mime_bundle(bullet: str,
                     html_content: str,
                     plain_text_content: str = '',
                     styling: str = '',
                     noscript: bool = False) -> dict[str, str]:
    """Build a MIME bundle for displaying a note in rich frontends.

    Args:
        bullet: Leading marker shown beside the note.
        html_content: HTML body to render.
        plain_text_content: Optional plain-text fallback.
        styling: Optional CSS to embed with the note.
        noscript: Whether to wrap the HTML content in ``<noscript>``.

    Returns:
        A MIME bundle suitable for IPython display APIs.

    Examples:
        >>> note_mime_bundle('ℹ️', '<b>Info</b>')['text/html']
        '<div style="display: flex;">...'
    """

    note_html = dedent(f"""\
        <div style="display: flex;">
            <div style="flex:1; width: 30px;">{bullet}</div>
            <div style="width: calc(100% - 30px);">{html_content}</div>
        </div>
        """)

    note_html += dedent(f"""\
        <div><style>
        {styling}
        </style></div>
        """) if styling else ''

    if noscript:
        note_html = dedent(f"""\
            <noscript>
            {note_html}
            </noscript>
            """)

    mime_bundle = {
        'text/html': note_html,
    }

    if plain_text_content:
        mime_bundle['text/plain'] = plain_text_content

    return mime_bundle


def display_jupyter_setup_note(detected_ui_type: JupyterUserInterfaceType.Literals):
    """Display setup guidance after Omnipy detects a Jupyter environment.

    Args:
        detected_ui_type: Detected Jupyter user-interface type.

    Raises:
        AssertionError: If a non-Jupyter-in-browser type reaches the browser-only branch.
    """
    from IPython.display import display

    display(
        note_mime_bundle(
            bullet='ℹ️',
            html_content=dedent("""\
                Omnipy has detected that it is being imported into a Jupyter
                session. Please make sure the following is run, in this or a
                separate cell:

                <pre><code>import omnipy as om
                om.setup_jupyter_ui()
                </code></pre>
                """),
        ),
        raw=True,
    )

    if UserInterfaceType.is_jupyter_embedded(detected_ui_type):
        display(
            note_mime_bundle(
                bullet='🔌',
                html_content=('The Jupyter kernel currently runs in '
                              'embedded mode, e.g. from within PyCharm. '
                              '<i>(If you are running Jupyter in a web '
                              'browser, you probably want to restart the '
                              'kernel by clicking the ↻ icon in the Jupyter '
                              'toolbar.)</i>')),
            raw=True,
        )
    else:
        assert UserInterfaceType.is_jupyter_in_browser(detected_ui_type), \
            (f'Unexpected user interface type: {detected_ui_type}. If this '
             'is shown then there is most probably a bug in Omnipy. Please '
             'report it on GitHub.')

        display(
            note_mime_bundle(
                bullet='🌐',
                html_content=('The Jupyter kernel currently runs in '
                              'web browser mode. <i>(If you are running '
                              'Jupyter elsewhere, e.g. from within '
                              'PyCharm, you probably want to '
                              'restart the kernel.)</i>'),
            ),
            raw=True,
        )

        display(
            note_mime_bundle(
                bullet='🔧',
                html_content=('<i>Workaround for '
                              '<a href="https://github.com/fairtracks/omnipy/issues/244">'
                              'Jupyter in PyCharm detection issue</a>:</i> '
                              'immediately after kernel startup, run '
                              'an empty or unrelated cell before the '
                              'cell that loads Omnipy.'),
            ),
            raw=True,
        )


def setup_jupyter_ui():
    """Set up Omnipy's rich Jupyter display integration.

    Call this once per Jupyter kernel after importing Omnipy. The function
    injects CSS and hidden reactive widgets that Omnipy uses to track theme
    changes and available display size, so notebook outputs render and resize
    correctly.

    Raises:
        AssertionError: If the active runtime is not configured for a Jupyter
            interface.
    """

    from IPython.display import display

    from omnipy import runtime
    import omnipy.data._display.integrations.jupyter.components as jupy_comp

    detected_ui_type = runtime.config.data.ui.detected_type

    embedded_content_styling = dedent("""\
        /*
        Remove black lines in ANSI-encoded code blocks
        */

        .jp-RenderedText pre {
            line-height: normal !important;
        }""")

    jupyter_in_browser_styling = dedent("""\
        /*
        Improve font rendering
        */

        #main, .vuetify-styles {
            text-rendering: geometricPrecision;
            -webkit-font-smoothing: subpixel-antialiased;
            -moz-osx-font-smoothing: grayscale;
        }

        /*
        Workaround for an issue where cells that are far out of view
        lose their padding. This causes issues with panels resizing
        when scrolling quickly.
        */

        .jp-Cell {
            padding: var(--jp-cell-padding) !important;
        }

        /*
        Remove horizontal spacing for vuetify code elements
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
        solid_background=False
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

        /*
        Remove padding and margin for hidden widgets to remove vertical
        whitespace
        */

        .solara-content-main > div.col:has(> .omnipy-hidden) {
            padding: 0px !important;
        }

        .solara-content-main:has(.omnipy-hidden) {
            margin: 0px !important;
        }

        /*
        Make sure cell that contain hidden widgets do not collapse
        completely when scrolled out of view.
        */

        .jp-Cell.getsize-protected-cell[style*="display: none;"]{
            display: block !important;
            height: 0px !important;
            opacity: 0px !important;
            padding: 0px 5px 0px 5px !important;
            }

        /*
        Fix horizontal stripes in HTML output when reactive widgets are not
        loaded (e.g. if a notebook with stored HTML outputs is viewed
        without rerunning the cells).
        */

        .jp-RenderedHTMLCommon code {
            display: inline-block;
        }

        """) + embedded_content_styling

    assert UserInterfaceType.is_jupyter(detected_ui_type), \
        (f'Unexpected user interface type: {detected_ui_type}. Expected '
         'a Jupyter variant. If run from a Jupyter session, please '
         'restart the kernel and try again.')

    display(
        note_mime_bundle(
            bullet='⚠️',
            html_content=('This cell was not loaded properly! You probably '
                          'want to rerun the code cell above (<i>Click in '
                          'the code cell, and press Shift+Enter '
                          '<kbd>⇧</kbd>+<kbd>↩</kbd></i>).'),
            noscript=True,
        ),
        raw=True,
    )

    jupyter_ui_config = runtime.config.data.ui.get_ui_type_config(detected_ui_type)

    if UserInterfaceType.is_jupyter_embedded(detected_ui_type):
        display(
            note_mime_bundle(
                bullet='⚙️',
                html_content=('This cell contains CSS styling to improve '
                              'display of Omnipy terminal text output in '
                              'a web browser. This is needed if you load '
                              'a notebook with saved outputs that were '
                              'originally generated in embedded mode '
                              '(e.g. from within PyCharm).'),
                plain_text_content=('No Omnipy-related CSS styling was '
                                    'loaded due to plain text output.'),
                styling=embedded_content_styling,
            ),
            raw=True,
        )
    else:
        assert UserInterfaceType.is_jupyter_in_browser(detected_ui_type), \
            (f'Unexpected user interface type: {detected_ui_type}. If this '
             'is shown then there is most probably a bug in Omnipy. Please '
             'report it on GitHub.')

        assert isinstance(jupyter_ui_config, IsJupyterUserInterfaceConfig)

        display(
            note_mime_bundle(
                bullet='⚙️',
                html_content=('This cell contains CSS styling and hidden '
                              'widgets to allow clean and reactive display '
                              'of Omnipy outputs when running Jupyter in '
                              'a web browser.'),
                plain_text_content=('No Omnipy-related CSS styling or '
                                    'hidden widgets were loaded due to '
                                    'plain text output.'),
                styling=jupyter_in_browser_styling,
            ),
            raw=True,
        )

    display(
        note_mime_bundle(
            bullet='↻',
            html_content=('<i>Make sure to rerun this cell whenever '
                          'the kernel is restarted.</i>'),
        ),
        raw=True,
    )

    if not UserInterfaceType.is_jupyter_embedded(detected_ui_type):
        assert isinstance(jupyter_ui_config, IsJupyterUserInterfaceConfig)

        display(
            note_mime_bundle(
                bullet='🔧',
                html_content=('<i>Workaround for '
                              '<a href="https://github.com/jupyterlab/jupyterlab/issues/15968">'
                              'JupyterLab erratic scrolling issue</a>:</i> '
                              'set the "Windowing mode" setting under the '
                              '"Notebook" section of the "Settings Editor" '
                              '(from the "Settings" menu) to '
                              '<i>"contentVisibility"</i> (JupyterLab v4.5 '
                              'onwards) or <i>"defer"</i> (<v4.5) instead '
                              'of <i>"full"</i>.'),
            ),
            raw=True,
        )

        bg_color_updater = jupy_comp.ReactiveBgColorUpdater(jupyter_ui_config=jupyter_ui_config)
        bg_color_updater.mime_bundle = note_mime_bundle(
            bullet='⚠️',
            html_content='Widget to automatically detect theme background color was not loaded.',
        )
        display(bg_color_updater)

        assert runtime.objects.reactive is not None
        size_updater = jupy_comp.ReactiveAvailableDisplaySizeUpdater(
            jupyter_ui_config=jupyter_ui_config,
            reactive_objects=runtime.objects.reactive,
        )
        size_updater.mime_bundle = note_mime_bundle(
            bullet='⚠️',
            html_content='Widget to automatically detect window size was not loaded.',
        )
        display(size_updater)

        mime_bundle_end = {'text/html': dedent("""\
                <noscript></noscript>""")}
        display(mime_bundle_end, raw=True)
