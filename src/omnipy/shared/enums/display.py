from typing import Literal

from typing_extensions import TypeIs

from omnipy.util.literal_enum import LiteralEnum


class DisplayDimensionsUpdateMode(LiteralEnum[str]):
    """
    Specifies how display dimensions should be updated.
    """

    Literals = Literal['auto', 'fixed']

    AUTO: Literal['auto'] = 'auto'
    """
    Automatically updates the `width` and `height` dimension configs of the
    relevant interface output based on the currently available display area
    every time some output renders or (in some cases) when there is a change
    in the available display area (e.g. a window is resized). Automatic
    updates might not work in cases when the available display area can be
    automatically determined (which is e.g. the case for `PYCHARM_TERMINAL`
    and `PYCHARM_IPYTHON` user interface types). In those cases, the
    specified dimensions are kept unchanged. Default values are defined for
    each type of user interface .
    """

    FIXED: Literal['fixed'] = 'fixed'
    """
    Updates the `width` and `height` dimension config according to the
    available display area only once at the start of the program. Default
    values are defined for each type of user interface. The default values
    can be overridden by the user in the configs, however users are then
    advised to first set `dims_mode` to `FIXED` even when the current
    display area cannot be automatically determined. Setting `dims_mode` to
    `FIXED` retains the current dimensions at the time of the setting.
    """


class PrettyPrinterLib(LiteralEnum[str]):
    """
    Supported libraries for pretty printing of various data structures.

    Comparison of RICH and DEVTOOLS for Python structures: the outputs are
    more or less the same. However, the RICH library formats the width of
    the output on a per-item basis, while the DEVTOOLS library formats the
    width of the output based on the maximum width of the output. This means
    that the RICH library will in many cases produce a more compact output,
    which is typically recommended. However, the DEVTOOLS library might be
    more suitable for visualizing Pydantic models with debug_mode set to
    `True`, as it is specifically designed for that purpose.
    """

    Literals = Literal['rich', 'devtools', 'compact-json', 'text', 'hexdump', 'auto']

    RICH: Literal['rich'] = 'rich'
    """
    The pretty printer of Rich library
    (https://rich.readthedocs.io/en/stable/), a general-purpose formatter
    of Python objects. This is the default value.
    """

    DEVTOOLS: Literal['devtools'] = 'devtools'
    """
    The pretty printer of the Devtools library
    (https://python-devtools.helpmanual.io/), a general-purpose formatter
    of Python objects and specifically designed for visualizing Pydantic
    models.
    """

    COMPACT_JSON: Literal['compact-json'] = 'compact-json'
    """
    The compact-json library (https://github.com/masaccio/compact-json),
    which is used for compact formatting of JSON data structures.
    """

    TEXT: Literal['text'] = 'text'
    """
    The plain text pretty printer, which is used for displaying plain text
    content.
    """

    HEXDUMP: Literal['hexdump'] = 'hexdump'
    """
    Hexdump pretty printer based on [simple-hexdump](https://pypi.org/project/simple-hexdump/)
    for displaying binary content.
    """

    AUTO: Literal['auto'] = 'auto'
    """
    Automatically selects the pretty printer based on:
    1. The content type
    2. The `syntax` config parameter
    """


# TODO: Update to hexdump implementation with utf8 support


class JsonSyntaxLanguage(LiteralEnum[str]):
    Literals = Literal['json', 'json-ld']

    JSON: Literal['json'] = 'json'
    JSON_LD: Literal['json-ld'] = 'json-ld'


class TextSyntaxLanguage(LiteralEnum[str]):
    Literals = Literal['text',
                       'yaml',
                       'xml',
                       'toml',
                       'bash',
                       'sql',
                       'html',
                       'markdown',
                       'css',
                       'numpy',
                       'sparql',
                       'tex']

    TEXT: Literal['text'] = 'text'
    YAML: Literal['yaml'] = 'yaml'
    XML: Literal['xml'] = 'xml'
    TOML: Literal['toml'] = 'toml'
    BASH: Literal['bash'] = 'bash'
    SQL: Literal['sql'] = 'sql'
    HTML: Literal['html'] = 'html'
    MARKDOWN: Literal['markdown'] = 'markdown'
    NUMPY: Literal['numpy'] = 'numpy'
    CSS: Literal['css'] = 'css'
    SPARQL: Literal['sparql'] = 'sparql'
    TEX: Literal['tex'] = 'tex'


class HexdumpSyntaxLanguage(LiteralEnum[str]):
    Literals = Literal['hexdump']

    HEXDUMP: Literal['hexdump'] = 'hexdump'


class PythonSyntaxLanguage(LiteralEnum[str]):
    Literals = Literal['python']

    PYTHON: Literal['python'] = 'python'


