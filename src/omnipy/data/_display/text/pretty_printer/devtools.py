import dataclasses
import re

from typing_extensions import override

from omnipy.data._display.constraints import Constraints
from omnipy.data._display.dimensions import DimensionsWithWidth
from omnipy.data._display.frame import FrameWithWidth
from omnipy.data._display.panel.draft.base import DraftPanel
from omnipy.data._display.panel.draft.text import ReflowedTextDraftPanel
from omnipy.data._display.panel.typedefs import FrameT
from omnipy.data._display.text.pretty_printer.base import WidthReducingPrettyPrinter
from omnipy.data._display.text.pretty_printer.mixins import PythonWidthReducingPrettyPrinterMixin
from omnipy.shared.constants import MAX_TERMINAL_SIZE
from omnipy.util import _pydantic as pyd


class DevtoolsPrettyPrinter(PythonWidthReducingPrettyPrinterMixin,
                            WidthReducingPrettyPrinter[object]):
    @override
    def _constraints_tightened_since_last_print(
        self,
        reflowed_text_panel: ReflowedTextDraftPanel[FrameWithWidth],
    ) -> bool:
        if (self._prev_constraints is None
                or self._prev_constraints.max_inline_container_width_incl is None):
            return True
        else:
            return (reflowed_text_panel.max_inline_container_width_incl
                    < self._prev_constraints.max_inline_container_width_incl)

    @override
    def _calc_reduced_frame_width(
        self,
        cropped_panel_dims: DimensionsWithWidth,
    ) -> pyd.NonNegativeInt:
        return cropped_panel_dims.width - 1

    @override
    def _calc_tightened_constraints(
        self,
        reflowed_text_panel: ReflowedTextDraftPanel[FrameWithWidth],
    ) -> Constraints:
        new_max_inline_container_width_incl = max(
            reflowed_text_panel.max_inline_container_width_incl - 1, 0)

        return dataclasses.replace(
            reflowed_text_panel.constraints,
            max_inline_container_width_incl=new_max_inline_container_width_incl,
        )

    @override
    def print_draft_to_str(self, draft_panel: DraftPanel[object, FrameT]) -> str:
        from devtools import PrettyFormat

        if draft_panel.constraints.max_inline_container_width_incl is not None:
            simple_cutoff = draft_panel.constraints.max_inline_container_width_incl
        else:
            simple_cutoff = MAX_TERMINAL_SIZE

        if draft_panel.frame.dims.width is not None:
            width = draft_panel.frame.dims.width + 1
        else:
            width = MAX_TERMINAL_SIZE

        while True:
            pf = PrettyFormat(
                indent_step=draft_panel.config.indent_tab_size,
                simple_cutoff=simple_cutoff,
                width=width,
            )

            try:
                return pf(draft_panel.content)
            except ValueError as e:
                text_match = re.search(r'invalid width (-?\d+)', str(e))

                if text_match:
                    internal_width = int(text_match.group(1))
                    delta_width = -internal_width + 1
                    simple_cutoff += delta_width
                    width += delta_width
                    continue

                if re.search(r'range\(\) arg 3 must not be zero', str(e)):
                    simple_cutoff += 1
                    width += 1
                    continue
                raise
