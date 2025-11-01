from dataclasses import dataclass
from functools import cached_property, lru_cache
from typing import Any, cast, Generic, Iterator

import rich.align
import rich.box
import rich.containers
import rich.style
import rich.table
import rich.text
from typing_extensions import override

from omnipy.data._display.dimensions import has_height, has_width
from omnipy.data._display.layout.base import Layout, PanelDesignDims
from omnipy.data._display.panel.base import (DimensionsAwarePanel,
                                             OutputVariant,
                                             panel_is_dimensions_aware)
from omnipy.data._display.panel.draft.base import (DraftPanel,
                                                   FullyRenderedDraftPanel,
                                                   FullyRenderedDraftPanelLayout)
from omnipy.data._display.panel.draft.layout import ResizedLayoutDraftPanel
from omnipy.data._display.panel.draft.monospaced import MonospacedDraftPanel
from omnipy.data._display.panel.helpers import (calculate_bg_color_from_color_style,
                                                ForceAutodetect,
                                                get_token_style_from_color_style)
from omnipy.data._display.panel.styling.base import StylizedMonospacedPanel, StylizedRichTypes
from omnipy.data._display.panel.styling.output import OutputMode, TableCroppingOutputVariant
from omnipy.data._display.panel.typedefs import FrameInvT
from omnipy.shared.constants import (INFO_BASE_16_TOKEN,
                                     INFO_GENERAL_TOKEN,
                                     PANEL_TITLE_BASE_16_TOKEN,
                                     PANEL_TITLE_EXTRA_STYLE,
                                     PANEL_TITLE_GENERAL_TOKEN,
                                     TABLE_BORDER_BASE_16_TOKEN,
                                     TABLE_BORDER_GENERAL_TOKEN,
                                     TITLE_BLANK_LINES)
from omnipy.shared.enums.display import DisplayColorSystem, PanelDesign
from omnipy.util import _pydantic as pyd


@pyd.dataclass(
    init=False,
    frozen=True,
    config=pyd.ConfigDict(extra=pyd.Extra.forbid, validate_all=True, arbitrary_types_allowed=True),
)
class StylizedLayoutPanel(
        StylizedMonospacedPanel[ResizedLayoutDraftPanel[FrameInvT],
                                FullyRenderedDraftPanelLayout,
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
            cast(MonospacedDraftPanel[FullyRenderedDraftPanelLayout, FrameInvT], resized_panel))

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
    ) -> FullyRenderedDraftPanelLayout:
        return FullyRenderedDraftPanelLayout(**content.render_fully())

    @staticmethod
    @lru_cache(maxsize=1024)
    def _get_stylized_layout_common(  # noqa: C901
        outer_panel: 'StylizedLayoutPanel[FrameInvT]',
        color_system: DisplayColorSystem.Literals,  # Only used for hashing
        force_autodetect_bg_color: ForceAutodetect.Literals,
    ) -> rich.table.Table:
        styles = PanelElementStyles(outer_panel, force_autodetect_bg_color)
        outer_layout_panel_styler = OuterLayoutPanelStyler(outer_panel, styles)
        return outer_layout_panel_styler.style_outer_panel()

    @override
    def _stylized_content_terminal_impl(self) -> StylizedRichTypes:
        return self._get_stylized_layout_common(
            outer_panel=self,
            color_system=self.config.system,
            force_autodetect_bg_color=ForceAutodetect.NEVER,
        )

    @override
    def _stylized_content_html_impl(self) -> StylizedRichTypes:
        return self._get_stylized_layout_common(
            outer_panel=self,
            color_system=DisplayColorSystem.ANSI_RGB,
            force_autodetect_bg_color=ForceAutodetect.NEVER,
        )

    @cached_property
    def table_cell_height(self) -> int:
        table_cell_height = self.content.total_subpanel_outer_dims.height

        if has_height(self.frame.dims):
            panel_design_dims = PanelDesignDims.create(self.config.panel)
            frame_cropped_table_cell_height = (
                self.frame.dims.height
                - panel_design_dims.num_extra_vertical_chars(num_vertical_panels=1))
            table_cell_height = min(table_cell_height, frame_cropped_table_cell_height)

        return table_cell_height

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


