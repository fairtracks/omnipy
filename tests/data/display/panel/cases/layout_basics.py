from typing import Annotated

import pytest_cases as pc

from omnipy.data._display.config import (ConsoleColorSystem,
                                         HorizontalOverflowMode,
                                         OutputConfig,
                                         VerticalOverflowMode)
from omnipy.data._display.dimensions import Dimensions
from omnipy.data._display.frame import Frame, FrameWithWidthAndHeight
from omnipy.data._display.layout import Layout

from ...helpers.classes import MockPanel, MockPanelStage2
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
            # height of the inner panel at the 'resize' stage, as the inner
            # panel width is already 0 and cannot be further reduced
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
            # The height is reduced to 2 at the 'resize' stage by setting
            # the height of the inner panel to 0.
            exp_resized_dims=Dimensions(width=4, height=2),
            # In the `stylize` stage, cropping to a frame with height=1
            # crops to a single ellipsis character, hence width is also
            # cropped to 1, independent of the width of the frame
            exp_stylized_dims=Dimensions(width=1, height=1),
            # For the 'only width' case, the "default" values of
            # `exp_output_no_frame` and `exp_dims_no_frame` is reiterated to
            # override `exp_plain_output` and `exp_stylized_dims` set above.
            exp_plain_output_only_width=('╭──╮\n'
                                         '│  │\n'
                                         '╰──╯\n'),
            # For the 'only width' case, the "default" values of
            # `exp_output_no_frame` and `exp_dims_no_frame` is reiterated to
            # override `exp_plain_output`, `exp_resized_dims` and
            # `exp_stylized_dims` set above.
            exp_dims_all_stages_only_width=Dimensions(width=4, height=3),
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
        FrameTestCase(frame=Frame(Dimensions(width=22, height=4))),
        FrameTestCase(frame=Frame(Dimensions(width=21, height=3))),
        FrameTestCase(
            frame=Frame(Dimensions(width=20, height=4)),
            exp_plain_output=('╭──────────────╮\n'
                              '│ Some content │\n'
                              '│ here         │\n'
                              '╰──────────────╯\n'),
            # The frame is larger than needed by the content, so the
            # extra whitespace is trimmed at the 'resize' stage,
            # reducing the panel width to 16
            exp_dims_all_stages=Dimensions(width=16, height=4),
        ),
        FrameTestCase(
            frame=Frame(Dimensions(width=15, height=5)),
            exp_plain_output=('╭─────────╮\n'
                              '│ Some    │\n'
                              '│ content │\n'
                              '│ here    │\n'
                              '╰─────────╯\n'),
            exp_dims_all_stages=Dimensions(width=11, height=5),
        ),
        FrameTestCase(
            frame=Frame(Dimensions(width=11, height=3)),
            # Only the first line of the panel content is shown, hence the
            # extra whitespace needed for line 2 is trimmed at the 'resize'
            # stage, reducing the panel width further down to 8.
            exp_plain_output=('╭──────╮\n'
                              '│ Some │\n'
                              '╰──────╯\n'),
            exp_dims_all_stages=Dimensions(width=8, height=3),
            exp_plain_output_only_width=('╭─────────╮\n'
                                         '│ Some    │\n'
                                         '│ content │\n'
                                         '│ here    │\n'
                                         '╰─────────╯\n'),
            exp_dims_all_stages_only_width=Dimensions(width=11, height=5),
        ),
    ),
    ids=(
        'no_frame',
        'larger_frame',
        'exact_frame',
        'two_lines_frame',
        'three_lines_frame',
        'height_crop_frame',
    ),
)
@pc.case(id='single_panel', tags=['dims_and_edge_cases', 'layout'])
def case_layout_single_panel(
    frame_case: FrameTestCase[FrameWithWidthAndHeight],
    per_frame_variant: Annotated[FrameVariant, pc.fixture],
) -> PanelFrameVariantTestCase[Layout]:
    return PanelFrameVariantTestCase(
        content=Layout(panel=MockPanel(content='Some content here',)),
        frame=frame_case.frame,
        config=OutputConfig(
            # Horizontal and vertical overflow modes are not applied to text
            # in these tests as MockPanel is used, which ignores horizontal
            # and vertical overflow modes.
            horizontal_overflow_mode=HorizontalOverflowMode.CROP,
            vertical_overflow_mode=VerticalOverflowMode.CROP_BOTTOM,
        ),
        exp_plain_output_no_frame=('╭───────────────────╮\n'
                                   '│ Some content here │\n'
                                   '╰───────────────────╯\n'),
        exp_dims_all_stages_no_frame=Dimensions(width=21, height=3),
        exp_plain_output_only_height=('╭───────────────────╮\n'
                                      '│ Some content here │\n'
                                      '╰───────────────────╯\n'),
        exp_dims_all_stages_only_height=Dimensions(width=21, height=3),
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
            frame=Frame(Dimensions(width=10, height=3)),
            # Notice that no automatic whitespace removal takes place when
            # the frame height is reduced to 3, as the panel frame width is
            # fixed to 6.
            exp_plain_output=('╭────────╮\n'
                              '│ Some   │\n'
                              '╰────────╯\n'),
            # No frame reduction in the resize phase due to fixed width and
            # height
            exp_resized_dims=Dimensions(width=10, height=4),
            exp_stylized_dims=Dimensions(width=10, height=3),
            exp_plain_output_only_width=('╭────────╮\n'
                                         '│ Some   │\n'
                                         '│ conten │\n'
                                         '╰────────╯\n'),
            exp_dims_all_stages_only_width=Dimensions(width=10, height=4),
        ),
        FrameTestCase(
            frame=Frame(Dimensions(width=9, height=3)),
            # Extra whitespace is still not removed.
            exp_plain_output=('╭───────╮\n'
                              '│ Some  │\n'
                              '╰───────╯\n'),
            # Still no frame reduction in the resize phase due to fixed
            # width and height
            exp_resized_dims=Dimensions(width=10, height=4),
            exp_stylized_dims=Dimensions(width=9, height=3),
            exp_plain_output_only_width=('╭───────╮\n'
                                         '│ Some  │\n'
                                         '│ cont… │\n'
                                         '╰───────╯\n'),
            exp_resized_dims_only_width=Dimensions(width=10, height=4),
            exp_stylized_dims_only_width=Dimensions(width=9, height=4),
            exp_plain_output_only_height=('╭────────╮\n'
                                          '│ Some   │\n'
                                          '╰────────╯\n'),
            exp_resized_dims_only_height=Dimensions(width=10, height=4),
            exp_stylized_dims_only_height=Dimensions(width=10, height=3),
        ),
    ),
    ids=(
        'no_frame',
        'larger_frame',
        'exact_frame',
        'height_crop_frame',
        'both_dims_crop_frame',
    ),
)
@pc.case(id='single_panel_fixed_dims', tags=['dims_and_edge_cases', 'layout'])
def case_layout_single_panel_fixed_dims(
    frame_case: FrameTestCase[FrameWithWidthAndHeight],
    per_frame_variant: Annotated[FrameVariant, pc.fixture],
) -> PanelFrameVariantTestCase[Layout]:
    return PanelFrameVariantTestCase(
        content=Layout(
            panel=MockPanel(
                content='Some content here', frame=Frame(Dimensions(width=6, height=2)))),
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
        FrameTestCase(
            frame=Frame(Dimensions(width=20, height=6)),
            exp_plain_output=('╭──────────────╮\n'
                              '│ A nice title │\n'
                              '│              │\n'
                              '│ Here is some │\n'
                              '│ text         │\n'
                              '╰──────────────╯\n'),
            # The frame is larger than needed by the content, so the
            # extra whitespace is trimmed at the 'resize' stage,
            # reducing the panel width to 16
            exp_dims_all_stages=Dimensions(width=16, height=6),
        ),
        FrameTestCase(
            frame=Frame(Dimensions(width=15, height=7)),
            exp_plain_output=('╭───────────╮\n'
                              '│  A nice   │\n'
                              '│   title   │\n'
                              '│           │\n'
                              '│ Here is   │\n'
                              '│ some text │\n'
                              '╰───────────╯\n'),
            # Title can be wrapped into two lines maximum
            exp_dims_all_stages=Dimensions(width=13, height=7),
        ),
        FrameTestCase(
            frame=Frame(Dimensions(width=10, height=8), fixed_width=False),
            # Not enough room for a double-line title, so the title is
            # cropped to a single line
            exp_plain_output=('╭────────╮\n'
                              '│ A nice │\n'
                              '│        │\n'
                              '│ Here   │\n'
                              '│ is     │\n'
                              '│ some   │\n'
                              '│ text   │\n'
                              '╰────────╯\n'),
            # The dims include the width of the double-line title cropped to
            # a single line
            exp_dims_all_stages=Dimensions(width=10, height=8),
            exp_plain_output_only_width=('╭────────╮\n'
                                         '│ A nice │\n'
                                         '│ title  │\n'
                                         '│        │\n'
                                         '│ Here   │\n'
                                         '│ is     │\n'
                                         '│ some   │\n'
                                         '│ text   │\n'
                                         '╰────────╯\n'),
            exp_dims_all_stages_only_width=Dimensions(width=10, height=9),
        ),
        FrameTestCase(
            frame=Frame(Dimensions(width=10, height=7), fixed_width=False),
            # Just enough room for a single-line title (last line cropped),
            # while content is cropped to 3 lines. Both crop operations
            # happen at the 'resize' stage
            config=OutputConfig(panel_title_at_top=False),
            exp_plain_output=('╭────────╮\n'
                              '│ Here   │\n'
                              '│ is     │\n'
                              '│ some   │\n'
                              '│        │\n'
                              '│ A nice │\n'
                              '╰────────╯\n'),
            exp_dims_all_stages=Dimensions(width=10, height=7),
            exp_plain_output_only_width=('╭────────╮\n'
                                         '│ Here   │\n'
                                         '│ is     │\n'
                                         '│ some   │\n'
                                         '│ text   │\n'
                                         '│        │\n'
                                         '│ A nice │\n'
                                         '│ title  │\n'
                                         '╰────────╯\n'),
            exp_dims_all_stages_only_width=Dimensions(width=10, height=9),
            exp_plain_output_only_height=('╭───────────────────╮\n'
                                          '│ Here is some text │\n'
                                          '│                   │\n'
                                          '│   A nice title    │\n'
                                          '╰───────────────────╯\n'),
            exp_dims_all_stages_only_height=Dimensions(width=21, height=5),
        ),
        FrameTestCase(
            frame=Frame(Dimensions(width=9, height=6), fixed_width=False),
            # When only 2 or fewer lines of content are not in conflict with
            # a single-line title, the title is removed. As this happens in
            # the 'resize' stage, horizontal cropping of the content is
            # triggered
            exp_plain_output=('╭──────╮\n'
                              '│ Here │\n'
                              '│ is   │\n'
                              '│ some │\n'
                              '│ text │\n'
                              '╰──────╯\n'),
            exp_dims_all_stages=Dimensions(width=8, height=6),
            exp_plain_output_only_width=('╭───────╮\n'
                                         '│ A nic │\n'
                                         '│ title │\n'
                                         '│       │\n'
                                         '│ Here  │\n'
                                         '│ is    │\n'
                                         '│ some  │\n'
                                         '│ text  │\n'
                                         '╰───────╯\n'),
            exp_resized_dims_only_width=Dimensions(width=10, height=9),
            exp_stylized_dims_only_width=Dimensions(width=9, height=9),
        ),
        FrameTestCase(
            frame=Frame(Dimensions(width=11, height=7), fixed_width=False),
            # Once there is enough width to remove the conflict between the
            # title and the table, the title reappears.
            exp_plain_output=('╭─────────╮\n'
                              '│ A nice  │\n'
                              '│         │\n'
                              '│ Here is │\n'
                              '│ some    │\n'
                              '│ text    │\n'
                              '╰─────────╯\n'),
            exp_dims_all_stages=Dimensions(width=11, height=7),
            exp_plain_output_only_width=('╭─────────╮\n'
                                         '│ A nice  │\n'
                                         '│  title  │\n'
                                         '│         │\n'
                                         '│ Here is │\n'
                                         '│ some    │\n'
                                         '│ text    │\n'
                                         '╰─────────╯\n'),
            exp_dims_all_stages_only_width=Dimensions(width=11, height=8),
        ),
        FrameTestCase(
            frame=Frame(Dimensions(width=9, height=10), fixed_width=False),
            # Title does not expand into more than two lines, even though
            # there is enough vertical space. The title stops the frame
            # from being cropped horizontally, even though the width is
            # specified as flexible
            exp_plain_output=('╭───────╮\n'
                              '│ A nic │\n'
                              '│ title │\n'
                              '│       │\n'
                              '│ Here  │\n'
                              '│ is    │\n'
                              '│ some  │\n'
                              '│ text  │\n'
                              '╰───────╯\n'),
            exp_resized_dims=Dimensions(width=10, height=9),
            exp_stylized_dims=Dimensions(width=9, height=9),
        ),
    ),
    ids=(
        'no_frame',
        'exact_frame',
        'reduced_width_frame_single_line_title',
        'reduced_width_frame_double_line_title',
        'reduced_height_frame_crop_title_to_single_line',
        'reduced_height_frame_crop_content_keep_title_at_bottom',
        'reduced_height_frame_remove_title',
        'expand_width_frame_title_reappears',
        'reduced_width_frame_max_double_line_title',
    ),
)
@pc.case(id='single_panel_with_title', tags=['dims_and_edge_cases', 'layout'])
def case_layout_single_panel_with_title(
    frame_case: FrameTestCase[FrameWithWidthAndHeight],
    per_frame_variant: Annotated[FrameVariant, pc.fixture],
) -> PanelFrameVariantTestCase[Layout]:
    return PanelFrameVariantTestCase(
        content=Layout(panel=MockPanel(content='Here is some text', title='A nice title'),),
        frame=frame_case.frame,
        config=OutputConfig(
            # Horizontal and vertical overflow modes are not applied to text
            # in these tests as MockPanel is used, which ignores horizontal
            # and vertical overflow modes.
            horizontal_overflow_mode=HorizontalOverflowMode.CROP,
            vertical_overflow_mode=VerticalOverflowMode.CROP_BOTTOM,
            console_color_system=ConsoleColorSystem.ANSI_RGB,
            transparent_background=False,
        ),
        exp_plain_output_no_frame=('╭───────────────────╮\n'
                                   '│   A nice title    │\n'
                                   '│                   │\n'
                                   '│ Here is some text │\n'
                                   '╰───────────────────╯\n'),
        exp_dims_all_stages_no_frame=Dimensions(width=21, height=5),
        exp_plain_output_only_height=('╭───────────────────╮\n'
                                      '│   A nice title    │\n'
                                      '│                   │\n'
                                      '│ Here is some text │\n'
                                      '╰───────────────────╯\n'),
        exp_dims_all_stages_only_height=Dimensions(width=21, height=5),
        frame_case=frame_case,
        frame_variant=per_frame_variant,
    )


