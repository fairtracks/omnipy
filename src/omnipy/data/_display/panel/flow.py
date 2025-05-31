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


def reflow_layout_to_fit_frame(
        input_layout_panel: DraftPanel[Layout[DraftPanel],
                                       FrameT]) -> ResizedLayoutDraftPanel[FrameT]:
    """
    Adjust a panel layout to fit within its frame constraints. Currently only handles layouts with
    a single row of panels.

    This function performs several operations in sequence:
    1. Distributes available width among panels
    2. Sets panel heights based on frame constraints
    3. Optimizes panel widths to match content
    4. Resizes panels to fit within frame width
    5. Widens panels whose titles need more space

    Parameters:
        input_layout_panel: Original draft panel containing a layout

    Returns:
        ResizedLayoutDraftPanel: Layout with optimized panel dimensions
    """

    if has_width(input_layout_panel.frame.dims):
        # Calculate widths for panels without pre-defined width
        draft_layout = _create_layout_with_distributed_widths(input_layout_panel)
    else:
        # If frame has no width, no width distribution is needed
        draft_layout = input_layout_panel.content

    outer_context = OuterLayoutResizeContext(input_layout_panel, draft_layout)

    outer_context = _set_panel_heights(outer_context)
    outer_context = _tighten_panel_widths(outer_context)

    if has_width(outer_context.frame.dims):
        outer_context = _resize_inner_panels(outer_context)
        outer_context = _tighten_panel_widths(outer_context)

        # TODO: In case outer frame is fixed width and wider than the outer
        #       panel dimensions, we need to expand the inner panels with
        #       flexible frame width, distributing the extra width among
        #       them.

        outer_context = _widen_inner_panels_to_make_room_for_titles(outer_context)

    return outer_context.resized_panel


