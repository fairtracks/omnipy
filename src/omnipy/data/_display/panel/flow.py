from collections import defaultdict
import dataclasses
from typing import cast

from omnipy.data._display.dimensions import (Dimensions,
                                             DimensionsWithWidthAndHeight,
                                             has_height,
                                             has_width)
from omnipy.data._display.frame import AnyFrame, Frame
from omnipy.data._display.panel.base import (DimensionsAwarePanel,
                                             FrameInvT,
                                             FrameT,
                                             panel_is_dimensions_aware)
from omnipy.data._display.panel.draft.base import ContentT, DimensionsAwareDraftPanel, DraftPanel
from omnipy.data._display.panel.draft.layout import ResizedLayoutDraftPanel
from omnipy.data._display.panel.layout import Layout
import omnipy.util._pydantic as pyd


def flow_layout_subpanels_inside_frame(
        layout_panel: DraftPanel[Layout[DraftPanel], FrameT]) -> ResizedLayoutDraftPanel[FrameT]:

    if not has_width(layout_panel.frame.dims):
        draft_layout: Layout = layout_panel.content
    else:
        frame_dims = layout_panel.frame.dims

        per_panel_width = None

        width_unset_panels = {}
        if has_width(frame_dims):
            preset_width = 0
            for key, panel in layout_panel.content.items():
                if panel.frame is not None and panel.frame.dims.width is not None:
                    preset_width += panel.frame.dims.width + 3
                elif panel_is_dimensions_aware(panel) and panel.dims.width is not None:
                    preset_width += panel.dims.width + 3
                else:
                    width_unset_panels[key] = panel

            num_unset_panels = len(width_unset_panels)
            if num_unset_panels > 0:
                per_panel_width = ((frame_dims.width - preset_width - 1) // num_unset_panels) - 3
                per_panel_width = max(per_panel_width, 0)
            else:
                per_panel_width = 0

        # print(f'per_panel_width: {per_panel_width}')

        draft_layout = Layout()
        for key, panel in layout_panel.content.items():
            if key in width_unset_panels:
                frame_width: int | None = per_panel_width
                frame_fixed_width: bool | None = False
            else:
                frame_width = panel.frame.dims.width
                frame_fixed_width = panel.frame.fixed_width

            draft_layout[key] = dataclasses.replace(
                panel,
                frame=Frame(
                    Dimensions(
                        width=frame_width,
                        height=panel.frame.dims.height,
                    ),
                    fixed_width=frame_fixed_width,
                    fixed_height=panel.frame.fixed_height,
                ),
            )

    return resize_layout_to_fit_frame(layout_panel, draft_layout)


def _create_new_resized_panel(
    draft_panel_basis: DraftPanel[ContentT, AnyFrame],
    frame: FrameInvT,
) -> DimensionsAwareDraftPanel[FrameInvT]:
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
    frame: AnyFrame,
    dim_aware_layout: Layout[DimensionsAwareDraftPanel[AnyFrame]],
) -> Layout[DimensionsAwareDraftPanel[AnyFrame]]:

    per_panel_height = None

    if has_height(frame.dims):
        per_panel_height = frame.dims.height - 2
        per_panel_height = max(per_panel_height, 0)

    # print(f'per_panel_height: {per_panel_height}')

    for key, panel in dim_aware_layout.items():
        if per_panel_height is not None \
                and not panel.frame.fixed_height:
            frame_fixed_height = False

            dim_aware_layout[key] = dataclasses.replace(
                panel,
                frame=Frame(  # type: ignore[arg-type]
                    Dimensions(
                        width=panel.frame.dims.width,
                        height=per_panel_height,
                    ),
                    fixed_width=panel.frame.fixed_width,
                    fixed_height=frame_fixed_height,
                ),
            )

    return dim_aware_layout


def _tighten_panel_widths(
    dim_aware_layout: Layout[DimensionsAwareDraftPanel[AnyFrame]]
) -> Layout[DimensionsAwareDraftPanel[AnyFrame]]:
    for key, panel in dim_aware_layout.items():
        if panel.frame.dims.width is not None and not panel.frame.fixed_width:
            new_frame_width: int | None = min(panel.frame.dims.width, panel.dims.width)
            new_fixed_width: bool | None = panel.frame.fixed_width
        else:
            new_frame_width = panel.frame.dims.width
            new_fixed_width = panel.frame.fixed_width if has_width(panel.frame.dims) else None

        frame = Frame(
            Dimensions(width=new_frame_width, height=panel.frame.dims.height),
            fixed_width=new_fixed_width,
            fixed_height=panel.frame.fixed_height)

        if frame != panel.frame:
            dim_aware_layout[key] = \
                dataclasses.replace(panel, frame=frame)  # type: ignore[arg-type]
    return dim_aware_layout


