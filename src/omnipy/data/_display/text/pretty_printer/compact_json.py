import operator
from typing import Callable, ClassVar

import compact_json.formatter
from typing_extensions import override

from omnipy.data._display.constraints import Constraints
from omnipy.data._display.frame import AnyFrame
from omnipy.data._display.panel.draft.base import DraftPanel
from omnipy.data._display.text.pretty_printer.base import ConstraintTighteningPrettyPrinter
from omnipy.data._display.text.pretty_printer.mixins import JsonStatsTighteningPrettyPrinterMixin
from omnipy.shared.constants import TERMINAL_DEFAULT_WIDTH


class CompactJsonPrettyPrinter(
        JsonStatsTighteningPrettyPrinterMixin,
        ConstraintTighteningPrettyPrinter[object],
):
    CONSTRAINT_STAT_NAME: ClassVar[str] = 'max_inline_list_or_dict_width_excl'
    CONSTRAINT_TIGHTEN_FUNC: Callable[[int], int] = lambda x: max(x - 1, 0)
    CONSTRAINT_TIGHTENED_OPERATOR: Callable[[int, int], bool] = operator.lt

    @override
    @classmethod
    def _get_default_constraints_for_draft_panel(
            cls, draft_panel: DraftPanel[object, AnyFrame]) -> Constraints:
        return Constraints(
            max_inline_list_or_dict_width_excl=(
                draft_panel.frame.dims.width or TERMINAL_DEFAULT_WIDTH))

    @override
    def print_draft_to_str(self, draft_panel: DraftPanel[object, AnyFrame]) -> str:
        max_inline_length = draft_panel.constraints.max_inline_list_or_dict_width_excl
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
