from abc import abstractmethod
from copy import copy
from enum import Enum
from functools import cached_property
import re
from textwrap import dedent
from typing import Callable, ClassVar, Generic, Iterable

import rich.console
import rich.segment
import rich.terminal_theme

from omnipy.data._display.config import VerticalOverflowMode
from omnipy.data._display.panel.base import FrameT, OutputVariant
from omnipy.data._display.panel.draft.base import ContentT
from omnipy.data._display.panel.helpers import (calculate_bg_color_triplet_from_color_style,
                                                calculate_fg_color_triplet_from_color_style,
                                                ForceAutodetect)
from omnipy.data._display.panel.styling.base import PanelT, StylizedMonospacedPanel


class OutputMode(str, Enum):
    PLAIN = 'plain'
    BW_STYLIZED = 'bw_stylized'
    COLORIZED = 'colorized'


class CommonOutputVariant(OutputVariant, Generic[PanelT, ContentT, FrameT]):
    _CSS_COLOR_STYLE_TEMPLATE_FG_AND_BG: ClassVar[str] = ('color: {foreground}; '
                                                          'background-color: {background}; ')

    _CSS_COLOR_STYLE_TEMPLATE_FG_ONLY: ClassVar[str] = 'color: {foreground}; '

    _CSS_FONT_FAMILIES_TEMPLATE: ClassVar[str] = 'font-family: {font_family_str}; '
    _CSS_FONT_SIZE_TEMPLATE: ClassVar[str] = 'font-size: {font_size}px; '
    _CSS_FONT_WEIGHT_TEMPLATE: ClassVar[str] = 'font-weight: {font_weight}; '
    _CSS_LINE_HEIGHT_TEMPLATE: ClassVar[str] = 'line-height: {line_height}; '

    _HTML_TAG_TEMPLATE: ClassVar[str] = ('<pre>'
                                         '<code style="'
                                         '{font_style}'
                                         '{color_style}">'
                                         '{code}'
                                         '</code>'
                                         '</pre>')

    _HTML_PAGE_TEMPLATE: ClassVar[str] = dedent("""\
        <!DOCTYPE html>
        <html>
          <head>
            <meta charset="UTF-8">
            <style>
              {{stylesheet}}
              body {{{{
                color: {{foreground}};
                background-color: {{background}};
              }}}}
            </style>
          </head>
          <body>
            {html_tag_template}
          </body>
        </html>
        """)

    def __init__(self,
                 output: 'StylizedMonospacedPanel[PanelT, ContentT, FrameT]',
                 output_mode: OutputMode) -> None:
        self._output = output
        self._config = output.config
        self._frame = output.frame
        self._output_mode = output_mode

    # Hacks to remove color and strip styles from the console record buffer, making use of
    # private methods in the rich library. These are needed to prevent the stylized output from
    # being displayed in the HTML output, as the library provides no other ways to do this.

    def _apply_filter_to_console_recording(
        self,
        console: rich.console.Console,
        filter_func: Callable[[list[rich.segment.Segment]], Iterable[rich.segment.Segment]],
    ) -> rich.console.Console:
        new_console = copy(console)
        with console._record_buffer_lock:
            new_console._record_buffer = \
                filter_func(console._record_buffer)  # type: ignore[assignment]
        return new_console

    def _remove_all_color_from_console_recording(
            self, console: rich.console.Console) -> rich.console.Console:
        return self._apply_filter_to_console_recording(console, rich.segment.Segment.remove_color)

    def _remove_styling_from_console_recording(
            self, console: rich.console.Console) -> rich.console.Console:
        return self._apply_filter_to_console_recording(console, rich.segment.Segment.strip_styles)

    # Terminal output

    def _prepare_terminal_console_according_to_output_mode(self) -> rich.console.Console:
        console_terminal = self._output._console_terminal

        if self._output_mode is OutputMode.BW_STYLIZED:
            return self._remove_all_color_from_console_recording(console_terminal)

        return console_terminal

    @property
    def _terminal(self) -> str:
        console = self._prepare_terminal_console_according_to_output_mode()
        plain_output = self._output_mode is OutputMode.PLAIN or console._color_system is None
        return console.export_text(clear=False, styles=not plain_output)

    # HTML output

    def _prepare_html_console_according_to_output_mode(self) -> rich.console.Console:
        console_html = self._output._console_html

        if self._output_mode is OutputMode.PLAIN:
            return self._remove_styling_from_console_recording(console_html)

        if self._output_mode is OutputMode.BW_STYLIZED:
            return self._remove_all_color_from_console_recording(console_html)

        return console_html

    def _prepare_css_font_style(self):
        font_style = ''

        if self._config.css_font_families:
            font_style += self._CSS_FONT_FAMILIES_TEMPLATE.format(font_family_str=', '.join(
                f"'{_}'" for _ in self._config.css_font_families))

        if self._config.css_font_size:
            font_style += self._CSS_FONT_SIZE_TEMPLATE.format(font_size=self._config.css_font_size)

        if self._config.css_font_weight:
            font_style += self._CSS_FONT_WEIGHT_TEMPLATE.format(
                font_weight=self._config.css_font_weight)

        if self._config.css_line_height:
            font_style += self._CSS_LINE_HEIGHT_TEMPLATE.format(
                line_height=self._config.css_line_height)

        return font_style

    def _prepare_html_tag_template(self):
        if self._output_mode == OutputMode.COLORIZED:
            if self._config.transparent_background:
                css_color_style = self._CSS_COLOR_STYLE_TEMPLATE_FG_ONLY
            else:
                css_color_style = self._CSS_COLOR_STYLE_TEMPLATE_FG_AND_BG
        else:
            css_color_style = ''

        html_tag_template = self._HTML_TAG_TEMPLATE.format(
            font_style=self._prepare_css_font_style(), color_style=css_color_style, code='{code}')

        return html_tag_template

    def _prepare_html_page_template(self):
        html_tag_template = self._HTML_TAG_TEMPLATE.format(
            font_style=self._prepare_css_font_style(),
            color_style='',
            code='{code}',
        )

        html_page_template = self._HTML_PAGE_TEMPLATE.format(html_tag_template=html_tag_template)

        return html_page_template

    def _prepare_color_theme_for_html(
            self, force_autodetect: ForceAutodetect) -> rich.terminal_theme.TerminalTheme:
        """
        Prepares the color theme for the HTML export, confusingly called a "terminal theme" in the
        rich library. The "terminal theme" is used to set the foreground and background colors for
        the HTML output, as well as converting from ANSI to RGB colors, if needed (for e.g.
        "ansi_dark" and "ansi_light" color styles).

        :param force_autodetect: Rule for when to force the auto-detection of background color,
            which sets the background color to black or bright white, depending on the luminance of
            the foreground color. ALWAYS forces the auto-detection, while NEVER disables it.
            IF_NO_BG_COLOR_IN_STYLE only forces the auto-detection if the background color is not
            set in the color style.

        :return: the "terminal theme" to use for the HTML export.
        """
        theme = rich.terminal_theme.DEFAULT_TERMINAL_THEME

        if self._output_mode is OutputMode.COLORIZED:
            theme = copy(theme)

            style_fg_color = calculate_fg_color_triplet_from_color_style(self._config.color_style)
            style_bg_color = calculate_bg_color_triplet_from_color_style(
                self._config.color_style,
                force_autodetect,
            )

            theme.foreground_color = style_fg_color
            if style_bg_color is not None:
                theme.background_color = style_bg_color

        return theme

    @property
    def _html_tag(self) -> str:
        console_html = self._prepare_html_console_according_to_output_mode()

        return console_html.export_html(
            theme=self._prepare_color_theme_for_html(
                force_autodetect=ForceAutodetect.IF_NO_BG_COLOR_IN_STYLE),
            clear=False,
            code_format=self._prepare_html_tag_template(),
            inline_styles=True)

    @property
    def _html_page(self) -> str:
        console = self._prepare_html_console_according_to_output_mode()

        if self._config.transparent_background:
            force_autodetect = ForceAutodetect.ALWAYS
        else:
            force_autodetect = ForceAutodetect.IF_NO_BG_COLOR_IN_STYLE

        return console.export_html(
            clear=False,
            theme=self._prepare_color_theme_for_html(force_autodetect=force_autodetect),
            code_format=self._prepare_html_page_template(),
        )