@pc.parametrize(
    'frame_case',
    (
        FrameTestCase(frame=None),
        FrameTestCase(frame=Frame(Dimensions(width=9, height=5))),
        FrameTestCase(frame=Frame(Dimensions(width=8, height=4))),
        FrameTestCase(
            frame=Frame(Dimensions(width=7, height=3)),
            exp_plain_output=('╭─────╮\n'
                              '│ So… │\n'
                              '╰─────╯\n'),
            # No resizing of inner frame is possible, as it is already
            # in the resized stage (stage 2).
            exp_resized_dims=Dimensions(width=8, height=4),
            # Cropping to frame is enacted by cropping at the 'stylize'
            # stage, both horizontally and vertically
            exp_stylized_dims=Dimensions(width=7, height=3),
            exp_plain_output_only_width=('╭─────╮\n'
                                         '│ So… │\n'
                                         '│ co… │\n'
                                         '╰─────╯\n'),
            exp_stylized_dims_only_width=Dimensions(width=7, height=4),
            exp_plain_output_only_height=('╭──────╮\n'
                                          '│ Some │\n'
                                          '╰──────╯\n'),
            exp_stylized_dims_only_height=Dimensions(width=8, height=3),
        ),
    ),
    ids=('no_frame', 'larger_frame', 'exact_frame', 'smaller_frame'),
)
@pc.case(id='single_panel_stage_2_fixed_dims', tags=['dims_and_edge_cases', 'layout'])
def case_layout_single_panel_stage_2_fixed_dims(
    frame_case: FrameTestCase[FrameWithWidthAndHeight],
    per_frame_variant: Annotated[FrameVariant, pc.fixture],
) -> PanelFrameVariantTestCase[Layout]:
    return PanelFrameVariantTestCase(
        content=Layout(
            panel=MockPanelStage2(
                content='Some\ncontent\nhere', frame=Frame(Dimensions(width=4, height=2)))),
        frame=frame_case.frame,
        config=OutputConfig(
            # Horizontal and vertical overflow modes are not applied to text
            # in these tests as MockPanelStage2 is used, which ignores
            # horizontal and vertical overflow modes.
            horizontal_overflow_mode=HorizontalOverflowMode.CROP,
            vertical_overflow_mode=VerticalOverflowMode.CROP_BOTTOM,
        ),
        exp_plain_output_no_frame=('╭──────╮\n'
                                   '│ Some │\n'
                                   '│ cont │\n'
                                   '╰──────╯\n'),
        exp_dims_all_stages_no_frame=Dimensions(width=8, height=4),
        frame_case=frame_case,
        frame_variant=per_frame_variant,
    )


