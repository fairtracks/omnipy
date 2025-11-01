from dataclasses import dataclass
from functools import cached_property
from typing import cast, Generic, NamedTuple

from omnipy.data._display.dimensions import Dimensions, DimensionsWithWidthAndHeight, has_width
from omnipy.data._display.frame import AnyFrame, Frame
from omnipy.data._display.layout.base import Layout
from omnipy.data._display.panel.base import panel_is_dimensions_aware
from omnipy.data._display.panel.draft.base import (DimensionsAwareDraftPanel,
                                                   DimensionsAwareDraftPanelLayout,
                                                   DraftPanel)
from omnipy.data._display.panel.draft.layout import ResizedLayoutDraftPanel
from omnipy.data._display.panel.typedefs import ContentT, FrameInvT, FrameT
from omnipy.util import _pydantic as pyd
from omnipy.util.helpers import first_key_in_mapping

# Functions


def create_panel_with_updated_frame(
    draft_panel_basis: DraftPanel[ContentT, AnyFrame],
    frame: FrameInvT,
) -> DimensionsAwareDraftPanel[ContentT, FrameInvT]:
    """
    Create a new dimensions-aware panel based on an existing panel with a new frame.

    This function creates a copy of the draft panel with a new frame and
    ensures the returned panel is dimensions-aware. If the original panel is
    not dimensions-aware, it renders the next stage to get a
    dimensions-aware panel.

    Parameters:
        draft_panel_basis: Original draft panel to base the new panel on
        frame: New frame to apply to the panel

    Returns:
        Dimensions-aware draft panel with the updated frame
    """
    new_draft_panel = cast(
        DraftPanel[ContentT, FrameInvT],
        draft_panel_basis.__class__(
            content=draft_panel_basis.content,
            title=draft_panel_basis.title,
            frame=frame,
            constraints=draft_panel_basis.constraints,
            config=draft_panel_basis.config,
        ),
    )
    if not panel_is_dimensions_aware(new_draft_panel):
        return cast(DimensionsAwareDraftPanel[ContentT, FrameInvT],
                    new_draft_panel.render_next_stage())
    else:
        return cast(DimensionsAwareDraftPanel[ContentT, FrameInvT], new_draft_panel)


# Classes


