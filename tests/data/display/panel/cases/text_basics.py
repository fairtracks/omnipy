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
            exp_plain_output='',
            exp_stylized_dims=Dimensions(width=0, height=0),
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
        exp_plain_output_no_frame='\n',
        exp_dims_all_stages_no_frame=Dimensions(width=0, height=1),
        exp_plain_output_only_width='\n',
        exp_dims_all_stages_only_width=Dimensions(width=0, height=1),
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
            exp_plain_output=' \n',
            exp_stylized_dims=Dimensions(width=1, height=1),
            exp_plain_output_only_width=' \n \n',
            exp_stylized_dims_only_width=Dimensions(width=1, height=2),
            exp_plain_output_only_height='  \n',
            exp_stylized_dims_only_height=Dimensions(width=2, height=1),
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
        exp_plain_output_no_frame='  \n  \n',
        exp_dims_all_stages_no_frame=Dimensions(width=2, height=2),
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
            exp_plain_output='\n\n',
            exp_stylized_dims=Dimensions(width=0, height=2),
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
        exp_plain_output_no_frame='\n\n\n',
        exp_dims_all_stages_no_frame=Dimensions(width=0, height=3),
        exp_plain_output_only_width='\n\n\n',
        exp_stylized_dims_only_width=Dimensions(width=0, height=3),
        frame_case=frame_case,
        frame_variant=per_frame_variant,
    )


@pc.parametrize(
    'frame_case',
    (
        FrameTestCase(frame=None),
        FrameTestCase(frame=Frame(Dimensions(width=14, height=5))),
        FrameTestCase(frame=Frame(Dimensions(width=13, height=4))),
        FrameTestCase(
            frame=Frame(Dimensions(width=13, height=3)),
            exp_plain_output='I scream,\nyou scream,\nwe all scream\n',
            # As normal, cropping with fixed frame dimensions only happens
            # at the "styling" stage
            exp_stylized_dims=Dimensions(width=13, height=3),
            exp_stylized_dims_only_height=Dimensions(width=13, height=3),
        ),
        FrameTestCase(
            frame=Frame(Dimensions(width=13, height=3), fixed_width=False),
            exp_plain_output='I scream,\nyou scream,\nwe all scream\n',
            # The width of the frame is defined as flexible and there is
            # a reduction in height, so the bottom line is cropped away
            # already in the "resizing" stage, to allow for auto-reduction
            # of the width (and possible adjustment of other panels).
            # However, since the two last lines in this case are equally
            # long, no adjustment of width is carried out.
            exp_dims_all_stages=Dimensions(width=13, height=3),
            # Width should not be auto-adjusted to fit the content at the
            # "resize" stage if the frame does not define the width.
            exp_resized_dims_only_height=Dimensions(width=13, height=4),
            # With only height, the cropping of the height of the frame
            # happens at the "styling" stage, as normal.
            exp_stylized_dims_only_height=Dimensions(width=13, height=3),
        ),
        FrameTestCase(
            frame=Frame(Dimensions(width=13, height=2), fixed_width=False),
            exp_plain_output='I scream,\nyou scream,\n',
            # Only the first two lines fit. Since the frame is wider than
            # the required width of the content and the width of the frame
            # is flexible (not fixed) the dimensions are reduced to the
            # content width at the "resizing" stage.
            exp_dims_all_stages=Dimensions(width=11, height=2),
            # Width should not be auto-adjusted to fit the content at the
            # "resize" stage if the frame does not define the width.
            exp_resized_dims_only_height=Dimensions(width=13, height=4),
            # With only height, the cropping of the height of the frame
            # happens at the "styling" stage, as normal.
            exp_stylized_dims_only_height=Dimensions(width=11, height=2),
        ),
    ),
    ids=(
        'no_frame',
        'larger_frame',
        'exact_frame',
        'crop_height_fixed_width',
        'crop_height_flexible_width_same',
        'crop_height_flexible_width_thinner',
    ),
)
@pc.case(id='simple_text', tags=['dims_and_edge_cases', 'syntax_text'])
def case_syntax_text_simple_text(
    frame_case: FrameTestCase[FrameWithWidthAndHeight],
    per_frame_variant: Annotated[FrameVariant, pc.fixture],
) -> PanelFrameVariantTestCase[str]:
    return PanelFrameVariantTestCase(
        content='I scream,\nyou scream,\nwe all scream\nfor ice cream',
        frame=frame_case.frame,
        config=None,
        exp_plain_output_no_frame='I scream,\nyou scream,\nwe all scream\nfor ice cream\n',
        exp_dims_all_stages_no_frame=Dimensions(width=13, height=4),
        exp_plain_output_only_width='I scream,\nyou scream,\nwe all scream\nfor ice cream\n',
        exp_dims_all_stages_only_width=Dimensions(width=13, height=4),
        frame_case=frame_case,
        frame_variant=per_frame_variant,
    )
