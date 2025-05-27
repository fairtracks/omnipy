from typing import Annotated

import pytest_cases as pc

from omnipy.data._display.layout import Layout
from omnipy.data._display.panel.draft.base import DraftPanel
from omnipy.data._display.panel.styling.layout import StylizedLayoutPanel

from .helpers import (apply_frame_variant_to_test_case,
                      assert_dims_aware_panel,
                      OutputPropertyType,
                      PanelFrameVariantTestCase,
                      PanelOutputTestCase,
                      prepare_test_case_for_stylized_layout,
                      strip_all_styling_from_panel_output)


@pc.parametrize_with_cases(
    'case',
    cases='.cases.layout_reflow',
    has_tag=('reflow_cases', 'layout'),
)
def test_resized_layout_draft_panel_reflow_cases(case: PanelFrameVariantTestCase[Layout]) -> None:
    frame_case = apply_frame_variant_to_test_case(case, stylized_stage=False)

    draft_layout_panel = DraftPanel(
        case.content,
        title=case.title,
        frame=frame_case.frame,
        config=case.config,
    )

    resized_layout_panel = draft_layout_panel.render_next_stage()

    assert_dims_aware_panel(
        resized_layout_panel,
        exp_dims=frame_case.exp_dims,
        exp_frame=frame_case.frame,
        exp_within_frame=frame_case.exp_within_frame,
    )


@pc.parametrize_with_cases(
    'case',
    cases='.cases.layout_reflow',
    has_tag=('reflow_cases', 'layout'),
)
def test_stylized_layout_panel_reflow_cases(
    case: PanelOutputTestCase[Layout] | PanelFrameVariantTestCase[Layout],
    plain_terminal: Annotated[OutputPropertyType, pc.fixture],
    output_format_accessor: Annotated[OutputPropertyType, pc.fixture],
) -> None:
    case = prepare_test_case_for_stylized_layout(case, plain_terminal, output_format_accessor)

    draft_layout_panel = DraftPanel(
        case.content,
        title=case.title,
        frame=case.frame,
        config=case.config,
    )

    layout_panel = StylizedLayoutPanel(draft_layout_panel)

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
