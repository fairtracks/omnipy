from functools import cache, cached_property
from typing import Generic

import rich.box
import rich.style
import rich.table
import rich.text
from typing_extensions import override

from omnipy.data._display.config import ColorStyles, ConsoleColorSystem
from omnipy.data._display.dimensions import has_width
from omnipy.data._display.layout import Layout
from omnipy.data._display.panel.base import (DimensionsAwarePanel,
                                             FrameT,
                                             FullyRenderedPanel,
                                             OutputVariant)
from omnipy.data._display.panel.draft.layout import ResizedLayoutDraftPanel
from omnipy.data._display.panel.helpers import (calculate_bg_color_from_color_style,
                                                calculate_fg_color_from_color_style,
                                                ForceAutodetect)
from omnipy.data._display.panel.styling.base import StylizedMonospacedPanel, StylizedRichTypes
from omnipy.data._display.panel.styling.output import OutputMode, TableCroppingOutputVariant
from omnipy.util import _pydantic as pyd


@pyd.dataclass(
    init=False,
    frozen=True,
    config=pyd.ConfigDict(extra=pyd.Extra.forbid, validate_all=True, arbitrary_types_allowed=True),
)
class StylizedLayoutPanel(
        StylizedMonospacedPanel[ResizedLayoutDraftPanel[FrameT], Layout, FrameT],
        Generic[FrameT],
):
    @pyd.validator('content', pre=True)
    def _copy_content(cls, content: Layout) -> Layout:
        return content.copy()

    # @cached_property
    # def _console_dimensions(self) -> DimensionsWithWidthAndHeight:
    #     console_dims = super()._console_dimensions
    #
    #     frame_dims = self.frame.dims
    #     if has_width(frame_dims) and frame_dims.width <= self.content.grid.dims.width:
    #         # Too small for the rich console to crop nicely, e.g.:
    #         # ┌┬┬┬
    #         # ││││
    #         # └┴┴┴
    #         # Instead, we set console width to #grid width + 1 and do the
    #         # cropping ourselves, in TableCroppingOutputVariant.
    #         #
    #         # EDIT: On second thought, perhaps cutting the edges is
    #         # better, as in indicates that the table has more columns...?
    #         #
    #         return Dimensions(width=self.content.grid.dims.width + 1, height=console_dims.height)
    #     else:
    #         return console_dims

    @pyd.validator('content', pre=True)
    def render_panels_fully(
        cls,
        content: Layout[DimensionsAwarePanel],
    ) -> Layout[FullyRenderedPanel]:
        return Layout(**content.render_fully())

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

        table = rich.table.Table(show_header=False, box=rich.box.ROUNDED, style=table_style)
        keys = list(layout.grid[(0, i)] for i in range(layout.grid.dims.width))
        strings = (
            rich.text.Text.from_ansi(layout[key].colorized.terminal, no_wrap=True) for key in keys)

        for key in keys:
            panel = layout[key]
            if panel.frame.fixed_width and has_width(panel.frame.dims):
                column_width = panel.frame.dims.width
            else:
                column_width = None
            table.add_column(width=column_width)

        table.add_row(*strings, style=table_style)

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
    @override
    def plain(self) -> OutputVariant:
        return TableCroppingOutputVariant(self, OutputMode.PLAIN)

    @cached_property
    @override
    def bw_stylized(self) -> OutputVariant:
        return TableCroppingOutputVariant(self, OutputMode.BW_STYLIZED)

    @cached_property
    @override
    def colorized(self) -> OutputVariant:
        return TableCroppingOutputVariant(self, OutputMode.COLORIZED)
