from typing import Annotated

import pytest_cases as pc

from omnipy.data._display.config import HorizontalOverflowMode, OutputConfig, VerticalOverflowMode
from omnipy.data._display.dimensions import Dimensions
from omnipy.data._display.frame import Frame, FrameWithWidthAndHeight
from omnipy.data._display.layout import Layout

from ...helpers.classes import MockPanel
from ..helpers import FrameTestCase, FrameVariant, PanelFrameVariantTestCase


@pc.parametrize(
    'frame_case',
    (
        FrameTestCase(frame=None),
        FrameTestCase(frame=Frame(Dimensions(width=5, height=5))),
        # Normally, height=1 outputs a single ellipsis character,
        # signalling more content. However, an empty layout has no
        # content, so the output is always empty.
        FrameTestCase(frame=Frame(Dimensions(width=0, height=1))),
        FrameTestCase(
            frame=Frame(Dimensions(width=0, height=0)),
            exp_plain_output='',
            exp_stylized_dims=Dimensions(width=0, height=0),
            exp_plain_output_only_width='\n',
            exp_stylized_dims_only_width=Dimensions(width=0, height=1),
        ),
    ),
    ids=(
        'no_frame',
        'larger_frame',
        'exact_frame',
        'zero_frame',
    ),
)
@pc.case(id='no_panels', tags=['dims_and_edge_cases', 'layout'])
def case_layout_no_panels(
    frame_case: FrameTestCase[FrameWithWidthAndHeight],
    per_frame_variant: Annotated[FrameVariant, pc.fixture],
) -> PanelFrameVariantTestCase[Layout]:
    return PanelFrameVariantTestCase(
        content=Layout(),
        frame=frame_case.frame,
        config=None,
        exp_plain_output_no_frame='\n',
        exp_dims_all_stages_no_frame=Dimensions(width=0, height=1),
        frame_case=frame_case,
        frame_variant=per_frame_variant,
    )


@pc.parametrize(
    'frame_case',
    (
        FrameTestCase(frame=None),
        FrameTestCase(frame=Frame(Dimensions(width=5, height=4)),),
        FrameTestCase(frame=Frame(Dimensions(width=4, height=3)),),
        FrameTestCase(
            frame=Frame(Dimensions(width=2, height=2)),
            exp_plain_output=('╭╮\n'
                              '╰╯\n'),
            # Cropping to frame is enacted for height only by resizing the
            # inner panel at the 'resize' stage, as the panel
            # width is already 0 and cannot be further reduced
            exp_resized_dims=Dimensions(width=4, height=2),
            # Width is cropped to 2 at the 'stylize' stage
            exp_stylized_dims=Dimensions(width=2, height=2),
            exp_plain_output_only_width=('╭╮\n'
                                         '││\n'
                                         '╰╯\n'),
            exp_resized_dims_only_width=Dimensions(width=4, height=3),
            exp_stylized_dims_only_width=Dimensions(width=2, height=3),
            exp_plain_output_only_height=('╭──╮\n'
                                          '╰──╯\n'),
            exp_resized_dims_only_height=Dimensions(width=4, height=2),
            exp_stylized_dims_only_height=Dimensions(width=4, height=2),
        ),
        FrameTestCase(
            frame=Frame(Dimensions(width=1, height=3)),
            exp_plain_output='…\n',
            # Cropping to a frame with width=1 crops to a single ellipsis
            # character, hence height is also cropped to 1, independent of
            # the height of the frame
            exp_stylized_dims=Dimensions(width=1, height=1),
            # For the 'only width' case, i.e. cropping to a frame with
            # width=1 and height=None, the height needs to be explicitly set
            # to 1, overriding the "default" non-cropped height of 3 set
            # globally for the test in the
            # `exp_dims_no_frame=Dimensions(width=4, height=3)` parameter
            # below.
            exp_stylized_dims_only_width=Dimensions(width=1, height=1),
            # For the 'only height' case, the "default" values of
            # `exp_output_no_frame` and `exp_dims_no_frame` is reiterated to
            # override `exp_plain_output` and `exp_stylized_dims` set above.
            exp_plain_output_only_height=('╭──╮\n'
                                          '│  │\n'
                                          '╰──╯\n'),
            exp_stylized_dims_only_height=Dimensions(width=4, height=3),
        ),
        FrameTestCase(
            frame=Frame(Dimensions(width=4, height=1)),
            exp_plain_output='…\n',
            # Cropping to a frame with height=1 crops to a single ellipsis
            # character, hence width is also cropped to 1, independent of
            # the width of the frame
            exp_stylized_dims=Dimensions(width=1, height=1),
            # For the 'only width' case, the "default" values of
            # `exp_output_no_frame` and `exp_dims_no_frame` is reiterated to
            # override `exp_plain_output` and `exp_stylized_dims` set above.
            exp_plain_output_only_width=('╭──╮\n'
                                         '│  │\n'
                                         '╰──╯\n'),
            exp_stylized_dims_only_width=Dimensions(width=4, height=3),
            # For the 'only height' case, the width needs to be explicitly
            # set to 1, overriding the "default" non-cropped height of 3 set
            # globally for the test by the `exp_dims_no_frame` parameter
            # below.
            exp_stylized_dims_only_height=Dimensions(width=1, height=1),
        ),
    ),
    ids=(
        'no_frame',
        'larger_frame',
        'exact_frame',
        'smaller_frame',
        'tiny_width',
        'tiny_height',
    ))
