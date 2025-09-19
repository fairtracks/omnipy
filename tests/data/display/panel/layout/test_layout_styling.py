from typing import Annotated

import pytest
import pytest_cases as pc

from omnipy.data._display.config import OutputConfig
from omnipy.data._display.constraints import Constraints
from omnipy.data._display.dimensions import Dimensions
from omnipy.data._display.frame import empty_frame, Frame
from omnipy.data._display.layout.base import Layout
from omnipy.data._display.panel.draft.layout import ResizedLayoutDraftPanel
from omnipy.data._display.panel.styling.layout import StylizedLayoutPanel
from omnipy.shared.enums.display import PanelDesign

from ..helpers.case_setup import (OutputPropertyType,
                                  PanelFrameVariantTestCase,
                                  PanelOutputTestCase,
                                  prepare_test_case_for_stylized_layout,
                                  StylizedPanelOutputExpectations,
                                  StylizedPanelTestCaseSetup)
from ..helpers.mocks import MockStylablePlainCropPanel, MockStylizedPlainCropPanel
from ..helpers.panel_assert import assert_dims_aware_panel, strip_all_styling_from_panel_output


def test_stylized_layout_panel_init() -> None:

    layout: Layout = Layout()
    layout['panel'] = MockStylablePlainCropPanel(content='Some Content')
    layout_panel = StylizedLayoutPanel(ResizedLayoutDraftPanel(layout))

    assert layout_panel.content is not layout
    assert layout_panel.frame == empty_frame()
    assert layout_panel.constraints == Constraints()
    assert layout_panel.config == OutputConfig()

    frame = Frame(Dimensions(10, 10))
    config = OutputConfig(panel=PanelDesign.TABLE_GRID)
    constraints = Constraints()
    configured_layout_panel = StylizedLayoutPanel(
        ResizedLayoutDraftPanel(
            layout,
            frame=frame,
            config=config,
            constraints=constraints,
        ))

    assert configured_layout_panel.content is not layout
    assert isinstance(configured_layout_panel.content['panel'], MockStylizedPlainCropPanel)
    assert configured_layout_panel.frame is not frame
    assert configured_layout_panel.frame == frame
    assert configured_layout_panel.constraints is not constraints
    assert configured_layout_panel.constraints == constraints
    assert configured_layout_panel.config is not config
    assert configured_layout_panel.config == config


def test_fail_stylized_layout_panel_if_extra_params() -> None:

    with pytest.raises(TypeError):
        StylizedLayoutPanel(ResizedLayoutDraftPanel(Layout()), extra=123)  # type: ignore[call-arg]


# noinspection PyDataclass
def test_stylized_layout_panel_immutable_properties() -> None:

    layout_panel = StylizedLayoutPanel(ResizedLayoutDraftPanel(Layout()))

    with pytest.raises(AttributeError):
        layout_panel.content = Layout()  # type: ignore[misc, assignment]

    with pytest.raises(AttributeError):
        layout_panel.frame = empty_frame()  # type: ignore[misc]

    with pytest.raises(AttributeError):
        layout_panel.constraints = Constraints()  # type: ignore[misc]

    with pytest.raises(AttributeError):
        layout_panel.config = OutputConfig()  # type: ignore[misc]


@pc.parametrize_with_cases(
    'case',
    cases='.cases.layout_basics',
    has_tag=('dims_and_edge_cases', 'layout'),
)
def test_stylized_layout_panel_basic_dims_and_edge_cases(
    case: PanelOutputTestCase[Layout] | PanelFrameVariantTestCase[Layout],
    plain_terminal: Annotated[OutputPropertyType, pc.fixture],
    output_format_accessor: Annotated[OutputPropertyType, pc.fixture],
) -> None:
    case = prepare_test_case_for_stylized_layout(case, plain_terminal, output_format_accessor)

    layout_panel = StylizedLayoutPanel(
        ResizedLayoutDraftPanel(
            case.content,
            title=case.title,
            frame=case.frame,
            config=case.config,
        ))
    assert_dims_aware_panel(
        layout_panel,
        exp_dims=case.exp_dims,
        exp_frame=case.frame,
        exp_within_frame=case.exp_within_frame,
    )

    if case.exp_plain_output is not None:
        processed_text_panel = strip_all_styling_from_panel_output(
            layout_panel,
            output_format_accessor,
        )
        assert processed_text_panel == case.exp_plain_output


@pc.parametrize_with_cases(
    'output_test_case_setup',
    cases='.cases.layout_styling',
    has_tag=('setup', 'layout'),
)
@pc.parametrize_with_cases(
    'output_prop_expectations',
    cases='.cases.layout_styling',
    has_tag=('expectations', 'layout'),
)
def test_output_properties_of_stylized_layout_panel(
    output_test_case_setup: Annotated[StylizedPanelTestCaseSetup, pc.fixture],
    output_prop_expectations: Annotated[StylizedPanelOutputExpectations, pc.fixture],
) -> None:

    case_id, content, title, frame, config = output_test_case_setup
    get_output_property, exp_plain_output_for_case_id = output_prop_expectations

    layout_panel = StylizedLayoutPanel(
        ResizedLayoutDraftPanel(
            content,
            title=title,
            frame=frame,
            config=config,
        ))
    for _ in range(2):
        assert get_output_property(layout_panel) == exp_plain_output_for_case_id(case_id)


def test_fail_stylized_layout_panel_render_next_stage() -> None:
    layout_panel = StylizedLayoutPanel(ResizedLayoutDraftPanel(Layout()))
    with pytest.raises(NotImplementedError):
        layout_panel.render_next_stage()
