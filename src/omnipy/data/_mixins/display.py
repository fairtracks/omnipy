from abc import ABCMeta, abstractmethod
import functools
import inspect
import os
from textwrap import dedent
from types import ModuleType
from typing import Any, cast

from devtools import debug, PrettyFormat
import humanize
from IPython.display import display
from IPython.lib.pretty import RepresentationPrinter
import objsize
from tabulate import tabulate

from omnipy.data._data_class_creator import DataClassBase
from omnipy.data.helpers import FailedData, PendingData
import omnipy.util._pydantic as pyd
from omnipy.util.helpers import get_first_item, has_items, is_non_str_byte_iterable


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


class ModelDisplayMixin(BaseDisplayMixin):
    def pretty_repr(self) -> str:
        from omnipy.data.dataset import Dataset, Model

        outer_type = cast(Model, self).outer_type()
        if inspect.isclass(outer_type) and issubclass(outer_type, Dataset):
            return cast(Dataset, self.contents).pretty_repr()

        # tabulate.PRESERVE_WHITESPACE = True  # Does not seem to work together with 'maxcolwidths'

        terminal_size_cols = cast(DataClassBase, self).config.terminal_size_columns
        terminal_size_lines = cast(DataClassBase, self).config.terminal_size_lines

        header_column_width = len('(bottom')
        num_columns = 2
        table_chars_width = 3 * num_columns + 1
        data_column_width = terminal_size_cols - table_chars_width - header_column_width

        data_indent = 2
        extra_space_due_to_escaped_chars = 12

        debug_module = cast(ModuleType, inspect.getmodule(debug))
        debug_module.pformat = PrettyFormat(  # type: ignore[attr-defined]
            indent_step=data_indent,
            simple_cutoff=20,
            width=data_column_width - data_indent - extra_space_due_to_escaped_chars,
            yield_from_generators=True,
        )

        structure = str(debug.format(self))
        structure_lines = structure.splitlines()
        new_structure_lines = dedent(os.linesep.join(structure_lines[1:])).splitlines()
        if new_structure_lines[0].startswith('self: '):
            new_structure_lines[0] = new_structure_lines[0][5:]
        max_section_height = (terminal_size_lines - 8) // 2
        structure_len = len(new_structure_lines)

        def _is_table():
            data = self.to_data()
            if is_non_str_byte_iterable(data) and has_items(data):
                first_level_item = get_first_item(data)
                if is_non_str_byte_iterable(first_level_item) and has_items(first_level_item):
                    second_level_item = get_first_item(first_level_item)
                    if not is_non_str_byte_iterable(second_level_item):
                        return True
            return False

        if structure_len > max_section_height * 2 + 1:
            top_structure_end = max_section_height
            bottom_structure_start = structure_len - max_section_height

            top_structure = os.linesep.join(new_structure_lines[:top_structure_end])
            bottom_structure = os.linesep.join(new_structure_lines[bottom_structure_start:])

            out = tabulate(
                (
                    ('#', self.__class__.__name__),
                    (os.linesep.join(str(i) for i in range(top_structure_end)), top_structure),
                    (os.linesep.join(str(i) for i in range(bottom_structure_start, structure_len)),
                     bottom_structure),
                ),
                maxcolwidths=[header_column_width, data_column_width],
                tablefmt='rounded_grid',
            )
        else:
            out = tabulate(
                (
                    ('#', self.__class__.__name__),
                    (os.linesep.join(str(i) for i in range(structure_len)),
                     os.linesep.join(new_structure_lines)),
                ),
                maxcolwidths=[header_column_width, data_column_width],
                tablefmt='rounded_grid',
            )

        return out


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
