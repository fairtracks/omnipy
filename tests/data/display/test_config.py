"""Tests for data display configuration."""

from typing import Any

import pytest

from omnipy.data._display.config import OutputConfig
from omnipy.shared.enums.colorstyles import (
    DarkLowContrastColorStyles,
    LightHighContrastColorStyles,
    RecommendedColorStyles,
)
from omnipy.shared.enums.display import (
    DarkBackground,
    DisplayColorSystem,
    HorizontalOverflowMode,
    Justify,
    MaxTitleHeight,
    PanelDesign,
    PrettyPrinterLib,
    SyntaxLanguageSpec,
    VerticalOverflowMode,
)
from omnipy.shared.enums.ui import UserInterfaceType


def test_output_config() -> None:
    config = OutputConfig(
        tab=2,
        indent=4,
        printer=PrettyPrinterLib.DEVTOOLS,
        syntax=SyntaxLanguageSpec.JSON,
        freedom=3.5,
        debug=True,
        ui=UserInterfaceType.JUPYTER,
        system=DisplayColorSystem.ANSI_RGB,
        style=DarkLowContrastColorStyles.ONE_DARK_PYGMENTS,
        dark=DarkBackground.TRUE,
        bg=True,
        fonts=('Menlo', 'monospace'),
        font_size=16,
        font_weight=400,
        line_height=1.0,
        h_overflow=HorizontalOverflowMode.CROP,
        v_overflow=VerticalOverflowMode.CROP_TOP,
        panel=PanelDesign.PANELS,
        title_at_top=False,
        max_title_height=MaxTitleHeight.ZERO,
        min_panel_width=5,
        min_crop_width=20,
        use_min_crop_width=True,
        max_panels_hor=15,
        max_nesting_depth=5,
        justify=Justify.RIGHT,
    )

    assert config.tab == 2
    assert config.indent == 4
    assert config.printer is PrettyPrinterLib.DEVTOOLS
    assert config.syntax is SyntaxLanguageSpec.JSON
    assert config.freedom == 3.5
    assert config.debug is True
    assert config.ui is UserInterfaceType.JUPYTER
    assert config.system is DisplayColorSystem.ANSI_RGB
    assert config.style is DarkLowContrastColorStyles.ONE_DARK_PYGMENTS
    assert config.dark is True
    assert config.bg is True
    assert config.fonts == ('Menlo', 'monospace')
    assert config.font_size == 16
    assert config.font_weight == 400
    assert config.line_height == 1.0
    assert config.h_overflow is HorizontalOverflowMode.CROP
    assert config.v_overflow is VerticalOverflowMode.CROP_TOP
    assert config.panel is PanelDesign.PANELS
    assert config.title_at_top is False
    assert config.min_panel_width == 5
    assert config.max_title_height == MaxTitleHeight.ZERO
    assert config.min_crop_width == 20
    assert config.use_min_crop_width is True
    assert config.max_panels_hor == 15
    assert config.max_nesting_depth == 5
    assert config.justify is Justify.RIGHT

    config = OutputConfig(
        tab='2',  # pyright: ignore[reportArgumentType]
        indent='4',  # pyright: ignore[reportArgumentType]
        printer='rich',
        # Any syntax language string supported by the pygments library should be accepted
        syntax='c++',
        freedom='3',  # pyright: ignore[reportArgumentType]
        debug='yes',  # pyright: ignore[reportArgumentType]
        ui='terminal',
        system='256',
        # Any color style string supported by the pygments library should be accepted
        # Note: the lilypond color style is for use with the lilypond music notation software and as
        #       thus excluded from the list of valid color styles in Omnipy, but it is still a valid
        #       color style in the Pygments library.
        style='lilypond',
        dark=1,  # pyright: ignore[reportArgumentType]
        bg=1,  # pyright: ignore[reportArgumentType]
        fonts=[],  # pyright: ignore[reportArgumentType]
        font_size='16',  # pyright: ignore[reportArgumentType]
        font_weight='400',  # pyright: ignore[reportArgumentType]
        line_height='1',  # pyright: ignore[reportArgumentType]
        h_overflow='ellipsis',
        v_overflow='crop_bottom',
        panel='table',
        title_at_top=0,  # pyright: ignore[reportArgumentType]
        max_title_height=1,
        min_panel_width='5',  # pyright: ignore[reportArgumentType]
        min_crop_width='20',  # pyright: ignore[reportArgumentType]
        use_min_crop_width=1,  # pyright: ignore[reportArgumentType]
        max_panels_hor=None,
        max_nesting_depth=None,
        justify='right',
    )
    assert config.tab == 2
    assert config.indent == 4
    assert config.printer is PrettyPrinterLib.RICH
    assert config.syntax == 'c++'
    assert config.freedom == 3.0
    assert config.debug is True
    assert config.ui is UserInterfaceType.TERMINAL
    assert config.system is DisplayColorSystem.ANSI_256
    assert config.style == 'lilypond'
    assert config.dark is True
    assert config.bg is True
    assert config.fonts == ()
    assert config.font_size == 16
    assert config.font_weight == 400
    assert config.line_height == 1.0
    assert config.h_overflow is HorizontalOverflowMode.ELLIPSIS
    assert config.v_overflow is VerticalOverflowMode.CROP_BOTTOM
    assert config.panel is PanelDesign.TABLE
    assert config.title_at_top is False
    assert config.max_title_height == MaxTitleHeight.ONE
    assert config.min_panel_width == 5
    assert config.min_crop_width == 20
    assert config.use_min_crop_width is True
    assert config.max_panels_hor is None
    assert config.max_nesting_depth is None
    assert config.justify is Justify.RIGHT

    config = OutputConfig(
        freedom=None,
        font_weight=None,
        font_size=None,
        line_height=None,
    )
    assert config.font_size is None
    assert config.font_weight is None
    assert config.line_height is None


