from textwrap import dedent

import pytest
import pytest_cases as pc

from omnipy.data._display.config import OutputConfig
from omnipy.data._display.constraints import Constraints
from omnipy.data._display.dimensions import Dimensions
from omnipy.data._display.frame import empty_frame, Frame
from omnipy.data._display.panel.draft.base import DraftPanel
from omnipy.data._display.panel.draft.text import ReflowedTextDraftPanel
from omnipy.data._display.panel.styling.text import SyntaxStylizedTextPanel
from omnipy.shared.enums.display import SyntaxLanguage

from ..helpers.case_setup import (apply_frame_variant_to_test_case,
                                  PanelFrameVariantTestCase,
                                  PanelOutputTestCase,
                                  set_case_config)
from ..helpers.panel_assert import (assert_dims_aware_panel,
                                    assert_draft_panel_subcls,
                                    assert_next_stage_panel)


def test_text_draft_panel_init() -> None:
    assert_draft_panel_subcls(DraftPanel, 'Some text')

    assert_draft_panel_subcls(
        DraftPanel,
        '{"json": "data"}',
        title='My JSON file',
        frame=Frame(Dimensions(20, 10)),
        constraints=Constraints(max_inline_container_width_incl=10),
        config=OutputConfig(syntax=SyntaxLanguage.JSON),
    )


def test_text_draft_panel_render_next_stage_simple() -> None:
    text_draft_panel = DraftPanel('Some\ntext')
    assert_next_stage_panel(
        this_panel=text_draft_panel,
        next_stage=text_draft_panel.render_next_stage(),
        next_stage_panel_cls=ReflowedTextDraftPanel,
        exp_content='Some\ntext',
    )


def test_text_draft_panel_render_next_stage_with_repr_complex() -> None:
    draft_panel_complex = DraftPanel(
        dedent("""\
        def my_function():
            return (1, 2, 3)"""),
        title='My repr panel',
        frame=Frame(Dimensions(18, 2)),
        constraints=Constraints(max_inline_container_width_incl=10),
        config=OutputConfig(indent=1, syntax=SyntaxLanguage.PYTHON),
    )
    assert_next_stage_panel(
        this_panel=draft_panel_complex,
        next_stage=draft_panel_complex.render_next_stage(),
        next_stage_panel_cls=ReflowedTextDraftPanel,
        exp_content=dedent("""\
        def my_function():
            return (1, 2, 3)"""),
    )


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
        panel_cls, '{}', title='EmptyDictPanel', config=OutputConfig(indent=4))

    content = "('a', 'b', (1, 2, 3))"
    assert_draft_panel_subcls(
        panel_cls,
        content,
        constraints=Constraints(max_inline_container_width_incl=10),
    )
    assert_draft_panel_subcls(
        panel_cls,
        content,
        title='AllPanel',
        frame=Frame(Dimensions(20, 10)),
        constraints=Constraints(max_inline_container_width_incl=10),
        config=OutputConfig(indent=4),
    )


