from typing import Annotated

import pytest
import pytest_cases as pc

from omnipy.data._display.config import OutputConfig
from omnipy.data._display.constraints import Constraints
from omnipy.data._display.dimensions import Dimensions
from omnipy.data._display.frame import empty_frame, Frame
from omnipy.data._display.layout import Layout
from omnipy.data._display.panel.draft.layout import ResizedLayoutDraftPanel
from omnipy.data._display.panel.styling.layout import StylizedLayoutPanel

from ..helpers.classes import MockPanel, MockPanelStage2, MockPanelStage3
from .helpers import (apply_frame_variant_to_test_case,
                      assert_dims_aware_panel,
                      assert_draft_panel_subcls,
                      assert_next_stage_panel,
                      OutputPropertyType,
                      PanelFrameVariantTestCase)


def test_resized_layout_draft_panel_init(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:
    panel_cls = ResizedLayoutDraftPanel
    assert_draft_panel_subcls(panel_cls, Layout(), None, None, None, content_is_identical=False)

    layout: Layout = Layout(abc=MockPanel('Some text'))
    assert_draft_panel_subcls(
        panel_cls, layout, Frame(Dimensions(None, None)), None, None, content_is_identical=False)
    assert_draft_panel_subcls(
        panel_cls, layout, Frame(Dimensions(10, None)), None, None, content_is_identical=False)
    assert_draft_panel_subcls(
        panel_cls, layout, Frame(Dimensions(None, 20)), None, None, content_is_identical=False)
    assert_draft_panel_subcls(
        panel_cls, layout, Frame(Dimensions(10, 20)), None, None, content_is_identical=False)
    assert_draft_panel_subcls(
        panel_cls, layout, None, None, OutputConfig(indent_tab_size=4), content_is_identical=False)
    assert_draft_panel_subcls(
        panel_cls,
        layout,
        None,
        Constraints(container_width_per_line_limit=10),
        None,
        content_is_identical=False,
    )
    assert_draft_panel_subcls(
        panel_cls,
        layout,
        Frame(Dimensions(20, 10)),
        Constraints(container_width_per_line_limit=10),
        OutputConfig(indent_tab_size=4),
        content_is_identical=False,
    )


def test_resized_layout_draft_panel_hashable(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:
    draft_panel_1 = ResizedLayoutDraftPanel(Layout())
    draft_panel_2 = ResizedLayoutDraftPanel(Layout())

    assert hash(draft_panel_1) == hash(draft_panel_2)

    draft_panel_3 = ResizedLayoutDraftPanel(Layout(a=MockPanel('Some text')))
    draft_panel_4 = ResizedLayoutDraftPanel(Layout(), frame=Frame(Dimensions(10, 20)))
    draft_panel_5 = ResizedLayoutDraftPanel(
        Layout(), constraints=Constraints(container_width_per_line_limit=10))
    draft_panel_6 = ResizedLayoutDraftPanel(Layout(), config=OutputConfig(indent_tab_size=4))

    assert hash(draft_panel_1) != hash(draft_panel_3) != hash(draft_panel_4) != hash(
        draft_panel_5) != hash(draft_panel_6)

    draft_panel_7 = ResizedLayoutDraftPanel(Layout(a=MockPanel('Some text')))
    draft_panel_8 = ResizedLayoutDraftPanel(Layout(), frame=Frame(Dimensions(10, 20)))
    draft_panel_9 = ResizedLayoutDraftPanel(
        Layout(), constraints=Constraints(container_width_per_line_limit=10))
    draft_panel_10 = ResizedLayoutDraftPanel(Layout(), config=OutputConfig(indent_tab_size=4))

    assert hash(draft_panel_3) == hash(draft_panel_7)
    assert hash(draft_panel_4) == hash(draft_panel_8)
    assert hash(draft_panel_5) == hash(draft_panel_9)
    assert hash(draft_panel_6) == hash(draft_panel_10)


def test_fail_resized_layout_draft_panel_if_extra_params(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:

    with pytest.raises(TypeError):
        ResizedLayoutDraftPanel(Layout(), extra=123)  # type: ignore[call-arg]


# noinspection PyDataclass
def test_fail_resized_layout_draft_panel_no_assignments(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:

    resized_layout_panel = ResizedLayoutDraftPanel(Layout())

    with pytest.raises(AttributeError):
        resized_layout_panel.content = Layout()  # type: ignore[misc]

    with pytest.raises(AttributeError):
        resized_layout_panel.frame = empty_frame()  # type: ignore[misc]

    with pytest.raises(AttributeError):
        resized_layout_panel.constraints = Constraints()  # type: ignore[misc]

    with pytest.raises(AttributeError):
        resized_layout_panel.config = OutputConfig()  # type: ignore[misc]


@pc.parametrize_with_cases(
    'case',
    cases='.cases.layout_basics',
    has_tag=('dims_and_edge_cases', 'layout'),
)
def test_resized_layout_draft_panel_basic_dims_and_edge_cases(
    case: PanelFrameVariantTestCase[Layout],
    output_format_accessor: Annotated[OutputPropertyType, pc.fixture],
    skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture],
) -> None:
    frame_case = apply_frame_variant_to_test_case(case, stylized_stage=False)

    text_panel = ResizedLayoutDraftPanel(case.content, frame=frame_case.frame, config=case.config)

    assert_dims_aware_panel(
        text_panel,
        exp_dims=frame_case.exp_dims,
        exp_frame=frame_case.frame,
        exp_within_frame=frame_case.exp_within_frame,
    )


def test_draft_panel_render_next_stage(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:
    resized_layout_panel = ResizedLayoutDraftPanel(Layout(panel=MockPanel('Some text')))
    assert_next_stage_panel(
        this_panel=resized_layout_panel,
        next_stage=resized_layout_panel.render_next_stage(),
        next_stage_panel_cls=StylizedLayoutPanel,
        exp_content=Layout(panel=MockPanelStage3('Some text')),
    )

    resized_layout_panel_complex = ResizedLayoutDraftPanel(
        Layout(
            first=MockPanel('Some text'),
            second=MockPanel('Some other text'),
        ),
        frame=Frame(Dimensions(16, 5)),
        constraints=Constraints(container_width_per_line_limit=10),
        config=OutputConfig(indent_tab_size=1),
    )
    assert_next_stage_panel(
        this_panel=resized_layout_panel_complex,
        next_stage=resized_layout_panel_complex.render_next_stage(),
        next_stage_panel_cls=StylizedLayoutPanel,
        exp_content=Layout(
            first=MockPanelStage3('Some\ntext', frame=Frame(Dimensions(4, None))),
            second=MockPanelStage3('Some\nother\ntext', frame=Frame(Dimensions(5, None)))),
    )

    resized_layout_panel_complex = ResizedLayoutDraftPanel(
        Layout(
            first=MockPanelStage2('Some\ntext'),
            second=MockPanel('Some other text'),
        ),
        frame=Frame(Dimensions(21, 5)),
        constraints=Constraints(container_width_per_line_limit=10),
        config=OutputConfig(indent_tab_size=1),
    )
    assert_next_stage_panel(
        this_panel=resized_layout_panel_complex,
        next_stage=resized_layout_panel_complex.render_next_stage(),
        next_stage_panel_cls=StylizedLayoutPanel,
        exp_content=Layout(
            first=MockPanelStage3('Some\ntext'),
            second=MockPanelStage3('Some other\ntext', frame=Frame(Dimensions(10, None)))),
    )
