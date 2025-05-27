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
@pc.case(id='single_panel', tags=['reflow_cases', 'layout'])
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
@pc.case(id='single_panel_fixed_dims', tags=['reflow_cases', 'layout'])
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
                              '│ A nic… │\n'
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
                              '│ A nic… │\n'
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
                                          '│                   │\n'
                                          '│                   │\n'
                                          '│   A nice title    │\n'
                                          '╰───────────────────╯\n'),
            # The 'resized' dims are based on the dims_if_cropped of the
            # inner panel, not the frame of the outer panel. Hence, the
            # height is 5, not 7
            exp_resized_dims_only_height=Dimensions(width=21, height=5),
            exp_stylized_dims_only_height=Dimensions(width=21, height=7),
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
                                         '│ A ni… │\n'
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
                              '│ A nice… │\n'
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
                              '│ A ni… │\n'
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
@pc.case(id='single_panel_with_title', tags=['reflow_cases', 'layout'])
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
        FrameTestCase(
            frame=Frame(Dimensions(width=16, height=None)),
            exp_resized_dims=Dimensions(width=24, height=7),
            exp_stylized_dims=Dimensions(width=16, height=7),
            exp_plain_output=('╭──────────────╮\n'
                              '│ Inner panel… │\n'
                              '│ fixed dims   │\n'
                              '│              │\n'
                              '│              │\n'
                              '│ Panel title  │\n'
                              '╰──────────────╯\n'),
        ),
        FrameTestCase(
            frame=Frame(Dimensions(width=14, height=6)),
            exp_resized_dims=Dimensions(width=24, height=7),
            exp_stylized_dims=Dimensions(width=14, height=6),
            exp_plain_output=('╭────────────╮\n'
                              '│ Inner pan… │\n'
                              '│ fixed dims │\n'
                              '│            │\n'
                              '│ Panel tit… │\n'
                              '╰────────────╯\n'),
            exp_plain_output_only_width=('╭────────────╮\n'
                                         '│ Inner pan… │\n'
                                         '│ fixed dims │\n'
                                         '│            │\n'
                                         '│            │\n'
                                         '│ Panel tit… │\n'
                                         '╰────────────╯\n'),
            # exp_dims_all_stages_only_width=Dimensions(width=24, height=7),
            exp_stylized_dims_only_height=Dimensions(width=24, height=6),
            exp_plain_output_only_height=('╭──────────────────────╮\n'
                                          '│ Inner panel with     │\n'
                                          '│ fixed dims           │\n'
                                          '│                      │\n'
                                          '│     Panel title      │\n'
                                          '╰──────────────────────╯\n'),
            # exp_dims_all_stages_only_height=Dimensions(width=24, height=7),
            exp_stylized_dims_only_width=Dimensions(width=14, height=7),
        ),
    ),
    ids=(
        'no_frame',
        'reduced_width',
        'reduced_width_crop_contents',
    ),
)
@pc.case(id='single_panel_with_title_fixed_dims', tags=['reflow_cases', 'layout'])
def case_layout_single_panel_with_title_fixed_dims(
    frame_case: FrameTestCase[FrameWithWidthAndHeight],
    per_frame_variant: Annotated[FrameVariant, pc.fixture],
) -> PanelFrameVariantTestCase[Layout]:
    return PanelFrameVariantTestCase(
        content=Layout(
            panel=MockPanel(
                content='Inner panel with fixed dims',
                title='Panel title',
                frame=Frame(Dimensions(width=20, height=5)),
            ),),
        frame=frame_case.frame,
        config=OutputConfig(panel_title_at_top=False,),
        exp_plain_output_no_frame=('╭──────────────────────╮\n'
                                   '│ Inner panel with     │\n'
                                   '│ fixed dims           │\n'
                                   '│                      │\n'
                                   '│                      │\n'
                                   '│     Panel title      │\n'
                                   '╰──────────────────────╯\n'),
        exp_dims_all_stages_no_frame=Dimensions(width=24, height=7),
        exp_plain_output_only_height=('╭──────────────────────╮\n'
                                      '│ Inner panel with     │\n'
                                      '│ fixed dims           │\n'
                                      '│                      │\n'
                                      '│                      │\n'
                                      '│     Panel title      │\n'
                                      '╰──────────────────────╯\n'),
        exp_dims_all_stages_only_height=Dimensions(width=24, height=7),
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
@pc.case(id='single_panel_stage_2_fixed_dims', tags=['reflow_cases', 'layout'])
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
        FrameTestCase(
            frame=Frame(Dimensions(width=7, height=3)),
            exp_plain_output=('╭──┬──╮\n'
                              '│  │  │\n'
                              '╰──┴──╯\n'),
            exp_dims_all_stages=Dimensions(width=7, height=3),
            exp_resized_dims_only_width=Dimensions(width=7, height=5),
        ),
        # All things being equal, reduce the rightmost panel. Contrast this
        # with the two-panel case in 'layout_basics.py', where the
        # leftmost panel is reduced first, as that case skips over layout
        # reflow.
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
            # Further recuction works the same as in the two-panel case in
            # 'layout_basics.py' and is skipped here.
            exp_resized_dims=Dimensions(width=7, height=3),
            exp_stylized_dims=Dimensions(width=5, height=3),
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
    ),
)
@pc.case(id='two_panels', tags=['reflow_cases', 'layout'])
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
