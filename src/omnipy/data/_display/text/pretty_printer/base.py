from abc import ABC, abstractmethod
import dataclasses
import operator
from typing import Callable, ClassVar, Generic

from typing_extensions import override

from omnipy.data._display.constraints import Constraints
from omnipy.data._display.dimensions import DimensionsWithWidth
from omnipy.data._display.frame import AnyFrame
from omnipy.data._display.panel.draft.base import DraftPanel
from omnipy.data._display.panel.draft.text import ReflowedTextDraftPanel
from omnipy.data._display.panel.typedefs import ContentT, FrameT
from omnipy.util import _pydantic as pyd
from omnipy.util.helpers import sorted_dict_hash


class PrettyPrinter(ABC, Generic[ContentT]):
    @abstractmethod
    def is_suitable_content(self, draft_panel: DraftPanel[ContentT, FrameT]) -> bool:
        ...

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
        import omnipy.data._display.text.pretty_printer.register as register

        pretty_printer = register.get_pretty_printer_from_config_value(draft_panel.config.printer)
        if pretty_printer:
            return pretty_printer

        pretty_printer = register.get_pretty_printer_from_content(draft_panel)
        if pretty_printer:
            return pretty_printer

        return register.get_pretty_printer_from_syntax(draft_panel.config.syntax)


class StatsTighteningPrettyPrinter(
        PrettyPrinter[ContentT],
        ABC,
        Generic[ContentT],
):
    def __init__(self) -> None:
        super().__init__()
        self._prev_stat_requirements: dict[str, pyd.NonNegativeInt | None] = {}
        self._prev_calculated_stats: dict[str, pyd.NonNegativeInt | None] = {}

    def __hash__(self) -> int:
        return hash((
            self.__class__,
            sorted_dict_hash(self._prev_stat_requirements),
            sorted_dict_hash(self._prev_calculated_stats),
        ))

    def prepare_draft_for_print_with_tightened_stat_requirements(
        self,
        draft_panel: DraftPanel[ContentT, FrameT],
        cur_reflowed_text_panel: ReflowedTextDraftPanel[AnyFrame],
    ) -> DraftPanel[ContentT, AnyFrame]:
        return DraftPanel(
            draft_panel.content,
            title=draft_panel.title,
            frame=draft_panel.frame,
            constraints=draft_panel.constraints,
            config=draft_panel.config,
        )

    def stats_tightened_since_last_print(
        self,
        draft_for_print: DraftPanel[ContentT, AnyFrame],
        cur_reflowed_text_panel: ReflowedTextDraftPanel[AnyFrame],
    ) -> bool:
        return False

    @staticmethod
    def _stat_tightened_since_last_print_common(
        prev_vals_dict: dict[str, pyd.NonNegativeInt | None],
        stat_name: str,
        cur_stat_val: pyd.NonNegativeInt | None,
        compare_operator: Callable[[int, int], bool],
    ) -> bool:
        if cur_stat_val is None:
            stat_tightened = False
        else:
            prev_stat_val = prev_vals_dict.get(stat_name)
            if prev_stat_val is None:
                stat_tightened = True
            else:
                stat_tightened = compare_operator(
                    cur_stat_val,
                    prev_stat_val,
                )

        prev_vals_dict[stat_name] = cur_stat_val

        return stat_tightened

    def _stat_req_and_calc_tightened_since_last_print_common(
        self,
        stat_name: str,
        cur_stat_requirement: pyd.NonNegativeInt | None,
        cur_calculated_stat: pyd.NonNegativeInt | None,
        compare_operator: Callable[[int, int], bool] = operator.lt,
    ) -> bool:
        stat_requirement_tightened = self._stat_tightened_since_last_print_common(
            self._prev_stat_requirements,
            stat_name,
            cur_stat_requirement,
            compare_operator,
        )
        calculated_stat_tightened = self._stat_tightened_since_last_print_common(
            self._prev_calculated_stats,
            stat_name,
            cur_calculated_stat,
            compare_operator,
        )
        return stat_requirement_tightened and calculated_stat_tightened

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


