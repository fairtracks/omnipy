from collections import defaultdict
import dataclasses
from typing import Callable

from typing_extensions import TypeVar

from omnipy.data._display.dimensions import has_height, has_width
from omnipy.data._display.frame import AnyFrame
from omnipy.data._display.layout.base import Layout, PanelDesignDims
from omnipy.data._display.layout.flow.helpers import (CrampedPanelInfo,
                                                      create_panel_with_updated_frame,
                                                      LayoutFlowContext,
                                                      PanelResizeHelper)
from omnipy.data._display.panel.base import DimensionsAwarePanel, panel_is_dimensions_aware
from omnipy.data._display.panel.draft.base import DimensionsAwareDraftPanel, DraftPanel
from omnipy.data._display.panel.draft.layout import ResizedLayoutDraftPanel
from omnipy.data._display.panel.typedefs import FrameT
from omnipy.shared.enums.display import PanelDesign
import omnipy.util._pydantic as pyd

LayoutT = TypeVar('LayoutT', bound=Layout)


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

    # print('Preparing draft layout...')
    if has_width(input_layout_panel.frame.dims):
        # Calculate widths for panels without pre-defined width
        draft_layout = _create_layout_with_distributed_widths(input_layout_panel)
    else:
        # If frame has no width, no width distribution is needed
        draft_layout = input_layout_panel.content.copy()

    if has_height(input_layout_panel.frame.dims):
        # Setting the heights of the inner panel of the draft layout...')
        draft_layout = _set_inner_panel_heights(input_layout_panel, draft_layout)

    # print('Creating LayoutFlowContext...')
    context = LayoutFlowContext(input_layout_panel, draft_layout)

    # print('Tightening panel frame widths...')
    context = _tighten_panel_frame_widths(context)

    if has_width(context.frame.dims) and len(context.draft_layout) > 1:
        # print('Resizing inner panels...')
        context = _resize_inner_panels(context)

    if has_height(context.frame.dims):
        # print('Reducing panel heights...')
        context = _reduce_panel_heights(context)

    if has_width(context.frame.dims):
        # print('Tightening panel frame widths again...')
        context = _tighten_panel_frame_widths(context)

        # print('Widening inner panels to make room for titles...')
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
            layout_panel.config.panel_design,
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
    panel_design: PanelDesign.Literals,
) -> int | None:
    """
    Calculate width for each panel without pre-set width.

    This divides the available frame width (after accounting for panels with
    preset widths and border characters) among panels without pre-defined
    widths. Pre-defined widths can either be defined in the frame or
    calculated based on content (or both).


    Parameters:
        layout: The panel layout
        frame_width: Width of the containing frame, or None if not constrained
        panel_design: Layout design parameters

    Returns:
        Width for each panel without pre-set width, or None if all panels
        already have pre-set widths.
    """
    width_unset_panels = {}
    preset_width = 0

    panel_design_dims = PanelDesignDims.create(panel_design)

    # Calculate total width used by panels with pre-set width
    for key, panel in layout.items():
        if has_width(panel.frame.dims):
            preset_width += (
                panel.frame.dims.width + panel_design_dims.num_horizontal_chars_per_panel)
        elif panel_is_dimensions_aware(panel):
            preset_width += (panel.dims.width + panel_design_dims.num_horizontal_chars_per_panel)
        else:
            width_unset_panels[key] = panel

    preset_width += panel_design_dims.num_horizontal_end_chars

    # Calculate width per unset panel
    num_unset_panels = len(width_unset_panels)
    if num_unset_panels > 0:
        available_width = frame_width - preset_width
        per_panel_width = ((available_width // num_unset_panels)
                           - panel_design_dims.num_horizontal_chars_per_panel)
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

        if context.panel_width_ok:
            break
    return context


def _sort_panels_by_resize_priority(context: LayoutFlowContext[FrameT]) -> list[str]:
    """
    Sort panels by priority for resizing operations.

    When shrinking (`context.too_wide_panel == True`), prioritizes:
    1. Shortest resizable panels first (lowest frame-cropped height)
    2. Resizable panels with the widest frames
    3. Panels with the widest (frame-cropped) content
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


def _set_inner_panel_heights(input_layout_panel: DraftPanel[Layout[DraftPanel], AnyFrame],
                             draft_layout: Layout[DraftPanel]) -> Layout[DraftPanel]:
    """
    Adjust heights of panels in a layout based on the frame's constraints.

    For panels with flexible heights, this sets their height to match the
    container frame's available height (minus borders). Panels with fixed
    height retain their original height.

    Parameters:
        input_layout_panel: The input layout panel
        draft_layout: The initial layout of draft panels

    Returns:
        Updated layout of draft panels with adjusted heights
    """
    assert has_height(input_layout_panel.frame.dims)

    per_inner_panel_height = _calc_inner_panel_height(
        input_layout_panel.config.panel_design,
        input_layout_panel.frame.dims.height,
    )

    return _resize_inner_panel_heights(
        draft_layout,
        lambda _panel: per_inner_panel_height,
    )


def _calc_inner_panel_height(panel_design: PanelDesign.Literals, outer_panel_height: int) -> int:
    panel_design_dims = PanelDesignDims.create(panel_design)

    inner_panel_height = max(outer_panel_height - panel_design_dims.num_extra_vertical_chars(1), 0)
    return inner_panel_height


def _resize_inner_panel_heights(
    layout: LayoutT,
    panel_height_func: Callable[[DimensionsAwareDraftPanel], pyd.NonNegativeInt],
) -> LayoutT:
    for key, panel in layout.items():
        should_use_panel_original_height = panel.frame.fixed_height

        if not should_use_panel_original_height:
            layout[key] = dataclasses.replace(
                panel,
                frame=panel.frame.modified_copy(
                    height=panel_height_func(panel), fixed_height=False),
            )
    return layout


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
        if (panel.title_width > 0 and panel.title_height > 0 and has_width(panel.frame.dims)
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

        context.dim_aware_layout[key] = create_panel_with_updated_frame(
            context.draft_layout[key],
            dim_aware_panel.frame.modified_copy(
                width=panel_width + width_addition, fixed_width=True),
        )

    return context


def _reduce_panel_heights(context: LayoutFlowContext[FrameT]) -> LayoutFlowContext[FrameT]:
    context.dim_aware_layout = _resize_inner_panel_heights(
        context.dim_aware_layout,
        lambda panel: panel.outer_dims.height,
    )

    return context
