from typing import cast

import rich.pretty
from typing_extensions import override

from omnipy.data._display.dimensions import DimensionsWithWidth
from omnipy.data._display.frame import AnyFrame, FrameWithWidth
from omnipy.data._display.panel.draft.base import DraftPanel
from omnipy.data._display.text.pretty_printer.base import WidthReducingPrettyPrinter
from omnipy.data._display.text.pretty_printer.mixins import PythonStatsTighteningPrettyPrinterMixin
from omnipy.shared.constants import MAX_TERMINAL_SIZE
from omnipy.util import _pydantic as pyd


class RichPrettyPrinter(PythonStatsTighteningPrettyPrinterMixin,
                        WidthReducingPrettyPrinter[object]):
    @override
    @classmethod
    def _calc_reduced_frame_width(
        cls,
        cropped_panel_dims: DimensionsWithWidth,
    ) -> pyd.NonNegativeInt:
        if cropped_panel_dims.height == 1:
            return cropped_panel_dims.width - 2
        else:
            return cropped_panel_dims.width - 1

    # @override
    # @classmethod
    # def _get_default_frame_for_draft_panel(
    #     cls,
    #     draft_panel: DraftPanel[object, AnyFrame],
    # ) -> FrameWithWidth:
    #     return cast(FrameWithWidth, draft_panel.frame)

    # @override
    # @classmethod
    # def _get_default_frame_for_draft_panel(
    #     cls,
    #     draft_panel: DraftPanel[object, AnyFrame],
    # ) -> FrameWithWidth:
    #     if draft_panel.frame.dims.width is not None:
    #         width = draft_panel.frame.dims.width + 1
    #     else:
    #         width = MAX_TERMINAL_SIZE
    @override
    def print_draft_to_str(self, draft_panel: DraftPanel[object, AnyFrame]) -> str:
        if draft_panel.frame.dims.width is not None:
            width = draft_panel.frame.dims.width + 1
        else:
            width = MAX_TERMINAL_SIZE

        return rich.pretty.pretty_repr(
            draft_panel.content,
            indent_size=draft_panel.config.indent,
            max_width=width,
        )
