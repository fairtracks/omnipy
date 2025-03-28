from typing import Annotated

import pytest
import pytest_cases as pc

from omnipy.data._display.config import LayoutStyle, OutputConfig
from omnipy.data._display.constraints import Constraints
from omnipy.data._display.dimensions import Dimensions
from omnipy.data._display.frame import empty_frame, Frame
from omnipy.data._display.layout import Layout
from omnipy.data._display.panel.styling.layout import StylizedLayoutPanel

from ..helpers.classes import MockPanel
from .helpers import (PanelOutputPropertyExpectations,
                      PanelOutputTestCase,
                      PanelOutputTestCaseSetup,
                      prepare_panel)


def test_stylized_layout_panel_init(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:

    layout = Layout()
    layout['panel'] = MockPanel(content='Some Content')
    layout_panel = StylizedLayoutPanel(layout)

    assert layout_panel.content is not layout
    assert layout_panel.content == layout
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

    assert configured_layout_panel.content == layout
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


# noinspection PyDataclass
def test_stylized_layout_panel_immutable_properties(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:

    layout_panel = StylizedLayoutPanel(Layout())

    with pytest.raises(AttributeError):
        layout_panel.content = Layout()  # type: ignore[misc]

    with pytest.raises(AttributeError):
        layout_panel.frame = empty_frame()  # type: ignore[misc]

    with pytest.raises(AttributeError):
        layout_panel.constraints = Constraints()  # type: ignore[misc]

    with pytest.raises(AttributeError):
        layout_panel.config = OutputConfig()  # type: ignore[misc]


@pc.parametrize_with_cases(
    'case',
    cases='.cases.layout_styling',
    has_tag=('grids_and_frames', 'layout_styling'),
)
def test_syntax_layout_panel_grids_and_frames(
    case: PanelOutputTestCase[Layout],
    skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture],
) -> None:

    layout_panel = StylizedLayoutPanel(case.content, frame=case.frame, config=case.config)
    processed_text_panel = prepare_panel(layout_panel, case.get_output_property)

    assert processed_text_panel == case.expected_output
    assert layout_panel.dims.width == case.expected_dims_width
    assert layout_panel.dims.height == case.expected_dims_height
    assert layout_panel.within_frame.width is case.expected_within_frame_width
    assert layout_panel.within_frame.height is case.expected_within_frame_height


@pc.parametrize_with_cases(
    'output_test_case_setup',
    cases='.cases.layout_styling',
    has_tag=('setup', 'layout_styling'),
)
@pc.parametrize_with_cases(
    'output_prop_expectations',
    cases='.cases.layout_styling',
    has_tag=('expectations', 'layout_styling'),
)
def test_output_properties_of_stylized_layout_panel(
        output_test_case_setup: Annotated[PanelOutputTestCaseSetup, pc.fixture],
        output_prop_expectations: Annotated[PanelOutputPropertyExpectations, pc.fixture],
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:

    case_id, content, frame, config = output_test_case_setup
    get_output_property, expected_output_for_case_id = output_prop_expectations

    layout_panel = StylizedLayoutPanel(content, frame=frame, config=config)
    for _ in range(2):
        assert get_output_property(layout_panel) == expected_output_for_case_id(case_id)


def test_stylized_layout_panel_empty_layout(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:

    # Create an empty layout
    layout = Layout()

    # Create stylized output
    layout_panel = StylizedLayoutPanel(layout)

    # Verify the output is empty or as expected
    terminal_output = layout_panel.plain.terminal
    assert terminal_output == ''  # Adjust this based on expected behavior for empty layout
