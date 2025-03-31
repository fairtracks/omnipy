from textwrap import dedent
from typing import Annotated

import pytest
import pytest_cases as pc

from omnipy.data._display.config import OutputConfig
from omnipy.data._display.constraints import Constraints
from omnipy.data._display.dimensions import Dimensions
from omnipy.data._display.frame import empty_frame, Frame
from omnipy.data._display.panel.base import FrameT, FullyRenderedPanel
from omnipy.data._display.panel.draft.text import ReflowedTextDraftPanel
from omnipy.data._display.panel.styling.text import SyntaxStylizedTextPanel

from .helpers import (apply_frame_variant_to_test_case,
                      assert_dims_aware_panel,
                      assert_draft_panel_subcls,
                      OutputPropertyType,
                      PanelOutputFrameVariantTestCase)


def test_reflowed_text_draft_panel_init(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:
    panel_cls = ReflowedTextDraftPanel
    assert_draft_panel_subcls(panel_cls, 'Some text', None, None, None)
    assert_draft_panel_subcls(panel_cls, '(1, 2, 3)', Frame(Dimensions(None, None)), None, None)
    assert_draft_panel_subcls(panel_cls, '(1, 2, 3)', Frame(Dimensions(10, None)), None, None)
    assert_draft_panel_subcls(panel_cls, '(1, 2, 3)', Frame(Dimensions(None, 20)), None, None)
    assert_draft_panel_subcls(panel_cls, '(1, 2, 3)', Frame(Dimensions(10, 20)), None, None)
    assert_draft_panel_subcls(panel_cls, '{}', None, None, OutputConfig(indent_tab_size=4))

    content = "('a', 'b', (1, 2, 3))"
    assert_draft_panel_subcls(
        panel_cls,
        content,
        None,
        Constraints(container_width_per_line_limit=10),
        None,
    )
    assert_draft_panel_subcls(
        panel_cls,
        content,
        Frame(Dimensions(20, 10)),
        Constraints(container_width_per_line_limit=10),
        OutputConfig(indent_tab_size=4),
    )


def test_reflowed_text_draft_panel_hashable(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:
    draft_panel_1 = ReflowedTextDraftPanel('')
    draft_panel_2 = ReflowedTextDraftPanel('')

    assert hash(draft_panel_1) == hash(draft_panel_2)

    draft_panel_3 = ReflowedTextDraftPanel('Some text')
    draft_panel_4 = ReflowedTextDraftPanel('', frame=Frame(Dimensions(10, 20)))
    draft_panel_5 = ReflowedTextDraftPanel(
        '', constraints=Constraints(container_width_per_line_limit=10))
    draft_panel_6 = ReflowedTextDraftPanel('', config=OutputConfig(indent_tab_size=4))

    assert hash(draft_panel_1) != hash(draft_panel_3) != hash(draft_panel_4) != hash(
        draft_panel_5) != hash(draft_panel_6)

    draft_panel_7 = ReflowedTextDraftPanel('Some text')
    draft_panel_8 = ReflowedTextDraftPanel('', frame=Frame(Dimensions(10, 20)))
    draft_panel_9 = ReflowedTextDraftPanel(
        '', constraints=Constraints(container_width_per_line_limit=10))
    draft_panel_10 = ReflowedTextDraftPanel('', config=OutputConfig(indent_tab_size=4))

    assert hash(draft_panel_3) == hash(draft_panel_7)
    assert hash(draft_panel_4) == hash(draft_panel_8)
    assert hash(draft_panel_5) == hash(draft_panel_9)
    assert hash(draft_panel_6) == hash(draft_panel_10)


def test_fail_reflowed_text_draft_panel_if_extra_params(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:

    with pytest.raises(TypeError):
        ReflowedTextDraftPanel('[123, 234, 345]', extra=123)  # type: ignore[call-arg]


# noinspection PyDataclass
def test_fail_reflowed_text_draft_panel_no_assignments(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:

    reflowed_text_panel = ReflowedTextDraftPanel('Some text')

    with pytest.raises(AttributeError):
        reflowed_text_panel.content = 'Some other text'  # type: ignore[misc]

    with pytest.raises(AttributeError):
        reflowed_text_panel.frame = empty_frame()  # type: ignore[misc]

    with pytest.raises(AttributeError):
        reflowed_text_panel.constraints = Constraints()  # type: ignore[misc]

    with pytest.raises(AttributeError):
        reflowed_text_panel.config = OutputConfig()  # type: ignore[misc]


@pc.parametrize_with_cases(
    'case',
    cases='.cases.text_basics',
    has_tag=('dimensions', 'syntax_text'),
)
def test_reflowed_text_draft_panel_basics_dimensions(
    case: PanelOutputFrameVariantTestCase[str],
    output_format_accessor: Annotated[OutputPropertyType, pc.fixture],
    skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture],
) -> None:
    frame_case = apply_frame_variant_to_test_case(case, crop_to_frame=False)

    text_panel = ReflowedTextDraftPanel(case.content, frame=frame_case.frame, config=case.config)
    assert_dims_aware_panel(
        text_panel,
        exp_dims=frame_case.exp_dims,
        exp_frame=frame_case.frame,
        exp_within_frame=frame_case.exp_within_frame,
    )


def test_reflowed_text_draft_panel_variable_width_chars(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:
    # Mandarin Chinese characters are double-width
    assert_dims_aware_panel(ReflowedTextDraftPanel('北京'), Dimensions(width=4, height=1))

    # Null character is zero-width
    assert_dims_aware_panel(ReflowedTextDraftPanel('\0北京\n北京'), Dimensions(width=4, height=2))

    # Soft hyphen character is zero-width
    assert_dims_aware_panel(
        ReflowedTextDraftPanel('hyphe\xad\nnate'), Dimensions(width=5, height=2))


def test_reflowed_text_draft_panel_max_container_width_across_lines(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:

    assert ReflowedTextDraftPanel('').max_container_width_across_lines == 0
    assert ReflowedTextDraftPanel('(1, 2, 3)').max_container_width_across_lines == 9
    assert ReflowedTextDraftPanel(dedent("""(
      [1, 2],
      1234567
    )"""),).max_container_width_across_lines == 6
    assert ReflowedTextDraftPanel(dedent("""(
      [1, 2],
      {'asd': 1234567}
    )"""),).max_container_width_across_lines == 16
    assert ReflowedTextDraftPanel(
        dedent("""(
      [
        1,
        2
      ],
      {
        'asd':
        1234567
      }
    )"""),).max_container_width_across_lines == 0


def test_reflowed_text_draft_panel_constraints_satisfaction(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:

    out = dedent("""(
      [1, 2],
      {'asd': 1234567}
    )""")

    assert ReflowedTextDraftPanel(out).max_container_width_across_lines == 16
    assert ReflowedTextDraftPanel(out).satisfies.container_width_per_line_limit is None

    draft = ReflowedTextDraftPanel(out, constraints=Constraints(container_width_per_line_limit=17))
    assert draft.satisfies.container_width_per_line_limit is True

    draft = ReflowedTextDraftPanel(out, constraints=Constraints(container_width_per_line_limit=16))
    assert draft.satisfies.container_width_per_line_limit is True

    constraints_15 = Constraints(container_width_per_line_limit=15)
    draft = ReflowedTextDraftPanel(out, constraints=constraints_15)
    assert draft.satisfies.container_width_per_line_limit is False

    out_shorter = dedent("""(
      [1, 2],
      {'asd': 123456}
    )""")
    draft = ReflowedTextDraftPanel(out_shorter, constraints=constraints_15)
    assert draft.satisfies.container_width_per_line_limit is True


def _assert_next_stage_panel(
    reflowed_text_panel: ReflowedTextDraftPanel[FrameT],
    next_stage: FullyRenderedPanel[FrameT],
    next_stage_panel_cls: type[SyntaxStylizedTextPanel[FrameT]],
) -> None:
    assert isinstance(next_stage, next_stage_panel_cls)
    assert next_stage.content == reflowed_text_panel.content
    assert next_stage.frame == reflowed_text_panel.frame
    assert next_stage.constraints == reflowed_text_panel.constraints
    assert next_stage.config == reflowed_text_panel.config


def test_draft_panel_render_next_stage(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:
    reflowed_text_panel = ReflowedTextDraftPanel('Some text')
    _assert_next_stage_panel(
        reflowed_text_panel,
        reflowed_text_panel.render_next_stage(),
        SyntaxStylizedTextPanel,
    )

    reflowed_text_panel_complex = ReflowedTextDraftPanel(
        '(1, 2, 3)',
        frame=Frame(Dimensions(9, 1)),
        constraints=Constraints(container_width_per_line_limit=10),
        config=OutputConfig(indent_tab_size=1),
    )
    _assert_next_stage_panel(
        reflowed_text_panel_complex,
        reflowed_text_panel_complex.render_next_stage(),
        SyntaxStylizedTextPanel,
    )
