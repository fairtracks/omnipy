from textwrap import dedent
from typing import Literal

from omnipy.shared.constants import (JUPYTER_DEFAULT_HEIGHT,
                                     JUPYTER_DEFAULT_WIDTH,
                                     TERMINAL_DEFAULT_HEIGHT,
                                     TERMINAL_DEFAULT_WIDTH)
from omnipy.util.literal_enum import LiteralEnum


class PersistOutputsOptions(LiteralEnum[str]):
    Literals = Literal['disabled', 'config', 'enabled']

    DISABLED: Literal['disabled'] = 'disabled'
    FOLLOW_CONFIG: Literal['config'] = 'config'
    ENABLED: Literal['enabled'] = 'enabled'


class RestoreOutputsOptions(LiteralEnum[str]):
    Literals = Literal['disabled', 'config', 'auto_ignore_params', 'force_ignore_params']

    DISABLED: Literal['disabled'] = 'disabled'
    FOLLOW_CONFIG: Literal['config'] = 'config'
    AUTO_ENABLE_IGNORE_PARAMS: Literal['auto_ignore_params'] = 'auto_ignore_params'
    FORCE_ENABLE_IGNORE_PARAMS: Literal['force_ignore_params'] = 'force_ignore_params'


class OutputStorageProtocolOptions(LiteralEnum[str]):
    Literals = Literal['local', 's3', 'config']

    LOCAL: Literal['local'] = 'local'
    S3: Literal['s3'] = 's3'
    FOLLOW_CONFIG: Literal['config'] = 'config'


class ConfigPersistOutputsOptions(LiteralEnum[str]):
    Literals = Literal['disabled', 'flow', 'all']

    DISABLED: Literal['disabled'] = 'disabled'
    ENABLE_FLOW_OUTPUTS: Literal['flow'] = 'flow'
    ENABLE_FLOW_AND_TASK_OUTPUTS: Literal['all'] = 'all'


class ConfigRestoreOutputsOptions(LiteralEnum[str]):
    Literals = Literal['disabled', 'auto_ignore_params']

    DISABLED: Literal['disabled'] = 'disabled'
    AUTO_ENABLE_IGNORE_PARAMS: Literal['auto_ignore_params'] = 'auto_ignore_params'


class ConfigOutputStorageProtocolOptions(LiteralEnum[str]):
    Literals = Literal['local', 's3']

    LOCAL: Literal['local'] = 'local'
    S3: Literal['s3'] = 's3'


class EngineChoice(LiteralEnum[str]):
    Literals = Literal['local', 'prefect']

    LOCAL: Literal['local'] = 'local'
    PREFECT: Literal['prefect'] = 'prefect'


class RunState(LiteralEnum[int]):
    Literals = Literal[1, 2, 3]

    INITIALIZED: Literal[1] = 1
    RUNNING: Literal[2] = 2
    FINISHED: Literal[3] = 3


# TODO: Add 'apply' state
# TODO: Add 'failed' state and error management
# TODO: Consider the need for a 'waiting' state


class RunStateLogMessages(LiteralEnum[str]):
    Literals = Literal['Initialized "{}"', 'Started running "{}"...', 'Finished running "{}"!']

    INITIALIZED: Literal['Initialized "{}"'] = 'Initialized "{}"'
    RUNNING: Literal['Started running "{}"...'] = 'Started running "{}"...'
    FINISHED: Literal['Finished running "{}"!'] = 'Finished running "{}"!'


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


_IPYTHON_DESCRIPTION = dedent("""
    IPython is an more advanced interactive interpreter than the builtin
    Python REPL, providing additional features such as syntax highlighting,
    tab completion, and better error messages.
    """)

_JUPYTER_DESCRIPTION = dedent("""
    The Jupyter environment supports rich output rendering (based on HTML)
    and interactive widgets and is typically used for data analysis,
    scientific computing, and machine learning tasks. Jupyter and allows for
    the execution of code in cells, with the output displayed inline in the
    notebook.
    """)

_PYCHARM_NOTE = dedent(f"""
    Note that PyCharm does not support automatic detection of the display
    dimensions, so the dimensions are set to the default values defined in
    the config ({TERMINAL_DEFAULT_WIDTH}x{TERMINAL_DEFAULT_HEIGHT} for the
    terminal, {JUPYTER_DEFAULT_WIDTH}x{JUPYTER_DEFAULT_HEIGHT} for Jupyter).
    """)

_BROWSER_DESCRIPTION = dedent("""
    A web browser with HTML rendering, such as Google Chrome, Mozilla
    Firefox, or Microsoft Edge. This is for now used to display HTML output
    and does not currently support any interactive features.
    """)


class UserInterfaceType(LiteralEnum[str]):
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

    Literals = Literal['terminal',
                       'ipython',
                       'pycharm_terminal',
                       'pycharm_ipython',
                       'pycharm_jupyter',
                       'jupyter',
                       'browser',
                       'browser_embedded',
                       'unknown',
                       'auto']

    TERMINAL: Literal['terminal'] = 'terminal'
    """
    A standard Python interactive interpreter (REPL), running within
    terminal-emulation software, such as the builtin "Terminal" app on Mac
    OS or GNOME Terminal on Linux, through a SSH connection to a remote
    server,  or directly on a console.
    """
    IPYTHON: Literal['ipython'] = 'ipython'
    """
    Same as `TERMINAL`, but running within the IPython interactive
    interpreter (REPL). The IPython interpreter is a more advanced
    interactive interpreter that provides additional features such as syntax
    highlighting, tab completion, and better error messages.
    """
    PYCHARM_TERMINAL: Literal['pycharm_terminal'] = 'pycharm_terminal'
    f"""
    The console and/or terminal of the JetBrains PyCharm IDE running with
    the Python interactive interpreter (REPL). {_PYCHARM_NOTE}
    """
    PYCHARM_IPYTHON: Literal['pycharm_ipython'] = 'pycharm_ipython'
    f"""
    The console and/or terminal of the JetBrains PyCharm IDE running with
    the IPython interactive interpreter (REPL). {_IPYTHON_DESCRIPTION}
    {_PYCHARM_NOTE}
    """
    PYCHARM_JUPYTER: Literal['pycharm_jupyter'] = 'pycharm_jupyter'
    f"""
    A Jupyter notebook running within the user interface of the JetBrains
    PyCharm IDE. {_JUPYTER_DESCRIPTION}
    {_PYCHARM_NOTE}.
    """
    JUPYTER: Literal['jupyter'] = 'jupyter'
    f"""
    A Jupyter notebook or JupyterLab environment. {_JUPYTER_DESCRIPTION}
    """
    BROWSER: Literal['browser'] = 'browser'
    f"""
    {_BROWSER_DESCRIPTION}. The `BROWSER` UI type displays content as full
    web pages.
    """
    BROWSER_EMBEDDED: Literal['browser_embedded'] = 'browser_embedded'
    f"""
    {_BROWSER_DESCRIPTION} The `BROWSER_EMBEDDED` UI type displays content
    as standalone HTML elements, and produce HTML code that can be embedded
    in other HTML documents.
    """
    UNKNOWN: Literal['unknown'] = 'unknown'
    """
    The `UNKNOWN` user interface type is used when the user interface type
    cannot be determined. This will in practice produce the same output as
    the `TERMINAL` display type, but assuming only basic terminal
    capabilities (such as ANSI escape codes for color and text formatting)
    are available.
    """
    AUTO: Literal['auto'] = 'auto'
    """
    The `AUTO` user interface type is used to describe that the user
    interface type has not yet been determined, and that it should be
    automatically determined by Omnipy. This is the default value.
    """


