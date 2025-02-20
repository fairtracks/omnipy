from textwrap import dedent
from typing import Annotated, TypedDict

import pytest

from omnipy.data._display.config import OutputConfig
from omnipy.data._display.constraints import Constraints
from omnipy.data._display.dimensions import Dimensions
from omnipy.data._display.draft import DraftMonospacedOutput, DraftOutput
from omnipy.data._display.frame import Frame


class _DraftOutputKwArgs(TypedDict, total=False):
    frame: Frame
    config: OutputConfig


def _create_draft_output_kwargs(
    frame: Frame | None = None,
    constraints: Constraints | None = None,
    config: OutputConfig | None = None,
) -> _DraftOutputKwArgs:
    kwargs = _DraftOutputKwArgs()

    if frame is not None:
        kwargs['frame'] = frame

    if constraints is not None:
        kwargs['constraints'] = constraints

    if config is not None:
        kwargs['config'] = config

    return kwargs


def _assert_draft_output(
    content: object,
    frame: Frame | None,
    constraints: Constraints | None,
    config: OutputConfig | None,
) -> None:
    kwargs = _create_draft_output_kwargs(frame, constraints, config)
    draft = DraftOutput(content, **kwargs)

    if frame is None:
        frame = Frame()

    if constraints is None:
        constraints = Constraints()

    if config is None:
        config = OutputConfig()

    assert draft.content is content

    assert draft.frame is not frame
    assert draft.frame == frame

    assert draft.constraints is not constraints
    assert draft.constraints == constraints

    assert draft.config is not config
    assert draft.config == config


