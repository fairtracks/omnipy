from collections import defaultdict
import dataclasses
from dataclasses import dataclass, field
from functools import cached_property
from typing import cast, Generic, NamedTuple

from omnipy.data._display.config import LayoutDesign
from omnipy.data._display.dimensions import DimensionsWithWidthAndHeight, has_height, has_width
from omnipy.data._display.frame import AnyFrame
from omnipy.data._display.panel.base import (DimensionsAwarePanel,
                                             FrameInvT,
                                             FrameT,
                                             panel_is_dimensions_aware)
from omnipy.data._display.panel.draft.base import ContentT, DimensionsAwareDraftPanel, DraftPanel
from omnipy.data._display.panel.draft.layout import (DimensionsAwareDraftPanelLayout,
                                                     ResizedLayoutDraftPanel)
from omnipy.data._display.panel.layout import Layout, LayoutDesignDims
import omnipy.util._pydantic as pyd


def optimize_layout_to_fit_frame(
        input_layout_panel: DraftPanel[Layout[DraftPanel],
                                       FrameT]) -> ResizedLayoutDraftPanel[FrameT]:
    """
    Adjust a panel layout to fit within its frame constraints. Currently
    only handles layouts with a single row of panels.

    This function performs several operations in sequence:
    1. Distributes available width among panels, if frame width is defined
    2. Sets panel heights based on frame height, if defined
    3. Tightens panel widths if they exceed their frame width
    4. Iteratively resizes panels to fit within the total frame width
    5. Widens panels whose titles need more space

    Parameters:
        input_layout_panel: Original draft panel containing a layout to be
                            optimized

    Returns:
        ResizedLayoutDraftPanel: Layout with optimized panel dimensions
    """

    if has_width(input_layout_panel.frame.dims):
        # Calculate widths for panels without pre-defined width
        draft_layout = _create_layout_with_distributed_widths(input_layout_panel)
    else:
        # If frame has no width, no width distribution is needed
        draft_layout = input_layout_panel.content

    context = LayoutFlowContext(input_layout_panel, draft_layout)

    context = _set_panel_heights(context)
    context = _tighten_panel_frame_widths(context)

    if has_width(context.frame.dims):
        context = _resize_inner_panels(context)
        context = _tighten_panel_frame_widths(context)

        # TODO: In case outer frame is fixed width and wider than the outer
        #       panel dimensions, we need to expand the inner panels with
        #       flexible frame width, distributing the extra width among
        #       them.

        context = _widen_inner_panels_to_make_room_for_titles(context)

    return context.resized_panel  # pyright: ignore [reportReturnType]


def _create_layout_with_distributed_widths(
        layout_panel: DraftPanel[Layout[DraftPanel], FrameT]) -> Layout[DraftPanel]:
    """
    Create a new layout with widths distributed among subpanels.

    Panels with pre-defined widths keep their widths. Remaining width is
    distributed evenly among panels without pre-defined widths.

    Parameters:
        layout_panel: Draft panel containing a layout

    Returns:
        New layout with distributed panel widths
    """
    frame_dims = layout_panel.frame.dims
    draft_layout: Layout[DraftPanel] = Layout()

    if has_width(frame_dims):
        # Calculate per-panel width for panels without pre-set width
        per_panel_width = _calculate_per_panel_width_for_panels_without_width(
            layout_panel.content,
            frame_dims.width,
            layout_panel.config.layout_design,
        )

        # Apply calculated widths to each panel
        for key, panel in layout_panel.content.items():
            panel_width, fixed_width = _determine_panel_width(panel, per_panel_width)

            draft_layout[key] = dataclasses.replace(
                panel,
                frame=panel.frame.modified_copy(width=panel_width, fixed_width=fixed_width),
            )

    return draft_layout