@dataclass(init=False)
class LayoutFlowContext(Generic[FrameT]):
    """
    Context object for the layout optimization process.

    This class maintains the state of the layout during resizing operations,
    provides properties for checking layout width status, and handles tracking
    which panels are resizable.

    Attributes:
        input_layout_panel: Original draft panel containing the layout
        draft_layout: Layout with initial width distribution
        dim_aware_layout: Dimensions-aware version of the layout
        keys_of_resizable_panels: Set of panel keys that can be resized
    """
    input_layout_panel: DraftPanel[Layout[DraftPanel], FrameT]
    draft_layout: Layout[DraftPanel]
    dim_aware_layout: DimensionsAwareDraftPanelLayout
    keys_of_resizable_panels: set[str]
    keys_of_removed_panels: set[str]

    def __init__(
        self,
        input_layout_panel: DraftPanel[Layout[DraftPanel], FrameT],
        draft_layout: Layout[DraftPanel],
        dim_aware_layout: DimensionsAwareDraftPanelLayout | pyd.UndefinedType = pyd.Undefined,
        keys_of_resizable_panels: set[str] | pyd.UndefinedType = pyd.Undefined,
        keys_of_removed_panels: set[str] | pyd.UndefinedType = pyd.Undefined,
    ) -> None:
        self.input_layout_panel = input_layout_panel
        self.draft_layout = draft_layout
        self._init_dim_aware_layout(dim_aware_layout)
        self._init_keys_of_resizable_panels(keys_of_resizable_panels)
        self._init_keys_of_removed_panels(keys_of_removed_panels)

    def _init_dim_aware_layout(
            self, dim_aware_layout: DimensionsAwareDraftPanelLayout | pyd.UndefinedType) -> None:
        if isinstance(dim_aware_layout, pyd.UndefinedType):
            # Create a dimensions-aware layout from the draft layout
            initial_resized_panel = ResizedLayoutDraftPanel.create_from_draft_panel(
                self.input_layout_panel,
                self.draft_layout,
            )
            self.dim_aware_layout = initial_resized_panel.content
        else:
            self.dim_aware_layout = dim_aware_layout

    def _init_keys_of_resizable_panels(
        self,
        keys_of_resizable_panels: set[str] | pyd.UndefinedType,
    ) -> None:
        def _panel_is_resizable(panel: DraftPanel) -> bool:
            """Check if panel is eligible for resizing."""
            return not (draft_panel.frame.fixed_width or panel_is_dimensions_aware(draft_panel))

        if isinstance(keys_of_resizable_panels, pyd.UndefinedType):
            self.keys_of_resizable_panels = set()
            # Identify panels that could be resizable.
            for key, draft_panel in self.draft_layout.items():
                if _panel_is_resizable(draft_panel):
                    self.keys_of_resizable_panels.add(key)
        else:
            self.keys_of_resizable_panels = keys_of_resizable_panels

    def _init_keys_of_removed_panels(
        self,
        keys_of_removed_panels: set[str] | pyd.UndefinedType,
    ) -> None:
        if isinstance(keys_of_removed_panels, pyd.UndefinedType):
            self.keys_of_removed_panels = set()
        else:
            self.keys_of_removed_panels = keys_of_removed_panels

    def copy(self) -> 'LayoutFlowContext[FrameT]':
        """
        Create a copy of the context with deep copies of mutable members.

        This creates a new context object with the same input layout panel
        and draft layout, but with deep copies of the dimensions-aware
        layout and resizable panels set to prevent unintended side effects
        when modifying the context.

        Returns:
            New LayoutFlowContext instance with copied members
        """
        return LayoutFlowContext(
            input_layout_panel=self.input_layout_panel,
            draft_layout=self.draft_layout,
            dim_aware_layout=self.dim_aware_layout.copy(),
            keys_of_resizable_panels=self.keys_of_resizable_panels.copy(),
            keys_of_removed_panels=self.keys_of_removed_panels.copy(),
        )

    @cached_property
    def frame(self) -> FrameT:
        """Get the frame of the input layout panel."""
        return self.input_layout_panel.frame

    @property
    def resized_panel(self) -> ResizedLayoutDraftPanel[FrameT]:
        """
        Create a resized layout draft panel from the current context state.

        This assembles a final panel from the input layout panel and optimized
        dimensions-aware layout, representing the completed layout optimization.

        Returns:
            Resized layout draft panel
        """
        resized_panel = ResizedLayoutDraftPanel.create_from_draft_panel(
            self.input_layout_panel,
            self.dim_aware_layout,
        )
        return resized_panel  # pyright: ignore [reportReturnType]

    @property
    def layout_dims(self) -> DimensionsWithWidthAndHeight:
        """
        Calculate the dimensions of the current layout.

        Returns:
            Dimensions of the current layout without including outer
            dimensions of subpanels (i.e. only the content, exclude titles,
            line numbers, etc.).
        """
        return self.dim_aware_layout.calc_dims(use_outer_dims_for_subpanels=False)

    @property
    def _delta_width(self) -> int | None:
        """
        Calculate the difference between frame width and layout width.

        This is used to determine if panels need to be resized to fit within
        the frame or if there's extra space available.

        Returns:
            Difference between frame width and layout width, or None if
            frame has no width
        """
        if has_width(self.frame.dims):
            return self.frame.dims.width - self.layout_dims.width
        else:
            return None

    @property
    def panel_width_ok(self) -> bool:
        """
        Check if the layout width matches the frame width exactly.

        Returns:
            True if the layout width matches the frame width or frame has no width,
            False otherwise
        """
        delta_width = self._delta_width
        return delta_width is None or delta_width == 0

    @property
    def too_wide_panel(self) -> bool:
        """
        Check if the layout is wider than the outer frame.

        Returns:
            True if the layout is wider than the outer frame, False
            otherwise
        """
        delta_width = self._delta_width
        return delta_width is not None and delta_width < 0

    @property
    def extra_width_available(self) -> bool:
        """
        Check if the outer frame has unused width available.

        Returns:
            True if the outer frame is wider than the layout, False
            otherwise
        """
        delta_width = self._delta_width
        return delta_width is not None and delta_width > 0

    @property
    def extra_width(self) -> int:
        """
        Get the amount of unused width in the outer frame.

        This is the difference between the outer frame width and layout
        width when the outer frame is wider than the layout.

        Raises:
            ValueError: If extra width is not available (outer frame is not
                        wider than layout)

        Returns:
            Amount of extra width available
        """
        delta_width = self._delta_width
        if delta_width is None:
            raise ValueError('Extra width is not available. '
                             'Please check "extra_width_available" first.')
        return delta_width

    @property
    def min_frame_width(self) -> int:
        """
        Calculate the minimum width required for the frame.

        When the total content width is less than the number of panels, the
        minimum width is set to 0 to allow for panel content to be hidden.
        Otherwise, the minimum width is 1 to ensure at least some content
        (or an ellipsis character) is visible for all panels.

        Returns:
            Minimum width required for the frame
        """
        if self.dim_aware_layout.total_subpanel_cropped_dims.width <= len(self.dim_aware_layout):
            return 0
        else:
            return 1

    def remove_panel_if_overly_cropped(self, key: str) -> bool:
        """
        Remove a panel if its has been overly cropped (currently only
        checking the crop width against the `min_crop_width` config).
        Removed panels are replaced with an ellipsis panel. Consecutive
        removed panels beyond the first are deleted entirely.
        :param key: Key of the panel to check
        :return: True if the panel was removed, False otherwise
        """
        panel = self.dim_aware_layout[key]

        if panel.config.use_min_crop_width and key != first_key_in_mapping(self.dim_aware_layout):
            if panel.overly_cropped():
                self.keys_of_removed_panels.add(key)
                self._turn_into_ellipsis_panel(key)
                self._delete_consecutively_removed_panels()
                return True
        return False

    def _turn_into_ellipsis_panel(self, key: str) -> None:
        panel = self.dim_aware_layout[key]
        ellipsis_panel = panel.create_modified_copy(
            '' if panel.title else '…',
            title='…' if panel.title else None,
            frame=Frame(Dimensions(width=1, height=None), fixed_width=True),
        )
        self.dim_aware_layout[key] = cast(DimensionsAwareDraftPanel,
                                          ellipsis_panel.render_next_stage())

    def _delete_consecutively_removed_panels(self) -> None:
        prev_key_removed = False
        keys_for_consecutively_removed_panels = []
        for cur_key in self.dim_aware_layout.keys():
            if cur_key in self.keys_of_removed_panels:
                if prev_key_removed:
                    keys_for_consecutively_removed_panels.append(cur_key)
                else:
                    prev_key_removed = True
            else:
                prev_key_removed = False

        for key in keys_for_consecutively_removed_panels:
            # Completely remove consecutive removed panels, leaving only the first
            del self.dim_aware_layout[key]

    def panel_removed(self, key) -> bool:
        return key in self.keys_of_removed_panels

    def remaining_panel_keys(self) -> tuple[str, ...]:
        """
        Get a list of keys for panels that have not been removed.

        Returns:
            List of keys for remaining panels in the layout
        """
        return tuple(
            key for key in self.dim_aware_layout.keys() if key not in self.keys_of_removed_panels)

    def changed_since(self, prev_context: 'LayoutFlowContext') -> bool:
        """
        Check if the layout dimensions or set of resizable panels have
        changed in comparison to a previous context.
        """
        return not (self.layout_dims == prev_context.layout_dims
                    and self.keys_of_resizable_panels == prev_context.keys_of_resizable_panels
                    and self.keys_of_removed_panels == prev_context.keys_of_removed_panels)

    def resizable_panel(self, key: str) -> bool:
        """
        Check if a panel with the given key is resizable.

        A panel is considered resizable if it does not have fixed width or
        have already settled into a shape (is dimensions-aware). Also, if
        a panel is being tightened without this changing the dimensions of
        the content, it is no longer considered resizable.

        Parameters:
            key: Key of the panel to check

        Returns:
            True if the panel is resizable, False otherwise
        """
        return key in self.keys_of_resizable_panels

    def update_resizability_of_panel(self, key: str, resize_helper: 'PanelResizeHelper') -> bool:
        """
        Update whether a panel should remain in the set of resizable panels.

        During resizing, some panels may reach a state where further
        tightening will not change their visible content, in which case it
        is no longer considered resizable. Conversely, if a non-resizable
        panel is widened, it will become resizable again.

        Parameters:
            key: Key of the panel being resized
            resize_helper: Helper object containing panel resize information

        Returns:
            True if the panel was removed from the set of resizable panels,
            else False
        """
        resizing = resize_helper
        if key in self.keys_of_resizable_panels:
            if self.too_wide_panel and resizing.frame_tightened and resizing.same_cropped_dims:
                self.keys_of_resizable_panels.remove(key)
                return True
        else:
            if resizing.widened_cropped_dims:
                self.keys_of_resizable_panels.add(key)
        return False


