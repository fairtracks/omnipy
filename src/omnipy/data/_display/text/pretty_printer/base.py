from abc import ABC, abstractmethod
from typing import cast, Generic

from omnipy.data._display.constraints import Constraints
from omnipy.data._display.dimensions import DimensionsWithWidth
from omnipy.data._display.frame import FrameWithWidth
from omnipy.data._display.panel.draft.base import DraftPanel
from omnipy.data._display.panel.draft.text import ReflowedTextDraftPanel
from omnipy.data._display.panel.typedefs import ContentT, FrameT
from omnipy.shared.enums.display import PrettyPrinterLib, SyntaxLanguage
from omnipy.util import _pydantic as pyd


class PrettyPrinter(ABC, Generic[ContentT]):
    @abstractmethod
    def format_draft(
        self,
        draft_panel: DraftPanel[ContentT, FrameT],
    ) -> ReflowedTextDraftPanel[FrameT]:
        ...

    @abstractmethod
    def prepare_draft_panel(
            self, draft_panel: DraftPanel[ContentT, FrameT]) -> DraftPanel[object, FrameT]:
        ...

    @classmethod
    def get_pretty_printer_for_draft_panel(cls, draft_panel: DraftPanel) -> 'PrettyPrinter':
        from omnipy.data._display.text.pretty_printer.compact_json import CompactJsonPrettyPrinter
        from omnipy.data._display.text.pretty_printer.devtools import DevtoolsPrettyPrinter
        from omnipy.data._display.text.pretty_printer.plain_text import PlainTextPrettyPrinter
        from omnipy.data._display.text.pretty_printer.rich import RichPrettyPrinter

        match draft_panel.config.language:
            case SyntaxLanguage.JSON:
                return CompactJsonPrettyPrinter()
            case SyntaxLanguage.PYTHON:
                match draft_panel.config.pretty_printer:
                    case PrettyPrinterLib.RICH:
                        return RichPrettyPrinter()
                    case PrettyPrinterLib.DEVTOOLS:
                        return DevtoolsPrettyPrinter()
            case _:
                return PlainTextPrettyPrinter()


class WidthReducingPrettyPrinter(PrettyPrinter[ContentT], Generic[ContentT]):
    def __init__(self) -> None:
        self._prev_frame_width: pyd.NonNegativeInt | None = None
        self._prev_constraints: Constraints | None = None
        self._prev_reflowed_text_panel_width: pyd.NonNegativeInt | None = None

    def __hash__(self) -> int:
        _hash = hash((self.__class__,
                      self._prev_frame_width,
                      self._prev_constraints,
                      self._prev_reflowed_text_panel_width))
        return _hash

    def width_reduced_since_last_print(
        self,
        draft_for_print: DraftPanel[ContentT, FrameWithWidth],
        reflowed_text_panel: ReflowedTextDraftPanel[FrameWithWidth],
    ) -> bool:

        if self._prev_frame_width is None:
            frame_width_reduced = True
        else:
            frame_width_reduced = (draft_for_print.frame.dims.width < self._prev_frame_width)

        if self._prev_reflowed_text_panel_width is None:
            dims_width_reduced = True
        else:
            dims_width_reduced = (
                reflowed_text_panel.orig_dims.width < self._prev_reflowed_text_panel_width)

        self._prev_frame_width = draft_for_print.frame.dims.width
        self._prev_reflowed_text_panel_width = reflowed_text_panel.orig_dims.width

        return frame_width_reduced and dims_width_reduced

    def constraints_tightened_since_last_print(
        self,
        draft_for_print: DraftPanel[ContentT, FrameWithWidth],
        reflowed_text_panel: ReflowedTextDraftPanel[FrameWithWidth],
    ) -> bool:
        reduced_constraints = self._constraints_tightened_since_last_print(reflowed_text_panel)

        self._prev_constraints = draft_for_print.constraints

        return reduced_constraints

    def _constraints_tightened_since_last_print(
        self,
        reflowed_text_panel: ReflowedTextDraftPanel[FrameWithWidth],
    ) -> bool:
        return False

    def prepare_draft_for_print_with_reduced_width_requirements(
        self,
        draft_panel: DraftPanel[ContentT, FrameT],
        reflowed_text_panel: ReflowedTextDraftPanel[FrameWithWidth],
    ) -> DraftPanel[ContentT, FrameWithWidth]:
        # For initial iteration, compare with frame of
        # cur_reflowed_text_panel provided as input
        if self._prev_frame_width is None:
            self._prev_frame_width = reflowed_text_panel.frame.dims.width

        new_frame = self._calc_frame_with_reduced_width(reflowed_text_panel)
        new_constraints = self._calc_tightened_constraints(reflowed_text_panel)
        return DraftPanel(
            draft_panel.content,
            title=draft_panel.title,
            frame=new_frame,
            constraints=new_constraints,
            config=draft_panel.config,
        )

    def _calc_frame_with_reduced_width(
        self,
        reflowed_text_panel: ReflowedTextDraftPanel[FrameWithWidth],
    ) -> FrameWithWidth:
        new_frame_width = self._calc_reduced_frame_width(reflowed_text_panel.orig_dims)
        return cast(FrameWithWidth, reflowed_text_panel.frame.modified_copy(width=new_frame_width))

    @abstractmethod
    def _calc_reduced_frame_width(
        self,
        cropped_panel_dims: DimensionsWithWidth,
    ) -> pyd.NonNegativeInt:
        pass

    def _calc_tightened_constraints(
        self,
        reflowed_text_panel: ReflowedTextDraftPanel[FrameWithWidth],
    ) -> Constraints:
        return reflowed_text_panel.constraints

    def format_draft(
        self,
        draft_panel: DraftPanel[ContentT, FrameT],
    ) -> ReflowedTextDraftPanel[FrameT]:
        return ReflowedTextDraftPanel.create_from_draft_panel(
            draft_panel,
            other_content=self.print_draft_to_str(draft_panel),
        )

    @abstractmethod
    def print_draft_to_str(self, draft_panel: DraftPanel[ContentT, FrameT]) -> str:
        pass
