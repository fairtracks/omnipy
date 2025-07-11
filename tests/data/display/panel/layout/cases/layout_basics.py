from typing import Annotated

import pytest_cases as pc

from omnipy.data._display.config import OutputConfig
from omnipy.data._display.dimensions import Dimensions
from omnipy.data._display.frame import Frame, FrameWithWidthAndHeight
from omnipy.data._display.layout.base import Layout
from omnipy.shared.enums.display import (DisplayColorSystem,
                                         HorizontalOverflowMode,
                                         Justify,
                                         VerticalOverflowMode)

from ...helpers.case_setup import FrameTestCase, FrameVariant, PanelFrameVariantTestCase
from ...helpers.mocks import MockResizedStylablePlainCropPanel, MockStylablePlainCropPanel

# Note:
#
# Mock panels are used as inner panels for these test cases to focus on
# outer layout panel functionality. In these tests, the inner panels provide
# simple styling, but only supports plain cropping, horizontally and
# vertically (`horizontal_overflow_mode` and `vertical_overflow_mode`
# config values are ignored).


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
        # Normally, height=1 outputs a single ellipsis character,
        # signalling more content. However, an empty layout has no
        # content, so the output is always empty.
        FrameTestCase(frame=Frame(Dimensions(width=0, height=1))),

        #
        # id='zero_frame'
        #
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
    frame_case: FrameTestCase[Layout, FrameWithWidthAndHeight],
    per_frame_variant: Annotated[FrameVariant, pc.fixture],
) -> PanelFrameVariantTestCase[Layout]:
    return PanelFrameVariantTestCase(
        content=Layout(),
        config=None,
        exp_plain_output_no_frame='\n',
        exp_dims_all_stages_no_frame=Dimensions(width=0, height=1),
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
        FrameTestCase(frame=Frame(Dimensions(width=5, height=4)),),

        #
        # id='exact_frame'
        #
        FrameTestCase(frame=Frame(Dimensions(width=4, height=3)),),

        #
        # id='smaller_frame'
        #
        FrameTestCase(
            frame=Frame(Dimensions(width=2, height=2)),
            exp_plain_output=('╭╮\n'
                              '╰╯\n'),
            # In all test cases in this module, ResizedLayoutDraftPanel is
            # created directly, skipping the layout reflow step for the
            # outer panel, which otherwise happens when transitioning from
            # DraftPanel to ResizedLayoutDraftPanel through
            # `render_next_stage()`. Hence, original dimensions of the empty
            # layout are unchanged at the "resize" stage.
            exp_resized_dims=Dimensions(width=4, height=3),
            # Width and height are in any case cropped to 2 at the
            # "stylize" stage to fit the frame
            exp_stylized_dims=Dimensions(width=2, height=2),
            exp_plain_output_only_width=('╭╮\n'
                                         '││\n'
                                         '╰╯\n'),
            exp_stylized_dims_only_width=Dimensions(width=2, height=3),
            exp_plain_output_only_height=('╭──╮\n'
                                          '╰──╯\n'),
            exp_stylized_dims_only_height=Dimensions(width=4, height=2),
        ),

        #
        # id='tiny_width'
        #
        FrameTestCase(
            frame=Frame(Dimensions(width=1, height=3), fixed_height=False),
            exp_plain_output='…\n',
            exp_resized_dims=Dimensions(width=4, height=3),
            # Cropping the table output and dimensions to an ellipsis
            # character happens at the "stylize" stage if either the width
            # or the height of the frame is 1.
            #
            # Here, the frame width is 1. The frame height is also reduced
            # to 1, independently of the previous height of the frame.
            exp_stylized_dims=Dimensions(width=1, height=1),
            # For the 'only height' case, there is no cropping to a single
            # ellipsis character.
            exp_plain_output_only_height=('╭──╮\n'
                                          '│  │\n'
                                          '╰──╯\n'),
            exp_stylized_dims_only_height=Dimensions(width=4, height=3),
        ),

        #
        # id='tiny_height'
        #
        FrameTestCase(
            frame=Frame(Dimensions(width=4, height=1)),
            exp_plain_output='…\n',
            exp_resized_dims=Dimensions(width=4, height=3),
            # Here, the table is cropped to an ellipsis character due to
            # the frame height being 1. The frame width is also reduced to 1,
            # independently of the width of the frame. (See test above for the
            # case of the frame width being 1.)
            exp_stylized_dims=Dimensions(width=1, height=1),
            # For the 'only width' case, there is no cropping to a single
            # ellipsis character.
            exp_plain_output_only_width=('╭──╮\n'
                                         '│  │\n'
                                         '╰──╯\n'),
            exp_stylized_dims_only_width=Dimensions(width=4, height=3),
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
    frame_case: FrameTestCase[Layout, FrameWithWidthAndHeight],
    per_frame_variant: Annotated[FrameVariant, pc.fixture],
) -> PanelFrameVariantTestCase[Layout]:
    return PanelFrameVariantTestCase(
        content=Layout(empty=MockStylablePlainCropPanel('')),
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
        #
        # id='no_frame'
        #
        FrameTestCase(frame=None),

        #
        # id='larger_frame'
        #
        FrameTestCase(frame=Frame(Dimensions(width=5, height=3))),

        #
        # id='exact_frame'
        #
        FrameTestCase(frame=Frame(Dimensions(width=4, height=2))),

        #
        # id='smaller_frame'
        #
        FrameTestCase(
            frame=Frame(Dimensions(width=2, height=2)),
            exp_plain_output=('╭╮\n'
                              '╰╯\n'),
            # Width is cropped to 2 at the "stylize" stage to fit the frame
            exp_stylized_dims=Dimensions(width=2, height=2),
            exp_plain_output_only_height=('╭──╮\n'
                                          '╰──╯\n'),
            exp_stylized_dims_only_height=Dimensions(width=4, height=2),
        ),

        #
        # id='tiny_width'
        #
        FrameTestCase(
            frame=Frame(Dimensions(width=1, height=3), fixed_height=False),
            # Cropping to an ellipsis character, works the same as in the
            # case of single empty panel above, except that height stays at
            # 2 in the 'only height' case.
            exp_plain_output='…\n',
            exp_stylized_dims=Dimensions(width=1, height=1),
            exp_plain_output_only_height=('╭──╮\n'
                                          '╰──╯\n'),
            exp_stylized_dims_only_height=Dimensions(width=4, height=2),
        ),

        #
        # id='tiny_height'
        #
        FrameTestCase(
            frame=Frame(Dimensions(width=4, height=1)),
            # Cropping to an ellipsis character, works the same as in the
            # case of single empty panel above, except that height stays at
            # 2 in the 'only width' case.
            exp_plain_output='…\n',
            exp_stylized_dims=Dimensions(width=1, height=1),
            exp_plain_output_only_width=('╭──╮\n'
                                         '╰──╯\n'),
            exp_stylized_dims_only_width=Dimensions(width=4, height=2),
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
@pc.case(id='single_empty_panel_height_zero', tags=['dims_and_edge_cases', 'layout'])
def case_layout_single_empty_panel_height_zero(
    frame_case: FrameTestCase[Layout, FrameWithWidthAndHeight],
    per_frame_variant: Annotated[FrameVariant, pc.fixture],
) -> PanelFrameVariantTestCase[Layout]:
    return PanelFrameVariantTestCase(
        content=Layout(
            empty=MockStylablePlainCropPanel('', frame=Frame(Dimensions(width=None, height=0)))),
        # When the height of the empty panel is zero, the middle line of the
        # frame is not rendered, so the output is just the top and bottom
        # frame lines, also at the "resize" stage.
        exp_plain_output_no_frame=('╭──╮\n'
                                   '╰──╯\n'),
        # Height is 2 at all stages, independent of the frame height
        exp_dims_all_stages_no_frame=Dimensions(width=4, height=2),
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
        FrameTestCase(frame=Frame(Dimensions(width=20, height=5))),

        #
        # id='exact_frame'
        #
        FrameTestCase(frame=Frame(Dimensions(width=19, height=4))),

        #
        # id='taller_and_thinner_frame'
        #
        FrameTestCase(
            frame=Frame(Dimensions(width=18, height=5)),
            # In all test cases in this module, ResizedLayoutDraftPanel is
            # created directly, skipping the layout reflow step for the
            # outer panel, which otherwise happens when transitioning from
            # DraftPanel to ResizedLayoutDraftPanel through
            # 'render_next_stage()'. Hence, the inner panel frame dimensions
            # remains unset. As a consequence nothing happens when the inner
            # panel is resized when automatically transformed to a
            # "stylized" panel (through 'render_next_stage()') at the time
            # the outer StylizedLayoutPanel is created.
            #
            # The inner panel content is wider than what is visible inside
            # the outer frame, however, since there is no inner frame, there
            # is no change of dimensions at the "resize" stage leaving the
            # extra height in the outer frame unused. There is also no
            # cropping according to the configured horizontal or vertical
            # cropping modes.
            #
            # The only cropping applied is a straight, no-ellipsis crop of
            # the inner content according to the available visible area
            # within the outer panel, applied at the "stylize" stage. This
            # is to make sure the outer frame is still kept in all
            # configurations.
            #
            # See the test cases in 'layout_reflow' for examples on how
            # horizontal and vertical cropping modes are supposed to work
            # by default.
            exp_plain_output=('╭────────────────╮\n'
                              '│ This content i │\n'
                              '│ extraordinary! │\n'
                              '╰────────────────╯\n'),
            exp_resized_dims=Dimensions(width=19, height=4),
            exp_stylized_dims=Dimensions(width=18, height=4),
            exp_plain_output_only_height=('╭─────────────────╮\n'
                                          '│ This content is │\n'
                                          '│ extraordinary!  │\n'
                                          '╰─────────────────╯\n'),
            exp_stylized_dims_only_height=Dimensions(width=19, height=4),
        ),

        #
        # id='taller_and_thinner_frame_inner_frame_reflow'
        #
        FrameTestCase(
            content=Layout(
                panel=MockStylablePlainCropPanel(
                    content='This content is\nextraordinary!',
                    frame=Frame(Dimensions(width=14, height=3),))),
            frame=Frame(Dimensions(width=18, height=5)),
            # See comment to the `taller_and_thinner_frame` test case above
            # for default behavior in these test cases, with no automatic
            # setting of the inner frame dimensions.
            #
            # Directly setting the inner frame according to the visible
            # part within the outer panel instead enables reflow of the
            # inner panel content, and the extra available height from the
            # outer frame is utilized.
            exp_plain_output=('╭────────────────╮\n'
                              '│ This content   │\n'
                              '│ is             │\n'
                              '│ extraordinary! │\n'
                              '╰────────────────╯\n'),
            exp_dims_all_stages=Dimensions(width=18, height=5),
        ),

        #
        # id='taller_and_thinner_frame_inner_frame_reflow_justify_right'
        #
        FrameTestCase(
            content=Layout(
                panel=MockStylablePlainCropPanel(
                    content='This content is\nextraordinary!',
                    frame=Frame(Dimensions(width=14, height=3),),
                    config=OutputConfig(justify_in_layout=Justify.RIGHT),
                )),
            frame=Frame(Dimensions(width=18, height=5)),
            # As 'taller_and_thinner_frame_inner_frame_reflow', but with
            # right justification.
            exp_plain_output=('╭────────────────╮\n'
                              '│   This content │\n'
                              '│             is │\n'
                              '│ extraordinary! │\n'
                              '╰────────────────╯\n'),
            exp_dims_all_stages=Dimensions(width=18, height=5),
        ),

        #
        # id='taller_and_thinner_frame_inner_frame_reflow_justify_center'
        #
        FrameTestCase(
            content=Layout(
                panel=MockStylablePlainCropPanel(
                    content='This content is\nextraordinary!',
                    frame=Frame(Dimensions(width=14, height=3),),
                    config=OutputConfig(justify_in_layout=Justify.CENTER),
                )),
            frame=Frame(Dimensions(width=18, height=5)),
            # As 'taller_and_thinner_frame_inner_frame_reflow', but with
            # right justification.
            exp_plain_output=('╭────────────────╮\n'
                              '│  This content  │\n'
                              '│       is       │\n'
                              '│ extraordinary! │\n'
                              '╰────────────────╯\n'),
            exp_dims_all_stages=Dimensions(width=18, height=5),
        ),
        #
        # id='smaller_frame_large_inner_panel_crop'
        #
        FrameTestCase(
            content=Layout(
                panel=MockResizedStylablePlainCropPanel(
                    content='This content is\nextraordinary!',
                    frame=Frame(Dimensions(width=17, height=3)),
                )),
            frame=Frame(Dimensions(width=18, height=3)),
            # See test cases 'taller_and_thinner_frame' and
            # 'taller_and_thinner_frame_inner_frame_reflow' above for
            # context.
            #
            # Predefining the inner panel as an already "resized" panel
            # skips the resizing step. With inner frame dimensions now
            # defined at the "resize" stage, larger than what is visible
            # through the outer frame, the content is plainly cropped to
            # fit the visible area at the "stylize" stage.
            exp_plain_output=('╭────────────────╮\n'
                              '│ This content i │\n'
                              '╰────────────────╯\n'),
            exp_resized_dims=Dimensions(width=21, height=5),
            exp_stylized_dims=Dimensions(width=18, height=3),
            exp_plain_output_only_width=('╭────────────────╮\n'
                                         '│ This content i │\n'
                                         '│ extraordinary! │\n'
                                         '│                │\n'
                                         '╰────────────────╯\n'),
            exp_resized_dims_only_width=Dimensions(width=21, height=5),
            exp_stylized_dims_only_width=Dimensions(width=18, height=5),
            exp_plain_output_only_height=('╭───────────────────╮\n'
                                          '│ This content is   │\n'
                                          '╰───────────────────╯\n'),
            exp_resized_dims_only_height=Dimensions(width=21, height=5),
            exp_stylized_dims_only_height=Dimensions(width=21, height=3),
        ),

        #
        # id='larger_frame_large_inner_panel'
        #
        FrameTestCase(
            content=Layout(
                panel=MockResizedStylablePlainCropPanel(
                    content='This content is\nextraordinary!',
                    frame=Frame(Dimensions(width=17, height=3)),
                )),
            frame=Frame(Dimensions(width=23, height=6)),
            # See test cases 'smaller_frame_larger_inner_panel_crop' above
            # for context.
            #
            # The inner frame dimensions are kept at the same as in
            # 'smaller_frame_larger_inner_panel_crop' above, however, the
            # outer frame is larger than what is required to show the entire
            # inner frame. However, the outer panel is reduced to exactly
            # fit the inner panel within the visible area. Hence, one needs
            # to increase the inner panel frame in order to add whitespace,
            # not the outer panel frame.
            exp_plain_output=('╭───────────────────╮\n'
                              '│ This content is   │\n'
                              '│ extraordinary!    │\n'
                              '│                   │\n'
                              '╰───────────────────╯\n'),
            exp_dims_all_stages=Dimensions(width=21, height=5),
        ),

        #
        # id='larger_frame_large_inner_panel_flexible_frame'
        #
        FrameTestCase(
            content=Layout(
                panel=MockResizedStylablePlainCropPanel(
                    content='This content is\nextraordinary!',
                    frame=Frame(
                        Dimensions(width=17, height=3),
                        fixed_width=False,
                        fixed_height=False,
                    ),
                )),
            frame=Frame(Dimensions(width=23, height=6)),
            # Same as 'larger_frame_large_inner_panel', but with inner panel
            # frame set to flexible in both dimensions.
            #
            # In this case, the outer panel collapse to just fit the inner
            # panel contents.
            exp_plain_output=('╭─────────────────╮\n'
                              '│ This content is │\n'
                              '│ extraordinary!  │\n'
                              '╰─────────────────╯\n'),
            exp_dims_all_stages=Dimensions(width=19, height=4),
        ),

        #
        # id='smallest_frame'
        #
        FrameTestCase(
            frame=Frame(Dimensions(width=5, height=3)),
            # Smallest frame that can fit some panel content, which is
            # cropped into a single character.
            exp_plain_output=('╭───╮\n'
                              '│ T │\n'
                              '╰───╯\n'),
            # Since the inner panel frame is undefined, no dimension
            # reduction happens in the "resize" stage. Instead, plain
            # cropping to a single character is applied at the "stylize"
            # stage to fit the visibility within the outer frame.
            exp_resized_dims=Dimensions(width=19, height=4),
            exp_stylized_dims=Dimensions(width=5, height=3),
            # The 'only width' case is cropped to a single character per
            # line.
            exp_plain_output_only_width=('╭───╮\n'
                                         '│ T │\n'
                                         '│ e │\n'
                                         '╰───╯\n'),
            exp_stylized_dims_only_width=Dimensions(width=5, height=4),
            exp_plain_output_only_height=('╭─────────────────╮\n'
                                          '│ This content is │\n'
                                          '╰─────────────────╯\n'),
            exp_stylized_dims_only_height=Dimensions(width=19, height=3),
        ),
    ),
    ids=(
        'no_frame',
        'larger_frame',
        'exact_frame',
        'taller_and_thinner_frame',
        'taller_and_thinner_frame_inner_frame_reflow',
        'taller_and_thinner_frame_inner_frame_reflow_justify_right',
        'taller_and_thinner_frame_inner_frame_reflow_justify_center',
        'smaller_frame_large_inner_panel_crop',
        'larger_frame_large_inner_panel',
        'larger_frame_large_inner_panel_flexible_frame',
        'smallest_frame',
    ),
)
@pc.case(id='single_panel', tags=['dims_and_edge_cases', 'layout'])
def case_layout_single_panel(
    frame_case: FrameTestCase[Layout, FrameWithWidthAndHeight],
    per_frame_variant: Annotated[FrameVariant, pc.fixture],
) -> PanelFrameVariantTestCase[Layout]:
    return PanelFrameVariantTestCase(
        content=Layout(
            panel=MockStylablePlainCropPanel(content='This content is\nextraordinary!',)),
        exp_plain_output_no_frame=('╭─────────────────╮\n'
                                   '│ This content is │\n'
                                   '│ extraordinary!  │\n'
                                   '╰─────────────────╯\n'),
        exp_dims_all_stages_no_frame=Dimensions(width=19, height=4),
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
        FrameTestCase(frame=Frame(Dimensions(width=23, height=5))),

        #
        # id='exact_frame_justify_right'
        #
        FrameTestCase(
            content=Layout(
                panel=MockStylablePlainCropPanel(
                    content='Here is some text',
                    title='A nice title',
                    frame=Frame(Dimensions(width=19, height=None)),
                    config=OutputConfig(justify_in_layout=Justify.RIGHT),
                ),),
            frame=Frame(Dimensions(width=23, height=5)),
            exp_plain_output=('╭─────────────────────╮\n'
                              '│    A nice title     │\n'
                              '│                     │\n'
                              '│   Here is some text │\n'
                              '╰─────────────────────╯\n'),
            exp_plain_output_only_height=('╭─────────────────────╮\n'
                                          '│    A nice title     │\n'
                                          '│                     │\n'
                                          '│   Here is some text │\n'
                                          '╰─────────────────────╯\n'),
            exp_dims_all_stages_only_height=Dimensions(width=23, height=5),
        ),

        #
        # id='exact_frame_justify_center'
        #
        FrameTestCase(
            content=Layout(
                panel=MockStylablePlainCropPanel(
                    content='Here is some text',
                    title='A nice title',
                    frame=Frame(Dimensions(width=19, height=None)),
                    config=OutputConfig(justify_in_layout=Justify.CENTER),
                ),),
            frame=Frame(Dimensions(width=23, height=5)),
            exp_plain_output=('╭─────────────────────╮\n'
                              '│    A nice title     │\n'
                              '│                     │\n'
                              '│  Here is some text  │\n'
                              '╰─────────────────────╯\n'),
            exp_plain_output_only_height=('╭─────────────────────╮\n'
                                          '│    A nice title     │\n'
                                          '│                     │\n'
                                          '│  Here is some text  │\n'
                                          '╰─────────────────────╯\n'),
            exp_dims_all_stages_only_height=Dimensions(width=23, height=5),
        ),

        #
        # id='exact_content_width_frame_single_line_title'
        #
        FrameTestCase(
            frame=Frame(Dimensions(width=21, height=5)),
            exp_plain_output=('╭───────────────────╮\n'
                              '│   A nice title    │\n'
                              '│                   │\n'
                              '│ Here is some text │\n'
                              '╰───────────────────╯\n'),
            exp_stylized_dims=Dimensions(width=21, height=5),
        ),

        #
        # id='reduced_width_frame_single_line_title'
        #
        FrameTestCase(
            frame=Frame(Dimensions(width=20, height=5)),
            exp_plain_output=('╭──────────────────╮\n'
                              '│   A nice title   │\n'
                              '│                  │\n'
                              '│ Here is some tex │\n'
                              '╰──────────────────╯\n'),
            exp_stylized_dims=Dimensions(width=20, height=5),
        ),

        #
        # id='reduced_width_frame_not_double_line_title'
        #
        FrameTestCase(
            frame=Frame(Dimensions(width=14, height=6)),
            exp_plain_output=('╭────────────╮\n'
                              '│ A nice ti… │\n'
                              '│            │\n'
                              '│ Here is so │\n'
                              '╰────────────╯\n'),
            # Title is cropped at the `stylize` stage, even though there
            # is enough frame height to display it in two lines. This is
            # because the outer layout panel reflow is skipped for these
            # tests.
            exp_stylized_dims=Dimensions(width=14, height=5),
        ),

        #
        # id='reduced_height_frame_keep_title_at_bottom'
        #
        FrameTestCase(
            frame=Frame(Dimensions(width=10, height=7)),
            # Even though the outer frame has enough height to display
            # extra lines of empty content, the outer layout panel height is
            # reduced to fit the inner panel dimensions.
            config=OutputConfig(panel_title_at_top=False),
            exp_plain_output=('╭────────╮\n'
                              '│ Here i │\n'
                              '│        │\n'
                              '│ A nic… │\n'
                              '╰────────╯\n'),
            exp_stylized_dims=Dimensions(width=10, height=5),
            exp_plain_output_only_width=('╭────────╮\n'
                                         '│ Here i │\n'
                                         '│        │\n'
                                         '│ A nic… │\n'
                                         '╰────────╯\n'),
            exp_stylized_dims_only_width=Dimensions(width=10, height=5),
            # In the 'only height' case, the outer panel width is spanned
            # according to the width of the inner panel, adding whitespace.
            exp_plain_output_only_height=('╭─────────────────────╮\n'
                                          '│ Here is some text   │\n'
                                          '│                     │\n'
                                          '│    A nice title     │\n'
                                          '╰─────────────────────╯\n'),
            exp_stylized_dims_only_height=Dimensions(width=23, height=5),
        ),

        #
        # id='reduced_height_frame_taller_inner_panel_keep_title_at_bottom'
        #
        FrameTestCase(
            content=Layout(
                panel=MockStylablePlainCropPanel(
                    content='Here is some text',
                    title='A nice title',
                    frame=Frame(Dimensions(width=19, height=5)),
                )),
            frame=Frame(Dimensions(width=10, height=7)),
            # Adding two lines to the inner panel frame height, spans the
            # outer panel height accordingly.
            config=OutputConfig(panel_title_at_top=False),
            exp_plain_output=('╭────────╮\n'
                              '│ Here i │\n'
                              '│        │\n'
                              '│        │\n'
                              '│        │\n'
                              '│ A nic… │\n'
                              '╰────────╯\n'),
            exp_resized_dims=Dimensions(width=23, height=7),
            exp_stylized_dims=Dimensions(width=10, height=7),
            exp_plain_output_only_width=('╭────────╮\n'
                                         '│ Here i │\n'
                                         '│        │\n'
                                         '│        │\n'
                                         '│        │\n'
                                         '│ A nic… │\n'
                                         '╰────────╯\n'),
            exp_stylized_dims_only_width=Dimensions(width=10, height=7),
            exp_plain_output_only_height=('╭─────────────────────╮\n'
                                          '│ Here is some text   │\n'
                                          '│                     │\n'
                                          '│                     │\n'
                                          '│                     │\n'
                                          '│    A nice title     │\n'
                                          '╰─────────────────────╯\n'),
            exp_dims_all_stages_only_height=Dimensions(width=23, height=7),
        ),

        #
        # id='reduced_height_frame_does_not_remove_title'
        #
        FrameTestCase(
            frame=Frame(Dimensions(width=10, height=4)),
            # When only 2 or fewer lines of content are not in conflict with
            # a single-line title, the title is removed. However, title
            # removal happens during outer layout panel reflow, which is
            # skipped in these tests.
            exp_plain_output=('╭────────╮\n'
                              '│ A nic… │\n'
                              '│        │\n'
                              '╰────────╯\n'),
            exp_stylized_dims=Dimensions(width=10, height=4),
            exp_plain_output_only_width=('╭────────╮\n'
                                         '│ A nic… │\n'
                                         '│        │\n'
                                         '│ Here i │\n'
                                         '╰────────╯\n'),
            exp_stylized_dims_only_width=Dimensions(width=10, height=5),
            exp_plain_output_only_height=('╭─────────────────────╮\n'
                                          '│    A nice title     │\n'
                                          '│                     │\n'
                                          '╰─────────────────────╯\n'),
            exp_stylized_dims_only_height=Dimensions(width=23, height=4),
        ),
    ),
    ids=(
        'no_frame',
        'exact_frame',
        'exact_frame_justify_right',
        'exact_frame_justify_center',
        'exact_content_width_frame_single_line_title',
        'reduced_width_frame_single_line_title',
        'reduced_width_frame_not_double_line_title',
        'reduced_height_frame_keep_title_at_bottom',
        'reduced_height_frame_taller_inner_panel_keep_title_at_bottom',
        'reduced_height_frame_does_not_remove_title',
    ),
)
@pc.case(id='single_panel_fixed_inner_width_with_title', tags=['dims_and_edge_cases', 'layout'])
def case_layout_single_panel_fixed_width_with_title(
    frame_case: FrameTestCase[Layout, FrameWithWidthAndHeight],
    per_frame_variant: Annotated[FrameVariant, pc.fixture],
) -> PanelFrameVariantTestCase[Layout]:
    return PanelFrameVariantTestCase(
        content=Layout(
            panel=MockStylablePlainCropPanel(
                content='Here is some text',
                title='A nice title',
                frame=Frame(Dimensions(width=19, height=None)),
            )),
        config=OutputConfig(
            color_system=DisplayColorSystem.ANSI_RGB,
            transparent_background=False,
        ),
        exp_plain_output_no_frame=('╭─────────────────────╮\n'
                                   '│    A nice title     │\n'
                                   '│                     │\n'
                                   '│ Here is some text   │\n'
                                   '╰─────────────────────╯\n'),
        exp_dims_all_stages_no_frame=Dimensions(width=23, height=5),
        exp_plain_output_only_height=('╭─────────────────────╮\n'
                                      '│    A nice title     │\n'
                                      '│                     │\n'
                                      '│ Here is some text   │\n'
                                      '╰─────────────────────╯\n'),
        exp_dims_all_stages_only_height=Dimensions(width=23, height=5),
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
        FrameTestCase(frame=Frame(Dimensions(width=29, height=5))),

        #
        # id='exact_frame'
        #
        FrameTestCase(frame=Frame(Dimensions(width=28, height=4))),

        #
        # id='width_27_frame'
        #
        # Since the inner panel contents have not been reflowed, the table
        # cropping of the Rich library is applied at the "stylize" stage.
        # This reduces the width of the widest panel first.
        FrameTestCase(
            frame=Frame(Dimensions(width=27, height=4)),
            exp_plain_output=('╭─────────────┬───────────╮\n'
                              '│ Some conten │ (1, 2, 3) │\n'
                              '│ is          │           │\n'
                              '╰─────────────┴───────────╯\n'),
            exp_stylized_dims=Dimensions(width=27, height=4),
        ),

        #
        # id='width_25_frame'
        #
        # The two panels now have exactly the same width.
        FrameTestCase(
            frame=Frame(Dimensions(width=25, height=4)),
            exp_plain_output=('╭───────────┬───────────╮\n'
                              '│ Some cont │ (1, 2, 3) │\n'
                              '│ is        │           │\n'
                              '╰───────────┴───────────╯\n'),
            exp_stylized_dims=Dimensions(width=25, height=4),
        ),

        #
        # id='width_24_frame'
        #
        # When the panels are of the same width, the Rich library crops the
        # rightmost panel first.
        FrameTestCase(
            frame=Frame(Dimensions(width=24, height=4)),
            exp_plain_output=('╭───────────┬──────────╮\n'
                              '│ Some cont │ (1, 2, 3 │\n'
                              '│ is        │          │\n'
                              '╰───────────┴──────────╯\n'),
            exp_stylized_dims=Dimensions(width=24, height=4),
        ),

        #
        # id='width_9_frame'
        #
        FrameTestCase(
            frame=Frame(Dimensions(width=9, height=4)),
            exp_plain_output=('╭───┬───╮\n'
                              '│ S │ ( │\n'
                              '│ i │   │\n'
                              '╰───┴───╯\n'),
            exp_stylized_dims=Dimensions(width=9, height=4),
        ),

        #
        # id='width_8_frame'
        #
        # Only one panel left with content. The Rich library crops the
        # rightmost panel first.
        FrameTestCase(
            frame=Frame(Dimensions(width=8, height=4)),
            exp_plain_output=('╭───┬──╮\n'
                              '│ S │  │\n'
                              '│ i │  │\n'
                              '╰───┴──╯\n'),
            exp_stylized_dims=Dimensions(width=8, height=4),
        ),

        #
        # id='width_7_frame'
        #
        # Since there is no content left to show, the height is reduced
        # to 3.
        FrameTestCase(
            frame=Frame(Dimensions(width=7, height=4)),
            exp_plain_output=('╭──┬──╮\n'
                              '│  │  │\n'
                              '╰──┴──╯\n'),
            exp_stylized_dims=Dimensions(width=7, height=3),
        ),

        #
        # id='width_6_frame'
        #
        # Here, the Rich library inconsistently crops the leftmost panel
        # first. Compare with similar test in layout/flow/layout_reflow.py,
        # where Omnipy overrides Rich and crops the rightmost panel first,
        # maintaining consistency.
        FrameTestCase(
            frame=Frame(Dimensions(width=6, height=4)),
            exp_plain_output=('╭─┬──╮\n'
                              '│ │  │\n'
                              '╰─┴──╯\n'),
            exp_stylized_dims=Dimensions(width=6, height=3),
        ),

        #
        # id='width_5_frame'
        #
        # Reduce the widest panel
        FrameTestCase(
            frame=Frame(Dimensions(width=5, height=4)),
            exp_plain_output=('╭─┬─╮\n'
                              '│ │ │\n'
                              '╰─┴─╯\n'),
            exp_stylized_dims=Dimensions(width=5, height=3),
        ),

        #
        # id='width_4_frame'
        #
        # Reduce the rightmost panel
        FrameTestCase(
            frame=Frame(Dimensions(width=4, height=4)),
            exp_plain_output=('╭─┬╮\n'
                              '│ ││\n'
                              '╰─┴╯\n'),
            exp_stylized_dims=Dimensions(width=4, height=3),
        ),

        #
        # id='width_3_frame'
        #
        # Reduce the widest panel
        FrameTestCase(
            frame=Frame(Dimensions(width=3, height=4)),
            exp_plain_output=('╭┬╮\n'
                              '│││\n'
                              '╰┴╯\n'),
            exp_stylized_dims=Dimensions(width=3, height=3),
        ),

        #
        # id='width_2_frame'
        #
        # Remove the rightmost panel border
        FrameTestCase(
            frame=Frame(Dimensions(width=2, height=4)),
            exp_plain_output=('╭┬\n'
                              '││\n'
                              '╰┴\n'),
            exp_stylized_dims=Dimensions(width=2, height=3),
        ),

        #
        # id='width_1_frame'
        #
        # Width 1 => ellipsis
        FrameTestCase(
            frame=Frame(Dimensions(width=1, height=4)),
            exp_plain_output='…\n',
            exp_stylized_dims=Dimensions(width=1, height=1),
        ),
    ),
    ids=(
        'no_frame',
        'larger_frame',
        'exact_frame',
        'width_27_frame',
        'width_25_frame',
        'width_24_frame',
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
@pc.case(id='two_panels_one_fixed_content_and_frame', tags=['dims_and_edge_cases', 'layout'])
def case_layout_two_panels_fixed_content_and_frame(
    frame_case: FrameTestCase[Layout, FrameWithWidthAndHeight],
    per_frame_variant: Annotated[FrameVariant, pc.fixture],
) -> PanelFrameVariantTestCase[Layout]:
    return PanelFrameVariantTestCase(
        content=Layout(
            # Stage 2 panel with fixed content and frame, as
            # MockPanel->MockPanelStage2 carries out content reflow if the
            # frame dimensions are set.
            first=MockResizedStylablePlainCropPanel(
                content='Some content\nis\nhere', frame=Frame(Dimensions(
                    width=12,
                    height=2,
                ))),
            # Here, the frame dimensions are not set, so MockPanel can be
            # used.
            second=MockStylablePlainCropPanel(content='(1, 2, 3)'),
        ),
        config=OutputConfig(
            # Horizontal and vertical overflow modes are not applied to text
            # in these tests as MockPanel is used, which ignores horizontal
            # and vertical overflow modes.
            horizontal_overflow_mode=HorizontalOverflowMode.CROP,
            vertical_overflow_mode=VerticalOverflowMode.CROP_BOTTOM,
            color_system=DisplayColorSystem.ANSI_RGB,
            transparent_background=False,
        ),
        exp_plain_output_no_frame=('╭──────────────┬───────────╮\n'
                                   '│ Some content │ (1, 2, 3) │\n'
                                   '│ is           │           │\n'
                                   '╰──────────────┴───────────╯\n'),
        exp_dims_all_stages_no_frame=Dimensions(width=28, height=4),
        # No test cases reduce frame height. Thus, the 'only_height'
        # parameters are set globally for the entire test.
        exp_plain_output_only_height=('╭──────────────┬───────────╮\n'
                                      '│ Some content │ (1, 2, 3) │\n'
                                      '│ is           │           │\n'
                                      '╰──────────────┴───────────╯\n'),
        exp_dims_all_stages_only_height=Dimensions(width=28, height=4),
        frame_case=frame_case,
        frame_variant=per_frame_variant,
    )
