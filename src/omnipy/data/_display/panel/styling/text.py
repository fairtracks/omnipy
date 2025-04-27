from functools import cache, cached_property
from typing import Generic

import rich.style
import rich.syntax
from typing_extensions import override

from omnipy.data._display.config import (ColorStyles,
                                         ConsoleColorSystem,
                                         HorizontalOverflowMode,
                                         SyntaxLanguage)
from omnipy.data._display.panel.base import FrameT, OutputVariant
from omnipy.data._display.panel.draft.text import ReflowedTextDraftPanel
from omnipy.data._display.panel.helpers import extract_value_if_enum
from omnipy.data._display.panel.styling.base import StylizedMonospacedPanel, StylizedRichTypes
from omnipy.data._display.panel.styling.output import OutputMode, VerticalTextCroppingOutputVariant
from omnipy.util import _pydantic as pyd


@pyd.dataclass(
    init=False,
    frozen=True,
    config=pyd.ConfigDict(extra=pyd.Extra.forbid, validate_all=True),
)
class SyntaxStylizedTextPanel(
        StylizedMonospacedPanel[ReflowedTextDraftPanel, str, FrameT],
        Generic[FrameT],
):
    @staticmethod
    @cache
    def _get_stylized_content_common(
        content: str,
        tab_size: int,
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
            tab_size=tab_size,
        )

    @override
    def _stylized_content_terminal_impl(self) -> StylizedRichTypes:
        return self._get_stylized_content_common(
            content=self.content,
            tab_size=self.config.tab_size,
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
            tab_size=self.config.tab_size,
            # Color system is hard-coded to 'truecolor' for HTML output
            console_color_system=ConsoleColorSystem.ANSI_RGB,
            console_color_style=self.config.color_style,
            language=self.config.language,
            horizontal_overflow_mode=self.config.horizontal_overflow_mode,
            # The HTML background color is set for the entire tag/page, so
            # we need to remove the background color for each element
            remove_bg_color=True)

    @cached_property
    @override
    def plain(self) -> OutputVariant:
        return VerticalTextCroppingOutputVariant(self, OutputMode.PLAIN)

    @cached_property
    @override
    def bw_stylized(self) -> OutputVariant:
        return VerticalTextCroppingOutputVariant(self, OutputMode.BW_STYLIZED)

    @cached_property
    @override
    def colorized(self) -> OutputVariant:
        return VerticalTextCroppingOutputVariant(self, OutputMode.COLORIZED)