class BackoffStrategy(LiteralEnum[str]):
    Literals = Literal['exponential', 'jitter', 'fibonacci', 'random']

    EXPONENTIAL: Literal['exponential'] = 'exponential'
    JITTER: Literal['jitter'] = 'jitter'
    FIBONACCI: Literal['fibonacci'] = 'fibonacci'
    RANDOM: Literal['random'] = 'random'


class PrettyPrinterLib(LiteralEnum[str]):
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

    Literals = Literal['rich', 'devtools']

    RICH: Literal['rich'] = 'rich'
    DEVTOOLS: Literal['devtools'] = 'devtools'


class SyntaxLanguage(LiteralEnum[str]):
    """
    Supported languages for syntax recognition and highlighting.

    A selected subset of the lexer languages supported by the Pygments
    library (https://pygments.org/languages/), assumed to be the ones most
    relevant for Omnipy.
    """

    Literals = Literal['python',
                       'text',
                       'json',
                       'json-ld',
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

    PYTHON: Literal['python'] = 'python'
    TEXT: Literal['text'] = 'text'
    JSON: Literal['json'] = 'json'
    JSON_LD: Literal['json-ld'] = 'json-ld'
    YAML: Literal['yaml'] = 'yaml'
    XML: Literal['xml'] = 'xml'
    TOML: Literal['toml'] = 'toml'
    BASH: Literal['bash'] = 'bash'
    SQL: Literal['sql'] = 'sql'
    HTML: Literal['html'] = 'html'
    MARKDOWN: Literal['markdown'] = 'markdown'
    CSS: Literal['css'] = 'css'
    NUMPY: Literal['numpy'] = 'numpy'
    SPARQL: Literal['sparql'] = 'sparql'
    TEX: Literal['tex'] = 'tex'


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
    The default color system, which is automatically detected
        based on the terminal capabilities. This is the default value.
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
    The truecolor ANSI color system, which supports 16 million
        colors. Most modern terminals support this color system.
        """
    WINDOWS_LEGACY: Literal['windows'] = 'windows'
    """
    The legacy Windows color system, for backwards
        compatibility with older Windows terminals.
    """


class RecommendedColorStyles(LiteralEnum[str]):
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

    Literals = Literal['ansi_dark',
                       'ansi_light',
                       'omnipy-selenized-black',
                       'omnipy-selenized-dark',
                       'omnipy-selenized-light',
                       'omnipy-selenized-white']

    ANSI_DARK: Literal['ansi_dark'] = 'ansi_dark'
    ANSI_LIGHT: Literal['ansi_light'] = 'ansi_light'
    OMNIPY_SELENIZED_BLACK: Literal['omnipy-selenized-black'] = 'omnipy-selenized-black'
    OMNIPY_SELENIZED_DARK: Literal['omnipy-selenized-dark'] = 'omnipy-selenized-dark'
    OMNIPY_SELENIZED_LIGHT: Literal['omnipy-selenized-light'] = 'omnipy-selenized-light'
    OMNIPY_SELENIZED_WHITE: Literal['omnipy-selenized-white'] = 'omnipy-selenized-white'


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


class DarkHighContrastColorStyles(LiteralEnum[str]):
    __doc__ = dedent("""
        High contrast dark color styles for syntax highlighting.
        """) + _GENERAL_COLOR_STYLE_DOCSTRING

    Literals = Literal['github-dark',
                       'lightbulb',
                       'monokai',
                       'rrt',
                       'tb16-3024',
                       'tb16-apathy',
                       'tb16-ashes',
                       'tb16-atelier-cave',
                       'tb16-atelier-dune',
                       'tb16-atelier-estuary',
                       'tb16-atelier-forest',
                       'tb16-atelier-heath',
                       'tb16-atelier-lakeside',
                       'tb16-atelier-plateau',
                       'tb16-atelier-savanna',
                       'tb16-atelier-seaside',
                       'tb16-atelier-sulphurpool',
                       'tb16-atlas',
                       'tb16-ayu-dark',
                       'tb16-ayu-mirage',
                       'tb16-aztec',
                       'tb16-bespin',
                       'tb16-black-metal-bathory',
                       'tb16-black-metal-burzum',
                       'tb16-black-metal-dark-funeral',
                       'tb16-black-metal-gorgoroth',
                       'tb16-black-metal-immortal',
                       'tb16-black-metal-khold',
                       'tb16-black-metal-marduk',
                       'tb16-black-metal-mayhem',
                       'tb16-black-metal-nile',
                       'tb16-black-metal-venom',
                       'tb16-black-metal',
                       'tb16-blueforest',
                       'tb16-blueish',
                       'tb16-brewer',
                       'tb16-bright',
                       'tb16-caroline',
                       'tb16-catppuccin-frappe',
                       'tb16-catppuccin-macchiato',
                       'tb16-catppuccin-mocha',
                       'tb16-chalk',
                       'tb16-circus',
                       'tb16-classic-dark',
                       'tb16-codeschool',
                       'tb16-colors',
                       'tb16-da-one-black',
                       'tb16-da-one-gray',
                       'tb16-da-one-ocean',
                       'tb16-da-one-sea',
                       'tb16-danqing',
                       'tb16-darcula',
                       'tb16-darkmoss',
                       'tb16-darktooth',
                       'tb16-darkviolet',
                       'tb16-decaf',
                       'tb16-deep-oceanic-next',
                       'tb16-default-dark',
                       'tb16-dracula',
                       'tb16-edge-dark',
                       'tb16-eighties',
                       'tb16-embers',
                       'tb16-equilibrium-dark',
                       'tb16-equilibrium-gray-dark',
                       'tb16-espresso',
                       'tb16-evenok-dark',
                       'tb16-everforest-dark-hard',
                       'tb16-everforest',
                       'tb16-flat',
                       'tb16-framer',
                       'tb16-gigavolt',
                       'tb16-google-dark',
                       'tb16-gotham',
                       'tb16-grayscale-dark',
                       'tb16-greenscreen',
                       'tb16-gruber',
                       'tb16-gruvbox-dark-hard',
                       'tb16-gruvbox-dark-medium',
                       'tb16-gruvbox-dark-pale',
                       'tb16-gruvbox-dark-soft',
                       'tb16-gruvbox-material-dark-hard',
                       'tb16-gruvbox-material-dark-medium',
                       'tb16-gruvbox-material-dark-soft',
                       'tb16-hardcore',
                       'tb16-harmonic16-dark',
                       'tb16-heetch',
                       'tb16-helios',
                       'tb16-hopscotch',
                       'tb16-horizon-dark',
                       'tb16-horizon-terminal-dark',
                       'tb16-humanoid-dark',
                       'tb16-ia-dark',
                       'tb16-irblack',
                       'tb16-isotope',
                       'tb16-jabuti',
                       'tb16-kanagawa',
                       'tb16-katy',
                       'tb16-kimber',
                       'tb16-macintosh',
                       'tb16-marrakesh',
                       'tb16-materia',
                       'tb16-material-darker',
                       'tb16-material-palenight',
                       'tb16-material',
                       'tb16-measured-dark',
                       'tb16-mellow-purple',
                       'tb16-mocha',
                       'tb16-monokai',
                       'tb16-moonlight',
                       'tb16-mountain',
                       'tb16-nebula',
                       'tb16-nord',
                       'tb16-nova',
                       'tb16-ocean',
                       'tb16-oceanicnext',
                       'tb16-onedark-dark',
                       'tb16-onedark',
                       'tb16-outrun-dark',
                       'tb16-oxocarbon-dark',
                       'tb16-pandora',
                       'tb16-paraiso',
                       'tb16-pasque',
                       'tb16-phd',
                       'tb16-pinky',
                       'tb16-pop',
                       'tb16-porple',
                       'tb16-precious-dark-eleven',
                       'tb16-precious-dark-fifteen',
                       'tb16-primer-dark-dimmed',
                       'tb16-primer-dark',
                       'tb16-purpledream',
                       'tb16-qualia',
                       'tb16-railscasts',
                       'tb16-rebecca',
                       'tb16-rose-pine-moon',
                       'tb16-rose-pine',
                       'tb16-saga',
                       'tb16-sandcastle',
                       'tb16-selenized-black',
                       'tb16-selenized-dark',
                       'tb16-seti',
                       'tb16-shades-of-purple',
                       'tb16-shadesmear-dark',
                       'tb16-silk-dark',
                       'tb16-snazzy',
                       'tb16-solarflare',
                       'tb16-solarized-dark',
                       'tb16-spaceduck',
                       'tb16-spacemacs',
                       'tb16-sparky',
                       'tb16-standardized-dark',
                       'tb16-stella',
                       'tb16-summerfruit-dark',
                       'tb16-synth-midnight-dark',
                       'tb16-tango',
                       'tb16-tender',
                       'tb16-terracotta-dark',
                       'tb16-tokyo-city-dark',
                       'tb16-tokyo-city-terminal-dark',
                       'tb16-tokyo-night-dark',
                       'tb16-tokyo-night-storm',
                       'tb16-tokyodark-terminal',
                       'tb16-tokyodark',
                       'tb16-tomorrow-night-eighties',
                       'tb16-tomorrow-night',
                       'tb16-tube',
                       'tb16-twilight',
                       'tb16-unikitty-dark',
                       'tb16-unikitty-reversible',
                       'tb16-uwunicorn',
                       'tb16-vesper',
                       'tb16-vice',
                       'tb16-windows-10',
                       'tb16-windows-95',
                       'tb16-windows-highcontrast',
                       'tb16-windows-nt',
                       'tb16-woodland',
                       'tb16-xcode-dusk',
                       'tb16-zenbones',
                       'tb16-zenburn']

    GITHUB_DARK: Literal['github-dark'] = 'github-dark'
    LIGHTBULB: Literal['lightbulb'] = 'lightbulb'
    MONOKAI: Literal['monokai'] = 'monokai'
    RRT: Literal['rrt'] = 'rrt'
    TB16_3024: Literal['tb16-3024'] = 'tb16-3024'
    TB16_APATHY: Literal['tb16-apathy'] = 'tb16-apathy'
    TB16_ASHES: Literal['tb16-ashes'] = 'tb16-ashes'
    TB16_ATELIER_CAVE: Literal['tb16-atelier-cave'] = 'tb16-atelier-cave'
    TB16_ATELIER_DUNE: Literal['tb16-atelier-dune'] = 'tb16-atelier-dune'
    TB16_ATELIER_ESTUARY: Literal['tb16-atelier-estuary'] = 'tb16-atelier-estuary'
    TB16_ATELIER_FOREST: Literal['tb16-atelier-forest'] = 'tb16-atelier-forest'
    TB16_ATELIER_HEATH: Literal['tb16-atelier-heath'] = 'tb16-atelier-heath'
    TB16_ATELIER_LAKESIDE: Literal['tb16-atelier-lakeside'] = 'tb16-atelier-lakeside'
    TB16_ATELIER_PLATEAU: Literal['tb16-atelier-plateau'] = 'tb16-atelier-plateau'
    TB16_ATELIER_SAVANNA: Literal['tb16-atelier-savanna'] = 'tb16-atelier-savanna'
    TB16_ATELIER_SEASIDE: Literal['tb16-atelier-seaside'] = 'tb16-atelier-seaside'
    TB16_ATELIER_SULPHURPOOL: Literal['tb16-atelier-sulphurpool'] = 'tb16-atelier-sulphurpool'
    TB16_ATLAS: Literal['tb16-atlas'] = 'tb16-atlas'
    TB16_AYU_DARK: Literal['tb16-ayu-dark'] = 'tb16-ayu-dark'
    TB16_AYU_MIRAGE: Literal['tb16-ayu-mirage'] = 'tb16-ayu-mirage'
    TB16_AZTEC: Literal['tb16-aztec'] = 'tb16-aztec'
    TB16_BESPIN: Literal['tb16-bespin'] = 'tb16-bespin'
    TB16_BLACK_METAL_BATHORY: Literal['tb16-black-metal-bathory'] = 'tb16-black-metal-bathory'
    TB16_BLACK_METAL_BURZUM: Literal['tb16-black-metal-burzum'] = 'tb16-black-metal-burzum'
    TB16_BLACK_METAL_DARK_FUNERAL: Literal[
        'tb16-black-metal-dark-funeral'] = 'tb16-black-metal-dark-funeral'
    TB16_BLACK_METAL_GORGOROTH: Literal['tb16-black-metal-gorgoroth'] = 'tb16-black-metal-gorgoroth'
    TB16_BLACK_METAL_IMMORTAL: Literal['tb16-black-metal-immortal'] = 'tb16-black-metal-immortal'
    TB16_BLACK_METAL_KHOLD: Literal['tb16-black-metal-khold'] = 'tb16-black-metal-khold'
    TB16_BLACK_METAL_MARDUK: Literal['tb16-black-metal-marduk'] = 'tb16-black-metal-marduk'
    TB16_BLACK_METAL_MAYHEM: Literal['tb16-black-metal-mayhem'] = 'tb16-black-metal-mayhem'
    TB16_BLACK_METAL_NILE: Literal['tb16-black-metal-nile'] = 'tb16-black-metal-nile'
    TB16_BLACK_METAL_VENOM: Literal['tb16-black-metal-venom'] = 'tb16-black-metal-venom'
    TB16_BLACK_METAL: Literal['tb16-black-metal'] = 'tb16-black-metal'
    TB16_BLUEFOREST: Literal['tb16-blueforest'] = 'tb16-blueforest'
    TB16_BLUEISH: Literal['tb16-blueish'] = 'tb16-blueish'
    TB16_BREWER: Literal['tb16-brewer'] = 'tb16-brewer'
    TB16_BRIGHT: Literal['tb16-bright'] = 'tb16-bright'
    TB16_CAROLINE: Literal['tb16-caroline'] = 'tb16-caroline'
    TB16_CATPPUCCIN_FRAPPE: Literal['tb16-catppuccin-frappe'] = 'tb16-catppuccin-frappe'
    TB16_CATPPUCCIN_MACCHIATO: Literal['tb16-catppuccin-macchiato'] = 'tb16-catppuccin-macchiato'
    TB16_CATPPUCCIN_MOCHA: Literal['tb16-catppuccin-mocha'] = 'tb16-catppuccin-mocha'
    TB16_CHALK: Literal['tb16-chalk'] = 'tb16-chalk'
    TB16_CIRCUS: Literal['tb16-circus'] = 'tb16-circus'
    TB16_CLASSIC_DARK: Literal['tb16-classic-dark'] = 'tb16-classic-dark'
    TB16_CODESCHOOL: Literal['tb16-codeschool'] = 'tb16-codeschool'
    TB16_COLORS: Literal['tb16-colors'] = 'tb16-colors'
    TB16_DA_ONE_BLACK: Literal['tb16-da-one-black'] = 'tb16-da-one-black'
    TB16_DA_ONE_GRAY: Literal['tb16-da-one-gray'] = 'tb16-da-one-gray'
    TB16_DA_ONE_OCEAN: Literal['tb16-da-one-ocean'] = 'tb16-da-one-ocean'
    TB16_DA_ONE_SEA: Literal['tb16-da-one-sea'] = 'tb16-da-one-sea'
    TB16_DANQING: Literal['tb16-danqing'] = 'tb16-danqing'
    TB16_DARCULA: Literal['tb16-darcula'] = 'tb16-darcula'
    TB16_DARKMOSS: Literal['tb16-darkmoss'] = 'tb16-darkmoss'
    TB16_DARKTOOTH: Literal['tb16-darktooth'] = 'tb16-darktooth'
    TB16_DARKVIOLET: Literal['tb16-darkviolet'] = 'tb16-darkviolet'
    TB16_DECAF: Literal['tb16-decaf'] = 'tb16-decaf'
    TB16_DEEP_OCEANIC_NEXT: Literal['tb16-deep-oceanic-next'] = 'tb16-deep-oceanic-next'
    TB16_DEFAULT_DARK: Literal['tb16-default-dark'] = 'tb16-default-dark'
    TB16_DRACULA: Literal['tb16-dracula'] = 'tb16-dracula'
    TB16_EDGE_DARK: Literal['tb16-edge-dark'] = 'tb16-edge-dark'
    TB16_EIGHTIES: Literal['tb16-eighties'] = 'tb16-eighties'
    TB16_EMBERS: Literal['tb16-embers'] = 'tb16-embers'
    TB16_EQUILIBRIUM_DARK: Literal['tb16-equilibrium-dark'] = 'tb16-equilibrium-dark'
    TB16_EQUILIBRIUM_GRAY_DARK: Literal['tb16-equilibrium-gray-dark'] = 'tb16-equilibrium-gray-dark'
    TB16_ESPRESSO: Literal['tb16-espresso'] = 'tb16-espresso'
    TB16_EVENOK_DARK: Literal['tb16-evenok-dark'] = 'tb16-evenok-dark'
    TB16_EVERFOREST_DARK_HARD: Literal['tb16-everforest-dark-hard'] = 'tb16-everforest-dark-hard'
    TB16_EVERFOREST: Literal['tb16-everforest'] = 'tb16-everforest'
    TB16_FLAT: Literal['tb16-flat'] = 'tb16-flat'
    TB16_FRAMER: Literal['tb16-framer'] = 'tb16-framer'
    TB16_GIGAVOLT: Literal['tb16-gigavolt'] = 'tb16-gigavolt'
    TB16_GOOGLE_DARK: Literal['tb16-google-dark'] = 'tb16-google-dark'
    TB16_GOTHAM: Literal['tb16-gotham'] = 'tb16-gotham'
    TB16_GRAYSCALE_DARK: Literal['tb16-grayscale-dark'] = 'tb16-grayscale-dark'
    TB16_GREENSCREEN: Literal['tb16-greenscreen'] = 'tb16-greenscreen'
    TB16_GRUBER: Literal['tb16-gruber'] = 'tb16-gruber'
    TB16_GRUVBOX_DARK_HARD: Literal['tb16-gruvbox-dark-hard'] = 'tb16-gruvbox-dark-hard'
    TB16_GRUVBOX_DARK_MEDIUM: Literal['tb16-gruvbox-dark-medium'] = 'tb16-gruvbox-dark-medium'
    TB16_GRUVBOX_DARK_PALE: Literal['tb16-gruvbox-dark-pale'] = 'tb16-gruvbox-dark-pale'
    TB16_GRUVBOX_DARK_SOFT: Literal['tb16-gruvbox-dark-soft'] = 'tb16-gruvbox-dark-soft'
    TB16_GRUVBOX_MATERIAL_DARK_HARD: Literal[
        'tb16-gruvbox-material-dark-hard'] = 'tb16-gruvbox-material-dark-hard'
    TB16_GRUVBOX_MATERIAL_DARK_MEDIUM: Literal[
        'tb16-gruvbox-material-dark-medium'] = 'tb16-gruvbox-material-dark-medium'
    TB16_GRUVBOX_MATERIAL_DARK_SOFT: Literal[
        'tb16-gruvbox-material-dark-soft'] = 'tb16-gruvbox-material-dark-soft'
    TB16_HARDCORE: Literal['tb16-hardcore'] = 'tb16-hardcore'
    TB16_HARMONIC16_DARK: Literal['tb16-harmonic16-dark'] = 'tb16-harmonic16-dark'
    TB16_HEETCH: Literal['tb16-heetch'] = 'tb16-heetch'
    TB16_HELIOS: Literal['tb16-helios'] = 'tb16-helios'
    TB16_HOPSCOTCH: Literal['tb16-hopscotch'] = 'tb16-hopscotch'
    TB16_HORIZON_DARK: Literal['tb16-horizon-dark'] = 'tb16-horizon-dark'
    TB16_HORIZON_TERMINAL_DARK: Literal['tb16-horizon-terminal-dark'] = 'tb16-horizon-terminal-dark'
    TB16_HUMANOID_DARK: Literal['tb16-humanoid-dark'] = 'tb16-humanoid-dark'
    TB16_IA_DARK: Literal['tb16-ia-dark'] = 'tb16-ia-dark'
    TB16_IRBLACK: Literal['tb16-irblack'] = 'tb16-irblack'
    TB16_ISOTOPE: Literal['tb16-isotope'] = 'tb16-isotope'
    TB16_JABUTI: Literal['tb16-jabuti'] = 'tb16-jabuti'
    TB16_KANAGAWA: Literal['tb16-kanagawa'] = 'tb16-kanagawa'
    TB16_KATY: Literal['tb16-katy'] = 'tb16-katy'
    TB16_KIMBER: Literal['tb16-kimber'] = 'tb16-kimber'
    TB16_MACINTOSH: Literal['tb16-macintosh'] = 'tb16-macintosh'
    TB16_MARRAKESH: Literal['tb16-marrakesh'] = 'tb16-marrakesh'
    TB16_MATERIA: Literal['tb16-materia'] = 'tb16-materia'
    TB16_MATERIAL_DARKER: Literal['tb16-material-darker'] = 'tb16-material-darker'
    TB16_MATERIAL_PALENIGHT: Literal['tb16-material-palenight'] = 'tb16-material-palenight'
    TB16_MATERIAL: Literal['tb16-material'] = 'tb16-material'
    TB16_MEASURED_DARK: Literal['tb16-measured-dark'] = 'tb16-measured-dark'
    TB16_MELLOW_PURPLE: Literal['tb16-mellow-purple'] = 'tb16-mellow-purple'
    TB16_MOCHA: Literal['tb16-mocha'] = 'tb16-mocha'
    TB16_MONOKAI: Literal['tb16-monokai'] = 'tb16-monokai'
    TB16_MOONLIGHT: Literal['tb16-moonlight'] = 'tb16-moonlight'
    TB16_MOUNTAIN: Literal['tb16-mountain'] = 'tb16-mountain'
    TB16_NEBULA: Literal['tb16-nebula'] = 'tb16-nebula'
    TB16_NORD: Literal['tb16-nord'] = 'tb16-nord'
    TB16_NOVA: Literal['tb16-nova'] = 'tb16-nova'
    TB16_OCEAN: Literal['tb16-ocean'] = 'tb16-ocean'
    TB16_OCEANICNEXT: Literal['tb16-oceanicnext'] = 'tb16-oceanicnext'
    TB16_ONEDARK_DARK: Literal['tb16-onedark-dark'] = 'tb16-onedark-dark'
    TB16_ONEDARK: Literal['tb16-onedark'] = 'tb16-onedark'
    TB16_OUTRUN_DARK: Literal['tb16-outrun-dark'] = 'tb16-outrun-dark'
    TB16_OXOCARBON_DARK: Literal['tb16-oxocarbon-dark'] = 'tb16-oxocarbon-dark'
    TB16_PANDORA: Literal['tb16-pandora'] = 'tb16-pandora'
    TB16_PARAISO: Literal['tb16-paraiso'] = 'tb16-paraiso'
    TB16_PASQUE: Literal['tb16-pasque'] = 'tb16-pasque'
    TB16_PHD: Literal['tb16-phd'] = 'tb16-phd'
    TB16_PINKY: Literal['tb16-pinky'] = 'tb16-pinky'
    TB16_POP: Literal['tb16-pop'] = 'tb16-pop'
    TB16_PORPLE: Literal['tb16-porple'] = 'tb16-porple'
    TB16_PRECIOUS_DARK_ELEVEN: Literal['tb16-precious-dark-eleven'] = 'tb16-precious-dark-eleven'
    TB16_PRECIOUS_DARK_FIFTEEN: Literal['tb16-precious-dark-fifteen'] = 'tb16-precious-dark-fifteen'
    TB16_PRIMER_DARK_DIMMED: Literal['tb16-primer-dark-dimmed'] = 'tb16-primer-dark-dimmed'
    TB16_PRIMER_DARK: Literal['tb16-primer-dark'] = 'tb16-primer-dark'
    TB16_PURPLEDREAM: Literal['tb16-purpledream'] = 'tb16-purpledream'
    TB16_QUALIA: Literal['tb16-qualia'] = 'tb16-qualia'
    TB16_RAILSCASTS: Literal['tb16-railscasts'] = 'tb16-railscasts'
    TB16_REBECCA: Literal['tb16-rebecca'] = 'tb16-rebecca'
    TB16_ROSE_PINE_MOON: Literal['tb16-rose-pine-moon'] = 'tb16-rose-pine-moon'
    TB16_ROSE_PINE: Literal['tb16-rose-pine'] = 'tb16-rose-pine'
    TB16_SAGA: Literal['tb16-saga'] = 'tb16-saga'
    TB16_SANDCASTLE: Literal['tb16-sandcastle'] = 'tb16-sandcastle'
    TB16_SELENIZED_BLACK: Literal['tb16-selenized-black'] = 'tb16-selenized-black'
    TB16_SELENIZED_DARK: Literal['tb16-selenized-dark'] = 'tb16-selenized-dark'
    TB16_SETI: Literal['tb16-seti'] = 'tb16-seti'
    TB16_SHADES_OF_PURPLE: Literal['tb16-shades-of-purple'] = 'tb16-shades-of-purple'
    TB16_SHADESMEAR_DARK: Literal['tb16-shadesmear-dark'] = 'tb16-shadesmear-dark'
    TB16_SILK_DARK: Literal['tb16-silk-dark'] = 'tb16-silk-dark'
    TB16_SNAZZY: Literal['tb16-snazzy'] = 'tb16-snazzy'
    TB16_SOLARFLARE: Literal['tb16-solarflare'] = 'tb16-solarflare'
    TB16_SOLARIZED_DARK: Literal['tb16-solarized-dark'] = 'tb16-solarized-dark'
    TB16_SPACEDUCK: Literal['tb16-spaceduck'] = 'tb16-spaceduck'
    TB16_SPACEMACS: Literal['tb16-spacemacs'] = 'tb16-spacemacs'
    TB16_SPARKY: Literal['tb16-sparky'] = 'tb16-sparky'
    TB16_STANDARDIZED_DARK: Literal['tb16-standardized-dark'] = 'tb16-standardized-dark'
    TB16_STELLA: Literal['tb16-stella'] = 'tb16-stella'
    TB16_SUMMERFRUIT_DARK: Literal['tb16-summerfruit-dark'] = 'tb16-summerfruit-dark'
    TB16_SYNTH_MIDNIGHT_DARK: Literal['tb16-synth-midnight-dark'] = 'tb16-synth-midnight-dark'
    TB16_TANGO: Literal['tb16-tango'] = 'tb16-tango'
    TB16_TENDER: Literal['tb16-tender'] = 'tb16-tender'
    TB16_TERRACOTTA_DARK: Literal['tb16-terracotta-dark'] = 'tb16-terracotta-dark'
    TB16_TOKYO_CITY_DARK: Literal['tb16-tokyo-city-dark'] = 'tb16-tokyo-city-dark'
    TB16_TOKYO_CITY_TERMINAL_DARK: Literal[
        'tb16-tokyo-city-terminal-dark'] = 'tb16-tokyo-city-terminal-dark'
    TB16_TOKYO_NIGHT_DARK: Literal['tb16-tokyo-night-dark'] = 'tb16-tokyo-night-dark'
    TB16_TOKYO_NIGHT_STORM: Literal['tb16-tokyo-night-storm'] = 'tb16-tokyo-night-storm'
    TB16_TOKYODARK_TERMINAL: Literal['tb16-tokyodark-terminal'] = 'tb16-tokyodark-terminal'
    TB16_TOKYODARK: Literal['tb16-tokyodark'] = 'tb16-tokyodark'
    TB16_TOMORROW_NIGHT_EIGHTIES: Literal[
        'tb16-tomorrow-night-eighties'] = 'tb16-tomorrow-night-eighties'
    TB16_TOMORROW_NIGHT: Literal['tb16-tomorrow-night'] = 'tb16-tomorrow-night'
    TB16_TUBE: Literal['tb16-tube'] = 'tb16-tube'
    TB16_TWILIGHT: Literal['tb16-twilight'] = 'tb16-twilight'
    TB16_UNIKITTY_DARK: Literal['tb16-unikitty-dark'] = 'tb16-unikitty-dark'
    TB16_UNIKITTY_REVERSIBLE: Literal['tb16-unikitty-reversible'] = 'tb16-unikitty-reversible'
    TB16_UWUNICORN: Literal['tb16-uwunicorn'] = 'tb16-uwunicorn'
    TB16_VESPER: Literal['tb16-vesper'] = 'tb16-vesper'
    TB16_VICE: Literal['tb16-vice'] = 'tb16-vice'
    TB16_WINDOWS_10: Literal['tb16-windows-10'] = 'tb16-windows-10'
    TB16_WINDOWS_95: Literal['tb16-windows-95'] = 'tb16-windows-95'
    TB16_WINDOWS_HIGHCONTRAST: Literal['tb16-windows-highcontrast'] = 'tb16-windows-highcontrast'
    TB16_WINDOWS_NT: Literal['tb16-windows-nt'] = 'tb16-windows-nt'
    TB16_WOODLAND: Literal['tb16-woodland'] = 'tb16-woodland'
    TB16_XCODE_DUSK: Literal['tb16-xcode-dusk'] = 'tb16-xcode-dusk'
    TB16_ZENBONES: Literal['tb16-zenbones'] = 'tb16-zenbones'
    TB16_ZENBURN: Literal['tb16-zenburn'] = 'tb16-zenburn'


class DarkLowContrastColorStyles(LiteralEnum[str]):
    __doc__ = dedent("""
        Lower contrast dark color styles for syntax highlighting.
        """) + _GENERAL_COLOR_STYLE_DOCSTRING

    Literals = Literal['coffee',
                       'dracula',
                       'fruity',
                       'gruvbox-dark',
                       'inkpot',
                       'material',
                       'native',
                       'nord-darker',
                       'nord',
                       'one-dark',
                       'paraiso-dark',
                       'solarized-dark',
                       'stata-dark',
                       'vim',
                       'zenburn',
                       'tb16-apprentice',
                       'tb16-brogrammer',
                       'tb16-brushtrees-dark',
                       'tb16-eris',
                       'tb16-eva-dim',
                       'tb16-eva',
                       'tb16-icy',
                       'tb16-lime',
                       'tb16-material-vivid',
                       'tb16-papercolor-dark',
                       'tb16-pico',
                       'tb16-summercamp',
                       'tb16-tarot',
                       'tb16-tokyo-night-moon',
                       'tb16-tokyo-night-terminal-dark',
                       'tb16-tokyo-night-terminal-storm',
                       'tb16-vulcan']

    COFFEE: Literal['coffee'] = 'coffee'
    DRACULA: Literal['dracula'] = 'dracula'
    FRUITY: Literal['fruity'] = 'fruity'
    GRUVBOX_DARK: Literal['gruvbox-dark'] = 'gruvbox-dark'
    INKPOT: Literal['inkpot'] = 'inkpot'
    MATERIAL: Literal['material'] = 'material'
    NATIVE: Literal['native'] = 'native'
    NORD_DARKER: Literal['nord-darker'] = 'nord-darker'
    NORD: Literal['nord'] = 'nord'
    ONE_DARK: Literal['one-dark'] = 'one-dark'
    PARAISO_DARK: Literal['paraiso-dark'] = 'paraiso-dark'
    SOLARIZED_DARK: Literal['solarized-dark'] = 'solarized-dark'
    STATA_DARK: Literal['stata-dark'] = 'stata-dark'
    VIM: Literal['vim'] = 'vim'
    ZENBURN: Literal['zenburn'] = 'zenburn'
    TB16_APPRENTICE: Literal['tb16-apprentice'] = 'tb16-apprentice'
    TB16_BROGRAMMER: Literal['tb16-brogrammer'] = 'tb16-brogrammer'
    TB16_BRUSHTREES_DARK: Literal['tb16-brushtrees-dark'] = 'tb16-brushtrees-dark'
    TB16_ERIS: Literal['tb16-eris'] = 'tb16-eris'
    TB16_EVA_DIM: Literal['tb16-eva-dim'] = 'tb16-eva-dim'
    TB16_EVA: Literal['tb16-eva'] = 'tb16-eva'
    TB16_ICY: Literal['tb16-icy'] = 'tb16-icy'
    TB16_LIME: Literal['tb16-lime'] = 'tb16-lime'
    TB16_MATERIAL_VIVID: Literal['tb16-material-vivid'] = 'tb16-material-vivid'
    TB16_PAPERCOLOR_DARK: Literal['tb16-papercolor-dark'] = 'tb16-papercolor-dark'
    TB16_PICO: Literal['tb16-pico'] = 'tb16-pico'
    TB16_SUMMERCAMP: Literal['tb16-summercamp'] = 'tb16-summercamp'
    TB16_TAROT: Literal['tb16-tarot'] = 'tb16-tarot'
    TB16_TOKYO_NIGHT_MOON: Literal['tb16-tokyo-night-moon'] = 'tb16-tokyo-night-moon'
    TB16_TOKYO_NIGHT_TERMINAL_DARK: Literal[
        'tb16-tokyo-night-terminal-dark'] = 'tb16-tokyo-night-terminal-dark'
    TB16_TOKYO_NIGHT_TERMINAL_STORM: Literal[
        'tb16-tokyo-night-terminal-storm'] = 'tb16-tokyo-night-terminal-storm'
    TB16_VULCAN: Literal['tb16-vulcan'] = 'tb16-vulcan'


class LightHighContrastColorStyles(LiteralEnum[str]):
    __doc__ = dedent("""
        High contrast light color styles for syntax highlighting.
        """) + _GENERAL_COLOR_STYLE_DOCSTRING

    Literals = Literal['bw',
                       'default',
                       'sas',
                       'staroffice',
                       'xcode',
                       'tb16-atelier-cave-light',
                       'tb16-atelier-dune-light',
                       'tb16-atelier-estuary-light',
                       'tb16-atelier-forest-light',
                       'tb16-atelier-heath-light',
                       'tb16-atelier-lakeside-light',
                       'tb16-atelier-plateau-light',
                       'tb16-atelier-savanna-light',
                       'tb16-atelier-seaside-light',
                       'tb16-atelier-sulphurpool-light',
                       'tb16-ayu-light',
                       'tb16-catppuccin-latte',
                       'tb16-classic-light',
                       'tb16-cupertino',
                       'tb16-da-one-paper',
                       'tb16-da-one-white',
                       'tb16-danqing-light',
                       'tb16-default-light',
                       'tb16-dirtysea',
                       'tb16-edge-light',
                       'tb16-embers-light',
                       'tb16-emil',
                       'tb16-equilibrium-gray-light',
                       'tb16-equilibrium-light',
                       'tb16-fruit-soda',
                       'tb16-github',
                       'tb16-google-light',
                       'tb16-grayscale-light',
                       'tb16-gruvbox-light-hard',
                       'tb16-gruvbox-light-medium',
                       'tb16-gruvbox-light-soft',
                       'tb16-gruvbox-material-light-hard',
                       'tb16-gruvbox-material-light-medium',
                       'tb16-gruvbox-material-light-soft',
                       'tb16-harmonic16-light',
                       'tb16-heetch-light',
                       'tb16-horizon-light',
                       'tb16-horizon-terminal-light',
                       'tb16-humanoid-light',
                       'tb16-ia-light',
                       'tb16-measured-light',
                       'tb16-mexico-light',
                       'tb16-nord-light',
                       'tb16-one-light',
                       'tb16-oxocarbon-light',
                       'tb16-papercolor-light',
                       'tb16-precious-light-warm',
                       'tb16-precious-light-white',
                       'tb16-primer-light',
                       'tb16-rose-pine-dawn',
                       'tb16-sagelight',
                       'tb16-sakura',
                       'tb16-selenized-light',
                       'tb16-selenized-white',
                       'tb16-shadesmear-light',
                       'tb16-shapeshifter',
                       'tb16-silk-light',
                       'tb16-solarflare-light',
                       'tb16-solarized-light',
                       'tb16-standardized-light',
                       'tb16-still-alive',
                       'tb16-summerfruit-light',
                       'tb16-synth-midnight-light',
                       'tb16-terracotta',
                       'tb16-tokyo-city-light',
                       'tb16-tokyo-city-terminal-light',
                       'tb16-tokyo-night-light',
                       'tb16-tokyo-night-terminal-light',
                       'tb16-tomorrow',
                       'tb16-unikitty-light',
                       'tb16-windows-95-light',
                       'tb16-windows-highcontrast-light']

    BW: Literal['bw'] = 'bw'
    DEFAULT: Literal['default'] = 'default'
    SAS: Literal['sas'] = 'sas'
    STAROFFICE: Literal['staroffice'] = 'staroffice'
    XCODE: Literal['xcode'] = 'xcode'
    TB16_ATELIER_CAVE_LIGHT: Literal['tb16-atelier-cave-light'] = 'tb16-atelier-cave-light'
    TB16_ATELIER_DUNE_LIGHT: Literal['tb16-atelier-dune-light'] = 'tb16-atelier-dune-light'
    TB16_ATELIER_ESTUARY_LIGHT: Literal['tb16-atelier-estuary-light'] = 'tb16-atelier-estuary-light'
    TB16_ATELIER_FOREST_LIGHT: Literal['tb16-atelier-forest-light'] = 'tb16-atelier-forest-light'
    TB16_ATELIER_HEATH_LIGHT: Literal['tb16-atelier-heath-light'] = 'tb16-atelier-heath-light'
    TB16_ATELIER_LAKESIDE_LIGHT: Literal[
        'tb16-atelier-lakeside-light'] = 'tb16-atelier-lakeside-light'
    TB16_ATELIER_PLATEAU_LIGHT: Literal['tb16-atelier-plateau-light'] = 'tb16-atelier-plateau-light'
    TB16_ATELIER_SAVANNA_LIGHT: Literal['tb16-atelier-savanna-light'] = 'tb16-atelier-savanna-light'
    TB16_ATELIER_SEASIDE_LIGHT: Literal['tb16-atelier-seaside-light'] = 'tb16-atelier-seaside-light'
    TB16_ATELIER_SULPHURPOOL_LIGHT: Literal[
        'tb16-atelier-sulphurpool-light'] = 'tb16-atelier-sulphurpool-light'
    TB16_AYU_LIGHT: Literal['tb16-ayu-light'] = 'tb16-ayu-light'
    TB16_CATPPUCCIN_LATTE: Literal['tb16-catppuccin-latte'] = 'tb16-catppuccin-latte'
    TB16_CLASSIC_LIGHT: Literal['tb16-classic-light'] = 'tb16-classic-light'
    TB16_CUPERTINO: Literal['tb16-cupertino'] = 'tb16-cupertino'
    TB16_DA_ONE_PAPER: Literal['tb16-da-one-paper'] = 'tb16-da-one-paper'
    TB16_DA_ONE_WHITE: Literal['tb16-da-one-white'] = 'tb16-da-one-white'
    TB16_DANQING_LIGHT: Literal['tb16-danqing-light'] = 'tb16-danqing-light'
    TB16_DEFAULT_LIGHT: Literal['tb16-default-light'] = 'tb16-default-light'
    TB16_DIRTYSEA: Literal['tb16-dirtysea'] = 'tb16-dirtysea'
    TB16_EDGE_LIGHT: Literal['tb16-edge-light'] = 'tb16-edge-light'
    TB16_EMBERS_LIGHT: Literal['tb16-embers-light'] = 'tb16-embers-light'
    TB16_EMIL: Literal['tb16-emil'] = 'tb16-emil'
    TB16_EQUILIBRIUM_GRAY_LIGHT: Literal[
        'tb16-equilibrium-gray-light'] = 'tb16-equilibrium-gray-light'
    TB16_EQUILIBRIUM_LIGHT: Literal['tb16-equilibrium-light'] = 'tb16-equilibrium-light'
    TB16_FRUIT_SODA: Literal['tb16-fruit-soda'] = 'tb16-fruit-soda'
    TB16_GITHUB: Literal['tb16-github'] = 'tb16-github'
    TB16_GOOGLE_LIGHT: Literal['tb16-google-light'] = 'tb16-google-light'
    TB16_GRAYSCALE_LIGHT: Literal['tb16-grayscale-light'] = 'tb16-grayscale-light'
    TB16_GRUVBOX_LIGHT_HARD: Literal['tb16-gruvbox-light-hard'] = 'tb16-gruvbox-light-hard'
    TB16_GRUVBOX_LIGHT_MEDIUM: Literal['tb16-gruvbox-light-medium'] = 'tb16-gruvbox-light-medium'
    TB16_GRUVBOX_LIGHT_SOFT: Literal['tb16-gruvbox-light-soft'] = 'tb16-gruvbox-light-soft'
    TB16_GRUVBOX_MATERIAL_LIGHT_HARD: Literal[
        'tb16-gruvbox-material-light-hard'] = 'tb16-gruvbox-material-light-hard'
    TB16_GRUVBOX_MATERIAL_LIGHT_MEDIUM: Literal[
        'tb16-gruvbox-material-light-medium'] = 'tb16-gruvbox-material-light-medium'
    TB16_GRUVBOX_MATERIAL_LIGHT_SOFT: Literal[
        'tb16-gruvbox-material-light-soft'] = 'tb16-gruvbox-material-light-soft'
    TB16_HARMONIC16_LIGHT: Literal['tb16-harmonic16-light'] = 'tb16-harmonic16-light'
    TB16_HEETCH_LIGHT: Literal['tb16-heetch-light'] = 'tb16-heetch-light'
    TB16_HORIZON_LIGHT: Literal['tb16-horizon-light'] = 'tb16-horizon-light'
    TB16_HORIZON_TERMINAL_LIGHT: Literal[
        'tb16-horizon-terminal-light'] = 'tb16-horizon-terminal-light'
    TB16_HUMANOID_LIGHT: Literal['tb16-humanoid-light'] = 'tb16-humanoid-light'
    TB16_IA_LIGHT: Literal['tb16-ia-light'] = 'tb16-ia-light'
    TB16_MEASURED_LIGHT: Literal['tb16-measured-light'] = 'tb16-measured-light'
    TB16_MEXICO_LIGHT: Literal['tb16-mexico-light'] = 'tb16-mexico-light'
    TB16_NORD_LIGHT: Literal['tb16-nord-light'] = 'tb16-nord-light'
    TB16_ONE_LIGHT: Literal['tb16-one-light'] = 'tb16-one-light'
    TB16_OXOCARBON_LIGHT: Literal['tb16-oxocarbon-light'] = 'tb16-oxocarbon-light'
    TB16_PAPERCOLOR_LIGHT: Literal['tb16-papercolor-light'] = 'tb16-papercolor-light'
    TB16_PRECIOUS_LIGHT_WARM: Literal['tb16-precious-light-warm'] = 'tb16-precious-light-warm'
    TB16_PRECIOUS_LIGHT_WHITE: Literal['tb16-precious-light-white'] = 'tb16-precious-light-white'
    TB16_PRIMER_LIGHT: Literal['tb16-primer-light'] = 'tb16-primer-light'
    TB16_ROSE_PINE_DAWN: Literal['tb16-rose-pine-dawn'] = 'tb16-rose-pine-dawn'
    TB16_SAGELIGHT: Literal['tb16-sagelight'] = 'tb16-sagelight'
    TB16_SAKURA: Literal['tb16-sakura'] = 'tb16-sakura'
    TB16_SELENIZED_LIGHT: Literal['tb16-selenized-light'] = 'tb16-selenized-light'
    TB16_SELENIZED_WHITE: Literal['tb16-selenized-white'] = 'tb16-selenized-white'
    TB16_SHADESMEAR_LIGHT: Literal['tb16-shadesmear-light'] = 'tb16-shadesmear-light'
    TB16_SHAPESHIFTER: Literal['tb16-shapeshifter'] = 'tb16-shapeshifter'
    TB16_SILK_LIGHT: Literal['tb16-silk-light'] = 'tb16-silk-light'
    TB16_SOLARFLARE_LIGHT: Literal['tb16-solarflare-light'] = 'tb16-solarflare-light'
    TB16_SOLARIZED_LIGHT: Literal['tb16-solarized-light'] = 'tb16-solarized-light'
    TB16_STANDARDIZED_LIGHT: Literal['tb16-standardized-light'] = 'tb16-standardized-light'
    TB16_STILL_ALIVE: Literal['tb16-still-alive'] = 'tb16-still-alive'
    TB16_SUMMERFRUIT_LIGHT: Literal['tb16-summerfruit-light'] = 'tb16-summerfruit-light'
    TB16_SYNTH_MIDNIGHT_LIGHT: Literal['tb16-synth-midnight-light'] = 'tb16-synth-midnight-light'
    TB16_TERRACOTTA: Literal['tb16-terracotta'] = 'tb16-terracotta'
    TB16_TOKYO_CITY_LIGHT: Literal['tb16-tokyo-city-light'] = 'tb16-tokyo-city-light'
    TB16_TOKYO_CITY_TERMINAL_LIGHT: Literal[
        'tb16-tokyo-city-terminal-light'] = 'tb16-tokyo-city-terminal-light'
    TB16_TOKYO_NIGHT_LIGHT: Literal['tb16-tokyo-night-light'] = 'tb16-tokyo-night-light'
    TB16_TOKYO_NIGHT_TERMINAL_LIGHT: Literal[
        'tb16-tokyo-night-terminal-light'] = 'tb16-tokyo-night-terminal-light'
    TB16_TOMORROW: Literal['tb16-tomorrow'] = 'tb16-tomorrow'
    TB16_UNIKITTY_LIGHT: Literal['tb16-unikitty-light'] = 'tb16-unikitty-light'
    TB16_WINDOWS_95_LIGHT: Literal['tb16-windows-95-light'] = 'tb16-windows-95-light'
    TB16_WINDOWS_HIGHCONTRAST_LIGHT: Literal[
        'tb16-windows-highcontrast-light'] = 'tb16-windows-highcontrast-light'


class LightLowContrastColorStyles(LiteralEnum[str]):
    __doc__ = dedent("""
        Lower contrast dark color styles for syntax highlighting.
        """) + _GENERAL_COLOR_STYLE_DOCSTRING

    Literals = Literal['abap',
                       'algol',
                       'algol_nu',
                       'arduino',
                       'autumn',
                       'borland',
                       'colorful',
                       'emacs',
                       'friendly_grayscale',
                       'friendly',
                       'gruvbox-light',
                       'igor',
                       'lovelace',
                       'manni',
                       'murphy',
                       'paraiso-light',
                       'pastie',
                       'perldoc',
                       'rainbow_dash',
                       'solarized-light',
                       'stata-light',
                       'tango',
                       'trac',
                       'vs',
                       'tb16-brushtrees',
                       'tb16-cupcake',
                       'tb16-material-lighter',
                       'tb16-windows-10-light',
                       'tb16-windows-nt-light']

    ABAP: Literal['abap'] = 'abap'
    ALGOL: Literal['algol'] = 'algol'
    ALGOL_NU: Literal['algol_nu'] = 'algol_nu'
    ARDUINO: Literal['arduino'] = 'arduino'
    AUTUMN: Literal['autumn'] = 'autumn'
    BORLAND: Literal['borland'] = 'borland'
    COLORFUL: Literal['colorful'] = 'colorful'
    EMACS: Literal['emacs'] = 'emacs'
    FRIENDLY_GRAYSCALE: Literal['friendly_grayscale'] = 'friendly_grayscale'
    FRIENDLY: Literal['friendly'] = 'friendly'
    GRUVBOX_LIGHT: Literal['gruvbox-light'] = 'gruvbox-light'
    IGOR: Literal['igor'] = 'igor'
    LOVELACE: Literal['lovelace'] = 'lovelace'
    MANNI: Literal['manni'] = 'manni'
    MURPHY: Literal['murphy'] = 'murphy'
    PARAISO_LIGHT: Literal['paraiso-light'] = 'paraiso-light'
    PASTIE: Literal['pastie'] = 'pastie'
    PERLDOC: Literal['perldoc'] = 'perldoc'
    RAINBOW_DASH: Literal['rainbow_dash'] = 'rainbow_dash'
    SOLARIZED_LIGHT: Literal['solarized-light'] = 'solarized-light'
    STATA_LIGHT: Literal['stata-light'] = 'stata-light'
    TANGO: Literal['tango'] = 'tango'
    TRAC: Literal['trac'] = 'trac'
    VS: Literal['vs'] = 'vs'
    TB16_BRUSHTREES: Literal['tb16-brushtrees'] = 'tb16-brushtrees'
    TB16_CUPCAKE: Literal['tb16-cupcake'] = 'tb16-cupcake'
    TB16_MATERIAL_LIGHTER: Literal['tb16-material-lighter'] = 'tb16-material-lighter'
    TB16_WINDOWS_10_LIGHT: Literal['tb16-windows-10-light'] = 'tb16-windows-10-light'
    TB16_WINDOWS_NT_LIGHT: Literal['tb16-windows-nt-light'] = 'tb16-windows-nt-light'


class AllColorStyles(RecommendedColorStyles,
                     DarkHighContrastColorStyles,
                     DarkLowContrastColorStyles,
                     LightHighContrastColorStyles,
                     LightLowContrastColorStyles):
    __doc__ = dedent("""
        All color styles available for syntax highlighting.
        """) + _GENERAL_COLOR_STYLE_DOCSTRING

    Literals = Literal[RecommendedColorStyles.Literals,
                       DarkHighContrastColorStyles.Literals,
                       DarkLowContrastColorStyles.Literals,
                       LightHighContrastColorStyles.Literals,
                       LightLowContrastColorStyles.Literals]


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


class PanelDesign(LiteralEnum[str]):
    """
    Visual design for the layout of the output.

    The layout designs are:
    - `TABLE`: The output is displayed as a simple table grid
    - `PANELS`: The output is displayed as a set of panels
    """

    Literals = Literal['table_grid', 'panels']

    TABLE_GRID: Literal['table_grid'] = 'table_grid'
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
