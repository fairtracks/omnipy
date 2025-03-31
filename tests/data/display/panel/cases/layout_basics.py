from typing import Annotated

import pytest_cases as pc

from omnipy.data._display.config import HorizontalOverflowMode, OutputConfig, VerticalOverflowMode
from omnipy.data._display.dimensions import Dimensions
from omnipy.data._display.frame import Frame, FrameWithWidthAndHeight
from omnipy.data._display.layout import Layout

from ...helpers.classes import MockPanel
from ..helpers import FrameVariant, PanelOutputFrameVariantTestCase, WithinFrameExp


@pc.parametrize(
    'frame, exp_within_frame',
    (
        (None, WithinFrameExp(width=None, height=None)),
        (Frame(Dimensions(width=0, height=0)), WithinFrameExp(width=True, height=False)),
        (Frame(Dimensions(width=0, height=1)), WithinFrameExp(width=True, height=True)),
        (Frame(Dimensions(width=5, height=5)), WithinFrameExp(width=True, height=True)),
    ),
    ids=('no_frame', 'smaller_frame', 'exact_frame', 'larger_frame'))
@pc.case(id='no_panels', tags=['dimensions', 'layout'])
def case_layout_no_panels(
    frame: FrameWithWidthAndHeight | None,
    exp_within_frame: WithinFrameExp,
    per_frame_variant: Annotated[FrameVariant, pc.fixture],
) -> PanelOutputFrameVariantTestCase[Layout]:
    return PanelOutputFrameVariantTestCase(
        content=Layout(),
        frame=frame,
        config=OutputConfig(horizontal_overflow_mode=HorizontalOverflowMode.CROP),
        exp_output='\n',
        exp_dims=Dimensions(width=0, height=1),
        cropping_frame_exp_output='',
        cropping_frame_exp_dims=Dimensions(width=0, height=0),
        cropping_frame_exp_within_frame=WithinFrameExp(width=True, height=True),
        exp_within_frame=exp_within_frame,
        frame_variant=per_frame_variant,
    )


@pc.parametrize(
    'frame, exp_within_frame',
    (
        (None, WithinFrameExp(width=None, height=None)),
        (Frame(Dimensions(width=3, height=2)), WithinFrameExp(width=False, height=False)),
        (Frame(Dimensions(width=4, height=3)), WithinFrameExp(width=True, height=True)),
        (Frame(Dimensions(width=5, height=4)), WithinFrameExp(width=True, height=True)),
    ),
    ids=('no_frame', 'smaller_frame', 'exact_frame', 'larger_frame'))
@pc.case(id='single_empty_panel', tags=['dimensions', 'layout'])
def case_layout_single_empty_panel(
    frame: FrameWithWidthAndHeight | None,
    exp_within_frame: WithinFrameExp,
    per_frame_variant: Annotated[FrameVariant, pc.fixture],
) -> PanelOutputFrameVariantTestCase[Layout]:
    return PanelOutputFrameVariantTestCase(
        content=Layout(empty=MockPanel('')),
        frame=frame,
        config=OutputConfig(horizontal_overflow_mode=HorizontalOverflowMode.CROP),
        exp_output=('╭──╮\n'
                    '│  │\n'
                    '╰──╯\n'),
        exp_dims=Dimensions(width=4, height=3),
        exp_within_frame=exp_within_frame,
        cropping_frame_exp_output=('╭─╮\n'
                                   '│ │\n'),
        cropping_frame_exp_dims=Dimensions(width=3, height=2),
        cropping_frame_exp_within_frame=WithinFrameExp(width=True, height=True),
        frame_variant=per_frame_variant,
    )


@pc.parametrize(
    'frame, exp_within_frame',
    (
        (None, WithinFrameExp(width=None, height=None)),
        (Frame(Dimensions(width=10, height=3)), WithinFrameExp(width=False, height=False)),
        (Frame(Dimensions(width=11, height=4)), WithinFrameExp(width=True, height=True)),
        (Frame(Dimensions(width=12, height=5)), WithinFrameExp(width=True, height=True)),
    ),
    ids=('no_frame', 'smaller_frame', 'exact_frame', 'larger_frame'))
@pc.case(id='single_panel', tags=['dimensions', 'layout'])
def case_layout_single_panel(
    frame: FrameWithWidthAndHeight | None,
    exp_within_frame: WithinFrameExp,
    per_frame_variant: Annotated[FrameVariant, pc.fixture],
) -> PanelOutputFrameVariantTestCase[Layout]:
    return PanelOutputFrameVariantTestCase(
        content=Layout(panel=MockPanel(content='Some content')),
        frame=frame,
        # Horizontal overflow modes are ignored within a table, due to Rich
        config=OutputConfig(horizontal_overflow_mode=HorizontalOverflowMode.WORD_WRAP),
        exp_output=('╭─────────╮\n'
                    '│ Some    │\n'
                    '│ content │\n'
                    '╰─────────╯\n'),
        exp_dims=Dimensions(width=11, height=4),
        exp_within_frame=exp_within_frame,
        cropping_frame_exp_output=('╭────────╮\n'
                                   '│ Some   │\n'
                                   '│ conte… │\n'),
        cropping_frame_exp_dims=Dimensions(width=10, height=3),
        cropping_frame_exp_within_frame=WithinFrameExp(width=True, height=True),
        frame_variant=per_frame_variant,
    )


@pc.parametrize(
    'frame, exp_within_frame',
    (
        (None, WithinFrameExp(width=None, height=None)),
        (Frame(Dimensions(width=13, height=4)), WithinFrameExp(width=False, height=False)),
        (Frame(Dimensions(width=14, height=5)), WithinFrameExp(width=True, height=True)),
        (Frame(Dimensions(width=15, height=6)), WithinFrameExp(width=True, height=True)),
    ),
    ids=('no_frame', 'smaller_frame', 'exact_frame', 'larger_frame'))
@pc.case(id='two_panels', tags=['dimensions', 'layout'])
def case_layout_two_panels(
    frame: FrameWithWidthAndHeight | None,
    exp_within_frame: WithinFrameExp,
    per_frame_variant: Annotated[FrameVariant, pc.fixture],
) -> PanelOutputFrameVariantTestCase[Layout]:
    return PanelOutputFrameVariantTestCase(
        content=Layout(
            first=MockPanel(content='Some text'),
            second=MockPanel(content='(1, 2, 3)'),
        ),
        frame=frame,
        config=OutputConfig(
            # Horizontal overflow modes are ignored within a table, due to Rich
            horizontal_overflow_mode=HorizontalOverflowMode.CROP,
            # However, vertical overflow modes are handled by Omnipy an honored
            vertical_overflow_mode=VerticalOverflowMode.CROP_TOP),
        exp_output=('╭──────┬─────╮\n'
                    '│ Some │ (1, │\n'
                    '│ text │ 2,  │\n'
                    '│      │ 3)  │\n'
                    '╰──────┴─────╯\n'),
        exp_dims=Dimensions(width=14, height=5),
        exp_within_frame=exp_within_frame,
        cropping_frame_exp_output=('│ So… │ (1, │\n'
                                   '│ te… │ 2,  │\n'
                                   '│     │ 3)  │\n'
                                   '╰─────┴─────╯\n'),
        cropping_frame_exp_dims=Dimensions(width=13, height=4),
        cropping_frame_exp_within_frame=WithinFrameExp(width=True, height=True),
        frame_variant=per_frame_variant,
    )
