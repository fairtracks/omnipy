from abc import abstractmethod
from copy import copy
from enum import Enum
from functools import cached_property
import html
import re
from textwrap import dedent
from typing import Callable, ClassVar, Generic, Iterable, NamedTuple

import rich.console
import rich.segment
import rich.terminal_theme

from omnipy.data._display.config import HorizontalOverflowMode, VerticalOverflowMode
from omnipy.data._display.dimensions import Dimensions, has_height, has_width
from omnipy.data._display.panel.base import FrameT, OutputVariant
from omnipy.data._display.panel.draft.base import ContentT
from omnipy.data._display.panel.helpers import (calculate_bg_color_triplet_from_color_style,
                                                calculate_fg_color_triplet_from_color_style,
                                                ForceAutodetect)
from omnipy.data._display.panel.styling.base import PanelT, StylizedMonospacedPanel
from omnipy.util.helpers import extract_newline, max_newline_stripped_width, strip_and_split_newline


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

        if self._output.config.horizontal_overflow_mode is HorizontalOverflowMode.WORD_WRAP:
            self._crop_dims = self._frame.dims
        else:
            self._crop_dims = self._output.input_panel_cropped_dims

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


class StylizedItem(NamedTuple):
    span_start: str
    content: str
    span_end: str


class CroppingOutputVariant(
        CommonOutputVariant[PanelT, ContentT, FrameT],
        Generic[PanelT, ContentT, FrameT],
):
    def _crop_top_level_html(self, html: str) -> str:
        return re.sub(
            r'(<code[^>]*>)([\S\s]*)(</code>)',
            self._manage_top_level_html_matches,
            html,
        )

    def _manage_top_level_html_matches(self, matches: re.Match) -> str:
        start_code_tag = matches.group(1)
        code_content = matches.group(2)
        end_code_tag = matches.group(3)

        return start_code_tag + self._crop_html_code(code_content) + end_code_tag

    def _crop_html_code(self, code_html: str) -> str:
        return self._crop_stylized_output_common(
            code_html,
            split_regexp=r'(<span[^>]*>[^<]*</span>)',
            findall_regexp=r'^(<span[^>]*>)?([^<]*)(</span>)?$',
            unescape_html=True,
        )

    def _crop_stylized_text(self, code_html: str) -> str:
        return self._crop_stylized_output_common(
            code_html,
            split_regexp=r'((?:\x1b\[[^m]*m)*[^\x1b]*(?:\x1b\[[^m]*m)*)',
            findall_regexp=r'^((?:\x1b\[[^m]*m)*)([^\x1b]*)((?:\x1b\[[^m]*m)*)$',
            unescape_html=False,
        )

    def _crop_stylized_output_common(
        self,
        output: str,
        split_regexp: str,
        findall_regexp: str,
        unescape_html: bool,
    ) -> str:
        lines = self._split_to_lines_and_crop_virtually(output)
        cropped_lines = []
        text_lines = []
        items_per_line: list[list[StylizedItem]] = []

        for line in lines:
            split_line = re.split(split_regexp, line)

            items: list[StylizedItem] = []
            for item_str in split_line:
                items.append(StylizedItem(*re.findall(findall_regexp, item_str)[0]))

            items_per_line.append(items)
            text_line = ''.join(item.content for item in items)

            if unescape_html:
                text_line = html.unescape(text_line)

            text_lines.append(text_line)

        text_lines, _exited_early = self._crop_lines_horizontally(text_lines)

        for i, cropped_text_line in enumerate(text_lines):
            cropped_line = ''
            items = items_per_line[i]

            if unescape_html:
                cropped_text_line = html.escape(cropped_text_line)

            for item in items:
                cropped_content = ''
                for char in item.content:
                    if _exited_early:  # e.g. returned ['…\n']
                        stripped_line, newline = strip_and_split_newline(cropped_text_line)
                        # Extracts the content of the cropped text line to reuse styling
                        cropped_content += stripped_line
                        # Retains newline to allow matching with remaining chars/items
                        cropped_text_line = newline
                    if cropped_text_line.startswith(char):
                        cropped_content += char
                        cropped_text_line = cropped_text_line[1:]

                cropped_line += item.span_start + cropped_content + item.span_end
            cropped_lines.append(cropped_line)

        return ''.join(cropped_lines)

    def _crop_text(self, output: str) -> str:
        if self._output_mode is OutputMode.PLAIN:
            lines = self._split_to_lines_and_crop_virtually(output)
            lines, _exited_early = self._crop_lines_horizontally(lines)
            return ''.join(lines)
        else:
            return self._crop_stylized_text(output)

    def _split_to_lines_and_crop_virtually(self, output):
        lines = output.splitlines(keepends=True)
        uncropped_height = len(lines)
        return self._crop_lines_vertically(
            lines,
            uncropped_height,
            self._crop_dims,
        )

    def _crop_lines_horizontally(self, lines: list[str]) -> tuple[list[str], bool]:
        uncropped_width = max_newline_stripped_width(lines)
        exited_early = False

        cropped_lines = []
        for line in lines:
            cropped_line, more = \
                self._crop_line_horizontally(line, uncropped_width, self._crop_dims)
            cropped_lines.append(cropped_line)
            if not more:
                exited_early = True
                break

        return cropped_lines, exited_early

    @abstractmethod
    def _crop_lines_vertically(
        self,
        lines: list[str],
        uncropped_height: int,
        crop_dims: Dimensions,
    ) -> list[str]:
        ...

    @abstractmethod
    def _crop_line_horizontally(
        self,
        line: str,
        uncropped_width: int,
        crop_dims: Dimensions,
    ) -> tuple[str, bool]:
        ...

    @cached_property
    def terminal(self) -> str:
        return self._crop_text(self._terminal)

    @cached_property
    def html_tag(self) -> str:
        return self._crop_top_level_html(self._html_tag)

    @cached_property
    def html_page(self) -> str:
        return self._crop_top_level_html(self._html_page)


