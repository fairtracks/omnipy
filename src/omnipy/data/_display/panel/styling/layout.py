from functools import cache, cached_property
from typing import cast, Generic, Iterable, Iterator

import pygments.token
import rich.align
import rich.box
import rich.containers
import rich.style
import rich.table
import rich.text
from typing_extensions import override

from omnipy.data._display.config import ColorStyles, ConsoleColorSystem, LayoutDesign
from omnipy.data._display.dimensions import has_height, has_width
from omnipy.data._display.frame import AnyFrame
from omnipy.data._display.panel.base import (DimensionsAwarePanel,
                                             FrameInvT,
                                             FullyRenderedPanel,
                                             OutputVariant,
                                             panel_is_dimensions_aware)
from omnipy.data._display.panel.draft.base import DraftPanel
from omnipy.data._display.panel.draft.layout import (DimensionsAwarePanelLayoutMixin,
                                                     ResizedLayoutDraftPanel)
from omnipy.data._display.panel.draft.monospaced import MonospacedDraftPanel
from omnipy.data._display.panel.helpers import (calculate_bg_color_from_color_style,
                                                calculate_fg_color_from_color_style,
                                                ForceAutodetect,
                                                get_token_style_from_color_style)
from omnipy.data._display.panel.layout import Layout
from omnipy.data._display.panel.styling.base import StylizedMonospacedPanel, StylizedRichTypes
from omnipy.data._display.panel.styling.output import OutputMode, TableCroppingOutputVariant
from omnipy.util import _pydantic as pyd


class FullyRenderedPanelLayout(
        Layout[FullyRenderedPanel[AnyFrame]],
        DimensionsAwarePanelLayoutMixin,
):
    ...


