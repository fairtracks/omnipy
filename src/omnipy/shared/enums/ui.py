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
    Literals = Literal['pycharm_terminal']

    PYCHARM_TERMINAL: Literal['pycharm_terminal'] = 'pycharm_terminal'
    f"""
    The console and/or terminal of the JetBrains PyCharm IDE running with
    the Python interactive interpreter (REPL). {_PYCHARM_NOTE}
    """


class PlainTerminalUserInterfaceType(PlainTerminalEmbeddedUserInterfaceType, LiteralEnum[str]):
    Literals = Literal['terminal', PlainTerminalEmbeddedUserInterfaceType.Literals, 'unknown']

    TERMINAL: Literal['terminal'] = 'terminal'
    """
    A standard Python interactive interpreter (REPL), running within
    terminal-emulation software, such as the builtin "Terminal" app on Mac
    OS or GNOME Terminal on Linux, through a SSH connection to a remote
    server,  or directly on a console.
    """

    UNKNOWN: Literal['unknown'] = 'unknown'
    """
    The `UNKNOWN` user interface type is used when the user interface type
    cannot be determined. This will in practice produce the same output as
    for the `TERMINAL` display type, As is default for terminals, we try to
    autodetect color capabilities (see `DisplayColorSystem.AUTO`). (such as
    ANSI escape codes for color and text formatting) are available.
    """


class IpythonEmbeddedTerminalUserInterfaceType(LiteralEnum[str]):
    Literals = Literal['pycharm_ipython']

    PYCHARM_IPYTHON: Literal['pycharm_ipython'] = 'pycharm_ipython'
    f"""
    The console and/or terminal of the JetBrains PyCharm IDE running with
    the IPython interactive interpreter (REPL).
     {_IPYTHON_DESCRIPTION} {_PYCHARM_NOTE}
    """


class IpythonTerminalUserInterfaceType(IpythonEmbeddedTerminalUserInterfaceType, LiteralEnum[str]):
    Literals = Literal['ipython', IpythonEmbeddedTerminalUserInterfaceType.Literals]

    IPYTHON: Literal['ipython'] = 'ipython'
    """
    Same as `TERMINAL`, but running within the IPython interactive
    interpreter (REPL). The IPython interpreter is a more advanced
    interactive interpreter that provides additional features such as syntax
    highlighting, tab completion, and better error messages.
    """


class TerminalUserInterfaceType(PlainTerminalUserInterfaceType, IpythonTerminalUserInterfaceType):
    Literals = Literal[
        PlainTerminalUserInterfaceType.Literals,
        IpythonTerminalUserInterfaceType.Literals,
    ]


class JupyterEmbeddedUserInterfaceType(LiteralEnum[str]):
    Literals = Literal['pycharm_jupyter']

    PYCHARM_JUPYTER: Literal['pycharm_jupyter'] = 'pycharm_jupyter'
    f"""
    A Jupyter notebook running within the user interface of the JetBrains
    PyCharm IDE.
     {_JUPYTER_DESCRIPTION} {_PYCHARM_NOTE}.
    """


class SupportsDarkTerminalBgDetection(TerminalUserInterfaceType, JupyterEmbeddedUserInterfaceType):
    Literals = Literal[
        TerminalUserInterfaceType.Literals,
        JupyterEmbeddedUserInterfaceType.Literals,
    ]


class JupyterInBrowserUserInterfaceType(LiteralEnum[str]):
    Literals = Literal['jupyter']

    JUPYTER: Literal['jupyter'] = 'jupyter'
    f"""
    A Jupyter notebook or JupyterLab environment opened from a web browser.
     {_JUPYTER_DESCRIPTION}
    """


class JupyterUserInterfaceType(
        JupyterEmbeddedUserInterfaceType,
        JupyterInBrowserUserInterfaceType,
):
    Literals = Literal[
        JupyterEmbeddedUserInterfaceType.Literals,
        JupyterInBrowserUserInterfaceType.Literals,
    ]


class BrowserPageUserInterfaceType(LiteralEnum[str]):
    Literals = Literal['browser-page']

    BROWSER_PAGE: Literal['browser-page'] = 'browser-page'
    f"""
    {_BROWSER_DESCRIPTION} The `BROWSER_PAGE` UI type displays content as
    full web pages.
    """


class BrowserTagUserInterfaceType(LiteralEnum[str]):
    Literals = Literal['browser-tag']

    BROWSER_TAG: Literal['browser-tag'] = 'browser-tag'
    f"""
    {_BROWSER_DESCRIPTION} The `BROWSER_TAG` UI type displays content as
    standalone HTML elements, for HTML code that can be embedded in other
    HTML documents.
    """


class BrowserUserInterfaceType(BrowserPageUserInterfaceType, BrowserTagUserInterfaceType):
    Literals = Literal[BrowserPageUserInterfaceType.Literals, BrowserTagUserInterfaceType.Literals]


class RgbColorUserInterfaceType(PlainTerminalEmbeddedUserInterfaceType,
                                IpythonEmbeddedTerminalUserInterfaceType,
                                JupyterUserInterfaceType,
                                BrowserUserInterfaceType):
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
    Literals = Literal[
        PlainTerminalUserInterfaceType.Literals,
        IpythonTerminalUserInterfaceType.Literals,
        JupyterEmbeddedUserInterfaceType.Literals,
    ]


class HtmlTagOutputUserInterfaceType(
        JupyterInBrowserUserInterfaceType,
        BrowserTagUserInterfaceType,
):
    Literals = Literal[
        JupyterInBrowserUserInterfaceType.Literals,
        BrowserTagUserInterfaceType.Literals,
    ]


class HtmlPageOutputUserInterfaceType(BrowserPageUserInterfaceType):
    Literals = Literal[BrowserPageUserInterfaceType.Literals]