@pc.parametrize(
    'frame_case',
    (
        FrameTestCase(frame=None),
        FrameTestCase(frame=Frame(Dimensions(width=31, height=4))),
        FrameTestCase(frame=Frame(Dimensions(width=30, height=3))),
        # Width-resizable panels:
        # - First
        # - Second
        #
        # Priority:
        # 1. All width-resizable panels have equal height
        # 2. All width-resizable panels have no or equal frame widths
        # 3. First panel is wider
        #
        # Resize widest panel first if every thing else is the same.
        # Do not create wider table than needed
        FrameTestCase(
            frame=Frame(Dimensions(width=29, height=4)),
            exp_plain_output=('╭───────────┬───────────╮\n'
                              '│ Some text │ (1, 2, 3) │\n'
                              '│ here      │           │\n'
                              '╰───────────┴───────────╯\n'),
            exp_dims_all_stages=Dimensions(width=25, height=4),
        ),
        # No change, but frame is now exact size again
        FrameTestCase(
            frame=Frame(Dimensions(width=25, height=4)),
            exp_plain_output=('╭───────────┬───────────╮\n'
                              '│ Some text │ (1, 2, 3) │\n'
                              '│ here      │           │\n'
                              '╰───────────┴───────────╯\n'),
            exp_dims_all_stages=Dimensions(width=25, height=4),
        ),
        # Width-resizable panels:
        # - First
        # - Second
        #
        # Priority:
        # 1. Second panel has lower height
        FrameTestCase(
            frame=Frame(Dimensions(width=24, height=4)),
            exp_plain_output=('╭───────────┬────────╮\n'
                              '│ Some text │ (1, 2, │\n'
                              '│ here      │ 3)     │\n'
                              '╰───────────┴────────╯\n'),
            exp_dims_all_stages=Dimensions(width=22, height=4),
        ),
        # Width-resizable panels:
        # - First
        # - Second
        #
        # Priority:
        # 1. All width-resizable panels have equal height
        # 2. First panel has wider frame
        #
        # First panel height is not extended due to fixed height frame.
        # With the first frame reduced, there is now room in the frame for
        # the second panel to return to its original size.
        FrameTestCase(
            frame=Frame(Dimensions(width=21, height=5)),
            exp_plain_output=('╭──────┬───────────╮\n'
                              '│ Some │ (1, 2, 3) │\n'
                              '│ text │           │\n'
                              '│ here │           │\n'
                              '╰──────┴───────────╯\n'),
            exp_dims_all_stages=Dimensions(width=20, height=5),
        ),
        # First panel is no longer width-resizable, since the text in the
        # first panel cannot be soft-wrapped more than what has already been
        # done.
        #
        # Width-resizable panels:
        # - Second
        #
        # Priority:
        # 1. Second panel has lower height per definition (being the only
        #    width-resizable panel left)
        FrameTestCase(
            frame=Frame(Dimensions(width=19, height=5)),
            exp_plain_output=('╭──────┬────────╮\n'
                              '│ Some │ (1, 2, │\n'
                              '│ text │ 3)     │\n'
                              '│ here │        │\n'
                              '╰──────┴────────╯\n'),
            exp_dims_all_stages=Dimensions(width=17, height=5),
        ),
        # Width-resizable panels:
        # - Second
        #
        # Priority:
        # 1. Second panel has lower height per definition (being the only
        #    width-resizable panel left)
        #
        # Slight rearrangement of the text in the second panel saves one
        # character
        FrameTestCase(
            frame=Frame(Dimensions(width=16, height=5)),
            exp_plain_output=('╭──────┬───────╮\n'
                              '│ Some │ (1,   │\n'
                              '│ text │ 2, 3) │\n'
                              '│ here │       │\n'
                              '╰──────┴───────╯\n'),
            exp_dims_all_stages=Dimensions(width=16, height=5),
        ),
        # Width-resizable panels:
        # - Second
        #
        # Priority:
        # 1. Second panel has lower height per definition (being the only
        #    width-resizable panel left)
        FrameTestCase(
            frame=Frame(Dimensions(width=15, height=5)),
            exp_plain_output=('╭──────┬─────╮\n'
                              '│ Some │ (1, │\n'
                              '│ text │ 2,  │\n'
                              '│ here │ 3)  │\n'
                              '╰──────┴─────╯\n'),
            exp_dims_all_stages=Dimensions(width=14, height=5),
        ),
        # Width-resizable panels:
        #   (none left)
        #
        # Priority:
        # 1. All width-resizable panels have equal height
        # 2. All width-resizable panels have no or equal frame widths
        # 3. First panel is wider
        FrameTestCase(
            frame=Frame(Dimensions(width=13, height=5)),
            exp_plain_output=('╭─────┬─────╮\n'
                              '│ Som │ (1, │\n'
                              '│ tex │ 2,  │\n'
                              '│ her │ 3)  │\n'
                              '╰─────┴─────╯\n'),
            exp_dims_all_stages=Dimensions(width=13, height=5),
        ),
        # Width-resizable panels:
        #   (none left)
        #
        # Priority:
        # 1. All width-resizable panels have equal height
        # 2. All width-resizable panels have no or equal frame widths
        # 3. Both panels have equal width
        # 4. With everything else being equal, reduce last panel first
        #
        # TODO: Consider alternative logic for panel prioritization
        # - Reduce second panel due to loss of fewer characters
        FrameTestCase(
            frame=Frame(Dimensions(width=12, height=5)),
            exp_plain_output=('╭─────┬────╮\n'
                              '│ Som │ (1 │\n'
                              '│ tex │ 2, │\n'
                              '│ her │ 3) │\n'
                              '╰─────┴────╯\n'),
            exp_dims_all_stages=Dimensions(width=12, height=5),
        ),
        # Width-resizable panels:
        #   (none left)
        #
        # Priority:
        # 1. All width-resizable panels have equal height
        # 2. All width-resizable panels have no or equal frame widths
        # 3. First panel is wider
        FrameTestCase(
            frame=Frame(Dimensions(width=11, height=5)),
            exp_plain_output=('╭────┬────╮\n'
                              '│ So │ (1 │\n'
                              '│ te │ 2, │\n'
                              '│ he │ 3) │\n'
                              '╰────┴────╯\n'),
            exp_dims_all_stages=Dimensions(width=11, height=5),
        ),
        # Width-resizable panels:
        #   (none left)
        #
        # Priority:
        # 1. All width-resizable panels have equal height
        # 2. All width-resizable panels have no or equal frame widths
        # 3. Both panels have equal width
        # 4. With everything else being equal, reduce last panel first
        #
        # Alternative logic for panel prioritization?
        # - Reduce first panel due to loss of fewer characters
        FrameTestCase(
            frame=Frame(Dimensions(width=10, height=5)),
            exp_plain_output=('╭────┬───╮\n'
                              '│ So │ ( │\n'
                              '│ te │ 2 │\n'
                              '│ he │ 3 │\n'
                              '╰────┴───╯\n'),
            exp_dims_all_stages=Dimensions(width=10, height=5),
        ),
        # Width-resizable panels:
        #   (none left)
        #
        # Priority:
        # 1. All width-resizable panels have equal height
        # 2. All width-resizable panels have no or equal frame widths
        # 3. First panel is wider
        FrameTestCase(
            frame=Frame(Dimensions(width=9, height=5)),
            exp_plain_output=('╭───┬───╮\n'
                              '│ S │ ( │\n'
                              '│ t │ 2 │\n'
                              '│ h │ 3 │\n'
                              '╰───┴───╯\n'),
            exp_dims_all_stages=Dimensions(width=9, height=5),
        ),
        # Width-resizable panels:
        #   (none left)
        #
        # Priority:
        # 1. All width-resizable panels have equal height
        # 2. All width-resizable panels have no or equal frame widths
        # 3. Both panels have equal width
        # 4. With everything else being equal, reduce last panel first
        #
        # Alternative logic for panel prioritization?
        # - Reduce first panel due to loss of fewer characters
        FrameTestCase(
            frame=Frame(Dimensions(width=8, height=5)),
            exp_plain_output=('╭───┬──╮\n'
                              '│ S │  │\n'
                              '│ t │  │\n'
                              '│ h │  │\n'
                              '╰───┴──╯\n'),
            exp_dims_all_stages=Dimensions(width=8, height=5),
        ),
        # Only one panel left with content
        FrameTestCase(
            frame=Frame(Dimensions(width=7, height=3)),
            exp_plain_output=('╭──┬──╮\n'
                              '│  │  │\n'
                              '╰──┴──╯\n'),
            exp_dims_all_stages=Dimensions(width=7, height=3),
            exp_resized_dims_only_width=Dimensions(width=7, height=5),
        ),
        # All things being equal, reduce the rightmost panel
        FrameTestCase(
            frame=Frame(Dimensions(width=6, height=3)),
            exp_plain_output=('╭──┬─╮\n'
                              '│  │ │\n'
                              '╰──┴─╯\n'),
            # No resizing of inner frame is possible in the 'resize' stage,
            # as the widths are 0 for both panels. Hence, width resizing
            # happens in the 'stylize' stage.
            exp_resized_dims=Dimensions(width=7, height=3),
            exp_stylized_dims=Dimensions(width=6, height=3),
            exp_resized_dims_only_width=Dimensions(width=7, height=5),
        ),
        # Reduce the widest panel
        FrameTestCase(
            frame=Frame(Dimensions(width=5, height=3)),
            exp_plain_output=('╭─┬─╮\n'
                              '│ │ │\n'
                              '╰─┴─╯\n'),
            # As above, resizing the width only in the 'stylize' stage
            exp_resized_dims=Dimensions(width=7, height=3),
            exp_stylized_dims=Dimensions(width=5, height=3),
            exp_resized_dims_only_width=Dimensions(width=7, height=5),
        ),
        # Reduce the rightmost panel
        FrameTestCase(
            frame=Frame(Dimensions(width=4, height=3)),
            exp_plain_output=('╭─┬╮\n'
                              '│ ││\n'
                              '╰─┴╯\n'),
            # As above, resizing the width only in the 'stylize' stage
            exp_resized_dims=Dimensions(width=7, height=3),
            exp_stylized_dims=Dimensions(width=4, height=3),
            exp_resized_dims_only_width=Dimensions(width=7, height=5),
        ),
        # Reduce the widest panel
        FrameTestCase(
            frame=Frame(Dimensions(width=3, height=3)),
            exp_plain_output=('╭┬╮\n'
                              '│││\n'
                              '╰┴╯\n'),
            # As above, resizing the width only in the 'stylize' stage
            exp_resized_dims=Dimensions(width=7, height=3),
            exp_stylized_dims=Dimensions(width=3, height=3),
            exp_resized_dims_only_width=Dimensions(width=7, height=5),
        ),
        # Remove the rightmost panel border
        FrameTestCase(
            frame=Frame(Dimensions(width=2, height=3)),
            exp_plain_output=('╭┬\n'
                              '││\n'
                              '╰┴\n'),
            # As above, resizing the width only in the 'stylize' stage
            exp_resized_dims=Dimensions(width=7, height=3),
            exp_stylized_dims=Dimensions(width=2, height=3),
            exp_resized_dims_only_width=Dimensions(width=7, height=5),
        ),
        # Width 1 => ellipsis
        FrameTestCase(
            frame=Frame(Dimensions(width=1, height=3)),
            exp_plain_output='…\n',
            # As above, resizing the width only in the 'stylize' stage
            exp_resized_dims=Dimensions(width=7, height=3),
            exp_stylized_dims=Dimensions(width=1, height=1),
            exp_resized_dims_only_width=Dimensions(width=7, height=5),
        ),
    ),
    ids=(
        'no_frame',
        'larger_frame',
        'exact_frame',
        'width_29_frame',
        'width_25_frame',
        'width_24_frame',
        'width_21_frame',
        'width_19_frame',
        'width_16_frame',
        'width_15_frame',
        'width_13_frame',
        'width_12_frame',
        'width_11_frame',
        'width_10_frame',
        'width_9_frame',
        'width_8_frame',
        'width_7_frame',
        'width_6_frame',
        'width_5_frame',
        'width_4_frame',
        'width_3_frame',
        'width_2_frame',
        'width_1_frame',
    ),
)
@pc.case(id='two_panels', tags=['dims_and_edge_cases', 'layout'])
def case_layout_two_panels(
    frame_case: FrameTestCase[FrameWithWidthAndHeight],
    per_frame_variant: Annotated[FrameVariant, pc.fixture],
) -> PanelFrameVariantTestCase[Layout]:
    return PanelFrameVariantTestCase(
        content=Layout(
            first=MockPanel(content='Some text here'),
            second=MockPanel(content='(1, 2, 3)'),
        ),
        frame=frame_case.frame,
        config=OutputConfig(
            # Horizontal and vertical overflow modes are not applied to text
            # in these tests as MockPanel is used, which ignores horizontal
            # and vertical overflow modes.
            horizontal_overflow_mode=HorizontalOverflowMode.CROP,
            vertical_overflow_mode=VerticalOverflowMode.CROP_BOTTOM,
            console_color_system=ConsoleColorSystem.ANSI_RGB,
            transparent_background=False,
        ),
        exp_plain_output_no_frame=('╭────────────────┬───────────╮\n'
                                   '│ Some text here │ (1, 2, 3) │\n'
                                   '╰────────────────┴───────────╯\n'),
        exp_dims_all_stages_no_frame=Dimensions(width=30, height=3),
        # No test cases reduce frame height. Thus, the 'only_height'
        # parameters are set globally for the entire test.
        exp_plain_output_only_height=('╭────────────────┬───────────╮\n'
                                      '│ Some text here │ (1, 2, 3) │\n'
                                      '╰────────────────┴───────────╯\n'),
        exp_dims_all_stages_only_height=Dimensions(width=30, height=3),
        frame_case=frame_case,
        frame_variant=per_frame_variant,
    )
