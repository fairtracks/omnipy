from enum import Enum
from textwrap import dedent

import pygments.lexers
import pygments.styles
import pygments.util

from omnipy.data._display.styles.dynamic_styles import install_base16_theme
import omnipy.util._pydantic as pyd

MAX_TERMINAL_SIZE = 2**16 - 1


class PrettyPrinterLib(str, Enum):
    """
    Supported libraries for pretty printing of Python data structures.

    For most data structures, the outputs are more or less the same.
    However, the RICH library formats the width of the output on a per-item
    basis, while the DEVTOOLS library formats the width of the output based
    on the maximum width of the output. This means that the RICH library
    will in many cases produce a more compact output, which is typically
    recommended.

    The libraries are:
    - `RICH`: The Rich library (https://rich.readthedocs.io/en/stable/).
        This is the default value.
    - `DEVTOOLS`: The Python Devtools library
        (https://python-devtools.helpmanual.io/). Included for future
        testing for data types such as numpy arrays, but might become
        deprecated in the future.
    """
    RICH = 'rich'
    DEVTOOLS = 'devtools'


class SyntaxLanguage(str, Enum):
    """
    Supported languages for syntax recognition and highlighting.

    A selected subset of the lexer languages supported by the Pygments
    library (https://pygments.org/languages/), assumed to be the ones most
    relevant for Omnipy.
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


class ConsoleColorSystem(str, Enum):
    """
    Supported console color systems for syntax highlighting.

    The color systems map to the color systems provided by the Rich library
    (https://rich.readthedocs.io/en/stable/console.html#color-systems).
    The names have been slightly modified to be more descriptive.

    The color systems are:
    - `AUTO`: The default color system, which is automatically detected
        based on the terminal capabilities. This is the default value.
    - `ANSI_16`: The standard ANSI color system, which supports 16 colors.
    - `ANSI_256`: The extended ANSI color system, which supports 256 colors.
    - `ANSI_RGB`: The truecolor ANSI color system, which supports 16 million
        colors. Most modern terminals support this color system.
    - `WINDOWS_LEGACY`: The legacy Windows color system, for backwards
        compatibility with older Windows terminals.
    """
    AUTO = 'auto'
    ANSI_16 = 'standard'
    ANSI_256 = '256'
    ANSI_RGB = 'truecolor'
    WINDOWS_LEGACY = 'windows'


class RecommendedColorStyles(str, Enum):
    """
    Recommended color styles for syntax highlighting, provided through the
    Pygments and Rich libraries.

    The Omnipy Selenized styles are based on the Selenized color scheme by
    Jan Warchoł (https://github.com/jan-warchol/selenized).

    Features:
    - Easy on the eyes.
    - Beautiful, vibrant and easily distinguishable accent colors.
    - Great readability and better compatibility with Web Content
      Accessibility Guidelines.

    The Omnipy adaptations features slightly less contrast for comment
    colors, which is offset by the use of italics to make them stand out.
    These color styles work well with transparent backgrounds to blend in
    with the current terminal theme. For best results, you should change
    the background color of the terminal (or the complete color theme) to
    align with the Omnipy Selenized styles.

    The Omnipy Selenized styles are available in four variants:
    - Black: A slightly soft dark theme with an almost black background,
             suitable also on a fully black background
    - Dark: A dark theme on a dark bluish background,
            a bit harsh on a fully black background
    - Light: A soft light theme on an off-white background,
             suitable also on a fully white background for a softer feel
    - White: A light theme on a fully white background

    The ANSI color settings from the Rich library are set as default out of
    pragmatism, as they make use of the predefined colors of the terminal
    instead of overriding with a predefined color style. The ANSI dark
    variant seems to be slightly more readable across both light and dark
    terminal themes. However, if you are using a light theme, you may want
    to use the light variant of the ANSI color style.

    The ANSI color styles are provided to make Omnipy work ok on a wider
    range of terminals, but they are not recommended for use in the long
    run. For best results, you should switch to the light or white variants
    of the Omnipy Selenized styles, or to another color style of your
    choice.
    """
    ANSI_DARK = 'ansi_dark'
    ANSI_LIGHT = 'ansi_light'
    OMNIPY_SELENIZED_BLACK = 'omnipy-selenized-black'
    OMNIPY_SELENIZED_DARK = 'omnipy-selenized-dark'
    OMNIPY_SELENIZED_LIGHT = 'omnipy-selenized-light'
    OMNIPY_SELENIZED_WHITE = 'omnipy-selenized-white'


_GENERAL_COLOR_STYLE_DOCSTRING = dedent("""
    All color styles are provided through the Pygments library. See
    the Pygment docs for an overview of the Pygment-included styles:
    https://pygments.org/styles/

    The "TB16" prefix indicates that the style is based on the Base16 color
    framework and auto-imported from the [color scheme repository]
    (https://github.com/tinted-theming/schemes) of the [Tinted Theming]
    (https://github.com/tinted-theming) project. The Base16 color framework
    was designed by Chris Kempson (https://github.com/chriskempson/base16).

    For a gallery of the "Tinted Theming" Base16 color schemes, see
    https://tinted-theming.github.io/tinted-gallery/.

    The mapping of the Base16 color framework onto the Pygments library is
    Omnipy-specific, and available as the function
    `get_styles_from_base16_colors()` in the
    `omnipy.data._display.styles.dynamic_styles` module.
    """)


class DarkHighContrastColorStyles(str, Enum):
    __doc__ = dedent("""
        High contrast dark color styles for syntax highlighting.
        """) + _GENERAL_COLOR_STYLE_DOCSTRING

    GITHUB_DARK = 'github-dark'
    LIGHTBULB = 'lightbulb'
    MONOKAI = 'monokai'
    RRT = 'rrt'
    TB16_3024 = 'tb16-3024'
    TB16_APATHY = 'tb16-apathy'
    TB16_ASHES = 'tb16-ashes'
    TB16_ATELIER_CAVE = 'tb16-atelier-cave'
    TB16_ATELIER_DUNE = 'tb16-atelier-dune'
    TB16_ATELIER_ESTUARY = 'tb16-atelier-estuary'
    TB16_ATELIER_FOREST = 'tb16-atelier-forest'
    TB16_ATELIER_HEATH = 'tb16-atelier-heath'
    TB16_ATELIER_LAKESIDE = 'tb16-atelier-lakeside'
    TB16_ATELIER_PLATEAU = 'tb16-atelier-plateau'
    TB16_ATELIER_SAVANNA = 'tb16-atelier-savanna'
    TB16_ATELIER_SEASIDE = 'tb16-atelier-seaside'
    TB16_ATELIER_SULPHURPOOL = 'tb16-atelier-sulphurpool'
    TB16_ATLAS = 'tb16-atlas'
    TB16_AYU_DARK = 'tb16-ayu-dark'
    TB16_AYU_MIRAGE = 'tb16-ayu-mirage'
    TB16_AZTEC = 'tb16-aztec'
    TB16_BESPIN = 'tb16-bespin'
    TB16_BLACK_METAL_BATHORY = 'tb16-black-metal-bathory'
    TB16_BLACK_METAL_BURZUM = 'tb16-black-metal-burzum'
    TB16_BLACK_METAL_DARK_FUNERAL = 'tb16-black-metal-dark-funeral'
    TB16_BLACK_METAL_GORGOROTH = 'tb16-black-metal-gorgoroth'
    TB16_BLACK_METAL_IMMORTAL = 'tb16-black-metal-immortal'
    TB16_BLACK_METAL_KHOLD = 'tb16-black-metal-khold'
    TB16_BLACK_METAL_MARDUK = 'tb16-black-metal-marduk'
    TB16_BLACK_METAL_MAYHEM = 'tb16-black-metal-mayhem'
    TB16_BLACK_METAL_NILE = 'tb16-black-metal-nile'
    TB16_BLACK_METAL_VENOM = 'tb16-black-metal-venom'
    TB16_BLACK_METAL = 'tb16-black-metal'
    TB16_BLUEFOREST = 'tb16-blueforest'
    TB16_BLUEISH = 'tb16-blueish'
    TB16_BREWER = 'tb16-brewer'
    TB16_BRIGHT = 'tb16-bright'
    TB16_CAROLINE = 'tb16-caroline'
    TB16_CATPPUCCIN_FRAPPE = 'tb16-catppuccin-frappe'
    TB16_CATPPUCCIN_MACCHIATO = 'tb16-catppuccin-macchiato'
    TB16_CATPPUCCIN_MOCHA = 'tb16-catppuccin-mocha'
    TB16_CHALK = 'tb16-chalk'
    TB16_CIRCUS = 'tb16-circus'
    TB16_CLASSIC_DARK = 'tb16-classic-dark'
    TB16_CODESCHOOL = 'tb16-codeschool'
    TB16_COLORS = 'tb16-colors'
    TB16_DA_ONE_BLACK = 'tb16-da-one-black'
    TB16_DA_ONE_GRAY = 'tb16-da-one-gray'
    TB16_DA_ONE_OCEAN = 'tb16-da-one-ocean'
    TB16_DA_ONE_SEA = 'tb16-da-one-sea'
    TB16_DANQING = 'tb16-danqing'
    TB16_DARCULA = 'tb16-darcula'
    TB16_DARKMOSS = 'tb16-darkmoss'
    TB16_DARKTOOTH = 'tb16-darktooth'
    TB16_DARKVIOLET = 'tb16-darkviolet'
    TB16_DECAF = 'tb16-decaf'
    TB16_DEEP_OCEANIC_NEXT = 'tb16-deep-oceanic-next'
    TB16_DEFAULT_DARK = 'tb16-default-dark'
    TB16_DRACULA = 'tb16-dracula'
    TB16_EDGE_DARK = 'tb16-edge-dark'
    TB16_EIGHTIES = 'tb16-eighties'
    TB16_EMBERS = 'tb16-embers'
    TB16_EQUILIBRIUM_DARK = 'tb16-equilibrium-dark'
    TB16_EQUILIBRIUM_GRAY_DARK = 'tb16-equilibrium-gray-dark'
    TB16_ESPRESSO = 'tb16-espresso'
    TB16_EVENOK_DARK = 'tb16-evenok-dark'
    TB16_EVERFOREST_DARK_HARD = 'tb16-everforest-dark-hard'
    TB16_EVERFOREST = 'tb16-everforest'
    TB16_FLAT = 'tb16-flat'
    TB16_FRAMER = 'tb16-framer'
    TB16_GIGAVOLT = 'tb16-gigavolt'
    TB16_GOOGLE_DARK = 'tb16-google-dark'
    TB16_GOTHAM = 'tb16-gotham'
    TB16_GRAYSCALE_DARK = 'tb16-grayscale-dark'
    TB16_GREENSCREEN = 'tb16-greenscreen'
    TB16_GRUBER = 'tb16-gruber'
    TB16_GRUVBOX_DARK_HARD = 'tb16-gruvbox-dark-hard'
    TB16_GRUVBOX_DARK_MEDIUM = 'tb16-gruvbox-dark-medium'
    TB16_GRUVBOX_DARK_PALE = 'tb16-gruvbox-dark-pale'
    TB16_GRUVBOX_DARK_SOFT = 'tb16-gruvbox-dark-soft'
    TB16_GRUVBOX_MATERIAL_DARK_HARD = 'tb16-gruvbox-material-dark-hard'
    TB16_GRUVBOX_MATERIAL_DARK_MEDIUM = 'tb16-gruvbox-material-dark-medium'
    TB16_GRUVBOX_MATERIAL_DARK_SOFT = 'tb16-gruvbox-material-dark-soft'
    TB16_HARDCORE = 'tb16-hardcore'
    TB16_HARMONIC16_DARK = 'tb16-harmonic16-dark'
    TB16_HEETCH = 'tb16-heetch'
    TB16_HELIOS = 'tb16-helios'
    TB16_HOPSCOTCH = 'tb16-hopscotch'
    TB16_HORIZON_DARK = 'tb16-horizon-dark'
    TB16_HORIZON_TERMINAL_DARK = 'tb16-horizon-terminal-dark'
    TB16_HUMANOID_DARK = 'tb16-humanoid-dark'
    TB16_IA_DARK = 'tb16-ia-dark'
    TB16_IRBLACK = 'tb16-irblack'
    TB16_ISOTOPE = 'tb16-isotope'
    TB16_JABUTI = 'tb16-jabuti'
    TB16_KANAGAWA = 'tb16-kanagawa'
    TB16_KATY = 'tb16-katy'
    TB16_KIMBER = 'tb16-kimber'
    TB16_MACINTOSH = 'tb16-macintosh'
    TB16_MARRAKESH = 'tb16-marrakesh'
    TB16_MATERIA = 'tb16-materia'
    TB16_MATERIAL_DARKER = 'tb16-material-darker'
    TB16_MATERIAL_PALENIGHT = 'tb16-material-palenight'
    TB16_MATERIAL = 'tb16-material'
    TB16_MEASURED_DARK = 'tb16-measured-dark'
    TB16_MELLOW_PURPLE = 'tb16-mellow-purple'
    TB16_MOCHA = 'tb16-mocha'
    TB16_MONOKAI = 'tb16-monokai'
    TB16_MOONLIGHT = 'tb16-moonlight'
    TB16_MOUNTAIN = 'tb16-mountain'
    TB16_NEBULA = 'tb16-nebula'
    TB16_NORD = 'tb16-nord'
    TB16_NOVA = 'tb16-nova'
    TB16_OCEAN = 'tb16-ocean'
    TB16_OCEANICNEXT = 'tb16-oceanicnext'
    TB16_ONEDARK_DARK = 'tb16-onedark-dark'
    TB16_ONEDARK = 'tb16-onedark'
    TB16_OUTRUN_DARK = 'tb16-outrun-dark'
    TB16_OXOCARBON_DARK = 'tb16-oxocarbon-dark'
    TB16_PANDORA = 'tb16-pandora'
    TB16_PARAISO = 'tb16-paraiso'
    TB16_PASQUE = 'tb16-pasque'
    TB16_PHD = 'tb16-phd'
    TB16_PINKY = 'tb16-pinky'
    TB16_POP = 'tb16-pop'
    TB16_PORPLE = 'tb16-porple'
    TB16_PRECIOUS_DARK_ELEVEN = 'tb16-precious-dark-eleven'
    TB16_PRECIOUS_DARK_FIFTEEN = 'tb16-precious-dark-fifteen'
    TB16_PRIMER_DARK_DIMMED = 'tb16-primer-dark-dimmed'
    TB16_PRIMER_DARK = 'tb16-primer-dark'
    TB16_PURPLEDREAM = 'tb16-purpledream'
    TB16_QUALIA = 'tb16-qualia'
    TB16_RAILSCASTS = 'tb16-railscasts'
    TB16_REBECCA = 'tb16-rebecca'
    TB16_ROSE_PINE_MOON = 'tb16-rose-pine-moon'
    TB16_ROSE_PINE = 'tb16-rose-pine'
    TB16_SAGA = 'tb16-saga'
    TB16_SANDCASTLE = 'tb16-sandcastle'
    TB16_SELENIZED_BLACK = 'tb16-selenized-black'
    TB16_SELENIZED_DARK = 'tb16-selenized-dark'
    TB16_SETI = 'tb16-seti'
    TB16_SHADES_OF_PURPLE = 'tb16-shades-of-purple'
    TB16_SHADESMEAR_DARK = 'tb16-shadesmear-dark'
    TB16_SILK_DARK = 'tb16-silk-dark'
    TB16_SNAZZY = 'tb16-snazzy'
    TB16_SOLARFLARE = 'tb16-solarflare'
    TB16_SOLARIZED_DARK = 'tb16-solarized-dark'
    TB16_SPACEDUCK = 'tb16-spaceduck'
    TB16_SPACEMACS = 'tb16-spacemacs'
    TB16_SPARKY = 'tb16-sparky'
    TB16_STANDARDIZED_DARK = 'tb16-standardized-dark'
    TB16_STELLA = 'tb16-stella'
    TB16_SUMMERFRUIT_DARK = 'tb16-summerfruit-dark'
    TB16_SYNTH_MIDNIGHT_DARK = 'tb16-synth-midnight-dark'
    TB16_TANGO = 'tb16-tango'
    TB16_TENDER = 'tb16-tender'
    TB16_TERRACOTTA_DARK = 'tb16-terracotta-dark'
    TB16_TOKYO_CITY_DARK = 'tb16-tokyo-city-dark'
    TB16_TOKYO_CITY_TERMINAL_DARK = 'tb16-tokyo-city-terminal-dark'
    TB16_TOKYO_NIGHT_DARK = 'tb16-tokyo-night-dark'
    TB16_TOKYO_NIGHT_STORM = 'tb16-tokyo-night-storm'
    TB16_TOKYODARK_TERMINAL = 'tb16-tokyodark-terminal'
    TB16_TOKYODARK = 'tb16-tokyodark'
    TB16_TOMORROW_NIGHT_EIGHTIES = 'tb16-tomorrow-night-eighties'
    TB16_TOMORROW_NIGHT = 'tb16-tomorrow-night'
    TB16_TUBE = 'tb16-tube'
    TB16_TWILIGHT = 'tb16-twilight'
    TB16_UNIKITTY_DARK = 'tb16-unikitty-dark'
    TB16_UNIKITTY_REVERSIBLE = 'tb16-unikitty-reversible'
    TB16_UWUNICORN = 'tb16-uwunicorn'
    TB16_VESPER = 'tb16-vesper'
    TB16_VICE = 'tb16-vice'
    TB16_WINDOWS_10 = 'tb16-windows-10'
    TB16_WINDOWS_95 = 'tb16-windows-95'
    TB16_WINDOWS_HIGHCONTRAST = 'tb16-windows-highcontrast'
    TB16_WINDOWS_NT = 'tb16-windows-nt'
    TB16_WOODLAND = 'tb16-woodland'
    TB16_XCODE_DUSK = 'tb16-xcode-dusk'
    TB16_ZENBONES = 'tb16-zenbones'
    TB16_ZENBURN = 'tb16-zenburn'


class DarkLowContrastColorStyles(str, Enum):
    __doc__ = dedent("""
        Lower contrast dark color styles for syntax highlighting.
        """) + _GENERAL_COLOR_STYLE_DOCSTRING

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
    TB16_APPRENTICE = 'tb16-apprentice'
    TB16_BROGRAMMER = 'tb16-brogrammer'
    TB16_BRUSHTREES_DARK = 'tb16-brushtrees-dark'
    TB16_ERIS = 'tb16-eris'
    TB16_EVA_DIM = 'tb16-eva-dim'
    TB16_EVA = 'tb16-eva'
    TB16_ICY = 'tb16-icy'
    TB16_LIME = 'tb16-lime'
    TB16_MATERIAL_VIVID = 'tb16-material-vivid'
    TB16_PAPERCOLOR_DARK = 'tb16-papercolor-dark'
    TB16_PICO = 'tb16-pico'
    TB16_SUMMERCAMP = 'tb16-summercamp'
    TB16_TAROT = 'tb16-tarot'
    TB16_TOKYO_NIGHT_MOON = 'tb16-tokyo-night-moon'
    TB16_TOKYO_NIGHT_TERMINAL_DARK = 'tb16-tokyo-night-terminal-dark'
    TB16_TOKYO_NIGHT_TERMINAL_STORM = 'tb16-tokyo-night-terminal-storm'
    TB16_VULCAN = 'tb16-vulcan'


class LightHighContrastColorStyles(str, Enum):
    __doc__ = dedent("""
        High contrast light color styles for syntax highlighting.
        """) + _GENERAL_COLOR_STYLE_DOCSTRING

    BW = 'bw'
    DEFAULT = 'default'
    SAS = 'sas'
    STAROFFICE = 'staroffice'
    XCODE = 'xcode'
    TB16_ATELIER_CAVE_LIGHT = 'tb16-atelier-cave-light'
    TB16_ATELIER_DUNE_LIGHT = 'tb16-atelier-dune-light'
    TB16_ATELIER_ESTUARY_LIGHT = 'tb16-atelier-estuary-light'
    TB16_ATELIER_FOREST_LIGHT = 'tb16-atelier-forest-light'
    TB16_ATELIER_HEATH_LIGHT = 'tb16-atelier-heath-light'
    TB16_ATELIER_LAKESIDE_LIGHT = 'tb16-atelier-lakeside-light'
    TB16_ATELIER_PLATEAU_LIGHT = 'tb16-atelier-plateau-light'
    TB16_ATELIER_SAVANNA_LIGHT = 'tb16-atelier-savanna-light'
    TB16_ATELIER_SEASIDE_LIGHT = 'tb16-atelier-seaside-light'
    TB16_ATELIER_SULPHURPOOL_LIGHT = 'tb16-atelier-sulphurpool-light'
    TB16_AYU_LIGHT = 'tb16-ayu-light'
    TB16_CATPPUCCIN_LATTE = 'tb16-catppuccin-latte'
    TB16_CLASSIC_LIGHT = 'tb16-classic-light'
    TB16_CUPERTINO = 'tb16-cupertino'
    TB16_DA_ONE_PAPER = 'tb16-da-one-paper'
    TB16_DA_ONE_WHITE = 'tb16-da-one-white'
    TB16_DANQING_LIGHT = 'tb16-danqing-light'
    TB16_DEFAULT_LIGHT = 'tb16-default-light'
    TB16_DIRTYSEA = 'tb16-dirtysea'
    TB16_EDGE_LIGHT = 'tb16-edge-light'
    TB16_EMBERS_LIGHT = 'tb16-embers-light'
    TB16_EMIL = 'tb16-emil'
    TB16_EQUILIBRIUM_GRAY_LIGHT = 'tb16-equilibrium-gray-light'
    TB16_EQUILIBRIUM_LIGHT = 'tb16-equilibrium-light'
    TB16_FRUIT_SODA = 'tb16-fruit-soda'
    TB16_GITHUB = 'tb16-github'
    TB16_GOOGLE_LIGHT = 'tb16-google-light'
    TB16_GRAYSCALE_LIGHT = 'tb16-grayscale-light'
    TB16_GRUVBOX_LIGHT_HARD = 'tb16-gruvbox-light-hard'
    TB16_GRUVBOX_LIGHT_MEDIUM = 'tb16-gruvbox-light-medium'
    TB16_GRUVBOX_LIGHT_SOFT = 'tb16-gruvbox-light-soft'
    TB16_GRUVBOX_MATERIAL_LIGHT_HARD = 'tb16-gruvbox-material-light-hard'
    TB16_GRUVBOX_MATERIAL_LIGHT_MEDIUM = 'tb16-gruvbox-material-light-medium'
    TB16_GRUVBOX_MATERIAL_LIGHT_SOFT = 'tb16-gruvbox-material-light-soft'
    TB16_HARMONIC16_LIGHT = 'tb16-harmonic16-light'
    TB16_HEETCH_LIGHT = 'tb16-heetch-light'
    TB16_HORIZON_LIGHT = 'tb16-horizon-light'
    TB16_HORIZON_TERMINAL_LIGHT = 'tb16-horizon-terminal-light'
    TB16_HUMANOID_LIGHT = 'tb16-humanoid-light'
    TB16_IA_LIGHT = 'tb16-ia-light'
    TB16_MEASURED_LIGHT = 'tb16-measured-light'
    TB16_MEXICO_LIGHT = 'tb16-mexico-light'
    TB16_NORD_LIGHT = 'tb16-nord-light'
    TB16_ONE_LIGHT = 'tb16-one-light'
    TB16_OXOCARBON_LIGHT = 'tb16-oxocarbon-light'
    TB16_PAPERCOLOR_LIGHT = 'tb16-papercolor-light'
    TB16_PRECIOUS_LIGHT_WARM = 'tb16-precious-light-warm'
    TB16_PRECIOUS_LIGHT_WHITE = 'tb16-precious-light-white'
    TB16_PRIMER_LIGHT = 'tb16-primer-light'
    TB16_ROSE_PINE_DAWN = 'tb16-rose-pine-dawn'
    TB16_SAGELIGHT = 'tb16-sagelight'
    TB16_SAKURA = 'tb16-sakura'
    TB16_SELENIZED_LIGHT = 'tb16-selenized-light'
    TB16_SELENIZED_WHITE = 'tb16-selenized-white'
    TB16_SHADESMEAR_LIGHT = 'tb16-shadesmear-light'
    TB16_SHAPESHIFTER = 'tb16-shapeshifter'
    TB16_SILK_LIGHT = 'tb16-silk-light'
    TB16_SOLARFLARE_LIGHT = 'tb16-solarflare-light'
    TB16_SOLARIZED_LIGHT = 'tb16-solarized-light'
    TB16_STANDARDIZED_LIGHT = 'tb16-standardized-light'
    TB16_STILL_ALIVE = 'tb16-still-alive'
    TB16_SUMMERFRUIT_LIGHT = 'tb16-summerfruit-light'
    TB16_SYNTH_MIDNIGHT_LIGHT = 'tb16-synth-midnight-light'
    TB16_TERRACOTTA = 'tb16-terracotta'
    TB16_TOKYO_CITY_LIGHT = 'tb16-tokyo-city-light'
    TB16_TOKYO_CITY_TERMINAL_LIGHT = 'tb16-tokyo-city-terminal-light'
    TB16_TOKYO_NIGHT_LIGHT = 'tb16-tokyo-night-light'
    TB16_TOKYO_NIGHT_TERMINAL_LIGHT = 'tb16-tokyo-night-terminal-light'
    TB16_TOMORROW = 'tb16-tomorrow'
    TB16_UNIKITTY_LIGHT = 'tb16-unikitty-light'
    TB16_WINDOWS_95_LIGHT = 'tb16-windows-95-light'
    TB16_WINDOWS_HIGHCONTRAST_LIGHT = 'tb16-windows-highcontrast-light'


class LightLowContrastColorStyles(str, Enum):
    __doc__ = dedent("""
        Lower contrast dark color styles for syntax highlighting.
        """) + _GENERAL_COLOR_STYLE_DOCSTRING

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
    TB16_BRUSHTREES = 'tb16-brushtrees'
    TB16_CUPCAKE = 'tb16-cupcake'
    TB16_MATERIAL_LIGHTER = 'tb16-material-lighter'
    TB16_WINDOWS_10_LIGHT = 'tb16-windows-10-light'
    TB16_WINDOWS_NT_LIGHT = 'tb16-windows-nt-light'


def _get_all_color_styles() -> dict[str, str]:
    all_color_styles = {}
    for style_set in (RecommendedColorStyles,
                      DarkHighContrastColorStyles,
                      DarkLowContrastColorStyles,
                      LightHighContrastColorStyles,
                      LightLowContrastColorStyles):
        for style in style_set:
            all_color_styles[style.name] = style.value
    return all_color_styles


AllColorStyles = _get_all_color_styles()

ColorStyles = (
    RecommendedColorStyles | DarkHighContrastColorStyles | DarkLowContrastColorStyles
    | LightHighContrastColorStyles | LightLowContrastColorStyles)


class HorizontalOverflowMode(str, Enum):
    """
    Horizontal overflow modes for the output.

    The horizontal overflow modes are:
    - `ELLIPSIS`: Adds an ellipsis (...) at the end of the line if it
        exceeds the width.
    - `CROP`: Crops the line to fit within the width, without adding an
        ellipsis.
    - `WORD_WRAP`: Wraps the line to the next line if it exceeds the
        width, breaking according to the specified syntax language.
    """
    ELLIPSIS = 'ellipsis'
    CROP = 'crop'
    WORD_WRAP = 'word_wrap'


class LayoutStyle(str, Enum):
    """
    Visual style for the layout of the output.

    The layout styles are:
    - `TABLE`: The output is displayed as a simple table grid
    - `PANELS`: The output is displayed as a set of panels
    """
    TABLE_GRID = 'table_grid'
    PANELS = 'panels'


class VerticalOverflowMode(str, Enum):
    """
    Vertical overflow modes for the output.

    The vertical overflow modes are:
    - `CROP_TOP`: Crops the top of the output if it exceeds the height.
    - `CROP_BOTTOM`: Crops the bottom of the output if it exceeds the
        height.
    """
    CROP_TOP = 'crop_top'
    CROP_BOTTOM = 'crop_bottom'


@pyd.dataclass(
    kw_only=True,
    frozen=True,
    config=pyd.ConfigDict(extra=pyd.Extra.forbid, validate_assignment=True),
)
class OutputConfig:
    """
    Configuration of data formatting for DraftOutput (and subclasses).

    This class manages all aspects of output rendering, including syntax
    highlighting, color schemes, font settings, and overflow behavior for
    both terminal and HTML output. It is intended to be used for a specific
    instance of DraftOutput, and not as a global configuration.

    Args:
        tab_size (NonNegativeInt): Number of spaces to use for each tab
        indent_tab_size (NonNegativeInt): Number of spaces to use for each
            indentation level.
        debug_mode (bool): When True, enables additional debugging
            information in the output, such as the hierarchy of the Model
            objects.
        pretty_printer (PrettyPrinterLib): Library to use for pretty
            printing (rich or devtools).
        language (SyntaxLanguage | str): Syntax language for code
            highlighting. Supported lexers are defined in SyntaxLanguage.
            For non-supported styles, the user can specify a string with the
            Pygments lexer name. For this to work, the lexer must be
            registered in the Pygments library.
        console_color_system (ConsoleColorSystem): Color system to use for
            terminal output. The default is AUTO, which automatically
            detects the color system based on particular environment
            variables. If color capabilities are not detected, the output
            will be in black and white. If the color system of a modern
            consoles/terminal is not auto-detected (which is the case for
            e.g. the PyCharm console), the user might want to set the color
            system manually to ANSI_RGB to force color output.
        color_style (ColorStyles | str): Color style/theme for syntax
            highlighting. Supported styles are defined in AllColorStyles.
            For non-supported languages, the user can specify a string with
            the Pygments style name. For this to work, the style must be
            registered in the Pygments library.
        transparent_background (bool): If True, uses transparent background
            for the output. In the case of terminal output, the background
            color will be the current background color of the terminal. For
            HTML output, the background color will be automatically set to
            pure black or pure white, depending on the luminosity of the
            foreground color.
        css_font_families (Tuple[str, ...]): Font families to use in HTML
            output, in order of preference (empty tuple for browser
            default).
        css_font_size (NonNegativeInt | None): Font size in pixels for HTML
            output (None for browser default).
        css_font_weight (NonNegativeInt | None): Font weight for HTML
            output (None for browser default).
        css_line_height (NonNegativeFloat | None): Line height multiplier
            for HTML output (None for browser default).
        horizontal_overflow_mode (HorizontalOverflowMode): How to handle
            text that exceeds the width.
        vertical_overflow_mode (VerticalOverflowMode): How to handle text
            that exceeds the height.
        layout_style (LayoutStyle): Visual styles for the layout of the
            output.
    """

    tab_size: pyd.NonNegativeInt = 4
    indent_tab_size: pyd.NonNegativeInt = 2
    debug_mode: bool = False
    pretty_printer: PrettyPrinterLib = PrettyPrinterLib.RICH
    language: SyntaxLanguage | str = SyntaxLanguage.PYTHON
    console_color_system: ConsoleColorSystem = ConsoleColorSystem.AUTO
    color_style: ColorStyles | str = RecommendedColorStyles.ANSI_DARK
    transparent_background: bool = True
    css_font_families: tuple[str, ...] = (
        'CommitMonoOmnipy',
        'Menlo',
        'DejaVu Sans Mono',
        'Consolas',
        'Courier New',
        'monospace',
    )
    css_font_size: pyd.NonNegativeInt | None = 14
    css_font_weight: pyd.NonNegativeInt | None = 450
    css_line_height: pyd.NonNegativeFloat | None = 1.35
    horizontal_overflow_mode: HorizontalOverflowMode = HorizontalOverflowMode.ELLIPSIS
    vertical_overflow_mode: VerticalOverflowMode = VerticalOverflowMode.CROP_BOTTOM
    layout_style: LayoutStyle = LayoutStyle.TABLE_GRID

    @pyd.validator('language')
    def validate_language(cls, language: SyntaxLanguage | str) -> SyntaxLanguage | str:
        try:
            if isinstance(language, SyntaxLanguage):
                return language
            elif pygments.lexers.get_lexer_by_name(language):
                return language
            else:
                raise ValueError(f'Invalid syntax language: {language}')
        except pygments.util.ClassNotFound as exp:
            raise ValueError(f'Invalid syntax language: {language}') from exp

    @pyd.validator('color_style')
    def validate_color_style(cls, color_style: ColorStyles | str) -> ColorStyles | str:
        try:
            if isinstance(color_style, RecommendedColorStyles):
                return color_style
            elif isinstance(color_style, ColorStyles):
                try:
                    pygments.styles.get_style_by_name(color_style.value)
                except pygments.util.ClassNotFound:
                    install_base16_theme(color_style.value)
                    pygments.styles.get_style_by_name(color_style.value)
                return color_style
            elif pygments.styles.get_style_by_name(color_style):
                return color_style
            else:
                raise ValueError(f'Invalid color style: {color_style}')
        except pygments.util.ClassNotFound as exp:
            raise ValueError(f'Invalid color style: {color_style}') from exp