class AutoDetectableUserInterfaceType(
        PlainTerminalUserInterfaceType,
        IpythonTerminalUserInterfaceType,
        JupyterUserInterfaceType,
):
    """
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
    """
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
    """
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
    """
    The `AUTO` user interface type is used to describe that the user
    interface type has not yet been determined, and that it should be
    automatically determined by Omnipy. This is the default value.
    """
    @classmethod
    def is_plain_terminal(
            cls, ui_type: 'UserInterfaceType.Literals'
    ) -> TypeIs[PlainTerminalUserInterfaceType.Literals]:
        f"""
        Check whether the user interface type refers to any plain
        (non-IPython) terminal UI types. {_UNKNOWN_NOTE} {_TYPEIS_NARROW_NOTE}
        """
        return ui_type in PlainTerminalUserInterfaceType

    @classmethod
    def is_ipython_terminal(
            cls, ui_type: 'UserInterfaceType.Literals'
    ) -> TypeIs[IpythonTerminalUserInterfaceType.Literals]:
        f"""
        Check whether the user interface type refers to an IPython
        interactive interpreter (REPL). {_TYPEIS_NARROW_NOTE}
        """
        return ui_type in IpythonTerminalUserInterfaceType

    @classmethod
    def is_terminal(
            cls,
            ui_type: 'UserInterfaceType.Literals') -> TypeIs[TerminalUserInterfaceType.Literals]:
        f"""
        Check whether the user interface type refers to any type of terminal
        UI types, including IPython and plain terminal.
         {_UNKNOWN_NOTE} {_TYPEIS_NARROW_NOTE}
        """
        return ui_type in TerminalUserInterfaceType

    @classmethod
    def is_jupyter_embedded(
            cls, ui_type: 'UserInterfaceType.Literals'
    ) -> TypeIs[JupyterEmbeddedUserInterfaceType.Literals]:
        f"""
        Check whether the user interface type refers to a Jupyter notebook
        embedded within other software, such as an IDE.
         {_TYPEIS_NARROW_NOTE}
        """
        return ui_type in JupyterEmbeddedUserInterfaceType

    @classmethod
    def supports_dark_terminal_bg_detection(
            cls, ui_type: 'UserInterfaceType.Literals'
    ) -> TypeIs[SupportsDarkTerminalBgDetection.Literals]:
        f"""
        Check whether the user interface type supports detection of dark
        background color by checking environment variables or using
        ANSI terminal functionality. This is typically the case for
        Jupyter notebooks embedded in IDEs, such as PyCharm, or other
        terminals.
         {_TYPEIS_NARROW_NOTE}
        """
        return ui_type in SupportsDarkTerminalBgDetection

    @classmethod
    def is_jupyter_in_browser(
        cls, ui_type: 'UserInterfaceType.Literals'
    ) -> TypeIs[JupyterInBrowserUserInterfaceType.Literals]:
        f"""
        Check whether the user interface type refers to a Jupyter notebook
        or JupyterLab environment opened from a web browser.
         {_TYPEIS_NARROW_NOTE}
        """
        return ui_type in JupyterInBrowserUserInterfaceType

    @classmethod
    def is_jupyter(
            cls,
            ui_type: 'UserInterfaceType.Literals') -> TypeIs[JupyterUserInterfaceType.Literals]:
        f"""
        Check whether the user interface type refers to a Jupyter notebook
        or JupyterLab environment in any context.
         {_TYPEIS_NARROW_NOTE}
        """
        return ui_type in JupyterUserInterfaceType

    @classmethod
    def is_browser(
            cls,
            ui_type: 'UserInterfaceType.Literals') -> TypeIs[BrowserUserInterfaceType.Literals]:
        f"""
        Check whether the user interface type refers to a web browser.
         {_TYPEIS_NARROW_NOTE}
        """
        return ui_type in BrowserUserInterfaceType

    @classmethod
    def supports_rgb_color_output(
            cls,
            ui_type: 'UserInterfaceType.Literals') -> TypeIs[RgbColorUserInterfaceType.Literals]:
        f"""
        Check whether the user interface type refers to any UI types that
        support RGB color output.
         {_TYPEIS_NARROW_NOTE}
        """
        return ui_type in RgbColorUserInterfaceType

    @classmethod
    def requires_terminal_output(
            cls, ui_type: 'UserInterfaceType.Literals'
    ) -> TypeIs[TerminalOutputUserInterfaceType.Literals]:
        f"""
        Check whether the user interface type refers to any UI types that
        require output with ANSI terminal encoding for colors and styles. If
        user interface type is unknown, we assume it is a terminal and try
        to autodetect color capabilities, as default for terminals (see
        `DisplayColorSystem.AUTO`).
         {_TYPEIS_NARROW_NOTE}
        """
        return ui_type in TerminalOutputUserInterfaceType

    @classmethod
    def requires_html_tag_output(
            cls, ui_type: 'UserInterfaceType.Literals'
    ) -> TypeIs[HtmlTagOutputUserInterfaceType.Literals]:
        f"""
        Check whether the user interface type refers to any UI types that
        require output as self-contained HTML tags for embedding in other
        HTML pages.
         {_TYPEIS_NARROW_NOTE}
        """
        return ui_type in HtmlTagOutputUserInterfaceType

    @classmethod
    def requires_html_page_output(
            cls, ui_type: 'UserInterfaceType.Literals'
    ) -> TypeIs[HtmlPageOutputUserInterfaceType.Literals]:
        f"""
        Check whether the user interface type refers to any UI types that
        require output as a full HTML page.
         {_TYPEIS_NARROW_NOTE}
        """
        return ui_type in HtmlPageOutputUserInterfaceType
