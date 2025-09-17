from typing import ClassVar

import compact_json.formatter
from typing_extensions import override

from omnipy.data._display.dimensions import has_width
from omnipy.data._display.panel.draft.base import DraftPanel
from omnipy.data._display.panel.typedefs import FrameT
from omnipy.data._display.text.pretty_printer.base import ConstraintTighteningPrettyPrinterMixin
from omnipy.data._display.text.pretty_printer.mixins import JsonStatsTighteningPrettyPrinterMixin
from omnipy.shared.constants import TERMINAL_DEFAULT_WIDTH


class CompactJsonPrettyPrinter(
        JsonStatsTighteningPrettyPrinterMixin,
        ConstraintTighteningPrettyPrinterMixin[object],
):
    CONSTRAINT_STAT_NAME: ClassVar[str] = 'max_inline_list_or_dict_width_excl'

    @override
    def print_draft_to_str(self, draft_panel: DraftPanel[object, FrameT]) -> str:
        max_inline_list_or_dict_width_excl = \
            draft_panel.constraints.max_inline_list_or_dict_width_excl

        if max_inline_list_or_dict_width_excl is not None:
            max_inline_length = max_inline_list_or_dict_width_excl
        elif has_width(draft_panel.frame.dims):
            max_inline_length = draft_panel.frame.dims.width
        else:
            max_inline_length = TERMINAL_DEFAULT_WIDTH

        assert max_inline_length is not None

        json_formatter = compact_json.formatter.Formatter(
            max_inline_length=max_inline_length,
            max_inline_complexity=2,
            max_compact_list_complexity=2,
            simple_bracket_padding=True,
            indent_spaces=draft_panel.config.indent,
            table_dict_minimum_similarity=90,
            table_list_minimum_similarity=90,
            dont_justify_numbers=True,
            ensure_ascii=False,
            east_asian_string_widths=True,
            multiline_compact_dict=False,
            omit_trailing_whitespace=True,
        )
        return json_formatter.serialize(draft_panel.content)  # pyright: ignore [reportArgumentType]
