import os
import sys
from textwrap import dedent
from typing import cast, TYPE_CHECKING

import rich.console

from omnipy.data.typechecks import is_model_instance
from omnipy.shared.enums.display import DisplayColorSystem
from omnipy.shared.enums.ui import (AutoDetectableUserInterfaceType,
                                    JupyterUserInterfaceType,
                                    SpecifiedUserInterfaceType,
                                    TerminalOutputUserInterfaceType,
                                    UserInterfaceType)
from omnipy.shared.protocols.config import IsJupyterUserInterfaceConfig

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
        case _ui_type if UserInterfaceType.is_jupyter(_ui_type):
            assert isinstance(ui_type_data_config, IsJupyterUserInterfaceConfig)
            display_jupyter_setup_note(_ui_type)
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
                builtins._ = obj  # type: ignore[attr-defined]  # part of displayhook contract
            else:
                sys.__displayhook__(obj)

    sys.displayhook = _omnipy_displayhook


def note_mime_bundle(bullet: str,
                     html_content: str,
                     plain_text_content: str = '',
                     styling: str = '',
                     noscript: bool = False) -> dict[str, str]:

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
    from IPython.display import display

    display(
        note_mime_bundle(
            bullet='ℹ️',
            html_content=dedent("""\
                Omnipy has detected that it is being imported into a Jupyter
                session. Please run the following in a separate cell:

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
    """
    Sets up the Jupyter user interface by displaying the CSS styles and
    adding hidden reactive elements for Jupyter Notebook or JupyterLab.
    Hidden reactive elements include:

      - A reactive element monitoring background color changes to detect
        changes in theme (dark/light)
      - A reactive element monitoring the available display size to
        auto-scale Omnipy outputs accordingly.

    This function is typically called in a Jupyter environment to ensure
    proper display and interaction with Omnipy components.
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
                              '<i>"defer"</i> instead of the '
                              'default <i>"full"</i>. Reactive '
                              'functionality might be less responsive '
                              'in this mode.'),
            ),
            raw=True,
        )

        bg_color_updater = jupy_comp.ReactiveBgColorUpdater(jupyter_ui_config=jupyter_ui_config)
        bg_color_updater.mime_bundle = note_mime_bundle(
            bullet='⚠️',
            html_content='Widget to automatically detect theme background color was not loaded.',
        )
        display(bg_color_updater)

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
