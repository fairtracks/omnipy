from textwrap import dedent

import pytest
import pytest_cases as pc

from omnipy.data._display.config import OutputConfig
from omnipy.data._display.constraints import Constraints
from omnipy.data._display.dimensions import Dimensions
from omnipy.data._display.frame import empty_frame, Frame
from omnipy.data._display.panel.draft.text import ReflowedTextDraftPanel
from omnipy.data._display.panel.styling.text import SyntaxStylizedTextPanel
import omnipy.util._pydantic as pyd

from ..helpers.case_setup import (apply_frame_variant_to_test_case,
                                  PanelFrameVariantTestCase,
                                  PanelOutputTestCase)
from ..helpers.panel_assert import (assert_dims_aware_panel,
                                    assert_draft_panel_subcls,
                                    assert_next_stage_panel)


def test_reflowed_text_draft_panel_init() -> None:
    panel_cls = ReflowedTextDraftPanel
    assert_draft_panel_subcls(panel_cls, 'Some text')
    assert_draft_panel_subcls(
        panel_cls, '(1, 2, 3)', title='UnboundPanel', frame=Frame(Dimensions(None, None)))
    assert_draft_panel_subcls(
        panel_cls, '(1, 2, 3)', title='WidthBoundPanel', frame=Frame(Dimensions(10, None)))
    assert_draft_panel_subcls(
        panel_cls, '(1, 2, 3)', title='HeightBoundPanel', frame=Frame(Dimensions(None, 20)))
    assert_draft_panel_subcls(
        panel_cls, '(1, 2, 3)', title='BoundPanel', frame=Frame(Dimensions(10, 20)))
    assert_draft_panel_subcls(
        panel_cls, '{}', title='EmptyDictPanel', config=OutputConfig(indent_tab_size=4))

    content = "('a', 'b', (1, 2, 3))"
    assert_draft_panel_subcls(
        panel_cls,
        content,
        constraints=Constraints(container_width_per_line_limit=10),
    )
    assert_draft_panel_subcls(
        panel_cls,
        content,
        title='AllPanel',
        frame=Frame(Dimensions(20, 10)),
        constraints=Constraints(container_width_per_line_limit=10),
        config=OutputConfig(indent_tab_size=4),
    )


def test_reflowed_text_draft_panel_hashable() -> None:
    panel_1 = ReflowedTextDraftPanel('')
    panel_2 = ReflowedTextDraftPanel('')

    assert hash(panel_1) == hash(panel_2)

    panel_3 = ReflowedTextDraftPanel('Some text')
    panel_4 = ReflowedTextDraftPanel('', title='Some panel')
    panel_5 = ReflowedTextDraftPanel('', frame=Frame(Dimensions(10, 20)))
    panel_6 = ReflowedTextDraftPanel('', constraints=Constraints(container_width_per_line_limit=10))
    panel_7 = ReflowedTextDraftPanel('', config=OutputConfig(indent_tab_size=4))

    assert hash(panel_1) != hash(panel_3) != hash(panel_4) != hash(panel_5) != hash(panel_6) \
           != hash(panel_7)

    panel_8 = ReflowedTextDraftPanel('Some text')
    panel_9 = ReflowedTextDraftPanel('', title='Some panel')
    panel_10 = ReflowedTextDraftPanel('', frame=Frame(Dimensions(10, 20)))
    panel_11 = ReflowedTextDraftPanel(
        '', constraints=Constraints(container_width_per_line_limit=10))
    panel_12 = ReflowedTextDraftPanel('', config=OutputConfig(indent_tab_size=4))

    assert hash(panel_3) == hash(panel_8)
    assert hash(panel_4) == hash(panel_9)
    assert hash(panel_5) == hash(panel_10)
    assert hash(panel_6) == hash(panel_11)
    assert hash(panel_7) == hash(panel_12)


def test_fail_reflowed_text_draft_panel_if_extra_params() -> None:
    with pytest.raises(TypeError):
        ReflowedTextDraftPanel('[123, 234, 345]', extra=123)  # type: ignore[call-arg]


# noinspection PyDataclass
def test_fail_reflowed_text_draft_panel_no_assignments() -> None:
    reflowed_text_panel = ReflowedTextDraftPanel('Some text')

    with pytest.raises(AttributeError):
        reflowed_text_panel.content = 'Some other text'  # type: ignore[misc]

    with pytest.raises(AttributeError):
        reflowed_text_panel.title = 'My panel'  # type: ignore[misc]

    with pytest.raises(AttributeError):
        reflowed_text_panel.frame = empty_frame()  # type: ignore[misc]

    with pytest.raises(AttributeError):
        reflowed_text_panel.constraints = Constraints()  # type: ignore[misc]

    with pytest.raises(AttributeError):
        reflowed_text_panel.config = OutputConfig()  # type: ignore[misc]


@pc.parametrize_with_cases(
    'case',
    cases='.cases.text_basics',
    has_tag=('dims_and_edge_cases', 'syntax_text'),
)
def test_reflowed_text_draft_panel_basic_dims_and_edge_cases(
        case: PanelFrameVariantTestCase[str] | PanelOutputTestCase[str]) -> None:
    if isinstance(case, PanelFrameVariantTestCase):
        frame_case = apply_frame_variant_to_test_case(case, stylized_stage=False)
    else:
        frame_case = case

    assert not isinstance(case.config, pyd.UndefinedType)

    text_panel = ReflowedTextDraftPanel(
        case.content,
        title=case.title,
        frame=frame_case.frame,
        config=case.config,
    )
    assert_dims_aware_panel(
        text_panel,
        exp_dims=frame_case.exp_dims,
        exp_frame=frame_case.frame,
        exp_within_frame=frame_case.exp_within_frame,
    )


