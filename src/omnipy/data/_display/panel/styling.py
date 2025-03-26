from copy import copy
from enum import Enum
from functools import cached_property
from io import StringIO
import re
from textwrap import dedent
from typing import Callable, ClassVar, Generic, Iterable, overload

import pygments.token
import rich.box
import rich.color
import rich.color_triplet
import rich.console
import rich.panel
import rich.segment
import rich.style
import rich.syntax
import rich.table
import rich.terminal_theme
import rich.text

from omnipy.data._display.config import (ConsoleColorSystem,
                                         HorizontalOverflowMode,
                                         VerticalOverflowMode)
from omnipy.data._display.dimensions import Dimensions, DimensionsWithWidthAndHeight
from omnipy.data._display.layout import Layout
from omnipy.data._display.panel.base import (FrameT,
                                             FullyRenderedPanel,
                                             OutputMode,
                                             OutputVariant,
                                             Panel,
                                             panel_is_fully_rendered)
from omnipy.data._display.panel.draft import ReflowedTextDraftPanel
import omnipy.util._pydantic as pyd


def extract_value_if_enum(conf_item: Enum | str) -> str:
    return conf_item.value if isinstance(conf_item, Enum) else conf_item


class StylizedMonospacedOutputVariant(OutputVariant):
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

    def __init__(self, output: 'SyntaxStylizedTextPanel', output_mode: OutputMode) -> None:
        self._output = output
        self._config = output.config
        self._color_style_name = extract_value_if_enum(self._config.color_style)
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

    # Vertical cropping methods for terminal and HTML output

    def _vertical_crop(self, text: str) -> str:
        if self._frame.dims.height is None:
            return text

        lines = text.splitlines(keepends=True)
        if len(lines) <= self._frame.dims.height:
            return text

        match self._config.vertical_overflow_mode:
            case VerticalOverflowMode.CROP_BOTTOM:
                return ''.join(lines[:self._frame.dims.height])
            case VerticalOverflowMode.CROP_TOP:
                return ''.join(lines[-self._frame.dims.height:])

    def _vertical_crop_matches(self, matches: re.Match) -> str:
        start_code_tag = matches.group(1)
        code_content = matches.group(2)
        end_code_tag = matches.group(3)

        return start_code_tag + self._vertical_crop(code_content) + end_code_tag

    def _vertical_crop_html(self, html: str) -> str:
        return re.sub(
            r'(<code[^>]*>)([\S\s]*)(</code>)',
            self._vertical_crop_matches,
            html,
            re.MULTILINE,
        )

    # Terminal output

    def _prepare_terminal_console_according_to_output_mode(self) -> rich.console.Console:
        console_terminal = self._output._console_terminal

        if self._output_mode is OutputMode.BW_STYLIZED:
            return self._remove_all_color_from_console_recording(console_terminal)

        return console_terminal

    @cached_property
    def terminal(self) -> str:
        console = self._prepare_terminal_console_according_to_output_mode()
        plain_output = self._output_mode is OutputMode.PLAIN or console._color_system is None
        text = console.export_text(clear=False, styles=not plain_output)
        return self._vertical_crop(text)

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

    def _calculate_fg_color(
            self, syntax_theme: rich.syntax.SyntaxTheme) -> rich.color_triplet.ColorTriplet:
        ANSI_FG_COLOR_MAP = {'ansi_light': 'black', 'ansi_dark': 'bright_white'}

        syntax_theme_fg_color = syntax_theme.get_style_for_token(pygments.token.Token).color

        if syntax_theme_fg_color is None and self._color_style_name in ANSI_FG_COLOR_MAP:
            syntax_theme_fg_color = rich.color.Color.parse(
                ANSI_FG_COLOR_MAP[self._color_style_name])

        # Currently, the rich library defaults to a black foreground color if the token color is not
        # set for a pygments style. However, this may change in the future, so we need to check for
        # this case defensively. All color styles currently defined for Omnipy should have a token
        # color set.
        assert syntax_theme_fg_color is not None

        return syntax_theme_fg_color.get_truecolor(foreground=True)

    def _calculate_bg_color(self,
                            syntax_theme: rich.syntax.SyntaxTheme,
                            style_fg_color: rich.color_triplet.ColorTriplet,
                            for_html_page: bool) -> rich.color_triplet.ColorTriplet | None:
        def _auto_detect_bw_background_color(
                style_fg_color: rich.color_triplet.ColorTriplet) -> rich.color.Color:
            """
            Auto-detects a black or bright white background color based on the luminance of the
            foreground color (i.e. whether the style is light or dark).
            """
            fg_luminance = sum(style_fg_color) / 3
            return rich.color.Color.parse('black' if fg_luminance > 127.5 else 'bright_white')

        syntax_theme_bg_color = syntax_theme.get_background_style().bgcolor

        # If the background color is not set in the theme, we need to auto-detect it as black or
        # bright white based on the luminance of the foreground color, to support both light and
        # dark color styles.
        #
        # In addition, a transparent background for a full HTML page output will in practice be a
        # bright white background, so we instead also autodetect a black or bright white background
        # color also in this case.
        if syntax_theme_bg_color is None \
                or (for_html_page and self._config.transparent_background):
            syntax_theme_bg_color = _auto_detect_bw_background_color(style_fg_color)

        if syntax_theme_bg_color is not None:
            return syntax_theme_bg_color.get_truecolor(foreground=False)
        else:
            return None

    def _prepare_color_theme(self, for_html_page: bool) -> rich.terminal_theme.TerminalTheme:
        """
        Prepares the color theme for the HTML export, confusingly called a "terminal theme" in the
        rich library. The "terminal theme" is used to set the foreground and background colors for
        the HTML output, as well as converting from ANSI to RGB colors, if needed (for e.g.
        "ansi_dark" and "ansi_light" color styles).

        :param for_html_page: if used for a full HTML page output, the background color is set to
                              black or bright white, depending on the luminance of the foreground
                              color.

        :return: the "terminal theme" to use for the HTML export.
        """
        theme = rich.terminal_theme.DEFAULT_TERMINAL_THEME

        if self._output_mode is OutputMode.COLORIZED:
            theme = copy(theme)

            syntax_theme = rich.syntax.Syntax.get_theme(self._color_style_name)
            style_fg_color = self._calculate_fg_color(syntax_theme)
            style_bg_color = self._calculate_bg_color(syntax_theme, style_fg_color, for_html_page)

            theme.foreground_color = style_fg_color
            if style_bg_color is not None:
                theme.background_color = style_bg_color

        return theme

    @cached_property
    def html_tag(self) -> str:
        console_html = self._prepare_html_console_according_to_output_mode()

        html = console_html.export_html(
            theme=self._prepare_color_theme(for_html_page=False),
            clear=False,
            code_format=self._prepare_html_tag_template(),
            inline_styles=True)
        html_cropped = self._vertical_crop_html(html)

        return html_cropped

    @cached_property
    def html_page(self) -> str:
        console = self._prepare_html_console_according_to_output_mode()

        html = console.export_html(
            clear=False,
            theme=self._prepare_color_theme(for_html_page=True),
            code_format=self._prepare_html_page_template(),
        )
        html_cropped = self._vertical_crop_html(html)

        return html_cropped


