from copy import copy
from functools import cache, cached_property
from io import StringIO
import re
from textwrap import dedent
from typing import Callable, ClassVar, Iterable, overload, TypeAlias

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

from omnipy.data._display.config import (ColorStyles,
                                         ConsoleColorSystem,
                                         HorizontalOverflowMode,
                                         SyntaxLanguage,
                                         VerticalOverflowMode)
from omnipy.data._display.dimensions import Dimensions, DimensionsWithWidthAndHeight
from omnipy.data._display.frame import AnyFrame
from omnipy.data._display.layout import Layout
from omnipy.data._display.panel.base import OutputMode, OutputVariant
from omnipy.data._display.panel.draft import ReflowedTextDraftPanel
from omnipy.data._display.panel.helpers import (calculate_bg_color_from_color_style,
                                                calculate_bg_color_triplet_from_color_style,
                                                calculate_fg_color_from_color_style,
                                                calculate_fg_color_triplet_from_color_style,
                                                extract_value_if_enum,
                                                ForceAutodetect)
import omnipy.util._pydantic as pyd

StylizedRichTypes: TypeAlias = rich.syntax.Syntax | rich.panel.Panel | rich.table.Table


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

    @cached_property
    def html_tag(self) -> str:
        console_html = self._prepare_html_console_according_to_output_mode()

        html = console_html.export_html(
            theme=self._prepare_color_theme_for_html(
                force_autodetect=ForceAutodetect.IF_NO_BG_COLOR_IN_STYLE),
            clear=False,
            code_format=self._prepare_html_tag_template(),
            inline_styles=True)
        html_cropped = self._vertical_crop_html(html)

        return html_cropped

    @cached_property
    def html_page(self) -> str:
        console = self._prepare_html_console_according_to_output_mode()

        if self._config.transparent_background:
            force_autodetect = ForceAutodetect.ALWAYS
        else:
            force_autodetect = ForceAutodetect.IF_NO_BG_COLOR_IN_STYLE

        html = console.export_html(
            clear=False,
            theme=self._prepare_color_theme_for_html(force_autodetect=force_autodetect),
            code_format=self._prepare_html_page_template(),
        )
        html_cropped = self._vertical_crop_html(html)

        return html_cropped


