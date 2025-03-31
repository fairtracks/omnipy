from typing import Annotated

import pytest_cases as pc

from omnipy.data._display.dimensions import Dimensions
from omnipy.data._display.frame import Frame, FrameWithWidthAndHeight

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
@pc.case(id='empty', tags=['dimensions', 'syntax_text'])
def case_syntax_text_empty(
    frame: FrameWithWidthAndHeight | None,
    exp_within_frame: WithinFrameExp,
    per_frame_variant: Annotated[FrameVariant, pc.fixture],
) -> PanelOutputFrameVariantTestCase[str]:
    return PanelOutputFrameVariantTestCase(
        content='',
        frame=frame,
        config=None,
        exp_output='\n',
        exp_dims=Dimensions(width=0, height=1),
        exp_within_frame=exp_within_frame,
        cropping_frame_exp_output='',
        cropping_frame_exp_dims=Dimensions(width=0, height=0),
        cropping_frame_exp_within_frame=WithinFrameExp(width=True, height=True),
        frame_variant=per_frame_variant,
    )


@pc.parametrize(
    'frame, exp_within_frame',
    (
        (None, WithinFrameExp(width=None, height=None)),
        (Frame(Dimensions(width=1, height=1)), WithinFrameExp(width=False, height=False)),
        (Frame(Dimensions(width=2, height=2)), WithinFrameExp(width=True, height=True)),
        (Frame(Dimensions(width=5, height=5)), WithinFrameExp(width=True, height=True)),
    ),
    ids=('whitespace', 'smaller_frame', 'exact_frame', 'larger_frame'))
@pc.case(id='whitespace', tags=['dimensions', 'syntax_text'])
def case_syntax_text_whitespace(
    frame: FrameWithWidthAndHeight | None,
    exp_within_frame: WithinFrameExp,
    per_frame_variant: Annotated[FrameVariant, pc.fixture],
) -> PanelOutputFrameVariantTestCase[str]:
    return PanelOutputFrameVariantTestCase(
        content='  \n  ',
        frame=frame,
        config=None,
        exp_output='  \n  \n',
        exp_dims=Dimensions(width=2, height=2),
        exp_within_frame=exp_within_frame,
        cropping_frame_exp_output=' \n',
        cropping_frame_exp_dims=Dimensions(width=1, height=1),
        cropping_frame_exp_within_frame=WithinFrameExp(width=True, height=True),
        frame_variant=per_frame_variant,
    )


@pc.parametrize(
    'frame, exp_within_frame',
    (
        (None, WithinFrameExp(width=None, height=None)),
        (Frame(Dimensions(width=0, height=2)), WithinFrameExp(width=True, height=False)),
        (Frame(Dimensions(width=0, height=3)), WithinFrameExp(width=True, height=True)),
        (Frame(Dimensions(width=1, height=4)), WithinFrameExp(width=True, height=True)),
    ),
    ids=('no_frame', 'smaller_frame', 'exact_frame', 'larger_frame'))
@pc.case(id='empty_lines', tags=['dimensions', 'syntax_text'])
def case_syntax_text_empty_lines(
    frame: FrameWithWidthAndHeight | None,
    exp_within_frame: WithinFrameExp,
    per_frame_variant: Annotated[FrameVariant, pc.fixture],
) -> PanelOutputFrameVariantTestCase[str]:
    return PanelOutputFrameVariantTestCase(
        content='\n\n',
        frame=frame,
        config=None,
        exp_output='\n\n\n',
        exp_dims=Dimensions(width=0, height=3),
        exp_within_frame=exp_within_frame,
        cropping_frame_exp_output='\n\n',
        cropping_frame_exp_dims=Dimensions(width=0, height=2),
        cropping_frame_exp_within_frame=WithinFrameExp(width=True, height=True),
        frame_variant=per_frame_variant,
    )