def _create_layout_with_distributed_widths(
        layout_panel: DraftPanel[Layout[DraftPanel], FrameT]) -> Layout[DraftPanel]:
    """
    Create a new layout with widths distributed among subpanels.

    Panels with pre-defined widths keep their widths. Remaining width is
    distributed evenly among panels without pre-defined widths.
    """
    frame_dims = layout_panel.frame.dims
    draft_layout: Layout[DraftPanel] = Layout()

    # Calculate per-panel width for panels without pre-set width
    per_panel_width = _calc_per_unset_panel_width(
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


def _calc_per_unset_panel_width(
    layout: Layout,
    frame_width: int | None,
    layout_design: LayoutDesign,
) -> int | None:
    """
    Calculate width for each panel without pre-set width.
    """
    if frame_width is None:
        return None

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
class OuterLayoutResizeContext(Generic[FrameT]):
    """Context for the layout resizing process."""
    input_layout_panel: DraftPanel[Layout[DraftPanel], FrameT]
    draft_layout: Layout[DraftPanel]
    dim_aware_layout: DimensionsAwareDraftPanelLayout
    no_resize_panel_keys: set[str] = field(default_factory=set)

    def __init__(
        self,
        input_layout_panel: DraftPanel[Layout[DraftPanel], FrameT],
        draft_layout: Layout[DraftPanel],
        dim_aware_layout: DimensionsAwareDraftPanelLayout | pyd.UndefinedType = pyd.Undefined,
        no_resize_panel_keys: set[str] | pyd.UndefinedType = pyd.Undefined,
    ) -> None:
        self.input_layout_panel = input_layout_panel
        self.draft_layout = draft_layout
        self._init_dim_aware_layout(dim_aware_layout)
        self._init_no_resize_panel_keys(no_resize_panel_keys)

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

    def _init_no_resize_panel_keys(
        self,
        no_resize_panel_keys: set[str] | pyd.UndefinedType,
    ) -> None:
        if isinstance(no_resize_panel_keys, pyd.UndefinedType):
            self.no_resize_panel_keys = set()
            # Identify panels that should not be resized
            for key, draft_panel in self.draft_layout.items():
                if draft_panel.frame.fixed_width is True or panel_is_dimensions_aware(draft_panel):
                    self.no_resize_panel_keys.add(key)
        else:
            self.no_resize_panel_keys = no_resize_panel_keys

    def copy(self) -> 'OuterLayoutResizeContext[FrameT]':
        """
        Create a copy of the context, with a deep copy of changeable members (dim_aware_layout
        and no_resize_panel_keys).
        """
        return OuterLayoutResizeContext(
            input_layout_panel=self.input_layout_panel,
            draft_layout=self.draft_layout,
            dim_aware_layout=self.dim_aware_layout.copy(),
            no_resize_panel_keys=self.no_resize_panel_keys.copy(),
        )

    @cached_property
    def frame(self) -> FrameT:
        """Get the frame of the input layout panel."""
        return self.input_layout_panel.frame

    @property
    def resized_panel(self) -> ResizedLayoutDraftPanel[FrameT]:
        resized_panel = ResizedLayoutDraftPanel.create_from_draft_panel(
            self.input_layout_panel,
            self.dim_aware_layout,
        )
        return resized_panel  # pyright: ignore [reportReturnType]

    @property
    def layout_dims(self) -> DimensionsWithWidthAndHeight:
        return self.dim_aware_layout.calc_dims(use_outer_dims_for_subpanels=False)

    @property
    def delta_width(self) -> int | None:
        if has_width(self.frame.dims):
            return self.layout_dims.width - self.frame.dims.width
        else:
            return None

    @property
    def has_extra_width(self) -> int | None:
        """Calculate extra width available for resizing."""

    @property
    def extra_width(self) -> int | None:
        """Calculate extra width available for resizing."""

    @property
    def min_frame_width(self) -> int:
        if self.dim_aware_layout.total_subpanel_cropped_dims.width <= len(self.dim_aware_layout):
            return 0
        else:
            return 1

    def changed_since(self, prev_context: 'OuterLayoutResizeContext') -> bool:
        """Check if the layout dimensions or set of resizable panels have changed."""
        return not (self.layout_dims == prev_context.layout_dims
                    and self.no_resize_panel_keys == prev_context.no_resize_panel_keys)


@dataclass
class InnerPanelResizeContext:
    draft_panel: DraftPanel
    dim_aware_panel: DimensionsAwareDraftPanel
    frame_width: pyd.NonNegativeInt | None = None
    frame_height: pyd.NonNegativeInt | None = None

    def __post_init__(self) -> None:
        self.frame_width = self.dim_aware_panel.frame.dims.width
        self.frame_height = self.dim_aware_panel.frame.dims.height

    def update_frame_width(self, outer_context: OuterLayoutResizeContext) -> None:
        delta_width = outer_context.delta_width

        if delta_width:
            frame_width = self.dim_aware_panel.cropped_dims.width
            frame_width_delta = (-1) if delta_width > 0 else -delta_width
            frame_width = max(frame_width + frame_width_delta, outer_context.min_frame_width)

            if self.draft_panel.frame.fixed_width:
                frame_width = self.draft_panel.frame.crop_width(frame_width, ignore_fixed_dims=True)

            self.frame_width = frame_width

    @cached_property
    def new_panel_frame(self):
        return self.draft_panel.frame.modified_copy(
            width=self.frame_width,
            height=self.frame_height,
            fixed_width=False if not has_width(self.draft_panel.frame.dims) else pyd.Undefined,
        )

    @cached_property
    def new_resized_panel(self) -> DimensionsAwareDraftPanel:
        return _create_new_resized_panel(
            self.draft_panel,
            self.new_panel_frame,
        )

    @cached_property
    def prev_cropped_dims(self) -> DimensionsWithWidthAndHeight:
        return self.dim_aware_panel.cropped_dims

    @cached_property
    def new_cropped_dims(self) -> DimensionsWithWidthAndHeight:
        return self.new_resized_panel.cropped_dims

    def update_resizable_panels(self, key: str, outer_context: OuterLayoutResizeContext) -> bool:
        if key not in outer_context.no_resize_panel_keys:
            prev_frame_dims = self.dim_aware_panel.frame.dims
            if outer_context.delta_width and outer_context.delta_width > 0 \
                    and self.new_resized_panel.dims.width == self.dim_aware_panel.dims.width:
                if has_width(self.new_panel_frame.dims) and \
                        has_width(prev_frame_dims) and \
                        self.new_panel_frame.dims.width < prev_frame_dims.width:
                    outer_context.no_resize_panel_keys.add(key)
                    return True
        else:
            if self.new_cropped_dims.width > self.prev_cropped_dims.width:
                outer_context.no_resize_panel_keys.remove(key)

        return False

    @cached_property
    def same_cropped_dims(self) -> bool:
        return self.prev_cropped_dims == self.new_cropped_dims


def _resize_inner_panels(outer_context):
    while True:
        if not outer_context.delta_width:
            break

        prev_outer_context = outer_context.copy()

        panel_priority = _determine_panel_priority(outer_context)

        # print(f'layout_dims: {layout_dims}')
        # print(f'frame.dims: {frame.dims}')
        # print(f'delta_width: {delta_width}')
        # print(f'min_frame_width: {min_frame_width}')

        for key in panel_priority:
            inner_context = InnerPanelResizeContext(
                draft_panel=outer_context.input_layout_panel.content[key],
                dim_aware_panel=outer_context.dim_aware_layout[key],
            )

            inner_context.update_frame_width(outer_context)

            if inner_context.new_panel_frame != inner_context.dim_aware_panel.frame \
                    and inner_context.draft_panel.frame.fixed_width is not True:

                if inner_context.update_resizable_panels(key, outer_context):
                    break

                if inner_context.same_cropped_dims:
                    continue

                outer_context.dim_aware_layout[key] = inner_context.new_resized_panel
                break

        if not outer_context.changed_since(prev_outer_context):
            break
    return outer_context


def _determine_panel_priority(outer_context: OuterLayoutResizeContext[FrameT]) -> list[str]:
    def _priority(
        el: tuple[int, tuple[str, DimensionsAwarePanel[AnyFrame]]]
    ) -> tuple[int | float, int | float, int, int]:
        i, (key, panel) = el

        def _largest_panel_height_if_resizable() -> int | float:
            if key not in outer_context.no_resize_panel_keys:
                if panel.frame.fixed_height:
                    return panel.frame.crop_height(panel.dims.height, ignore_fixed_dims=True)
                else:
                    return panel.dims.height
            return float('inf')

        def _smallest_panel_frame_width_if_resizable() -> int | float:
            if key not in outer_context.no_resize_panel_keys and has_width(panel.frame.dims):
                return -panel.frame.dims.width

            return -float('inf')

        def _smallest_cropped_width() -> int:
            return -panel.cropped_dims.width

        def _last_index() -> int:
            return -i

        return (
            _largest_panel_height_if_resizable(),
            _smallest_panel_frame_width_if_resizable(),
            _smallest_cropped_width(),
            _last_index(),
        )

    panel_priority = [
        key for _i, (key, _panel) in sorted(
            enumerate(outer_context.dim_aware_layout.items()), key=_priority,
            reverse=outer_context.delta_width is not None and outer_context.delta_width < 0)
    ]

    # print(f'panel_priority: {panel_priority}')
    # for i, (key, panel) in enumerate(outer_context.dim_aware_layout.items()):
    #     print(f'panel frame: {key}: {panel.frame}')
    #     print(f'_priority(({i}, ({key}, <panel>))): {_priority((i, (key, panel)))}')

    return panel_priority


def _create_new_resized_panel(
    draft_panel_basis: DraftPanel[ContentT, AnyFrame],
    frame: FrameInvT,
) -> DimensionsAwareDraftPanel[FrameInvT]:
    """
    Create a new dimensions-aware panel based on an existing panel with a
    new frame.

    This function creates a copy of the draft panel with a new frame and
    ensures the returned panel is dimensions-aware. If the original panel is
    not dimensions-aware, it renders the next stage to get a
    dimensions-aware panel.
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


def _set_panel_heights(
        outer_context: OuterLayoutResizeContext[FrameT]) -> OuterLayoutResizeContext[FrameT]:
    """
    Adjust heights of panels in a layout based on frame height.

    For non-fixed height panels in the layout, sets their height to match
    the container frame's available height (minus borders). Panels with
    fixed height retain their original height.
    """
    frame = outer_context.frame

    layout_design = outer_context.input_layout_panel.config.layout_design
    layout_design_dims = LayoutDesignDims.create(layout_design)

    per_panel_height = None
    if has_height(frame.dims):
        per_panel_height = max(frame.dims.height - layout_design_dims.extra_vertical_chars(1), 0)

    for key, panel in outer_context.dim_aware_layout.items():
        should_use_panel_original_height = (per_panel_height is None or panel.frame.fixed_height)

        if not should_use_panel_original_height:
            outer_context.dim_aware_layout[key] = dataclasses.replace(
                panel,
                frame=panel.frame.modified_copy(height=per_panel_height,
                                                fixed_height=False),  # type: ignore[arg-type]
            )

    return outer_context


def _tighten_panel_widths(
        outer_context: OuterLayoutResizeContext[FrameT]) -> OuterLayoutResizeContext[FrameT]:
    """
    Reduce panel widths to match their content width when possible.

    Panels with fixed width or without specified width are left unchanged.
    """
    for key, panel in outer_context.dim_aware_layout.items():
        # Skip panels without width or with fixed width constraint
        if not has_width(panel.frame.dims) or panel.frame.fixed_width:
            continue

        # Calculate new optimal width
        new_frame = panel.frame.modified_copy(width=panel.frame.crop_width(panel.dims.width))

        # Only update panel if frame dimensions changed
        if new_frame != panel.frame:
            outer_context.dim_aware_layout[key] = dataclasses.replace(
                panel,
                frame=new_frame,  # type: ignore[arg-type]
            )

    return outer_context


class CrampedPanelInfo(NamedTuple):
    key: str
    panel_width: int


def _widen_inner_panels_to_make_room_for_titles(
        outer_context: OuterLayoutResizeContext[FrameT]) -> OuterLayoutResizeContext[FrameT]:
    """
    Allocate extra width to panels whose titles are wider than their content
    areas.

    Distributes available extra width to panels that need it most (where
    title width exceeds content width), prioritizing smallest gaps first.
    """
    assert outer_context.delta_width is not None
    extra_width = -outer_context.delta_width

    # Find panels with titles wider than content
    cramped_panels = _identify_cramped_panels(outer_context)
    if not cramped_panels or extra_width <= 0:
        return outer_context

    # Distribute extra width to cramped panels
    panel_width_additions = _allocate_extra_width(cramped_panels, extra_width)

    # Apply width additions to panels
    return _apply_width_additions(outer_context, panel_width_additions)


def _identify_cramped_panels(
        outer_context: OuterLayoutResizeContext[FrameT]
) -> defaultdict[int, list[CrampedPanelInfo]]:
    """
    Identify panels where title width exceeds content width and group by
    title width.
    """
    title_width2cramped_panels: defaultdict[int, list[CrampedPanelInfo]] = defaultdict(list)

    for key, panel in outer_context.dim_aware_layout.items():
        if (panel.title_width > 0 and has_width(panel.frame.dims)
                and panel.frame.fixed_width is not True
                and panel.cropped_dims.width < panel.title_width):
            title_width2cramped_panels[panel.title_width].append(
                CrampedPanelInfo(key, panel.cropped_dims.width))

    return title_width2cramped_panels


def _allocate_extra_width(
    title_width2cramped_panels: defaultdict[int, list[CrampedPanelInfo]],
    extra_width: int,
) -> defaultdict[str, int]:
    """
    Distribute extra width to cramped panels, prioritizing smallest gaps
    first.
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
    outer_context: OuterLayoutResizeContext[FrameT],
    panel_width_additions: defaultdict[str, int],
) -> OuterLayoutResizeContext[FrameT]:
    """Apply calculated width additions to panels that need them."""
    for key, width_addition in panel_width_additions.items():
        dim_aware_panel = outer_context.dim_aware_layout[key]
        panel_width = dim_aware_panel.cropped_dims.width

        outer_context.dim_aware_layout[key] = _create_new_resized_panel(
            outer_context.draft_layout[key],
            dim_aware_panel.frame.modified_copy(
                width=panel_width + width_addition, fixed_width=False),
        )

    return outer_context