@pyd.dataclass(
    init=False,
    frozen=True,
    config=pyd.ConfigDict(extra=pyd.Extra.forbid, validate_all=True),
)
class SyntaxStylizedTextPanel(ReflowedTextDraftPanel[AnyFrame]):
    @overload
    def __init__(self, content: ReflowedTextDraftPanel[AnyFrame]):
        ...

    @overload
    def __init__(self, content: str, frame=None, constraints=None, config=None):
        ...

    def __init__(self,
                 content: str | ReflowedTextDraftPanel[AnyFrame],
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

    @staticmethod
    @cache
    def _get_stylized_content_common(
        content: str,
        console_color_system: ConsoleColorSystem,  # Only used for hashing
        console_color_style: ColorStyles | str,
        language: SyntaxLanguage | str,
        horizontal_overflow_mode: HorizontalOverflowMode,
        remove_bg_color: bool,
    ) -> rich.syntax.Syntax:
        style_name = extract_value_if_enum(console_color_style)
        lexer_name = extract_value_if_enum(language)
        word_wrap = horizontal_overflow_mode == HorizontalOverflowMode.WORD_WRAP

        # Workaround to remove the background color from the theme, as setting
        # background_color='default' (the official solution,
        # see https://github.com/Textualize/rich/issues/284#issuecomment-694947144)
        # does not work for HTML content.
        theme = rich.syntax.Syntax.get_theme(style_name)

        if remove_bg_color:
            theme._background_color = None  # type: ignore[attr-defined]
            theme._background_style = rich.style.Style()  # type: ignore[attr-defined]

        return rich.syntax.Syntax(
            content,
            lexer=lexer_name,
            theme=theme,
            # background_color='default' if self.config.transparent_background else None,
            word_wrap=word_wrap,
        )

    @cached_property
    def _stylized_content_terminal(self) -> StylizedRichTypes:
        self._clean_rich_style_caches()

        return self._get_stylized_content_common(
            content=self.content,
            console_color_system=self.config.console_color_system,
            console_color_style=self.config.color_style,
            language=self.config.language,
            horizontal_overflow_mode=self.config.horizontal_overflow_mode,
            remove_bg_color=self.config.transparent_background,
        )

    @cached_property
    def _stylized_content_html(self) -> StylizedRichTypes:
        self._clean_rich_style_caches()

        return self._get_stylized_content_common(
            content=self.content,
            # Color system is hard-coded to 'truecolor' for HTML output
            console_color_system=ConsoleColorSystem.ANSI_RGB,
            console_color_style=self.config.color_style,
            language=self.config.language,
            horizontal_overflow_mode=self.config.horizontal_overflow_mode,
            # The HTML background color is set for the entire tag/page, so
            # we need to remove the background color for each element
            remove_bg_color=True)

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

        return Dimensions(width=console_width, height=console_height)

    @staticmethod
    @cache
    def _get_console_common(
        stylized_content: rich.console.RenderableType,
        console_width: int,
        console_height: int,
        frame_width: int | None,
        console_color_system: ConsoleColorSystem,
        horizontal_overflow_mode: HorizontalOverflowMode,
    ) -> rich.console.Console:
        def _map_horizontal_overflow_mode_to_console_overflow_method(
                horizontal_overflow_mode: HorizontalOverflowMode
        ) -> rich.console.OverflowMethod | None:
            match (horizontal_overflow_mode):
                case HorizontalOverflowMode.ELLIPSIS:
                    return 'ellipsis'
                case HorizontalOverflowMode.CROP:
                    return 'crop'
                case HorizontalOverflowMode.WORD_WRAP:
                    return None

        console = rich.console.Console(
            file=StringIO(),
            width=console_width,
            height=console_height,
            color_system=console_color_system.value,
            record=True,
        )

        overflow_method = _map_horizontal_overflow_mode_to_console_overflow_method(
            horizontal_overflow_mode)
        soft_wrap = True if frame_width is None else False
        console.print(stylized_content, overflow=overflow_method, soft_wrap=soft_wrap)

        return console

    @property
    def _console_terminal(self) -> rich.console.Console:
        return self._get_console_common(
            stylized_content=self._stylized_content_terminal,
            console_width=self._console_dimensions.width,
            console_height=self._console_dimensions.height,
            frame_width=self.frame.dims.width,
            console_color_system=self.config.console_color_system,
            horizontal_overflow_mode=self.config.horizontal_overflow_mode,
        )

    @property
    def _console_html(self) -> rich.console.Console:
        # Color system is hard-coded to 'truecolor' for HTML output
        return self._get_console_common(
            stylized_content=self._stylized_content_html,
            console_width=self._console_dimensions.width,
            console_height=self._console_dimensions.height,
            frame_width=self.frame.dims.width,
            console_color_system=ConsoleColorSystem.ANSI_RGB,
            horizontal_overflow_mode=self.config.horizontal_overflow_mode,
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
        """
        Returns the plain sting output of the panel as a list of lines.
        This is used in DraftPanel to calculate the dimensions of the panel,
        as well as other statistics.
        """
        return self.plain.terminal.splitlines()


@pyd.dataclass(
    frozen=True,
    config=pyd.ConfigDict(extra=pyd.Extra.forbid, validate_all=True, arbitrary_types_allowed=True),
)
class StylizedLayoutPanel(SyntaxStylizedTextPanel):
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

    @property
    def _stylized_content_terminal(self) -> StylizedRichTypes:
        self._clean_rich_style_caches()

        return self._get_stylized_layout_common(
            layout=self.layout,
            console_color_system=self.config.console_color_system,
            color_style=self.config.color_style,
            transparent_background=self.config.transparent_background,
            force_autodetect_bg_color=ForceAutodetect.NEVER,
        )

    @property
    def _stylized_content_html(self) -> StylizedRichTypes:
        self._clean_rich_style_caches()

        return self._get_stylized_layout_common(
            layout=self.layout,
            console_color_system=ConsoleColorSystem.ANSI_RGB,
            color_style=self.config.color_style,
            transparent_background=self.config.transparent_background,
            force_autodetect_bg_color=ForceAutodetect.NEVER,
        )
