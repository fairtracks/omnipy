from dataclasses import dataclass
import shutil

_terminal_size = shutil.get_terminal_size()


@dataclass
class DataConfig:
    interactive_mode: bool = True
    terminal_size_columns: int = _terminal_size.columns
    terminal_size_lines: int = _terminal_size.lines
