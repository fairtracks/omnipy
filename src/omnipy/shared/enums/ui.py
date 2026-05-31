"""User interface enums for environment detection, capabilities, and output targets."""

from textwrap import dedent
from typing import Literal

from typing_extensions import TypeIs

from omnipy.shared.constants import (JUPYTER_DEFAULT_HEIGHT,
                                     JUPYTER_DEFAULT_WIDTH,
                                     TERMINAL_DEFAULT_HEIGHT,
                                     TERMINAL_DEFAULT_WIDTH)
from omnipy.util.literal_enum import LiteralEnum

_IPYTHON_DESCRIPTION = dedent("""\
    IPython is an more advanced interactive interpreter than the builtin
    Python REPL, providing additional features such as syntax highlighting,
    tab completion, and better error messages.""")

_JUPYTER_DESCRIPTION = dedent("""\
    The Jupyter environment supports rich output rendering (based on HTML)
    and interactive widgets and is typically used for data analysis,
    scientific computing, and machine learning tasks. Jupyter and allows for
    the execution of code in cells, with the output displayed inline in the
    notebook.""")

_PYCHARM_NOTE = dedent(f"""\
    Note that PyCharm does not support automatic detection of the display
    dimensions, so the dimensions are set to the default values defined in
    the config ({TERMINAL_DEFAULT_WIDTH}x{TERMINAL_DEFAULT_HEIGHT} for the
    terminal, {JUPYTER_DEFAULT_WIDTH}x{JUPYTER_DEFAULT_HEIGHT} for
    Jupyter).""")

_BROWSER_DESCRIPTION = dedent("""\
    A web browser with HTML rendering, such as Google Chrome, Mozilla
    Firefox, or Microsoft Edge. This is for now used to display HTML output
    and does not currently support any interactive features.""")

_UNKNOWN_NOTE = dedent("""\
    If user interface type is `UNKNOWN`, we still assume it is a
    terminal.""")

_TYPEIS_NARROW_NOTE = dedent("""\
    If True, the `ui_type` is narrowed accordingly.""")


class PlainTerminalEmbeddedUserInterfaceType(LiteralEnum[str]):
    """Plain terminal UI enum values embedded inside another application."""

    Literals = Literal['pycharm_terminal']

    PYCHARM_TERMINAL: Literal['pycharm_terminal'] = 'pycharm_terminal'
    f"""PyCharm terminal running the builtin Python REPL.

    The console and/or terminal of the JetBrains PyCharm IDE running with
    the Python interactive interpreter (REPL). {_PYCHARM_NOTE}
    """


class PlainTerminalUserInterfaceType(PlainTerminalEmbeddedUserInterfaceType, LiteralEnum[str]):
    """Plain terminal UI enum values supported by Omnipy."""

    Literals = Literal['terminal', PlainTerminalEmbeddedUserInterfaceType.Literals, 'unknown']

    TERMINAL: Literal['terminal'] = 'terminal'
    """Standard Python REPL running in a terminal.

    A standard Python interactive interpreter (REPL), running within
    terminal-emulation software, such as the builtin "Terminal" app on Mac
    OS or GNOME Terminal on Linux, through a SSH connection to a remote
    server,  or directly on a console.
    """

    UNKNOWN: Literal['unknown'] = 'unknown'
    """Fallback UI type when the environment cannot be determined.

    The `UNKNOWN` user interface type is used when the user interface type
    cannot be determined. This will in practice produce the same output as
    for the `TERMINAL` display type. As is default for terminals, we try
    to autodetect color capabilities such as ANSI escape codes for color
    and text formatting (see `DisplayColorSystem.AUTO`).
    """


class IpythonEmbeddedTerminalUserInterfaceType(LiteralEnum[str]):
    """IPython terminal UI enum values embedded inside another application."""

    Literals = Literal['pycharm_ipython']

    PYCHARM_IPYTHON: Literal['pycharm_ipython'] = 'pycharm_ipython'
    f"""PyCharm terminal running the IPython REPL.

    The console and/or terminal of the JetBrains PyCharm IDE running with
    the IPython interactive interpreter (REPL).
     {_IPYTHON_DESCRIPTION} {_PYCHARM_NOTE}
    """


