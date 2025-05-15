from typing import Annotated

import pytest_cases as pc

from omnipy.data._display.config import HorizontalOverflowMode, OutputConfig
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


@pc.parametrize(
    'frame_case',
    (
        FrameTestCase(frame=None),
        FrameTestCase(frame=Frame(Dimensions(width=4, height=1), fixed_width=False)),
        FrameTestCase(
            frame=Frame(Dimensions(width=3, height=1), fixed_width=False),
            exp_plain_output='北…\n',
            exp_dims_all_stages=Dimensions(width=3, height=1),
        ),
        FrameTestCase(
            frame=Frame(Dimensions(width=3, height=1)),
            exp_plain_output='北…\n',
            # The frame is fixed width, so the cropping logic for
            # double-width characters is not applied in the "reflowing"
            # stage. Hence, the width is not reduced until the "styling"
            # stage.
            exp_stylized_dims=Dimensions(width=3, height=1),
        ),
        FrameTestCase(
            frame=Frame(Dimensions(width=3, height=1), fixed_width=False),
            config=OutputConfig(horizontal_overflow_mode=HorizontalOverflowMode.CROP),
            exp_plain_output='北\n',
            exp_dims_all_stages=Dimensions(width=2, height=1),
        ),
        FrameTestCase(
            frame=Frame(Dimensions(width=3, height=1)),
            config=OutputConfig(horizontal_overflow_mode=HorizontalOverflowMode.CROP),
            exp_plain_output='北 \n',
            # The frame is fixed width, so the cropping logic for
            # double-width characters is not applied in the "reflowing"
            # stage. The rich library adds a space at the end in the
            # "styling" stage to ensure exact text width.
            exp_stylized_dims=Dimensions(width=3, height=1),
        ),
        FrameTestCase(
            frame=Frame(Dimensions(width=2, height=1), fixed_width=False),
            exp_plain_output='…\n',
            exp_dims_all_stages=Dimensions(width=1, height=1),
        ),
        FrameTestCase(
            frame=Frame(Dimensions(width=2, height=1)),
            exp_plain_output=' …\n',
            # The frame is fixed width, so the cropping logic for
            # double-width characters is not applied in the "reflowing"
            # stage. The rich library adds a space at the beginning in the
            # "styling" stage to ensure exact text width.
            exp_stylized_dims=Dimensions(width=2, height=1),
        ),
        FrameTestCase(
            frame=Frame(Dimensions(width=2, height=1), fixed_width=False),
            config=OutputConfig(horizontal_overflow_mode=HorizontalOverflowMode.CROP),
            exp_plain_output='北\n',
            exp_dims_all_stages=Dimensions(width=2, height=1),
        ),
        FrameTestCase(
            frame=Frame(Dimensions(width=2, height=1)),
            config=OutputConfig(horizontal_overflow_mode=HorizontalOverflowMode.CROP),
            exp_plain_output='北\n',
            # The frame is fixed width, so the cropping logic for
            # double-width characters is not applied in the "reflowing"
            # stage. Hence, the width is not reduced until the "styling"
            # stage.
            exp_stylized_dims=Dimensions(width=2, height=1),
        ),
        FrameTestCase(
            frame=Frame(Dimensions(width=1, height=1), fixed_width=False),
            exp_plain_output='…\n',
            exp_dims_all_stages=Dimensions(width=1, height=1),
        ),
        FrameTestCase(
            frame=Frame(Dimensions(width=1, height=1)),
            exp_plain_output='…\n',
            # The frame is fixed width, so the cropping logic for
            # double-width characters is not applied in the "reflowing"
            # stage. Hence, the width is not reduced until the "styling"
            # stage.
            exp_stylized_dims=Dimensions(width=1, height=1),
        ),
        FrameTestCase(
            frame=Frame(Dimensions(width=1, height=1), fixed_width=False),
            config=OutputConfig(horizontal_overflow_mode=HorizontalOverflowMode.CROP),
            exp_plain_output='\n',
            exp_dims_all_stages=Dimensions(width=0, height=1),
        ),
        FrameTestCase(
            frame=Frame(Dimensions(width=1, height=1)),
            config=OutputConfig(horizontal_overflow_mode=HorizontalOverflowMode.CROP),
            exp_plain_output=' \n',
            # The frame is fixed width, so the cropping logic for
            # double-width characters is not applied in the "reflowing"
            # stage. The rich library adds a space at the end in the
            # "styling" stage to ensure exact text width.
            exp_stylized_dims=Dimensions(width=1, height=1),
        ),
        FrameTestCase(
            frame=Frame(Dimensions(width=0, height=1), fixed_width=False),
            config=OutputConfig(horizontal_overflow_mode=HorizontalOverflowMode.CROP),
            exp_plain_output='\n',
            # Frame width is zero, which shortcuts the cropping logic for
            # double-width characters in the "reflowing" stage. Hence, the
            # width is not reduced until the "styling" stage.
            exp_stylized_dims=Dimensions(width=0, height=1),
        ),
        FrameTestCase(
            frame=Frame(Dimensions(width=0, height=1)),
            config=OutputConfig(horizontal_overflow_mode=HorizontalOverflowMode.CROP),
            exp_plain_output='\n',
            # Frame width is both zero and fixed. Both shortcuts the
            # cropping logic for double-width characters in the "reflowing"
            # stage. Hence, the width is not reduced until the "styling"
            # stage.
            exp_stylized_dims=Dimensions(width=0, height=1),
        ),
    ),
    ids=(
        'no_frame',
        'exact_frame',
        'smaller_odd_width_frame_ellipsis',
        'smaller_odd_width_fixed_frame_ellipsis',
        'smaller_odd_width_frame_crop',
        'smaller_odd_width_fixed_frame_crop',
        'smaller_even_width_frame_ellipsis',
        'smaller_even_width_fixed_frame_ellipsis',
        'smaller_even_width_frame_crop',
        'smaller_even_width_fixed_frame_crop',
        'single_width_frame_ellipsis',
        'single_width_fixed_frame_ellipsis',
        'single_width_frame_crop',
        'single_width_fixed_frame_crop',
        'no_width_frame_ellipsis',
        'no_width_fixed_frame_ellipsis',
    ),
)
@pc.case(id='double_width_chars', tags=['dims_and_edge_cases', 'syntax_text'])
def case_syntax_text_double_width_chars(
    frame_case: FrameTestCase[FrameWithWidthAndHeight],
    per_frame_variant: Annotated[FrameVariant, pc.fixture],
) -> PanelFrameVariantTestCase[str]:
    return PanelFrameVariantTestCase(
        # Mandarin Chinese characters are double-width
        content='北京',
        frame=frame_case.frame,
        exp_plain_output_no_frame='北京\n',
        exp_dims_all_stages_no_frame=Dimensions(width=4, height=1),
        exp_plain_output_only_height='北京\n',
        exp_dims_all_stages_only_height=Dimensions(width=4, height=1),
        frame_case=frame_case,
        frame_variant=per_frame_variant,
    )


