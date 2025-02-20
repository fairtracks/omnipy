from textwrap import dedent
from typing import Annotated

import pytest

from omnipy.data._display.config import (HorizontalOverflowMode,
                                         LowerContrastLightColorStyles,
                                         OutputConfig,
                                         SyntaxLanguage,
                                         VerticalOverflowMode)
from omnipy.data._display.constraints import Constraints
from omnipy.data._display.dimensions import Dimensions
from omnipy.data._display.draft import DraftMonospacedOutput
from omnipy.data._display.frame import Frame
from omnipy.data._display.styling import StylizedMonospacedOutput


def test_stylized_output_init(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:

    output = StylizedMonospacedOutput('[123, 234, 345]',)

    assert output.content == '[123, 234, 345]'
    assert output.frame == Frame()
    assert output.constraints == Constraints()
    assert output.config == OutputConfig()

    draft = DraftMonospacedOutput(
        '[123, 234, 345]',
        frame=Frame(Dimensions(10, 10)),
        constraints=Constraints(),
        config=OutputConfig(
            language=SyntaxLanguage.PYTHON,
            color_style=None,
        ),
    )

    output = StylizedMonospacedOutput(draft)

    assert output.content == '[123, 234, 345]'
    assert output.frame is not draft.frame
    assert output.frame == draft.frame
    assert output.constraints is not draft.constraints
    assert output.constraints == draft.constraints
    assert output.config is not draft.config
    assert output.config == draft.config


def test_fail_stylized_output_if_extra_params(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:

    with pytest.raises(TypeError):
        StylizedMonospacedOutput('[123, 234, 345]', extra=123)  # type: ignore[call-overload]

    output = StylizedMonospacedOutput('[123, 234, 345]')
    output.extra = 123


def test_stylized_output_immutable_properties(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:

    output = StylizedMonospacedOutput('[123, 234, 345]',)

    with pytest.raises(AttributeError):
        output.content = '[234, 345, 456]'

    with pytest.raises(AttributeError):
        output.frame = Frame()

    with pytest.raises(AttributeError):
        output.constraints = Constraints()

    with pytest.raises(AttributeError):
        output.config = OutputConfig()


def test_plain_output_to_terminal(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:

    content = "MyClass({'abc': [123, 234]})"

    output = StylizedMonospacedOutput(content)
    assert output.plain.to_terminal() == "MyClass({'abc': [123, 234]})\n"
    assert output.within_frame.width is None
    assert output.within_frame.height is None

    output = StylizedMonospacedOutput(
        content,
        frame=Frame(Dimensions(21, None)),
        config=OutputConfig(
            color_style=LowerContrastLightColorStyles.MURPHY,
            horizontal_overflow_mode=HorizontalOverflowMode.WORD_WRAP),
    )
    assert output.plain.to_terminal() == dedent("""\
        MyClass({'abc': [123,
        234]})
        """)
    assert output.within_frame.width is True
    assert output.within_frame.height is None

    output = StylizedMonospacedOutput(
        content,
        frame=Frame(Dimensions(21, None)),
        config=OutputConfig(
            color_style=LowerContrastLightColorStyles.MURPHY,
            horizontal_overflow_mode=HorizontalOverflowMode.ELLIPSIS),
    )
    assert output.plain.to_terminal() == "MyClass({'abc': [123…\n"
    assert output.within_frame.width is True
    assert output.within_frame.height is None

    output = StylizedMonospacedOutput(
        content,
        frame=Frame(Dimensions(21, None)),
        config=OutputConfig(
            color_style=LowerContrastLightColorStyles.MURPHY,
            horizontal_overflow_mode=HorizontalOverflowMode.CROP),
    )
    assert output.plain.to_terminal() == "MyClass({'abc': [123,\n"
    assert output.within_frame.width is True
    assert output.within_frame.height is None

    output = StylizedMonospacedOutput(
        "MyClass({'abc': [123, 234]})",
        frame=Frame(Dimensions(9, 20)),
        config=OutputConfig(
            color_style=LowerContrastLightColorStyles.MURPHY,
            horizontal_overflow_mode=HorizontalOverflowMode.WORD_WRAP),
    )
    assert output.plain.to_terminal() == dedent("""\
        MyClass({
        'abc': 
        [123, 
        234]})
        """)  # noqa: W291
    assert output.within_frame.width is True
    assert output.within_frame.height is True

    output = StylizedMonospacedOutput(
        "MyClass({'abc': [123, 234]})",
        frame=Frame(Dimensions(9, 2)),
        config=OutputConfig(
            color_style=LowerContrastLightColorStyles.MURPHY,
            horizontal_overflow_mode=HorizontalOverflowMode.WORD_WRAP,
            vertical_overflow_mode=VerticalOverflowMode.CROP_BOTTOM,
        ))
    assert output.plain.to_terminal() == dedent("""\
        MyClass({
        'abc': 
        """)  # noqa: W291
    assert output.within_frame.width is True
    assert output.within_frame.height is True

    output = StylizedMonospacedOutput(
        "MyClass({'abc': [123, 234]})",
        frame=Frame(Dimensions(9, 2)),
        config=OutputConfig(
            color_style=LowerContrastLightColorStyles.MURPHY,
            horizontal_overflow_mode=HorizontalOverflowMode.WORD_WRAP,
            vertical_overflow_mode=VerticalOverflowMode.CROP_TOP,
        ))
    assert output.plain.to_terminal() == dedent("""\
        [123, 
        234]})
        """)  # noqa: W291
    assert output.within_frame.width is True
    assert output.within_frame.height is True
