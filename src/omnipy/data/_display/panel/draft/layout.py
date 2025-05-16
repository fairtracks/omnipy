from collections import defaultdict
import dataclasses
from functools import cache, cached_property
from typing import Any, cast, Generic

from typing_extensions import override

from omnipy.data._display.dimensions import (Dimensions,
                                             DimensionsWithWidthAndHeight,
                                             has_height,
                                             has_width)
from omnipy.data._display.frame import AnyFrame, Frame
from omnipy.data._display.layout import Layout
from omnipy.data._display.panel.base import DimensionsAwarePanel, FrameT, panel_is_dimensions_aware
from omnipy.data._display.panel.draft.base import DraftPanel
from omnipy.data._display.panel.draft.monospaced import MonospacedDraftPanel
from omnipy.shared.exceptions import ShouldNotOccurException
import omnipy.util._pydantic as pyd


@pyd.dataclass(
    init=False, frozen=True, config=pyd.ConfigDict(extra=pyd.Extra.forbid, validate_all=True))
class ResizedLayoutDraftPanel(
        MonospacedDraftPanel[Layout[DimensionsAwarePanel[AnyFrame]], FrameT],
        Generic[FrameT],
):
    @classmethod
    def _create_new_resized_panel(
        cls,
        draft_panel_basis: DraftPanel,
        frame: Frame,
    ) -> DimensionsAwarePanel[AnyFrame]:
        new_draft_panel = draft_panel_basis.__class__(
            content=draft_panel_basis.content,
            title=draft_panel_basis.title,
            frame=frame,
            constraints=draft_panel_basis.constraints,
            config=draft_panel_basis.config,
        )
        return new_draft_panel.render_next_stage()

    @classmethod
    def _set_panel_heights(
        cls, frame: AnyFrame, dim_aware_panels: dict[str, DimensionsAwarePanel[AnyFrame]]
    ) -> dict[str, DimensionsAwarePanel[AnyFrame]]:

        per_panel_height = None

        if has_height(frame.dims):
            per_panel_height = frame.dims.height - 2
            per_panel_height = max(per_panel_height, 0)

        # print(f'per_panel_height: {per_panel_height}')

        for key, panel in dim_aware_panels.items():
            if per_panel_height is not None \
                    and not panel.frame.fixed_height:
                frame_fixed_height = False

                dim_aware_panels[key] = dataclasses.replace(
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

        return dim_aware_panels

    @classmethod
    def _tighten_panel_widths(
        cls, dim_aware_panels: dict[str, DimensionsAwarePanel[AnyFrame]]
    ) -> dict[str, DimensionsAwarePanel[AnyFrame]]:
        for key, panel in dim_aware_panels.items():
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
                dim_aware_panels[key] = \
                    dataclasses.replace(panel, frame=frame)  # type: ignore[arg-type]
        return dim_aware_panels

    @classmethod
    def _widen_inner_panels_to_make_room_for_titles(
        cls,
        dim_aware_panels: dict[str, DimensionsAwarePanel[AnyFrame]],
        content: Layout[DraftPanel],
        extra_width: int,
    ) -> dict[str, DimensionsAwarePanel[AnyFrame]]:
        title_width2cramped_panel_info: defaultdict[int, list[tuple[str, int]]] = defaultdict(list)

        for key, panel in dim_aware_panels.items():
            if panel.title_width > 0 \
                    and panel.frame.dims.width is not None \
                    and panel.frame.fixed_width is not True \
                    and cls._panel_dims_if_cropped(panel).width < panel.title_width:
                title_width2cramped_panel_info[panel.title_width].append(
                    (key, cls._panel_dims_if_cropped(panel).width))

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
            dim_aware_panel = dim_aware_panels[key]
            panel_width = cls._panel_dims_if_cropped(dim_aware_panel).width
            title_adjusted_frame = Frame(
                dims=Dimensions(
                    width=panel_width + width_addition,
                    height=dim_aware_panel.frame.dims.height,
                ),
                fixed_width=False,
                fixed_height=dim_aware_panel.frame.fixed_height,
            )
            dim_aware_panels[key] = cls._create_new_resized_panel(
                content[key],
                title_adjusted_frame,
            )
        return dim_aware_panels

    @pyd.validator('content', pre=True)
    def resize_panels_to_fit_frame(  # noqa: C901
        cls,
        content: Layout[DraftPanel],
        values: dict[str, Any],
    ) -> Layout[DimensionsAwarePanel[AnyFrame]]:
        frame = cast(AnyFrame, values['frame'])

        dim_aware_panels: dict[
            str, DimensionsAwarePanel[AnyFrame]] = content.render_until_dimensions_aware()
        dim_aware_panels = cls._set_panel_heights(frame, dim_aware_panels)
        dim_aware_panels = cls._tighten_panel_widths(dim_aware_panels)
        dim_aware_panels = cls._widen_inner_panels_to_make_room_for_titles(
            dim_aware_panels,
            content,
            extra_width=-1,
        )

        dim_aware_layout: Layout[DimensionsAwarePanel[AnyFrame]]
        prev_layout_dims: DimensionsWithWidthAndHeight | None = None

        no_resize_panel_keys: set[str] = set()
        for key, draft_panel in content.items():
            if draft_panel.frame.fixed_width is True or panel_is_dimensions_aware(draft_panel):
                no_resize_panel_keys.add(key)

        prev_no_resize_panel_keys = no_resize_panel_keys.copy()

        delta_width = None
        while True:
            dim_aware_layout = Layout(**dim_aware_panels)
            layout_dims = cls._calc_table_layout_dims(dim_aware_layout, exclude_title=True)
            delta_width = layout_dims.width - frame.dims.width \
                if has_width(frame.dims) else None

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
                        -cls._panel_dims_if_cropped(panel).width,
                        -i)

            panel_priority = [
                key for i, (key, panel) in sorted(
                    enumerate(dim_aware_panels.items()), key=_priority,
                    reverse=delta_width is not None and delta_width < 0)
            ]

            # print(f'layout_dims: {layout_dims}')
            # print(f'frame.dims: {frame.dims}')
            # print(f'delta_width: {delta_width}')
            # print(f'panel_priority: {panel_priority}')
            # for i, (key, panel) in enumerate(dim_aware_panels.items()):
            #     print(f'panel frame: {key}: {panel.frame}')
            #     print(f'_priority(({i}, ({key}, <panel>))): {_priority((i, (key, panel)))}')

            total_layout_subpanel_dims_if_cropped = cls.total_subpanel_dims_if_cropped(
                dim_aware_layout, exclude_title=True)
            min_frame_width = 0 if total_layout_subpanel_dims_if_cropped.width <= len(
                dim_aware_panels) else 1
            # print(f'total_layout_subpanel_dims_if_cropped: '
            #       f'{total_layout_subpanel_dims_if_cropped}')
            # print(f'min_frame_width: {min_frame_width}')

            for key in panel_priority:
                cur_draft_panel = content[key]
                cur_dim_aware_panel = dim_aware_panels[key]

                frame_width = cur_dim_aware_panel.frame.dims.width
                frame_height = cur_dim_aware_panel.frame.dims.height
                draft_fixed_width = cur_draft_panel.frame.fixed_width
                draft_fixed_height = cur_draft_panel.frame.fixed_height

                if delta_width:
                    frame_width = cls._panel_dims_if_cropped(cur_dim_aware_panel).width
                    frame_width_delta = (-1) if delta_width > 0 else -delta_width
                    frame_width = max(frame_width + frame_width_delta, min_frame_width)

                    if draft_fixed_width is True and has_width(cur_draft_panel.frame.dims):
                        frame_width = min(frame_width, cur_draft_panel.frame.dims.width)

                new_panel_frame = Frame(
                    dims=Dimensions(width=frame_width, height=frame_height),
                    fixed_width=draft_fixed_width
                    if has_width(cur_draft_panel.frame.dims) else False,
                    fixed_height=draft_fixed_height,
                )
                if new_panel_frame != cur_dim_aware_panel.frame \
                        and cur_draft_panel.frame.fixed_width is not True:
                    resized_panel = cls._create_new_resized_panel(
                        cur_draft_panel,
                        new_panel_frame,
                    )

                    prev_cropped_dims = cls._panel_dims_if_cropped(cur_dim_aware_panel)
                    new_cropped_dims = cls._panel_dims_if_cropped(resized_panel)

                    if key not in no_resize_panel_keys:
                        prev_frame_dims = cur_dim_aware_panel.frame.dims
                        if delta_width and delta_width > 0 \
                                and resized_panel.dims.width == cur_dim_aware_panel.dims.width:
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

                    dim_aware_panels[key] = resized_panel
                    break

        dim_aware_panels = cls._tighten_panel_widths(dim_aware_panels)
        # TODO: In case outer frame is fixed width and wider than the outer
        #       panel dimensions, we need to expand the inner panels with
        #       flexible frame width, distributing the extra width among
        #       them.

        if delta_width is None or delta_width < 0:
            dim_aware_panels = cls._widen_inner_panels_to_make_room_for_titles(
                dim_aware_panels,
                content,
                extra_width=-delta_width if delta_width is not None else -1,
            )

        return Layout(**dim_aware_panels)

    @staticmethod
    @cache
    def _panel_dims_if_cropped(
            panel: DimensionsAwarePanel[AnyFrame]) -> DimensionsWithWidthAndHeight:
        return panel.dims_if_cropped

    @staticmethod
    @cache
    def total_subpanel_dims_if_cropped(
        layout: Layout[DimensionsAwarePanel[AnyFrame]],
        exclude_title: bool,
    ) -> DimensionsWithWidthAndHeight:
        def _panel_dims_if_cropped(
                panel: DimensionsAwarePanel[AnyFrame]) -> DimensionsWithWidthAndHeight:
            panel_dims_cropped = ResizedLayoutDraftPanel._panel_dims_if_cropped(panel)

            if exclude_title:
                return panel_dims_cropped
            else:
                if panel.title_height > 0:
                    panel_dims_width = max(panel_dims_cropped.width, panel.title_width)
                else:
                    panel_dims_width = panel_dims_cropped.width

                panel_dims_height = panel_dims_cropped.height + panel.title_height_with_blank_lines
                if has_height(panel.frame.dims):
                    panel_dims_height = min(panel.frame.dims.height, panel_dims_height)

                return Dimensions(width=panel_dims_width, height=panel_dims_height)

        all_panel_dims = [_panel_dims_if_cropped(panel) for panel in layout.values()]
        return Dimensions(
            width=sum(panel_dims.width for panel_dims in all_panel_dims),
            height=max((panel_dims.height for panel_dims in all_panel_dims), default=0))

    @classmethod
    def _calc_table_layout_dims(
        cls,
        layout: Layout[DimensionsAwarePanel[AnyFrame]],
        exclude_title: bool,
    ) -> DimensionsWithWidthAndHeight:

        if len(layout) > 0:
            total_subpanel_dims = cls.total_subpanel_dims_if_cropped(
                layout,
                exclude_title=exclude_title,
            )
            return Dimensions(
                width=total_subpanel_dims.width + len(layout) * 3 + 1,
                height=total_subpanel_dims.height + 2,
            )
        else:
            return Dimensions(width=0, height=1)

    @cached_property
    @override
    def dims(self) -> Dimensions[pyd.NonNegativeInt, pyd.NonNegativeInt]:
        return self._calc_table_layout_dims(self.content, exclude_title=False)

    @cached_property
    def _content_lines(self) -> list[str]:
        raise ShouldNotOccurException()

    def render_next_stage(self) -> 'DimensionsAwarePanel[FrameT]':
        from omnipy.data._display.panel.styling.layout import StylizedLayoutPanel
        return StylizedLayoutPanel(self)
