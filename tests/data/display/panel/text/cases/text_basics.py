from typing import Annotated

import pytest_cases as pc

from omnipy.data._display.config import HorizontalOverflowMode, OutputConfig, VerticalOverflowMode
from omnipy.data._display.dimensions import Dimensions
from omnipy.data._display.frame import Frame, FrameWithWidthAndHeight

from ...helpers.case_setup import FrameTestCase, FrameVariant, PanelFrameVariantTestCase


@pc.parametrize(
    'frame_case',
    (
        #
        # id='no_frame'
        #
        FrameTestCase(frame=None),

        #
        # id='larger_frame'
        #
        FrameTestCase(frame=Frame(Dimensions(width=5, height=5))),

        #
        # id='exact_frame'
        #
        FrameTestCase(frame=Frame(Dimensions(width=0, height=1))),

        #
        # id='smaller_frame'
        #
        FrameTestCase(
            frame=Frame(Dimensions(width=0, height=0)),
            exp_plain_output='',
            exp_stylized_dims=Dimensions(width=0, height=0),
        ),
    ),
    ids=(
        'no_frame',
        'larger_frame',
        'exact_frame',
        'smaller_frame',
    ),
)
@pc.case(id='empty', tags=['dims_and_edge_cases', 'syntax_text'])
def case_syntax_text_empty(
    frame_case: FrameTestCase[str, FrameWithWidthAndHeight],
    per_frame_variant: Annotated[FrameVariant, pc.fixture],
) -> PanelFrameVariantTestCase[str]:
    return PanelFrameVariantTestCase(
        content='',
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
        #
        # id='no_frame'
        #
        FrameTestCase(frame=None),

        #
        # id='larger_frame'
        #
        FrameTestCase(frame=Frame(Dimensions(width=5, height=5))),

        #
        # id='exact_frame'
        #
        FrameTestCase(frame=Frame(Dimensions(width=2, height=2))),

        #
        # id='smaller_frame'
        #
        FrameTestCase(
            frame=Frame(Dimensions(width=1, height=1)),
            config=OutputConfig(vertical_overflow_mode=VerticalOverflowMode.CROP_BOTTOM),
            exp_plain_output=' \n',
            exp_stylized_dims=Dimensions(width=1, height=1),
            exp_plain_output_only_width=' \n \n',
            exp_stylized_dims_only_width=Dimensions(width=1, height=2),
            exp_plain_output_only_height='  \n',
            exp_stylized_dims_only_height=Dimensions(width=2, height=1),
        ),
    ),
    ids=(
        'no_frame',
        'larger_frame',
        'exact_frame',
        'smaller_frame',
    ),
)
@pc.case(id='whitespace', tags=['dims_and_edge_cases', 'syntax_text'])
def case_syntax_text_whitespace(
    frame_case: FrameTestCase[str, FrameWithWidthAndHeight],
    per_frame_variant: Annotated[FrameVariant, pc.fixture],
) -> PanelFrameVariantTestCase[str]:
    return PanelFrameVariantTestCase(
        content='  \n  ',
        config=None,
        exp_plain_output_no_frame='  \n  \n',
        exp_dims_all_stages_no_frame=Dimensions(width=2, height=2),
        frame_case=frame_case,
        frame_variant=per_frame_variant,
    )


