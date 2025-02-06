from abc import ABCMeta, abstractmethod
import functools
import inspect
import os
import re
from textwrap import dedent
from typing import Any, cast

import humanize
from IPython.display import display
from IPython.lib.pretty import RepresentationPrinter
import objsize
from pygments.styles import get_style_by_name
from rich.color import Color, ColorType
from rich.color_triplet import ColorTriplet
from rich.syntax import PygmentsSyntaxTheme
from rich.terminal_theme import TerminalTheme
from tabulate import tabulate

from omnipy.data._data_class_creator import DataClassBase
from omnipy.data._display import pretty_repr, PrettyPrinterLib
from omnipy.data.helpers import FailedData, PendingData
import omnipy.util._pydantic as pyd


class BaseDisplayMixin(metaclass=ABCMeta):
    def _repr_pretty_(self, p: RepresentationPrinter, cycle: bool) -> None:
        if cycle:
            p.text(f'{cast(pyd.GenericModel, self).__repr_name__()}(...)')
        else:
            if len(p.stack) == 1:
                p.text(self.pretty_repr())
            else:
                p.text(self.__repr__())

    @abstractmethod
    def pretty_repr(self) -> str:
        ...

    def display(self) -> None:
        display(self)

    def __str__(self) -> str:
        return repr(self)


class ModelDisplayMixin(BaseDisplayMixin):  # noqa: C901
    def pretty_repr(self) -> str:  # noqa: C901
        from omnipy.data.dataset import Dataset, Model

        outer_type = cast(Model, self).outer_type()
        if inspect.isclass(outer_type) and issubclass(outer_type, Dataset):
            return cast(Dataset, self.contents).pretty_repr()

        # tabulate.PRESERVE_WHITESPACE = True  # Does not seem to work together with 'maxcolwidths'

        terminal_size_cols = cast(DataClassBase, self).config.terminal_size_columns
        terminal_size_lines = cast(DataClassBase, self).config.terminal_size_lines

        # header_column_width = len('(bottom')
        # num_columns = 1
        table_chars_width = 4
        # data_column_width = terminal_size_cols - table_chars_width - header_column_width
        num_count_chars = 6
        count_char_padding = 2 + 1
        data_column_width = max(
            terminal_size_cols - table_chars_width - num_count_chars - count_char_padding, 1)
        print(data_column_width)

        # structure = self._pretty_print_model(
        #     data_column_width,
        #     data_indent=2,
        #     simple_cutoff=data_column_width,
        #     # extra_space_due_to_escaped_chars=12,
        #     extra_space_due_to_escaped_chars=0,
        #     pygments_style='one-dark',
        # )
        structure = pretty_repr(
            self,
            indent_tab_size=2,
            max_width=data_column_width,
            height=max(terminal_size_lines - 6, 1),
            pretty_printer=PrettyPrinterLib.RICH,
        )
        structure_lines = structure.splitlines()

        max_section_height = (terminal_size_lines - 8) // 2
        structure_len = len(structure_lines)
        print(structure_len, max_section_height * 2 + 1)

        # def _is_table():
        #     data = self.to_data()
        #     if is_non_str_byte_iterable(data) and has_items(data):
        #         first_level_item = get_first_item(data)
        #         if is_non_str_byte_iterable(first_level_item) and has_items(first_level_item):
        #             second_level_item = get_first_item(first_level_item)
        #             if not is_non_str_byte_iterable(second_level_item):
        #                 return True
        #     return False

        # if structure_len > max_section_height * 2 + 1:
        if True:
            top_structure_end = max_section_height
            bottom_structure_start = structure_len - max_section_height

            from pygments.token import Token
            from rich import box
            from rich.console import Console
            from rich.style import Style
            from rich.syntax import Syntax
            from rich.table import Table
            from rich.text import Text

            pygments_style = get_style_by_name('one-dark')

            # pygments_style = get_style_by_name('friendly')
            # pygments_style = get_style_by_name('monokai')

            class BgColor(Color):
                @property
                def is_system_defined(self) -> bool:
                    """Check if the color is ultimately defined by the system."""
                    return False

                @property
                def is_default(self) -> bool:
                    """Check if the color is a default color."""
                    return True

                def get_truecolor(self,
                                  theme: TerminalTheme | None = None,
                                  foreground: bool = True) -> ColorTriplet:
                    # return (183, 183, 183)
                    # return (55, 55, 55)

                    # rich.color.blend_rgb formula:
                    #   b + (f - b) * c = o
                    # where:
                    #   b = background color
                    #   f = foreground color
                    #   c = cross fade
                    #   o = output color
                    #
                    # Solving for b if o = 0.5(f-t)
                    # where:
                    #   t = terminal background color
                    # gives:
                    #   b + fc - bc = 0.5(f-t)
                    #   b - bc = 0.5(f-t) - fc
                    #   b(1-c) = 0.5f - 0.5t - fc = (0.5 - c)f - 0.5t
                    #   b = (0.5 - c)/(1-c) * f - 0.5/(1-c) * t
                    #
                    # Solving for b if o = 0.5(t-f)
                    # where:
                    #   t = terminal background color
                    # gives:
                    #   b + fc - bc = 0.5(t-f)
                    #   b - bc = 0.5(t-f) - fc
                    #   b(1-c) = 0.5t - 0.5f - fc = 0.5t - (0.5 + c)f
                    #   b = 0.5/(1-c) * t - (0.5 + c)/(1-c) * f

                    pygments_theme = PygmentsSyntaxTheme(theme=pygments_style)
                    fg_color: Color | None = pygments_theme.get_style_for_token(Token.Text).color
                    assert fg_color is not None

                    fg_rgb = fg_color.triplet
                    assert fg_rgb is not None
                    mean_fg_color = (fg_rgb.red + fg_rgb.green + fg_rgb.blue) / 3

                    f = mean_fg_color
                    t = 0 if f > 127 else 255
                    c = 0.3  # cross fade

                    if f > t:
                        mean_bg_color: int = int((0.5 - c) / (1 - c) * f - 0.5 / (1 - c) * t)
                    else:
                        mean_bg_color: int = int(0.5 / (1 - c) * t - (0.5 + c) / (1 - c) * f)

                    return ColorTriplet(mean_bg_color, mean_bg_color, mean_bg_color)

            # pygments_style.transparent_background = False

            class MyStyle(Style):
                @property
                def transparent_background(self) -> bool:
                    return False

            default_bg_color = BgColor('default', ColorType.DEFAULT)
            pygments_style.background_color = default_bg_color  # type: ignore
            pygments_theme = PygmentsSyntaxTheme(theme=pygments_style)
            pygments_theme._background_style = MyStyle(
                bgcolor=BgColor('default', ColorType.DEFAULT))
            max_width = terminal_size_cols - table_chars_width
            # max_width = 140

            top_structure = Syntax(
                structure,
                'python',
                theme=pygments_theme,
                line_numbers=True,
                word_wrap=True,
                # highlight_lines=set(range(structure_len)),
                line_range=(0, top_structure_end),

                # background_color=BgColor('default', ColorType.DEFAULT),
            )
            bottom_structure = Syntax(
                structure,
                'python',
                theme=pygments_theme,
                line_numbers=True,
                word_wrap=True,
                line_range=(bottom_structure_start, None),  # background_color='default',
            )

            table = Table(
                title=Text(self.__class__.__name__, style='table.title'),
                show_header=False,
                box=box.ROUNDED,  # width=terminal_size_cols,
            )

            def print_in_console(data, max_width: int) -> list[str]:
                console = Console(color_system='truecolor', width=max_width)
                console.begin_capture()
                console.print(data)
                printed_data = console.end_capture()
                # return printed_data.splitlines()
                ansii_escape = r'\x1b\[[\d;]*m'
                return list(
                    re.sub(rf'\s+({ansii_escape}*)$', '\\1', line)
                    for line in printed_data.splitlines())

            printed_top_structure_lines = print_in_console(top_structure, max_width)
            print(printed_top_structure_lines)
            printed_bottom_structure_lines = print_in_console(bottom_structure, max_width)

            print(f'{max_width=}')

            # table.add_column('Index', justify='right')
            table.add_column('Structure', justify='left')

            # table.add_row(
            #     os.linesep.join(str(i + 1) for i in range(max_section_height)),
            #     os.linesep.join(printed_top_structure_lines))

            for i in range(max_section_height):
                table.add_row(
                    Text.from_ansi(printed_top_structure_lines[i]),
                    end_section=i == max_section_height - 1)
            for i in range(max_section_height):
                table.add_row(Text.from_ansi(printed_bottom_structure_lines[i]))

            # table.add_row(os.linesep.join(printed_bottom_structure_lines))
            # table.add_row(top_structure, end_section=True)
            # table.add_row(bottom_structure)

            console = Console(
                color_system='truecolor',  # width=terminal_size_cols,
                # height=terminal_size_lines,
            )
            # print(top_structure._get_number_styles(console))
            console.begin_capture()
            console.print(table)
            out = console.end_capture()

        else:
            out = tabulate(
                (
                    ('#', self.__class__.__name__),
                    (os.linesep.join(str(i) for i in range(structure_len)),
                     os.linesep.join(structure_lines)),
                ),
                maxcolwidths=[num_count_chars, data_column_width],
                tablefmt='rounded_grid',
            )

        return out

    def _fixup_pretty_print(self, structure):
        # Split into lines and remove the first line
        structure_lines = structure.splitlines()[1:]

        # Remove 'self: ' from the second line (now the first line)
        structure_lines[0] = re.sub(r'^(\s+)self\S*: ', '\\1', structure_lines[0])

        # Remove extra debug output from the last line
        structure_lines[-1] = re.sub(r'\(\S+\) (len=\d+)?$', '', structure_lines[-1])

        # Join and dedent the lines
        return dedent(os.linesep.join(structure_lines))


