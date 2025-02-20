from enum import Enum

from pygments.lexers import get_lexer_by_name
from pygments.styles import get_style_by_name

from omnipy.util._pydantic import ConfigDict, dataclass, Extra, NonNegativeInt, validator

MAX_TERMINAL_SIZE = 2**16 - 1


class PrettyPrinterLib(str, Enum):
    RICH = 'rich'
    DEVTOOLS = 'devtools'


class SyntaxLanguage(str, Enum):
    """
    A selected subset of the languages supported by the Pygments library
    (https://pygments.org/languages/), assumed to be the ones most relevant for Omnipy. All
    parameters accepting a syntax language should also accept a string with the name of the
    language, allowing the user to specify a language not present in this enum.
    """
    PYTHON = 'python'
    JSON = 'json'
    JSON_LD = 'json-ld'
    YAML = 'yaml'
    XML = 'xml'
    TOML = 'toml'
    BASH = 'bash'
    SQL = 'sql'
    HTML = 'html'
    MARKDOWN = 'markdown'
    CSS = 'css'
    NUMPY = 'numpy'
    SPARQL = 'sparql'
    TEX = 'tex'


class SpecialColorStyles(str, Enum):
    """
    Color styles that make use of the ANSI color settings in the terminal instead of overriding with
    a predefined color style.
    """
    ANSI_DARK = 'ansi_dark'
    ANSI_LIGHT = 'ansi_light'


class HighContrastLightColorStyles(str, Enum):
    """
    High contrast light color styles for syntax highlighting, provided by the Pygments library.
    """
    BW = 'bw'
    DEFAULT = 'default'
    SAS = 'sas'
    STAROFFICE = 'staroffice'
    XCODE = 'xcode'


class HighContrastDarkColorStyles(str, Enum):
    """
    High contrast dark color styles for syntax highlighting, provided by the Pygments library.
    """
    GITHUB_DARK = 'github-dark'
    LIGHTBULB = 'lightbulb'
    MONOKAI = 'monokai'
    RRT = 'rrt'


class LowerContrastLightColorStyles(str, Enum):
    """
    Lower contrast light color styles for syntax highlighting, provided by the Pygments library.
    """
    ABAP = 'abap'
    ALGOL = 'algol'
    ALGOL_NU = 'algol_nu'
    ARDUINO = 'arduino'
    AUTUMN = 'autumn'
    BORLAND = 'borland'
    COLORFUL = 'colorful'
    EMACS = 'emacs'
    FRIENDLY_GRAYSCALE = 'friendly_grayscale'
    FRIENDLY = 'friendly'
    GRUVBOX_LIGHT = 'gruvbox-light'
    IGOR = 'igor'
    LOVELACE = 'lovelace'
    MANNI = 'manni'
    MURPHY = 'murphy'
    PARAISO_LIGHT = 'paraiso-light'
    PASTIE = 'pastie'
    PERLDOC = 'perldoc'
    RAINBOW_DASH = 'rainbow_dash'
    SOLARIZED_LIGHT = 'solarized-light'
    STATA_LIGHT = 'stata-light'
    TANGO = 'tango'
    TRAC = 'trac'
    VS = 'vs'


class LowerContrastDarkColorStyles(str, Enum):
    """
    Lower contrast dark color styles for syntax highlighting, provided by the Pygments library.
    """
    COFFEE = 'coffee'
    DRACULA = 'dracula'
    FRUITY = 'fruity'
    GRUVBOX_DARK = 'gruvbox-dark'
    INKPOT = 'inkpot'
    MATERIAL = 'material'
    NATIVE = 'native'
    NORD_DARKER = 'nord-darker'
    NORD = 'nord'
    ONE_DARK = 'one-dark'
    PARAISO_DARK = 'paraiso-dark'
    SOLARIZED_DARK = 'solarized-dark'
    STATA_DARK = 'stata-dark'
    VIM = 'vim'
    ZENBURN = 'zenburn'


ColorStyles = (
    SpecialColorStyles | HighContrastLightColorStyles | HighContrastDarkColorStyles
    | LowerContrastLightColorStyles
    | LowerContrastDarkColorStyles)
"""
All color styles for syntax highlighting, provided by the Pygments library.
All parameters accepting a color style should also accept a string with the name of the style,
allowing the user to specify imported or custom styles not present in these enums.
"""


class HorizontalOverflowMode(str, Enum):
    """
    Horizontal overflow modes for the console output.
    """
    ELLIPSIS = 'ellipsis'
    CROP = 'crop'
    WORD_WRAP = 'word_wrap'


class VerticalOverflowMode(str, Enum):
    """
    Vertical overflow modes for the console output.
    """
    CROP_TOP = 'crop_top'
    CROP_BOTTOM = 'crop_bottom'


@dataclass(kw_only=True, config=ConfigDict(extra=Extra.forbid, validate_assignment=True))
class OutputConfig:
    indent_tab_size: NonNegativeInt = 2
    debug_mode: bool = False
    pretty_printer: PrettyPrinterLib = PrettyPrinterLib.RICH
    language: SyntaxLanguage | str | None = SyntaxLanguage.PYTHON
    color_style: ColorStyles | str | None = SpecialColorStyles.ANSI_LIGHT
    horizontal_overflow_mode: HorizontalOverflowMode = HorizontalOverflowMode.WORD_WRAP
    vertical_overflow_mode: VerticalOverflowMode = VerticalOverflowMode.CROP_BOTTOM

    @validator('language')
    def validate_language(cls, value: SyntaxLanguage | str | None) -> SyntaxLanguage | str | None:
        if value is None:
            return None
        if isinstance(value, SyntaxLanguage):
            return value
        if get_lexer_by_name(value):
            return value

    @validator('color_style')
    def validate_color_style(cls, value: ColorStyles | str | None) -> ColorStyles | str | None:
        if value is None:
            return None
        if isinstance(value, ColorStyles):
            return value
        if get_style_by_name(value):
            return value