@pc.parametrize(
    'frame_case',
    (
        #
        # id='no_frame'
        #
        FrameTestCase(frame=None),

        #
        # id='larger_frame'
        #
        FrameTestCase(frame=Frame(Dimensions(width=1, height=4))),

        #
        # id='exact_frame'
        #
        FrameTestCase(frame=Frame(Dimensions(width=0, height=3))),

        #
        # id='smaller_frame'
        #
        FrameTestCase(
            frame=Frame(Dimensions(width=0, height=2)),
            exp_plain_output='\n\n',
            exp_stylized_dims=Dimensions(width=0, height=2),
        ),
    ),
    ids=(
        'no_frame',
        'larger_frame',
        'exact_frame',
        'smaller_frame',
    ),
)
@pc.case(id='empty_lines', tags=['dims_and_edge_cases', 'syntax_text'])
def case_syntax_text_empty_lines(
    frame_case: FrameTestCase[str, FrameWithWidthAndHeight],
    per_frame_variant: Annotated[FrameVariant, pc.fixture],
) -> PanelFrameVariantTestCase[str]:
    return PanelFrameVariantTestCase(
        content='\n\n',
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
        #
        # id='no_frame'
        #
        FrameTestCase(frame=None),

        #
        # id='larger_frame'
        #
        FrameTestCase(frame=Frame(Dimensions(width=14, height=5))),

        #
        # id='exact_frame'
        #
        FrameTestCase(frame=Frame(Dimensions(width=13, height=4))),

        #
        # id='crop_height_flexible_width'
        #
        FrameTestCase(
            frame=Frame(Dimensions(width=13, height=3), fixed_width=False),
            exp_plain_output='I scream,\nyou scream,\n…\n',
            # The width of the frame is defined as flexible and there is
            # a reduction in height, so the bottom line is cropped away and
            # the second last line is reduced to an ellipsis. Both happens
            # in the "resized" stage. This is to allow for auto-reduction
            # of the width (and possible adjustment of other panels).
            exp_dims_all_stages=Dimensions(width=11, height=3),
        ),

        #
        # id='crop_height_fixed_width'
        #
        FrameTestCase(
            frame=Frame(Dimensions(width=13, height=3)),
            exp_plain_output='I scream,\nyou scream,\n…\n',
            # Compare with 'crop_height_flexible_width'. When the frame
            # width is fixed, the dimensions remain unchanged in the
            # "resize" stage as there is no space to be redistributed to
            # other panels.
            exp_resized_dims=Dimensions(width=13, height=4),
            # Vertical cropping instead only happens at the "styling"
            # stage.
            exp_stylized_dims=Dimensions(width=11, height=3),
        ),

        #
        # id='crop_height_and_width_flexible_width_ellipsis_bottom'
        #
        FrameTestCase(
            frame=Frame(Dimensions(width=9, height=3), fixed_width=False),
            exp_plain_output='I scream,\nyou scre…\n…\n',
            # Only types of cropping that has the potential to create extra
            # whitespace on the right side of the panel are considered in
            # the "resize" stage. Here, vertical cropping reduces width by
            # two as the two longest lines (bottom two) are removed.
            exp_resized_dims=Dimensions(width=11, height=3),
            # Simple Horizontal cropping happens in the "stylize" stage.
            exp_stylized_dims=Dimensions(width=9, height=3),
            # With only the frame width defined, no vertical cropping is
            # possible. Simple horizontal cropping happens in the "styling"
            # stage.
            exp_plain_output_only_width='I scream,\nyou scre…\nwe all s…\nfor ice …\n',
            exp_stylized_dims_only_width=Dimensions(width=9, height=4),
            # With only the frame height defined, no vertical cropping is
            # applied at the "resize" stage. This is because
            # `frame.width is None` entails that the panel is wide enough to
            # support the maximum width over all lines, also those out of
            # frame. Vertical cropping to an ellipsis character happens in
            # the "styling" stage.
            exp_plain_output_only_height='I scream,\nyou scream,\n…\n',
            exp_stylized_dims_only_height=Dimensions(width=11, height=3),
        ),

        #
        # id='crop_height_and_width_fixed_width_ellipsis_bottom'
        #
        FrameTestCase(
            frame=Frame(Dimensions(width=9, height=3)),
            exp_plain_output='I scream,\nyou scre…\n…\n',
            # Vertical cropping at the "resize" stage requires the frame
            # width to be flexible. Here, it is fixed.
            exp_resized_dims=Dimensions(width=13, height=4),
            # Content is instead cropped both vertically and horizontally
            # in the "stylize" stage.
            exp_stylized_dims=Dimensions(width=9, height=3),
            # "Only width" and "only height" cases are handled the same as
            # in the test case
            # "crop_height_and_width_flexible_width_ellipsis_bottom".
            exp_plain_output_only_width='I scream,\nyou scre…\nwe all s…\nfor ice …\n',
            exp_stylized_dims_only_width=Dimensions(width=9, height=4),
            exp_plain_output_only_height='I scream,\nyou scream,\n…\n',
            exp_stylized_dims_only_height=Dimensions(width=11, height=3),
        ),

        #
        # id='crop_height_and_width_flexible_width_ellipsis_top'
        #
        FrameTestCase(
            frame=Frame(Dimensions(width=9, height=3), fixed_width=False),
            config=OutputConfig(
                horizontal_overflow_mode=HorizontalOverflowMode.CROP,
                vertical_overflow_mode=VerticalOverflowMode.ELLIPSIS_TOP,
            ),
            exp_plain_output='…\nwe all sc\nfor ice c\n',
            # With vertical overflow mode set to ELLIPSIS_TOP and frame
            # width flexible, vertical cropping is still carried out in the
            # "resize" stage. However, cropping from top does not reduce the
            # width (the longest lines are the bottom two).
            exp_resized_dims=Dimensions(width=13, height=3),
            # Simple horizontal cropping happens in the "styling" stage,
            # in this case plain cropping without ellipsis.
            exp_stylized_dims=Dimensions(width=9, height=3),
            exp_plain_output_only_width='I scream,\nyou screa\nwe all sc\nfor ice c\n',
            exp_stylized_dims_only_width=Dimensions(width=9, height=4),
            exp_plain_output_only_height='…\nwe all scream\nfor ice cream\n',
            exp_stylized_dims_only_height=Dimensions(width=13, height=3),
        ),

        #
        # id='crop_height_and_width_flexible_width_crop_top'
        #
        FrameTestCase(
            frame=Frame(Dimensions(width=9, height=3), fixed_width=False),
            config=OutputConfig(
                horizontal_overflow_mode=HorizontalOverflowMode.CROP,
                vertical_overflow_mode=VerticalOverflowMode.CROP_TOP,
            ),
            exp_plain_output='you screa\nwe all sc\nfor ice c\n',
            # With vertical overflow mode set to CROP_TOP and frame width
            # flexible, vertical cropping is still carried out in the
            # "resize" stage. However, cropping from top does not reduce the
            # width (the longest lines are the bottom two).
            exp_resized_dims=Dimensions(width=13, height=3),
            # Simple horizontal cropping happens in the "styling" stage,
            # in this case plain cropping without ellipsis.
            exp_stylized_dims=Dimensions(width=9, height=3),
            exp_plain_output_only_width='I scream,\nyou screa\nwe all sc\nfor ice c\n',
            exp_stylized_dims_only_width=Dimensions(width=9, height=4),
            exp_plain_output_only_height='you scream,\nwe all scream\nfor ice cream\n',
            exp_stylized_dims_only_height=Dimensions(width=13, height=3),
        ),

        #
        # id='crop_height_and_width_flexible_width_crop_bottom'
        #
        FrameTestCase(
            frame=Frame(Dimensions(width=9, height=2), fixed_width=False),
            config=OutputConfig(
                horizontal_overflow_mode=HorizontalOverflowMode.CROP,
                vertical_overflow_mode=VerticalOverflowMode.CROP_BOTTOM,
            ),
            exp_plain_output='I scream,\nyou screa\n',
            # As in 'crop_height_and_width_flexible_width_crop_top'
            # vertical cropping is carried out in the "resize" stage.
            # However, in this case, the bottom two lines are removed (frame
            # height is 2) and the width is once more reduced.
            exp_resized_dims=Dimensions(width=11, height=2),
            # Simple horizontal cropping happens in the "styling" stage,
            # in this case plain cropping without ellipsis.
            exp_stylized_dims=Dimensions(width=9, height=2),
            exp_plain_output_only_width='I scream,\nyou screa\nwe all sc\nfor ice c\n',
            exp_stylized_dims_only_width=Dimensions(width=9, height=4),
            exp_plain_output_only_height='I scream,\nyou scream,\n',
            exp_stylized_dims_only_height=Dimensions(width=11, height=2),
        ),

        #
        # id='crop_height_and_width_flexible_width_word_wrap'
        #
        FrameTestCase(
            frame=Frame(Dimensions(width=9, height=3), fixed_width=False),
            config=OutputConfig(
                horizontal_overflow_mode=HorizontalOverflowMode.WORD_WRAP,
                vertical_overflow_mode=VerticalOverflowMode.CROP_BOTTOM,
            ),
            exp_plain_output='I scream,\nyou \nscream,\n',
            # TODO: Since horizontal cropping with WORD_WRAP has the
            #       potential to reduce the width if combined with vertical
            #       cropping, it should be carried out in the "resize"
            #       stage.
            #
            # As in 'crop_height_and_width_flexible_width_crop_bottom'
            # vertical cropping is carried out in the "resize" stage.
            # However, in this case the second last line (of length 13) is
            # retained and width is not reduced.
            exp_resized_dims=Dimensions(width=13, height=3),
            # In this case word wrap is carried out in the "stylize" stage
            # instead of horizontal cropping.
            exp_stylized_dims=Dimensions(width=9, height=3),
            exp_plain_output_only_width=('I scream,\nyou \nscream,\nwe all \nscream\n'
                                         'for ice \ncream\n'),
            exp_stylized_dims_only_width=Dimensions(width=9, height=7),
            exp_plain_output_only_height='I scream,\nyou scream,\nwe all scream\n',
            exp_stylized_dims_only_height=Dimensions(width=13, height=3),
        ),

        #
        # id='crop_height_single_line_flexible_width'
        #
        FrameTestCase(
            frame=Frame(Dimensions(width=13, height=1), fixed_width=False),
            # Reducing the height to 1, vertical cropping ensures that the
            # only output is a single ellipsis character. Hence, the width
            # is also reduced to 1. Since the frame width is flexible, both
            # dimensions are reduced at the "resize" stage.
            exp_plain_output='…\n',
            exp_dims_all_stages=Dimensions(width=1, height=1),
        ),

        #
        # id='crop_height_single_line_fixed_width'
        #
        FrameTestCase(
            frame=Frame(Dimensions(width=13, height=1)),
            exp_plain_output='…\n',
            # Compare to 'crop_height_single_line_flexible_width'. Fixed
            # frame width disables vertical cropping at the "resize" stage.
            exp_resized_dims=Dimensions(width=13, height=4),
            # Vertical cropping instead only happens at the "styling"
            # stage.
            exp_stylized_dims=Dimensions(width=1, height=1),
        ),
    ),
    ids=(
        'no_frame',
        'larger_frame',
        'exact_frame',
        'crop_height_flexible_width',
        'crop_height_fixed_width',
        'crop_height_and_width_flexible_width_ellipsis_bottom',
        'crop_height_and_width_fixed_width_ellipsis_bottom',
        'crop_height_and_width_flexible_width_ellipsis_top',
        'crop_height_and_width_flexible_width_crop_top',
        'crop_height_and_width_flexible_width_crop_bottom',
        'crop_height_and_width_flexible_width_word_wrap',
        'crop_height_single_line_flexible_width',
        'crop_height_single_line_fixed_width',
    ),
)
@pc.case(id='simple_text', tags=['dims_and_edge_cases', 'syntax_text'])
def case_syntax_text_simple_text(
    frame_case: FrameTestCase[str, FrameWithWidthAndHeight],
    per_frame_variant: Annotated[FrameVariant, pc.fixture],
) -> PanelFrameVariantTestCase[str]:
    return PanelFrameVariantTestCase(
        content='I scream,\nyou scream,\nwe all scream\nfor ice cream',
        config=None,
        exp_plain_output_no_frame='I scream,\nyou scream,\nwe all scream\nfor ice cream\n',
        exp_dims_all_stages_no_frame=Dimensions(width=13, height=4),
        exp_plain_output_only_width='I scream,\nyou scream,\nwe all scream\nfor ice cream\n',
        exp_dims_all_stages_only_width=Dimensions(width=13, height=4),
        # Width should not be auto-adjusted to fit the content at the
        # "resize" stage if the frame does not define the width.
        exp_resized_dims_only_height=Dimensions(width=13, height=4),
        frame_case=frame_case,
        frame_variant=per_frame_variant,
    )


