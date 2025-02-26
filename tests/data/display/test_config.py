from typing import Annotated

import pytest

from omnipy.data._display.config import (DarkLowContrastColorStyles,
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
        color_style=DarkLowContrastColorStyles.ONE_DARK,
        horizontal_overflow_mode=HorizontalOverflowMode.CROP,
        vertical_overflow_mode=VerticalOverflowMode.CROP_TOP,
    )

    assert config.indent_tab_size == 4
    assert config.debug_mode is True
    assert config.pretty_printer is PrettyPrinterLib.DEVTOOLS
    assert config.language is SyntaxLanguage.JSON
    assert config.color_style is DarkLowContrastColorStyles.ONE_DARK
    assert config.horizontal_overflow_mode is HorizontalOverflowMode.CROP

    config = OutputConfig(
        indent_tab_size=0,
        debug_mode=False,
        pretty_printer='rich',  # type: ignore[arg-type]
        language='xml',
        color_style='xcode',
        horizontal_overflow_mode='ellipsis',  # type: ignore[arg-type]
        vertical_overflow_mode='crop_bottom',  # type: ignore[arg-type]
    )
    assert config.indent_tab_size == 0
    assert config.debug_mode is False
    assert config.pretty_printer is PrettyPrinterLib.RICH
    assert config.language is SyntaxLanguage.XML
    assert config.color_style is LightHighContrastColorStyles.XCODE
    assert config.horizontal_overflow_mode is HorizontalOverflowMode.ELLIPSIS
    assert config.vertical_overflow_mode is VerticalOverflowMode.CROP_BOTTOM


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

    # Any color style string supported by the pygments library should be accepted
    # Note: the lilypond color style is for use with the lilypond music notation software and as
    #       thus excluded from the list of valid color styles in Omnipy, but it is still a valid
    #       color style in the Pygments library.
    config.color_style = 'lilypond'
    assert config.color_style == 'lilypond'

    with pytest.raises(ValueError):
        config.color_style = '123'

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
        OutputConfig(color_style='red')

    with pytest.raises(ValueError):
        OutputConfig(horizontal_overflow_mode=None)  # type: ignore[arg-type]


def test_output_config_default_values(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:
    config = OutputConfig()
    assert config.indent_tab_size == 2
    assert config.debug_mode is False
    assert config.pretty_printer is PrettyPrinterLib.RICH
    assert config.language is SyntaxLanguage.PYTHON
    assert config.color_style is SpecialColorStyles.ANSI_LIGHT
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