@pyd.dataclass(
    init=False,
    frozen=True,
    config=pyd.ConfigDict(extra=pyd.Extra.forbid, validate_all=True, arbitrary_types_allowed=True),
)
class StylizedLayoutPanel(
        StylizedMonospacedPanel[ResizedLayoutDraftPanel[FrameInvT],
                                FullyRenderedPanelLayout,
                                FrameInvT],
        Generic[FrameInvT],
):
    def __init__(self, panel: DraftPanel[Layout, FrameInvT] | ResizedLayoutDraftPanel[FrameInvT]):
        if not panel_is_dimensions_aware(panel):
            resized_panel: ResizedLayoutDraftPanel[FrameInvT] = cast(
                ResizedLayoutDraftPanel[FrameInvT], panel.render_next_stage())
        else:
            resized_panel = panel

        super().__init__(
            cast(MonospacedDraftPanel[FullyRenderedPanelLayout, FrameInvT], resized_panel))

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
    ) -> FullyRenderedPanelLayout:
        return FullyRenderedPanelLayout(**content.render_fully())

    @staticmethod
    @cache
    def _get_stylized_layout_common(  # noqa: C901
        layout: FullyRenderedPanelLayout,
        frame: FrameInvT,
        layout_design: LayoutDesign,
        panel_title_at_top: bool,
        rich_overflow_method: rich.console.OverflowMethod | None,
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
        title_style = get_token_style_from_color_style(pygments.token.Token.Name.Decorator,
                                                       color_style)
        title_style._bgcolor = style_bg_color

        panels = list(layout[layout.grid[(0, i)]] for i in range(layout.grid.dims.width))
        my_rounded_box = rich.box.Box('╭─┬╮\n'
                                      '│ ││\n'
                                      '│ ││\n'
                                      '│ ││\n'
                                      '├─┼┤\n'
                                      '│ ││\n'
                                      '│ ││\n'
                                      '╰─┴╯\n')

        if has_height(frame.dims):
            layout_design_dims = layout.get_layout_design_dims(layout_design)
            table_cell_height = (
                frame.dims.height - layout_design_dims.extra_vertical_chars(num_vertical_panels=1))
        else:
            table_cell_height = layout.total_subpanel_outer_dims.height

        def _add_ellipsis_if_vertically_cropped(panel, title_lines):
            if len(panel.resized_title) > panel.title_height >= 1:
                last_title_line = title_lines[-1]
                if len(last_title_line) > 0:
                    # Add ellipsis if title height is cropped

                    max_title_width = (
                        max(panel.dims.width, panel.frame.dims.width)
                        if has_width(panel.frame.dims) else panel.dims.width)

                    title_lines[-1] = f'{last_title_line[:max_title_width-1]}…'

            return title_lines

        def _prepare_content(panels: Iterable[FullyRenderedPanel]) -> Iterator[rich.table.Table]:
            for panel in panels:
                content = rich.text.Text.from_ansi(panel.colorized.terminal, no_wrap=True)
                title: str | rich.text.Text = ''

                if panel.title:
                    title_lines = panel.resized_title[:panel.title_height]
                    title_lines = _add_ellipsis_if_vertically_cropped(panel, title_lines)

                    if title_lines:
                        full_panel_title_height = panel.title_height + panel.TITLE_BLANK_LINES
                    else:
                        full_panel_title_height = 0

                    def num_free_lines_for_title(
                        table_cell_height: int,
                        panel: DimensionsAwarePanel,
                    ) -> int:
                        return max(table_cell_height - panel.cropped_dims.height, 0)

                    free_lines_for_title = num_free_lines_for_title(table_cell_height, panel)
                    extra_blank_lines_if_title_at_bottom = max(
                        free_lines_for_title - full_panel_title_height, 0)
                    if panel.title_overlaps_panel:
                        panel_content_lines = table_cell_height - full_panel_title_height
                    else:
                        panel_content_lines = panel.cropped_dims.height

                    content_lines: list[rich.text.Text] | rich.containers.Lines = \
                        content.split('\n')

                    if len(content_lines) < panel_content_lines:
                        # rich.text.Text.from_ansi() might remove empty lines at the end.
                        # Add them back here
                        for _ in range(panel_content_lines - len(content_lines)):
                            content_lines.append(rich.text.Text(''))
                    elif len(content_lines) > panel_content_lines:
                        # Crop content_lines if too high
                        content_lines = content_lines[:panel_content_lines]

                    linesep_text = rich.text.Text('\n', no_wrap=True)
                    content = linesep_text.join(content_lines)

                    if title_lines:
                        if panel_title_at_top:
                            title_with_space = '\n'.join(title_lines
                                                         + [''] * (panel.TITLE_BLANK_LINES))
                        else:
                            num_blank_lines = (
                                panel.TITLE_BLANK_LINES + extra_blank_lines_if_title_at_bottom)
                            title_with_space = '\n'.join([''] * num_blank_lines + title_lines)

                        title = rich.text.Text(
                            title_with_space,
                            style=title_style,
                            no_wrap=True,
                            justify='center',
                            overflow='ellipsis',  # Titles are always cropped with ellipsis
                        )

                content_table = rich.table.Table(
                    show_header=True if title and panel_title_at_top else False,
                    show_footer=True if title and not panel_title_at_top else False,
                    box=None,
                    padding=(0, 0),
                )

                if panel.frame.fixed_width and has_width(panel.frame.dims):
                    column_width = panel.frame.dims.width
                else:
                    column_width = None

                if title:
                    if panel_title_at_top:
                        content_table.add_column(header=title, width=column_width)
                    else:
                        content_table.add_column(footer=title, width=column_width)
                else:
                    content_table.add_column(width=column_width)

                content_table.add_row(content)

                yield content_table

        table = rich.table.Table(
            show_header=False,
            box=my_rounded_box,
            style=table_style,
            footer_style=title_style,
        )
        table.add_row(*(x for x in _prepare_content(panels)), style=table_style)

        return table

    @override
    def _stylized_content_terminal_impl(self) -> StylizedRichTypes:
        return self._get_stylized_layout_common(
            layout=self.content,
            frame=self.frame,
            layout_design=self.config.layout_design,
            panel_title_at_top=self.config.panel_title_at_top,
            rich_overflow_method=self.rich_overflow_method,
            console_color_system=self.config.console_color_system,
            color_style=self.config.color_style,
            transparent_background=self.config.transparent_background,
            force_autodetect_bg_color=ForceAutodetect.NEVER,
        )

    @override
    def _stylized_content_html_impl(self) -> StylizedRichTypes:
        return self._get_stylized_layout_common(
            layout=self.content,
            frame=self.frame,
            layout_design=self.config.layout_design,
            panel_title_at_top=self.config.panel_title_at_top,
            rich_overflow_method=self.rich_overflow_method,
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