def test_output_config_hashable() -> None:
    config_1 = OutputConfig()

    config_2 = OutputConfig()
    assert hash(config_1) == hash(config_2)

    config_settings: list[dict[str, Any]] = [
        {'tab': 2},
        {'indent': 4},
        {'printer': PrettyPrinterLib.DEVTOOLS},
        {'syntax': SyntaxLanguageSpec.XML},
        {'freedom': 1.0},
        {'debug': True},
        {'ui': UserInterfaceType.JUPYTER},
        {'system': DisplayColorSystem.ANSI_256},
        {'style': LightHighContrastColorStyles.XCODE_PYGMENTS},
        {'dark': DarkBackground.TRUE},
        {'bg': True},
        {'fonts': ()},
        {'font_size': 16},
        {'font_weight': 400},
        {'line_height': 1.0},
        {'h_overflow': HorizontalOverflowMode.ELLIPSIS},
        {'v_overflow': VerticalOverflowMode.CROP_TOP},
        {'panel': PanelDesign.PANELS},
        {'title_at_top': False},
        {'min_panel_width': 5},
        {'max_title_height': MaxTitleHeight.ZERO},
        {'min_crop_width': 20},
        {'use_min_crop_width': True},
        {'max_panels_hor': 15},
        {'max_nesting_depth': 5},
        {'justify': Justify.RIGHT},
    ]

    prev_hash = hash(config_1)
    for setting in config_settings:
        config_3 = OutputConfig(**setting)
        config_4 = OutputConfig(**setting)

        assert hash(config_3) != prev_hash
        assert hash(config_3) == hash(config_4)

        prev_hash = hash(config_3)