@pc.parametrize(
    'frame_case',
    (
        #
        # id='no_frame'
        #
        FrameTestCase(frame=None),

        #
        # id='exact_frame'
        #
        FrameTestCase(frame=Frame(Dimensions(width=4, height=2), fixed_width=False)),

        #
        # id='smaller_odd_width_frame_ellipsis'
        #
        FrameTestCase(
            frame=Frame(Dimensions(width=3, height=2), fixed_width=False),
            exp_plain_output='北…\n北…\n',
            exp_dims_all_stages=Dimensions(width=3, height=2),
        ),

        #
        # id='smaller_odd_width_fixed_frame_ellipsis'
        #
        FrameTestCase(
            frame=Frame(Dimensions(width=3, height=2)),
            exp_plain_output='北…\n北…\n',
            # The frame is fixed width, so the cropping logic for
            # double-width characters is not applied in the "reflowing"
            # stage. Hence, the width is not reduced until the "styling"
            # stage.
            exp_stylized_dims=Dimensions(width=3, height=2),
        ),

        #
        # id='smaller_odd_width_frame_crop'
        #
        FrameTestCase(
            frame=Frame(Dimensions(width=3, height=2), fixed_width=False),
            config=OutputConfig(horizontal_overflow_mode=HorizontalOverflowMode.CROP),
            exp_plain_output='北\n北\n',
            exp_dims_all_stages=Dimensions(width=2, height=2),
        ),

        #
        # id='smaller_odd_width_fixed_frame_crop'
        #
        FrameTestCase(
            frame=Frame(Dimensions(width=3, height=2)),
            config=OutputConfig(horizontal_overflow_mode=HorizontalOverflowMode.CROP),
            exp_plain_output='北 \n北 \n',
            # The frame is fixed width, so the cropping logic for
            # double-width characters is not applied in the "reflowing"
            # stage. The rich library adds a space at the end in the
            # "styling" stage to ensure exact text width.
            exp_stylized_dims=Dimensions(width=3, height=2),
        ),

        #
        # id='smaller_even_width_frame_ellipsis'
        #
        FrameTestCase(
            frame=Frame(Dimensions(width=2, height=2), fixed_width=False),
            exp_plain_output='…\n…\n',
            exp_dims_all_stages=Dimensions(width=1, height=2),
        ),

        #
        # id='smaller_even_width_fixed_frame_ellipsis'
        #
        FrameTestCase(
            frame=Frame(Dimensions(width=2, height=2)),
            exp_plain_output=' …\n …\n',
            # The frame is fixed width, so the cropping logic for
            # double-width characters is not applied in the "reflowing"
            # stage. The rich library adds a space at the beginning in the
            # "styling" stage to ensure exact text width.
            exp_stylized_dims=Dimensions(width=2, height=2),
        ),

        #
        # id='smaller_even_width_frame_crop'
        #
        FrameTestCase(
            frame=Frame(Dimensions(width=2, height=2), fixed_width=False),
            config=OutputConfig(horizontal_overflow_mode=HorizontalOverflowMode.CROP),
            exp_plain_output='北\n北\n',
            exp_dims_all_stages=Dimensions(width=2, height=2),
        ),

        #
        # id='smaller_even_width_fixed_frame_crop'
        #
        FrameTestCase(
            frame=Frame(Dimensions(width=2, height=2)),
            config=OutputConfig(horizontal_overflow_mode=HorizontalOverflowMode.CROP),
            exp_plain_output='北\n北\n',
            # The frame is fixed width, so the cropping logic for
            # double-width characters is not applied in the "reflowing"
            # stage. Hence, the width is not reduced until the "styling"
            # stage.
            exp_stylized_dims=Dimensions(width=2, height=2),
        ),

        #
        # id='single_width_frame_ellipsis'
        #
        FrameTestCase(
            frame=Frame(Dimensions(width=1, height=2), fixed_width=False),
            exp_plain_output='…\n…\n',
            exp_dims_all_stages=Dimensions(width=1, height=2),
        ),

        #
        # id='single_width_fixed_frame_ellipsis'
        #
        FrameTestCase(
            frame=Frame(Dimensions(width=1, height=2)),
            exp_plain_output='…\n…\n',
            # The frame is fixed width, so the cropping logic for
            # double-width characters is not applied in the "reflowing"
            # stage. Hence, the width is not reduced until the "styling"
            # stage.
            exp_stylized_dims=Dimensions(width=1, height=2),
        ),

        #
        # id='single_width_frame_crop'
        #
        FrameTestCase(
            frame=Frame(Dimensions(width=1, height=2), fixed_width=False),
            config=OutputConfig(horizontal_overflow_mode=HorizontalOverflowMode.CROP),
            exp_plain_output='\n\n',
            exp_dims_all_stages=Dimensions(width=0, height=2),
        ),

        #
        # id='single_width_fixed_frame_crop'
        #
        FrameTestCase(
            frame=Frame(Dimensions(width=1, height=2)),
            config=OutputConfig(horizontal_overflow_mode=HorizontalOverflowMode.CROP),
            exp_plain_output=' \n \n',
            # The frame is fixed width, so the cropping logic for
            # double-width characters is not applied in the "reflowing"
            # stage. The rich library adds a space at the end in the
            # "styling" stage to ensure exact text width.
            exp_stylized_dims=Dimensions(width=1, height=2),
        ),

        #
        # id='no_width_frame_ellipsis'
        #
        FrameTestCase(
            frame=Frame(Dimensions(width=0, height=2), fixed_width=False),
            config=OutputConfig(horizontal_overflow_mode=HorizontalOverflowMode.CROP),
            exp_plain_output='\n\n',
            # Frame width is zero, which shortcuts the cropping logic for
            # double-width characters in the "reflowing" stage. Hence, the
            # width is not reduced until the "styling" stage.
            exp_stylized_dims=Dimensions(width=0, height=2),
        ),

        #
        # id='no_width_fixed_frame_ellipsis'
        #
        FrameTestCase(
            frame=Frame(Dimensions(width=0, height=2)),
            config=OutputConfig(horizontal_overflow_mode=HorizontalOverflowMode.CROP),
            exp_plain_output='\n\n',
            # Frame width is both zero and fixed. Both shortcuts the
            # cropping logic for double-width characters in the "reflowing"
            # stage. Hence, the width is not reduced until the "styling"
            # stage.
            exp_stylized_dims=Dimensions(width=0, height=2),
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
    frame_case: FrameTestCase[str, FrameWithWidthAndHeight],
    per_frame_variant: Annotated[FrameVariant, pc.fixture],
) -> PanelFrameVariantTestCase[str]:
    return PanelFrameVariantTestCase(
        # Mandarin Chinese characters are double-width
        content='北京\n北京',
        exp_plain_output_no_frame='北京\n北京\n',
        exp_dims_all_stages_no_frame=Dimensions(width=4, height=2),
        exp_plain_output_only_height='北京\n北京\n',
        exp_dims_all_stages_only_height=Dimensions(width=4, height=2),
        frame_case=frame_case,
        frame_variant=per_frame_variant,
    )


@pc.parametrize(
    'frame_case',
    (
        #
        # id='no_frame'
        #
        FrameTestCase(frame=None),

        #
        # id='exact_frame'
        #
        FrameTestCase(frame=Frame(Dimensions(width=5, height=1), fixed_width=False)),

        #
        # id='smaller_even_width_frame_ellipsis'
        #
        FrameTestCase(
            frame=Frame(Dimensions(width=4, height=1), fixed_width=False),
            exp_plain_output=' a…\n',
            exp_dims_all_stages=Dimensions(width=3, height=1),
        ),

        #
        # id='smaller_even_width_fixed_frame_ellipsis'
        #
        FrameTestCase(
            frame=Frame(Dimensions(width=4, height=1)),
            exp_plain_output=' a …\n',
            # The frame is fixed width, so the cropping logic for
            # tab characters is not applied in the "reflowing" stage.
            # The rich library adds a space before the ellipsis in the
            # "styling" stage to ensure exact text width.
            exp_stylized_dims=Dimensions(width=4, height=1),
        ),

        #
        # id='smaller_even_width_frame_ellipsis_tab_size_3'
        #
        FrameTestCase(
            frame=Frame(Dimensions(width=4, height=1), fixed_width=False),
            config=OutputConfig(tab_size=3),
            exp_plain_output=' a b\n',
            # No cropping needed
            exp_dims_all_stages=Dimensions(width=4, height=1),
            exp_plain_output_only_height=' a b\n',
            exp_dims_all_stages_only_height=Dimensions(width=4, height=1),
        ),

        #
        # id='smaller_even_width_fixed_frame_ellipsis_tab_size_3'
        #
        FrameTestCase(
            frame=Frame(Dimensions(width=4, height=1)),
            config=OutputConfig(tab_size=3),
            exp_plain_output=' a b\n',
            # No cropping needed
            exp_dims_all_stages=Dimensions(width=4, height=1),
            exp_plain_output_only_height=' a b\n',
            exp_dims_all_stages_only_height=Dimensions(width=4, height=1),
        ),

        #
        # id='smaller_even_width_frame_crop'
        #
        FrameTestCase(
            frame=Frame(Dimensions(width=4, height=1), fixed_width=False),
            config=OutputConfig(horizontal_overflow_mode=HorizontalOverflowMode.CROP),
            exp_plain_output=' a\n',
            exp_dims_all_stages=Dimensions(width=2, height=1),
        ),

        #
        # id='smaller_even_width_fixed_frame_crop'
        #
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

        #
        # id='smaller_odd_width_frame_ellipsis'
        #
        FrameTestCase(
            frame=Frame(Dimensions(width=3, height=1), fixed_width=False),
            exp_plain_output=' a…\n',
            exp_dims_all_stages=Dimensions(width=3, height=1),
        ),

        #
        # id='smaller_odd_width_fixed_frame_ellipsis'
        #
        FrameTestCase(
            frame=Frame(Dimensions(width=3, height=1)),
            exp_plain_output=' a…\n',
            # The frame is fixed width, so the cropping logic for
            # tab characters is not applied in the "reflowing" stage.
            # Hence, the width is not reduced until the "styling" stage.
            exp_stylized_dims=Dimensions(width=3, height=1),
        ),

        #
        # id='smaller_odd_width_frame_crop'
        #
        FrameTestCase(
            frame=Frame(Dimensions(width=3, height=1), fixed_width=False),
            config=OutputConfig(horizontal_overflow_mode=HorizontalOverflowMode.CROP),
            exp_plain_output=' a\n',
            exp_dims_all_stages=Dimensions(width=2, height=1),
        ),

        #
        # id='smaller_odd_width_fixed_frame_crop'
        #
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

        #
        # id='width_two_frame_ellipsis'
        #
        FrameTestCase(
            frame=Frame(Dimensions(width=2, height=1), fixed_width=False),
            exp_plain_output=' …\n',
            # The space in the beginning is part of the content, hence it
            # is not removed.
            exp_dims_all_stages=Dimensions(width=2, height=1),
        ),

        #
        # id='width_two_fixed_frame_ellipsis'
        #
        FrameTestCase(
            frame=Frame(Dimensions(width=2, height=1)),
            exp_plain_output=' …\n',
            # The frame is fixed width, so the cropping logic for
            # tab characters is not applied in the "reflowing" stage.
            # Hence, the width is not reduced until the "styling" stage.
            exp_stylized_dims=Dimensions(width=2, height=1),
        ),

        #
        # id='width_two_frame_crop'
        #
        FrameTestCase(
            frame=Frame(Dimensions(width=2, height=1), fixed_width=False),
            config=OutputConfig(horizontal_overflow_mode=HorizontalOverflowMode.CROP),
            exp_plain_output=' a\n',
            exp_dims_all_stages=Dimensions(width=2, height=1),
        ),

        #
        # id='width_two_fixed_frame_crop'
        #
        FrameTestCase(
            frame=Frame(Dimensions(width=2, height=1)),
            config=OutputConfig(horizontal_overflow_mode=HorizontalOverflowMode.CROP),
            exp_plain_output=' a\n',
            # The frame is fixed width, so the cropping logic for
            # tab characters is not applied in the "reflowing" stage.
            # Hence, the width is not reduced until the "styling" stage.
            exp_stylized_dims=Dimensions(width=2, height=1),
        ),

        #
        # id='no_width_frame_ellipsis'
        #
        FrameTestCase(
            frame=Frame(Dimensions(width=0, height=1), fixed_width=False),
            config=OutputConfig(horizontal_overflow_mode=HorizontalOverflowMode.CROP),
            exp_plain_output='\n',
            # Frame width is zero, which shortcuts the cropping logic for
            # tab characters in the "reflowing" stage. Hence, the width is
            # not reduced until the "styling" stage.
            exp_stylized_dims=Dimensions(width=0, height=1),
        ),

        #
        # id='no_width_fixed_frame_ellipsis'
        #
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
    frame_case: FrameTestCase[str, FrameWithWidthAndHeight],
    per_frame_variant: Annotated[FrameVariant, pc.fixture],
) -> PanelFrameVariantTestCase[str]:
    return PanelFrameVariantTestCase(
        # Tab character width depends on context, filling the spaces until
        # the next tab stop (4 chars by default)
        content=' a\tb',
        exp_plain_output_no_frame=' a  b\n',
        exp_dims_all_stages_no_frame=Dimensions(width=5, height=1),
        exp_plain_output_only_height=' a  b\n',
        exp_dims_all_stages_only_height=Dimensions(width=5, height=1),
        frame_case=frame_case,
        frame_variant=per_frame_variant,
    )
