from typing import Annotated

import pytest

from omnipy.data._display.config import (HighContrastLightColorStyles,
                                         LowerContrastDarkColorStyles,
                                         OutputConfig,
                                         PrettyPrinterLib,
                                         SpecialColorStyles,
                                         SyntaxLanguage)


def test_output_config(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:
    config = OutputConfig(
        indent_tab_size=4,
        debug_mode=True,
        pretty_printer=PrettyPrinterLib.DEVTOOLS,
        language=SyntaxLanguage.JSON,
        color_style=LowerContrastDarkColorStyles.ONE_DARK,
    )
    assert config.indent_tab_size == 4
    assert config.debug_mode is True
    assert config.pretty_printer is PrettyPrinterLib.DEVTOOLS
    assert config.language is SyntaxLanguage.JSON
    assert config.color_style is LowerContrastDarkColorStyles.ONE_DARK

    config = OutputConfig(
        indent_tab_size=0,
        debug_mode=False,
        pretty_printer='rich',  # type: ignore[arg-type]
        language='xml',
        color_style='xcode',
    )
    assert config.indent_tab_size == 0
    assert config.debug_mode is False
    assert config.pretty_printer is PrettyPrinterLib.RICH
    assert config.language is SyntaxLanguage.XML
    assert config.color_style is HighContrastLightColorStyles.XCODE


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

    config.pretty_printer = PrettyPrinterLib.DEVTOOLS
    assert config.pretty_printer is PrettyPrinterLib.DEVTOOLS

    with pytest.raises(ValueError):
        config.pretty_printer = 'something'  # type: ignore[assignment]

    config.language = None
    assert config.language is None

    # Any language string supported by the pygments library should be accepted
    config.language = 'c++'
    assert config.language == 'c++'

    with pytest.raises(ValueError):
        config.language = '123'

    config.color_style = None
    assert config.color_style is None

    # Any color style string supported by the pygments library should be accepted
    # Note: the lilypond color style is for use with the lilypond music notation software and as
    #       thus excluded from the list of valid color styles in Omnipy, but it is still a valid
    #       color style in the Pygments library.
    config.color_style = 'lilypond'
    assert config.color_style == 'lilypond'

    with pytest.raises(ValueError):
        config.color_style = '123'


def test_fail_output_config_if_invalid_params(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:
    with pytest.raises(ValueError):
        OutputConfig(indent_tab_size=-1)

    with pytest.raises(ValueError):
        OutputConfig(indent_tab_size=None)  # type: ignore

    with pytest.raises(ValueError):
        OutputConfig(debug_mode=None)  # type: ignore

    with pytest.raises(ValueError):
        OutputConfig(pretty_printer=None)  # type: ignore

    with pytest.raises(ValueError):
        OutputConfig(language='xyz')


def test_output_config_default_values(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:
    config = OutputConfig()
    assert config.indent_tab_size == 2
    assert config.debug_mode is False
    assert config.pretty_printer is PrettyPrinterLib.RICH
    assert config.language is SyntaxLanguage.PYTHON
    assert config.color_style is SpecialColorStyles.ANSI_LIGHT


def test_fail_output_config_if_extra_params(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:
    with pytest.raises(TypeError):
        OutputConfig(indent_tab_size=4, debug_mode=True, extra=2)  # type: ignore


def test_fail_output_config_no_positional_parameters(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:
    with pytest.raises(TypeError):
        OutputConfig(2, True)  # type: ignore
