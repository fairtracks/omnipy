"""Base classes for display pretty printers and iterative tightening logic."""

from abc import ABC, abstractmethod
import dataclasses
import operator
from typing import Callable, ClassVar, Generic

from typing_extensions import override

from omnipy.data._display.config import OutputConfig
from omnipy.data._display.constraints import Constraints
from omnipy.data._display.dimensions import DimensionsWithWidth
from omnipy.data._display.frame import AnyFrame, FrameWithWidth
from omnipy.data._display.panel.draft.base import DraftPanel
from omnipy.data._display.panel.draft.text import ReflowedTextDraftPanel
from omnipy.data._display.panel.typedefs import ContentT, FrameT
from omnipy.shared.enums.display import PrettyPrinterLib, SyntaxLanguageSpec
from omnipy.util.helpers import sorted_dict_hash
import omnipy.util.pydantic as pyd


class PrettyPrinter(ABC, Generic[ContentT]):
    """Base strategy for converting draft panel content into text output.

    Subclasses define how content is selected, normalized, and formatted into a
    ``ReflowedTextDraftPanel`` that can continue through the rendering pipeline.
    """

    @classmethod
    @abstractmethod
    def is_suitable_content(
        cls,
        draft_panel: DraftPanel[object, AnyFrame],
        default: bool = False,
    ) -> bool:
        """Return whether this pretty printer can handle the draft panel.

        Args:
            draft_panel: Draft panel whose content should be evaluated.
            default: Whether suitability is checked as a fallback/default match.

        Returns:
            ``True`` if the printer should be selected for the panel.
        """
        ...

    @classmethod
    @abstractmethod
    def get_pretty_printer_lib(cls) -> PrettyPrinterLib.Literals:
        """Return the config enum value represented by this printer.

        Returns:
            The ``PrettyPrinterLib`` literal used for explicit printer
            selection.
        """
        ...

    @classmethod
    @abstractmethod
    def get_default_syntax_language(cls) -> SyntaxLanguageSpec.Literals:
        """Return the default syntax language used when config is auto.

        Returns:
            The ``SyntaxLanguageSpec`` literal to apply when syntax auto-detect
            resolves to this printer.
        """
        ...

    @classmethod
    @abstractmethod
    def _get_content_for_draft_panel(cls, draft_panel: DraftPanel[object, AnyFrame]) -> ContentT:
        ...

    @classmethod
    def _get_default_constraints_for_draft_panel(
            cls, draft_panel: DraftPanel[object, AnyFrame]) -> Constraints:
        return draft_panel.constraints

    @classmethod
    def _set_default_configs_for_panel_if_auto(cls, config: OutputConfig) -> OutputConfig:
        if config.printer is PrettyPrinterLib.AUTO:
            printer = cls.get_pretty_printer_lib()
        else:
            printer = config.printer

        if config.syntax is SyntaxLanguageSpec.AUTO or config.debug is True:
            syntax = cls.get_default_syntax_language()
        else:
            syntax = config.syntax

        return dataclasses.replace(
            config,
            printer=printer,
            syntax=syntax,
        )

    def prepare_draft_panel(
        self,
        draft_panel: DraftPanel[object, FrameT],
    ) -> DraftPanel[ContentT, FrameT]:
        """Normalize draft content and defaults before formatting.

        Args:
            draft_panel: Input draft panel with arbitrary content type.

        Returns:
            A copy of the draft panel with printer-specific content and default
            constraints/config values applied.
        """
        return draft_panel.create_modified_copy(
            content=self._get_content_for_draft_panel(draft_panel),
            frame=draft_panel.frame,
            constraints=self._get_default_constraints_for_draft_panel(draft_panel),
            config=self._set_default_configs_for_panel_if_auto(draft_panel.config),
        )

    @abstractmethod
    def format_prepared_draft(
        self,
        draft_panel: DraftPanel[ContentT, FrameT],
    ) -> ReflowedTextDraftPanel[FrameT]:
        """Format already-normalized panel content into reflowed text.

        Args:
            draft_panel: Draft panel prepared by :meth:`prepare_draft_panel`.

        Returns:
            Reflowed text panel ready for styling/rendering.
        """
        ...

    @classmethod
    def get_pretty_printer_for_draft_panel(
        cls,
        draft_panel: DraftPanel,
    ) -> 'PrettyPrinter':
        """Resolve the most appropriate pretty printer for a draft panel.

        Resolution order is explicit config, debug override, content-based
        matching, syntax-based matching, and finally default content fallback.

        Args:
            draft_panel: Draft panel for which a printer should be selected.

        Returns:
            A pretty printer instance capable of formatting the panel.
        """
        import omnipy.data._display.text.pretty_printer.register as register

        pretty_printer = register.get_pretty_printer_from_config_value(draft_panel.config.printer)
        if pretty_printer:
            return pretty_printer

        pretty_printer = register.get_debug_pretty_printer_if_debug_mode(draft_panel.config.debug)
        if pretty_printer:
            return pretty_printer

        pretty_printer = register.get_pretty_printer_from_content(draft_panel, default=False)
        if pretty_printer:
            return pretty_printer

        pretty_printer = register.get_pretty_printer_from_syntax(draft_panel.config.syntax)
        if pretty_printer:
            return pretty_printer

        return register.get_pretty_printer_from_content(draft_panel, default=True)


