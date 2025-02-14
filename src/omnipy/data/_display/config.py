from enum import Enum

from omnipy.util._pydantic import ConfigDict, dataclass, Extra, NonNegativeInt


class PrettyPrinterLib(str, Enum):
    RICH = 'rich'
    DEVTOOLS = 'devtools'


@dataclass(kw_only=True, config=ConfigDict(extra=Extra.forbid))
class OutputConfig:
    indent_tab_size: NonNegativeInt = 2
    debug_mode: bool = False
    pretty_printer: PrettyPrinterLib = PrettyPrinterLib.RICH
