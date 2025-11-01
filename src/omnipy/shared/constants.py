# Data - General
import omnipy.util._pydantic as pyd

ROOT_KEY = '__root__'
DATA_KEY = 'data'
UNTITLED_KEY = '_untitled'
ASYNC_LOAD_SLEEP_TIME = 0.05

# Data - Display

MAX_TERMINAL_SIZE = 2**16 - 1
MIN_PANEL_WIDTH = 3
MIN_CROP_WIDTH = 33

TERMINAL_DEFAULT_WIDTH: pyd.NonNegativeInt | None = 80
TERMINAL_DEFAULT_HEIGHT: pyd.NonNegativeInt | None = 24

JUPYTER_DEFAULT_WIDTH: pyd.NonNegativeInt | None = 112
JUPYTER_DEFAULT_HEIGHT: pyd.NonNegativeInt | None = 48

BROWSER_DEFAULT_WIDTH: pyd.NonNegativeInt | None = 160
BROWSER_DEFAULT_HEIGHT: pyd.NonNegativeInt | None = None

# Data - Display - Panel

# TODO: If an issue in practice, consider making TITLE_BLANK_LINES depend on
#       the panel style (i.e., no blank lines for nested layout panels).
TITLE_BLANK_LINES = 1
DOUBLE_LINE_TITLE_HEIGHT = TITLE_BLANK_LINES + 2
SINGLE_LINE_TITLE_HEIGHT = TITLE_BLANK_LINES + 1

MIN_PANEL_LINES_SHOWN_TO_ALLOW_DOUBLE_LINE_TITLE = 8
MIN_PANEL_LINES_SHOWN_TO_ALLOW_SINGLE_LINE_TITLE = 3

PANEL_TITLE_BASE_16_TOKEN = ('Base16', 'Classes')
PANEL_TITLE_GENERAL_TOKEN = ('Name', 'Class')
PANEL_TITLE_EXTRA_STYLE = 'italic not bold not underline'
TABLE_BORDER_BASE_16_TOKEN = ('Base16', 'LineHighlight')
TABLE_BORDER_GENERAL_TOKEN = ('Comment',)
INFO_BASE_16_TOKEN = ('Base16', 'DarkForeground')
INFO_GENERAL_TOKEN = ('Comment',)

# Data - Display - Styles
STYLE_CLS_NAME_TINTED_BASE16_PREFIX = 'TintedBase16'
STYLE_CLS_NAME_SUFFIX = 'Style'
THEME_KEY_TINTED_BASE16_SUFFIX = '-t16'
PYGMENTS_SUFFIX = '-pygments'
ANSI_PREFIX = 'ansi-'
RANDOM_PREFIX = 'random'
AUTO_VALUE = 'auto'