@pyd.dataclass(
    init=False,
    frozen=True,
    config=pyd.ConfigDict(extra=pyd.Extra.forbid, validate_all=True),
)
class SyntaxStylizedTextPanel(ReflowedTextDraftPanel[FrameT], Generic[FrameT]):
    @overload
    def __init__(self, content: ReflowedTextDraftPanel[FrameT]):
        ...

    @overload
    def __init__(self, content: str, frame=None, constraints=None, config=None):
        ...

    def __init__(self,
                 content: str | ReflowedTextDraftPanel[FrameT],
                 frame=None,
                 constraints=None,
                 config=None):
        if isinstance(content, ReflowedTextDraftPanel):
            assert frame is None
            assert constraints is None
            assert config is None

            str_content = content.content
            frame = content.frame
            constraints = content.constraints
            config = content.config
        else:
            str_content = content

        super().__init__(str_content, frame, constraints, config)

    @staticmethod
    def _clean_rich_style_caches():
        """
        Clears object-level caches of the Style class in the Rich library to ensure that the current
        color system is used to render the output. This is needed as the Style caches do not take
        the current color system into account.

        """

        # The cache of the '_add()' method is the main cache causing issues
        rich.style.Style._add.cache_clear()

        # However, we clean these caches as well to be sure
        rich.style.Style.get_html_style.cache_clear()
        rich.style.Style.clear_meta_and_links.cache_clear()

    def _get_stylized_content_common(self, remove_bg_color: bool) -> rich.console.RenderableType:
        style_name = extract_value_if_enum(self.config.color_style)
        lexer_name = extract_value_if_enum(self.config.language)
        word_wrap = self.config.horizontal_overflow_mode == HorizontalOverflowMode.WORD_WRAP

        # Workaround to remove the background color from the theme, as setting
        # background_color='default' (the official solution,
        # see https://github.com/Textualize/rich/issues/284#issuecomment-694947144)
        # does not work for HTML content.
        theme = rich.syntax.Syntax.get_theme(style_name)

        if remove_bg_color:
            theme._background_color = None  # type: ignore[attr-defined]
            theme._background_style = rich.style.Style()  # type: ignore[attr-defined]

        return rich.syntax.Syntax(
            self.content,
            lexer=lexer_name,
            theme=theme,
            # background_color='default' if self.config.transparent_background else None,
            word_wrap=word_wrap,
        )

    @cached_property
    def _stylized_content_terminal(self) -> rich.console.RenderableType:
        self._clean_rich_style_caches()

        if self.config.transparent_background \
                and self.config.console_color_system is ConsoleColorSystem.ANSI_RGB:
            return self._stylized_content_html
        else:
            return self._get_stylized_content_common(
                remove_bg_color=self.config.transparent_background)

    @cached_property
    def _stylized_content_html(self) -> rich.console.RenderableType:
        self._clean_rich_style_caches()

        return self._get_stylized_content_common(remove_bg_color=True)

    def _get_console_dimensions_from_content(self) -> DimensionsWithWidthAndHeight:
        if isinstance(self.content, ReflowedTextDraftPanel):
            return self.content.dims
        else:
            return ReflowedTextDraftPanel(self.content).dims

    @cached_property
    def _console_dimensions(self) -> DimensionsWithWidthAndHeight:
        console_width = self.frame.dims.width
        console_height = self.frame.dims.height

        if console_width is None or console_height is None:
            console_dims = self._get_console_dimensions_from_content()
            if console_width is None:
                console_width = console_dims.width
            if console_height is None:
                console_height = console_dims.height

    def _get_console_overload(self) -> rich.console.OverflowMethod | None:
        match (self.config.horizontal_overflow_mode):
            case HorizontalOverflowMode.ELLIPSIS:
                return 'ellipsis'
            case HorizontalOverflowMode.CROP:
                return 'crop'
            case HorizontalOverflowMode.WORD_WRAP:
                return None

    def _get_console_common(
        self,
        stylized_content: rich.console.RenderableType,
        console_color_system: ConsoleColorSystem,
    ) -> rich.console.Console:
        width, height = self._get_console_frame_width_and_height()

        console = rich.console.Console(
            file=StringIO(),
            width=self._console_dimensions.width,
            height=self._console_dimensions.height,
            color_system=console_color_system.value,
            record=True,
        )

        overflow = self._get_console_overload()
        soft_wrap = True if self.frame.dims.width is None else False
        console.print(stylized_content, overflow=overflow, soft_wrap=soft_wrap)

        return console

    @cached_property
    def _console_terminal(self) -> rich.console.Console:
        console_color_system = self.config.console_color_system

        if (self.config.transparent_background
                and console_color_system is ConsoleColorSystem.ANSI_RGB):
            return self._console_html

        return self._get_console_common(self._stylized_content_terminal, console_color_system)

    @cached_property
    def _console_html(self) -> rich.console.Console:
        # Color system is hard-coded to 'truecolor' for HTML output
        return self._get_console_common(
            self._stylized_content_html,
            console_color_system=ConsoleColorSystem.ANSI_RGB,
        )

    @cached_property
    def plain(self) -> OutputVariant:
        return StylizedMonospacedOutputVariant(self, OutputMode.PLAIN)

    @cached_property
    def bw_stylized(self) -> OutputVariant:
        return StylizedMonospacedOutputVariant(self, OutputMode.BW_STYLIZED)

    @cached_property
    def colorized(self) -> OutputVariant:
        return StylizedMonospacedOutputVariant(self, OutputMode.COLORIZED)

    @cached_property
    def _content_lines(self) -> list[str]:
        return self.plain.terminal.splitlines()


