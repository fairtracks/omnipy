import dataclasses

import compact_json.formatter
from typing_extensions import override

from omnipy.data._display.constraints import Constraints
from omnipy.data._display.dimensions import DimensionsWithWidth, has_width
from omnipy.data._display.frame import FrameWithWidth
from omnipy.data._display.panel.draft.base import DraftPanel
from omnipy.data._display.panel.draft.text import ReflowedTextDraftPanel
from omnipy.data._display.panel.typedefs import FrameT
from omnipy.data._display.text.pretty_printer.base import WidthReducingPrettyPrinter
from omnipy.data._display.text.pretty_printer.mixins import JsonWidthReducingPrettyPrinterMixin
from omnipy.shared.constants import TERMINAL_DEFAULT_WIDTH
from omnipy.util import _pydantic as pyd


class CompactJsonPrettyPrinter(JsonWidthReducingPrettyPrinterMixin,
                               WidthReducingPrettyPrinter[object]):
    @override
    def _constraints_tightened_since_last_print(
        self,
        reflowed_text_panel: ReflowedTextDraftPanel[FrameWithWidth],
    ) -> bool:
        if (self._prev_constraints is None
                or self._prev_constraints.max_inline_list_or_dict_width_excl is None):
            return True
        else:
            return (reflowed_text_panel.max_inline_list_or_dict_width_excl
                    < self._prev_constraints.max_inline_list_or_dict_width_excl)

    @override
    def _calc_reduced_frame_width(
        self,
        cropped_panel_dims: DimensionsWithWidth,
    ) -> pyd.NonNegativeInt:
        # Not really used, but just in case
        return cropped_panel_dims.width

    @override
    def _calc_tightened_constraints(
        self,
        reflowed_text_panel: ReflowedTextDraftPanel[FrameWithWidth],
    ) -> Constraints:
        new_max_inline_list_or_dict_width_excl = max(
            reflowed_text_panel.max_inline_list_or_dict_width_excl - 1, 0)

        return dataclasses.replace(
            reflowed_text_panel.constraints,
            max_inline_list_or_dict_width_excl=new_max_inline_list_or_dict_width_excl,
        )

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
