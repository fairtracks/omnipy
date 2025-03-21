# The omnipy-selenized-* themes are adapted from the selenized-* base16 themes
# available at https://github.com/tinted-theming/schemes/tree/spec-0.11/base16,
# with slightly increased contrast for comment colors.
#
# The selenized-* themes are adaptations (by GitHub user "ali-githb",
# https://github.com/tinted-theming/base16-schemes/pull/20) of the Selenized
# theme by Jan Warchoł, available at https://github.com/jan-warchol/selenized,
# under the following License:
#
# MIT License
#
# Copyright (c) 2021 Jan Warchoł
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import pygments.style

from .helpers import Base16Colors, get_styles_from_base16_colors


class OmnipySelenizedBlackStyle(pygments.style.Style):
    name = 'omnipy-selenized-black'
    author = 'Jan Warchol / adapted to base16 by ali / modified by Sveinung Gundersen'
    variant = 'dark'
    _palette = Base16Colors(
        base00='#181818',
        base01='#252525',
        base02='#3b3b3b',
        base03='#878787',  # Original: #777777
        base04='#878787',  # Original: #777777
        base05='#b9b9b9',
        base06='#dedede',
        base07='#dedede',
        base08='#ed4a46',
        base09='#e67f43',
        base0A='#dbb32d',
        base0B='#70b433',
        base0C='#3fc5b7',
        base0D='#368aeb',
        base0E='#a580e2',
        base0F='#eb6eb7',
    )

    background_color = _palette.base00
    highlight_color = _palette.base02

    styles = get_styles_from_base16_colors(_palette)


class OmnipySelenizedDarkStyle(pygments.style.Style):
    name = 'omnipy-selenized-dark'
    author = 'Jan Warchol / adapted to base16 by ali / modified by Sveinung Gundersen'
    variant = 'dark'
    _palette = Base16Colors(
        base00='#103c48',
        base01='#184956',
        base02='#2d5b69',
        base03='#80959a',  # Original: #72898f
        base04='#80959a',  # Original: #72898f
        base05='#adbcbc',
        base06='#cad8d9',
        base07='#cad8d9',
        base08='#fa5750',
        base09='#ed8649',
        base0A='#dbb32d',
        base0B='#75b938',
        base0C='#41c7b9',
        base0D='#4695f7',
        base0E='#af88eb',
        base0F='#f275be',
    )

    background_color = _palette.base00
    highlight_color = _palette.base02

    styles = get_styles_from_base16_colors(_palette)


class OmnipySelenizedLightStyle(pygments.style.Style):
    name = 'omnipy-selenized-light'
    author = 'Jan Warchol / adapted to base16 by ali / modified by Sveinung Gundersen'
    variant = 'light'
    _palette = Base16Colors(
        base00='#fbf3db',
        base01='#ece3cc',
        base02='#d5cdb6',
        base03='#808c8a',  # Original: #909995
        base04='#808c8a',  # Original: #909995
        base05='#53676d',
        base06='#3a4d53',
        base07='#3a4d53',
        base08='#cc1729',
        base09='#bc5819',
        base0A='#a78300',
        base0B='#428b00',
        base0C='#00978a',
        base0D='#006dce',
        base0E='#825dc0',
        base0F='#c44392',
    )

    background_color = _palette.base00
    highlight_color = _palette.base02

    styles = get_styles_from_base16_colors(_palette)


class OmnipySelenizedWhiteStyle(pygments.style.Style):
    name = 'omnipy-selenized-white'
    author = 'Jan Warchol / adapted to base16 by ali / modified by Sveinung Gundersen'
    variant = 'light'
    _palette = Base16Colors(
        base00='#ffffff',
        base01='#ebebeb',
        base02='#cdcdcd',
        base03='#777777',  # Original: #878787
        base04='#777777',  # Original: #878787
        base05='#474747',
        base06='#282828',
        base07='#282828',
        base08='#bf0000',
        base09='#ba3700',
        base0A='#af8500',
        base0B='#008400',
        base0C='#009a8a',
        base0D='#0054cf',
        base0E='#6b40c3',
        base0F='#dd0f9d',
    )

    background_color = _palette.base00
    highlight_color = _palette.base02

    styles = get_styles_from_base16_colors(_palette)