@pc.case(id='single_empty_panel', tags=['dims_and_edge_cases', 'layout'])
def case_layout_single_empty_panel(
    frame_case: FrameTestCase[FrameWithWidthAndHeight],
    per_frame_variant: Annotated[FrameVariant, pc.fixture],
) -> PanelFrameVariantTestCase[Layout]:
    return PanelFrameVariantTestCase(
        content=Layout(empty=MockPanel('')),
        frame=frame_case.frame,
        config=OutputConfig(
            # Horizontal and vertical overflow modes only apply to text
            # content within the panels. The table itself is always cropped
            # to an ellipsis when the dim in either way reaches 1.
            horizontal_overflow_mode=HorizontalOverflowMode.CROP,
            vertical_overflow_mode=VerticalOverflowMode.CROP_BOTTOM,
        ),
        exp_plain_output_no_frame=('╭──╮\n'
                                   '│  │\n'
                                   '╰──╯\n'),
        exp_dims_all_stages_no_frame=Dimensions(width=4, height=3),
        frame_case=frame_case,
        frame_variant=per_frame_variant,
    )


@pc.parametrize(
    'frame_case',
    (
        FrameTestCase(frame=None),
        FrameTestCase(frame=Frame(Dimensions(width=11, height=5))),
        FrameTestCase(frame=Frame(Dimensions(width=10, height=4))),
        FrameTestCase(
            frame=Frame(Dimensions(width=9, height=3)),
            exp_plain_output=('╭──────╮\n'
                              '│ Some │\n'
                              '╰──────╯\n'),
            # Cropping to frame is enacted by resizing the inner panel
            # at the 'resize' stage
            exp_resized_dims=Dimensions(width=9, height=3),
            # Due to the whitespace at the end of the first line, another
            # character is lost in the width at the 'stylize' stage
            exp_stylized_dims=Dimensions(width=8, height=3),
            exp_plain_output_only_width=('╭───────╮\n'
                                         '│ Some  │\n'
                                         '│ conte │\n'
                                         '╰───────╯\n'),
            # For the 'only width' case, the last line is not cropped,
            # and the width is not reduced due to whitespace at the end of
            # line. Hence, the width is specifically set to 9, overriding
            # `exp_stylized_dims` set above
            exp_stylized_dims_only_width=Dimensions(width=9, height=4),
            # For the 'only height' case, only the first line is displayed
            # and width is reduced by 2 compared to the "default" value of
            # 10 set globally for the test in the `exp_dims_no_frame`
            # parameter (below), due to whitespace at the end of the first
            # line. Hence, the width is specifically set to 8 here.
            exp_stylized_dims_only_height=Dimensions(width=8, height=3),
        ),
    ),
    ids=('no_frame', 'larger_frame', 'exact_frame', 'smaller_frame'),
)
@pc.case(id='single_panel', tags=['dims_and_edge_cases', 'layout'])
def case_layout_single_panel(
    frame_case: FrameTestCase[FrameWithWidthAndHeight],
    per_frame_variant: Annotated[FrameVariant, pc.fixture],
) -> PanelFrameVariantTestCase[Layout]:
    return PanelFrameVariantTestCase(
        content=Layout(
            panel=MockPanel(content='Some content', frame=Frame(Dimensions(width=6, height=2)))),
        frame=frame_case.frame,
        config=OutputConfig(
            # Horizontal and vertical overflow modes are not applied to text
            # in these tests as MockPanel is used, which ignores horizontal
            # and vertical overflow modes.
            horizontal_overflow_mode=HorizontalOverflowMode.CROP,
            vertical_overflow_mode=VerticalOverflowMode.CROP_BOTTOM,
        ),
        exp_plain_output_no_frame=('╭────────╮\n'
                                   '│ Some   │\n'
                                   '│ conten │\n'
                                   '╰────────╯\n'),
        exp_dims_all_stages_no_frame=Dimensions(width=10, height=4),
        frame_case=frame_case,
        frame_variant=per_frame_variant,
    )