def _widen_inner_panels_to_make_room_for_titles(
    dim_aware_layout: Layout[DimensionsAwareDraftPanel[AnyFrame]],
    draft_layout: Layout[DraftPanel[Layout, AnyFrame]],
    extra_width: int,
) -> Layout[DimensionsAwareDraftPanel[AnyFrame]]:
    title_width2cramped_panel_info: defaultdict[int, list[tuple[str, int]]] = defaultdict(list)

    for key, panel in dim_aware_layout.items():
        if panel.title_width > 0 \
                and panel.frame.dims.width is not None \
                and panel.frame.fixed_width is not True \
                and panel.dims_if_cropped.width < panel.title_width:
            title_width2cramped_panel_info[panel.title_width].append(
                (key, panel.dims_if_cropped.width))

    title_widths = list(sorted(title_width2cramped_panel_info.keys()))
    panel_width_additions: defaultdict[str, int] = defaultdict(int)

    while extra_width != 0 and len(title_widths) > 0:
        title_width = title_widths[0]
        key, panel_width = title_width2cramped_panel_info[title_width].pop(0)
        panel_width_additions[key] += 1
        extra_width -= 1
        if panel_width + 1 < title_width:
            title_width2cramped_panel_info[title_width].append((key, panel_width + 1))
        if len(title_width2cramped_panel_info[title_width]) == 0:
            del title_width2cramped_panel_info[title_width]
            title_widths.pop(0)

    for key, width_addition in panel_width_additions.items():
        dim_aware_panel = dim_aware_layout[key]
        panel_width = dim_aware_panel.dims_if_cropped.width
        title_adjusted_frame = Frame(
            dims=Dimensions(
                width=panel_width + width_addition,
                height=dim_aware_panel.frame.dims.height,
            ),
            fixed_width=False,
            fixed_height=dim_aware_panel.frame.fixed_height,
        )
        dim_aware_layout[key] = _create_new_resized_panel(
            draft_layout[key],
            title_adjusted_frame,
        )
    return dim_aware_layout