class IpythonTerminalUserInterfaceType(IpythonEmbeddedTerminalUserInterfaceType, LiteralEnum[str]):
    """IPython terminal UI enum values supported by Omnipy."""

    Literals = Literal['ipython', IpythonEmbeddedTerminalUserInterfaceType.Literals]

    IPYTHON: Literal['ipython'] = 'ipython'
    """IPython REPL running in a terminal.

    Same as `TERMINAL`, but running within the IPython interactive
    interpreter (REPL). The IPython interpreter is a more advanced
    interactive interpreter that provides additional features such as syntax
    highlighting, tab completion, and better error messages.
    """


class TerminalUserInterfaceType(PlainTerminalUserInterfaceType, IpythonTerminalUserInterfaceType):
    """Terminal UI enum values covering plain and IPython terminals."""

    Literals = Literal[
        PlainTerminalUserInterfaceType.Literals,
        IpythonTerminalUserInterfaceType.Literals,
    ]


class JupyterEmbeddedUserInterfaceType(LiteralEnum[str]):
    """Embedded Jupyter UI enum values, such as notebooks inside IDEs."""

    Literals = Literal['pycharm_jupyter']

    PYCHARM_JUPYTER: Literal['pycharm_jupyter'] = 'pycharm_jupyter'
    f"""PyCharm-hosted Jupyter notebook UI.

    A Jupyter notebook running within the user interface of the JetBrains
    PyCharm IDE.
     {_JUPYTER_DESCRIPTION} {_PYCHARM_NOTE}.
    """


class SupportsDarkTerminalBgDetection(TerminalUserInterfaceType, JupyterEmbeddedUserInterfaceType):
    """UI enum values that support dark terminal background detection."""

    Literals = Literal[
        TerminalUserInterfaceType.Literals,
        JupyterEmbeddedUserInterfaceType.Literals,
    ]


class JupyterInBrowserUserInterfaceType(LiteralEnum[str]):
    """Browser-hosted Jupyter UI enum values."""

    Literals = Literal['jupyter']

    JUPYTER: Literal['jupyter'] = 'jupyter'
    f"""Browser-hosted Jupyter notebook or JupyterLab UI.

    A Jupyter notebook or JupyterLab environment opened from a web browser.
     {_JUPYTER_DESCRIPTION}
    """


class JupyterUserInterfaceType(
        JupyterEmbeddedUserInterfaceType,
        JupyterInBrowserUserInterfaceType,
):
    """Jupyter UI enum values for embedded and browser-hosted notebooks."""

    Literals = Literal[
        JupyterEmbeddedUserInterfaceType.Literals,
        JupyterInBrowserUserInterfaceType.Literals,
    ]


class BrowserPageUserInterfaceType(LiteralEnum[str]):
    """Browser UI enum values that render full HTML pages."""

    Literals = Literal['browser-page']

    BROWSER_PAGE: Literal['browser-page'] = 'browser-page'
    f"""Browser UI for full-page HTML output.

    {_BROWSER_DESCRIPTION} The `BROWSER_PAGE` UI type displays content as
    full web pages.
    """


class BrowserTagUserInterfaceType(LiteralEnum[str]):
    """Browser UI enum values that render embeddable HTML fragments."""

    Literals = Literal['browser-tag']

    BROWSER_TAG: Literal['browser-tag'] = 'browser-tag'
    f"""Browser UI for embeddable HTML fragment output.

    {_BROWSER_DESCRIPTION} The `BROWSER_TAG` UI type displays content as
    standalone HTML elements, for HTML code that can be embedded in other
    HTML documents.
    """


class BrowserUserInterfaceType(BrowserPageUserInterfaceType, BrowserTagUserInterfaceType):
    """Browser UI enum values for page-based and tag-based output."""

    Literals = Literal[BrowserPageUserInterfaceType.Literals, BrowserTagUserInterfaceType.Literals]


class RgbColorUserInterfaceType(PlainTerminalEmbeddedUserInterfaceType,
                                 IpythonEmbeddedTerminalUserInterfaceType,
                                 JupyterUserInterfaceType,
                                 BrowserUserInterfaceType):
    """UI enum values that support RGB color output."""

    Literals = Literal[
        PlainTerminalEmbeddedUserInterfaceType.Literals,
        IpythonEmbeddedTerminalUserInterfaceType.Literals,
        JupyterUserInterfaceType.Literals,
        BrowserUserInterfaceType.Literals,
    ]


