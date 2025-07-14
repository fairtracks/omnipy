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


def test_output_config() -> None:
    config = OutputConfig(
        tab_size=2,
        indent_tab_size=4,
        debug_mode=True,
        pretty_printer=PrettyPrinterLib.DEVTOOLS,
        language=SyntaxLanguage.JSON,
        proportional_freedom=3.5,
        color_system=DisplayColorSystem.ANSI_RGB,
        color_style=DarkLowContrastColorStyles.ONE_DARK,
        css_font_families=('Menlo', 'monospace'),
        css_font_size=16,
        css_font_weight=400,
        css_line_height=1.0,
        horizontal_overflow_mode=HorizontalOverflowMode.CROP,
        vertical_overflow_mode=VerticalOverflowMode.CROP_TOP,
        panel_design=PanelDesign.PANELS,
        panel_title_at_top=False,
        max_title_height=MaxTitleHeight.ZERO,
        justify_in_layout=Justify.RIGHT,
    )

    assert config.tab_size == 2
    assert config.indent_tab_size == 4
    assert config.debug_mode is True
    assert config.pretty_printer is PrettyPrinterLib.DEVTOOLS
    assert config.language is SyntaxLanguage.JSON
    assert config.proportional_freedom == 3.5
    assert config.color_system is DisplayColorSystem.ANSI_RGB
    assert config.color_style is DarkLowContrastColorStyles.ONE_DARK
    assert config.css_font_families == ('Menlo', 'monospace')
    assert config.css_font_size == 16
    assert config.css_font_weight == 400
    assert config.css_line_height == 1.0
    assert config.horizontal_overflow_mode is HorizontalOverflowMode.CROP
    assert config.vertical_overflow_mode is VerticalOverflowMode.CROP_TOP
    assert config.panel_design is PanelDesign.PANELS
    assert config.panel_title_at_top is False
    assert config.max_title_height == MaxTitleHeight.ZERO
    assert config.justify_in_layout is Justify.RIGHT

    config = OutputConfig(
        tab_size='2',  # type: ignore[arg-type]
        indent_tab_size='4',  # type: ignore[arg-type]
        debug_mode='yes',  # type: ignore[arg-type]
        pretty_printer='rich',
        # Any language string supported by the pygments library should be accepted
        language='c++',
        proportional_freedom='3',  # type: ignore[arg-type]
        color_system='256',
        # Any color style string supported by the pygments library should be accepted
        # Note: the lilypond color style is for use with the lilypond music notation software and as
        #       thus excluded from the list of valid color styles in Omnipy, but it is still a valid
        #       color style in the Pygments library.
        color_style='lilypond',
        css_font_families=[],  # type: ignore[arg-type]
        css_font_size='16',  # type: ignore[arg-type]
        css_font_weight='400',  # type: ignore[arg-type]
        css_line_height='1',  # type: ignore[arg-type]
        horizontal_overflow_mode='ellipsis',
        vertical_overflow_mode='crop_bottom',
        panel_design='table_grid',
        panel_title_at_top=0,  # type: ignore[arg-type]
        max_title_height=1,
        justify_in_layout='right',
    )
    assert config.tab_size == 2
    assert config.indent_tab_size == 4
    assert config.debug_mode is True
    assert config.pretty_printer is PrettyPrinterLib.RICH
    assert config.language == 'c++'
    assert config.proportional_freedom == 3.0
    assert config.color_system is DisplayColorSystem.ANSI_256
    assert config.color_style == 'lilypond'
    assert config.css_font_families == ()
    assert config.css_font_size == 16
    assert config.css_font_weight == 400
    assert config.css_line_height == 1.0
    assert config.horizontal_overflow_mode is HorizontalOverflowMode.ELLIPSIS
    assert config.vertical_overflow_mode is VerticalOverflowMode.CROP_BOTTOM
    assert config.panel_design is PanelDesign.TABLE_GRID
    assert config.panel_title_at_top is False
    assert config.max_title_height == MaxTitleHeight.ONE
    assert config.justify_in_layout is Justify.RIGHT

    config = OutputConfig(
        css_font_weight=None,
        css_font_size=None,
        css_line_height=None,
    )
    assert config.css_font_size is None
    assert config.css_font_weight is None
    assert config.css_line_height is None


