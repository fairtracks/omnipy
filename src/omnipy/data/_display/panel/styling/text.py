from functools import cached_property, lru_cache
from typing import Generic

import rich.style
import rich.syntax
from typing_extensions import override

from omnipy.data._display.panel.base import OutputVariant
from omnipy.data._display.panel.draft.text import ReflowedTextDraftPanel
from omnipy.data._display.panel.styling.base import StylizedMonospacedPanel, StylizedRichTypes
from omnipy.data._display.panel.styling.output import OutputMode, TextCroppingOutputVariant
from omnipy.data._display.panel.typedefs import FrameT
from omnipy.data._display.styles.dynamic_styles import clean_style_name
from omnipy.shared.enums.colorstyles import AllColorStyles
from omnipy.shared.enums.display import (DisplayColorSystem,
                                         HorizontalOverflowMode,
                                         SyntaxLanguage,
                                         VerticalOverflowMode)
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
    @lru_cache(maxsize=1024)
    def _get_stylized_content_common(
        content: str,
        tab_size: int,
        color_system: DisplayColorSystem.Literals,  # Only used for hashing
        console_color_style: AllColorStyles.Literals | str,
        syntax_language: SyntaxLanguage.Literals | str,
        horizontal_overflow_mode: HorizontalOverflowMode.Literals,
        remove_bg_color: bool,
    ) -> rich.syntax.Syntax:
        style_name = clean_style_name(console_color_style)
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
            lexer=syntax_language,
            theme=theme,
            # background_color=None if self.config.solid_background else 'default',
            word_wrap=word_wrap,
            tab_size=tab_size,
        )

    @staticmethod
    # @lru_cache
    def _vert_cropped_content(
        content: str,
        height: pyd.NonNegativeInt | None,
        vert_overflow_mode: VerticalOverflowMode.Literals,
    ) -> str:
        """
        Crops the content vertically to the specified height.
        """
        if height is None:
            return content

        lines = content.splitlines(keepends=True)
        height += 1  # Add one line to correctly add ellipsis if needed
        if height < len(lines):
            match vert_overflow_mode:
                case VerticalOverflowMode.CROP_BOTTOM | VerticalOverflowMode.ELLIPSIS_BOTTOM:
                    return ''.join(lines[:height])
                case VerticalOverflowMode.CROP_TOP | VerticalOverflowMode.ELLIPSIS_TOP:
                    return ''.join(lines[-height:])
        return content

    @override
    def _stylized_content_terminal_impl(self) -> StylizedRichTypes:
        cropped_content = self._vert_cropped_content(
            self.content,
            self.frame.dims.height,
            self.config.v_overflow,
        )

        return self._get_stylized_content_common(
            content=cropped_content,
            tab_size=self.config.tab,
            color_system=self.config.system,
            console_color_style=self.config.style,
            syntax_language=self.config.syntax,
            horizontal_overflow_mode=self.config.h_overflow,
            remove_bg_color=not self.config.bg,
        )

    @override
    def _stylized_content_html_impl(self) -> StylizedRichTypes:
        cropped_content = self._vert_cropped_content(
            self.content,
            self.frame.dims.height,
            self.config.v_overflow,
        )

        return self._get_stylized_content_common(
            content=cropped_content,
            tab_size=self.config.tab,
            # Color system is hard-coded to 'truecolor' for HTML output
            color_system=DisplayColorSystem.ANSI_RGB,
            console_color_style=self.config.style,
            syntax_language=self.config.syntax,
            horizontal_overflow_mode=self.config.h_overflow,
            # The HTML background color is set for the entire tag/page, so
            # we need to remove the background color for each element
            remove_bg_color=True)

    @cached_property
    @override
    def plain(self) -> OutputVariant:
        return TextCroppingOutputVariant(self, OutputMode.PLAIN)

    @cached_property
    @override
    def bw_stylized(self) -> OutputVariant:
        return TextCroppingOutputVariant(self, OutputMode.BW_STYLIZED)

    @cached_property
    @override
    def colorized(self) -> OutputVariant:
        return TextCroppingOutputVariant(self, OutputMode.COLORIZED)
