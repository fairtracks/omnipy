import re
from typing import Annotated, Callable

import pytest
import pytest_cases as pc

from omnipy.data._display.config import (ConsoleColorSystem,
                                         OutputConfig,
                                         SpecialColorStyles,
                                         SyntaxLanguage)
from omnipy.data._display.constraints import Constraints
from omnipy.data._display.dimensions import Dimensions
from omnipy.data._display.draft import DraftMonospacedOutput
from omnipy.data._display.frame import Frame
from omnipy.data._display.styling import StylizedMonospacedOutput

from .cases.styling import OutputPropertyExpectations, OutputTestCase, OutputTestCaseSetup


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


@pc.parametrize_with_cases('case', cases='.cases.styling', has_tag='overflow_modes')
def test_stylized_output_overflow_modes(
    case: OutputTestCase,
    skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture],
) -> None:

    output = StylizedMonospacedOutput(case.content, frame=case.frame, config=case.config)
    processed_output = _prepare_output(output, case.get_output_property)

    assert processed_output == case.expected_output
    assert output.within_frame.width is case.expected_within_frame_width
    assert output.within_frame.height is case.expected_within_frame_height


@pc.parametrize_with_cases('output_test_case_setup', cases='.cases.styling', has_tag='setup')
@pc.parametrize_with_cases(
    'output_prop_expectations', cases='.cases.styling', has_tag='expectations')
def test_output_properties_of_stylized_output(
        output_test_case_setup: Annotated[OutputTestCaseSetup, pc.fixture],
        output_prop_expectations: Annotated[OutputPropertyExpectations, pc.fixture],
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:

    case_id, content, frame, config = output_test_case_setup
    get_output_property, expected_output_for_case_id = output_prop_expectations

    output = StylizedMonospacedOutput(content, frame=frame, config=config)
    for _ in range(2):
        assert get_output_property(output) == expected_output_for_case_id(case_id)


def test_stylized_output_json_syntax(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:
    json_content = '{"values": [1, 2, 3], "nested": {"key": true}}'

    output = StylizedMonospacedOutput(
        json_content,
        config=OutputConfig(
            language=SyntaxLanguage.JSON, console_color_system=ConsoleColorSystem.ANSI_RGB))

    assert output.content == json_content
    assert output.config.language == SyntaxLanguage.JSON

    # Checking that the plain output is unchanged (except for the trailing newline)
    assert output.plain.terminal == json_content + '\n'

    # Checking that 'true' is recognized as a keyword in the colorized terminal and HTML outputs
    assert '\x1b[94mtrue\x1b[0m' in output.colorized.terminal
    assert ('<span style="color: #0000ff; text-decoration-color: #0000ff">true</span>'
            in output.colorized.html_tag)


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
