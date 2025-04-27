from typing import Annotated

import pytest
import pytest_cases as pc

from omnipy.data._display.config import (ConsoleColorSystem,
                                         OutputConfig,
                                         RecommendedColorStyles,
                                         SyntaxLanguage)
from omnipy.data._display.constraints import Constraints
from omnipy.data._display.dimensions import Dimensions
from omnipy.data._display.frame import empty_frame, Frame
from omnipy.data._display.panel.draft.text import ReflowedTextDraftPanel
from omnipy.data._display.panel.styling.text import SyntaxStylizedTextPanel

from .helpers import (apply_frame_variant_to_test_case,
                      assert_dims_aware_panel,
                      OutputPropertyType,
                      PanelFrameVariantTestCase,
                      PanelOutputTestCase,
                      strip_all_styling_from_panel_output,
                      StylizedPanelOutputExpectations,
                      StylizedPanelTestCaseSetup)


def test_syntax_stylized_text_panel_init(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:

    stylized_text_panel = SyntaxStylizedTextPanel(ReflowedTextDraftPanel('[123, 234, 345]'),)

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


# noinspection PyDataclass
def test_syntax_stylized_text_panel_hashable(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:

    panel_1 = SyntaxStylizedTextPanel(ReflowedTextDraftPanel(''))
    panel_2 = SyntaxStylizedTextPanel(ReflowedTextDraftPanel(''))

    assert hash(panel_1) == hash(panel_2)

    panel_3 = SyntaxStylizedTextPanel(ReflowedTextDraftPanel('[123, 234, 345]'))
    panel_4 = SyntaxStylizedTextPanel(
        ReflowedTextDraftPanel('', frame=Frame(Dimensions(width=10, height=20))))
    panel_5 = SyntaxStylizedTextPanel(
        ReflowedTextDraftPanel('', constraints=Constraints(container_width_per_line_limit=9)))
    panel_6 = SyntaxStylizedTextPanel(
        ReflowedTextDraftPanel('', config=OutputConfig(indent_tab_size=4)))

    assert hash(panel_1) != hash(panel_3) != hash(panel_4) != hash(panel_5) != hash(panel_6)

    panel_7 = SyntaxStylizedTextPanel(ReflowedTextDraftPanel('[123, 234, 345]'))
    panel_8 = SyntaxStylizedTextPanel(
        ReflowedTextDraftPanel('', frame=Frame(Dimensions(width=10, height=20))))
    panel_9 = SyntaxStylizedTextPanel(
        ReflowedTextDraftPanel('', constraints=Constraints(container_width_per_line_limit=9)))
    panel_10 = SyntaxStylizedTextPanel(
        ReflowedTextDraftPanel('', config=OutputConfig(indent_tab_size=4)))

    assert hash(panel_3) == hash(panel_7)
    assert hash(panel_4) == hash(panel_8)
    assert hash(panel_5) == hash(panel_9)
    assert hash(panel_6) == hash(panel_10)


def test_fail_syntax_stylized_text_panel_if_extra_params(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:

    with pytest.raises(TypeError):
        SyntaxStylizedTextPanel(
            ReflowedTextDraftPanel('[123, 234, 345]'), extra=123)  # type: ignore[call-arg]


# noinspection PyDataclass
def test_syntax_stylized_text_panel_no_assignments(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:

    text_panel = SyntaxStylizedTextPanel(ReflowedTextDraftPanel('[123, 234, 345]',))

    with pytest.raises(AttributeError):
        text_panel.content = '[234, 345, 456]'  # type: ignore[misc]

    with pytest.raises(AttributeError):
        text_panel.frame = Frame(Dimensions(10, 20))  # type: ignore[misc]

    with pytest.raises(AttributeError):
        text_panel.constraints = Constraints(  # type: ignore[misc]
            container_width_per_line_limit=10)

    with pytest.raises(AttributeError):
        text_panel.config = OutputConfig()  # type: ignore[misc]


@pc.parametrize_with_cases(
    'case',
    cases='.cases.text_basics',
    has_tag=('dims_and_edge_cases', 'syntax_text'),
)
def test_syntax_stylized_text_panel_basic_dims_and_edge_cases(
    case: PanelFrameVariantTestCase[str],
    output_format_accessor: Annotated[OutputPropertyType, pc.fixture],
    skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture],
) -> None:
    frame_case = apply_frame_variant_to_test_case(case, stylized_stage=True)

    text_panel = SyntaxStylizedTextPanel(
        ReflowedTextDraftPanel(case.content, frame=frame_case.frame, config=case.config))
    assert_dims_aware_panel(
        text_panel,
        exp_dims=frame_case.exp_dims,
        exp_frame=frame_case.frame,
        exp_within_frame=frame_case.exp_within_frame,
    )

    if frame_case.exp_plain_output is not None:
        processed_text_panel = strip_all_styling_from_panel_output(
            text_panel,
            output_format_accessor,
        )
        assert processed_text_panel == frame_case.exp_plain_output


def test_syntax_stylized_text_panel_variable_width_chars(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:
    def _get_plain_terminal_output_from_contents(
            contents: str,
            config: OutputConfig = OutputConfig(),
    ) -> str:
        return SyntaxStylizedTextPanel(ReflowedTextDraftPanel(
            contents,
            config=config,
        )).plain.terminal

    # Mandarin Chinese characters are double-width
    assert _get_plain_terminal_output_from_contents('北京') == '北京\n'

    # Null character is zero-width
    assert _get_plain_terminal_output_from_contents('\0北京\n北京') == '\x00北京\n北京\n'

    # Soft hyphen character is zero-width
    assert _get_plain_terminal_output_from_contents('hyphe\xad\nnate') == 'hyphe\xad\nnate\n'

    # Tab character width depends on context
    assert _get_plain_terminal_output_from_contents('\ta') == '    a\n'
    assert _get_plain_terminal_output_from_contents(' a\tb') == ' a  b\n'
    assert _get_plain_terminal_output_from_contents('abcd  \te') == 'abcd    e\n'

    # Tab character width also depends on config
    config = OutputConfig(tab_size=6)
    assert _get_plain_terminal_output_from_contents('\ta', config) == '      a\n'
    assert _get_plain_terminal_output_from_contents(' a\tb', config) == ' a    b\n'
    assert _get_plain_terminal_output_from_contents('abcd  \te', config) == 'abcd        e\n'


@pc.parametrize_with_cases(
    'case',
    cases='.cases.text_styling',
    has_tag=('overflow_modes', 'syntax_text'),
)
def test_syntax_stylized_text_panel_overflow_modes(
    case: PanelOutputTestCase,
    output_format_accessor: Annotated[OutputPropertyType, pc.fixture],
    skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture],
) -> None:

    text_panel = SyntaxStylizedTextPanel(
        ReflowedTextDraftPanel(case.content, frame=case.frame, config=case.config))
    processed_text_panel = strip_all_styling_from_panel_output(text_panel, output_format_accessor)

    assert processed_text_panel == case.exp_plain_output
    assert text_panel.dims.width == case.exp_dims.width
    assert text_panel.dims.height == case.exp_dims.height
    assert text_panel.within_frame.width is case.exp_within_frame.width
    assert text_panel.within_frame.height is case.exp_within_frame.height


@pc.parametrize_with_cases(
    'output_test_case_setup',
    cases='.cases.text_styling',
    has_tag=('setup', 'syntax_text'),
)
@pc.parametrize_with_cases(
    'output_prop_expectations',
    cases='.cases.text_styling',
    has_tag=('expectations', 'syntax_text'),
)
def test_output_properties_of_syntax_stylized_text_panel(
        output_test_case_setup: Annotated[StylizedPanelTestCaseSetup, pc.fixture],
        output_prop_expectations: Annotated[StylizedPanelOutputExpectations, pc.fixture],
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:

    case_id, content, frame, config = output_test_case_setup
    get_output_property, exp_plain_output_for_case_id = output_prop_expectations

    text_panel = SyntaxStylizedTextPanel(
        ReflowedTextDraftPanel(content, frame=frame, config=config))
    for _ in range(2):
        assert get_output_property(text_panel) == exp_plain_output_for_case_id(case_id)


def test_syntax_stylized_text_panel_json(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:
    json_content = '{"values": [1, 2, 3], "nested": {"key": true}}'

    text_panel = SyntaxStylizedTextPanel(
        ReflowedTextDraftPanel(
            json_content,
            config=OutputConfig(
                language=SyntaxLanguage.JSON, console_color_system=ConsoleColorSystem.ANSI_RGB)))

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

    text_panel = SyntaxStylizedTextPanel(ReflowedTextDraftPanel(content))
    assert text_panel.plain.html_tag != ''
    assert text_panel.bw_stylized.terminal != ''
    assert text_panel.colorized.terminal != ''

    text_panel = SyntaxStylizedTextPanel(ReflowedTextDraftPanel(content))
    assert text_panel.bw_stylized.terminal != ''
    assert text_panel.plain.terminal != ''
    assert text_panel.colorized.terminal != ''


def test_fail_stylized_layout_panel_render_next_stage(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:
    layout_panel = SyntaxStylizedTextPanel(ReflowedTextDraftPanel('Some content'))
    with pytest.raises(NotImplementedError):
        layout_panel.render_next_stage()