# noinspection PyDataclass
def test_fail_output_config_no_assignments() -> None:
    config = OutputConfig()

    with pytest.raises(AttributeError):
        config.tab = 3  # pyright: ignore[reportAttributeAccessIssue]

    with pytest.raises(AttributeError):
        config.indent = 3  # pyright: ignore[reportAttributeAccessIssue]

    with pytest.raises(AttributeError):
        config.printer = PrettyPrinterLib.DEVTOOLS  # pyright: ignore[reportAttributeAccessIssue]

    with pytest.raises(AttributeError):
        config.syntax = SyntaxLanguageSpec.XML  # pyright: ignore[reportAttributeAccessIssue]

    with pytest.raises(AttributeError):
        config.freedom = 3.0  # pyright: ignore[reportAttributeAccessIssue]

    with pytest.raises(AttributeError):
        config.debug = False  # pyright: ignore[reportAttributeAccessIssue]

    with pytest.raises(AttributeError):
        config.ui = UserInterfaceType.JUPYTER  # pyright: ignore[reportAttributeAccessIssue]

    with pytest.raises(AttributeError):
        config.system = DisplayColorSystem.WINDOWS_LEGACY  # pyright: ignore[reportAttributeAccessIssue]

    with pytest.raises(AttributeError):
        config.style = DarkLowContrastColorStyles.GRUVBOX_DARK_PYGMENTS  # pyright: ignore[reportAttributeAccessIssue]

    with pytest.raises(AttributeError):
        config.dark = True  # pyright: ignore[reportAttributeAccessIssue]

    with pytest.raises(AttributeError):
        config.bg = True  # pyright: ignore[reportAttributeAccessIssue]

    with pytest.raises(AttributeError):
        config.fonts = ('Menlo', 'monospace')  # pyright: ignore[reportAttributeAccessIssue]

    with pytest.raises(AttributeError):
        config.font_size = 18  # pyright: ignore[reportAttributeAccessIssue]

    with pytest.raises(AttributeError):
        config.font_weight = 500  # pyright: ignore[reportAttributeAccessIssue]

    with pytest.raises(AttributeError):
        config.line_height = 1.5  # pyright: ignore[reportAttributeAccessIssue]

    with pytest.raises(AttributeError):
        config.h_overflow = HorizontalOverflowMode.ELLIPSIS  # pyright: ignore[reportAttributeAccessIssue]

    with pytest.raises(AttributeError):
        config.v_overflow = VerticalOverflowMode.CROP_TOP  # pyright: ignore[reportAttributeAccessIssue]

    with pytest.raises(AttributeError):
        config.panel = PanelDesign.PANELS  # pyright: ignore[reportAttributeAccessIssue]

    with pytest.raises(AttributeError):
        config.title_at_top = False  # pyright: ignore[reportAttributeAccessIssue]

    with pytest.raises(AttributeError):
        config.min_panel_width = 5  # pyright: ignore[reportAttributeAccessIssue]

    with pytest.raises(AttributeError):
        config.max_title_height = MaxTitleHeight.ONE  # pyright: ignore[reportAttributeAccessIssue]

    with pytest.raises(AttributeError):
        config.min_crop_width = 20  # pyright: ignore[reportAttributeAccessIssue]

    with pytest.raises(AttributeError):
        config.use_min_crop_width = True  # pyright: ignore[reportAttributeAccessIssue]

    with pytest.raises(AttributeError):
        config.max_panels_hor = 15  # pyright: ignore[reportAttributeAccessIssue]

    with pytest.raises(AttributeError):
        config.max_nesting_depth = 5  # pyright: ignore[reportAttributeAccessIssue]

    with pytest.raises(AttributeError):
        config.justify = Justify.RIGHT  # pyright: ignore[reportAttributeAccessIssue]