@pyd.dataclass(
    frozen=True,
    config=pyd.ConfigDict(extra=pyd.Extra.forbid, validate_all=True, arbitrary_types_allowed=True),
)
class StylizedLayoutPanel(SyntaxStylizedTextPanel[FrameT], Generic[FrameT]):
    layout: Layout = pyd.Field(default_factory=Layout)

    def __init__(self,
                 layout: Layout,
                 frame: object = None,
                 constraints: object = None,
                 config: object = None) -> None:
        object.__setattr__(self, 'layout', layout)
        super().__init__('', frame, constraints, config)

    @pyd.validator('layout', pre=True)
    def _copy_layout(cls, layout: Layout) -> Layout:
        return layout.copy()


    @cached_property
    def dims(self) -> Dimensions[pyd.NonNegativeInt, pyd.NonNegativeInt]:
        dimensions_aware_panels = self.layout.render_until_dimensions_aware()
        if dimensions_aware_panels:
            return Dimensions(
                width=(sum(panel.dims.width for panel in dimensions_aware_panels.values())
                       + len(dimensions_aware_panels) * 3 + 1),
                height=max(panel.dims.height for panel in dimensions_aware_panels.values()) + 2,
            )
        else:
            return Dimensions(width=0, height=0)

    # For now. Later refactor inheritance to remove this
    @cached_property
    def max_container_width_across_lines(self) -> pyd.NonNegativeInt:
        return 0

    def _get_console_dimensions_from_content(self) -> DimensionsWithWidthAndHeight:
        return self.dims

    def _get_stylized_content_common(self, remove_bg_color: bool) -> rich.console.RenderableType:
        fully_rendered_panels: dict[str, FullyRenderedPanel] = {}
        remaining_panels: dict[str, Panel] = self.layout.data.copy()

        while len(remaining_panels) > 0:
            newly_rendered_panels = {}
            for key, panel in remaining_panels.items():
                if panel_is_fully_rendered(panel):
                    fully_rendered_panels[key] = panel
                else:
                    newly_rendered_panels[key] = panel.render_next_stage()

            remaining_panels = newly_rendered_panels

        if fully_rendered_panels:
            self._init_dims = Dimensions(
                width=(sum(panel.dims.width for panel in fully_rendered_panels.values())
                       + len(fully_rendered_panels) * 3 + 1),
                height=max(panel.dims.height for panel in fully_rendered_panels.values()) + 2,
            )

        table = rich.table.Table(show_header=False, box=rich.box.ROUNDED)
        keys = (self.layout.grid[(0, i)] for i in range(self.layout.grid.dims.width))
        strings = (
            rich.text.Text.from_ansi(fully_rendered_panels[key].colorized.terminal) for key in keys)
        table.add_row(*strings)

        return table