@dataclass
class PanelElementStyles:
    title_style: rich.style.Style
    table_style: rich.style.Style
    info_style: rich.style.Style

    def __init__(
        self,
        outer_panel: 'StylizedLayoutPanel[FrameInvT]',
        force_autodetect_bg_color: ForceAutodetect.Literals,
    ) -> None:
        color_style = outer_panel.config.style

        if outer_panel.config.bg:
            style_bg_color = calculate_bg_color_from_color_style(
                color_style, force_autodetect=force_autodetect_bg_color)
        else:
            style_bg_color = None

        basic_title_style = get_token_style_from_color_style(PANEL_TITLE_BASE_16_TOKEN, color_style)
        if basic_title_style is rich.style.Style.null():
            basic_title_style = get_token_style_from_color_style(PANEL_TITLE_GENERAL_TOKEN,
                                                                 color_style)

        self.title_style = rich.style.Style(color=basic_title_style.color, bgcolor=style_bg_color)
        self.title_style += rich.style.Style.parse(PANEL_TITLE_EXTRA_STYLE)

        basic_table_style = get_token_style_from_color_style(TABLE_BORDER_BASE_16_TOKEN,
                                                             color_style)
        if basic_table_style is rich.style.Style.null():
            basic_table_style = get_token_style_from_color_style(TABLE_BORDER_GENERAL_TOKEN,
                                                                 color_style)
        self.table_style = rich.style.Style(color=basic_table_style.color, bgcolor=style_bg_color)

        basic_info_style = get_token_style_from_color_style(INFO_BASE_16_TOKEN, color_style)
        if basic_info_style is rich.style.Style.null():
            basic_info_style = get_token_style_from_color_style(INFO_GENERAL_TOKEN, color_style)

        self.info_style = (
            rich.style.Style(color=basic_info_style.color, bgcolor=style_bg_color)
            + rich.style.Style(italic=True))


class InnerPanelStyler:
    def __init__(
        self,
        inner_panel: FullyRenderedDraftPanel,
        table_cell_height: int,
        panel_title_at_top: bool,
        styles: PanelElementStyles,
    ):
        self._panel = inner_panel
        self._table_cell_height = table_cell_height
        self._panel_title_at_top = panel_title_at_top
        self._styles = styles

    def _add_ellipsis_to_title_if_vertically_cropped(self, title_lines: list[str]) -> list[str]:
        if len(self._panel.resized_title) > self._panel.title_height >= 1:
            last_title_line = title_lines[-1]
            if len(last_title_line) > 0:
                max_title_width = (
                    max(self._panel.dims.width, self._panel.frame.dims.width)
                    if has_width(self._panel.frame.dims) else self._panel.dims.width)

                # Add ellipsis if title height is cropped
                title_lines[-1] = f'{last_title_line[:max_title_width - 1]}…'

        return title_lines

    @cached_property
    def _title_lines(self) -> list[str]:
        title_lines = self._panel.resized_title[:self._panel.title_height]
        title_lines = self._add_ellipsis_to_title_if_vertically_cropped(title_lines)
        return title_lines

    @property
    def _full_panel_title_height(self) -> int:
        if self._title_lines:
            return self._panel.title_height + TITLE_BLANK_LINES
        else:
            return 0

    @property
    def _num_free_lines_for_title(self) -> int:
        return max((self._table_cell_height - self._panel.cropped_dims.height), 0)

    @property
    def _num_extra_blank_lines_if_title_at_bottom(self) -> int:
        return max((self._num_free_lines_for_title - self._full_panel_title_height), 0)

    @cached_property
    def _num_content_lines(self) -> int:
        if self._panel.title_overlaps_panel:
            return self._table_cell_height - self._full_panel_title_height
        else:
            return self._panel.cropped_dims.height

    @property
    def _frame_width_else_outer_dims_width(self) -> int | None:
        if has_width(self._panel.frame.dims):
            return self._panel.frame.dims.width
        else:
            return self._panel.outer_dims.width

    def _style_title(self) -> str | rich.text.Text:
        title: str | rich.text.Text = ''

        if self._title_lines:
            if self._panel_title_at_top:
                title_with_space = '\n'.join(self._title_lines + [''] * TITLE_BLANK_LINES)
            else:
                num_blank_lines = (
                    TITLE_BLANK_LINES + self._num_extra_blank_lines_if_title_at_bottom)
                title_with_space = '\n'.join(([''] * num_blank_lines) + self._title_lines)

            title = rich.text.Text(
                title_with_space,
                style=self._styles.title_style,
                no_wrap=True,
                justify='center',
                overflow='ellipsis',  # Titles are always cropped with ellipsis
            )

        return title

    def _style_and_crop_content(self) -> rich.text.Text:
        content = rich.text.Text.from_ansi(self._panel.colorized.terminal, no_wrap=True)

        content_lines: list[rich.text.Text] | rich.containers.Lines = \
            content.split('\n')

        if len(content_lines) < self._num_content_lines:
            # rich.text.Text.from_ansi() might remove empty lines at the end.
            # Add them back here
            for _ in range(self._num_content_lines - len(content_lines)):
                content_lines.append(rich.text.Text(''))

        elif len(content_lines) > self._num_content_lines:
            # Crop content_lines if too high
            content_lines = content_lines[:self._num_content_lines]

        linesep_text = rich.text.Text('\n', no_wrap=True)
        return linesep_text.join(content_lines)

    def style_inner_panel(self) -> rich.table.Table:
        styled_title = self._style_title()
        styled_and_cropped_content = self._style_and_crop_content()
        column_width = self._frame_width_else_outer_dims_width

        panel_title_at_top = self._panel_title_at_top
        content_table = rich.table.Table(
            show_header=True if styled_title and panel_title_at_top else False,
            show_footer=True if styled_title and not panel_title_at_top else False,
            box=None,
            padding=(0, 0),
        )

        add_column_kwargs: dict[str, Any] = dict(
            width=column_width,
            overflow='crop',
            justify=self._panel.config.justify,
        )

        if styled_title:
            if panel_title_at_top:
                content_table.add_column(header=styled_title, **add_column_kwargs)
            else:
                content_table.add_column(footer=styled_title, **add_column_kwargs)
        else:
            content_table.add_column(**add_column_kwargs)

        content_table.add_row(styled_and_cropped_content)

        return content_table


