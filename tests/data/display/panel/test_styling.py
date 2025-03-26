import re
from textwrap import dedent
from typing import Annotated

import pytest
import pytest_cases as pc

from omnipy.data._display.config import (ConsoleColorSystem,
                                         LayoutStyle,
                                         OutputConfig,
                                         RecommendedColorStyles,
                                         SyntaxLanguage)
from omnipy.data._display.constraints import Constraints
from omnipy.data._display.dimensions import Dimensions
from omnipy.data._display.frame import empty_frame, Frame
from omnipy.data._display.layout import Layout
from omnipy.data._display.panel.draft import ReflowedTextDraftPanel
from omnipy.data._display.panel.styling import StylizedLayoutPanel, SyntaxStylizedTextPanel

from .cases.styling import (OutputPropertyType,
                            PanelOutputPropertyExpectations,
                            PanelOutputTestCase,
                            PanelOutputTestCaseSetup)
from .helpers.classes import MockPanel


def test_syntax_stylized_text_panel_init(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:

    stylized_text_panel = SyntaxStylizedTextPanel('[123, 234, 345]',)

    assert stylized_text_panel.content == '[123, 234, 345]'
    assert stylized_text_panel.frame == empty_frame()
    assert stylized_text_panel.constraints == Constraints()
    assert stylized_text_panel.config == OutputConfig()

    reflowed_text_panel = ReflowedTextDraftPanel(
        '[123, 234, 345]',
        frame=Frame(Dimensions(10, 10)),
        constraints=Constraints(),
        config=OutputConfig(
            language=SyntaxLanguage.PYTHON,
            color_style=RecommendedColorStyles.ANSI_LIGHT,
        ),
    )

    stylized_reflowed_text_panel = SyntaxStylizedTextPanel(reflowed_text_panel)

    assert stylized_reflowed_text_panel.content == '[123, 234, 345]'
    assert stylized_reflowed_text_panel.frame is not reflowed_text_panel.frame
    assert stylized_reflowed_text_panel.frame == reflowed_text_panel.frame
    assert stylized_reflowed_text_panel.constraints is not reflowed_text_panel.constraints
    assert stylized_reflowed_text_panel.constraints == reflowed_text_panel.constraints
    assert stylized_reflowed_text_panel.config is not reflowed_text_panel.config
    assert stylized_reflowed_text_panel.config == reflowed_text_panel.config


def test_fail_syntax_stylized_text_panel_if_extra_params(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:

    with pytest.raises(TypeError):
        SyntaxStylizedTextPanel('[123, 234, 345]', extra=123)  # type: ignore[call-overload]

    text_panel = SyntaxStylizedTextPanel('[123, 234, 345]')
    text_panel.extra = 123


def test_syntax_stylized_text_panel_immutable_properties(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:

    text_panel = SyntaxStylizedTextPanel('[123, 234, 345]',)

    with pytest.raises(AttributeError):
        text_panel.content = '[234, 345, 456]'

    with pytest.raises(AttributeError):
        text_panel.frame = empty_frame()

    with pytest.raises(AttributeError):
        text_panel.constraints = Constraints()

    with pytest.raises(AttributeError):
        text_panel.config = OutputConfig()


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


def _prepare_panel(
    text_panel: SyntaxStylizedTextPanel,
    get_output_property: OutputPropertyType,
) -> str:
    return _strip_ansi(_strip_html(get_output_property(text_panel)))


def test_stylized_monospaced_panel_with_empty_input(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:
    stylized_empty_text_panel = SyntaxStylizedTextPanel('')

    assert stylized_empty_text_panel.content == ''
    assert stylized_empty_text_panel.plain.terminal == ''  # Just a newline
    assert stylized_empty_text_panel.plain.html_tag.strip().endswith(
        '></code></pre>')  # Empty but valid HTML

    # Test with whitespace only
    stylized_whitespace_panel = SyntaxStylizedTextPanel('  \n  ')

    assert stylized_whitespace_panel.content == '  \n  '
    assert stylized_whitespace_panel.plain.terminal == '  \n  \n'

    # Verify dimensions
    assert stylized_empty_text_panel.dims.width == 0
    assert stylized_empty_text_panel.dims.height == 0

    assert stylized_whitespace_panel.dims.width == 2
    assert stylized_whitespace_panel.dims.height == 2  # Two lines

    # Test with frame to ensure no errors
    framed_stylized_empty_text_panel = SyntaxStylizedTextPanel('', frame=Frame(Dimensions(10, 5)))

    assert framed_stylized_empty_text_panel.within_frame.width is True


@pc.parametrize_with_cases('case', cases='.cases.styling', has_tag='overflow_modes')
def test_syntax_stylized_text_panel_overflow_modes(
    case: PanelOutputTestCase,
    skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture],
) -> None:

    text_panel = SyntaxStylizedTextPanel(case.content, frame=case.frame, config=case.config)
    processed_text_panel = _prepare_panel(text_panel, case.get_output_property)

    assert processed_text_panel == case.expected_output
    assert text_panel.within_frame.width is case.expected_within_frame_width
    assert text_panel.within_frame.height is case.expected_within_frame_height


@pc.parametrize_with_cases('output_test_case_setup', cases='.cases.styling', has_tag='setup')
@pc.parametrize_with_cases(
    'output_prop_expectations', cases='.cases.styling', has_tag='expectations')
def test_output_properties_of_syntax_stylized_text_panel(
        output_test_case_setup: Annotated[PanelOutputTestCaseSetup, pc.fixture],
        output_prop_expectations: Annotated[PanelOutputPropertyExpectations, pc.fixture],
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:

    case_id, content, frame, config = output_test_case_setup
    get_output_property, expected_output_for_case_id = output_prop_expectations

    text_panel = SyntaxStylizedTextPanel(content, frame=frame, config=config)
    for _ in range(2):
        assert get_output_property(text_panel) == expected_output_for_case_id(case_id)


def test_syntax_stylized_text_panel_json(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:
    json_content = '{"values": [1, 2, 3], "nested": {"key": true}}'

    text_panel = SyntaxStylizedTextPanel(
        json_content,
        config=OutputConfig(
            language=SyntaxLanguage.JSON, console_color_system=ConsoleColorSystem.ANSI_RGB))

    assert text_panel.content == json_content
    assert text_panel.config.language == SyntaxLanguage.JSON

    # Checking that the plain output is unchanged (except for the trailing newline)
    assert text_panel.plain.terminal == json_content + '\n'

    # Checking that 'true' is recognized as a keyword in the colorized terminal and HTML outputs
    assert '\x1b[94mtrue\x1b[0m' in text_panel.colorized.terminal
    assert ('<span style="color: #0000ff; text-decoration-color: #0000ff">true</span>'
            in text_panel.colorized.html_tag)


def test_syntax_stylized_text_panel_console_recording_not_deleted_by_filtering(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:

    content = 'Hello, World!'

    text_panel = SyntaxStylizedTextPanel(content)
    assert text_panel.plain.html_tag != ''
    assert text_panel.bw_stylized.terminal != ''
    assert text_panel.colorized.terminal != ''

    text_panel = SyntaxStylizedTextPanel(content)
    assert text_panel.bw_stylized.terminal != ''
    assert text_panel.plain.terminal != ''
    assert text_panel.colorized.terminal != ''


def test_stylized_layout_panel_init(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:

    layout = Layout()
    layout['panel'] = MockPanel(contents='Some Content')
    layout_panel = StylizedLayoutPanel(layout)

    assert layout_panel.content == ''
    assert layout_panel.layout is not layout
    assert layout_panel.layout == layout
    assert layout_panel.frame == empty_frame()
    assert layout_panel.constraints == Constraints()
    assert layout_panel.config == OutputConfig()

    frame = Frame(Dimensions(10, 10))
    config = OutputConfig(layout_style=LayoutStyle.PANELS)
    constraints = Constraints()
    configured_layout_panel = StylizedLayoutPanel(
        layout,
        frame=frame,
        config=config,
        constraints=constraints,
    )

    assert configured_layout_panel.content == ''
    assert configured_layout_panel.layout == layout
    assert configured_layout_panel.frame is not frame
    assert configured_layout_panel.frame == frame
    assert configured_layout_panel.constraints is not constraints
    assert configured_layout_panel.constraints == constraints
    assert configured_layout_panel.config is not config
    assert configured_layout_panel.config == config


def test_fail_stylized_layout_panel_if_extra_params(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:

    with pytest.raises(TypeError):
        StylizedLayoutPanel(Layout(), extra=123)  # type: ignore[call-arg]

    layout_panel = StylizedLayoutPanel(Layout())
    layout_panel.extra = 123


def test_stylized_layout_panel_immutable_properties(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:

    layout_panel = StylizedLayoutPanel(Layout())

    with pytest.raises(AttributeError):
        layout_panel.content = '[234, 345, 456]'

    with pytest.raises(AttributeError):
        layout_panel.layout = Layout()

    with pytest.raises(AttributeError):
        layout_panel.frame = empty_frame()

    with pytest.raises(AttributeError):
        layout_panel.constraints = Constraints()

    with pytest.raises(AttributeError):
        layout_panel.config = OutputConfig()


def test_stylized_layout_panel_basic_grid(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:

    from omnipy.data._display.layout import Layout
    from omnipy.data._display.panel.styling import StylizedLayoutPanel

    # Create a simple layout with mock panels
    layout = Layout()
    layout['first'] = MockPanel(contents='Panel_1 Content')
    layout['second'] = MockPanel(contents='Panel_2 Content')

    # Create stylized output with default config (should use Table grid)
    layout_panel = StylizedLayoutPanel(
        layout, config=OutputConfig(console_color_system=ConsoleColorSystem.ANSI_RGB))

    # Check terminal output
    assert layout_panel.plain.terminal == dedent("""\
        ╭─────────┬─────────╮
        │ Panel_1 │ Panel_2 │
        │ Content │ Content │
        ╰─────────┴─────────╯
        """)

    assert layout_panel.bw_stylized.terminal == dedent("""\
        ╭─────────┬─────────╮
        │ \x1b[1mPanel_1\x1b[0m │ \x1b[1mPanel_2\x1b[0m │
        │ \x1b[1mContent\x1b[0m │ \x1b[1mContent\x1b[0m │
        ╰─────────┴─────────╯
        """)

    assert layout_panel.colorized.terminal == dedent("""\
        ╭─────────┬─────────╮
        │ \x1b[1;34mPanel_1\x1b[0m │ \x1b[1;34mPanel_2\x1b[0m │
        │ \x1b[1;34mContent\x1b[0m │ \x1b[1;34mContent\x1b[0m │
        ╰─────────┴─────────╯
        """)


def test_stylized_layout_panel_empty_layout(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:
    from omnipy.data._display.layout import Layout
    from omnipy.data._display.panel.styling import StylizedLayoutPanel

    # Create an empty layout
    layout = Layout()

    # Create stylized output
    layout_panel = StylizedLayoutPanel(layout)

    # Verify the output is empty or as expected
    terminal_output = layout_panel.plain.terminal
    assert terminal_output == ''  # Adjust this based on expected behavior for empty layout