@dataclass
class PanelResizeHelper:
    """
    Helper class for panel resizing operations.

    Tracks the original and new frame dimensions of a panel being resized,
    provides methods for adjusting frame width, and properties for checking
    how dimensions have changed during resizing.

    Attributes:
        draft_panel: Original draft panel being resized
        dim_aware_panel: Dimensions-aware version of the panel
        frame_width: Current frame width
        frame_height: Current frame height
    """
    draft_panel: DraftPanel
    dim_aware_panel: DimensionsAwareDraftPanel
    frame_width: pyd.NonNegativeInt | None = None
    frame_height: pyd.NonNegativeInt | None = None

    def __post_init__(self) -> None:
        self.frame_width = self.dim_aware_panel.frame.dims.width
        self.frame_height = self.dim_aware_panel.frame.dims.height

    def adjust_frame_width(
        self,
        frame_width_delta: int,
        context: LayoutFlowContext,
    ) -> None:
        """
        Adjust the frame width of a panel by a specified delta amount.

        This method modifies the frame width while respecting minimum width
        constraints and panel fixed width settings. If the panel has fixed
        width, the width is cropped if larger than the defined frame width.

        Parameters:
            frame_width_delta: Amount to change the frame width (positive to
                               expand, negative to shrink)
            context: Layout flow context containing minimum width
                     constraints

        Returns:
            None: Updates the frame_width attribute in-place
        """
        frame_width = max(
            self.dim_aware_panel.cropped_dims.width + frame_width_delta,
            context.min_frame_width,
        )

        if self.draft_panel.frame.fixed_width:
            frame_width = self.draft_panel.frame.crop_width(frame_width, ignore_fixed_dims=True)

        self.frame_width = frame_width

    @cached_property
    def orig_frame(self) -> AnyFrame:
        """
        Get the original frame of the draft panel.

        Returns:
            Original frame of the draft panel
        """
        return self.draft_panel.frame

    @cached_property
    def new_frame(self) -> AnyFrame:
        """
        Create a new frame based on the adjusted dimensions.

        Returns a new frame with the updated width and height,
        preserving other attributes of the original frame.

        Returns:
            New frame with adjusted dimensions
        """
        return self.draft_panel.frame.modified_copy(
            width=self.frame_width,
            height=self.frame_height,
            fixed_width=False if not has_width(self.draft_panel.frame.dims) else pyd.Undefined,
        )

    @cached_property
    def frame_changed(self) -> bool:
        """
        Check if the frame dimensions have changed.

        Returns:
            True if the new frame differs from the original frame, False otherwise
        """
        return self.new_frame != self.orig_frame

    @cached_property
    def frame_tightened(self) -> bool:
        """
        Check if the frame width has been reduced.

        Returns:
            True if the new frame width is less than the original frame width,
            False otherwise
        """
        return (has_width(self.new_frame.dims) and has_width(self.orig_frame.dims)
                and self.new_frame.dims.width < self.orig_frame.dims.width)

    @cached_property
    def new_resized_panel(self) -> DimensionsAwareDraftPanel:
        """
        Create a new panel with the updated frame.

        Returns:
            New dimensions-aware draft panel with the updated frame
        """
        return create_panel_with_updated_frame(
            self.draft_panel,
            self.new_frame,
        )

    @cached_property
    def prev_cropped_dims(self) -> DimensionsWithWidthAndHeight:
        """
        Get the original cropped dimensions of the panel.

        Returns:
            Original cropped dimensions of the panel
        """
        return self.dim_aware_panel.cropped_dims

    @cached_property
    def new_cropped_dims(self) -> DimensionsWithWidthAndHeight:
        """
        Get the cropped dimensions of the panel with the new frame.

        Returns:
            Cropped dimensions of the panel with the new frame
        """
        return self.new_resized_panel.cropped_dims

    @cached_property
    def same_cropped_dims(self) -> bool:
        """
        Check if the cropped dimensions are unchanged after resizing.

        Returns:
            True if the new cropped dimensions match the previous cropped dimensions,
            False otherwise
        """
        return self.new_cropped_dims == self.prev_cropped_dims

    @cached_property
    def widened_cropped_dims(self) -> bool:
        """
        Check if the cropped width has increased after resizing.

        Returns:
            True if the new cropped width is greater than the previous cropped width,
            False otherwise
        """
        return self.new_cropped_dims.width > self.prev_cropped_dims.width


class CrampedPanelInfo(NamedTuple):
    key: str
    panel_width: int