def test_fail_output_config_if_invalid_params() -> None:
    with pytest.raises(ValueError):
        OutputConfig(tab=-1)

    with pytest.raises(ValueError):
        OutputConfig(tab=None)  # pyright: ignore[reportArgumentType]

    with pytest.raises(ValueError):
        OutputConfig(indent=-1)

    with pytest.raises(ValueError):
        OutputConfig(indent=None)  # pyright: ignore[reportArgumentType]

    with pytest.raises(ValueError):
        OutputConfig(printer=None)  # pyright: ignore[reportArgumentType]

    with pytest.raises(ValueError):
        OutputConfig(syntax='xyz')

    with pytest.raises(ValueError):
        OutputConfig(freedom=-1)

    with pytest.raises(ValueError):
        OutputConfig(debug=None)  # pyright: ignore[reportArgumentType]

    with pytest.raises(ValueError):
        OutputConfig(ui=None)  # pyright: ignore[reportArgumentType]

    with pytest.raises(ValueError):
        OutputConfig(system=None)  # pyright: ignore[reportArgumentType]

    with pytest.raises(ValueError):
        OutputConfig(style='red')

    with pytest.raises(ValueError):
        OutputConfig(dark=None)  # pyright: ignore[reportArgumentType]

    with pytest.raises(ValueError):
        OutputConfig(bg=None)  # pyright: ignore[reportArgumentType]

    with pytest.raises(ValueError):
        OutputConfig(fonts=None)  # pyright: ignore[reportArgumentType]

    with pytest.raises(ValueError):
        OutputConfig(font_size=-1)

    with pytest.raises(ValueError):
        OutputConfig(font_weight=-1)

    with pytest.raises(ValueError):
        OutputConfig(line_height=-1)

    with pytest.raises(ValueError):
        OutputConfig(h_overflow=None)  # pyright: ignore[reportArgumentType]

    with pytest.raises(ValueError):
        OutputConfig(v_overflow=None)  # pyright: ignore[reportArgumentType]

    with pytest.raises(ValueError):
        OutputConfig(panel=None)  # pyright: ignore[reportArgumentType]

    with pytest.raises(ValueError):
        OutputConfig(title_at_top=None)  # pyright: ignore[reportArgumentType]

    with pytest.raises(ValueError):
        OutputConfig(max_title_height=None)  # pyright: ignore[reportArgumentType]

    with pytest.raises(ValueError):
        OutputConfig(min_panel_width=None)  # pyright: ignore[reportArgumentType]

    with pytest.raises(ValueError):
        OutputConfig(min_crop_width=None)  # pyright: ignore[reportArgumentType]

    with pytest.raises(ValueError):
        # min_crop_width must be larger or equal to min_panel_width
        OutputConfig(min_panel_width=20, min_crop_width=10)

    with pytest.raises(ValueError):
        OutputConfig(use_min_crop_width=None)  # pyright: ignore[reportArgumentType]

    with pytest.raises(ValueError):
        OutputConfig(max_panels_hor=-1)

    with pytest.raises(ValueError):
        OutputConfig(max_nesting_depth=-1)

    with pytest.raises(ValueError):
        OutputConfig(justify=None)  # pyright: ignore[reportArgumentType]


def test_output_config_default_values() -> None:
    config = OutputConfig()
    assert config.tab == 4
    assert config.indent == 2
    assert config.printer is PrettyPrinterLib.AUTO
    assert config.syntax is SyntaxLanguageSpec.AUTO
    assert config.freedom == 2.5
    assert config.debug is False
    assert config.ui is UserInterfaceType.AUTO
    assert config.system is DisplayColorSystem.AUTO
    assert config.style is RecommendedColorStyles.AUTO
    assert config.dark is DarkBackground.AUTO
    assert config.bg is False
    assert config.fonts == (
        'Menlo',
        'DejaVu Sans Mono',
        'Consolas',
        'Courier New',
        'monospace',
    )
    assert config.font_size == 14
    assert config.font_weight == 400
    assert config.line_height == 1.25
    assert config.h_overflow is HorizontalOverflowMode.ELLIPSIS
    assert config.v_overflow is VerticalOverflowMode.ELLIPSIS_BOTTOM
    assert config.panel is PanelDesign.TABLE
    assert config.title_at_top is True
    assert config.min_panel_width == 3
    assert config.max_title_height is MaxTitleHeight.AUTO
    assert config.min_crop_width == 33
    assert config.use_min_crop_width is False
    assert config.max_panels_hor == 9
    assert config.max_nesting_depth == 3
    assert config.justify is Justify.LEFT


def test_fail_output_config_if_extra_params() -> None:
    with pytest.raises(TypeError):
        OutputConfig(indent=4, debug=True, extra=2)  # type: ignore


def test_fail_output_config_no_positional_parameters() -> None:
    with pytest.raises(TypeError):
        OutputConfig(2, True)  # type: ignore


def test_output_config_fail_invalid_syntax() -> None:
    with pytest.raises(ValueError):
        OutputConfig(syntax='invalid_syntax')


def test_output_config_fail_invalid_style() -> None:
    with pytest.raises(ValueError):
        OutputConfig(style='invalid_style')


def test_output_config_cleaned_style() -> None:
    OutputConfig(style='ansi_dark')


def test_output_config_fail_min_crop_width_smaller_than_min_panel_width() -> None:
    with pytest.raises(ValueError):
        OutputConfig(min_panel_width=10, min_crop_width=5)