def test_reflowed_text_draft_panel_hashable() -> None:
    panel_1 = ReflowedTextDraftPanel('')
    panel_2 = ReflowedTextDraftPanel('')

    assert hash(panel_1) == hash(panel_2)

    panel_3 = ReflowedTextDraftPanel('Some text')
    panel_4 = ReflowedTextDraftPanel('', title='Some panel')
    panel_5 = ReflowedTextDraftPanel('', frame=Frame(Dimensions(10, 20)))
    panel_6 = ReflowedTextDraftPanel(
        '', constraints=Constraints(max_inline_container_width_incl=10))
    panel_7 = ReflowedTextDraftPanel('', config=OutputConfig(indent=4))

    assert hash(panel_1) != hash(panel_3) != hash(panel_4) != hash(panel_5) != hash(panel_6) \
           != hash(panel_7)

    panel_8 = ReflowedTextDraftPanel('Some text')
    panel_9 = ReflowedTextDraftPanel('', title='Some panel')
    panel_10 = ReflowedTextDraftPanel('', frame=Frame(Dimensions(10, 20)))
    panel_11 = ReflowedTextDraftPanel(
        '', constraints=Constraints(max_inline_container_width_incl=10))
    panel_12 = ReflowedTextDraftPanel('', config=OutputConfig(indent=4))

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
    'any_case',
    cases='.cases.text_basics',
    has_tag=('dims_and_edge_cases', 'syntax_text'),
)
def test_reflowed_text_draft_panel_basic_dims_and_edge_cases(
        any_case: PanelFrameVariantTestCase[str] | PanelOutputTestCase[str]) -> None:
    if isinstance(any_case, PanelFrameVariantTestCase):
        case = apply_frame_variant_to_test_case(any_case, stylized_stage=False)
    else:
        case = any_case

    case = set_case_config(case, min_panel_width=0)

    text_panel = ReflowedTextDraftPanel(
        case.content,
        title=case.title,
        frame=case.frame,
        config=case.config,
    )
    assert_dims_aware_panel(
        text_panel,
        exp_dims=case.exp_dims,
        exp_frame=case.frame,
        exp_within_frame=case.exp_within_frame,
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
        ReflowedTextDraftPanel('\tc', config=OutputConfig(tab=6)),
        Dimensions(width=7, height=1),
    )
    assert_dims_aware_panel(
        ReflowedTextDraftPanel(' a\tb', config=OutputConfig(tab=6)),
        Dimensions(width=7, height=1),
    )
    assert_dims_aware_panel(
        ReflowedTextDraftPanel('abcd  \te', config=OutputConfig(tab=6)),
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


def test_overflow_lines() -> None:
    panel = ReflowedTextDraftPanel('')
    assert panel.horizontal_overflow_lines == []

    panel = ReflowedTextDraftPanel('Short line')
    assert panel.horizontal_overflow_lines == []

    panel = ReflowedTextDraftPanel('Short line', frame=Frame(Dimensions(10, None)))
    assert panel.horizontal_overflow_lines == []

    panel = ReflowedTextDraftPanel('Short line', frame=Frame(Dimensions(9, None)))
    assert panel.horizontal_overflow_lines == ['Short line']

    panel = ReflowedTextDraftPanel(
        'Line one\nLonger line two\nShort', frame=Frame(Dimensions(9, None)))
    assert panel.horizontal_overflow_lines == ['Longer line two']

    panel = ReflowedTextDraftPanel(
        'Line one\nLonger line two\n    Spaced        ', frame=Frame(Dimensions(9, None)))
    assert panel.horizontal_overflow_lines == ['Longer line two', '    Spaced        ']

    panel = ReflowedTextDraftPanel(
        'Line one\nLonger line two\n    Spaced        ', frame=Frame(Dimensions(0, None)))
    assert panel.horizontal_overflow_lines == ['Line one', 'Longer line two', '    Spaced        ']


def test_reflowed_text_draft_panel_max_inline_container_width_incl() -> None:
    assert ReflowedTextDraftPanel('').max_inline_container_width_incl == 0

    assert ReflowedTextDraftPanel('(1, 2, 3)').max_inline_container_width_incl == 9

    assert ReflowedTextDraftPanel(
        dedent("""(
            [1, 2],
            1234567
        )"""),).max_inline_container_width_incl == 6

    assert ReflowedTextDraftPanel(
        dedent("""(
            [1, 2],
            {'asd': 1234567}
        )"""),).max_inline_container_width_incl == 16

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
        )"""),).max_inline_container_width_incl == 0


def test_reflowed_text_draft_panel_max_inline_list_or_dict_width_excl() -> None:
    assert ReflowedTextDraftPanel('').max_inline_list_or_dict_width_excl == 0

    # Only defined for lists and dicts, not tuples
    assert ReflowedTextDraftPanel('(1, 2, 3)').max_inline_list_or_dict_width_excl == 0

    assert ReflowedTextDraftPanel(dedent("""
        [1, 2]
    """),).max_inline_list_or_dict_width_excl == 4

    assert ReflowedTextDraftPanel(
        dedent("""
            {"asd": 1234567, "dsa": 65432}
        """),).max_inline_list_or_dict_width_excl == 28

    assert ReflowedTextDraftPanel(
        dedent("""
            [
              1, 2, 3, 4,
              5, 6, 7
            ]
        """),).max_inline_list_or_dict_width_excl == 10

    assert ReflowedTextDraftPanel(
        dedent("""
            {
              "asd": 1234567, "dsa": [ 1, 2, 3, 4 ],
              "qwe": 1234567890
            }
        """),).max_inline_list_or_dict_width_excl == 37

    assert ReflowedTextDraftPanel(
        dedent("""
            [
              1, 2, 3, [ 4, 5, 6 ],
              [ 7, 8, 9, 10 ]
            ]
        """),).max_inline_list_or_dict_width_excl == 20

    assert ReflowedTextDraftPanel(
        dedent("""
            [
              {"asd": 1234567},
              {"qwe": 1234567890}
            ]
        """),).max_inline_list_or_dict_width_excl == 19

    assert ReflowedTextDraftPanel(
        dedent("""
            [
              {"asd": 1234567, "dsa": 65432},
              {"qwe": 1234567890}, {"rty": 987654321}
            ]
        """),).max_inline_list_or_dict_width_excl == 39

    assert ReflowedTextDraftPanel(
        dedent("""
            {
              "this_is_a_very_long_key_longer_than_most": [
                { "asd": 1234567, "dsa": "abcde" },
                { "qwe": 1234567890 },
                { "rty": 987654321 }
              ], "no": [
                { "asd": 12 }, { "dsa": "abc" }
              ]
            }
        """),).max_inline_list_or_dict_width_excl == 34

    assert ReflowedTextDraftPanel(
        dedent("""
            {
              "asd": [1, 2, 3, 4], "dsa": [5, 6, 7],
              "qwe": [8, 9, 10]
            }
        """),).max_inline_list_or_dict_width_excl == 37

    assert ReflowedTextDraftPanel(
        dedent("""
            {
              "asd": {"12": "abc", "13": "def"}, "dsa": {"14": "ghi"},
              "qwe": {"15": "jkl"}
            }
        """),).max_inline_list_or_dict_width_excl == 55

    assert ReflowedTextDraftPanel(
        dedent("""
            [
              {
                "asd"    : {"12": "abc", "13": "def", "14": "ghi", "15": "jkl"},
                "dsa"    : {"14": "ghi"}, "qwe": {"15": "jkl"}
              }, {
                "asd"    : {"12": "abc", "13": "def"},
                "dsa"    : {"14": "ghi"},
              },
            ]
        """),).max_inline_list_or_dict_width_excl == 52

    assert ReflowedTextDraftPanel(
        dedent("""
            [
              {
                "geometry": {
                  "loc": { "lng": 77.2, "lat": 28.1 },
                  "vp": { "ne": { "lng": 77.2, "lat": 28.1 }, "se": { "lng": 77.2, "lat": 28.6 } },
                }
              }
            ]
        """),).max_inline_list_or_dict_width_excl == 74


def test_reflowed_text_draft_panel_max_inline_list_or_dict_width_excl_no_counts() -> None:
    # Only defined for lists and dicts, not tuples
    assert ReflowedTextDraftPanel('(1, 2, 3)').max_inline_list_or_dict_width_excl == 0

    # Do not count lists within a string
    assert ReflowedTextDraftPanel(dedent("""
        "[1, 2]"
    """),).max_inline_list_or_dict_width_excl == 0

    # Do not count simple items within a list
    assert ReflowedTextDraftPanel(
        dedent("""
        [
          1,
          "abc"
        ]
    """),).max_inline_list_or_dict_width_excl == 0

    # Do not count lists within a string within a list
    assert ReflowedTextDraftPanel(
        dedent("""
            [
              "[1, 2, 3]",
              123
            ]
        """),).max_inline_list_or_dict_width_excl == 0

    # Do not count simple items within a dict
    assert ReflowedTextDraftPanel(
        dedent("""
            {
              "asd": 1234567,
              "dsa": 65432
            }
        """),).max_inline_list_or_dict_width_excl == 0

    # Do not count lists within a string within a dict
    assert ReflowedTextDraftPanel(
        dedent("""
            {
              "asd": "[1, 2, 3]"
            }
        """),).max_inline_list_or_dict_width_excl == 0


def test_reflowed_text_draft_panel_max_inline_list_or_dict_width_excl_border_cases() -> None:
    # assert ReflowedTextDraftPanel(
    #     dedent("""
    #     [
    #         "\\\", [1, 2]"
    #     ]
    # """),).max_inline_list_or_dict_width_excl == 0
    #
    # assert ReflowedTextDraftPanel(
    #     dedent("""
    #     {
    #         "key:": "value"
    #     }
    # """),).max_inline_list_or_dict_width_excl == 0

    assert ReflowedTextDraftPanel(
        dedent("""
        {
            "key": "value:"
        }
    """),).max_inline_list_or_dict_width_excl == 0