def _calculate_per_panel_width_for_panels_without_width(
    layout: Layout,
    frame_width: int,
    layout_design: LayoutDesign,
) -> int | None:
    """
    Calculate width for each panel without pre-set width.

    This divides the available frame width (after accounting for panels with
    preset widths and border characters) among panels without pre-defined
    widths. Pre-defined widths can either be defined in the frame or
    calculated based on contents (or both).


    Parameters:
        layout: The panel layout
        frame_width: Width of the containing frame, or None if not constrained
        layout_design: Layout design parameters

    Returns:
        Width for each panel without pre-set width, or None if all panels
        already have pre-set widths.
    """
    width_unset_panels = {}
    preset_width = 0

    layout_design_dims = LayoutDesignDims.create(layout_design)

    # Calculate total width used by panels with pre-set width
    for key, panel in layout.items():
        if has_width(panel.frame.dims):
            preset_width += panel.frame.dims.width + layout_design_dims.horizontal_chars_per_panel
        elif panel_is_dimensions_aware(panel):
            preset_width += panel.dims.width + layout_design_dims.horizontal_chars_per_panel
        else:
            width_unset_panels[key] = panel

    preset_width += layout_design_dims.horizontal_end_chars

    # Calculate width per unset panel
    num_unset_panels = len(width_unset_panels)
    if num_unset_panels > 0:
        available_width = frame_width - preset_width
        per_panel_width = ((available_width // num_unset_panels)
                           - layout_design_dims.horizontal_chars_per_panel)
        return max(per_panel_width, 0)

    return None


def _determine_panel_width(panel: DraftPanel,
                           per_panel_width: int | None) -> tuple[int | None, bool | None]:
    """
    Determine width and fixed_width flag for a panel.

    For panels without a pre-defined width, assigns the calculated per-panel width.
    For panels with an existing width, preserves their original width and fixed_width flag.

    Parameters:
        panel: Panel to determine width for
        per_panel_width: Calculated width for panels without pre-set width

    Returns:
        Tuple of (width, fixed_width) for the panel
    """
    # For panels with unset frame width and no calculated dimensions, use
    # calculated per_panel_width
    if not has_width(panel.frame.dims) and not panel_is_dimensions_aware(panel):
        return per_panel_width, False

    # For panels with set frame width, keep original width and fixed_width
    return panel.frame.dims.width, panel.frame.fixed_width


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
    keys_of_resizable_panels: set[str] = field(default_factory=set)

    def __init__(
        self,
        input_layout_panel: DraftPanel[Layout[DraftPanel], FrameT],
        draft_layout: Layout[DraftPanel],
        dim_aware_layout: DimensionsAwareDraftPanelLayout | pyd.UndefinedType = pyd.Undefined,
        keys_of_resizable_panels: set[str] | pyd.UndefinedType = pyd.Undefined,
    ) -> None:
        self.input_layout_panel = input_layout_panel
        self.draft_layout = draft_layout
        self._init_dim_aware_layout(dim_aware_layout)
        self._init_keys_of_resizable_panels(keys_of_resizable_panels)

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
            dimensions of subpanels (i.e. only the contents, exclude titles,
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

    def changed_since(self, prev_context: 'LayoutFlowContext') -> bool:
        """
        Check if the layout dimensions or set of resizable panels have
        changed in comparison to a previous context.
        """
        return not (self.layout_dims == prev_context.layout_dims
                    and self.keys_of_resizable_panels == prev_context.keys_of_resizable_panels)

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

    def update_resizability_of_panel(self, key: str, resize_helper: 'PanelResizeHelper'):
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
            True if the panel was removed from the set of resizable panels
        """
        resizing = resize_helper
        if key in self.keys_of_resizable_panels:
            if self.too_wide_panel and resizing.frame_tightened and resizing.same_cropped_dims:
                self.keys_of_resizable_panels.remove(key)
                return True
        else:
            if resizing.widened_cropped_dims:
                self.keys_of_resizable_panels.add(key)


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
        return _create_panel_with_updated_frame(
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


def _resize_inner_panels(context: LayoutFlowContext):
    """
    Iteratively resize inner panels to fit within the total frame width.

    This function adjusts panel widths based on priority order until either:
    1. The total width fits perfectly within the frame
    2. No further adjustments can be made without violating constraints

    The algorithm prioritizes certain panels for resizing based on their
    dimensions, position in the layout, and whether they're marked as
    resizable.

    Parameters:
        context: The layout flow context containing panels to be resized

    Returns:
        Updated layout flow context with resized panels
    """
    while True:
        if context.panel_width_ok:
            break

        prev_context = context.copy()

        panel_priority = _sort_panels_by_resize_priority(context)

        for key in panel_priority:
            resize_helper = PanelResizeHelper(
                draft_panel=context.input_layout_panel.content[key],
                dim_aware_panel=context.dim_aware_layout[key],
            )

            if context.extra_width_available:
                frame_width_delta = context.extra_width
            else:
                # If no extra width is available, reduce frame width by 1.
                frame_width_delta = -1

            resize_helper.adjust_frame_width(frame_width_delta, context)

            if resize_helper.frame_changed and resize_helper.orig_frame.fixed_width is not True:

                panel_no_longer_resizable = context.update_resizability_of_panel(key, resize_helper)
                if panel_no_longer_resizable:
                    break

                if resize_helper.same_cropped_dims:
                    continue

                context.dim_aware_layout[key] = resize_helper.new_resized_panel
                break

        if not context.changed_since(prev_context):
            break
    return context


def _sort_panels_by_resize_priority(context: LayoutFlowContext[FrameT]) -> list[str]:
    """
    Sort panels by priority for resizing operations.

    When shrinking (`context.too_wide_panel == True`), prioritizes:
    1. Shortest resizable panels first (lowest frame-cropped height)
    2. Resizable panels with the widest frames
    3. Panels with the widest (frame-cropped) contents
    4. Panel most to the right in the layout (lowest index)

    When expanding (`context.extra_width_available == True`), the priority
    order is reversed.

    Parameters:
        context: The layout flow context

    Returns:
        List of panel keys sorted by resize priority
    """
    def _priority(
        el: tuple[int, tuple[str, DimensionsAwarePanel[AnyFrame]]]
    ) -> tuple[int | float, int | float, int, int]:
        i, (key, panel) = el

        def _shortest_panel_if_resizable() -> int | float:
            if key in context.keys_of_resizable_panels:
                if panel.frame.fixed_height:
                    return panel.frame.crop_height(panel.dims.height, ignore_fixed_dims=True)
                else:
                    return panel.dims.height
            return float('inf')

        def _panel_with_widest_frame_if_resizable() -> int | float:
            if key in context.keys_of_resizable_panels and has_width(panel.frame.dims):
                return -panel.frame.dims.width

            return float('inf')

        def _widest_panel() -> int:
            return -panel.cropped_dims.width

        def _lowest_index() -> int:
            return -i

        return (
            _shortest_panel_if_resizable(),
            _panel_with_widest_frame_if_resizable(),
            _widest_panel(),
            _lowest_index(),
        )

    panel_priority = [
        key for _i, (key, _panel) in sorted(
            enumerate(context.dim_aware_layout.items()), key=_priority,
            reverse=context.extra_width_available)
    ]

    # print(f'context._delta_width: {context._delta_width}')
    # print(f'panel_priority: {panel_priority}')
    # for i, (key, panel) in enumerate(context.dim_aware_layout.items()):
    #     print(f'panel frame: {key}: {panel.frame}')
    #     print(f'_priority(({i}, ({key}, <panel>))): {_priority((i, (key, panel)))}')

    return panel_priority


def _create_panel_with_updated_frame(
    draft_panel_basis: DraftPanel[ContentT, AnyFrame],
    frame: FrameInvT,
) -> DimensionsAwareDraftPanel[FrameInvT]:
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
        return cast(DimensionsAwareDraftPanel[FrameInvT], new_draft_panel.render_next_stage())
    else:
        return cast(DimensionsAwareDraftPanel[FrameInvT], new_draft_panel)


def _set_panel_heights(context: LayoutFlowContext[FrameT]) -> LayoutFlowContext[FrameT]:
    """
    Adjust heights of panels in a layout based on the frame's constraints.

    For panels with flexible heights, this sets their height to match the
    container frame's available height (minus borders). Panels with fixed
    height retain their original height.

    Parameters:
        context: The layout flow context containing panels to be adjusted

    Returns:
        Updated layout flow context with adjusted panel heights
    """
    frame = context.frame

    layout_design = context.input_layout_panel.config.layout_design
    layout_design_dims = LayoutDesignDims.create(layout_design)

    per_panel_height = None
    if has_height(frame.dims):
        per_panel_height = max(frame.dims.height - layout_design_dims.extra_vertical_chars(1), 0)

    for key, panel in context.dim_aware_layout.items():
        should_use_panel_original_height = (per_panel_height is None or panel.frame.fixed_height)

        if not should_use_panel_original_height:
            context.dim_aware_layout[key] = dataclasses.replace(
                panel,
                frame=panel.frame.modified_copy(height=per_panel_height,
                                                fixed_height=False),  # type: ignore[arg-type]
            )

    return context


def _tighten_panel_frame_widths(context: LayoutFlowContext[FrameT]) -> LayoutFlowContext[FrameT]:
    """
    Reduce panel frame widths to match their content width when possible.

    This function adjusts the frame of panels with flexible frame widths to
    be only as wide as needed for their content, which helps optimize space
    usage in the layout.

    Parameters:
        context: The layout flow context containing panels to be adjusted

    Returns:
        Updated layout flow context with tightened panel frame widths
    """
    for key, panel in context.dim_aware_layout.items():
        # Skip panels without frame width or with fixed frame width
        if not has_width(panel.frame.dims) or panel.frame.fixed_width:
            continue

        # Calculate new tightened width
        new_frame = panel.frame.modified_copy(width=panel.frame.crop_width(panel.dims.width))

        # Only update panel if frame dimensions changed
        if new_frame != panel.frame:
            context.dim_aware_layout[key] = dataclasses.replace(
                panel,
                frame=new_frame,  # type: ignore[arg-type]
            )

    return context


class CrampedPanelInfo(NamedTuple):
    key: str
    panel_width: int


def _widen_inner_panels_to_make_room_for_titles(
        context: LayoutFlowContext[FrameT]) -> LayoutFlowContext[FrameT]:
    """
    Allocate extra width to panels whose titles are wider than their frames.

    If there is unused width available in the layout frame, this function
    distributes it to panels where the title width exceeds the panel width.
    It prioritizes panels with shorter titles first to ensure the maximum
    number of titles can be fully displayed.

    Parameters:
        context: The layout flow context

    Returns:
        Updated context with widened panels
    """
    if not context.extra_width_available:
        # No extra width available to distribute
        return context

    # Find panels with titles wider than their frames
    cramped_panels = _identify_cramped_panels(context)
    if not cramped_panels:
        return context

    # Distribute extra width to cramped panels
    panel_width_additions = _distribute_width_to_cramped_panels(cramped_panels, context.extra_width)

    # Apply width additions to panels
    return _apply_width_additions(context, panel_width_additions)


def _identify_cramped_panels(
        context: LayoutFlowContext[FrameT]) -> defaultdict[int, list[CrampedPanelInfo]]:
    """
    Identify panels where the title width exceeds the frame width, and where
    the frame width is defined to be flexible (not fixed).

    Groups panels by their title width to facilitate prioritizing
    shorter titles first when distributing extra width.

    Parameters:
        context: The layout flow context

    Returns:
        Dict mapping title widths to lists of cramped panels
    """
    title_width2cramped_panels: defaultdict[int, list[CrampedPanelInfo]] = defaultdict(list)

    for key, panel in context.dim_aware_layout.items():
        if (panel.title_width > 0 and has_width(panel.frame.dims)
                and panel.frame.fixed_width is not True
                and panel.cropped_dims.width < panel.title_width):
            title_width2cramped_panels[panel.title_width].append(
                CrampedPanelInfo(key, panel.cropped_dims.width))

    return title_width2cramped_panels


def _distribute_width_to_cramped_panels(
    title_width2cramped_panels: defaultdict[int, list[CrampedPanelInfo]],
    extra_width: int,
) -> defaultdict[str, int]:
    """
    Distribute extra width to cramped panels, prioritizing shortest titles
    first.

    Uses a round-robin approach to add 1 unit of width at a time to panels
    with the shortest titles first until either all panels fit their titles
    or the extra width is exhausted.

    Parameters:
        title_width2cramped_panels: Dict mapping title widths to panels
        extra_width: Total extra width available to distribute

    Returns:
        Dict mapping panel keys to width additions
    """
    panel_width_additions: defaultdict[str, int] = defaultdict(int)
    title_widths = list(sorted(title_width2cramped_panels.keys()))

    while extra_width > 0 and title_widths:
        title_width = title_widths[0]
        key, panel_width = title_width2cramped_panels[title_width].pop(0)

        # Add 1 to this panel's width
        panel_width_additions[key] += 1
        extra_width -= 1

        # If panel still needs width, put it back in the queue
        if panel_width + 1 < title_width:
            title_width2cramped_panels[title_width].append(CrampedPanelInfo(key, panel_width + 1))

        elif not title_width2cramped_panels[title_width]:
            # Remove empty title width entries
            del title_width2cramped_panels[title_width]
            title_widths.pop(0)

    return panel_width_additions


def _apply_width_additions(
    context: LayoutFlowContext[FrameT],
    panel_width_additions: defaultdict[str, int],
) -> LayoutFlowContext[FrameT]:
    """
    Apply calculated width additions to panels that need more space for
    titles.

    Parameters:
        context: The layout flow context containing panels to be modified
        panel_width_additions: Dict mapping panel keys to width amounts to
                               add

    Returns:
        Updated layout flow context with modified panel frames
    """
    for key, width_addition in panel_width_additions.items():
        dim_aware_panel = context.dim_aware_layout[key]
        panel_width = dim_aware_panel.cropped_dims.width

        context.dim_aware_layout[key] = _create_panel_with_updated_frame(
            context.draft_layout[key],
            dim_aware_panel.frame.modified_copy(
                width=panel_width + width_addition, fixed_width=False),
        )

    return context