def test_draft_output(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:
    _assert_draft_output('Some text', None, None, None)
    _assert_draft_output([1, 2, 3], Frame(Dimensions(None, None)), None, None)
    _assert_draft_output([1, 2, 3], Frame(Dimensions(10, None)), None, None)
    _assert_draft_output([1, 2, 3], Frame(Dimensions(None, 20)), None, None)
    _assert_draft_output([1, 2, 3], Frame(Dimensions(10, 20)), None, None)
    _assert_draft_output(None, None, None, OutputConfig(indent_tab_size=4))

    output = {'a': 1, 'b': 2}
    _assert_draft_output(output, None, Constraints(container_width_per_line_limit=10), None)
    _assert_draft_output(
        output,
        Frame(Dimensions(20, 10)),
        Constraints(container_width_per_line_limit=10),
        OutputConfig(indent_tab_size=4),
    )


def test_draft_output_validate_assignments(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:
    draft = DraftOutput('Some text')

    draft.content = [1, 2, 3]  # type: ignore[assignment]
    assert draft.content == [1, 2, 3]

    frame = Frame(Dimensions(10, 20))
    draft.frame = frame
    assert draft.frame is not frame
    assert draft.frame == frame

    with pytest.raises(ValueError):
        draft.frame = 123  # type: ignore[assignment]

    constraints = Constraints(container_width_per_line_limit=10)
    draft.constraints = constraints
    assert draft.constraints is not constraints
    assert draft.constraints == constraints

    with pytest.raises(ValueError):
        draft.constraints = 'abc'

    config = OutputConfig(indent_tab_size=4)
    draft.config = config
    assert draft.config is not config
    assert draft.config == config

    with pytest.raises(ValueError):
        draft.config = 'abc'  # type: ignore[assignment]


def test_draft_output_constraints_satisfaction(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:

    draft = DraftOutput('Some text')
    assert draft.satisfies.container_width_per_line_limit is None

    draft = DraftOutput('Some text', constraints=Constraints(container_width_per_line_limit=10))
    assert draft.satisfies.container_width_per_line_limit is False


def _assert_draft_monospaced_output(
    output: str,
    width: int,
    height: int,
    frame_width: int | None = None,
    frame_height: int | None = None,
    fits_width: bool | None = None,
    fits_height: bool | None = None,
    fits_both: bool | None = None,
) -> None:
    draft = DraftMonospacedOutput(output, frame=Frame(Dimensions(frame_width, frame_height)))

    assert draft.dims.width == width
    assert draft.dims.height == height
    assert draft.frame.dims.width == frame_width
    assert draft.frame.dims.height == frame_height

    dims_fit = draft.within_frame
    assert dims_fit.width == fits_width
    assert dims_fit.height == fits_height
    assert dims_fit.both == fits_both


def test_draft_monospaced_output_within_frame(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:

    out = 'Some output\nAnother line'
    _assert_draft_monospaced_output(
        out, 12, 2, None, None, fits_width=None, fits_height=None, fits_both=None)
    _assert_draft_monospaced_output(
        out, 12, 2, 12, None, fits_width=True, fits_height=None, fits_both=None)
    _assert_draft_monospaced_output(
        out, 12, 2, None, 2, fits_width=None, fits_height=True, fits_both=None)
    _assert_draft_monospaced_output(
        out, 12, 2, 12, 2, fits_width=True, fits_height=True, fits_both=True)
    _assert_draft_monospaced_output(
        out, 12, 2, 11, None, fits_width=False, fits_height=None, fits_both=None)
    _assert_draft_monospaced_output(
        out, 12, 2, None, 1, fits_width=None, fits_height=False, fits_both=None)
    _assert_draft_monospaced_output(
        out, 12, 2, 12, 1, fits_width=True, fits_height=False, fits_both=False)
    _assert_draft_monospaced_output(
        out, 12, 2, 11, 2, fits_width=False, fits_height=True, fits_both=False)
    _assert_draft_monospaced_output(
        out, 12, 2, 11, 1, fits_width=False, fits_height=False, fits_both=False)


def test_draft_monospaced_output_validate_assignments(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:
    draft = DraftMonospacedOutput('Some text')

    draft.content = 'Some other text'
    assert draft.content == 'Some other text'

    with pytest.raises(ValueError):
        draft.content = [1, 2, 3]  # type: ignore[assignment]

    frame = Frame(Dimensions(10, 20))
    draft.frame = frame
    assert draft.frame is not frame
    assert draft.frame == frame

    with pytest.raises(ValueError):
        draft.frame = 123  # type: ignore[assignment]

    config = OutputConfig(indent_tab_size=4)
    draft.config = config
    assert draft.config is not config
    assert draft.config == config

    with pytest.raises(ValueError):
        draft.config = 'abc'  # type: ignore[assignment]


def test_draft_monospaced_output_frame_empty(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:
    _assert_draft_monospaced_output('', 0, 0, None, None, None, None, None)
    _assert_draft_monospaced_output('', 0, 0, 0, None, True, None, None)
    _assert_draft_monospaced_output('', 0, 0, None, 0, None, True, None)
    _assert_draft_monospaced_output('', 0, 0, 0, 0, True, True, True)


def test_draft_monospaced_output_variable_width_chars(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:
    # Mandarin Chinese characters are double-width
    _assert_draft_monospaced_output('北京', 4, 1)

    # Null character is zero-width
    _assert_draft_monospaced_output('\0北京\n北京', 4, 2)

    # Soft hyphen character is zero-width
    _assert_draft_monospaced_output('hyphe\xad\nnate', 5, 2)


def test_draft_monospaced_output_max_container_width_across_lines(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:

    assert DraftMonospacedOutput('').max_container_width_across_lines == 0
    assert DraftMonospacedOutput('(1, 2, 3)').max_container_width_across_lines == 9
    assert DraftMonospacedOutput(dedent("""(
      [1, 2],
      1234567
    )"""),).max_container_width_across_lines == 6
    assert DraftMonospacedOutput(dedent("""(
      [1, 2],
      {'asd': 1234567}
    )"""),).max_container_width_across_lines == 16
    assert DraftMonospacedOutput(
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


def test_draft_monospaced_output_constraints_satisfaction(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:

    out = dedent("""(
      [1, 2],
      {'asd': 1234567}
    )""")

    assert DraftMonospacedOutput(out).max_container_width_across_lines == 16
    assert DraftMonospacedOutput(out).satisfies.container_width_per_line_limit is None

    draft = DraftMonospacedOutput(out, constraints=Constraints(container_width_per_line_limit=17))
    assert draft.satisfies.container_width_per_line_limit is True

    draft = DraftMonospacedOutput(out, constraints=Constraints(container_width_per_line_limit=16))
    assert draft.satisfies.container_width_per_line_limit is True

    constraints_15 = Constraints(container_width_per_line_limit=15)
    draft = DraftMonospacedOutput(out, constraints=constraints_15)
    assert draft.satisfies.container_width_per_line_limit is False

    out_shorter = dedent("""(
      [1, 2],
      {'asd': 123456}
    )""")
    draft = DraftMonospacedOutput(out_shorter, constraints=constraints_15)
    assert draft.satisfies.container_width_per_line_limit is True
