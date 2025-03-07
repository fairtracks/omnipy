from copy import copy
from enum import Enum
from functools import cached_property
from io import StringIO
import re
from textwrap import dedent
from typing import Callable, ClassVar, Generic, Iterable, Literal, overload

from pygments.token import Token
from rich.color import Color
from rich.console import Console, OverflowMethod
from rich.segment import Segment
from rich.style import Style
from rich.syntax import Syntax
from rich.terminal_theme import DEFAULT_TERMINAL_THEME, TerminalTheme

from omnipy.data._display.config import HorizontalOverflowMode, VerticalOverflowMode
from omnipy.data._display.draft import DraftMonospacedOutput, FrameT
from omnipy.util._pydantic import ConfigDict, dataclass, Extra


class OutputMode(str, Enum):
    PLAIN = 'plain'
    BW_STYLIZED = 'bw_stylized'
    COLORIZED = 'colorized'


class OutputVariant:
    _FONT_FAMILY_LIST: ClassVar[tuple[str, ...]] = (
        'CommitMonoOmnipy',
        'Menlo',
        'DejaVu Sans Mono',
        'Consolas',
        'Courier New',
        'monospace',
    )
    _FONT_FAMILY_STR: ClassVar[str] = ', '.join(f"'{_}'" for _ in _FONT_FAMILY_LIST)
    _FONT_WEIGHT: ClassVar[int] = 450
    _FONT_SIZE: ClassVar[int] = 14
    _LINE_HEIGHT: ClassVar[float] = 1.35

    _CSS_COLOR_STYLE_TEMPLATE_FG_AND_BG: ClassVar[str] = ('color: {foreground}; '
                                                          'background-color: {background}; ')

    _CSS_COLOR_STYLE_TEMPLATE_FG_ONLY: ClassVar[str] = 'color: {foreground}; '

    _CSS_DEFAULT_FONT_STYLE: ClassVar[str] = (f'font-family: {_FONT_FAMILY_STR}; '
                                              f'font-weight: {_FONT_WEIGHT}; '
                                              f'font-size: {_FONT_SIZE}px; '
                                              f'line-height: {_LINE_HEIGHT}; ')

    _HTML_TAG_TEMPLATE: ClassVar[str] = ('<pre>'
                                         '<code style="'
                                         '{font_style}'
                                         '{color_style}">'
                                         '{code}'
                                         '</code>'
                                         '</pre>')

    _HTML_PAGE_TEMPLATE: ClassVar[str] = dedent(f"""\
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
            {_HTML_TAG_TEMPLATE.format(font_style=_CSS_DEFAULT_FONT_STYLE,
                                       color_style='',
                                       code='{code}')}
          </body>
        </html>
        """)

    # Refactor to take StylizedMonospacedOutput as input, in order to lazify console creation, and
    # avoid creating the console twice (once for terminal and once for HTML) if not needed. Will
    # also simplify the signature.
    def __init__(self,
                 console_terminal: Console,
                 console_html: Console,
                 output_mode: OutputMode,
                 style_name: str,
                 transparent_background: bool,
                 frame_height: int | None,
                 vertical_overflow_mode: VerticalOverflowMode) -> None:
        self._console_terminal = console_terminal
        self._console_html = console_html
        self._output_mode = output_mode
        self._style_name = style_name
        self._transparent_background = transparent_background
        self._frame_height = frame_height
        self._vertical_overflow_mode = vertical_overflow_mode

    def _vertical_crop(self, text: str) -> str:
        if self._frame_height is None:
            return text

        lines = text.splitlines(keepends=True)
        if len(lines) <= self._frame_height:
            return text

        match (self._vertical_overflow_mode):
            case VerticalOverflowMode.CROP_BOTTOM:
                return ''.join(lines[:self._frame_height])
            case VerticalOverflowMode.CROP_TOP:
                return ''.join(lines[-self._frame_height:])

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

    @cached_property
    def terminal(self) -> str:
        ansi_output = self._output_mode is not OutputMode.PLAIN
        console = self._prepare_terminal_export()
        text = console.export_text(clear=False, styles=ansi_output)
        return self._vertical_crop(text)

    def _prepare_terminal_export(self) -> Console:
        if self._output_mode is OutputMode.BW_STYLIZED:
            return self._remove_all_color_from_console_recording(self._console_terminal)
        return self._console_terminal

    @cached_property
    def html_page(self) -> str:
        console = self._prepare_html_export()
        html = console.export_html(
            clear=False, theme=self._get_terminal_theme(), code_format=self._HTML_PAGE_TEMPLATE)
        return self._vertical_crop_html(html)

    @cached_property
    def html_tag(self) -> str:
        console = self._prepare_html_export()

        if self._output_mode == OutputMode.COLORIZED:
            if self._transparent_background:
                css_color_style = self._CSS_COLOR_STYLE_TEMPLATE_FG_ONLY
            else:
                css_color_style = self._CSS_COLOR_STYLE_TEMPLATE_FG_AND_BG
        else:
            css_color_style = ''

        html_tag_template = self._HTML_TAG_TEMPLATE.format(
            font_style=self._CSS_DEFAULT_FONT_STYLE, color_style=css_color_style, code='{code}')

        html = console.export_html(
            clear=False,
            theme=self._get_terminal_theme(),
            code_format=html_tag_template,
            inline_styles=True)
        return self._vertical_crop_html(html)

    def _prepare_html_export(self) -> Console:
        if self._output_mode is OutputMode.PLAIN:
            return self._remove_styling_from_console_recording(self._console_html)
        if self._output_mode is OutputMode.BW_STYLIZED:
            return self._remove_all_color_from_console_recording(self._console_html)
        return self._console_html

    # Hacks to remove color and strip styles from the console record buffer, making use of
    # private methods in the rich library. These are needed to prevent the stylized output from
    # being displayed in the HTML output, as the library provides no other ways to do this.

    def _apply_filter_to_console_recording(
        self,
        console: Console,
        filter_func: Callable[[list[Segment]], Iterable[Segment]],
    ) -> Console:
        new_console = copy(console)
        with console._record_buffer_lock:
            new_console._record_buffer = \
                filter_func(console._record_buffer)  # type: ignore[assignment]
        return new_console

    def _remove_all_color_from_console_recording(self, console: Console) -> Console:
        return self._apply_filter_to_console_recording(console, Segment.remove_color)

    def _remove_styling_from_console_recording(self, console: Console) -> Console:
        return self._apply_filter_to_console_recording(console, Segment.strip_styles)

    def _get_terminal_theme(self) -> TerminalTheme:

        ansi_fg_color_map = {'ansi_light': 'black', 'ansi_dark': 'bright_white'}

        terminal_theme = DEFAULT_TERMINAL_THEME

        if self._output_mode is OutputMode.COLORIZED:
            terminal_theme = copy(terminal_theme)

            syntax_theme = Syntax.get_theme(self._style_name)

            syntax_theme_fg_color = syntax_theme.get_style_for_token(Token).color
            if syntax_theme_fg_color is None and self._style_name in ansi_fg_color_map:
                syntax_theme_fg_color = Color.parse(ansi_fg_color_map[self._style_name])
            assert syntax_theme_fg_color is not None
            terminal_theme.foreground_color = syntax_theme_fg_color.get_truecolor(foreground=True)

            syntax_theme_bg_color = syntax_theme.get_background_style().bgcolor
            if syntax_theme_bg_color is None or self._transparent_background:
                fg_luminance = sum(terminal_theme.foreground_color) / 3
                syntax_theme_bg_color = \
                    Color.parse('black' if fg_luminance > 127.5 else 'bright_white')
            if syntax_theme_bg_color is not None:
                terminal_theme.background_color = syntax_theme_bg_color.get_truecolor(
                    foreground=False)

        return terminal_theme


