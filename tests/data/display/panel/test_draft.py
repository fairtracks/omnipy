import pytest

from omnipy.data._display.config import OutputConfig
from omnipy.data._display.constraints import Constraints
from omnipy.data._display.dimensions import Dimensions
from omnipy.data._display.frame import (AnyFrame,
                                        empty_frame,
                                        Frame,
                                        FrameWithWidthAndHeight,
                                        UndefinedFrame)
from omnipy.data._display.layout.base import Layout
from omnipy.data._display.panel.draft.base import DraftPanel
from omnipy.data._display.panel.draft.layout import ResizedLayoutDraftPanel
from omnipy.data._display.panel.draft.text import ReflowedTextDraftPanel

from .helpers.mocks import MockResizedStylablePlainCropPanel, MockStylablePlainCropPanel
from .helpers.panel_assert import assert_draft_panel_subcls, assert_next_stage_panel


def test_draft_panel_init() -> None:
    assert_draft_panel_subcls(DraftPanel, 'Some text')
    assert_draft_panel_subcls(
        DraftPanel, (1, 2, 3), title='UnboundPanel', frame=Frame(Dimensions(None, None)))
    assert_draft_panel_subcls(
        DraftPanel, (1, 2, 3), title='WidthBoundPanel', frame=Frame(Dimensions(10, None)))
    assert_draft_panel_subcls(
        DraftPanel, (1, 2, 3), title='HeightBoundPanel', frame=Frame(Dimensions(None, 20)))
    assert_draft_panel_subcls(
        DraftPanel, (1, 2, 3), title='BoundPanel', frame=Frame(Dimensions(10, 20)))
    assert_draft_panel_subcls(
        DraftPanel, None, title='NonePanel', config=OutputConfig(indent_tab_size=4))

    content = ('a', 'b', (1, 2, 3))
    assert_draft_panel_subcls(
        DraftPanel,
        content,
        constraints=Constraints(container_width_per_line_limit=10),
    )
    assert_draft_panel_subcls(
        DraftPanel,
        content,
        title='AllPanel',
        frame=Frame(Dimensions(20, 10)),
        constraints=Constraints(container_width_per_line_limit=10),
        config=OutputConfig(indent_tab_size=4),
    )


def test_draft_panel_hashable() -> None:
    panel_1 = DraftPanel('')
    panel_2 = DraftPanel('')

    assert hash(panel_1) == hash(panel_2)

    panel_3 = DraftPanel('Some text')
    panel_4 = DraftPanel('', title='My panel')
    panel_5 = DraftPanel('', frame=Frame(Dimensions(10, 20)))
    panel_6 = DraftPanel('', constraints=Constraints(container_width_per_line_limit=10))
    panel_7 = DraftPanel('', config=OutputConfig(indent_tab_size=4))

    assert hash(panel_1) != hash(panel_3) != hash(panel_4) != hash(panel_5) \
           != hash(panel_6) != hash(panel_7)

    panel_8 = DraftPanel('Some text')
    panel_9 = DraftPanel('', title='My panel')
    panel_10 = DraftPanel('', frame=Frame(Dimensions(10, 20)))
    panel_11 = DraftPanel('', constraints=Constraints(container_width_per_line_limit=10))
    panel_12 = DraftPanel('', config=OutputConfig(indent_tab_size=4))

    assert hash(panel_3) == hash(panel_8)
    assert hash(panel_4) == hash(panel_9)
    assert hash(panel_5) == hash(panel_10)
    assert hash(panel_6) == hash(panel_11)
    assert hash(panel_7) == hash(panel_12)


def test_draft_panel_mutable_not_hashable() -> None:
    # Test with mutable content
    mutable_content = [1, 2, 3]
    draft_panel = DraftPanel(mutable_content)

    with pytest.raises(TypeError):
        hash(draft_panel)  # Ensure hash is computed


# noinspection PyDataclass
def test_fail_draft_panel_no_assignments() -> None:
    draft_panel = DraftPanel('Some text')

    with pytest.raises(AttributeError):
        draft_panel.content = [1, 2, 3]  # type: ignore[misc, assignment]

    with pytest.raises(AttributeError):
        draft_panel.title = 'Some title'  # type: ignore[misc]

    with pytest.raises(AttributeError):
        draft_panel.frame = Frame(Dimensions(10, 20))  # type: ignore[misc]

    with pytest.raises(AttributeError):
        draft_panel.constraints = Constraints(  # type: ignore[misc]
            container_width_per_line_limit=10)

    with pytest.raises(AttributeError):
        draft_panel.config = OutputConfig(indent_tab_size=4)  # type: ignore[misc]


def test_draft_panel_constraints_satisfaction() -> None:

    draft_panel = DraftPanel('Some text')
    assert draft_panel.satisfies.container_width_per_line_limit is None

    draft_panel = DraftPanel(
        'Some text', constraints=Constraints(container_width_per_line_limit=10))
    assert draft_panel.satisfies.container_width_per_line_limit is False