def test_reflowed_text_draft_panel_constraints_satisfaction() -> None:
    out = dedent("""(
      [1, 2],
      {"asd": 1234567}
    )""")

    assert ReflowedTextDraftPanel(out).max_inline_container_width_incl == 16
    assert ReflowedTextDraftPanel(out).max_inline_list_or_dict_width_excl == 14
    assert ReflowedTextDraftPanel(out).satisfies.max_inline_container_width_incl is None
    assert ReflowedTextDraftPanel(out).satisfies.max_inline_list_or_dict_width_excl is None

    draft = ReflowedTextDraftPanel(out, constraints=Constraints(max_inline_container_width_incl=16))
    assert draft.satisfies.max_inline_container_width_incl is True
    assert draft.satisfies.max_inline_list_or_dict_width_excl is None

    draft = ReflowedTextDraftPanel(
        out, constraints=Constraints(max_inline_list_or_dict_width_excl=14))
    assert draft.satisfies.max_inline_container_width_incl is None
    assert draft.satisfies.max_inline_list_or_dict_width_excl is True

    constraints_too_tight = Constraints(
        max_inline_container_width_incl=15, max_inline_list_or_dict_width_excl=13)
    draft = ReflowedTextDraftPanel(out, constraints=constraints_too_tight)
    assert draft.satisfies.max_inline_container_width_incl is False
    assert draft.satisfies.max_inline_list_or_dict_width_excl is False

    out_shorter = dedent("""(
      [1, 2],
      {"asd": 123456}
    )""")
    draft = ReflowedTextDraftPanel(out_shorter, constraints=constraints_too_tight)
    assert draft.satisfies.max_inline_container_width_incl is True
    assert draft.satisfies.max_inline_list_or_dict_width_excl is True


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
        constraints=Constraints(max_inline_container_width_incl=10),
        config=OutputConfig(indent=1),
    )
    assert_next_stage_panel(
        this_panel=reflowed_text_panel_complex,
        next_stage=reflowed_text_panel_complex.render_next_stage(),
        next_stage_panel_cls=SyntaxStylizedTextPanel,
        exp_content=reflowed_text_panel_complex.content,
    )
