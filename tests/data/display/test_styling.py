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
    for _ in range(2):
        assert output.plain.terminal == "MyClass({'abc': [123, 234]})\n"
    assert output.within_frame.width is None
    assert output.within_frame.height is None

    output = StylizedMonospacedOutput(
        content,
        frame=Frame(Dimensions(21, None)),
        config=OutputConfig(
            color_style=LowerContrastLightColorStyles.MURPHY,
            horizontal_overflow_mode=HorizontalOverflowMode.WORD_WRAP),
    )
    assert output.plain.terminal == dedent("""\
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
    assert output.plain.terminal == "MyClass({'abc': [123…\n"
    assert output.within_frame.width is True
    assert output.within_frame.height is None

    output = StylizedMonospacedOutput(
        content,
        frame=Frame(Dimensions(21, None)),
        config=OutputConfig(
            color_style=LowerContrastLightColorStyles.MURPHY,
            horizontal_overflow_mode=HorizontalOverflowMode.CROP),
    )
    assert output.plain.terminal == "MyClass({'abc': [123,\n"
    assert output.within_frame.width is True
    assert output.within_frame.height is None

    output = StylizedMonospacedOutput(
        content,
        frame=Frame(Dimensions(9, 20)),
        config=OutputConfig(
            color_style=LowerContrastLightColorStyles.MURPHY,
            horizontal_overflow_mode=HorizontalOverflowMode.WORD_WRAP),
    )
    assert output.plain.terminal == dedent("""\
        MyClass({
        'abc': 
        [123, 
        234]})
        """)  # noqa: W291
    assert output.within_frame.width is True
    assert output.within_frame.height is True

    output = StylizedMonospacedOutput(
        content,
        frame=Frame(Dimensions(9, 2)),
        config=OutputConfig(
            color_style=LowerContrastLightColorStyles.MURPHY,
            horizontal_overflow_mode=HorizontalOverflowMode.WORD_WRAP,
            vertical_overflow_mode=VerticalOverflowMode.CROP_BOTTOM,
        ))
    assert output.plain.terminal == dedent("""\
        MyClass({
        'abc': 
        """)  # noqa: W291
    assert output.within_frame.width is True
    assert output.within_frame.height is True

    output = StylizedMonospacedOutput(
        content,
        frame=Frame(Dimensions(9, 2)),
        config=OutputConfig(
            color_style=LowerContrastLightColorStyles.MURPHY,
            horizontal_overflow_mode=HorizontalOverflowMode.WORD_WRAP,
            vertical_overflow_mode=VerticalOverflowMode.CROP_TOP,
        ))
    assert output.plain.terminal == dedent("""\
        [123, 
        234]})
        """)  # noqa: W291
    assert output.within_frame.width is True
    assert output.within_frame.height is True


def test_bw_stylized_output_to_terminal(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:

    content = "MyClass({'abc': [123, 234]})"

    output = StylizedMonospacedOutput(content)
    for _ in range(2):
        assert output.bw_stylized.terminal == "MyClass({'abc': [123, 234]})\n"

    output = StylizedMonospacedOutput(
        content,
        config=OutputConfig(color_style=LowerContrastLightColorStyles.MURPHY,),
    )
    for _ in range(2):
        assert output.bw_stylized.terminal \
               == "MyClass({'abc': [\x1b[1m123\x1b[0m, \x1b[1m234\x1b[0m]})\n"

    output = StylizedMonospacedOutput(
        content,
        frame=Frame(Dimensions(9, 3)),
        config=OutputConfig(
            color_style=LowerContrastLightColorStyles.MURPHY,
            horizontal_overflow_mode=HorizontalOverflowMode.WORD_WRAP,
            vertical_overflow_mode=VerticalOverflowMode.CROP_TOP,
        ))
    assert output.bw_stylized.terminal == dedent("""\
        'abc': 
        [\x1b[1m123\x1b[0m, 
        \x1b[1m234\x1b[0m]})
        """)  # noqa: W291


def test_colorized_output_to_terminal(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:

    content = "MyClass({'abc': [123, 234]})"

    output = StylizedMonospacedOutput(content)
    for _ in range(2):
        assert output.colorized.terminal == (
            "\x1b[49mMyClass({\x1b[0m\x1b[33;49m'\x1b[0m\x1b[33;49mabc\x1b[0m\x1b[33;49m'"
            '\x1b[0m\x1b[49m: [\x1b[0m\x1b[34;49m123\x1b[0m\x1b[49m, \x1b[0m\x1b[34;49m234'
            '\x1b[0m\x1b[49m]})\x1b[0m\n')

    output = StylizedMonospacedOutput(
        content,
        config=OutputConfig(color_style=LowerContrastLightColorStyles.MURPHY,),
    )
    for _ in range(2):
        assert output.colorized.terminal == (
            '\x1b[38;2;0;0;0;49mMyClass\x1b[0m\x1b[38;2;0;0;0;49m(\x1b[0m\x1b[38;2;0;0;0;49m{'
            "\x1b[0m\x1b[38;2;0;0;0;49m'\x1b[0m\x1b[38;2;0;0;0;49mabc\x1b[0m\x1b[38;2;0;0;0;49m'"
            '\x1b[0m\x1b[38;2;0;0;0;49m:\x1b[0m\x1b[38;2;0;0;0;49m \x1b[0m\x1b[38;2;0;0;0;49m['
            '\x1b[0m\x1b[1;38;2;102;102;255;49m123\x1b[0m\x1b[38;2;0;0;0;49m,'
            '\x1b[0m\x1b[38;2;0;0;0;49m \x1b[0m\x1b[1;38;2;102;102;255;49m234'
            '\x1b[0m\x1b[38;2;0;0;0;49m]\x1b[0m\x1b[38;2;0;0;0;49m}\x1b[0m\x1b[38;2;0;0;0;49m)'
            '\x1b[0m\n')

    output = StylizedMonospacedOutput(
        content,
        frame=Frame(Dimensions(9, 3)),
        config=OutputConfig(
            color_style=LowerContrastLightColorStyles.MURPHY,
            horizontal_overflow_mode=HorizontalOverflowMode.WORD_WRAP,
            vertical_overflow_mode=VerticalOverflowMode.CROP_TOP,
        ))
    assert output.colorized.terminal == (
        "\x1b[38;2;0;0;0;49m'\x1b[0m\x1b[38;2;0;0;0;49mabc\x1b[0m\x1b[38;2;0;0;0;49m'"
        '\x1b[0m\x1b[38;2;0;0;0;49m:\x1b[0m\x1b[38;2;0;0;0;49m \x1b[0m\n'
        '\x1b[38;2;0;0;0;49m[\x1b[0m\x1b[1;38;2;102;102;255;49m123'
        '\x1b[0m\x1b[38;2;0;0;0;49m,\x1b[0m\x1b[38;2;0;0;0;49m \x1b[0m\n'
        '\x1b[1;38;2;102;102;255;49m234\x1b[0m\x1b[38;2;0;0;0;49m]'
        '\x1b[0m\x1b[38;2;0;0;0;49m}\x1b[0m\x1b[38;2;0;0;0;49m)\x1b[0m\n')
