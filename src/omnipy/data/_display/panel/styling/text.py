from functools import cache, cached_property
import re
from typing import Generic, overload

import rich.style
import rich.syntax
from typing_extensions import override

from omnipy.data._display.config import (ColorStyles,
                                         ConsoleColorSystem,
                                         HorizontalOverflowMode,
                                         SyntaxLanguage,
                                         VerticalOverflowMode)
from omnipy.data._display.dimensions import DimensionsWithWidthAndHeight
from omnipy.data._display.panel.base import FrameT, OutputVariant
from omnipy.data._display.panel.draft.text import ReflowedTextDraftPanel
from omnipy.data._display.panel.helpers import extract_value_if_enum
from omnipy.data._display.panel.styling.base import StylizedPanel, StylizedRichTypes
from omnipy.data._display.panel.styling.output import CommonOutputVariant, ContentT, OutputMode
from omnipy.util import _pydantic as pyd


class StylizedTextOutputVariant(CommonOutputVariant[ContentT, FrameT], Generic[ContentT, FrameT]):
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

    @cached_property
    def terminal(self) -> str:
        return self._vertical_crop(self._terminal)

    @cached_property
    def html_tag(self) -> str:
        return self._vertical_crop_html(self._html_tag)

    @cached_property
    def html_page(self) -> str:
        return self._vertical_crop_html(self._html_page)


@pyd.dataclass(
    init=False,
    frozen=True,
    config=pyd.ConfigDict(extra=pyd.Extra.forbid, validate_all=True),
)
class SyntaxStylizedTextPanel(StylizedPanel[str, FrameT],
                              ReflowedTextDraftPanel[FrameT],
                              Generic[FrameT]):
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

    @override
    def _stylized_content_terminal_impl(self) -> StylizedRichTypes:
        return self._get_stylized_content_common(
            content=self.content,
            console_color_system=self.config.console_color_system,
            console_color_style=self.config.color_style,
            language=self.config.language,
            horizontal_overflow_mode=self.config.horizontal_overflow_mode,
            remove_bg_color=self.config.transparent_background,
        )

    @override
    def _stylized_content_html_impl(self) -> StylizedRichTypes:
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

    @override
    def _get_console_dimensions_from_content(self) -> DimensionsWithWidthAndHeight:
        if isinstance(self.content, ReflowedTextDraftPanel):
            return self.content.dims
        else:
            return ReflowedTextDraftPanel(self.content).dims

    @cached_property
    @override
    def _content_lines(self) -> list[str]:
        """
        Returns the plain sting output of the panel as a list of lines.
        This is used in DraftPanel to calculate the dimensions of the panel,
        as well as other statistics.
        """
        return self.plain.terminal.splitlines()

    @cached_property
    def plain(self) -> OutputVariant:
        return StylizedTextOutputVariant(self, OutputMode.PLAIN)

    @cached_property
    def bw_stylized(self) -> OutputVariant:
        return StylizedTextOutputVariant(self, OutputMode.BW_STYLIZED)

    @cached_property
    def colorized(self) -> OutputVariant:
        return StylizedTextOutputVariant(self, OutputMode.COLORIZED)
