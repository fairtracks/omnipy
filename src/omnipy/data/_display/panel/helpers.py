from enum import Enum
from functools import lru_cache
from typing import Literal

import pygments.token
import rich.color
import rich.color_triplet
import rich.style
import rich.syntax

from omnipy.shared.enums import AllColorStyles
from omnipy.util.literal_enum import LiteralEnum


class ForceAutodetect(LiteralEnum[str]):
    Literals = Literal['never', 'if_no_bg_color_in_style', 'always']

    NEVER: Literal['never'] = 'never'
    IF_NO_BG_COLOR_IN_STYLE: Literal['if_no_bg_color_in_style'] = 'if_no_bg_color_in_style'
    ALWAYS: Literal['always'] = 'always'


def extract_value_if_enum(conf_item: Enum | str) -> str:
    return conf_item.value if isinstance(conf_item, Enum) else conf_item


@lru_cache
def get_syntax_theme_from_color_style(
        color_style: AllColorStyles.Literals) -> rich.syntax.SyntaxTheme:
    color_style_name = extract_value_if_enum(color_style)
    return rich.syntax.Syntax.get_theme(color_style_name)


@lru_cache
def get_token_style_from_color_style(
    token: pygments.token._TokenType,
    color_style: AllColorStyles.Literals,
) -> rich.style.Style:
    syntax_theme = get_syntax_theme_from_color_style(color_style)
    return syntax_theme.get_style_for_token(token)


@lru_cache
def calculate_fg_color_from_color_style(color_style: AllColorStyles.Literals) -> rich.color.Color:
    ANSI_FG_COLOR_MAP = {'ansi_light': 'black', 'ansi_dark': 'bright_white'}

    color_style_name = extract_value_if_enum(color_style)

    fg_color = get_token_style_from_color_style(pygments.token.Token, color_style).color

    if fg_color is None and color_style_name in ANSI_FG_COLOR_MAP:
        fg_color = rich.color.Color.parse(ANSI_FG_COLOR_MAP[color_style_name])

    # Currently, the rich library defaults to a black foreground color if the token color is not
    # set for a pygments style. However, this may change in the future, so we need to check for
    # this case defensively. All color styles currently defined for Omnipy should have a token
    # color set.
    assert fg_color is not None

    return fg_color


@lru_cache
def calculate_fg_color_triplet_from_color_style(
        color_style: AllColorStyles.Literals) -> rich.color_triplet.ColorTriplet:
    syntax_theme_fg_color = calculate_fg_color_from_color_style(color_style)
    return syntax_theme_fg_color.get_truecolor(foreground=True)


@lru_cache
def calculate_bg_color_from_color_style(
    color_style: AllColorStyles.Literals,
    force_autodetect: ForceAutodetect.Literals,
) -> rich.color.Color | None:
    def _auto_detect_bw_background_color(
            fg_color_triplet: rich.color_triplet.ColorTriplet) -> rich.color.Color:
        """
        Auto-detects a black or bright white background color based on the luminance of the
        foreground color (i.e. whether the style is light or dark).
        """
        fg_luminance = sum(fg_color_triplet) / 3
        return rich.color.Color.parse('black' if fg_luminance > 127.5 else 'bright_white')

    syntax_theme = get_syntax_theme_from_color_style(color_style)
    bg_color = syntax_theme.get_background_style().bgcolor

    # If the background color is not set in the theme, we need to auto-detect it as black or
    # bright white based on the luminance of the foreground color, to support both light and
    # dark color styles.
    #
    # In addition, a transparent background for a full HTML page output will in practice be a
    # bright white background, so we instead also autodetect a black or bright white background
    # color also in this case.

    if (bg_color is None and force_autodetect is ForceAutodetect.IF_NO_BG_COLOR_IN_STYLE) \
            or (force_autodetect is ForceAutodetect.ALWAYS):
        fg_color_triplet = calculate_fg_color_triplet_from_color_style(color_style)
        bg_color = _auto_detect_bw_background_color(fg_color_triplet)

    return bg_color


@lru_cache
def calculate_bg_color_triplet_from_color_style(
    color_style: AllColorStyles.Literals,
    force_autodetect: ForceAutodetect.Literals,
) -> rich.color_triplet.ColorTriplet | None:
    bg_color = calculate_bg_color_from_color_style(color_style, force_autodetect)

    if bg_color is not None:
        return bg_color.get_truecolor(foreground=False)
    else:
        return None
