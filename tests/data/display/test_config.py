from typing import Annotated

import pygments.styles
import pytest

from omnipy.data._display.config import (ConsoleColorSystem,
                                         DarkLowContrastColorStyles,
                                         HorizontalOverflowMode,
                                         LightHighContrastColorStyles,
                                         OutputConfig,
                                         PrettyPrinterLib,
                                         SpecialColorStyles,
                                         SyntaxLanguage,
                                         VerticalOverflowMode)


def test_output_config(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:
    config = OutputConfig(
        indent_tab_size=4,
        debug_mode=True,
        pretty_printer=PrettyPrinterLib.DEVTOOLS,
        language=SyntaxLanguage.JSON,
        console_color_system=ConsoleColorSystem.ANSI_RGB,
        color_style=DarkLowContrastColorStyles.ONE_DARK,
        css_font_families=('Menlo', 'monospace'),
        css_font_size=16,
        css_font_weight=400,
        css_line_height=1.0,
        horizontal_overflow_mode=HorizontalOverflowMode.CROP,
        vertical_overflow_mode=VerticalOverflowMode.CROP_TOP,
    )

    assert config.indent_tab_size == 4
    assert config.debug_mode is True
    assert config.pretty_printer is PrettyPrinterLib.DEVTOOLS
    assert config.language is SyntaxLanguage.JSON
    assert config.console_color_system is ConsoleColorSystem.ANSI_RGB
    assert config.color_style is DarkLowContrastColorStyles.ONE_DARK
    assert config.css_font_families == ('Menlo', 'monospace')
    assert config.css_font_size == 16
    assert config.css_font_weight == 400
    assert config.css_line_height == 1.0
    assert config.horizontal_overflow_mode is HorizontalOverflowMode.CROP
    assert config.vertical_overflow_mode is VerticalOverflowMode.CROP_TOP

    config = OutputConfig(
        indent_tab_size='4',  # type: ignore[arg-type]
        debug_mode='yes',  # type: ignore[arg-type]
        pretty_printer='rich',  # type: ignore[arg-type]
        language='xml',
        console_color_system='256',  # type: ignore[arg-type]
        color_style='xcode',
        css_font_families=[],  # type: ignore[arg-type]
        css_font_size='16',  # type: ignore[arg-type]
        css_font_weight='400',  # type: ignore[arg-type]
        css_line_height='1',  # type: ignore[arg-type]
        horizontal_overflow_mode='ellipsis',  # type: ignore[arg-type]
        vertical_overflow_mode='crop_bottom',  # type: ignore[arg-type]
    )
    assert config.indent_tab_size == 4
    assert config.debug_mode is True
    assert config.pretty_printer is PrettyPrinterLib.RICH
    assert config.language is SyntaxLanguage.XML
    assert config.console_color_system is ConsoleColorSystem.ANSI_256
    assert config.color_style is LightHighContrastColorStyles.XCODE
    assert config.css_font_families == ()
    assert config.css_font_size == 16
    assert config.css_font_weight == 400
    assert config.css_line_height == 1.0
    assert config.horizontal_overflow_mode is HorizontalOverflowMode.ELLIPSIS
    assert config.vertical_overflow_mode is VerticalOverflowMode.CROP_BOTTOM

    config = OutputConfig(
        css_font_weight=None,
        css_font_size=None,
        css_line_height=None,
    )
    assert config.css_font_size is None
    assert config.css_font_weight is None
    assert config.css_line_height is None


def test_output_config_validate_assignments(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:
    config = OutputConfig(indent_tab_size=4, debug_mode=True)

    config.indent_tab_size = 3
    assert config.indent_tab_size == 3

    with pytest.raises(ValueError):
        config.indent_tab_size = 'abc'  # type: ignore[assignment]

    config.debug_mode = False
    assert config.debug_mode is False

    with pytest.raises(ValueError):
        config.debug_mode = None  # type: ignore[assignment]

    config.pretty_printer = 'devtools'  # type: ignore[assignment]
    assert config.pretty_printer is PrettyPrinterLib.DEVTOOLS

    with pytest.raises(ValueError):
        config.pretty_printer = 'something'  # type: ignore[assignment]

    # Any language string supported by the pygments library should be accepted
    config.language = 'c++'
    assert config.language == 'c++'

    with pytest.raises(ValueError):
        config.language = '123'

    config.console_color_system = 'windows'  # type: ignore[assignment]
    assert config.console_color_system is ConsoleColorSystem.WINDOWS_LEGACY

    with pytest.raises(ValueError):
        config.console_color_system = 'abc'  # type: ignore[assignment]

    # Any color style string supported by the pygments library should be accepted
    # Note: the lilypond color style is for use with the lilypond music notation software and as
    #       thus excluded from the list of valid color styles in Omnipy, but it is still a valid
    #       color style in the Pygments library.
    config.color_style = 'lilypond'
    assert config.color_style == 'lilypond'

    with pytest.raises(ValueError):
        config.color_style = '123'

    config.css_font_families = ['Menlo', 'monospace']  # type: ignore[assignment]
    assert config.css_font_families == ('Menlo', 'monospace')

    with pytest.raises(ValueError):
        config.css_font_families = 'monospace'  # type: ignore[assignment]

    config.css_font_size = '18'  # type: ignore[assignment]
    assert config.css_font_size == 18

    with pytest.raises(ValueError):
        config.css_font_size = 'abc'  # type: ignore[assignment]

    config.css_font_weight = '500'  # type: ignore[assignment]
    assert config.css_font_weight == 500

    with pytest.raises(ValueError):
        config.css_font_weight = 'abc'  # type: ignore[assignment]

    config.css_line_height = '1.5'  # type: ignore[assignment]
    assert config.css_line_height == 1.5

    with pytest.raises(ValueError):
        config.css_line_height = 'abc'  # type: ignore[assignment]

    config.horizontal_overflow_mode = 'ellipsis'  # type: ignore[assignment]
    assert config.horizontal_overflow_mode is HorizontalOverflowMode.ELLIPSIS

    with pytest.raises(ValueError):
        config.horizontal_overflow_mode = 'abc'  # type: ignore[assignment]

    config.vertical_overflow_mode = 'crop_top'  # type: ignore[assignment]
    assert config.vertical_overflow_mode is VerticalOverflowMode.CROP_TOP

    with pytest.raises(ValueError):
        config.vertical_overflow_mode = 'abc'  # type: ignore[assignment]


def test_fail_output_config_if_invalid_params(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:
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
        OutputConfig(console_color_system=None)  # type: ignore[arg-type]

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


def test_output_config_default_values(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:
    config = OutputConfig()
    assert config.indent_tab_size == 2
    assert config.debug_mode is False
    assert config.pretty_printer is PrettyPrinterLib.RICH
    assert config.language is SyntaxLanguage.PYTHON
    assert config.console_color_system is ConsoleColorSystem.AUTO
    assert config.color_style is SpecialColorStyles.ANSI_DARK
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
    assert config.horizontal_overflow_mode is HorizontalOverflowMode.WORD_WRAP
    assert config.vertical_overflow_mode is VerticalOverflowMode.CROP_BOTTOM


def test_fail_output_config_if_extra_params(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:
    with pytest.raises(TypeError):
        OutputConfig(indent_tab_size=4, debug_mode=True, extra=2)  # type: ignore


def test_fail_output_config_no_positional_parameters(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:
    with pytest.raises(TypeError):
        OutputConfig(2, True)  # type: ignore


def test_config_autoimport_base16_color_style(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:
    style_name = 'tb16-zenburn'
    OutputConfig(color_style=style_name)  # To trigger the auto-import
    pygments_style = pygments.styles.get_style_by_name(style_name)
    assert pygments_style.background_color == '#383838'