@pc.parametrize(
    'frame_case',
    (
        FrameTestCase(frame=None),
        FrameTestCase(frame=Frame(Dimensions(width=5, height=1), fixed_width=False)),
        FrameTestCase(
            frame=Frame(Dimensions(width=4, height=1), fixed_width=False),
            exp_plain_output=' a…\n',
            exp_dims_all_stages=Dimensions(width=3, height=1),
        ),
        FrameTestCase(
            frame=Frame(Dimensions(width=4, height=1)),
            exp_plain_output=' a …\n',
            # The frame is fixed width, so the cropping logic for
            # tab characters is not applied in the "reflowing" stage.
            # The rich library adds a space before the ellipsis in the
            # "styling" stage to ensure exact text width.
            exp_stylized_dims=Dimensions(width=4, height=1),
        ),
        FrameTestCase(
            frame=Frame(Dimensions(width=4, height=1), fixed_width=False),
            config=OutputConfig(tab_size=3),
            exp_plain_output=' a b\n',
            # No cropping needed
            exp_dims_all_stages=Dimensions(width=4, height=1),
            exp_plain_output_only_height=' a b\n',
            exp_dims_all_stages_only_height=Dimensions(width=4, height=1),
        ),
        FrameTestCase(
            frame=Frame(Dimensions(width=4, height=1)),
            config=OutputConfig(tab_size=3),
            exp_plain_output=' a b\n',
            # No cropping needed
            exp_dims_all_stages=Dimensions(width=4, height=1),
            exp_plain_output_only_height=' a b\n',
            exp_dims_all_stages_only_height=Dimensions(width=4, height=1),
        ),
        FrameTestCase(
            frame=Frame(Dimensions(width=4, height=1), fixed_width=False),
            config=OutputConfig(horizontal_overflow_mode=HorizontalOverflowMode.CROP),
            exp_plain_output=' a\n',
            exp_dims_all_stages=Dimensions(width=2, height=1),
        ),
        FrameTestCase(
            frame=Frame(Dimensions(width=4, height=1)),
            config=OutputConfig(horizontal_overflow_mode=HorizontalOverflowMode.CROP),
            exp_plain_output=' a  \n',
            # The frame is fixed width, so the cropping logic for
            # tab characters is not applied in the "reflowing" stage.
            # The rich library adds whitespace in the "styling" stage to
            # ensure exact text width.
            exp_stylized_dims=Dimensions(width=4, height=1),
        ),
        FrameTestCase(
            frame=Frame(Dimensions(width=3, height=1), fixed_width=False),
            exp_plain_output=' a…\n',
            exp_dims_all_stages=Dimensions(width=3, height=1),
        ),
        FrameTestCase(
            frame=Frame(Dimensions(width=3, height=1)),
            exp_plain_output=' a…\n',
            # The frame is fixed width, so the cropping logic for
            # tab characters is not applied in the "reflowing" stage.
            # Hence, the width is not reduced until the "styling" stage.
            exp_stylized_dims=Dimensions(width=3, height=1),
        ),
        FrameTestCase(
            frame=Frame(Dimensions(width=3, height=1), fixed_width=False),
            config=OutputConfig(horizontal_overflow_mode=HorizontalOverflowMode.CROP),
            exp_plain_output=' a\n',
            exp_dims_all_stages=Dimensions(width=2, height=1),
        ),
        FrameTestCase(
            frame=Frame(Dimensions(width=3, height=1)),
            config=OutputConfig(horizontal_overflow_mode=HorizontalOverflowMode.CROP),
            exp_plain_output=' a \n',
            # The frame is fixed width, so the cropping logic for
            # tab characters is not applied in the "reflowing" stage.
            # The rich library adds whitespace in the "styling" stage to
            # ensure exact text width.
            exp_stylized_dims=Dimensions(width=3, height=1),
        ),
        FrameTestCase(
            frame=Frame(Dimensions(width=2, height=1), fixed_width=False),
            exp_plain_output=' …\n',
            # The space in the beginning is part of the content, hence it
            # is not removed.
            exp_dims_all_stages=Dimensions(width=2, height=1),
        ),
        FrameTestCase(
            frame=Frame(Dimensions(width=2, height=1)),
            exp_plain_output=' …\n',
            # The frame is fixed width, so the cropping logic for
            # tab characters is not applied in the "reflowing" stage.
            # Hence, the width is not reduced until the "styling" stage.
            exp_stylized_dims=Dimensions(width=2, height=1),
        ),
        FrameTestCase(
            frame=Frame(Dimensions(width=2, height=1), fixed_width=False),
            config=OutputConfig(horizontal_overflow_mode=HorizontalOverflowMode.CROP),
            exp_plain_output=' a\n',
            exp_dims_all_stages=Dimensions(width=2, height=1),
        ),
        FrameTestCase(
            frame=Frame(Dimensions(width=2, height=1)),
            config=OutputConfig(horizontal_overflow_mode=HorizontalOverflowMode.CROP),
            exp_plain_output=' a\n',
            # The frame is fixed width, so the cropping logic for
            # tab characters is not applied in the "reflowing" stage.
            # Hence, the width is not reduced until the "styling" stage.
            exp_stylized_dims=Dimensions(width=2, height=1),
        ),
        FrameTestCase(
            frame=Frame(Dimensions(width=0, height=1), fixed_width=False),
            config=OutputConfig(horizontal_overflow_mode=HorizontalOverflowMode.CROP),
            exp_plain_output='\n',
            # Frame width is zero, which shortcuts the cropping logic for
            # tab characters in the "reflowing" stage. Hence, the width is
            # not reduced until the "styling" stage.
            exp_stylized_dims=Dimensions(width=0, height=1),
        ),
        FrameTestCase(
            frame=Frame(Dimensions(width=0, height=1)),
            config=OutputConfig(horizontal_overflow_mode=HorizontalOverflowMode.CROP),
            exp_plain_output='\n',
            # Frame width is both zero and fixed. Both shortcuts the
            # cropping logic for tab characters in the "reflowing" stage.
            # Hence, the width is not reduced until the "styling" stage.
            exp_stylized_dims=Dimensions(width=0, height=1),
        ),
    ),
    ids=(
        'no_frame',
        'exact_frame',
        'smaller_even_width_frame_ellipsis',
        'smaller_even_width_fixed_frame_ellipsis',
        'smaller_even_width_frame_ellipsis_tab_size_3',
        'smaller_even_width_fixed_frame_ellipsis_tab_size_3',
        'smaller_even_width_frame_crop',
        'smaller_even_width_fixed_frame_crop',
        'smaller_odd_width_frame_ellipsis',
        'smaller_odd_width_fixed_frame_ellipsis',
        'smaller_odd_width_frame_crop',
        'smaller_odd_width_fixed_frame_crop',
        'width_two_frame_ellipsis',
        'width_two_fixed_frame_ellipsis',
        'width_two_frame_crop',
        'width_two_fixed_frame_crop',
        'no_width_frame_ellipsis',
        'no_width_fixed_frame_ellipsis',
    ),
)
@pc.case(id='tab_char', tags=['dims_and_edge_cases', 'syntax_text'])
def case_syntax_text_tab_char(
    frame_case: FrameTestCase[FrameWithWidthAndHeight],
    per_frame_variant: Annotated[FrameVariant, pc.fixture],
) -> PanelFrameVariantTestCase[str]:
    return PanelFrameVariantTestCase(
        # Tab character width depends on context, filling the spaces until
        # the next tab stop (4 chars by default)
        content=' a\tb',
        frame=frame_case.frame,
        exp_plain_output_no_frame=' a  b\n',
        exp_dims_all_stages_no_frame=Dimensions(width=5, height=1),
        exp_plain_output_only_height=' a  b\n',
        exp_dims_all_stages_only_height=Dimensions(width=5, height=1),
        frame_case=frame_case,
        frame_variant=per_frame_variant,
    )
