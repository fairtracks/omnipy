from textwrap import dedent
from typing import Annotated

import pytest

from omnipy.data._display.config import OutputConfig
from omnipy.data._display.constraints import Constraints
from omnipy.data._display.dimensions import Dimensions
from omnipy.data._display.frame import empty_frame, Frame
from omnipy.data._display.panel.base import FrameT, Panel
from omnipy.data._display.panel.draft.text import ReflowedTextDraftPanel
from omnipy.data._display.panel.styling.text import SyntaxStylizedTextPanel


def _assert_reflowed_text_draft_panel(
    output: str,
    width: int,
    height: int,
    frame_width: int | None = None,
    frame_height: int | None = None,
    fits_width: bool | None = None,
    fits_height: bool | None = None,
    fits_both: bool | None = None,
) -> None:
    reflowed_text_panel = ReflowedTextDraftPanel(
        output, frame=Frame(Dimensions(frame_width, frame_height)))

    assert reflowed_text_panel.dims.width == width
    assert reflowed_text_panel.dims.height == height
    assert reflowed_text_panel.frame.dims.width == frame_width
    assert reflowed_text_panel.frame.dims.height == frame_height

    dims_fit = reflowed_text_panel.within_frame
    assert dims_fit.width == fits_width
    assert dims_fit.height == fits_height
    assert dims_fit.both == fits_both


def test_reflowed_text_draft_panel_within_frame(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:

    out = 'Some output\nAnother line'
    _assert_reflowed_text_draft_panel(
        out, 12, 2, None, None, fits_width=None, fits_height=None, fits_both=None)
    _assert_reflowed_text_draft_panel(
        out, 12, 2, 12, None, fits_width=True, fits_height=None, fits_both=None)
    _assert_reflowed_text_draft_panel(
        out, 12, 2, None, 2, fits_width=None, fits_height=True, fits_both=None)
    _assert_reflowed_text_draft_panel(
        out, 12, 2, 12, 2, fits_width=True, fits_height=True, fits_both=True)
    _assert_reflowed_text_draft_panel(
        out, 12, 2, 11, None, fits_width=False, fits_height=None, fits_both=None)
    _assert_reflowed_text_draft_panel(
        out, 12, 2, None, 1, fits_width=None, fits_height=False, fits_both=None)
    _assert_reflowed_text_draft_panel(
        out, 12, 2, 12, 1, fits_width=True, fits_height=False, fits_both=False)
    _assert_reflowed_text_draft_panel(
        out, 12, 2, 11, 2, fits_width=False, fits_height=True, fits_both=False)
    _assert_reflowed_text_draft_panel(
        out, 12, 2, 11, 1, fits_width=False, fits_height=False, fits_both=False)


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


def test_reflowed_text_draft_panel_frame_empty(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:
    _assert_reflowed_text_draft_panel('', 0, 0, None, None, None, None, None)
    _assert_reflowed_text_draft_panel('', 0, 0, 0, None, True, None, None)
    _assert_reflowed_text_draft_panel('', 0, 0, None, 0, None, True, None)
    _assert_reflowed_text_draft_panel('', 0, 0, 0, 0, True, True, True)


def test_reflowed_text_draft_panel_variable_width_chars(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:
    # Mandarin Chinese characters are double-width
    _assert_reflowed_text_draft_panel('北京', 4, 1)

    # Null character is zero-width
    _assert_reflowed_text_draft_panel('\0北京\n北京', 4, 2)

    # Soft hyphen character is zero-width
    _assert_reflowed_text_draft_panel('hyphe\xad\nnate', 5, 2)


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


def test_reflowed_text_draft_panel_with_empty_content(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:
    # Test with empty string
    reflowed_empty_text_panel = ReflowedTextDraftPanel('')

    assert reflowed_empty_text_panel.content == ''
    assert reflowed_empty_text_panel.dims.width == 0
    assert reflowed_empty_text_panel.dims.height == 0

    # Test with only whitespace
    reflowed_whitespace_panel = ReflowedTextDraftPanel('  \n  ')

    assert reflowed_whitespace_panel.content == '  \n  '
    assert reflowed_whitespace_panel.dims.width == 2
    assert reflowed_whitespace_panel.dims.height == 2

    # Test empty content with frame
    framed_reflowed_empty_text_panel = ReflowedTextDraftPanel('', frame=Frame(Dimensions(10, 5)))

    assert framed_reflowed_empty_text_panel.within_frame.width is True
    assert framed_reflowed_empty_text_panel.within_frame.height is True
    assert framed_reflowed_empty_text_panel.within_frame.both is True

    # Test empty content with constraints
    constrained_reflowed_empty_text_panel = ReflowedTextDraftPanel(
        '', constraints=Constraints(container_width_per_line_limit=10))

    assert constrained_reflowed_empty_text_panel.satisfies.container_width_per_line_limit is True
    assert constrained_reflowed_empty_text_panel.max_container_width_across_lines == 0


def _assert_next_stage_panel(
    reflowed_text_panel: ReflowedTextDraftPanel[FrameT],
    next_stage: Panel[FrameT],
    next_stage_panel_cls: type[ReflowedTextDraftPanel[FrameT]],
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