@dataclass(config=ConfigDict(extra=Extra.forbid, validate_all=True))
class StylizedMonospacedOutput(DraftMonospacedOutput[FrameT], Generic[FrameT]):
    @overload
    def __init__(self, content: DraftMonospacedOutput[FrameT]):
        ...

    @overload
    def __init__(self, content: str, frame=None, constraints=None, config=None):
        ...

    def __init__(self,
                 content: str | DraftMonospacedOutput[FrameT],
                 frame=None,
                 constraints=None,
                 config=None):
        if isinstance(content, DraftMonospacedOutput):
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
    def _extract_value_if_enum(conf_item: Enum | str) -> str:
        return conf_item.value if isinstance(conf_item, Enum) else conf_item

    def _get_stylized_content_common(self, remove_bg_color: bool) -> Syntax:
        style_name = self._extract_value_if_enum(self.config.color_style)
        lexer_name = self._extract_value_if_enum(self.config.language)
        word_wrap = self.config.horizontal_overflow_mode == HorizontalOverflowMode.WORD_WRAP

        # Workaround to remove the background color from the theme, as setting
        # background_color='default' (the official solution,
        # see https://github.com/Textualize/rich/issues/284#issuecomment-694947144)
        # does not work for HTML content.
        theme = Syntax.get_theme(style_name)
        if remove_bg_color:
            theme._background_color = None  # type: ignore[attr-defined]
            theme._background_style = Style()  # type: ignore[attr-defined]

        return Syntax(
            self.content,
            lexer=lexer_name,
            theme=theme,
            # background_color='default' if self.config.transparent_background else None,
            word_wrap=word_wrap,
        )

    @cached_property
    def _stylized_content_terminal(self) -> Syntax:
        if self.config.transparent_background:
            return self._stylized_content_html
        else:
            return self._get_stylized_content_common(remove_bg_color=False)

    @cached_property
    def _stylized_content_html(self) -> Syntax:
        return self._get_stylized_content_common(remove_bg_color=True)

    def _get_console_frame_width_and_height(self) -> tuple[int, int]:
        frame_width = self.frame.dims.width
        frame_height = self.frame.dims.height

        if frame_width is None or frame_height is None:
            draft = DraftMonospacedOutput(self.content)

            if frame_width is None:
                frame_width = draft.dims.width
            if frame_height is None:
                frame_height = draft.dims.height

        return frame_width, frame_height

    def _get_console_overload(self) -> OverflowMethod | None:
        match (self.config.horizontal_overflow_mode):
            case HorizontalOverflowMode.ELLIPSIS:
                return 'ellipsis'
            case HorizontalOverflowMode.CROP:
                return 'crop'
            case HorizontalOverflowMode.WORD_WRAP:
                return None

    def _get_console_common(
        self,
        stylized_content: Syntax,
        color_system: Literal['auto', 'standard', '256', 'truecolor', 'windows'],
    ) -> Console:
        width, height = self._get_console_frame_width_and_height()

        console = Console(
            file=StringIO(),
            width=width,
            height=height,
            color_system=color_system,
            record=True,
        )

        overflow = self._get_console_overload()
        soft_wrap = True if self.frame.dims.width is None else False
        console.print(stylized_content, overflow=overflow, soft_wrap=soft_wrap)

        return console

    @cached_property
    def _console_terminal(self) -> Console:
        color_system: Literal['truecolor'] = 'truecolor'  # placeholder for config

        if self.config.transparent_background and color_system == 'truecolor':
            return self._console_html
        return self._get_console_common(self._stylized_content_terminal, color_system)

    @cached_property
    def _console_html(self) -> Console:
        # Color system is hard-coded to 'truecolor' for HTML output
        return self._get_console_common(self._stylized_content_html, color_system='truecolor')

    @cached_property
    def plain(self) -> OutputVariant:
        return OutputVariant(
            self._console_terminal,
            self._console_html,
            OutputMode.PLAIN,
            self._extract_value_if_enum(self.config.color_style),
            self.config.transparent_background,
            self.frame.dims.height,
            self.config.vertical_overflow_mode,
        )

    @cached_property
    def bw_stylized(self) -> OutputVariant:
        return OutputVariant(
            self._console_terminal,
            self._console_html,
            OutputMode.BW_STYLIZED,
            self._extract_value_if_enum(self.config.color_style),
            self.config.transparent_background,
            self.frame.dims.height,
            self.config.vertical_overflow_mode,
        )

    @cached_property
    def colorized(self) -> OutputVariant:
        return OutputVariant(
            self._console_terminal,
            self._console_html,
            OutputMode.COLORIZED,
            self._extract_value_if_enum(self.config.color_style),
            self.config.transparent_background,
            self.frame.dims.height,
            self.config.vertical_overflow_mode,
        )

    @cached_property
    def _content_lines(self) -> list[str]:
        return self.plain.terminal.splitlines()
