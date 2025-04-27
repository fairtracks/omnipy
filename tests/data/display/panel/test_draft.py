from typing import Annotated

import pytest

from omnipy.data._display.config import OutputConfig
from omnipy.data._display.constraints import Constraints
from omnipy.data._display.dimensions import Dimensions
from omnipy.data._display.frame import (AnyFrame,
                                        empty_frame,
                                        Frame,
                                        FrameWithWidthAndHeight,
                                        UndefinedFrame)
from omnipy.data._display.layout import Layout
from omnipy.data._display.panel.draft.base import DraftPanel
from omnipy.data._display.panel.draft.layout import ResizedLayoutDraftPanel
from omnipy.data._display.panel.draft.text import ReflowedTextDraftPanel

from ..helpers.classes import MockPanel, MockPanelStage2
from .helpers import assert_draft_panel_subcls, assert_next_stage_panel


def test_draft_panel_init(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:
    assert_draft_panel_subcls(DraftPanel, 'Some text', None, None, None)
    assert_draft_panel_subcls(DraftPanel, (1, 2, 3), Frame(Dimensions(None, None)), None, None)
    assert_draft_panel_subcls(DraftPanel, (1, 2, 3), Frame(Dimensions(10, None)), None, None)
    assert_draft_panel_subcls(DraftPanel, (1, 2, 3), Frame(Dimensions(None, 20)), None, None)
    assert_draft_panel_subcls(DraftPanel, (1, 2, 3), Frame(Dimensions(10, 20)), None, None)
    assert_draft_panel_subcls(DraftPanel, None, None, None, OutputConfig(indent_tab_size=4))

    content = ('a', 'b', (1, 2, 3))
    assert_draft_panel_subcls(
        DraftPanel,
        content,
        None,
        Constraints(container_width_per_line_limit=10),
        None,
    )
    assert_draft_panel_subcls(
        DraftPanel,
        content,
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


def test_draft_panel_render_next_stage_with_repr(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:
    draft_panel = DraftPanel('Some text')
    assert_next_stage_panel(
        this_panel=draft_panel,
        next_stage=draft_panel.render_next_stage(),
        next_stage_panel_cls=ReflowedTextDraftPanel,
        exp_content="'Some text'",
    )

    draft_panel_complex = DraftPanel(
        (1, 2, 3),
        frame=Frame(Dimensions(3, 5)),
        constraints=Constraints(container_width_per_line_limit=10),
        config=OutputConfig(indent_tab_size=1),
    )
    assert_next_stage_panel(
        this_panel=draft_panel_complex,
        next_stage=draft_panel_complex.render_next_stage(),
        next_stage_panel_cls=ReflowedTextDraftPanel,
        exp_content='(\n 1,\n 2,\n 3\n)',
    )


def test_draft_panel_render_next_stage_with_layout(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:
    draft_panel: DraftPanel[Layout, AnyFrame] = DraftPanel(Layout())
    assert_next_stage_panel(
        this_panel=draft_panel,
        next_stage=draft_panel.render_next_stage(),
        next_stage_panel_cls=ResizedLayoutDraftPanel,
        exp_content=Layout(),
    )

    draft_panel_complex: DraftPanel[Layout, FrameWithWidthAndHeight] = DraftPanel(
        Layout(tuple=MockPanel('(1, 2, 3)'), text=MockPanel('Here is some text')),
        frame=Frame(Dimensions(21, 5)),
        constraints=Constraints(container_width_per_line_limit=10),
        config=OutputConfig(indent_tab_size=1),
    )
    assert_next_stage_panel(
        this_panel=draft_panel_complex,
        next_stage=draft_panel_complex.render_next_stage(),
        next_stage_panel_cls=ResizedLayoutDraftPanel,
        exp_content=Layout(
            tuple=MockPanelStage2(
                '(1, 2,\n3)',
                frame=Frame(Dimensions(6, 2)),
            ),
            text=MockPanelStage2(
                'Here is\nsome\ntext',
                frame=Frame(Dimensions(7, 3)),
            ),
        ),
    )

    draft_panel_half_framed: DraftPanel[Layout, FrameWithWidthAndHeight] = DraftPanel(
        Layout(
            tuple=MockPanel('(1, 2, 3)', frame=Frame(Dimensions(9, 1))),
            text=MockPanel('Here is some text')),
        frame=Frame(Dimensions(20, 5)),
        constraints=Constraints(container_width_per_line_limit=10),
        config=OutputConfig(indent_tab_size=1),
    )
    assert_next_stage_panel(
        this_panel=draft_panel_half_framed,
        next_stage=draft_panel_half_framed.render_next_stage(),
        next_stage_panel_cls=ResizedLayoutDraftPanel,
        exp_content=Layout(
            tuple=MockPanelStage2(
                '(1, 2, 3)',
                frame=Frame(Dimensions(9, 1)),
            ),
            text=MockPanelStage2(
                'Here\nis\nsome\ntext',
                frame=Frame(Dimensions(4, 3)),
            ),
        ),
    )

    draft_panel_half_rendered: DraftPanel[Layout, FrameWithWidthAndHeight] = DraftPanel(
        Layout(
            tuple=MockPanelStage2('(1,\n2,\n3)'),
            text1=MockPanel('Here is some text'),
            text2=MockPanel('Here is some other text'),
        ),
        frame=Frame(Dimensions(24, 5)),
        constraints=Constraints(container_width_per_line_limit=10),
        config=OutputConfig(indent_tab_size=1),
    )
    assert_next_stage_panel(
        this_panel=draft_panel_half_rendered,
        next_stage=draft_panel_half_rendered.render_next_stage(),
        next_stage_panel_cls=ResizedLayoutDraftPanel,
        exp_content=Layout(
            tuple=MockPanelStage2('(1,\n2,\n3)'),
            text1=MockPanelStage2(
                'Here\nis\nsome\ntext',
                frame=Frame(Dimensions(4, 3)),
            ),
            text2=MockPanelStage2(
                'Here is\nsome\nother\ntext',
                frame=Frame(Dimensions(7, 3)),
            ),
        ),
    )