class WidthReducingPrettyPrinter(StatsTighteningPrettyPrinter[ContentT], Generic[ContentT]):
    @override
    def prepare_draft_for_print_with_tightened_stat_requirements(
        self,
        draft_panel: DraftPanel[ContentT, FrameT],
        cur_reflowed_text_panel: ReflowedTextDraftPanel[AnyFrame],
    ) -> DraftPanel[ContentT, AnyFrame]:
        # For initial iteration, compare with frame of
        # cur_reflowed_text_panel provided as input
        if 'frame_width' not in self._prev_stat_requirements:
            self._prev_stat_requirements['frame_width'] = cur_reflowed_text_panel.frame.dims.width

        new_frame = self._calc_frame_with_reduced_width(cur_reflowed_text_panel)

        return DraftPanel(
            draft_panel.content,
            title=draft_panel.title,
            frame=new_frame,
            constraints=draft_panel.constraints,
            config=draft_panel.config,
        )

    def _calc_frame_with_reduced_width(
        self,
        cur_reflowed_text_panel: ReflowedTextDraftPanel[AnyFrame],
    ) -> AnyFrame:
        new_frame_width = self._calc_reduced_frame_width(cur_reflowed_text_panel.orig_dims)
        return cur_reflowed_text_panel.frame.modified_copy(width=new_frame_width)

    @classmethod
    @abstractmethod
    def _calc_reduced_frame_width(
        cls,
        cropped_panel_dims: DimensionsWithWidth,
    ) -> pyd.NonNegativeInt:
        pass

    def stats_tightened_since_last_print(
        self,
        draft_for_print: DraftPanel[ContentT, AnyFrame],
        cur_reflowed_text_panel: ReflowedTextDraftPanel[AnyFrame],
    ) -> bool:
        return super().stats_tightened_since_last_print(
            draft_for_print,
            cur_reflowed_text_panel,
        ) or self._stat_req_and_calc_tightened_since_last_print_common(
            'frame_width',
            draft_for_print.frame.dims.width,
            cur_reflowed_text_panel.orig_dims.width,
        )


class ConstraintTighteningPrettyPrinterMixin(
        StatsTighteningPrettyPrinter[ContentT],
        ABC,
        Generic[ContentT],
):
    # Must be defined in subclasses
    CONSTRAINT_STAT_NAME: ClassVar[str]

    @override
    def prepare_draft_for_print_with_tightened_stat_requirements(
        self,
        draft_panel: DraftPanel[ContentT, FrameT],
        cur_reflowed_text_panel: ReflowedTextDraftPanel[AnyFrame],
    ) -> DraftPanel[ContentT, AnyFrame]:
        draft_for_print = super().prepare_draft_for_print_with_tightened_stat_requirements(
            draft_panel,
            cur_reflowed_text_panel,
        )

        new_constraints = self._calc_tightened_constraint(cur_reflowed_text_panel)
        return dataclasses.replace(draft_for_print, constraints=new_constraints)

    # Override in subclasses if needed
    @classmethod
    def _calc_tightened_constraint(
        cls,
        reflowed_text_panel: ReflowedTextDraftPanel[AnyFrame],
    ) -> Constraints:
        new_constraint_stat_val = max(getattr(reflowed_text_panel, cls.CONSTRAINT_STAT_NAME) - 1, 0)

        return dataclasses.replace(
            reflowed_text_panel.constraints,
            **{cls.CONSTRAINT_STAT_NAME: new_constraint_stat_val},
        )

    @override
    def stats_tightened_since_last_print(
        self,
        draft_for_print: DraftPanel[ContentT, AnyFrame],
        cur_reflowed_text_panel: ReflowedTextDraftPanel[AnyFrame],
    ) -> bool:
        return super().stats_tightened_since_last_print(
            draft_for_print,
            cur_reflowed_text_panel,
        ) or self._stat_req_and_calc_tightened_since_last_print_common(
            self.CONSTRAINT_STAT_NAME,
            getattr(draft_for_print.constraints, self.CONSTRAINT_STAT_NAME),
            getattr(cur_reflowed_text_panel, self.CONSTRAINT_STAT_NAME),
        )