@pc.parametrize(
    'frame_case',
    (
        FrameTestCase(frame=None),
        FrameTestCase(frame=Frame(Dimensions(width=21, height=5))),
        FrameTestCase(frame=Frame(Dimensions(width=20, height=4))),
        # Reduce panels with smallest height first. Do not create wider
        # table than needed
        FrameTestCase(
            frame=Frame(Dimensions(width=18, height=5)),
            exp_plain_output=('╭──────┬────────╮\n'
                              '│ Some │ (1, 2, │\n'
                              '│ text │ 3)     │\n'
                              '╰──────┴────────╯\n'),
            exp_dims_all_stages=Dimensions(width=17, height=4),
        ),
        # No change, but frame is now exact size again
        FrameTestCase(
            frame=Frame(Dimensions(width=17, height=5)),
            exp_plain_output=('╭──────┬────────╮\n'
                              '│ Some │ (1, 2, │\n'
                              '│ text │ 3)     │\n'
                              '╰──────┴────────╯\n'),
            exp_dims_all_stages=Dimensions(width=17, height=4),
        ),
        # Still no loss of characters in second panel
        FrameTestCase(
            frame=Frame(Dimensions(width=14, height=5)),
            exp_plain_output=('╭──────┬─────╮\n'
                              '│ Some │ (1, │\n'
                              '│ text │ 2,  │\n'
                              '│      │ 3)  │\n'
                              '╰──────┴─────╯\n'),
            exp_dims_all_stages=Dimensions(width=14, height=5),
            # Cropping to a frame with width=14 and height=None expands the
            # height of the second panel to 5, one character more than the
            # height when no frame cropping is applied, as described by the
            # "default" `exp_dims_no_frame=Dimensions(width=20, height=4)`
            # parameter set globally for the test (see below). Hence, the
            # heightmust be specifically set to 5 here.
            exp_dims_all_stages_only_width=Dimensions(width=14, height=5),
            # However, if only the height of the frame is set, then no
            # cropping is applied. Hence, we need to reiterate the "default"
            # `exp_dims_no_frame` dimensions for the 'only height' case
            exp_dims_all_stages_only_height=Dimensions(width=20, height=4),
        ),
        # Will lose characters in both panels - choose the one with largest
        # number of characters )excluding whitespace=
        FrameTestCase(
            frame=Frame(Dimensions(width=13, height=5)),
            exp_plain_output=('╭─────┬─────╮\n'
                              '│ Som │ (1, │\n'
                              '│ tex │ 2,  │\n'
                              '│     │ 3)  │\n'
                              '╰─────┴─────╯\n'),
            exp_dims_all_stages=Dimensions(width=13, height=5),
            # As explained for the width=14 case above, the height must be
            # specifically set to 5 here for the 'only width' case, while
            # the "default" `exp_dims_no_frame` dimensions are reiterated
            # for the 'only height' case
            exp_dims_all_stages_only_width=Dimensions(width=13, height=5),
            exp_dims_all_stages_only_height=Dimensions(width=20, height=4),
        ),
    ),
    ids=(
        'no_frame',
        'larger_frame',
        'exact_frame',
        'width_18_frame',
        'width_17_frame',
        'width_14_frame',
        'width_13_frame',
    ),
)
@pc.case(id='two_panels_with_dims', tags=['dims_and_edge_cases', 'layout'])
def case_layout_two_panels_with_dims(
    frame_case: FrameTestCase[FrameWithWidthAndHeight],
    per_frame_variant: Annotated[FrameVariant, pc.fixture],
) -> PanelFrameVariantTestCase[Layout]:
    return PanelFrameVariantTestCase(
        content=Layout(
            first=MockPanel(content='Some text', frame=Frame(Dimensions(width=4, height=2))),
            second=MockPanel(content='(1, 2, 3)'),
        ),
        frame=frame_case.frame,
        config=OutputConfig(
            # Horizontal and vertical overflow modes are not applied to text
            # in these tests as MockPanel is used, which ignores horizontal
            # and vertical overflow modes.
            horizontal_overflow_mode=HorizontalOverflowMode.CROP,
            vertical_overflow_mode=VerticalOverflowMode.CROP_BOTTOM,
        ),
        exp_plain_output_no_frame=('╭──────┬───────────╮\n'
                                   '│ Some │ (1, 2, 3) │\n'
                                   '│ text │           │\n'
                                   '╰──────┴───────────╯\n'),
        exp_dims_all_stages_no_frame=Dimensions(width=20, height=4),
        # The height is not reduced in any cases, hence there is no
        # cropping in the 'only height' variant of any case. Thus, the
        # 'only_height' parameters are set globally for the entire test
        exp_plain_output_only_height=('╭──────┬───────────╮\n'
                                      '│ Some │ (1, 2, 3) │\n'
                                      '│ text │           │\n'
                                      '╰──────┴───────────╯\n'),
        exp_dims_all_stages_only_height=Dimensions(width=20, height=4),
        frame_case=frame_case,
        frame_variant=per_frame_variant,
    )