class TextCroppingOutputVariant(
        CroppingOutputVariant[PanelT, ContentT, FrameT],
        Generic[PanelT, ContentT, FrameT],
):
    def _crop_lines_vertically(
        self,
        lines: list[str],
        uncropped_height: int,
        crop_dims: Dimensions,
    ) -> list[str]:
        if not has_height(crop_dims) or uncropped_height <= crop_dims.height:
            return lines

        match self._config.vertical_overflow_mode:
            case VerticalOverflowMode.CROP_BOTTOM:
                return lines[:crop_dims.height]
            case VerticalOverflowMode.CROP_TOP:
                return lines[-crop_dims.height:]

    def _crop_line_horizontally(
        self,
        line: str,
        uncropped_width: int,
        crop_dims: Dimensions,
    ) -> tuple[str, bool]:
        line_content, newline = strip_and_split_newline(line)
        # To enforce cropping at the "resize" stage, e.g.
        # crop_content_for_tab_and_double_width_chars(), even in the
        # presence of StylizedMonospacedPanel._apply_console_newline_hack()
        if has_width(crop_dims) and len(line_content) > crop_dims.width:
            return line_content[:crop_dims.width] + newline, True

        return line, True


class TableCroppingOutputVariant(
        CroppingOutputVariant[PanelT, ContentT, FrameT],
        Generic[PanelT, ContentT, FrameT],
):
    def _crop_lines_vertically(
        self,
        lines: list[str],
        uncropped_height: int,
        crop_dims: Dimensions,
    ) -> list[str]:
        if not has_height(crop_dims) or uncropped_height <= crop_dims.height:
            return lines

        if self._frame.dims.height == 0:
            return []

        return lines[:crop_dims.height - 1] + [lines[-1]]

    def _crop_line_horizontally(
        self,
        line: str,
        uncropped_width: int,
        crop_dims: Dimensions,
    ) -> tuple[str, bool]:
        # Checks if width or height is 1, and if so returns '…' or '' (depending on uncropped_width)
        # Code is placed only here and not in _crop_lines_vertically to simplify logic for cropping
        # of HTML text
        if (has_width(crop_dims) and crop_dims.width == 1
                or has_height(crop_dims) and crop_dims.height == 1):
            newline = extract_newline(line)
            if uncropped_width >= 1:
                return '…' + newline, False
            else:
                return '' + newline, False

        if not has_width(crop_dims) or uncropped_width <= crop_dims.width:
            return line, True

        line_stripped, newline = strip_and_split_newline(line)
        line_stripped_and_cropped = line_stripped[:crop_dims.width - 1] + line_stripped[-1:]
        return line_stripped_and_cropped + newline, True
