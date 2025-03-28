from typing import Annotated, TypedDict

import pytest

from omnipy.data._display.config import OutputConfig
from omnipy.data._display.constraints import Constraints
from omnipy.data._display.dimensions import Dimensions
from omnipy.data._display.frame import empty_frame, Frame, UndefinedFrame
from omnipy.data._display.panel.base import FrameT, Panel
from omnipy.data._display.panel.draft.base import DraftPanel
from omnipy.data._display.panel.draft.text import ReflowedTextDraftPanel


class _DraftOutputKwArgs(TypedDict, total=False):
    frame: Frame
    constraints: Constraints
    config: OutputConfig


def _create_draft_panel_kwargs(
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


def _assert_draft_panel(
    content: object,
    frame: Frame | None,
    constraints: Constraints | None,
    config: OutputConfig | None,
) -> None:
    kwargs = _create_draft_panel_kwargs(frame, constraints, config)
    draft_panel = DraftPanel(content, **kwargs)

    if frame is None:
        frame = empty_frame()

    if constraints is None:
        constraints = Constraints()

    if config is None:
        config = OutputConfig()

    assert draft_panel.content is content

    assert draft_panel.frame is not frame
    assert draft_panel.frame == frame

    assert draft_panel.constraints is not constraints
    assert draft_panel.constraints == constraints

    assert draft_panel.config is not config
    assert draft_panel.config == config


def test_draft_panel(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:
    _assert_draft_panel('Some text', None, None, None)
    _assert_draft_panel((1, 2, 3), Frame(Dimensions(None, None)), None, None)
    _assert_draft_panel((1, 2, 3), Frame(Dimensions(10, None)), None, None)
    _assert_draft_panel((1, 2, 3), Frame(Dimensions(None, 20)), None, None)
    _assert_draft_panel((1, 2, 3), Frame(Dimensions(10, 20)), None, None)
    _assert_draft_panel(None, None, None, OutputConfig(indent_tab_size=4))

    output = ('a', 'b', (1, 2, 3))
    _assert_draft_panel(output, None, Constraints(container_width_per_line_limit=10), None)
    _assert_draft_panel(
        output,
        Frame(Dimensions(20, 10)),
        Constraints(container_width_per_line_limit=10),
        OutputConfig(indent_tab_size=4),
    )


def test_draft_panel_hashable(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:
    draft_panel_1 = DraftPanel('')
    draft_panel_2 = DraftPanel('')

    assert hash(draft_panel_1) == hash(draft_panel_2)

    draft_panel_3 = DraftPanel('Some text')
    draft_panel_4 = DraftPanel('', frame=Frame(Dimensions(10, 20)))
    draft_panel_5 = DraftPanel('', constraints=Constraints(container_width_per_line_limit=10))
    draft_panel_6 = DraftPanel('', config=OutputConfig(indent_tab_size=4))

    assert hash(draft_panel_1) != hash(draft_panel_3) != hash(draft_panel_4) != hash(
        draft_panel_5) != hash(draft_panel_6)

    draft_panel_7 = DraftPanel('Some text')
    draft_panel_8 = DraftPanel('', frame=Frame(Dimensions(10, 20)))
    draft_panel_9 = DraftPanel('', constraints=Constraints(container_width_per_line_limit=10))
    draft_panel_10 = DraftPanel('', config=OutputConfig(indent_tab_size=4))

    assert hash(draft_panel_3) == hash(draft_panel_7)
    assert hash(draft_panel_4) == hash(draft_panel_8)
    assert hash(draft_panel_5) == hash(draft_panel_9)
    assert hash(draft_panel_6) == hash(draft_panel_10)


def test_draft_panel_mutable_not_hashable(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:
    # Test with mutable content
    mutable_content = [1, 2, 3]
    draft_panel = DraftPanel(mutable_content)

    with pytest.raises(TypeError):
        hash(draft_panel)  # Ensure hash is computed


# noinspection PyDataclass
def test_fail_draft_panel_no_assignments(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:
    draft_panel = DraftPanel('Some text')

    with pytest.raises(AttributeError):
        draft_panel.content = [1, 2, 3]  # type: ignore[misc, assignment]

    with pytest.raises(AttributeError):
        draft_panel.frame = Frame(Dimensions(10, 20))  # type: ignore[misc]

    with pytest.raises(AttributeError):
        draft_panel.constraints = Constraints(  # type: ignore[misc]
            container_width_per_line_limit=10)

    with pytest.raises(AttributeError):
        draft_panel.config = OutputConfig(indent_tab_size=4)  # type: ignore[misc]


def test_draft_panel_constraints_satisfaction(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:

    draft_panel = DraftPanel('Some text')
    assert draft_panel.satisfies.container_width_per_line_limit is None

    draft_panel = DraftPanel(
        'Some text', constraints=Constraints(container_width_per_line_limit=10))
    assert draft_panel.satisfies.container_width_per_line_limit is False


def test_draft_panel_with_empty_content(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:

    # Test with empty string
    empty_string_draft_panel = DraftPanel('')

    assert empty_string_draft_panel.content == ''
    assert empty_string_draft_panel.frame == empty_frame()
    assert empty_string_draft_panel.constraints == Constraints()
    assert empty_string_draft_panel.config == OutputConfig()

    # Test with None
    none_draft_panel = DraftPanel(None)

    assert none_draft_panel.content is None

    # Test with empty collections
    empty_list_draft_panel: DraftPanel[list, UndefinedFrame] = DraftPanel([])
    empty_dict_draft_panel: DraftPanel[dict, UndefinedFrame] = DraftPanel({})
    empty_tuple_draft_panel: DraftPanel[tuple, UndefinedFrame] = DraftPanel(())

    assert empty_list_draft_panel.content == []
    assert empty_dict_draft_panel.content == {}
    assert empty_tuple_draft_panel.content == ()

    # Test with empty content and frame
    framed_empty_draft_panel = DraftPanel('', frame=Frame(Dimensions(10, 5)))

    assert framed_empty_draft_panel.frame.dims.width == 10
    assert framed_empty_draft_panel.frame.dims.height == 5
    assert framed_empty_draft_panel.content == ''


def _assert_next_stage_panel(draft_panel: DraftPanel[object, FrameT],
                             next_stage: Panel[FrameT],
                             next_stage_panel_cls: type[DraftPanel[object, FrameT]],
                             expected_content: str) -> None:
    assert isinstance(next_stage, next_stage_panel_cls)
    assert next_stage.content == expected_content
    assert next_stage.frame == draft_panel.frame
    assert next_stage.constraints == draft_panel.constraints
    assert next_stage.config == draft_panel.config


def test_draft_panel_render_next_stage(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:
    draft_panel = DraftPanel('Some text')
    _assert_next_stage_panel(
        draft_panel,
        draft_panel.render_next_stage(),
        ReflowedTextDraftPanel,
        "'Some text'",
    )

    draft_panel_complex = DraftPanel(
        (1, 2, 3),
        frame=Frame(Dimensions(3, 5)),
        constraints=Constraints(container_width_per_line_limit=10),
        config=OutputConfig(indent_tab_size=1),
    )
    _assert_next_stage_panel(
        draft_panel_complex,
        draft_panel_complex.render_next_stage(),
        ReflowedTextDraftPanel,
        '(\n 1,\n 2,\n 3\n)',
    )