class OuterLayoutPanelStyler:
    def __init__(
        self,
        outer_panel: 'StylizedLayoutPanel[FrameInvT]',
        styles: PanelElementStyles,
    ):
        self._outer_panel = outer_panel
        self._styles = styles

    def style_outer_panel(self) -> rich.table.Table:
        assert self._outer_panel.config.panel in [PanelDesign.TABLE, PanelDesign.TABLE_SHOW_STYLE]
        return self._style_outer_panel_as_table()

    def _get_style_text(self) -> str:
        style_text_prefix = 'Style: '
        short_style_text = self._outer_panel.config.style
        full_style_text = style_text_prefix + short_style_text

        if len(full_style_text) > self._outer_panel.inner_cropped_dims.width:
            return short_style_text
        else:
            return full_style_text

    def style_color_style_line(self) -> rich.text.Text | None:
        if self._outer_panel.config.panel == PanelDesign.TABLE_SHOW_STYLE:
            return rich.text.Text(
                self._get_style_text(),
                style=self._styles.info_style,
                no_wrap=True,
                overflow='ellipsis',
                justify='right',
            )
        else:
            return None

    def _style_outer_panel_as_table(self) -> rich.table.Table:
        assert self._outer_panel.config.panel in [PanelDesign.TABLE, PanelDesign.TABLE_SHOW_STYLE]

        table = rich.table.Table(
            caption=self.style_color_style_line(),
            show_header=False,
            box=rich.box.ROUNDED,
            style=self._styles.table_style,
            footer_style=self._styles.title_style,
        )

        table.add_row(*(x for x in self._style_inner_panels()), style=self._styles.table_style)

        return table

    def _style_inner_panels(self) -> Iterator[rich.table.Table]:
        for inner_panel in self._outer_panel.content.grid.get_row(0):
            inner_panel_layout_props = InnerPanelStyler(
                inner_panel,
                self._outer_panel.table_cell_height,
                self._outer_panel.config.title_at_top,
                self._styles,
            )
            yield inner_panel_layout_props.style_inner_panel()