def test_draft_panel_with_empty_content() -> None:

    # Test with empty string
    empty_string_draft_panel = DraftPanel('')

    assert empty_string_draft_panel.content == ''
    assert empty_string_draft_panel.title == ''
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

    # Test with empty content and frame with fixed dimensions
    framed_empty_draft_panel = DraftPanel('', frame=Frame(Dimensions(10, 5)))

    assert framed_empty_draft_panel.frame.dims.width == 10
    assert framed_empty_draft_panel.frame.dims.height == 5
    assert framed_empty_draft_panel.content == ''


def test_draft_panel_render_next_stage_with_repr_simple() -> None:
    draft_panel = DraftPanel('Some text')
    assert_next_stage_panel(
        this_panel=draft_panel,
        next_stage=draft_panel.render_next_stage(),
        next_stage_panel_cls=ReflowedTextDraftPanel,
        exp_content="'Some text'",
    )


def test_draft_panel_render_next_stage_with_repr_complex() -> None:
    draft_panel_complex = DraftPanel(
        (1, 2, 3),
        title='My text panel',
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


def test_draft_panel_render_next_stage_with_layout_simple() -> None:
    draft_panel: DraftPanel[Layout, AnyFrame] = DraftPanel(Layout())
    assert_next_stage_panel(
        this_panel=draft_panel,
        next_stage=draft_panel.render_next_stage(),
        next_stage_panel_cls=ResizedLayoutDraftPanel,
        exp_content=Layout(),
    )


def test_draft_panel_render_next_stage_with_layout_complex() -> None:
    draft_panel_complex: DraftPanel[Layout, FrameWithWidthAndHeight] = DraftPanel(
        Layout(
            tuple=MockStylablePlainCropPanel('(1, 2, 3)', title='Tuple panel'),
            text=MockStylablePlainCropPanel('Here is some text', title='Text panel'),
        ),
        title='My layout panel',
        frame=Frame(Dimensions(21, 5)),
        constraints=Constraints(container_width_per_line_limit=10),
        config=OutputConfig(indent_tab_size=1),
    )
    assert_next_stage_panel(
        this_panel=draft_panel_complex,
        next_stage=draft_panel_complex.render_next_stage(),
        next_stage_panel_cls=ResizedLayoutDraftPanel,
        exp_content=Layout(
            tuple=MockResizedStylablePlainCropPanel(
                '(1, 2,\n3)',
                title='Tuple panel',
                frame=Frame(
                    Dimensions(6, 2),
                    fixed_width=False,
                    fixed_height=False,
                ),
            ),
            text=MockResizedStylablePlainCropPanel(
                'Here is\nsome\ntext',
                title='Text panel',
                frame=Frame(
                    Dimensions(8, 3),
                    fixed_width=False,
                    fixed_height=False,
                ),
            ),
        ),
    )


def test_draft_panel_render_next_stage_with_layout_half_framed() -> None:
    draft_panel_half_framed: DraftPanel[Layout, FrameWithWidthAndHeight] = DraftPanel(
        Layout(
            tuple=MockStylablePlainCropPanel(
                '(1, 2, 3)',
                title='Framed tuple panel',
                frame=Frame(Dimensions(9, 1)),
            ),
            text=MockStylablePlainCropPanel(
                'Here is some text',
                title='Text panel',
            ),
        ),
        frame=Frame(Dimensions(20, 5)),
        constraints=Constraints(container_width_per_line_limit=10),
        config=OutputConfig(indent_tab_size=1),
    )
    assert_next_stage_panel(
        this_panel=draft_panel_half_framed,
        next_stage=draft_panel_half_framed.render_next_stage(),
        next_stage_panel_cls=ResizedLayoutDraftPanel,
        exp_content=Layout(
            tuple=MockResizedStylablePlainCropPanel(
                '(1, 2, 3)',
                title='Framed tuple panel',
                frame=Frame(Dimensions(9, 1)),
            ),
            text=MockResizedStylablePlainCropPanel(
                'Here\nis\nsome\ntext',
                title='Text panel',
                frame=Frame(
                    Dimensions(4, 3),
                    fixed_width=False,
                    fixed_height=False,
                ),
            ),
        ),
    )


def test_draft_panel_render_next_stage_with_layout_half_rendered() -> None:
    draft_panel_half_rendered: DraftPanel[Layout, FrameWithWidthAndHeight] = DraftPanel(
        Layout(
            tuple=MockResizedStylablePlainCropPanel('(1,\n2,\n3)', title='Stage 2 tuple panel'),
            text1=MockStylablePlainCropPanel('Here is some text', title='Text panel 1'),
            text2=MockStylablePlainCropPanel('Here is some other text', title='Text panel 2'),
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
            tuple=MockResizedStylablePlainCropPanel(
                '(1,\n2,\n3)',
                title='Stage 2 tuple panel',
                frame=Frame(
                    Dimensions(None, 3),
                    fixed_width=False,
                    fixed_height=False,
                ),
            ),
            text1=MockResizedStylablePlainCropPanel(
                'Here\nis\nsome\ntext',
                title='Text panel 1',
                frame=Frame(
                    Dimensions(4, 3),
                    fixed_width=False,
                    fixed_height=False,
                ),
            ),
            text2=MockResizedStylablePlainCropPanel(
                'Here is\nsome\nother\ntext',
                title='Text panel 2',
                frame=Frame(
                    Dimensions(7, 3),
                    fixed_width=False,
                    fixed_height=False,
                ),
            ),
        ),
    )