class StatsTighteningPrettyPrinter(
        PrettyPrinter[ContentT],
        ABC,
        Generic[ContentT],
):
    """Pretty printer that can iteratively tighten formatting constraints.

    This base class tracks prior statistics across iterations so subclasses can
    detect whether successive formatting attempts moved in the expected
    direction.
    """

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

    @abstractmethod
    def prepare_draft_for_print_with_tightened_stat_reqs(
        self,
        draft_panel: DraftPanel[ContentT, FrameT],
        cur_reflowed_text_panel: ReflowedTextDraftPanel[FrameWithWidth],
    ) -> DraftPanel[ContentT, FrameT | FrameWithWidth]:
        """Return a modified draft with stricter requirements for next print.

        Args:
            draft_panel: The draft that was previously formatted.
            cur_reflowed_text_panel: Result from the most recent formatting
                attempt.

        Returns:
            A modified draft panel for the next formatting iteration.
        """
        ...

    def stats_tightened_since_last_print(
        self,
        draft_for_print: DraftPanel[ContentT, FrameT],
        cur_reflowed_text_panel: ReflowedTextDraftPanel[FrameWithWidth],
    ) -> bool:
        """Return whether tracked requirements tightened since last iteration.

        Args:
            draft_for_print: Draft panel being evaluated for the next attempt.
            cur_reflowed_text_panel: Result from the current formatting pass.

        Returns:
            ``True`` when one or more tracked values tightened.
        """
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
        compare_operator: Callable[[int, int], bool],
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

    def format_prepared_draft(
        self,
        draft_panel: DraftPanel[ContentT, FrameT],
    ) -> ReflowedTextDraftPanel[FrameT]:
        """Format by converting the draft to a string and reflowing it.

        Args:
            draft_panel: Prepared draft panel to format.

        Returns:
            Reflowed text draft panel wrapping the printed string.
        """
        return ReflowedTextDraftPanel.create_from_draft_panel(
            draft_panel,
            other_content=self.print_draft_to_str(draft_panel),
        )

    @abstractmethod
    def print_draft_to_str(self, draft_panel: DraftPanel[ContentT, AnyFrame]) -> str:
        """Render the draft content into a plain string representation.

        Args:
            draft_panel: Draft panel whose content should be stringified.

        Returns:
            Text representation used as input for reflow and styling.
        """
        pass


class WidthReducingPrettyPrinter(StatsTighteningPrettyPrinter[ContentT], Generic[ContentT]):
    """Pretty printer that retries formatting with progressively smaller widths.

    Each iteration lowers frame width and checks whether both required and
    observed width statistics tightened.
    """

    def _init_prev_frame_width(
        self,
        cur_reflowed_text_panel: ReflowedTextDraftPanel[FrameWithWidth],
    ) -> None:
        # For initial iteration, compare with frame of
        # cur_reflowed_text_panel provided as input
        if 'frame_width' not in self._prev_stat_requirements:
            self._prev_stat_requirements['frame_width'] = cur_reflowed_text_panel.frame.dims.width

    @override
    def prepare_draft_for_print_with_tightened_stat_reqs(
        self,
        draft_panel: DraftPanel[ContentT, FrameT],
        cur_reflowed_text_panel: ReflowedTextDraftPanel[FrameWithWidth],
    ) -> DraftPanel[ContentT, FrameT | FrameWithWidth]:
        """Return a copy of the draft panel with reduced frame width.

        Args:
            draft_panel: Draft panel to prepare for the next print attempt.
            cur_reflowed_text_panel: Current reflowed panel used to derive the
                next width.

        Returns:
            Draft panel copy with a narrowed frame.
        """
        self._init_prev_frame_width(cur_reflowed_text_panel)
        new_frame = self._calc_frame_with_reduced_width(cur_reflowed_text_panel)
        return draft_panel.create_modified_copy(
            draft_panel.content,
            frame=new_frame,
            constraints=draft_panel.constraints,
        )

    def _calc_frame_with_reduced_width(
        self,
        cur_reflowed_text_panel: ReflowedTextDraftPanel[FrameWithWidth],
    ) -> FrameWithWidth:

        new_frame_width = max(0, self._calc_reduced_frame_width(cur_reflowed_text_panel.orig_dims))
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
        draft_for_print: DraftPanel[ContentT, FrameT],
        cur_reflowed_text_panel: ReflowedTextDraftPanel[FrameWithWidth],
    ) -> bool:
        """Return whether width-related statistics tightened this iteration.

        Args:
            draft_for_print: Draft panel for the current print attempt.
            cur_reflowed_text_panel: Most recent reflowed output panel.

        Returns:
            ``True`` if frame width requirements and measured widths tightened.
        """
        return super().stats_tightened_since_last_print(
            draft_for_print,
            cur_reflowed_text_panel,
        ) or self._stat_req_and_calc_tightened_since_last_print_common(
            'frame_width',
            draft_for_print.frame.dims.width,
            cur_reflowed_text_panel.orig_dims.width,
            operator.lt)


