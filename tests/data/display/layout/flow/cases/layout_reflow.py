from typing import Annotated

import pytest_cases as pc

from omnipy.data._display.config import (ConsoleColorSystem,
                                         HorizontalOverflowMode,
                                         OutputConfig,
                                         VerticalOverflowMode)
from omnipy.data._display.dimensions import Dimensions
from omnipy.data._display.frame import Frame, FrameWithWidthAndHeight
from omnipy.data._display.layout.base import Layout

from ....panel.helpers.case_setup import FrameTestCase, FrameVariant, PanelFrameVariantTestCase
from ..helpers.mocks import MockConfigCropPanel, MockResizedConfigCropPanel

# Note:
#
# Mock panels are used as inner panels for these test cases to focus on
# outer layout panel functionality. In these tests, the inner panels only
# provides plain styling, but supports all types of horizontal and vertical
# overflow modes (according to config values).


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
        FrameTestCase(frame=Frame(Dimensions(width=20, height=5))),

        #
        # id='exact_frame'
        #
        FrameTestCase(frame=Frame(Dimensions(width=19, height=4))),

        #
        # id='taller_and_thinner_frame_reflow'
        #
        FrameTestCase(
            frame=Frame(Dimensions(width=18, height=5)),
            # The content is wider than the frame, so the content is
            # resized to fit the frame. The height and width is recalculated
            # from the reflowed content as the "resize" stage, allowing
            # white space to be reclaimed.
            exp_plain_output=('╭────────────────╮\n'
                              '│ This content   │\n'
                              '│ is             │\n'
                              '│ extraordinary! │\n'
                              '╰────────────────╯\n'),
            exp_dims_all_stages=Dimensions(width=18, height=5),
        ),

        #
        # id='thinner_frame'
        #
        FrameTestCase(
            frame=Frame(Dimensions(width=18, height=4)),
            # Vertical cropping with ellipsis after reflow. Since the last
            # line is removed, the height and width is recalculated as the
            # "resize" stage, allowing more white space to be reclaimed.
            exp_plain_output=('╭──────────────╮\n'
                              '│ This content │\n'
                              '│ …            │\n'
                              '╰──────────────╯\n'),
            exp_dims_all_stages=Dimensions(width=16, height=4),
            exp_plain_output_only_width=('╭────────────────╮\n'
                                         '│ This content   │\n'
                                         '│ is             │\n'
                                         '│ extraordinary! │\n'
                                         '╰────────────────╯\n'),
            exp_dims_all_stages_only_width=Dimensions(width=18, height=5),
        ),

        #
        # id='ellipsis_in_both_dims'
        #
        FrameTestCase(
            frame=Frame(Dimensions(width=10, height=5)),
            # Vertical and horizontal cropping, simultaneously, with
            # ellipses. Recalculation of dimensions at the "resize" stage
            # allows whitespace to be reclaimed.
            exp_plain_output=('╭────────╮\n'
                              '│ This   │\n'
                              '│ conte… │\n'
                              '│ …      │\n'
                              '╰────────╯\n'),
            exp_dims_all_stages=Dimensions(width=10, height=5),
            exp_plain_output_only_width=('╭────────╮\n'
                                         '│ This   │\n'
                                         '│ conte… │\n'
                                         '│ is     │\n'
                                         '│ extra… │\n'
                                         '╰────────╯\n'),
            exp_dims_all_stages_only_width=Dimensions(width=10, height=6),
        ),

        #
        # id='larger_inner_frame_ellipses_out_of_view'
        #
        FrameTestCase(
            content=Layout(
                panel=MockConfigCropPanel(
                    content='These contents are extra- ordinary!',
                    frame=Frame(Dimensions(width=7, height=4)),
                )),
            frame=Frame(Dimensions(width=10, height=5)),
            # Compare with 'ellipsis_in_both_dims':
            #
            # Setting the inner panel frame larger than what is visible
            # within the outer panel frame, removes the ellipses from the
            # output. The reason is that it is the inner panel that crops
            # the content according to the config. In the "only width" and
            # "only height" cases, you can see that the ellipses are found
            # just outside the visible area within the outer panel.
            exp_plain_output=('╭────────╮\n'
                              '│ These  │\n'
                              '│ conten │\n'
                              '│ are    │\n'
                              '╰────────╯\n'),
            exp_resized_dims=Dimensions(width=11, height=6),
            exp_stylized_dims=Dimensions(width=10, height=5),
            exp_plain_output_only_width=('╭────────╮\n'
                                         '│ These  │\n'
                                         '│ conten │\n'
                                         '│ are    │\n'
                                         '│ …      │\n'
                                         '╰────────╯\n'),
            exp_resized_dims_only_width=Dimensions(width=11, height=6),
            exp_stylized_dims_only_width=Dimensions(width=10, height=6),
            exp_plain_output_only_height=('╭─────────╮\n'
                                          '│ These   │\n'
                                          '│ conten… │\n'
                                          '│ are     │\n'
                                          '╰─────────╯\n'),
            exp_resized_dims_only_height=Dimensions(width=11, height=6),
            exp_stylized_dims_only_height=Dimensions(width=11, height=5),
        ),

        #
        # id='cropping_from_right_and_top'
        #
        FrameTestCase(
            content=Layout(
                panel=MockConfigCropPanel(
                    content='This content is\nextraordinary!',
                    config=OutputConfig(
                        horizontal_overflow_mode=HorizontalOverflowMode.CROP,
                        vertical_overflow_mode=VerticalOverflowMode.CROP_TOP,
                    ),
                )),
            frame=Frame(Dimensions(width=14, height=4)),
            # Here, vertical content is cropped plainly from the top, in the
            # "resize" stage.
            exp_plain_output=('╭────────────╮\n'
                              '│ content is │\n'
                              '│ extraordin │\n'
                              '╰────────────╯\n'),
            exp_dims_all_stages=Dimensions(width=14, height=4),
            exp_plain_output_only_width=('╭────────────╮\n'
                                         '│ This       │\n'
                                         '│ content is │\n'
                                         '│ extraordin │\n'
                                         '╰────────────╯\n'),
            exp_dims_all_stages_only_width=Dimensions(width=14, height=5),
        ),

        #
        # id='single_line_resized_inner_panel_flexible_width_crop_to_ellipsis'
        #
        FrameTestCase(
            content=Layout(
                panel=MockResizedConfigCropPanel(
                    content='This content is\nextraordinary!',
                    frame=Frame(Dimensions(width=15, height=1), fixed_width=False))),
            frame=Frame(Dimensions(width=19, height=3)),
            # Inner panel is a resized panel with a defined frame width,
            # which is flexible, and a frame height of 1. With the vertical
            # cropping mode set as default to
            # 'VerticalOverflowMode.ELLIPSIS_BOTTOM', the content is cropped
            # to a single ellipsis character, with the reduced dimensions
            # calculated at the "resize" stage to allow for other panels to
            # make use of the released area.
            exp_plain_output=('╭───╮\n'
                              '│ … │\n'
                              '╰───╯\n'),
            exp_dims_all_stages=Dimensions(width=5, height=3),
            exp_plain_output_only_height=('╭───╮\n'
                                          '│ … │\n'
                                          '╰───╯\n'),
            exp_dims_all_stages_only_height=Dimensions(width=5, height=3),
        ),

        #
        # id='single_line_resized_inner_panel_fixed_width_no_ellipsis_crop'
        #
        FrameTestCase(
            content=Layout(
                panel=MockResizedConfigCropPanel(
                    content='This content is\nextraordinary!',
                    frame=Frame(Dimensions(width=15, height=1)))),
            frame=Frame(Dimensions(width=19, height=3)),
            # Same as previous test case, but with the inner panel frame
            # width fixed. In this case, the inner panel content is still
            # cropped to a single ellipsis character, but the width is not
            # reduced and the outer panel will not reduce to reclaim the
            # whitespace on the right, even though the outer frame width is
            # flexible.
            exp_plain_output=('╭─────────────────╮\n'
                              '│ …               │\n'
                              '╰─────────────────╯\n'),
            exp_dims_all_stages=Dimensions(width=19, height=3),
            exp_plain_output_only_height=('╭─────────────────╮\n'
                                          '│ …               │\n'
                                          '╰─────────────────╯\n'),
            exp_dims_all_stages_only_height=Dimensions(width=19, height=3),
        ),

        #
        # id='smallest_frame_with_ellipsis'
        #
        FrameTestCase(
            frame=Frame(Dimensions(width=5, height=3)),
            # Smallest frame that can fit some panel content, which is
            # cropped vertically into a single ellipsis character at the
            # "resize" stage.
            exp_plain_output=('╭───╮\n'
                              '│ … │\n'
                              '╰───╯\n'),
            exp_dims_all_stages=Dimensions(width=5, height=3),
            # The 'only width' case is horizontally cropped to a single
            # ellipsis character per line.
            exp_plain_output_only_width=('╭───╮\n'
                                         '│ … │\n'
                                         '│ … │\n'
                                         '│ … │\n'
                                         '│ … │\n'
                                         '╰───╯\n'),
            exp_dims_all_stages_only_width=Dimensions(width=5, height=6),
            exp_plain_output_only_height=('╭───╮\n'
                                          '│ … │\n'
                                          '╰───╯\n'),
            exp_dims_all_stages_only_height=Dimensions(width=5, height=3),
        ),
    ),
    ids=(
        'no_frame',
        'larger_frame',
        'exact_frame',
        'taller_and_thinner_frame_reflow',
        'thinner_frame',
        'ellipses_in_both_dims',
        'larger_inner_frame_ellipses_out_of_view',
        'cropping_from_right_and_top',
        'single_line_resized_inner_panel_flexible_width_crop_to_ellipsis',
        'single_line_resized_inner_panel_fixed_width_no_ellipsis_crop',
        'smallest_frame_with_ellipsis',
    ),
)
@pc.case(id='single_panel', tags=['reflow_cases', 'layout'])
def case_layout_single_panel(
    frame_case: FrameTestCase[Layout, FrameWithWidthAndHeight],
    per_frame_variant: Annotated[FrameVariant, pc.fixture],
) -> PanelFrameVariantTestCase[Layout]:
    return PanelFrameVariantTestCase(
        content=Layout(panel=MockConfigCropPanel(content='This content is\nextraordinary!',)),
        exp_plain_output_no_frame=('╭─────────────────╮\n'
                                   '│ This content is │\n'
                                   '│ extraordinary!  │\n'
                                   '╰─────────────────╯\n'),
        exp_dims_all_stages_no_frame=Dimensions(width=19, height=4),
        exp_plain_output_only_height=('╭─────────────────╮\n'
                                      '│ This content is │\n'
                                      '│ extraordinary!  │\n'
                                      '╰─────────────────╯\n'),
        exp_dims_all_stages_only_height=Dimensions(width=19, height=4),
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
        FrameTestCase(frame=Frame(Dimensions(width=11, height=6))),

        #
        # id='exact_frame'
        #
        FrameTestCase(frame=Frame(Dimensions(width=10, height=5))),

        #
        # id='height_crop_frame'
        #
        FrameTestCase(
            frame=Frame(Dimensions(width=10, height=3)),
            # Notice that no automatic whitespace removal takes place when
            # the frame height is reduced to 3, as the inner panel frame
            # width is fixed to 6.
            exp_plain_output=('╭────────╮\n'
                              '│ Some   │\n'
                              '╰────────╯\n'),
            # No frame reduction in the resize stage due to fixed width and
            # height
            exp_resized_dims=Dimensions(width=10, height=5),
            exp_stylized_dims=Dimensions(width=10, height=3),
            exp_plain_output_only_width=('╭────────╮\n'
                                         '│ Some   │\n'
                                         '│ conte… │\n'
                                         '│ …      │\n'
                                         '╰────────╯\n'),
            exp_dims_all_stages_only_width=Dimensions(width=10, height=5),
        ),

        #
        # id='both_dims_crop_frame'
        #
        FrameTestCase(
            frame=Frame(Dimensions(width=9, height=3)),
            # Extra whitespace is still not removed.
            exp_plain_output=('╭───────╮\n'
                              '│ Some  │\n'
                              '╰───────╯\n'),
            # Still no frame reduction in the resize phase due to fixed
            # width and height
            exp_resized_dims=Dimensions(width=10, height=5),
            exp_stylized_dims=Dimensions(width=9, height=3),
            exp_plain_output_only_width=('╭───────╮\n'
                                         '│ Some  │\n'
                                         '│ conte │\n'
                                         '│ …     │\n'
                                         '╰───────╯\n'),
            exp_stylized_dims_only_width=Dimensions(width=9, height=5),
            exp_plain_output_only_height=('╭────────╮\n'
                                          '│ Some   │\n'
                                          '╰────────╯\n'),
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
    frame_case: FrameTestCase[Layout, FrameWithWidthAndHeight],
    per_frame_variant: Annotated[FrameVariant, pc.fixture],
) -> PanelFrameVariantTestCase[Layout]:
    return PanelFrameVariantTestCase(
        content=Layout(
            panel=MockConfigCropPanel(
                content='Some content shown here', frame=Frame(Dimensions(width=6, height=3)))),
        exp_plain_output_no_frame=('╭────────╮\n'
                                   '│ Some   │\n'
                                   '│ conte… │\n'
                                   '│ …      │\n'
                                   '╰────────╯\n'),
        exp_dims_all_stages_no_frame=Dimensions(width=10, height=5),
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
        FrameTestCase(frame=Frame(Dimensions(width=21, height=5))),

        #
        # id='reduced_width_frame_single_line_title'
        #
        FrameTestCase(
            frame=Frame(Dimensions(width=20, height=6)),
            exp_plain_output=('╭──────────────╮\n'
                              '│ A nice title │\n'
                              '│              │\n'
                              '│ Here is some │\n'
                              '│ text         │\n'
                              '╰──────────────╯\n'),
            # The frame is larger than needed by the content, so the
            # extra whitespace is trimmed at the "resize" stage,
            # reducing the panel width to 16
            exp_dims_all_stages=Dimensions(width=16, height=6),
        ),

        #
        # id='reduced_width_frame_double_line_title'
        #
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

        #
        # id='reduced_height_frame_crop_title_to_single_line'
        #
        FrameTestCase(
            frame=Frame(Dimensions(width=10, height=8)),
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

        #
        # id='reduced_height_frame_crop_content_keep_title_at_bottom'
        #
        FrameTestCase(
            frame=Frame(Dimensions(width=10, height=7)),
            # Just enough room for a single-line title (last line cropped),
            # while content is cropped to 3 lines. Both crop operations
            # happen at the "resize" stage
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
                                          '│   A nice title    │\n'
                                          '╰───────────────────╯\n'),
            exp_dims_all_stages_only_height=Dimensions(width=21, height=5),
        ),

        #
        # id='reduced_height_frame_remove_title'
        #
        FrameTestCase(
            frame=Frame(Dimensions(width=9, height=6)),
            # When only 2 or fewer lines of content are not in conflict with
            # a single-line title, the title is removed. As this happens in
            # the "resize" stage, horizontal cropping of the content is
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

        #
        # id='expand_width_frame_title_reappears'
        #
        FrameTestCase(
            frame=Frame(Dimensions(width=11, height=7)),
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

        #
        # id='reduced_width_frame_max_double_line_title'
        #
        FrameTestCase(
            frame=Frame(Dimensions(width=9, height=10)),
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
    frame_case: FrameTestCase[Layout, FrameWithWidthAndHeight],
    per_frame_variant: Annotated[FrameVariant, pc.fixture],
) -> PanelFrameVariantTestCase[Layout]:
    return PanelFrameVariantTestCase(
        content=Layout(
            panel=MockConfigCropPanel(content='Here is some text', title='A nice title'),),
        config=OutputConfig(
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
        #
        # id='no_frame'
        #
        FrameTestCase(frame=None),

        #
        # id='reduced_width'
        #
        FrameTestCase(
            frame=Frame(Dimensions(width=16, height=None)),
            exp_resized_dims=Dimensions(width=24, height=7),
            exp_stylized_dims=Dimensions(width=16, height=7),
            # Ellipses are not shown as the inner panel frame is fixed to a
            # larger dimension than what is visible within the outer frame.
            # Reducing the inner frame according to the visible area would
            # add ellipses.
            #
            # Also, whitespace on the right side are not reclaimed for the
            # same reason.
            #
            # See also the 'single_panel_resized_inner_panel_fixed_dims' case.
            exp_plain_output=('╭──────────────╮\n'
                              '│ Inner panel  │\n'
                              '│ fixed dims   │\n'
                              '│              │\n'
                              '│              │\n'
                              '│ Panel title  │\n'
                              '╰──────────────╯\n'),
        ),

        #
        # id='reduced_width_crop_contents'
        #
        FrameTestCase(
            frame=Frame(Dimensions(width=14, height=6)),
            exp_resized_dims=Dimensions(width=24, height=7),
            exp_stylized_dims=Dimensions(width=14, height=6),
            # The title is cropped with an ellipsis, as it is part of the
            # outer table.
            exp_plain_output=('╭────────────╮\n'
                              '│ Inner pane │\n'
                              '│ fixed dims │\n'
                              '│            │\n'
                              '│ Panel tit… │\n'
                              '╰────────────╯\n'),
            exp_plain_output_only_width=('╭────────────╮\n'
                                         '│ Inner pane │\n'
                                         '│ fixed dims │\n'
                                         '│            │\n'
                                         '│            │\n'
                                         '│ Panel tit… │\n'
                                         '╰────────────╯\n'),
            exp_stylized_dims_only_height=Dimensions(width=24, height=6),
            exp_plain_output_only_height=('╭──────────────────────╮\n'
                                          '│ Inner panel with     │\n'
                                          '│ fixed dims           │\n'
                                          '│                      │\n'
                                          '│     Panel title      │\n'
                                          '╰──────────────────────╯\n'),
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
    frame_case: FrameTestCase[Layout, FrameWithWidthAndHeight],
    per_frame_variant: Annotated[FrameVariant, pc.fixture],
) -> PanelFrameVariantTestCase[Layout]:
    return PanelFrameVariantTestCase(
        content=Layout(
            panel=MockConfigCropPanel(
                content='Inner panel with fixed dims',
                title='Panel title',
                frame=Frame(Dimensions(width=20, height=5)),
            ),),
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
        #
        # id='no_frame'
        #
        FrameTestCase(frame=None),

        #
        # id='larger_frame'
        #
        FrameTestCase(frame=Frame(Dimensions(width=9, height=5))),

        #
        # id='exact_frame'
        #
        FrameTestCase(frame=Frame(Dimensions(width=8, height=4))),

        #
        # id='smaller_frame'
        #
        FrameTestCase(
            frame=Frame(Dimensions(width=7, height=3)),
            # Ellipses are not shown as the inner panel frame is fixed to a
            # larger dimension than what is visible within the outer frame.
            # Reducing the inner frame according to the visible area would
            # add ellipses.
            #
            # Also, whitespace on the right side are not reclaimed for the
            # same reason.
            exp_plain_output=('╭─────╮\n'
                              '│ Som │\n'
                              '╰─────╯\n'),
            # No resizing of inner frame is possible, as it is already
            # in the resized stage.
            exp_resized_dims=Dimensions(width=8, height=4),
            # Cropping to frame is enacted by cropping at the "stylize"
            # stage, both horizontally and vertically
            exp_stylized_dims=Dimensions(width=7, height=3),
            exp_plain_output_only_width=('╭─────╮\n'
                                         '│ Som │\n'
                                         '│ …   │\n'
                                         '╰─────╯\n'),
            exp_stylized_dims_only_width=Dimensions(width=7, height=4),
            exp_plain_output_only_height=('╭──────╮\n'
                                          '│ Some │\n'
                                          '╰──────╯\n'),
            exp_stylized_dims_only_height=Dimensions(width=8, height=3),
        ),
    ),
    ids=(
        'no_frame',
        'larger_frame',
        'exact_frame',
        'smaller_frame',
    ),
)
@pc.case(id='single_panel_resized_inner_panel_fixed_dims', tags=['reflow_cases', 'layout'])
def case_layout_single_panel_resized_inner_panel_fixed_dims(
    frame_case: FrameTestCase[Layout, FrameWithWidthAndHeight],
    per_frame_variant: Annotated[FrameVariant, pc.fixture],
) -> PanelFrameVariantTestCase[Layout]:
    return PanelFrameVariantTestCase(
        content=Layout(
            panel=MockResizedConfigCropPanel(
                content='Some\ncontent\nhere', frame=Frame(Dimensions(width=4, height=2)))),
        # Without an outer frame, the visible area of the outer panel is the
        # size of the inner panel frame. Hence, the ellipsis from the inner
        # panel cropping is fully visible.
        exp_plain_output_no_frame=('╭──────╮\n'
                                   '│ Some │\n'
                                   '│ …    │\n'
                                   '╰──────╯\n'),
        exp_dims_all_stages_no_frame=Dimensions(width=8, height=4),
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
        FrameTestCase(frame=Frame(Dimensions(width=31, height=4))),

        #
        # id='exact_frame'
        #
        FrameTestCase(frame=Frame(Dimensions(width=30, height=3))),

        #
        # id='width_29_frame'
        #

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

        #
        # id='width_25_frame'
        #

        # No change, but frame is now exact size again
        FrameTestCase(
            frame=Frame(Dimensions(width=25, height=4)),
            exp_plain_output=('╭───────────┬───────────╮\n'
                              '│ Some text │ (1, 2, 3) │\n'
                              '│ here      │           │\n'
                              '╰───────────┴───────────╯\n'),
            exp_dims_all_stages=Dimensions(width=25, height=4),
        ),

        #
        # id='width_24_frame'
        #

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

        #
        # id='width_21_frame'
        #

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

        #
        # id='width_19_frame'
        #

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

        #
        # id='width_16_frame'
        #

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

        #
        # id='width_15_frame'
        #

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

        #
        # id='width_13_frame'
        #

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
                              '│ So… │ (1, │\n'
                              '│ te… │ 2,  │\n'
                              '│ he… │ 3)  │\n'
                              '╰─────┴─────╯\n'),
            exp_dims_all_stages=Dimensions(width=13, height=5),
        ),

        #
        # id='width_12_frame'
        #

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
                              '│ So… │ (… │\n'
                              '│ te… │ 2, │\n'
                              '│ he… │ 3) │\n'
                              '╰─────┴────╯\n'),
            exp_dims_all_stages=Dimensions(width=12, height=5),
        ),

        #
        # id='width_11_frame'
        #

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
                              '│ S… │ (… │\n'
                              '│ t… │ 2, │\n'
                              '│ h… │ 3) │\n'
                              '╰────┴────╯\n'),
            exp_dims_all_stages=Dimensions(width=11, height=5),
        ),

        #
        # id='width_10_frame'
        #

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
                              '│ S… │ … │\n'
                              '│ t… │ … │\n'
                              '│ h… │ … │\n'
                              '╰────┴───╯\n'),
            exp_dims_all_stages=Dimensions(width=10, height=5),
        ),

        #
        # id='width_9_frame'
        #

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
                              '│ … │ … │\n'
                              '│ … │ … │\n'
                              '│ … │ … │\n'
                              '╰───┴───╯\n'),
            exp_dims_all_stages=Dimensions(width=9, height=5),
        ),

        #
        # id='width_8_frame'
        #

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
                              '│ … │  │\n'
                              '│ … │  │\n'
                              '│ … │  │\n'
                              '╰───┴──╯\n'),
            exp_dims_all_stages=Dimensions(width=8, height=5),
        ),

        #
        # id='width_7_frame'
        #
        FrameTestCase(
            frame=Frame(Dimensions(width=7, height=3)),
            exp_plain_output=('╭──┬──╮\n'
                              '│  │  │\n'
                              '╰──┴──╯\n'),
            exp_dims_all_stages=Dimensions(width=7, height=3),
            exp_resized_dims_only_width=Dimensions(width=7, height=5),
        ),

        #
        # id='width_6_frame'
        #

        # All things being equal, reduce the rightmost panel. Contrast this
        # with the two-panel case in 'panel/cases/layout_basics.py' where
        # theleftmost panel is reduced first, as that case skips over layout
        # reflow.
        FrameTestCase(
            frame=Frame(Dimensions(width=6, height=3)),
            exp_plain_output=('╭──┬─╮\n'
                              '│  │ │\n'
                              '╰──┴─╯\n'),
            # No resizing of inner panel is possible in the "resize" stage,
            # as the widths are 0 for both panels. Hence, width resizing
            # happens in the "stylize" stage.
            exp_resized_dims=Dimensions(width=7, height=3),
            exp_stylized_dims=Dimensions(width=6, height=3),
            exp_resized_dims_only_width=Dimensions(width=7, height=5),
        ),

        #
        # id='width_5_frame'
        #

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
    frame_case: FrameTestCase[Layout, FrameWithWidthAndHeight],
    per_frame_variant: Annotated[FrameVariant, pc.fixture],
) -> PanelFrameVariantTestCase[Layout]:
    return PanelFrameVariantTestCase(
        content=Layout(
            first=MockConfigCropPanel(content='Some text here'),
            second=MockConfigCropPanel(content='(1, 2, 3)'),
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