class TerminalOutputUserInterfaceType(
        PlainTerminalUserInterfaceType,
        IpythonTerminalUserInterfaceType,
        JupyterEmbeddedUserInterfaceType,
):
    """UI enum values that require ANSI terminal output."""

    Literals = Literal[
        PlainTerminalUserInterfaceType.Literals,
        IpythonTerminalUserInterfaceType.Literals,
        JupyterEmbeddedUserInterfaceType.Literals,
    ]


class HtmlTagOutputUserInterfaceType(
        JupyterInBrowserUserInterfaceType,
        BrowserTagUserInterfaceType,
):
    """UI enum values that require self-contained HTML tag output."""

    Literals = Literal[
        JupyterInBrowserUserInterfaceType.Literals,
        BrowserTagUserInterfaceType.Literals,
    ]


class HtmlPageOutputUserInterfaceType(BrowserPageUserInterfaceType):
    """UI enum values that require full HTML page output."""

    Literals = Literal[BrowserPageUserInterfaceType.Literals]


class AutoDetectableUserInterfaceType(
        PlainTerminalUserInterfaceType,
        IpythonTerminalUserInterfaceType,
        JupyterUserInterfaceType,
):
    """User interface types that Omnipy can detect automatically.

    User interface types that can be automatically detected by Omnipy, based
    on the environment in which the code is running.
    """

    Literals = Literal[
        PlainTerminalUserInterfaceType.Literals,
        IpythonTerminalUserInterfaceType.Literals,
        JupyterUserInterfaceType.Literals,
    ]


class SpecifiedUserInterfaceType(PlainTerminalUserInterfaceType,
                                 IpythonTerminalUserInterfaceType,
                                 JupyterUserInterfaceType,
                                 BrowserUserInterfaceType):
    """User interface types represented as explicit concrete UI values.

    User interface types that are specified as a particular UI type, either
    automatically determined by Omnipy or hard-coded (i.e. for browser
    output). This is a union of all supported user interface types
    (including `UNKNOWN`), except for `AUTO`.
    """

    Literals = Literal[
        PlainTerminalUserInterfaceType.Literals,
        IpythonTerminalUserInterfaceType.Literals,
        JupyterUserInterfaceType.Literals,
        BrowserUserInterfaceType.Literals,
    ]