class CroppingOutputVariant(
        CommonOutputVariant[PanelT, ContentT, FrameT],
        Generic[PanelT, ContentT, FrameT],
):
    def _crop_matches(self, matches: re.Match) -> str:
        start_code_tag = matches.group(1)
        code_content = matches.group(2)
        end_code_tag = matches.group(3)

        return start_code_tag + self._crop(code_content) + end_code_tag

    def _crop_html(self, html: str) -> str:
        return re.sub(
            r'(<code[^>]*>)([\S\s]*)(</code>)',
            self._crop_matches,
            html,
            re.MULTILINE,
        )

    @abstractmethod
    def _crop(self, output: str) -> str:
        ...

    @cached_property
    def terminal(self) -> str:
        return self._crop(self._terminal)

    @cached_property
    def html_tag(self) -> str:
        return self._crop_html(self._html_tag)

    @cached_property
    def html_page(self) -> str:
        return self._crop_html(self._html_page)


class VerticalTextCroppingOutputVariant(
        CroppingOutputVariant[PanelT, ContentT, FrameT],
        Generic[PanelT, ContentT, FrameT],
):
    def _crop(self, output: str) -> str:
        if self._frame.dims.height is None:
            return output

        lines = output.splitlines(keepends=True)
        if len(lines) <= self._frame.dims.height:
            return output

        match self._config.vertical_overflow_mode:
            case VerticalOverflowMode.CROP_BOTTOM:
                return ''.join(lines[:self._frame.dims.height])
            case VerticalOverflowMode.CROP_TOP:
                return ''.join(lines[-self._frame.dims.height:])


class TableCroppingOutputVariant(
        CroppingOutputVariant[PanelT, ContentT, FrameT],
        Generic[PanelT, ContentT, FrameT],
):
    def _crop(self, output: str) -> str:
        lines = output.splitlines(keepends=True)
        uncropped_width = max((len(line) for line in lines), default=0)
        uncropped_height = len(lines)

        if (uncropped_width > 1 and uncropped_height) and \
                (getattr(self._frame.dims, 'width') == 1
                 or getattr(self._frame.dims, 'height') == 1):
            return '…'

        if self._frame.dims.height is None:
            return output

        if len(lines) <= self._frame.dims.height:
            return output

        cropped_lines = lines[:self._frame.dims.height - 1] + [lines[-1]]
        return ''.join(cropped_lines)