class ConstraintTighteningPrettyPrinter(
        StatsTighteningPrettyPrinter[ContentT],
        ABC,
        Generic[ContentT],
):
    """Pretty printer that retries formatting with stricter constraints.

    Subclasses declare which constraint statistic to tighten and how to compare
    tightened values between iterations.
    """

    # Must be defined in subclasses
    CONSTRAINT_STAT_NAME: ClassVar[str]
    CONSTRAINT_TIGHTEN_FUNC: Callable[[int], int]
    CONSTRAINT_TIGHTENED_OPERATOR: Callable[[int, int], bool]

    @override
    def prepare_draft_for_print_with_tightened_stat_reqs(
        self,
        draft_panel: DraftPanel[ContentT, FrameT],
        cur_reflowed_text_panel: ReflowedTextDraftPanel[FrameWithWidth],
    ) -> DraftPanel[ContentT, FrameT | FrameWithWidth]:
        """Return a draft copy with tightened constraint values.

        Args:
            draft_panel: Draft panel to update for another print attempt.
            cur_reflowed_text_panel: Current output panel used to compute the
                tightened constraint.

        Returns:
            Draft panel copy containing updated constraints.
        """

        new_constraints = self._calc_tightened_constraint(draft_panel, cur_reflowed_text_panel)

        return draft_panel.create_modified_copy(
            draft_panel.content,
            constraints=new_constraints,
        )

    # Override in subclasses if needed
    @classmethod
    def _calc_tightened_constraint(
        cls,
        draft_panel: DraftPanel[object, FrameT],
        reflowed_text_panel: ReflowedTextDraftPanel[AnyFrame],
    ) -> Constraints:
        prev_constraint_stat_val = getattr(reflowed_text_panel, cls.CONSTRAINT_STAT_NAME)
        new_constraint_val = cls.CONSTRAINT_TIGHTEN_FUNC(prev_constraint_stat_val)

        prev_constraint_val = getattr(reflowed_text_panel.constraints, cls.CONSTRAINT_STAT_NAME)
        assert prev_constraint_val is not None

        if cls.CONSTRAINT_TIGHTENED_OPERATOR(new_constraint_val, prev_constraint_val):
            # Always tighten constraints, never relax
            return dataclasses.replace(
                reflowed_text_panel.constraints,
                **{cls.CONSTRAINT_STAT_NAME: new_constraint_val},
            )
        else:
            return reflowed_text_panel.constraints

    @override
    def stats_tightened_since_last_print(
        self,
        draft_for_print: DraftPanel[ContentT, FrameT],
        cur_reflowed_text_panel: ReflowedTextDraftPanel[FrameWithWidth],
    ) -> bool:
        """Return whether the configured constraint statistic tightened.

        Args:
            draft_for_print: Draft panel for the current print attempt.
            cur_reflowed_text_panel: Most recent reflowed output panel.

        Returns:
            ``True`` when both requested and calculated constraint stats moved
            in the tightening direction.
        """
        return super().stats_tightened_since_last_print(
            draft_for_print,
            cur_reflowed_text_panel,
        ) or self._stat_req_and_calc_tightened_since_last_print_common(
            self.CONSTRAINT_STAT_NAME,
            getattr(draft_for_print.constraints, self.CONSTRAINT_STAT_NAME),
            getattr(cur_reflowed_text_panel, self.CONSTRAINT_STAT_NAME),
            self.CONSTRAINT_TIGHTENED_OPERATOR,
        )
