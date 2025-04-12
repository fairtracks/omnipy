from typing import Annotated

import pytest_cases as pc

from omnipy.data._display.dimensions import Dimensions
from omnipy.data._display.frame import Frame, FrameWithWidthAndHeight

from ..helpers import FrameTestCase, FrameVariant, PanelFrameVariantTestCase


@pc.parametrize(
    'frame_case',
    (
        FrameTestCase(frame=None),
        FrameTestCase(frame=Frame(Dimensions(width=5, height=5))),
        FrameTestCase(frame=Frame(Dimensions(width=0, height=1))),
        FrameTestCase(
            frame=Frame(Dimensions(width=0, height=0)),
            exp_output='',
            exp_stylized_dims=Dimensions(width=0, height=0),
            exp_output_only_width='\n',
        ),
    ),
    ids=('no_frame', 'larger_frame', 'exact_frame', 'smaller_frame'),
)
@pc.case(id='empty', tags=['dims_and_edge_cases', 'syntax_text'])
def case_syntax_text_empty(
    frame_case: FrameTestCase[FrameWithWidthAndHeight],
    per_frame_variant: Annotated[FrameVariant, pc.fixture],
) -> PanelFrameVariantTestCase[str]:
    return PanelFrameVariantTestCase(
        content='',
        frame=frame_case.frame,
        config=None,
        exp_output_no_frame='\n',
        exp_dims_no_frame=Dimensions(width=0, height=1),
        frame_case=frame_case,
        frame_variant=per_frame_variant,
    )


@pc.parametrize(
    'frame_case',
    (
        FrameTestCase(frame=None),
        FrameTestCase(frame=Frame(Dimensions(width=5, height=5))),
        FrameTestCase(frame=Frame(Dimensions(width=2, height=2))),
        FrameTestCase(
            frame=Frame(Dimensions(width=1, height=1)),
            exp_output=' \n',
            exp_stylized_dims=Dimensions(width=1, height=1),
            exp_output_only_width=' \n \n',
            exp_output_only_height='  \n',
        ),
    ),
    ids=('no_frame', 'larger_frame', 'exact_frame', 'smaller_frame'),
)
@pc.case(id='whitespace', tags=['dims_and_edge_cases', 'syntax_text'])
def case_syntax_text_whitespace(
    frame_case: FrameTestCase[FrameWithWidthAndHeight],
    per_frame_variant: Annotated[FrameVariant, pc.fixture],
) -> PanelFrameVariantTestCase[str]:
    return PanelFrameVariantTestCase(
        content='  \n  ',
        frame=frame_case.frame,
        config=None,
        exp_output_no_frame='  \n  \n',
        exp_dims_no_frame=Dimensions(width=2, height=2),
        frame_case=frame_case,
        frame_variant=per_frame_variant,
    )


@pc.parametrize(
    'frame_case',
    (
        FrameTestCase(frame=None),
        FrameTestCase(frame=Frame(Dimensions(width=1, height=4))),
        FrameTestCase(frame=Frame(Dimensions(width=0, height=3))),
        FrameTestCase(
            frame=Frame(Dimensions(width=0, height=2)),
            exp_output='\n\n',
            exp_stylized_dims=Dimensions(width=0, height=2),
            exp_output_only_width='\n\n\n',
        ),
    ),
    ids=('no_frame', 'larger_frame', 'exact_frame', 'smaller_frame'),
)
@pc.case(id='empty_lines', tags=['dims_and_edge_cases', 'syntax_text'])
def case_syntax_text_empty_lines(
    frame_case: FrameTestCase[FrameWithWidthAndHeight],
    per_frame_variant: Annotated[FrameVariant, pc.fixture],
) -> PanelFrameVariantTestCase[str]:
    return PanelFrameVariantTestCase(
        content='\n\n',
        frame=frame_case.frame,
        config=None,
        exp_output_no_frame='\n\n\n',
        exp_dims_no_frame=Dimensions(width=0, height=3),
        frame_case=frame_case,
        frame_variant=per_frame_variant,
    )
