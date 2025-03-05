import re
from textwrap import dedent
from typing import Annotated, Callable

import pytest
import pytest_cases as pc

from omnipy.data._display.config import (HorizontalOverflowMode,
                                         OutputConfig,
                                         SpecialColorStyles,
                                         SyntaxLanguage,
                                         VerticalOverflowMode)
from omnipy.data._display.constraints import Constraints
from omnipy.data._display.dimensions import Dimensions
from omnipy.data._display.draft import DraftMonospacedOutput
from omnipy.data._display.frame import Frame
from omnipy.data._display.styling import StylizedMonospacedOutput

from .cases.styling import OutputPropertyExpectations, OutputTestCaseSetup


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
            color_style=SpecialColorStyles.ANSI_LIGHT,
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


def _strip_html(html: str) -> str:
    matches = re.findall(r'<code[^>]*>([\S\s]*)</code>', html, re.MULTILINE)
    if not matches:
        return html

    code_no_tags = re.sub(r'<[^>]+>', '', matches[0])

    def _to_char(match: re.Match) -> str:
        import sys
        byte_as_str = match[1]
        return int(byte_as_str, 16).to_bytes(length=1, byteorder=sys.byteorder).decode()

    code_no_escapes = re.sub(r'&#x(\d+);', _to_char, code_no_tags)
    return code_no_escapes


def _strip_ansi(text: str) -> str:
    return re.sub(r'\x1b\[[^m]+m', '', text)


def _prepare_output(
    output: StylizedMonospacedOutput,
    get_output_property: Callable[[StylizedMonospacedOutput], str],
) -> str:
    return _strip_ansi(_strip_html(get_output_property(output)))


@pc.parametrize_with_cases(
    'output_prop_expectations', cases='.cases.styling', has_tag='expectations')
def test_stylized_output_overflow_modes(
        output_prop_expectations: Annotated[OutputPropertyExpectations, pc.fixture],
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:

    get_output_property, _ = output_prop_expectations

    content = ("[MyClass({'abc': [123, 234]}),\n"
               " MyClass({'def': [345, 456]})]")

    output = StylizedMonospacedOutput(
        content,
        frame=Frame(Dimensions(22, None)),
        config=OutputConfig(horizontal_overflow_mode=HorizontalOverflowMode.WORD_WRAP),
    )
    assert _prepare_output(output, get_output_property) == dedent("""\
        [MyClass({'abc': [123,
        234]}),
         MyClass({'def': [345,
        456]})]
        """)
    assert output.within_frame.width is True
    assert output.within_frame.height is None

    output = StylizedMonospacedOutput(
        content,
        frame=Frame(Dimensions(22, None)),
        config=OutputConfig(horizontal_overflow_mode=HorizontalOverflowMode.ELLIPSIS),
    )
    assert _prepare_output(output, get_output_property) == dedent("""\
        [MyClass({'abc': [123…
         MyClass({'def': [345…
        """)
    assert output.within_frame.width is True
    assert output.within_frame.height is None

    output = StylizedMonospacedOutput(
        content,
        frame=Frame(Dimensions(22, None)),
        config=OutputConfig(horizontal_overflow_mode=HorizontalOverflowMode.CROP),
    )
    assert _prepare_output(output, get_output_property) == dedent("""\
        [MyClass({'abc': [123,
         MyClass({'def': [345,
        """)
    assert output.within_frame.width is True
    assert output.within_frame.height is None

    output = StylizedMonospacedOutput(
        content,
        frame=Frame(Dimensions(10, 8)),
        config=OutputConfig(horizontal_overflow_mode=HorizontalOverflowMode.WORD_WRAP),
    )
    assert _prepare_output(output, get_output_property) == dedent("""\
        [MyClass({
        'abc': 
        [123, 
        234]}),
         MyClass({
        'def': 
        [345, 
        456]})]
        """)  # noqa: W291
    assert output.within_frame.width is True
    assert output.within_frame.height is True

    output = StylizedMonospacedOutput(
        content,
        frame=Frame(Dimensions(10, 4)),
        config=OutputConfig(
            horizontal_overflow_mode=HorizontalOverflowMode.WORD_WRAP,
            vertical_overflow_mode=VerticalOverflowMode.CROP_BOTTOM,
        ))
    assert _prepare_output(output, get_output_property) == dedent("""\
        [MyClass({
        'abc': 
        [123, 
        234]}),
        """)  # noqa: W291
    assert output.within_frame.width is True
    assert output.within_frame.height is True

    output = StylizedMonospacedOutput(
        content,
        frame=Frame(Dimensions(10, 1)),
        config=OutputConfig(
            horizontal_overflow_mode=HorizontalOverflowMode.WORD_WRAP,
            vertical_overflow_mode=VerticalOverflowMode.CROP_TOP,
        ))
    assert _prepare_output(output, get_output_property) == dedent("""\
        456]})]
        """)  # noqa: W291
    assert output.within_frame.width is True
    assert output.within_frame.height is True


@pc.parametrize_with_cases('output_test_case_setup', cases='.cases.styling', has_tag='setup')
@pc.parametrize_with_cases(
    'output_prop_expectations', cases='.cases.styling', has_tag='expectations')
def test_output_properties_of_stylized_output(
        output_test_case_setup: Annotated[OutputTestCaseSetup, pc.fixture],
        output_prop_expectations: Annotated[OutputPropertyExpectations, pc.fixture],
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:

    case_id, content, frame, config = output_test_case_setup
    get_output_property, expected_outputs = output_prop_expectations
    expected_output = expected_outputs[case_id]

    output = StylizedMonospacedOutput(content, frame=frame, config=config)
    for _ in range(2):
        assert get_output_property(output) == expected_output


def test_stylized_output_console_recording_not_deleted_by_filtering(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:

    content = 'Hello, World!'

    output = StylizedMonospacedOutput(content)
    assert output.plain.html_tag != ''
    assert output.bw_stylized.terminal != ''
    assert output.colorized.terminal != ''

    output = StylizedMonospacedOutput(content)
    assert output.bw_stylized.terminal != ''
    assert output.plain.terminal != ''
    assert output.colorized.terminal != ''
