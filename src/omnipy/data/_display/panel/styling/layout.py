from functools import cache, cached_property
from typing import Generic

import rich.box
import rich.style
import rich.table
import rich.text
from typing_extensions import override

from omnipy.data._display.config import ColorStyles, ConsoleColorSystem
from omnipy.data._display.dimensions import Dimensions, DimensionsWithWidthAndHeight
from omnipy.data._display.layout import Layout
from omnipy.data._display.panel.base import DimensionsAwarePanel, FrameT, OutputVariant
from omnipy.data._display.panel.draft.base import ContentT
from omnipy.data._display.panel.helpers import (calculate_bg_color_from_color_style,
                                                calculate_fg_color_from_color_style,
                                                ForceAutodetect)
from omnipy.data._display.panel.styling.base import StylizedPanel, StylizedRichTypes
from omnipy.data._display.panel.styling.output import CommonOutputVariant, OutputMode
from omnipy.util import _pydantic as pyd


class StylizedLayoutOutputVariant(CommonOutputVariant[ContentT, FrameT], Generic[ContentT, FrameT]):
    @cached_property
    def terminal(self) -> str:
        return self._terminal

    @cached_property
    def html_tag(self) -> str:
        return self._html_tag

    @cached_property
    def html_page(self) -> str:
        return self._html_page


@pyd.dataclass(
    init=False,
    frozen=True,
    config=pyd.ConfigDict(extra=pyd.Extra.forbid, validate_all=True, arbitrary_types_allowed=True),
)
class StylizedLayoutPanel(DimensionsAwarePanel[FrameT], StylizedPanel[Layout, FrameT]):
    @pyd.validator('content', pre=True)
    def _copy_content(cls, content: Layout) -> Layout:
        return content.copy()

    @cached_property
    @override
    def dims(self) -> Dimensions[pyd.NonNegativeInt, pyd.NonNegativeInt]:
        dimensions_aware_panels = self.content.render_until_dimensions_aware()
        if dimensions_aware_panels:
            return Dimensions(
                width=(sum(panel.dims.width for panel in dimensions_aware_panels.values())
                       + len(dimensions_aware_panels) * 3 + 1),
                height=max(panel.dims.height for panel in dimensions_aware_panels.values()) + 2,
            )
        else:
            return Dimensions(width=0, height=0)

    @override
    def _get_console_dimensions_from_content(self) -> DimensionsWithWidthAndHeight:
        return self.dims

    @staticmethod
    @cache
    def _get_stylized_layout_common(
        layout: Layout,
        console_color_system: ConsoleColorSystem,  # Only used for hashing
        color_style: ColorStyles,
        transparent_background: bool,
        force_autodetect_bg_color: ForceAutodetect,
    ) -> rich.table.Table:

        style_fg_color = calculate_fg_color_from_color_style(color_style)
        if transparent_background:
            style_bg_color = None
        else:
            style_bg_color = calculate_bg_color_from_color_style(
                color_style, force_autodetect=force_autodetect_bg_color)
        table_style = rich.style.Style(color=style_fg_color, bgcolor=style_bg_color)

        fully_rendered_panels = layout.render_fully()

        table = rich.table.Table(show_header=False, box=rich.box.ROUNDED, style=table_style)
        keys = (layout.grid[(0, i)] for i in range(layout.grid.dims.width))
        strings = (
            rich.text.Text.from_ansi(fully_rendered_panels[key].colorized.terminal) for key in keys)
        table.add_row(*strings)

        return table

    @override
    def _stylized_content_terminal_impl(self) -> StylizedRichTypes:
        return self._get_stylized_layout_common(
            layout=self.content,
            console_color_system=self.config.console_color_system,
            color_style=self.config.color_style,
            transparent_background=self.config.transparent_background,
            force_autodetect_bg_color=ForceAutodetect.NEVER,
        )

    @override
    def _stylized_content_html_impl(self) -> StylizedRichTypes:
        return self._get_stylized_layout_common(
            layout=self.content,
            console_color_system=ConsoleColorSystem.ANSI_RGB,
            color_style=self.config.color_style,
            transparent_background=self.config.transparent_background,
            force_autodetect_bg_color=ForceAutodetect.NEVER,
        )

    @cached_property
    def plain(self) -> OutputVariant:
        return StylizedLayoutOutputVariant(self, OutputMode.PLAIN)

    @cached_property
    def bw_stylized(self) -> OutputVariant:
        return StylizedLayoutOutputVariant(self, OutputMode.BW_STYLIZED)

    @cached_property
    def colorized(self) -> OutputVariant:
        return StylizedLayoutOutputVariant(self, OutputMode.COLORIZED)
