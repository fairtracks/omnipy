import pygments.lexers
import pygments.styles
import pygments.util

from omnipy.data._display.styles.dynamic_styles import install_base16_theme
from omnipy.shared.enums import (AllColorStyles,
                                 DisplayColorSystem,
                                 HorizontalOverflowMode,
                                 Justify,
                                 MaxTitleHeight,
                                 PanelDesign,
                                 PrettyPrinterLib,
                                 RecommendedColorStyles,
                                 SyntaxLanguage,
                                 VerticalOverflowMode)
import omnipy.util._pydantic as pyd


@pyd.dataclass(
    kw_only=True,
    frozen=True,
    config=pyd.ConfigDict(extra=pyd.Extra.forbid, validate_assignment=True),
)
class OutputConfig:
    """
    Configuration of data formatting for DraftOutput (and subclasses).

    This class manages all aspects of output rendering, including syntax
    highlighting, color schemes, font settings, and overflow behavior for
    both terminal and HTML output. It is intended to be used for a specific
    instance of DraftOutput, and not as a global configuration.

    Parameters:
        tab_size (NonNegativeInt): Number of spaces to use for each tab
        indent_tab_size (NonNegativeInt): Number of spaces to use for each
            indentation level.
        debug_mode (bool): When True, enables additional debugging
            information in the output, such as the hierarchy of the Model
            objects.
        pretty_printer (PrettyPrinterLib.Literals): Library to use for
            pretty printing (rich or devtools).
        language (SyntaxLanguage.Literals | str): Syntax language for code
            highlighting. Supported lexers are defined in SyntaxLanguage.
            For non-supported styles, the user can specify a string with the
            Pygments lexer name. For this to work, the lexer must be
            registered in the Pygments library.
        color_system (ColorSystem.Literals): Color system to
            use for terminal output. The default is AUTO, which
            automatically detects the color system based on particular
            environment variables. If color capabilities are not detected,
            the output will be in black and white. If the color system of a
            modern consoles/terminal is not auto-detected (which is the case
            for e.g. the PyCharm console), the user might want to set the
            color system manually to ANSI_RGB to force color output.
        color_style (AllColorStyles.Literals | str): Color style/theme for
            syntax highlighting and other display elements. Supported styles
            are defined in AllColorStyles. For non-supported languages, the
            user can specify a string with the Pygments style name. For this
            to work, the style must be registered in the Pygments library.
        transparent_background (bool): If True, uses transparent background
            for the output. In the case of terminal output, the background
            color will be the current background color of the terminal. For
            HTML output, the background color will be automatically set to
            pure black or pure white, depending on the luminosity of the
            foreground color.
        css_font_families (Tuple[str, ...]): Font families to use in HTML
            output, in order of preference (empty tuple for browser
            default).
        css_font_size (NonNegativeInt | None): Font size in pixels for HTML
            output (None for browser default).
        css_font_weight (NonNegativeInt | None): Font weight for HTML
            output (None for browser default).
        css_line_height (NonNegativeFloat | None): Line height multiplier
            for HTML output (None for browser default).
        horizontal_overflow_mode (HorizontalOverflowMode.Literals): How to
            handle text that exceeds the width.
        vertical_overflow_mode (VerticalOverflowMode.Literals): How to
            handle text that exceeds the height.
        layout_design (LayoutDesign.Literals): Visual design for the layout
            of the output.
        panel_title_at_top (bool): Whether panel titles will be displayed
            over the panel contents (True) or below the contents (False)
        max_title_height (MaxTitleHeight.Literals): Maximum height of the
            panel title. If AUTO, the height is determined by the content of
            the title, up to a maximum of two lines. If ZERO, the title is
            not displayed at all. If ONE or TWO, the title is displayed with
            a fixed height of max one or two lines, respectively.
        justify_in_layout (Justify.Literals): Justification mode for the
            panel if inside a layout panel. This is only used for the panel
            contents.
    """

    tab_size: pyd.NonNegativeInt = 4
    indent_tab_size: pyd.NonNegativeInt = 2
    debug_mode: bool = False
    pretty_printer: PrettyPrinterLib.Literals = PrettyPrinterLib.RICH
    language: SyntaxLanguage.Literals | str = SyntaxLanguage.PYTHON
    color_system: DisplayColorSystem.Literals = DisplayColorSystem.AUTO
    color_style: AllColorStyles.Literals | str = RecommendedColorStyles.ANSI_DARK
    transparent_background: bool = True
    css_font_families: tuple[str, ...] = (
        'CommitMonoOmnipy',
        'Menlo',
        'DejaVu Sans Mono',
        'Consolas',
        'Courier New',
        'monospace',
    )
    css_font_size: pyd.NonNegativeInt | None = 14
    css_font_weight: pyd.NonNegativeInt | None = 450
    css_line_height: pyd.NonNegativeFloat | None = 1.35
    horizontal_overflow_mode: HorizontalOverflowMode.Literals = HorizontalOverflowMode.ELLIPSIS
    vertical_overflow_mode: VerticalOverflowMode.Literals = VerticalOverflowMode.ELLIPSIS_BOTTOM
    panel_design: PanelDesign.Literals = PanelDesign.TABLE_GRID
    panel_title_at_top: bool = True
    max_title_height: MaxTitleHeight.Literals = MaxTitleHeight.AUTO
    justify_in_layout: Justify.Literals = Justify.LEFT

    @pyd.validator('language')
    def validate_language(
        cls,
        language: SyntaxLanguage.Literals | str,
    ) -> SyntaxLanguage.Literals | str:
        try:
            if language in SyntaxLanguage:
                return language
            elif pygments.lexers.get_lexer_by_name(language):
                return language
            else:
                raise ValueError(f'Invalid syntax language: {language}')
        except pygments.util.ClassNotFound as exp:
            raise ValueError(f'Invalid syntax language: {language}') from exp

    @pyd.validator('color_style')
    def validate_color_style(
        cls,
        color_style: AllColorStyles.Literals | str,
    ) -> AllColorStyles.Literals | str:
        try:
            if color_style in RecommendedColorStyles:
                return color_style
            elif color_style in AllColorStyles:
                try:
                    pygments.styles.get_style_by_name(color_style)
                except pygments.util.ClassNotFound:
                    install_base16_theme(color_style)
                    pygments.styles.get_style_by_name(color_style)
                return color_style
            elif pygments.styles.get_style_by_name(color_style):
                return color_style
            else:
                raise ValueError(f'Invalid color style: {color_style}')
        except pygments.util.ClassNotFound as exp:
            raise ValueError(f'Color style not registered in Pygments: {color_style}. '
                             f'This may be due to a network error.') from exp