def test_reflowed_text_draft_panel_variable_width_chars() -> None:
    # Mandarin Chinese characters are double-width
    assert_dims_aware_panel(ReflowedTextDraftPanel('北京'), Dimensions(width=4, height=1))

    # Null character is zero-width
    assert_dims_aware_panel(ReflowedTextDraftPanel('\0北京\n北京'), Dimensions(width=4, height=2))

    # Soft hyphen character is zero-width
    assert_dims_aware_panel(
        ReflowedTextDraftPanel('hyphe\xad\nnate'), Dimensions(width=5, height=2))

    # Tab character width depends on context
    assert_dims_aware_panel(ReflowedTextDraftPanel('\tc'), Dimensions(width=5, height=1))
    assert_dims_aware_panel(ReflowedTextDraftPanel(' a\tb'), Dimensions(width=5, height=1))
    assert_dims_aware_panel(ReflowedTextDraftPanel('abcd  \te'), Dimensions(width=9, height=1))

    # Tab character width also depends on config
    assert_dims_aware_panel(
        ReflowedTextDraftPanel('\tc', config=OutputConfig(tab_size=6)),
        Dimensions(width=7, height=1),
    )
    assert_dims_aware_panel(
        ReflowedTextDraftPanel(' a\tb', config=OutputConfig(tab_size=6)),
        Dimensions(width=7, height=1),
    )
    assert_dims_aware_panel(
        ReflowedTextDraftPanel('abcd  \te', config=OutputConfig(tab_size=6)),
        Dimensions(width=13, height=1),
    )


#
# def test_reflowed_text_draft_panel_visible_char_coverage() -> None:
#     panel = ReflowedTextDraftPanel('', frame=Frame(Dimensions(width=6, height=3)))
#     assert panel.visible_char_coverage() == 0
#
#     # Test without a frame
#     panel = ReflowedTextDraftPanel('Line 1\nLine 2\nLine 3',)
#     assert panel.visible_char_coverage() == 18
#
#     # Ignore whitespace at beginning and end of line
#     panel = ReflowedTextDraftPanel('  Line 1\t\n    Line 2  \n  Line 3 ',)
#     assert panel.visible_char_coverage() == 18
#
#     # Test with a frame that fits multiple lines of text
#     panel = ReflowedTextDraftPanel(
#         '  Line 1\t\n    Line 2  \n  Line 3 ', frame=Frame(Dimensions(width=6, height=3)))
#     assert panel.visible_char_coverage() == 18  # 6 chars per line * 3 lines
#
#     # Test with a frame that truncates multi-line text vertically
#     panel = ReflowedTextDraftPanel(
#         '  Line 1\t\n    Line 2  \n  Line 3 ', frame=Frame(Dimensions(width=6, height=2)))
#     assert panel.visible_char_coverage() == 12  # 6 chars per line * 2 lines
#
#     # Test with a frame that truncates multi-line text both horizontally and
#     # vertically
#     panel = ReflowedTextDraftPanel(
#         '  Line 1\t\n    Line 2  \n  Line 3 ', frame=Frame(Dimensions(width=5, height=2)))
#     assert panel.visible_char_coverage() == 12  # 6 chars per line * 2 lines
#
#     # Test with Asian characters (double-width), rounding down
#     panel = ReflowedTextDraftPanel('\t北京欢迎你  ', frame=Frame(Dimensions(width=8, height=1)))
#     assert panel.visible_char_coverage() == 6  # 3 double-width chars (2 + 1)
#
#     # Test with Asian characters and multiple lines
#     panel = ReflowedTextDraftPanel('北京欢\n  迎你\n  上海', frame=Frame(Dimensions(width=8, height=2)))
#     assert panel.visible_char_coverage() == 12  # 8 chars (line 1) + 4 chars (line 2)
#
#     # Test with mixed content (Asian and English characters)
#     panel = ReflowedTextDraftPanel('Hello 北京', frame=Frame(Dimensions(width=10, height=1)))
#     assert panel.visible_char_coverage() == 10  # 5 English + 2 double-width Asian chars


def test_reflowed_text_draft_panel_max_container_width_across_lines() -> None:
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


def test_reflowed_text_draft_panel_constraints_satisfaction() -> None:
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


def test_draft_panel_render_next_stage() -> None:
    reflowed_text_panel = ReflowedTextDraftPanel('Some text')
    assert_next_stage_panel(
        this_panel=reflowed_text_panel,
        next_stage=reflowed_text_panel.render_next_stage(),
        next_stage_panel_cls=SyntaxStylizedTextPanel,
        exp_content=reflowed_text_panel.content,
    )

    reflowed_text_panel_complex = ReflowedTextDraftPanel(
        '(1, 2, 3)',
        title='My panel',
        frame=Frame(Dimensions(9, 1)),
        constraints=Constraints(container_width_per_line_limit=10),
        config=OutputConfig(indent_tab_size=1),
    )
    assert_next_stage_panel(
        this_panel=reflowed_text_panel_complex,
        next_stage=reflowed_text_panel_complex.render_next_stage(),
        next_stage_panel_cls=SyntaxStylizedTextPanel,
        exp_content=reflowed_text_panel_complex.content,
    )