def test_output_config_hashable() -> None:
    config_1 = OutputConfig()

    config_2 = OutputConfig()
    assert hash(config_1) == hash(config_2)

    config_settings: list[dict[str, Any]] = [
        {
            'tab_size': 2
        },
        {
            'indent_tab_size': 4
        },
        {
            'debug_mode': True
        },
        {
            'pretty_printer': PrettyPrinterLib.DEVTOOLS
        },
        {
            'language': SyntaxLanguage.XML
        },
        {
            'proportional_freedom': 1.0
        },
        {
            'color_system': DisplayColorSystem.ANSI_256
        },
        {
            'color_style': LightHighContrastColorStyles.XCODE
        },
        {
            'css_font_families': ()
        },
        {
            'css_font_size': 16
        },
        {
            'css_font_weight': 400
        },
        {
            'css_line_height': 1.0
        },
        {
            'horizontal_overflow_mode': HorizontalOverflowMode.ELLIPSIS
        },
        {
            'vertical_overflow_mode': VerticalOverflowMode.CROP_TOP
        },
        {
            'panel_design': PanelDesign.PANELS
        },
        {
            'panel_title_at_top': False
        },
        {
            'max_title_height': MaxTitleHeight.ZERO
        },
        {
            'justify_in_layout': Justify.RIGHT
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
        config.tab_size = 3  # type: ignore[misc]

    with pytest.raises(AttributeError):
        config.indent_tab_size = 3  # type: ignore[misc]

    with pytest.raises(AttributeError):
        config.debug_mode = False  # type: ignore[misc]

    with pytest.raises(AttributeError):
        config.pretty_printer = PrettyPrinterLib.DEVTOOLS  # type: ignore[misc]

    with pytest.raises(AttributeError):
        config.language = SyntaxLanguage.XML  # type: ignore[misc]

    with pytest.raises(AttributeError):
        config.proportional_freedom = 3.0  # type: ignore[misc]

    with pytest.raises(AttributeError):
        config.color_system = DisplayColorSystem.WINDOWS_LEGACY  # type: ignore[misc]

    with pytest.raises(AttributeError):
        config.color_style = DarkLowContrastColorStyles.GRUVBOX_DARK  # type: ignore[misc]

    with pytest.raises(AttributeError):
        config.css_font_families = ('Menlo', 'monospace')  # type: ignore[misc]

    with pytest.raises(AttributeError):
        config.css_font_size = 18  # type: ignore[misc]

    with pytest.raises(AttributeError):
        config.css_font_weight = 500  # type: ignore[misc]

    with pytest.raises(AttributeError):
        config.css_line_height = 1.5  # type: ignore[misc]

    with pytest.raises(AttributeError):
        config.horizontal_overflow_mode = HorizontalOverflowMode.ELLIPSIS  # type: ignore[misc]

    with pytest.raises(AttributeError):
        config.vertical_overflow_mode = VerticalOverflowMode.CROP_TOP  # type: ignore[misc]

    with pytest.raises(AttributeError):
        config.panel_design = PanelDesign.PANELS  # type: ignore[misc]

    with pytest.raises(AttributeError):
        config.panel_title_at_top = False  # type: ignore[misc]

    with pytest.raises(AttributeError):
        config.max_title_height = MaxTitleHeight.ONE  # type: ignore[misc]

    with pytest.raises(AttributeError):
        config.justify_in_layout = Justify.RIGHT  # type: ignore[misc]


def test_fail_output_config_if_invalid_params() -> None:
    with pytest.raises(ValueError):
        OutputConfig(tab_size=-1)

    with pytest.raises(ValueError):
        OutputConfig(tab_size=None)  # type: ignore[arg-type]

    with pytest.raises(ValueError):
        OutputConfig(indent_tab_size=-1)

    with pytest.raises(ValueError):
        OutputConfig(indent_tab_size=None)  # type: ignore[arg-type]

    with pytest.raises(ValueError):
        OutputConfig(debug_mode=None)  # type: ignore[arg-type]

    with pytest.raises(ValueError):
        OutputConfig(pretty_printer=None)  # type: ignore[arg-type]

    with pytest.raises(ValueError):
        OutputConfig(language='xyz')

    with pytest.raises(ValueError):
        OutputConfig(proportional_freedom=-1)

    with pytest.raises(ValueError):
        OutputConfig(color_system=None)  # type: ignore[arg-type]

    with pytest.raises(ValueError):
        OutputConfig(color_style='red')

    with pytest.raises(ValueError):
        OutputConfig(css_font_families=None)  # type: ignore[arg-type]

    with pytest.raises(ValueError):
        OutputConfig(css_font_weight=-1)

    with pytest.raises(ValueError):
        OutputConfig(css_font_weight=-1)

    with pytest.raises(ValueError):
        OutputConfig(css_font_weight=-1)

    with pytest.raises(ValueError):
        OutputConfig(horizontal_overflow_mode=None)  # type: ignore[arg-type]

    with pytest.raises(ValueError):
        OutputConfig(vertical_overflow_mode=None)  # type: ignore[arg-type]

    with pytest.raises(ValueError):
        OutputConfig(panel_design=None)  # type: ignore[arg-type]

    with pytest.raises(ValueError):
        OutputConfig(panel_title_at_top=None)  # type: ignore[arg-type]

    with pytest.raises(ValueError):
        OutputConfig(max_title_height=None)  # type: ignore[arg-type]

    with pytest.raises(ValueError):
        OutputConfig(justify_in_layout=None)  # type: ignore[arg-type]


def test_output_config_default_values() -> None:
    config = OutputConfig()
    assert config.tab_size == 4
    assert config.indent_tab_size == 2
    assert config.debug_mode is False
    assert config.pretty_printer is PrettyPrinterLib.RICH
    assert config.language is SyntaxLanguage.PYTHON
    assert config.proportional_freedom == 2.5
    assert config.color_system is DisplayColorSystem.AUTO
    assert config.color_style is RecommendedColorStyles.ANSI_DARK
    assert config.css_font_families == (
        'CommitMonoOmnipy',
        'Menlo',
        'DejaVu Sans Mono',
        'Consolas',
        'Courier New',
        'monospace',
    )
    assert config.css_font_size == 14
    assert config.css_font_weight == 450
    assert config.css_line_height == 1.35
    assert config.horizontal_overflow_mode is HorizontalOverflowMode.ELLIPSIS
    assert config.vertical_overflow_mode is VerticalOverflowMode.ELLIPSIS_BOTTOM
    assert config.panel_design is PanelDesign.TABLE_GRID
    assert config.panel_title_at_top is True
    assert config.max_title_height is MaxTitleHeight.AUTO
    assert config.justify_in_layout is Justify.LEFT


def test_fail_output_config_if_extra_params() -> None:
    with pytest.raises(TypeError):
        OutputConfig(indent_tab_size=4, debug_mode=True, extra=2)  # type: ignore


def test_fail_output_config_no_positional_parameters() -> None:
    with pytest.raises(TypeError):
        OutputConfig(2, True)  # type: ignore


def test_config_autoimport_base16_color_style(
        register_runtime: Annotated[Iterator[None], pytest.fixture]) -> None:
    style_name = 'tb16-zenburn'
    OutputConfig(color_style=style_name)  # To trigger the auto-import
    pygments_style = pygments.styles.get_style_by_name(style_name)
    assert pygments_style.background_color == '#383838'