def resize_layout_to_fit_frame(  # noqa: C901
    layout_panel: DraftPanel[Layout[DraftPanel], FrameT],
    draft_layout: Layout,
) -> ResizedLayoutDraftPanel[FrameT]:

    # dim_aware_panels: dict[str, DimensionsAwarePanel[AnyFrame]] = panel.content
    resized_panel = ResizedLayoutDraftPanel.create_from_draft_panel(layout_panel, draft_layout)
    frame = resized_panel.frame

    dim_aware_layout = resized_panel.content
    dim_aware_layout = _set_panel_heights(frame, dim_aware_layout)
    dim_aware_layout = _tighten_panel_widths(dim_aware_layout)
    dim_aware_layout = _widen_inner_panels_to_make_room_for_titles(
        dim_aware_layout,
        draft_layout,
        extra_width=-1,
    )

    prev_layout_dims: DimensionsWithWidthAndHeight | None = None

    no_resize_panel_keys: set[str] = set()
    for key, draft_panel in draft_layout.items():
        if draft_panel.frame.fixed_width is True or panel_is_dimensions_aware(draft_panel):
            no_resize_panel_keys.add(key)

    prev_no_resize_panel_keys = no_resize_panel_keys.copy()

    delta_width = None
    while True:
        layout_dims = ResizedLayoutDraftPanel.calc_table_layout_dims(
            dim_aware_layout,
            exclude_title=True,
        )
        delta_width = layout_dims.width - frame.dims.width \
            if has_width(frame.dims) else None

        pass
        if layout_dims == prev_layout_dims \
                and no_resize_panel_keys == prev_no_resize_panel_keys:
            break

        prev_layout_dims = layout_dims
        prev_no_resize_panel_keys = no_resize_panel_keys.copy()

        if not delta_width:
            break

        def _priority(
            el: tuple[int, tuple[str, DimensionsAwarePanel[AnyFrame]]]
        ) -> tuple[int | float, int | float, int, int]:
            i, (key, panel) = el

            panel_height: pyd.NonNegativeInt = panel.frame.dims.height \
                if has_height(panel.frame.dims) \
                and panel.frame.dims.height < panel.dims.height \
                and panel.frame.fixed_height \
                else panel.dims.height

            return (float('inf') if key in no_resize_panel_keys else panel_height,
                    float('inf') if key in no_resize_panel_keys else
                    (-panel.frame.dims.width if has_width(panel.frame.dims) else -float('inf')),
                    -panel.dims_if_cropped.width,
                    -i)

        panel_priority = [
            key for i, (key, panel) in sorted(
                enumerate(dim_aware_layout.items()), key=_priority, reverse=delta_width is not None
                and delta_width < 0)
        ]

        # print(f'layout_dims: {layout_dims}')
        # print(f'frame.dims: {frame.dims}')
        # print(f'delta_width: {delta_width}')
        # print(f'panel_priority: {panel_priority}')
        # for i, (key, panel) in enumerate(dim_aware_panels.items()):
        #     print(f'panel frame: {key}: {panel.frame}')
        #     print(f'_priority(({i}, ({key}, <panel>))): {_priority((i, (key, panel)))}')

        total_layout_subpanel_dims_if_cropped = (
            ResizedLayoutDraftPanel.total_subpanel_dims_if_cropped(
                dim_aware_layout,
                exclude_title=True,
            ))
        min_frame_width = 0 if total_layout_subpanel_dims_if_cropped.width <= len(
            dim_aware_layout) else 1
        # print(f'total_layout_subpanel_dims_if_cropped: '
        #       f'{total_layout_subpanel_dims_if_cropped}')
        # print(f'min_frame_width: {min_frame_width}')

        for key in panel_priority:
            cur_draft_panel = layout_panel.content[key]
            cur_dim_aware_panel = dim_aware_layout[key]

            frame_width = cur_dim_aware_panel.frame.dims.width
            frame_height = cur_dim_aware_panel.frame.dims.height
            draft_fixed_width = cur_draft_panel.frame.fixed_width
            draft_fixed_height = cur_draft_panel.frame.fixed_height

            if delta_width:
                frame_width = cur_dim_aware_panel.dims_if_cropped.width
                frame_width_delta = (-1) if delta_width > 0 else -delta_width
                frame_width = max(frame_width + frame_width_delta, min_frame_width)

                if draft_fixed_width is True and has_width(cur_draft_panel.frame.dims):
                    frame_width = min(frame_width, cur_draft_panel.frame.dims.width)

            new_panel_frame = Frame(
                dims=Dimensions(width=frame_width, height=frame_height),
                fixed_width=draft_fixed_width if has_width(cur_draft_panel.frame.dims) else False,
                fixed_height=draft_fixed_height,
            )
            if new_panel_frame != cur_dim_aware_panel.frame \
                    and cur_draft_panel.frame.fixed_width is not True:
                new_resized_panel = _create_new_resized_panel(
                    cur_draft_panel,
                    new_panel_frame,
                )

                prev_cropped_dims = cur_dim_aware_panel.dims_if_cropped
                new_cropped_dims = new_resized_panel.dims_if_cropped

                if key not in no_resize_panel_keys:
                    prev_frame_dims = cur_dim_aware_panel.frame.dims
                    if delta_width and delta_width > 0 \
                            and new_resized_panel.dims.width == cur_dim_aware_panel.dims.width:
                        if has_width(new_panel_frame.dims) and \
                                has_width(prev_frame_dims) and \
                                new_panel_frame.dims.width < prev_frame_dims.width:
                            no_resize_panel_keys.add(key)
                            break
                else:
                    if new_cropped_dims.width > prev_cropped_dims.width:
                        no_resize_panel_keys.remove(key)

                if new_cropped_dims == prev_cropped_dims:
                    continue

                dim_aware_layout[key] = new_resized_panel
                break

    dim_aware_layout = _tighten_panel_widths(dim_aware_layout)
    # TODO: In case outer frame is fixed width and wider than the outer
    #       panel dimensions, we need to expand the inner panels with
    #       flexible frame width, distributing the extra width among
    #       them.

    if delta_width is None or delta_width < 0:
        dim_aware_layout = _widen_inner_panels_to_make_room_for_titles(
            dim_aware_layout,
            draft_layout,
            extra_width=-delta_width if delta_width is not None else -1,
        )
    ret_panel = ResizedLayoutDraftPanel.create_from_draft_panel(layout_panel, dim_aware_layout)
    return ret_panel  # pyright: ignore [reportReturnType]
