from typing import Any

import pygments.lexers
import pygments.styles
import pygments.util

from omnipy.data._display.styles.dynamic_styles import (clean_style_name,
                                                        handle_random_name,
                                                        install_base16_theme)
from omnipy.shared.constants import MIN_CROP_WIDTH, MIN_PANEL_WIDTH
from omnipy.shared.enums.colorstyles import AllColorStyles, RecommendedColorStyles
from omnipy.shared.enums.display import (DisplayColorSystem,
                                         HorizontalOverflowMode,
                                         Justify,
                                         MaxTitleHeight,
                                         PanelDesign,
                                         PrettyPrinterLib,
                                         SyntaxLanguage,
                                         VerticalOverflowMode)
from omnipy.shared.enums.ui import SpecifiedUserInterfaceType, UserInterfaceType
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
        tab (NonNegativeInt): Number of spaces to use for each tab
        indent (NonNegativeInt): Number of spaces to use for each
            indentation level.
        printer (PrettyPrinterLib.Literals): Library to use for pretty
            printing.
        syntax (SyntaxLanguage.Literals | str): Syntax language for code
            highlighting. Supported lexers are defined in SyntaxLanguage.
            For non-supported styles, the user can specify a string with the
            Pygments lexer name. For this to work, the lexer must be
            registered in the Pygments library.
        freedom (float | None): Parameter that controls the level of
            freedom for formatted text to follow the geometry of the frame
            size (=total available area) in a proportional manner. If the
            proportional freedom is 0 (the lowest), then the output area
            must not in any case be proportionally wider that the frame
            (i.e. a 16:9 frame will only produce output that is 16:9 or
            narrower). Larger values of proportional freedom allow the
            output to be proportionally wider than the total available
            frame, to a degree that relates to the size difference between
            the frame and the content (larger difference gives more
            freedom). The default value of 2.5 is a good compromise
            between readability/aesthetics and good use of the screen
            estate. If None, the freedom is unlimited (i.e. proportionality
            is not taken into account at all).
        debug (bool): When True, enables additional debugging information in
            the output, such as the hierarchy of the Model objects.
        ui (UserInterfaceType.Literals): Type of user interface for which
            the output should being prepared. The user interface describes
            the technical solutions available for interacting with the user,
            encompassing the support available for displaying output as well
            as how the user interacts with the library (including the type
            of interactive interpreter used, if any).
        system (ColorSystem.Literals): Color system to use for terminal
            output. The default is AUTO, which automatically detects the
            color system based on particular environment variables. If color
            capabilities are not detected, the output will be in black and
            white. If the color system of a modern consoles/terminal is not
            auto-detected (which is the case for e.g. the PyCharm console),
            the user might want to set the color system manually to ANSI_RGB
            to force color output.
        style (AllColorStyles.Literals | str): Color style/theme for syntax
            highlighting and other display elements. Supported styles are
            defined in AllColorStyles. For non-supported styles, the user
            can specify a string with the Pygments style name. For this to
            work, the style must be registered in the Pygments library.
        bg (bool): If False, uses transparent background for the output. In
            the case of terminal output, the background color will be the
            current background color of the terminal. For HTML output, the
            background color will be automatically set to pure black or pure
            white, depending on the luminosity of the foreground color.
        fonts (Tuple[str, ...]): Font families to use in HTML output, in
            order of preference (empty tuple for browser default).
        font_size (NonNegativeInt | None): Font size in pixels for HTML output
            (None for browser default).
        font_weight (NonNegativeInt | None): Font weight for HTML output (None
            for browser default).
        line_height (NonNegativeFloat | None): Line height multiplier for HTML
            output (None for browser default).
        h_overflow (HorizontalOverflowMode.Literals): How to handle text
            that exceeds the width.
        v_overflow (VerticalOverflowMode.Literals): How to handle text
            that exceeds the height.
        panel (PanelDesign.Literals): Visual design of the panel used as
            container for the output. Only TABLE is currently
            supported, which displays the output in a table-like grid.
        title_at_top (bool): Whether panel titles will be displayed over the
            panel content (True) or below the content (False)
        max_title_height (MaxTitleHeight.Literals): Maximum height of the
            panel title. If AUTO, the height is determined by the content
            of the title, up to a maximum of two lines. If ZERO, the title
            is not displayed at all. If ONE or TWO, the title is displayed
            with a fixed height of max one or two lines, respectively.
        min_panel_width (NonNegativeInt): Minimum width in characters per
            panel.
        min_crop_width (NonNegativeInt): Minimum cropping width in
            characters for panels in cases where more than one panel are to
            be displayed. This is for instance used to calculate the
            number of models to display in a Dataset peek(). Only applied
            if `use_min_crop_width` is set to `True`. `min_crop_width`
            must be equal to or larger than `min_panel_width`.
        use_min_crop_width (bool): Whether the `min_crop_width` value should
            be considered in cases where more than one panel are to
            be displayed, potentially reduce the number of displayed panels.
        justify (Justify.Literals): Justification mode for the panel if
            inside a layout panel. This is only used for the panel content.
    """

    tab: pyd.NonNegativeInt = 4
    indent: pyd.NonNegativeInt = 2
    printer: PrettyPrinterLib.Literals = PrettyPrinterLib.AUTO
    syntax: SyntaxLanguage.Literals | str = SyntaxLanguage.PYTHON
    freedom: pyd.NonNegativeFloat | None = 2.5
    debug: bool = False
    ui: SpecifiedUserInterfaceType.Literals = UserInterfaceType.TERMINAL
    system: DisplayColorSystem.Literals = DisplayColorSystem.AUTO
    style: AllColorStyles.Literals | str = RecommendedColorStyles.ANSI_DARK
    bg: bool = False
    fonts: tuple[str, ...] = (
        'Menlo',
        'DejaVu Sans Mono',
        'Consolas',
        'Courier New',
        'monospace',
    )
    font_size: pyd.NonNegativeInt | None = 14
    font_weight: pyd.NonNegativeInt | None = 400
    line_height: pyd.NonNegativeFloat | None = 1.25
    h_overflow: HorizontalOverflowMode.Literals = HorizontalOverflowMode.ELLIPSIS
    v_overflow: VerticalOverflowMode.Literals = VerticalOverflowMode.ELLIPSIS_BOTTOM
    panel: PanelDesign.Literals = PanelDesign.TABLE
    title_at_top: bool = True
    max_title_height: MaxTitleHeight.Literals = MaxTitleHeight.AUTO
    min_panel_width: pyd.NonNegativeInt = MIN_PANEL_WIDTH
    min_crop_width: pyd.NonNegativeInt = MIN_CROP_WIDTH
    use_min_crop_width: bool = False
    justify: Justify.Literals = Justify.LEFT

    @pyd.validator('syntax')
    def check_syntax(
        cls,
        syntax: SyntaxLanguage.Literals | str,
    ) -> SyntaxLanguage.Literals | str:
        try:
            if SyntaxLanguage.is_syntax_language(syntax):
                return syntax
            elif pygments.lexers.get_lexer_by_name(syntax):
                return syntax
            else:
                raise ValueError(f'Invalid syntax language: {syntax}')
        except pygments.util.ClassNotFound as exp:
            raise ValueError(f'Invalid syntax language: {syntax}') from exp

    @pyd.validator('style')
    def check_color_style(
        cls,
        style: AllColorStyles.Literals | str,
    ) -> AllColorStyles.Literals | str:
        try:
            if style in RecommendedColorStyles:
                return style
            elif style in AllColorStyles:
                style = handle_random_name(style)
                if style not in RecommendedColorStyles:
                    try:
                        pygments.styles.get_style_by_name(clean_style_name(style))
                    except pygments.util.ClassNotFound:
                        install_base16_theme(style)
                        pygments.styles.get_style_by_name(style)
                return style
            elif pygments.styles.get_style_by_name(style):
                return style
            else:
                raise ValueError(f'Invalid color style: {style}')
        except pygments.util.ClassNotFound as exp:
            raise ValueError(f'Color style not registered in Pygments: {style}. '
                             f'This may be due to a network error.') from exp

    @pyd.root_validator
    def check_min_crop_width(cls, values: dict[str, Any]) -> dict[str, Any]:
        min_crop_width = values.get('min_crop_width')
        min_panel_width = values.get('min_panel_width')
        if min_crop_width is not None and min_panel_width is not None:
            if min_crop_width < min_panel_width:
                raise ValueError(f'min_crop_width ({min_crop_width}) cannot be less than '
                                 f'min_panel_width ({min_panel_width})')
        return values
