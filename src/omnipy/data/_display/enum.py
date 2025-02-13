from enum import Enum


class PrettyPrinterLib(str, Enum):
    DEVTOOLS = 'devtools'
    RICH = 'rich'