class UserInterfaceType(SpecifiedUserInterfaceType, LiteralEnum[str]):
    """Describe the interface type used for Omnipy interaction and output.

    Describes the type of interface in use for interacting with the user,
    encompassing the support available for displaying output as well as how
    the user interacts with the library (including the type of interactive
    interpreter used, if any).

    Should be automatically determined by Omnipy, but the user can also be
    set the user interface type manually in the config if for some reason
    needed (e.g. if auto-detection fails). In particular, the user can
    expect this to fail in other IDEs than PyCharm, which is the only IDE
    currently supported by Omnipy.
    """

    Literals = Literal[SpecifiedUserInterfaceType.Literals, 'auto']

    AUTO: Literal['auto'] = 'auto'
    """Automatically detect the user interface type.

    The `AUTO` user interface type is used to describe that the user
    interface type has not yet been determined, and that it should be
    automatically determined by Omnipy. This is the default value.
    """
    @classmethod
    def is_plain_terminal(
            cls, ui_type: 'UserInterfaceType.Literals'
    ) -> TypeIs[PlainTerminalUserInterfaceType.Literals]:
        """Check whether a UI type is a plain terminal variant.

        Args:
            ui_type: User interface type literal to classify.

        Returns:
            True if ``ui_type`` is a non-IPython terminal type. ``UNKNOWN``
            is treated as a terminal type.
        """
        return ui_type in PlainTerminalUserInterfaceType

    @classmethod
    def is_ipython_terminal(
            cls, ui_type: 'UserInterfaceType.Literals'
    ) -> TypeIs[IpythonTerminalUserInterfaceType.Literals]:
        """Check whether a UI type is an IPython terminal variant.

        Args:
            ui_type: User interface type literal to classify.

        Returns:
            True if ``ui_type`` refers to an IPython terminal UI type.
        """
        return ui_type in IpythonTerminalUserInterfaceType

    @classmethod
    def is_terminal(
            cls,
            ui_type: 'UserInterfaceType.Literals') -> TypeIs[TerminalUserInterfaceType.Literals]:
        """Check whether a UI type is any terminal variant.

        Args:
            ui_type: User interface type literal to classify.

        Returns:
            True if ``ui_type`` is a plain-terminal or IPython-terminal type.
            ``UNKNOWN`` is treated as a terminal type.
        """
        return ui_type in TerminalUserInterfaceType

    @classmethod
    def is_jupyter_embedded(
            cls, ui_type: 'UserInterfaceType.Literals'
    ) -> TypeIs[JupyterEmbeddedUserInterfaceType.Literals]:
        """Check whether a UI type is an embedded Jupyter variant.

        Args:
            ui_type: User interface type literal to classify.

        Returns:
            True if ``ui_type`` refers to Jupyter embedded in another app.
        """
        return ui_type in JupyterEmbeddedUserInterfaceType

    @classmethod
    def supports_dark_terminal_bg_detection(
            cls, ui_type: 'UserInterfaceType.Literals'
    ) -> TypeIs[SupportsDarkTerminalBgDetection.Literals]:
        """Check whether a UI type supports dark terminal background detection.

        Args:
            ui_type: User interface type literal to classify.

        Returns:
            True if ``ui_type`` supports terminal-style dark background
            detection.
        """
        return ui_type in SupportsDarkTerminalBgDetection

    @classmethod
    def is_jupyter_in_browser(
        cls, ui_type: 'UserInterfaceType.Literals'
    ) -> TypeIs[JupyterInBrowserUserInterfaceType.Literals]:
        """Check whether a UI type is a browser-hosted Jupyter variant.

        Args:
            ui_type: User interface type literal to classify.

        Returns:
            True if ``ui_type`` refers to Jupyter or JupyterLab in a browser.
        """
        return ui_type in JupyterInBrowserUserInterfaceType

    @classmethod
    def is_jupyter(
            cls,
            ui_type: 'UserInterfaceType.Literals') -> TypeIs[JupyterUserInterfaceType.Literals]:
        """Check whether a UI type is any Jupyter variant.

        Args:
            ui_type: User interface type literal to classify.

        Returns:
            True if ``ui_type`` refers to Jupyter in embedded or browser form.
        """
        return ui_type in JupyterUserInterfaceType

    @classmethod
    def is_browser(
            cls,
            ui_type: 'UserInterfaceType.Literals') -> TypeIs[BrowserUserInterfaceType.Literals]:
        """Check whether a UI type is a browser output variant.

        Args:
            ui_type: User interface type literal to classify.

        Returns:
            True if ``ui_type`` maps to one of the browser output types.
        """
        return ui_type in BrowserUserInterfaceType

    @classmethod
    def supports_rgb_color_output(
            cls,
            ui_type: 'UserInterfaceType.Literals') -> TypeIs[RgbColorUserInterfaceType.Literals]:
        """Check whether a UI type supports RGB color output.

        Args:
            ui_type: User interface type literal to classify.

        Returns:
            True if ``ui_type`` supports RGB color rendering.
        """
        return ui_type in RgbColorUserInterfaceType

    @classmethod
    def requires_terminal_output(
            cls, ui_type: 'UserInterfaceType.Literals'
    ) -> TypeIs[TerminalOutputUserInterfaceType.Literals]:
        """Check whether a UI type requires ANSI terminal-style output.

        Args:
            ui_type: User interface type literal to classify.

        Returns:
            True if ``ui_type`` requires terminal-encoded output. ``UNKNOWN``
            is treated as terminal output.
        """
        return ui_type in TerminalOutputUserInterfaceType

    @classmethod
    def requires_html_tag_output(
            cls, ui_type: 'UserInterfaceType.Literals'
    ) -> TypeIs[HtmlTagOutputUserInterfaceType.Literals]:
        """Check whether a UI type requires self-contained HTML tag output.

        Args:
            ui_type: User interface type literal to classify.

        Returns:
            True if ``ui_type`` requires embeddable HTML tag output.
        """
        return ui_type in HtmlTagOutputUserInterfaceType

    @classmethod
    def requires_html_page_output(
            cls, ui_type: 'UserInterfaceType.Literals'
    ) -> TypeIs[HtmlPageOutputUserInterfaceType.Literals]:
        """Check whether a UI type requires full HTML page output.

        Args:
            ui_type: User interface type literal to classify.

        Returns:
            True if ``ui_type`` requires full-page HTML output.
        """
        return ui_type in HtmlPageOutputUserInterfaceType
