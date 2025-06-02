from typing import Annotated

import pytest_cases as pc

from omnipy.data._display.config import (ConsoleColorSystem,
                                         HorizontalOverflowMode,
                                         OutputConfig,
                                         VerticalOverflowMode)
from omnipy.data._display.dimensions import Dimensions
from omnipy.data._display.frame import Frame, FrameWithWidthAndHeight
from omnipy.data._display.layout.base import Layout

from ...helpers.case_setup import FrameTestCase, FrameVariant, PanelFrameVariantTestCase
from ...helpers.mocks import MockPanel, MockPanelStage2


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
            # Original dimensions of the empty layout are unchanged
            # when creating a ResizedLayoutDraftPanel directly. Layout
            # reflow happens at the transition of DraftPanel to
            # ResizedLayoutDraftPanel, when calling 'render_next_stage()'
            exp_resized_dims=Dimensions(width=4, height=3),
            # Width and height are in any case cropped to 2 at the
            # 'stylize' stage to fit the frame
            exp_stylized_dims=Dimensions(width=2, height=2),
            exp_plain_output_only_width=('╭╮\n'
                                         '││\n'
                                         '╰╯\n'),
            exp_stylized_dims_only_width=Dimensions(width=2, height=3),
            exp_plain_output_only_height=('╭──╮\n'
                                          '╰──╯\n'),
            exp_stylized_dims_only_height=Dimensions(width=4, height=2),
        ),
        FrameTestCase(
            frame=Frame(Dimensions(width=1, height=3), fixed_height=False),
            exp_plain_output='…\n',
            exp_resized_dims=Dimensions(width=4, height=3),
            # Cropping the table output and dimensions to an ellipsis
            # character also happens at the 'stylize' stage. This happens
            # when either the width or the height of the frame is 1.
            # Here, the frame width is 1. The frame height is also reduced
            # to 1, independent of the height of the frame.
            exp_stylized_dims=Dimensions(width=1, height=1),
            # For the 'only height' case, there is no cropping to a single
            # ellipsis character.
            exp_plain_output_only_height=('╭──╮\n'
                                          '│  │\n'
                                          '╰──╯\n'),
            exp_stylized_dims_only_height=Dimensions(width=4, height=3),
        ),
        FrameTestCase(
            frame=Frame(Dimensions(width=4, height=1)),
            exp_plain_output='…\n',
            exp_resized_dims=Dimensions(width=4, height=3),
            # Here, the table is cropped to an ellipsis character due to
            # the frame height being 1. The frame width is also reduced to 1,
            # independent of the width of the frame. (See test above for the
            # case of frame width being 1.)
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
    frame_case: FrameTestCase[FrameWithWidthAndHeight],
    per_frame_variant: Annotated[FrameVariant, pc.fixture],
) -> PanelFrameVariantTestCase[Layout]:
    return PanelFrameVariantTestCase(
        content=Layout(empty=MockPanel('')),
        frame=frame_case.frame,
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
        FrameTestCase(
            frame=Frame(
                Dimensions(width=5, height=3),
                # The height and width of the frame are not fixed, so that
                # the empty panel can maintain its natural size (height=2).
                fixed_height=False,
                fixed_width=False,
            ),),
        FrameTestCase(frame=Frame(Dimensions(width=4, height=2)),),
        FrameTestCase(
            frame=Frame(Dimensions(width=2, height=2)),
            exp_plain_output=('╭╮\n'
                              '╰╯\n'),
            # Width is cropped to 2 at the 'stylize' stage to fit the frame
            exp_stylized_dims=Dimensions(width=2, height=2),
            exp_plain_output_only_height=('╭──╮\n'
                                          '╰──╯\n'),
            exp_stylized_dims_only_height=Dimensions(width=4, height=2),
        ),
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
    frame_case: FrameTestCase[FrameWithWidthAndHeight],
    per_frame_variant: Annotated[FrameVariant, pc.fixture],
) -> PanelFrameVariantTestCase[Layout]:
    return PanelFrameVariantTestCase(
        content=Layout(empty=MockPanel('', frame=Frame(Dimensions(width=None, height=0)))),
        frame=frame_case.frame,
        # When the height of the empty panel is zero, the middle line of the
        # frame is not rendered, so the output is just the top and bottom
        # frame lines, also at the 'resize' stage.
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
        FrameTestCase(frame=None),
        FrameTestCase(frame=Frame(Dimensions(width=17, height=5))),
        FrameTestCase(frame=Frame(Dimensions(width=16, height=4))),
        FrameTestCase(
            frame=Frame(Dimensions(width=15, height=5)),
            # The panel content is wider than the frame, so it is cropped
            # to fit the frame dimensions at the 'stylize' stage. Since
            # there is no reflowing of the panel content, the extra height
            # is not utilized.
            exp_plain_output=('╭─────────────╮\n'
                              '│ Some conte… │\n'
                              '│ here        │\n'
                              '╰─────────────╯\n'),
            exp_resized_dims=Dimensions(width=16, height=4),
            exp_stylized_dims=Dimensions(width=15, height=4),
            exp_plain_output_only_height=('╭──────────────╮\n'
                                          '│ Some content │\n'
                                          '│ here         │\n'
                                          '╰──────────────╯\n'),
            exp_dims_all_stages_only_height=Dimensions(width=16, height=4),
        ),
        FrameTestCase(
            frame=Frame(Dimensions(width=5, height=3)),
            # Smallest frame that can fit some panel content, which is
            # cropped into a single ellipsis character.
            exp_plain_output=('╭───╮\n'
                              '│ … │\n'
                              '╰───╯\n'),
            exp_resized_dims=Dimensions(width=16, height=4),
            exp_stylized_dims=Dimensions(width=5, height=3),
            # The 'only width' case is cropped to a single ellipsis
            # character per line.
            exp_plain_output_only_width=('╭───╮\n'
                                         '│ … │\n'
                                         '│ … │\n'
                                         '╰───╯\n'),
            exp_stylized_dims_only_width=Dimensions(width=5, height=4),
            exp_plain_output_only_height=('╭──────────────╮\n'
                                          '│ Some content │\n'
                                          '╰──────────────╯\n'),
            exp_stylized_dims_only_height=Dimensions(width=16, height=3),
        ),
    ),
    ids=(
        'no_frame',
        'larger_frame',
        'exact_frame',
        'smaller_width_frame',
        'tiny_frame',
    ),
)
@pc.case(id='single_panel', tags=['dims_and_edge_cases', 'layout'])
def case_layout_single_panel(
    frame_case: FrameTestCase[FrameWithWidthAndHeight],
    per_frame_variant: Annotated[FrameVariant, pc.fixture],
) -> PanelFrameVariantTestCase[Layout]:
    return PanelFrameVariantTestCase(
        content=Layout(panel=MockPanel(content='Some content\nhere',)),
        frame=frame_case.frame,
        config=OutputConfig(
            # Horizontal and vertical overflow modes are not applied to text
            # in these tests as MockPanel is used, which ignores horizontal
            # and vertical overflow modes. Instead, the default ellipsis
            # cropping mode of the Ric library is applied to the text
            # content.
            horizontal_overflow_mode=HorizontalOverflowMode.CROP,
            vertical_overflow_mode=VerticalOverflowMode.CROP_BOTTOM,
        ),
        exp_plain_output_no_frame=('╭──────────────╮\n'
                                   '│ Some content │\n'
                                   '│ here         │\n'
                                   '╰──────────────╯\n'),
        exp_dims_all_stages_no_frame=Dimensions(width=16, height=4),
        frame_case=frame_case,
        frame_variant=per_frame_variant,
    )