class DatasetDisplayMixin(BaseDisplayMixin):
    def pretty_repr(self) -> str:
        from omnipy.data.dataset import Dataset

        return tabulate(
            ((
                i,
                k,
                self._type_str(v),
                self._len_if_available(v),
                self._obj_size_if_available(v),
            ) for i, (k, v) in enumerate(cast(Dataset, self).data.items())),
            ('#', 'Data file name', 'Type', 'Length', 'Size (in memory)'),
            tablefmt='rounded_outline',
        )

    @classmethod
    def _type_str(cls, obj: Any) -> str:
        if isinstance(obj, PendingData):
            return f'{obj.job_name} -> Data pending...'
        elif isinstance(obj, FailedData):
            return f'{obj.job_name} -> {obj.exception.__class__.__name__}: {obj.exception}'
        else:
            return type(obj).__name__

    @classmethod
    def _len_if_available(cls, obj: Any) -> int | str:
        try:
            return len(obj)
        except TypeError:
            return 'N/A'

    @classmethod
    def _obj_size_if_available(cls, obj: Any) -> str:
        if isinstance(obj, PendingData):
            return 'N/A'
        else:
            try:
                cached_obj_size_func = functools.cache(cls._obj_size)
                return cached_obj_size_func(obj)
            except TypeError:
                return cls._obj_size(obj)

    @staticmethod
    def _obj_size(obj: Any) -> str:
        return humanize.naturalsize(objsize.get_deep_size(obj))
