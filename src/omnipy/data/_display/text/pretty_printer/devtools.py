import operator
import re
from typing import Callable, ClassVar

from typing_extensions import override

from omnipy.data._display import constraints
from omnipy.data._display.constraints import Constraints
from omnipy.data._display.dimensions import DimensionsWithWidth
from omnipy.data._display.frame import AnyFrame, FrameWithWidth
from omnipy.data._display.panel.draft.base import DraftPanel
from omnipy.data._display.panel.draft.text import ReflowedTextDraftPanel
from omnipy.data._display.panel.typedefs import FrameT
from omnipy.data._display.text.pretty_printer.base import (ConstraintTighteningPrettyPrinterMixin,
                                                           WidthReducingPrettyPrinter)
from omnipy.data._display.text.pretty_printer.mixins import PythonStatsTighteningPrettyPrinterMixin
from omnipy.shared.constants import MAX_TERMINAL_SIZE
from omnipy.util import _pydantic as pyd


class DevtoolsPrettyPrinter(
        PythonStatsTighteningPrettyPrinterMixin,
        ConstraintTighteningPrettyPrinterMixin[object],
        WidthReducingPrettyPrinter[object],
):
    CONSTRAINT_STAT_NAME: ClassVar[str] = 'max_inline_container_width_incl'
    CONSTRAINT_TIGHTEN_FUNC: Callable[[int], int] = lambda x: max(x - 1, 0)
    CONSTRAINT_TIGHTENED_OPERATOR: Callable[[int, int], bool] = operator.lt

    @override
    @classmethod
    def _calc_reduced_frame_width(
        cls,
        cropped_panel_dims: DimensionsWithWidth,
    ) -> pyd.NonNegativeInt:
        return cropped_panel_dims.width - 1

    @override
    @classmethod
    def _get_default_constraints_for_draft_panel(
            cls, draft_panel: DraftPanel[object, AnyFrame]) -> Constraints:
        return Constraints(
            max_inline_container_width_incl=(draft_panel.frame.dims.width or MAX_TERMINAL_SIZE))

    @override
    def prepare_draft_for_print_with_tightened_stat_requirements(
        self,
        draft_panel: DraftPanel[object, FrameT],
        cur_reflowed_text_panel: ReflowedTextDraftPanel[FrameWithWidth],
    ) -> DraftPanel[object, FrameT | FrameWithWidth]:
        self._init_prev_frame_width(cur_reflowed_text_panel)

        constraints_val = draft_panel.constraints.max_inline_container_width_incl
        assert constraints_val is not None

        prev_frame_width = self._prev_stat_requirements['frame_width']
        assert prev_frame_width is not None

        # if constraints_val > prev_frame_width:
        #     return ConstraintTighteningPrettyPrinterMixin.prepare_draft_for_print_with_tightened_stat_requirements(
        #         self, draft_panel, cur_reflowed_text_panel)
        # else:
        #     return WidthReducingPrettyPrinter.prepare_draft_for_print_with_tightened_stat_requirements(
        #         self, draft_panel, cur_reflowed_text_panel)

        # if constraints_val > prev_frame_width:
        draft_panel_for_print = ConstraintTighteningPrettyPrinterMixin.prepare_draft_for_print_with_tightened_stat_requirements(
            self, draft_panel, cur_reflowed_text_panel)
        # else:
        #     draft_panel_for_print = draft_panel
        return WidthReducingPrettyPrinter.prepare_draft_for_print_with_tightened_stat_requirements(
            self, draft_panel_for_print, cur_reflowed_text_panel)

        new_constraints = self._calc_tightened_constraint(draft_panel, cur_reflowed_text_panel)

        return draft_panel.create_modified_copy(draft_panel.content, constraints=new_constraints)

    @override
    def print_draft_to_str(self, draft_panel: DraftPanel[object, AnyFrame]) -> str:
        from devtools import PrettyFormat

        simple_cutoff = draft_panel.constraints.max_inline_container_width_incl
        assert simple_cutoff is not None

        if draft_panel.frame.dims.width is not None:
            width = draft_panel.frame.dims.width + 1
            # width = draft_panel.frame.dims.width
        else:
            width = MAX_TERMINAL_SIZE

        while True:
            pf = PrettyFormat(
                indent_step=draft_panel.config.indent,
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