@pc.parametrize(
    'frame_case',
    (
        FrameTestCase(frame=None),
        FrameTestCase(frame=Frame(Dimensions(width=21, height=5))),
        FrameTestCase(
            frame=Frame(Dimensions(width=20, height=5)),
            exp_plain_output=('╭──────────────────╮\n'
                              '│   A nice title   │\n'
                              '│                  │\n'
                              '│ Here is some te… │\n'
                              '╰──────────────────╯\n'),
            exp_stylized_dims=Dimensions(width=20, height=5),
        ),
        FrameTestCase(
            frame=Frame(Dimensions(width=14, height=6)),
            exp_plain_output=('╭────────────╮\n'
                              '│ A nice ti… │\n'
                              '│            │\n'
                              '│ Here is s… │\n'
                              '╰────────────╯\n'),
            # Title is cropped at the `stylize` stage, even though there
            # is enough frame height to display it in two lines. This is
            # because the layout reflowing is skipped for these tests.
            exp_stylized_dims=Dimensions(width=14, height=5),
        ),
        FrameTestCase(
            frame=Frame(Dimensions(width=10, height=7)),
            # Just enough room for a single-line title (last line cropped),
            # while content is cropped to 3 lines. Both crop operations
            # happen at the 'resize' stage
            config=OutputConfig(panel_title_at_top=False),
            exp_plain_output=('╭────────╮\n'
                              '│ Here … │\n'
                              '│        │\n'
                              '│        │\n'
                              '│        │\n'
                              '│ A nic… │\n'
                              '╰────────╯\n'),
            exp_stylized_dims=Dimensions(width=10, height=7),
            exp_plain_output_only_width=('╭────────╮\n'
                                         '│ Here … │\n'
                                         '│        │\n'
                                         '│ A nic… │\n'
                                         '╰────────╯\n'),
            exp_stylized_dims_only_width=Dimensions(width=10, height=5),
            exp_plain_output_only_height=('╭───────────────────╮\n'
                                          '│ Here is some text │\n'
                                          '│                   │\n'
                                          '│                   │\n'
                                          '│                   │\n'
                                          '│   A nice title    │\n'
                                          '╰───────────────────╯\n'),
            # The 'resized' dims are based on the cropped_dims of the
            # inner panel, not the frame of the outer panel. Hence, the
            # height is 5, not 7
            exp_stylized_dims_only_height=Dimensions(width=21, height=7),
        ),
        FrameTestCase(
            frame=Frame(Dimensions(width=10, height=4)),
            # When only 2 or fewer lines of content are not in conflict with
            # a single-line title, the title is removed. As this happens in
            # the 'resize' stage, horizontal cropping of the content is
            # triggered
            exp_plain_output=('╭────────╮\n'
                              '│ A nic… │\n'
                              '│        │\n'
                              '╰────────╯\n'),
            exp_stylized_dims=Dimensions(width=10, height=4),
            exp_plain_output_only_width=('╭────────╮\n'
                                         '│ A nic… │\n'
                                         '│        │\n'
                                         '│ Here … │\n'
                                         '╰────────╯\n'),
            exp_stylized_dims_only_width=Dimensions(width=10, height=5),
            exp_plain_output_only_height=('╭───────────────────╮\n'
                                          '│   A nice title    │\n'
                                          '│                   │\n'
                                          '╰───────────────────╯\n'),
            exp_stylized_dims_only_height=Dimensions(width=21, height=4),
        ),
    ),
    ids=(
        'no_frame',
        'exact_frame',
        'reduced_width_frame_single_line_title',
        'reduced_width_frame_double_line_title',
        'reduced_height_frame_crop_content_keep_title_at_bottom',
        'reduced_height_frame_remove_title',
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
        FrameTestCase(frame=Frame(Dimensions(width=29, height=5))),
        FrameTestCase(frame=Frame(Dimensions(width=28, height=4))),
        # Since the contents have not been reflowed, the table cropping of
        # the Rich library is applied at the 'stylize' stage. This reduces
        # the width of the widest panel first.
        FrameTestCase(
            frame=Frame(Dimensions(width=27, height=4)),
            exp_plain_output=('╭─────────────┬───────────╮\n'
                              '│ Some conte… │ (1, 2, 3) │\n'
                              '│ is          │           │\n'
                              '╰─────────────┴───────────╯\n'),
            exp_stylized_dims=Dimensions(width=27, height=4),
        ),
        # The two panels now have exactly the same width.
        FrameTestCase(
            frame=Frame(Dimensions(width=25, height=4)),
            exp_plain_output=('╭───────────┬───────────╮\n'
                              '│ Some con… │ (1, 2, 3) │\n'
                              '│ is        │           │\n'
                              '╰───────────┴───────────╯\n'),
            exp_stylized_dims=Dimensions(width=25, height=4),
        ),
        # When the panels are of the same width, the Rich library crops the
        # rightmost panel first.
        FrameTestCase(
            frame=Frame(Dimensions(width=24, height=4)),
            exp_plain_output=('╭───────────┬──────────╮\n'
                              '│ Some con… │ (1, 2, … │\n'
                              '│ is        │          │\n'
                              '╰───────────┴──────────╯\n'),
            exp_stylized_dims=Dimensions(width=24, height=4),
        ),
        FrameTestCase(
            frame=Frame(Dimensions(width=9, height=4)),
            exp_plain_output=('╭───┬───╮\n'
                              '│ … │ … │\n'
                              '│ … │   │\n'
                              '╰───┴───╯\n'),
            exp_stylized_dims=Dimensions(width=9, height=4),
        ),
        # Only one panel left with content. The Rich library crops the
        # rightmost panel first.
        FrameTestCase(
            frame=Frame(Dimensions(width=8, height=4)),
            exp_plain_output=('╭───┬──╮\n'
                              '│ … │  │\n'
                              '│ … │  │\n'
                              '╰───┴──╯\n'),
            exp_stylized_dims=Dimensions(width=8, height=4),
        ),
        # Since there is no content left to show, the height is reduced
        # to 3.
        FrameTestCase(
            frame=Frame(Dimensions(width=7, height=4)),
            exp_plain_output=('╭──┬──╮\n'
                              '│  │  │\n'
                              '╰──┴──╯\n'),
            exp_stylized_dims=Dimensions(width=7, height=3),
        ),
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
        # Reduce the widest panel
        FrameTestCase(
            frame=Frame(Dimensions(width=5, height=4)),
            exp_plain_output=('╭─┬─╮\n'
                              '│ │ │\n'
                              '╰─┴─╯\n'),
            exp_stylized_dims=Dimensions(width=5, height=3),
        ),
        # Reduce the rightmost panel
        FrameTestCase(
            frame=Frame(Dimensions(width=4, height=4)),
            exp_plain_output=('╭─┬╮\n'
                              '│ ││\n'
                              '╰─┴╯\n'),
            exp_stylized_dims=Dimensions(width=4, height=3),
        ),
        # Reduce the widest panel
        FrameTestCase(
            frame=Frame(Dimensions(width=3, height=4)),
            exp_plain_output=('╭┬╮\n'
                              '│││\n'
                              '╰┴╯\n'),
            exp_stylized_dims=Dimensions(width=3, height=3),
        ),
        # Remove the rightmost panel border
        FrameTestCase(
            frame=Frame(Dimensions(width=2, height=4)),
            exp_plain_output=('╭┬\n'
                              '││\n'
                              '╰┴\n'),
            exp_stylized_dims=Dimensions(width=2, height=3),
        ),
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
    frame_case: FrameTestCase[FrameWithWidthAndHeight],
    per_frame_variant: Annotated[FrameVariant, pc.fixture],
) -> PanelFrameVariantTestCase[Layout]:
    return PanelFrameVariantTestCase(
        content=Layout(
            # Stage 2 panel with fixed content and frame, as
            # MockPanel->MockPanelStage2 carries out content reflow if the
            # frame dimensions are set.
            first=MockPanelStage2(
                content='Some content\nis\nhere', frame=Frame(Dimensions(
                    width=12,
                    height=2,
                ))),
            # Here, the frame dimensions are not set, so MockPanel can be
            # used.
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