class SyntaxLanguage(JsonSyntaxLanguage,
                     TextSyntaxLanguage,
                     HexdumpSyntaxLanguage,
                     PythonSyntaxLanguage):
    """
    Supported languages for syntax recognition and highlighting.

    A selected subset of the lexer languages supported by the Pygments
    library (https://pygments.org/languages/), assumed to be the ones most
    relevant for Omnipy.
    """

    Literals = Literal[JsonSyntaxLanguage.Literals,
                       TextSyntaxLanguage.Literals,
                       HexdumpSyntaxLanguage.Literals,
                       PythonSyntaxLanguage.Literals]

    @classmethod
    def is_syntax_language(cls, syntax: str) -> 'TypeIs[SyntaxLanguage.Literals]':
        """
        Checks if the given syntax is a Syntax language.
        """
        return syntax in SyntaxLanguage

    @classmethod
    def is_json_syntax(cls, syntax: str) -> TypeIs[JsonSyntaxLanguage.Literals]:
        """
        Checks if the given syntax is a JSON syntax.
        """
        return syntax in JsonSyntaxLanguage

    @classmethod
    def is_text_syntax(cls, syntax: str) -> TypeIs[TextSyntaxLanguage.Literals]:
        """
        Checks if the given syntax is a general text syntax.
        """
        return syntax in TextSyntaxLanguage

    @classmethod
    def is_hexdump_syntax(cls, syntax: str) -> TypeIs[HexdumpSyntaxLanguage.Literals]:
        """
        Checks if the given syntax is the syntax for displaying binary as hexdump
        """
        return syntax in HexdumpSyntaxLanguage

    @classmethod
    def is_python_syntax(cls, syntax: str) -> TypeIs[PythonSyntaxLanguage.Literals]:
        """
        Checks if the given syntax is a Python variant.
        """
        return syntax in PythonSyntaxLanguage


class DisplayColorSystem(LiteralEnum[str]):
    """
    Supported display color systems for syntax highlighting.

    The color systems map to the color systems provided by the Rich library
    (https://rich.readthedocs.io/en/stable/console.html#color-systems).
    The names of the Omnipy attributes have been slightly modified to be
    more descriptive.
    """

    Literals = Literal['auto', 'standard', '256', 'truecolor', 'windows']

    AUTO: Literal['auto'] = 'auto'
    """
    The default color system, which is automatically detected based on the
    terminal capabilities. This is the default value.
    """

    ANSI_16: Literal['standard'] = 'standard'
    """
    The standard ANSI color system, which supports 16 colors.
    """

    ANSI_256: Literal['256'] = '256'
    """
    The extended ANSI color system, which supports 256 colors.
    """

    ANSI_RGB: Literal['truecolor'] = 'truecolor'
    """
    The truecolor ANSI color system, which supports 16 million colors. Most
    modern terminals support this color system.
    """

    WINDOWS_LEGACY: Literal['windows'] = 'windows'
    """
    The legacy Windows color system, for backwards compatibility with older
    Windows terminals.
    """


class HorizontalOverflowMode(LiteralEnum[str]):
    """
    Horizontal overflow modes for the output. Horizontal overflow modes have
    no effect on layout panels.

    The horizontal overflow modes are:
    - `ELLIPSIS`: Adds an ellipsis (...) at the end of the line if it
        exceeds the width.
    - `CROP`: Crops the line to fit within the width, without adding an
        ellipsis.
    - `WORD_WRAP`: Wraps the line to the next line if it exceeds the
        width, breaking according to the specified syntax language.
    """

    Literals = Literal['ellipsis', 'crop', 'word_wrap']

    ELLIPSIS: Literal['ellipsis'] = 'ellipsis'
    CROP: Literal['crop'] = 'crop'
    WORD_WRAP: Literal['word_wrap'] = 'word_wrap'


# TODO: Improve word wrap support for layout panels.


class PanelDesign(LiteralEnum[str]):
    """
    Visual design for the layout of the output.

    The layout designs are:
    - `TABLE`: The output is displayed as a simple table grid
    - `TABLE_SHOW_STYLE`: The output is displayed as a simple table grid
    - `PANELS`: The output is displayed as a set of panels
    """

    Literals = Literal['table', 'table_show_style', 'panels']

    TABLE: Literal['table'] = 'table'
    TABLE_SHOW_STYLE: Literal['table_show_style'] = 'table_show_style'
    PANELS: Literal['panels'] = 'panels'


class VerticalOverflowMode(LiteralEnum[str]):
    """
    Vertical overflow modes for the output. Vertical overflow modes have
    no effect on layout panels.

    The vertical overflow modes are:
    - `CROP_TOP`: Crops the top of the output if it exceeds the height.
    - `CROP_BOTTOM`: Crops the bottom of the output if it exceeds the
        height.
    """

    Literals = Literal['crop_top', 'crop_bottom', 'ellipsis_top', 'ellipsis_bottom']

    CROP_TOP: Literal['crop_top'] = 'crop_top'
    CROP_BOTTOM: Literal['crop_bottom'] = 'crop_bottom'
    ELLIPSIS_TOP: Literal['ellipsis_top'] = 'ellipsis_top'
    ELLIPSIS_BOTTOM: Literal['ellipsis_bottom'] = 'ellipsis_bottom'


class MaxTitleHeight(LiteralEnum[int]):
    Literals = Literal[-1, 0, 1, 2]

    AUTO: Literal[-1] = -1
    ZERO: Literal[0] = 0
    ONE: Literal[1] = 1
    TWO: Literal[2] = 2


class Justify(LiteralEnum[str]):
    """
    Justification modes for the output.

    The justification modes are:
    - `LEFT`: Left-justified text.
    - `RIGHT`: Right-justified text.
    - `CENTER`: Centered text.
    """

    Literals = Literal['left', 'center', 'right']

    LEFT: Literal['left'] = 'left'
    CENTER: Literal['center'] = 'center'
    RIGHT: Literal['right'] = 'right'
