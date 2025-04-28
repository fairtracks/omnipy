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
    @pyd.validator('content', pre=True)
    def resize_panels_to_fit_frame(  # noqa: C901
        cls,
        content: Layout[DraftPanel],
        values: dict[str, Any],
    ) -> Layout[DimensionsAwarePanel[AnyFrame]]:
        dim_aware_panels: dict[
            str, DimensionsAwarePanel[AnyFrame]] = content.render_until_dimensions_aware()
        dim_aware_layout: Layout[DimensionsAwarePanel[AnyFrame]]
        prev_layout_dims: DimensionsWithWidthAndHeight | None = None

        no_resize_panel_keys: set[str] = set()
        for key, draft_panel in content.items():
            if draft_panel.frame.fixed_width is True or panel_is_dimensions_aware(draft_panel):
                no_resize_panel_keys.add(key)

        prev_no_reflow_panel_keys = no_resize_panel_keys.copy()

        while True:
            dim_aware_layout = Layout(**dim_aware_panels)
            layout_dims = cls._calc_table_layout_dims(dim_aware_layout)
            if layout_dims == prev_layout_dims \
                    and no_resize_panel_keys == prev_no_reflow_panel_keys:
                break

            prev_layout_dims = layout_dims
            prev_no_reflow_panel_keys = no_resize_panel_keys.copy()

            frame_dims = cast(Frame, values['frame']).dims
            delta_width = layout_dims.width - frame_dims.width \
                if has_width(frame_dims) else None
            delta_height = max(layout_dims.height - frame_dims.height, 0) \
                if has_height(frame_dims) else None

            if not (delta_width or delta_height):
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

            print(f'layout_dims: {layout_dims}')
            print(f'frame_dims: {frame_dims}')
            print(f'delta_width: {delta_width}')
            print(f'delta_height: {delta_height}')
            print(f'panel_priority: {panel_priority}')
            for i, (key, panel) in enumerate(dim_aware_panels.items()):
                print(f'panel frame: {key}: {panel.frame}')
                print(f'_priority(({i}, ({key}, <panel>))): {_priority((i, (key, panel)))}')

            total_layout_subpanel_dims_if_cropped = cls.total_subpanel_dims_if_cropped(
                dim_aware_layout)
            min_frame_width = 0 if total_layout_subpanel_dims_if_cropped.width <= len(
                dim_aware_panels) else 1
            print(f'total_layout_subpanel_dims_if_cropped: {total_layout_subpanel_dims_if_cropped}')
            print(f'min_frame_width: {min_frame_width}')

            for key in panel_priority:
                draft_panel = content[key]

                frame_width = dim_aware_panels[key].frame.dims.width
                frame_height = dim_aware_panels[key].frame.dims.height
                draft_fixed_width = draft_panel.frame.fixed_width
                draft_fixed_height = draft_panel.frame.fixed_height

                if delta_width:
                    frame_width = cls._panel_dims_if_cropped(dim_aware_panels[key]).width
                    frame_width_delta = (-1) if delta_width > 0 else -delta_width
                    frame_width = max(frame_width + frame_width_delta, min_frame_width)

                    if draft_fixed_width is True and has_width(draft_panel.frame.dims):
                        frame_width = min(frame_width, draft_panel.frame.dims.width)

                if delta_height:
                    frame_height = cls._panel_dims_if_cropped(dim_aware_panels[key]).height
                    frame_height_delta = -delta_height

                    if not (frame_height_delta < 0
                            and frame_height < total_layout_subpanel_dims_if_cropped.height):
                        if frame_height >= -frame_height_delta:
                            frame_height += frame_height_delta

                        if draft_fixed_height is True and has_height(draft_panel.frame.dims):
                            frame_height = min(frame_height, draft_panel.frame.dims.height)

                new_panel_frame = Frame(
                    dims=Dimensions(width=frame_width, height=frame_height),
                    fixed_width=draft_fixed_width,
                    fixed_height=draft_fixed_height,
                )
                if new_panel_frame != dim_aware_panels[key].frame and not panel_is_dimensions_aware(
                        draft_panel):
                    new_draft_panel = draft_panel.__class__(
                        content=draft_panel.content,
                        title=draft_panel.title,
                        frame=new_panel_frame,
                        constraints=draft_panel.constraints,
                        config=draft_panel.config,
                    )
                    resized_panel: DimensionsAwarePanel[
                        AnyFrame] = new_draft_panel.render_next_stage()

                    prev_cropped_dims = cls._panel_dims_if_cropped(dim_aware_panels[key])
                    new_cropped_dims = cls._panel_dims_if_cropped(resized_panel)

                    if key not in no_resize_panel_keys:
                        prev_frame_dims = dim_aware_panels[key].frame.dims
                        if delta_width and delta_width > 0 \
                                and resized_panel.dims.width == dim_aware_panels[key].dims.width:
                            if has_width(resized_panel.frame.dims) and \
                                    has_width(prev_frame_dims) and \
                                    resized_panel.frame.dims.width < prev_frame_dims.width:
                                no_resize_panel_keys.add(key)
                                break
                    else:
                        if new_cropped_dims.width > prev_cropped_dims.width:
                            no_resize_panel_keys.remove(key)

                    if new_cropped_dims == prev_cropped_dims:
                        continue

                    dim_aware_panels[key] = resized_panel
                    break

        for key, panel in dim_aware_panels.items():
            frame = Frame(
                Dimensions(
                    width=min(panel.frame.dims.width, panel.dims.width)
                    if panel.frame.dims.width is not None else None,
                    height=min(panel.frame.dims.height, panel.dims.height)
                    if panel.frame.dims.height is not None else None,
                ))
            if frame != panel.frame:
                dim_aware_layout[key] = \
                    dataclasses.replace(panel, frame=frame)  # type: ignore[arg-type]

        return dim_aware_layout

    @staticmethod
    @cache
    def _panel_dims_if_cropped(
            panel: DimensionsAwarePanel[AnyFrame]) -> DimensionsWithWidthAndHeight:
        return panel.dims_if_cropped

    @staticmethod
    @cache
    def total_subpanel_dims_if_cropped(
            layout: Layout[DimensionsAwarePanel[AnyFrame]]) -> DimensionsWithWidthAndHeight:
        return Dimensions(
            width=sum(
                ResizedLayoutDraftPanel._panel_dims_if_cropped(panel).width
                for panel in layout.values()),
            height=max((ResizedLayoutDraftPanel._panel_dims_if_cropped(panel).height
                        for panel in layout.values()),
                       default=0))

    @classmethod
    def _calc_table_layout_dims(
            cls, layout: Layout[DimensionsAwarePanel[AnyFrame]]) -> DimensionsWithWidthAndHeight:
        if len(layout) > 0:
            total_subpanel_dims = cls.total_subpanel_dims_if_cropped(layout)
            return Dimensions(
                width=total_subpanel_dims.width + len(layout) * 3 + 1,
                height=total_subpanel_dims.height + 2,
            )
        else:
            return Dimensions(width=0, height=1)

    @cached_property
    @override
    def dims(self) -> Dimensions[pyd.NonNegativeInt, pyd.NonNegativeInt]:
        return self._calc_table_layout_dims(self.content)

    @cached_property
    def _content_lines(self) -> list[str]:
        raise ShouldNotOccurException()

    def render_next_stage(self) -> 'DimensionsAwarePanel[FrameT]':
        from omnipy.data._display.panel.styling.layout import StylizedLayoutPanel
        return StylizedLayoutPanel(self)
