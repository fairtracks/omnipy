from typing import Annotated, Any, Iterator

import pygments.styles
import pytest

from omnipy.data._display.config import OutputConfig
from omnipy.shared.enums.colorstyles import (DarkLowContrastColorStyles,
                                             LightHighContrastColorStyles,
                                             RecommendedColorStyles)
from omnipy.shared.enums.display import (DisplayColorSystem,
                                         HorizontalOverflowMode,
                                         Justify,
                                         MaxTitleHeight,
                                         PanelDesign,
                                         PrettyPrinterLib,
                                         SyntaxLanguage,
                                         VerticalOverflowMode)
from omnipy.shared.enums.ui import UserInterfaceType


def test_output_config() -> None:
    config = OutputConfig(
        tab=2,
        indent=4,
        printer=PrettyPrinterLib.DEVTOOLS,
        lang=SyntaxLanguage.JSON,
        freedom=3.5,
        debug=True,
        ui=UserInterfaceType.JUPYTER,
        system=DisplayColorSystem.ANSI_RGB,
        style=DarkLowContrastColorStyles.ONE_DARK_PYGMENTS,
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
        justify=Justify.RIGHT,
    )

    assert config.tab == 2
    assert config.indent == 4
    assert config.printer is PrettyPrinterLib.DEVTOOLS
    assert config.lang is SyntaxLanguage.JSON
    assert config.freedom == 3.5
    assert config.debug is True
    assert config.ui is UserInterfaceType.JUPYTER
    assert config.system is DisplayColorSystem.ANSI_RGB
    assert config.style is DarkLowContrastColorStyles.ONE_DARK_PYGMENTS
    assert config.bg is True
    assert config.fonts == ('Menlo', 'monospace')
    assert config.font_size == 16
    assert config.font_weight == 400
    assert config.line_height == 1.0
    assert config.h_overflow is HorizontalOverflowMode.CROP
    assert config.v_overflow is VerticalOverflowMode.CROP_TOP
    assert config.panel is PanelDesign.PANELS
    assert config.title_at_top is False
    assert config.max_title_height == MaxTitleHeight.ZERO
    assert config.justify is Justify.RIGHT

    config = OutputConfig(
        tab='2',  # type: ignore[arg-type]
        indent='4',  # type: ignore[arg-type]
        printer='rich',
        # Any language string supported by the pygments library should be accepted
        lang='c++',
        freedom='3',  # type: ignore[arg-type]
        debug='yes',  # type: ignore[arg-type]
        ui='terminal',
        system='256',
        # Any color style string supported by the pygments library should be accepted
        # Note: the lilypond color style is for use with the lilypond music notation software and as
        #       thus excluded from the list of valid color styles in Omnipy, but it is still a valid
        #       color style in the Pygments library.
        style='lilypond',
        bg=1,  # type: ignore[arg-type]
        fonts=[],  # type: ignore[arg-type]
        font_size='16',  # type: ignore[arg-type]
        font_weight='400',  # type: ignore[arg-type]
        line_height='1',  # type: ignore[arg-type]
        h_overflow='ellipsis',
        v_overflow='crop_bottom',
        panel='table_grid',
        title_at_top=0,  # type: ignore[arg-type]
        max_title_height=1,
        justify='right',
    )
    assert config.tab == 2
    assert config.indent == 4
    assert config.printer is PrettyPrinterLib.RICH
    assert config.lang == 'c++'
    assert config.freedom == 3.0
    assert config.debug is True
    assert config.ui is UserInterfaceType.TERMINAL
    assert config.system is DisplayColorSystem.ANSI_256
    assert config.style == 'lilypond'
    assert config.bg is True
    assert config.fonts == ()
    assert config.font_size == 16
    assert config.font_weight == 400
    assert config.line_height == 1.0
    assert config.h_overflow is HorizontalOverflowMode.ELLIPSIS
    assert config.v_overflow is VerticalOverflowMode.CROP_BOTTOM
    assert config.panel is PanelDesign.TABLE_GRID
    assert config.title_at_top is False
    assert config.max_title_height == MaxTitleHeight.ONE
    assert config.justify is Justify.RIGHT

    config = OutputConfig(
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
        {
            'tab': 2
        },
        {
            'indent': 4
        },
        {
            'printer': PrettyPrinterLib.DEVTOOLS
        },
        {
            'lang': SyntaxLanguage.XML
        },
        {
            'freedom': 1.0
        },
        {
            'debug': True
        },
        {
            'ui': UserInterfaceType.JUPYTER
        },
        {
            'system': DisplayColorSystem.ANSI_256
        },
        {
            'style': LightHighContrastColorStyles.XCODE_PYGMENTS
        },
        {
            'bg': True
        },
        {
            'fonts': ()
        },
        {
            'font_size': 16
        },
        {
            'font_weight': 400
        },
        {
            'line_height': 1.0
        },
        {
            'h_overflow': HorizontalOverflowMode.ELLIPSIS
        },
        {
            'v_overflow': VerticalOverflowMode.CROP_TOP
        },
        {
            'panel': PanelDesign.PANELS
        },
        {
            'title_at_top': False
        },
        {
            'max_title_height': MaxTitleHeight.ZERO
        },
        {
            'justify': Justify.RIGHT
        },
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
        config.tab = 3  # type: ignore[misc]

    with pytest.raises(AttributeError):
        config.indent = 3  # type: ignore[misc]

    with pytest.raises(AttributeError):
        config.printer = PrettyPrinterLib.DEVTOOLS  # type: ignore[misc]

    with pytest.raises(AttributeError):
        config.lang = SyntaxLanguage.XML  # type: ignore[misc]

    with pytest.raises(AttributeError):
        config.freedom = 3.0  # type: ignore[misc]

    with pytest.raises(AttributeError):
        config.debug = False  # type: ignore[misc]

    with pytest.raises(AttributeError):
        config.ui = UserInterfaceType.JUPYTER  # type: ignore[misc]

    with pytest.raises(AttributeError):
        config.system = DisplayColorSystem.WINDOWS_LEGACY  # type: ignore[misc]

    with pytest.raises(AttributeError):
        config.style = DarkLowContrastColorStyles.GRUVBOX_DARK  # type: ignore[misc]

    with pytest.raises(AttributeError):
        config.bg = True  # type: ignore[misc]

    with pytest.raises(AttributeError):
        config.fonts = ('Menlo', 'monospace')  # type: ignore[misc]

    with pytest.raises(AttributeError):
        config.font_size = 18  # type: ignore[misc]

    with pytest.raises(AttributeError):
        config.font_weight = 500  # type: ignore[misc]

    with pytest.raises(AttributeError):
        config.line_height = 1.5  # type: ignore[misc]

    with pytest.raises(AttributeError):
        config.h_overflow = HorizontalOverflowMode.ELLIPSIS  # type: ignore[misc]

    with pytest.raises(AttributeError):
        config.v_overflow = VerticalOverflowMode.CROP_TOP  # type: ignore[misc]

    with pytest.raises(AttributeError):
        config.panel = PanelDesign.PANELS  # type: ignore[misc]

    with pytest.raises(AttributeError):
        config.title_at_top = False  # type: ignore[misc]

    with pytest.raises(AttributeError):
        config.max_title_height = MaxTitleHeight.ONE  # type: ignore[misc]

    with pytest.raises(AttributeError):
        config.justify = Justify.RIGHT  # type: ignore[misc]


def test_fail_output_config_if_invalid_params() -> None:
    with pytest.raises(ValueError):
        OutputConfig(tab=-1)

    with pytest.raises(ValueError):
        OutputConfig(tab=None)  # type: ignore[arg-type]

    with pytest.raises(ValueError):
        OutputConfig(indent=-1)

    with pytest.raises(ValueError):
        OutputConfig(indent=None)  # type: ignore[arg-type]

    with pytest.raises(ValueError):
        OutputConfig(printer=None)  # type: ignore[arg-type]

    with pytest.raises(ValueError):
        OutputConfig(lang='xyz')

    with pytest.raises(ValueError):
        OutputConfig(freedom=-1)

    with pytest.raises(ValueError):
        OutputConfig(debug=None)  # type: ignore[arg-type]

    with pytest.raises(ValueError):
        OutputConfig(ui=None)  # type: ignore[arg-type]

    with pytest.raises(ValueError):
        OutputConfig(system=None)  # type: ignore[arg-type]

    with pytest.raises(ValueError):
        OutputConfig(style='red')

    with pytest.raises(ValueError):
        OutputConfig(bg=None)  # type: ignore[arg-type]

    with pytest.raises(ValueError):
        OutputConfig(fonts=None)  # type: ignore[arg-type]

    with pytest.raises(ValueError):
        OutputConfig(font_weight=-1)

    with pytest.raises(ValueError):
        OutputConfig(font_weight=-1)

    with pytest.raises(ValueError):
        OutputConfig(font_weight=-1)

    with pytest.raises(ValueError):
        OutputConfig(h_overflow=None)  # type: ignore[arg-type]

    with pytest.raises(ValueError):
        OutputConfig(v_overflow=None)  # type: ignore[arg-type]

    with pytest.raises(ValueError):
        OutputConfig(panel=None)  # type: ignore[arg-type]

    with pytest.raises(ValueError):
        OutputConfig(title_at_top=None)  # type: ignore[arg-type]

    with pytest.raises(ValueError):
        OutputConfig(max_title_height=None)  # type: ignore[arg-type]

    with pytest.raises(ValueError):
        OutputConfig(justify=None)  # type: ignore[arg-type]


def test_output_config_default_values() -> None:
    config = OutputConfig()
    assert config.tab == 4
    assert config.indent == 2
    assert config.printer is PrettyPrinterLib.AUTO
    assert config.lang is SyntaxLanguage.PYTHON
    assert config.freedom == 2.5
    assert config.debug is False
    assert config.ui is UserInterfaceType.TERMINAL
    assert config.system is DisplayColorSystem.AUTO
    assert config.style is RecommendedColorStyles.ANSI_DARK
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
    assert config.panel is PanelDesign.TABLE_GRID
    assert config.title_at_top is True
    assert config.max_title_height is MaxTitleHeight.AUTO
    assert config.justify is Justify.LEFT


def test_fail_output_config_if_extra_params() -> None:
    with pytest.raises(TypeError):
        OutputConfig(indent=4, debug=True, extra=2)  # type: ignore


def test_fail_output_config_no_positional_parameters() -> None:
    with pytest.raises(TypeError):
        OutputConfig(2, True)  # type: ignore


def test_config_autoimport_base16_color_style(
        register_runtime: Annotated[Iterator[None], pytest.fixture]) -> None:
    style_name = 'zenburn-t16'
    OutputConfig(style=style_name)  # To trigger the auto-import
    pygments_style = pygments.styles.get_style_by_name(style_name)
    assert pygments_style.background_color == '#383838'
