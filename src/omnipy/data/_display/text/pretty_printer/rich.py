import rich.pretty
from typing_extensions import override

from omnipy.data._display.dimensions import DimensionsWithWidth
from omnipy.data._display.panel.draft.base import DraftPanel
from omnipy.data._display.panel.typedefs import FrameT
from omnipy.data._display.text.pretty_printer.base import WidthReducingPrettyPrinter
from omnipy.shared.constants import MAX_TERMINAL_SIZE
from omnipy.util import _pydantic as pyd


class RichPrettyPrinter(WidthReducingPrettyPrinter):
    @override
    def _calc_reduced_frame_width(
        self,
        cropped_panel_dims: DimensionsWithWidth,
    ) -> pyd.NonNegativeInt:
        if cropped_panel_dims.height == 1:
            return cropped_panel_dims.width - 2
        else:
            return cropped_panel_dims.width - 1

    @override
    def print_draft_to_str(self, draft_panel: DraftPanel[object, FrameT]) -> str:
        if draft_panel.frame.dims.width is not None:
            max_width = draft_panel.frame.dims.width + 1
        else:
            max_width = MAX_TERMINAL_SIZE

        return rich.pretty.pretty_repr(
            draft_panel.content,
            indent_size=draft_panel.config.indent_tab_size,
            max_width=max_width,
        )
