from typing import Annotated

import pytest_cases as pc

from omnipy.data._display.config import OutputConfig
from omnipy.data._display.dimensions import Dimensions
from omnipy.data._display.frame import Frame
from omnipy.data._display.layout.base import Layout
from omnipy.shared.enums.colorstyles import DarkHighContrastColorStyles, RecommendedColorStyles
from omnipy.shared.enums.display import DisplayColorSystem, HorizontalOverflowMode, PanelDesign

from ...helpers.case_setup import (OutputPropertyType,
                                   StylizedPanelOutputExpectations,
                                   StylizedPanelTestCaseSetup)
from ...helpers.mocks import MockStylablePlainCropPanel
from ...helpers.panel_assert import (fill_html_page_template,
                                     fill_html_tag_template,
                                     FONT_RENDER_BODY_STYLE)

# Note:
#
# Mock panels are used as inner panels for these test cases to focus on
# outer layout panel functionality. In these tests, the inner panels provide
# simple styling, but only supports plain cropping, horizontally and
# vertically (`horizontal_overflow_mode` and `vertical_overflow_mode`
# config values are ignored).


@pc.parametrize(
    'solid_background, panel_design',
    [(True, PanelDesign.TABLE), (False, PanelDesign.TABLE_SHOW_STYLE)],
)
@pc.case(id='no-frame-dark-color', tags=['setup', 'layout'])
def case_layout_styling_setup_no_frame(
    solid_background: bool,
    panel_design: PanelDesign.Literals,
) -> StylizedPanelTestCaseSetup[Layout]:
    # Create a simple layout with mock panels
    layout: Layout = Layout()
    layout['first'] = MockStylablePlainCropPanel(
        content='Panel_1 Content', frame=Frame(Dimensions(width=7, height=2)))
    layout['second'] = MockStylablePlainCropPanel(
        content='Panel_2 Content', frame=Frame(Dimensions(width=7, height=2)))

    # Create stylized output with default config (should use Table grid)
    return StylizedPanelTestCaseSetup(
        case_id=(
            'no-frame-dark-color' + ('-no-bg' if not solid_background else '') +  # noqa: W504
            ('-show-style' if panel_design is PanelDesign.TABLE_SHOW_STYLE else '')),
        content=layout,
        config=OutputConfig(
            system=DisplayColorSystem.ANSI_RGB,
            style=DarkHighContrastColorStyles.LIGHTBULB_PYGMENTS,
            panel=panel_design,
            bg=solid_background),
    )


@pc.parametrize(
    'solid_background, panel_design',
    [(True, PanelDesign.TABLE), (False, PanelDesign.TABLE_SHOW_STYLE)],
)
@pc.case(id='frame-title-light-color', tags=['setup', 'layout'])
def case_layout_styling_setup_frame_and_title(
    solid_background: bool,
    panel_design: PanelDesign.Literals,
) -> StylizedPanelTestCaseSetup[Layout]:
    # Create a simple layout with mock panels
    layout: Layout = Layout()
    layout['first'] = MockStylablePlainCropPanel(
        content='True',
        title='The title of Panel 1',
    )
    layout['second'] = MockStylablePlainCropPanel(
        content='Some longer content here',
        title='Panel 2',
    )

    # Create stylized output with default config (should use Table grid)
    return StylizedPanelTestCaseSetup(
        case_id=(
            'frame-title-light-color' + ('-no-bg' if not solid_background else '') +  # noqa: W504
            ('-show-style' if panel_design is PanelDesign.TABLE_SHOW_STYLE else '')),
        content=layout,
        config=OutputConfig(
            system=DisplayColorSystem.ANSI_RGB,
            style=RecommendedColorStyles.OMNIPY_SELENIZED_LIGHT,
            panel=panel_design,
            bg=solid_background,
            h_overflow=HorizontalOverflowMode.ELLIPSIS,
            title_at_top=False,
        ))


@pc.parametrize(
    'solid_background, panel_design',
    [(True, PanelDesign.TABLE), (False, PanelDesign.TABLE_SHOW_STYLE)],
)
@pc.case(id='tiny-cropped-table-dark-color', tags=['setup', 'layout'])
def case_layout_styling_setup_small_frame(
    solid_background: bool,
    panel_design: PanelDesign.Literals,
) -> StylizedPanelTestCaseSetup[Layout]:
    # Create a simple layout with mock panels
    layout: Layout = Layout()
    layout['first'] = MockStylablePlainCropPanel(
        content='Panel_1 Content', frame=Frame(Dimensions(width=7, height=2)))
    layout['second'] = MockStylablePlainCropPanel(
        content='Panel_2 Content', frame=Frame(Dimensions(width=7, height=2)))

    # Create stylized output with default config (should use Table grid)
    return StylizedPanelTestCaseSetup(
        case_id=(
            'tiny-cropped-table-dark-color' +  # noqa: W504
            ('-no-bg' if not solid_background else '') +  # noqa: W504
            ('-show-style' if panel_design is PanelDesign.TABLE_SHOW_STYLE else '')),
        content=layout,
        frame=Frame(Dimensions(width=2, height=2)),
        config=OutputConfig(
            system=DisplayColorSystem.ANSI_RGB,
            style=DarkHighContrastColorStyles.LIGHTBULB_PYGMENTS,
            panel=panel_design,
            bg=solid_background),
    )


@pc.case(id='plain-terminal-output', tags=['expectations', 'layout'])
def case_layout_styling_expectations_plain_terminal(
        plain_terminal: Annotated[OutputPropertyType,
                                  pc.fixture]) -> StylizedPanelOutputExpectations:
    no_frame_dark_color_exp_output = ('╭─────────┬─────────╮\n'
                                      '│ Panel_1 │ Panel_2 │\n'
                                      '│ Content │ Content │\n'
                                      '╰─────────┴─────────╯\n')

    no_frame_dark_color_no_bg_show_style_exp_output = (
        no_frame_dark_color_exp_output + '   lightbulb-pygments\n')

    frame_title_light_color_exp_output = ('╭────────────┬──────────────────────────╮\n'
                                          '│ True       │ Some longer content here │\n'
                                          '│            │                          │\n'
                                          '│ The title  │                          │\n'
                                          '│ of Panel 1 │         Panel 2          │\n'
                                          '╰────────────┴──────────────────────────╯\n')

    frame_title_light_color_no_bg_show_style_exp_output = (
        frame_title_light_color_exp_output + '            Style: omnipy-selenized-light\n')

    def _exp_plain_output_for_case_id(case_id: str) -> str:
        match case_id:
            case 'no-frame-dark-color':
                return no_frame_dark_color_exp_output

            case 'no-frame-dark-color-no-bg-show-style':
                return no_frame_dark_color_no_bg_show_style_exp_output

            case 'frame-title-light-color':
                return frame_title_light_color_exp_output

            case 'frame-title-light-color-no-bg-show-style':
                return frame_title_light_color_no_bg_show_style_exp_output

            case 'tiny-cropped-table-dark-color':
                return ('╭┬\n'
                        '╰┴\n')

            case 'tiny-cropped-table-dark-color-no-bg-show-style':
                return ('╭┬\n'
                        'li\n')
            case _:
                raise ValueError(f'Unexpected case_id: {case_id}')

    return StylizedPanelOutputExpectations(
        get_output_property=plain_terminal,
        exp_plain_output_for_case_id=_exp_plain_output_for_case_id,
    )


@pc.case(id='bw-stylized-terminal-output', tags=['expectations', 'layout'])
def case_layout_styling_expectations_bw_stylized_terminal(
    bw_stylized_terminal: Annotated[OutputPropertyType,
                                    pc.fixture]) -> StylizedPanelOutputExpectations:
    no_frame_dark_color_exp_output = ('╭─────────┬─────────╮\n'
                                      '│ \x1b[1mPanel_1\x1b[0m │ \x1b[1mPanel_2\x1b[0m │\n'
                                      '│ \x1b[1mContent\x1b[0m │ \x1b[1mContent\x1b[0m │\n'
                                      '╰─────────┴─────────╯\n')

    no_frame_dark_color_no_bg_show_style_exp_output = (
        no_frame_dark_color_exp_output + '\x1b[3m   lightbulb-pygments\x1b[0m\n')

    frame_title_light_color_exp_output = (
        '╭────────────┬──────────────────────────╮\n'
        '│ \x1b[1mTrue\x1b[0m       │ \x1b[1mSome\x1b[0m \x1b[1mlonger\x1b[0m '
        '\x1b[1mcontent\x1b[0m \x1b[1mhere\x1b[0m │\n'
        '│ \x1b[3m          \x1b[0m │ \x1b[3m                        \x1b[0m │\n'
        '│ \x1b[3mThe title \x1b[0m │ \x1b[3m                        \x1b[0m │\n'
        '│ \x1b[3mof Panel 1\x1b[0m │ \x1b[3m        Panel 2         \x1b[0m │\n'
        '╰────────────┴──────────────────────────╯\n')

    frame_title_light_color_no_bg_show_style_exp_output = (
        frame_title_light_color_exp_output
        + '\x1b[3m            Style: omnipy-selenized-light\x1b[0m\n')

    def _exp_plain_output_for_case_id(case_id: str) -> str:
        match case_id:
            case 'no-frame-dark-color':
                return no_frame_dark_color_exp_output

            case 'no-frame-dark-color-no-bg-show-style':
                return no_frame_dark_color_no_bg_show_style_exp_output

            case 'frame-title-light-color':
                return frame_title_light_color_exp_output

            case 'frame-title-light-color-no-bg-show-style':
                return frame_title_light_color_no_bg_show_style_exp_output

            case 'tiny-cropped-table-dark-color':
                return ('╭┬\n'
                        '╰┴\n')

            case 'tiny-cropped-table-dark-color-no-bg-show-style':
                return ('╭┬\n'
                        '\x1b[3mli\x1b[0m\n')
            case _:
                raise ValueError(f'Unexpected case_id: {case_id}')

    return StylizedPanelOutputExpectations(
        get_output_property=bw_stylized_terminal,
        exp_plain_output_for_case_id=_exp_plain_output_for_case_id,
    )


@pc.case(id='colorized-terminal-output', tags=['expectations', 'layout'])
def case_layout_styling_expectations_colorized_terminal(
    colorized_terminal: Annotated[OutputPropertyType,
                                  pc.fixture]) -> StylizedPanelOutputExpectations:
    def _exp_plain_output_for_case_id(case_id: str) -> str:
        match case_id:
            case 'no-frame-dark-color':
                return (('\x1b[38;2;126;138;161;48;2;29;35;49m╭─────────┬─────────╮\x1b[0m\n'
                         '\x1b[38;2;126;138;161;48;2;29;35;49m│\x1b[0m'
                         '\x1b[38;2;126;138;161;48;2;29;35;49m \x1b[0m'
                         '\x1b[1;34;48;2;29;35;49mPanel_1\x1b[0m'
                         '\x1b[38;2;126;138;161;48;2;29;35;49m \x1b[0m'
                         '\x1b[38;2;126;138;161;48;2;29;35;49m│\x1b[0m'
                         '\x1b[38;2;126;138;161;48;2;29;35;49m \x1b[0m'
                         '\x1b[1;34;48;2;29;35;49mPanel_2\x1b[0m'
                         '\x1b[38;2;126;138;161;48;2;29;35;49m \x1b[0m'
                         '\x1b[38;2;126;138;161;48;2;29;35;49m│\x1b[0m\n'
                         '\x1b[38;2;126;138;161;48;2;29;35;49m│\x1b[0m'
                         '\x1b[38;2;126;138;161;48;2;29;35;49m \x1b[0m'
                         '\x1b[1;34;48;2;29;35;49mContent\x1b[0m'
                         '\x1b[38;2;126;138;161;48;2;29;35;49m \x1b[0m'
                         '\x1b[38;2;126;138;161;48;2;29;35;49m│\x1b[0m'
                         '\x1b[38;2;126;138;161;48;2;29;35;49m \x1b[0m'
                         '\x1b[1;34;48;2;29;35;49mContent\x1b[0m'
                         '\x1b[38;2;126;138;161;48;2;29;35;49m \x1b[0m'
                         '\x1b[38;2;126;138;161;48;2;29;35;49m│\x1b[0m\n'
                         '\x1b[38;2;126;138;161;48;2;29;35;49m╰─────────┴─────────╯\x1b[0m\n'))

            case 'no-frame-dark-color-no-bg-show-style':
                return (('\x1b[38;2;126;138;161m╭─────────┬─────────╮\x1b[0m\n'
                         '\x1b[38;2;126;138;161m│\x1b[0m\x1b[38;2;126;138;161m \x1b[0m'
                         '\x1b[1;34mPanel_1\x1b[0m\x1b[38;2;126;138;161m \x1b[0m'
                         '\x1b[38;2;126;138;161m│\x1b[0m\x1b[38;2;126;138;161m \x1b[0m'
                         '\x1b[1;34mPanel_2\x1b[0m\x1b[38;2;126;138;161m \x1b[0m'
                         '\x1b[38;2;126;138;161m│\x1b[0m\n\x1b[38;2;126;138;161m│\x1b[0m'
                         '\x1b[38;2;126;138;161m \x1b[0m\x1b[1;34mContent\x1b[0m'
                         '\x1b[38;2;126;138;161m \x1b[0m\x1b[38;2;126;138;161m│\x1b[0m'
                         '\x1b[38;2;126;138;161m \x1b[0m\x1b[1;34mContent\x1b[0m'
                         '\x1b[38;2;126;138;161m \x1b[0m\x1b[38;2;126;138;161m│\x1b[0m\n'
                         '\x1b[38;2;126;138;161m╰─────────┴─────────╯\x1b[0m\n'
                         '\x1b[3;38;2;126;138;161m   lightbulb-pygments\x1b[0m\n'))

            case 'frame-title-light-color':
                return ('\x1b[38;2;128;140;138;48;2;251;243;219m'
                        '╭────────────┬──────────────────────────╮\x1b[0m\n'
                        '\x1b[38;2;128;140;138;48;2;251;243;219m│\x1b[0m'
                        '\x1b[38;2;128;140;138;48;2;251;243;219m \x1b[0m'
                        '\x1b[1;34;48;2;251;243;219mTrue\x1b[0m'
                        '\x1b[38;2;128;140;138;48;2;251;243;219m      \x1b[0m'
                        '\x1b[38;2;128;140;138;48;2;251;243;219m \x1b[0m'
                        '\x1b[38;2;128;140;138;48;2;251;243;219m│\x1b[0m'
                        '\x1b[38;2;128;140;138;48;2;251;243;219m \x1b[0m'
                        '\x1b[1;34;48;2;251;243;219mSome\x1b[0m'
                        '\x1b[38;2;128;140;138;48;2;251;243;219m \x1b[0m'
                        '\x1b[1;34;48;2;251;243;219mlonger\x1b[0m'
                        '\x1b[38;2;128;140;138;48;2;251;243;219m \x1b[0m'
                        '\x1b[1;34;48;2;251;243;219mcontent\x1b[0m'
                        '\x1b[38;2;128;140;138;48;2;251;243;219m \x1b[0m'
                        '\x1b[1;34;48;2;251;243;219mhere\x1b[0m'
                        '\x1b[38;2;128;140;138;48;2;251;243;219m \x1b[0m'
                        '\x1b[38;2;128;140;138;48;2;251;243;219m│\x1b[0m\n'
                        '\x1b[38;2;128;140;138;48;2;251;243;219m│\x1b[0m'
                        '\x1b[38;2;128;140;138;48;2;251;243;219m \x1b[0m'
                        '\x1b[3;38;2;167;131;0;48;2;251;243;219m          \x1b[0m'
                        '\x1b[38;2;128;140;138;48;2;251;243;219m \x1b[0m'
                        '\x1b[38;2;128;140;138;48;2;251;243;219m│\x1b[0m'
                        '\x1b[38;2;128;140;138;48;2;251;243;219m \x1b[0m'
                        '\x1b[3;38;2;167;131;0;48;2;251;243;219m                        \x1b[0m'
                        '\x1b[38;2;128;140;138;48;2;251;243;219m \x1b[0m'
                        '\x1b[38;2;128;140;138;48;2;251;243;219m│\x1b[0m\n'
                        '\x1b[38;2;128;140;138;48;2;251;243;219m│\x1b[0m'
                        '\x1b[38;2;128;140;138;48;2;251;243;219m \x1b[0m'
                        '\x1b[3;38;2;167;131;0;48;2;251;243;219mThe title \x1b[0m'
                        '\x1b[38;2;128;140;138;48;2;251;243;219m \x1b[0m'
                        '\x1b[38;2;128;140;138;48;2;251;243;219m│\x1b[0m'
                        '\x1b[38;2;128;140;138;48;2;251;243;219m \x1b[0m'
                        '\x1b[3;38;2;167;131;0;48;2;251;243;219m                        \x1b[0m'
                        '\x1b[38;2;128;140;138;48;2;251;243;219m \x1b[0m'
                        '\x1b[38;2;128;140;138;48;2;251;243;219m│\x1b[0m\n'
                        '\x1b[38;2;128;140;138;48;2;251;243;219m│\x1b[0m'
                        '\x1b[38;2;128;140;138;48;2;251;243;219m \x1b[0m'
                        '\x1b[3;38;2;167;131;0;48;2;251;243;219mof Panel 1\x1b[0m'
                        '\x1b[38;2;128;140;138;48;2;251;243;219m \x1b[0m'
                        '\x1b[38;2;128;140;138;48;2;251;243;219m│\x1b[0m'
                        '\x1b[38;2;128;140;138;48;2;251;243;219m \x1b[0m'
                        '\x1b[3;38;2;167;131;0;48;2;251;243;219m        Panel 2         \x1b[0m'
                        '\x1b[38;2;128;140;138;48;2;251;243;219m \x1b[0m'
                        '\x1b[38;2;128;140;138;48;2;251;243;219m│\x1b[0m\n'
                        '\x1b[38;2;128;140;138;48;2;251;243;219m'
                        '╰────────────┴──────────────────────────╯\x1b[0m\n')

            case 'frame-title-light-color-no-bg-show-style':
                return (
                    '\x1b[38;2;128;140;138m'
                    '╭────────────┬──────────────────────────╮\x1b[0m\n'
                    '\x1b[38;2;128;140;138m│\x1b[0m'
                    '\x1b[38;2;128;140;138m \x1b[0m'
                    '\x1b[1;34mTrue\x1b[0m'
                    '\x1b[38;2;128;140;138m      \x1b[0m'
                    '\x1b[38;2;128;140;138m \x1b[0m'
                    '\x1b[38;2;128;140;138m│\x1b[0m'
                    '\x1b[38;2;128;140;138m \x1b[0m'
                    '\x1b[1;34mSome\x1b[0m'
                    '\x1b[38;2;128;140;138m \x1b[0m'
                    '\x1b[1;34mlonger\x1b[0m'
                    '\x1b[38;2;128;140;138m \x1b[0m'
                    '\x1b[1;34mcontent\x1b[0m'
                    '\x1b[38;2;128;140;138m \x1b[0m'
                    '\x1b[1;34mhere\x1b[0m'
                    '\x1b[38;2;128;140;138m \x1b[0m'
                    '\x1b[38;2;128;140;138m│\x1b[0m\n'
                    '\x1b[38;2;128;140;138m│\x1b[0m'
                    '\x1b[38;2;128;140;138m \x1b[0m'
                    '\x1b[3;38;2;167;131;0m          \x1b[0m'
                    '\x1b[38;2;128;140;138m \x1b[0m'
                    '\x1b[38;2;128;140;138m│\x1b[0m'
                    '\x1b[38;2;128;140;138m \x1b[0m'
                    '\x1b[3;38;2;167;131;0m                        \x1b[0m'
                    '\x1b[38;2;128;140;138m \x1b[0m'
                    '\x1b[38;2;128;140;138m│\x1b[0m\n'
                    '\x1b[38;2;128;140;138m│\x1b[0m'
                    '\x1b[38;2;128;140;138m \x1b[0m'
                    '\x1b[3;38;2;167;131;0mThe title \x1b[0m'
                    '\x1b[38;2;128;140;138m \x1b[0m'
                    '\x1b[38;2;128;140;138m│\x1b[0m'
                    '\x1b[38;2;128;140;138m \x1b[0m'
                    '\x1b[3;38;2;167;131;0m                        \x1b[0m'
                    '\x1b[38;2;128;140;138m \x1b[0m'
                    '\x1b[38;2;128;140;138m│\x1b[0m\n'
                    '\x1b[38;2;128;140;138m│\x1b[0m'
                    '\x1b[38;2;128;140;138m \x1b[0m'
                    '\x1b[3;38;2;167;131;0mof Panel 1\x1b[0m'
                    '\x1b[38;2;128;140;138m \x1b[0m'
                    '\x1b[38;2;128;140;138m│\x1b[0m'
                    '\x1b[38;2;128;140;138m \x1b[0m'
                    '\x1b[3;38;2;167;131;0m        Panel 2         \x1b[0m'
                    '\x1b[38;2;128;140;138m \x1b[0m'
                    '\x1b[38;2;128;140;138m│\x1b[0m\n'
                    '\x1b[38;2;128;140;138m'
                    '╰────────────┴──────────────────────────╯\x1b[0m\n'
                    '\x1b[3;38;2;128;140;138m            Style: omnipy-selenized-light\x1b[0m\n')

            case 'tiny-cropped-table-dark-color':
                return ('\x1b[38;2;126;138;161;48;2;29;35;49m╭┬\x1b[0m\n'
                        '\x1b[38;2;126;138;161;48;2;29;35;49m╰┴\x1b[0m\n')

            case 'tiny-cropped-table-dark-color-no-bg-show-style':
                return ('\x1b[38;2;126;138;161m╭┬\x1b[0m\n'
                        '\x1b[3;38;2;126;138;161mli\x1b[0m\n')

            case _:
                raise ValueError(f'Unexpected case_id: {case_id}')

    return StylizedPanelOutputExpectations(
        get_output_property=colorized_terminal,
        exp_plain_output_for_case_id=_exp_plain_output_for_case_id,
    )


@pc.case(id='plain-html-tag-output', tags=['expectations', 'layout'])
def case_layout_styling_expectations_plain_html_tag(
        plain_html_tag: Annotated[OutputPropertyType,
                                  pc.fixture]) -> StylizedPanelOutputExpectations:
    no_frame_dark_color_exp_output = ('╭─────────┬─────────╮\n'
                                      '│ Panel_1 │ Panel_2 │\n'
                                      '│ Content │ Content │\n'
                                      '╰─────────┴─────────╯')

    no_frame_dark_color_no_bg_show_style_exp_output = (
        no_frame_dark_color_exp_output + '\n'
        '   lightbulb-pygments')

    frame_title_light_color_exp_output = ('╭────────────┬──────────────────────────╮\n'
                                          '│ True       │ Some longer content here │\n'
                                          '│            │                          │\n'
                                          '│ The title  │                          │\n'
                                          '│ of Panel 1 │         Panel 2          │\n'
                                          '╰────────────┴──────────────────────────╯')

    frame_title_light_color_no_bg_show_style_exp_output = (
        frame_title_light_color_exp_output + '\n'
        '            Style: omnipy-selenized-light')

    tiny_cropped_table_dark_color_exp_output = ('╭┬\n'
                                                '╰┴')

    tiny_cropped_table_dark_color_no_bg_show_style_exp_output = ('╭┬\n'
                                                                 'li')

    def _exp_plain_output_for_case_id(case_id: str) -> str:
        match case_id:
            case 'no-frame-dark-color':
                return fill_html_tag_template(
                    data=no_frame_dark_color_exp_output,
                    case_id=case_id,
                )

            case 'no-frame-dark-color-no-bg-show-style':
                return fill_html_tag_template(
                    data=no_frame_dark_color_no_bg_show_style_exp_output,
                    case_id=case_id,
                )

            case 'frame-title-light-color':
                return fill_html_tag_template(
                    data=frame_title_light_color_exp_output,
                    case_id=case_id,
                )

            case 'frame-title-light-color-no-bg-show-style':
                return fill_html_tag_template(
                    data=frame_title_light_color_no_bg_show_style_exp_output,
                    case_id=case_id,
                )

            case 'tiny-cropped-table-dark-color':
                return fill_html_tag_template(
                    data=tiny_cropped_table_dark_color_exp_output,
                    case_id=case_id,
                )

            case 'tiny-cropped-table-dark-color-no-bg-show-style':
                return fill_html_tag_template(
                    data=tiny_cropped_table_dark_color_no_bg_show_style_exp_output,
                    case_id=case_id,
                )

            case _:
                raise ValueError(f'Unexpected case_id: {case_id}')

    return StylizedPanelOutputExpectations(
        get_output_property=plain_html_tag,
        exp_plain_output_for_case_id=_exp_plain_output_for_case_id,
    )


@pc.case(id='bw-stylized-html-tag-output', tags=['expectations', 'layout'])
def case_layout_styling_expectations_bw_stylized_html_tag(
    bw_stylized_html_tag: Annotated[OutputPropertyType,
                                    pc.fixture]) -> StylizedPanelOutputExpectations:
    no_frame_dark_color_exp_output = ('╭─────────┬─────────╮\n'
                                      '│ <span style="font-weight: bold">Panel_1</span> '
                                      '│ <span style="font-weight: bold">Panel_2</span> │\n'
                                      '│ <span style="font-weight: bold">Content</span> '
                                      '│ <span style="font-weight: bold">Content</span> │\n'
                                      '╰─────────┴─────────╯')

    no_frame_dark_color_no_bg_show_style_exp_output = (
        no_frame_dark_color_exp_output + '\n'
        '<span style="font-style: italic">   lightbulb-pygments</span>')

    frame_title_light_color_exp_output = (
        '╭────────────┬──────────────────────────╮\n'
        '│ <span style="font-weight: bold">True</span>       │ '
        '<span style="font-weight: bold">Some</span> '
        '<span style="font-weight: bold">longer</span> '
        '<span style="font-weight: bold">content</span> '
        '<span style="font-weight: bold">here</span> │\n'
        '│ <span style="font-style: italic">          </span> │ '
        '<span style="font-style: italic">                        </span> │\n'
        '│ <span style="font-style: italic">The title </span> │ '
        '<span style="font-style: italic">                        </span> │\n'
        '│ <span style="font-style: italic">of Panel 1</span> │ '
        '<span style="font-style: italic">        Panel 2         </span> │\n'
        '╰────────────┴──────────────────────────╯')

    frame_title_light_color_no_bg_show_style_exp_output = (
        frame_title_light_color_exp_output + '\n'
        '<span style="font-style: italic">            Style: omnipy-selenized-light</span>')

    tiny_cropped_table_dark_color_exp_output = ('╭┬\n'
                                                '╰┴')

    tiny_cropped_table_dark_color_no_bg_show_style_exp_output = (
        '╭┬\n'
        '<span style="font-style: italic">li</span>')

    def _exp_plain_output_for_case_id(case_id: str) -> str:
        match case_id:
            case 'no-frame-dark-color':
                return fill_html_tag_template(
                    data=no_frame_dark_color_exp_output,
                    case_id=case_id,
                )

            case 'no-frame-dark-color-no-bg-show-style':
                return fill_html_tag_template(
                    data=no_frame_dark_color_no_bg_show_style_exp_output,
                    case_id=case_id,
                )

            case 'frame-title-light-color':
                return fill_html_tag_template(
                    data=frame_title_light_color_exp_output,
                    case_id=case_id,
                )

            case 'frame-title-light-color-no-bg-show-style':
                return fill_html_tag_template(
                    data=frame_title_light_color_no_bg_show_style_exp_output,
                    case_id=case_id,
                )

            case 'tiny-cropped-table-dark-color':
                return fill_html_tag_template(
                    data=tiny_cropped_table_dark_color_exp_output,
                    case_id=case_id,
                )

            case 'tiny-cropped-table-dark-color-no-bg-show-style':
                return fill_html_tag_template(
                    data=tiny_cropped_table_dark_color_no_bg_show_style_exp_output,
                    case_id=case_id,
                )

            case _:
                raise ValueError(f'Unexpected case_id: {case_id}')

    return StylizedPanelOutputExpectations(
        get_output_property=bw_stylized_html_tag,
        exp_plain_output_for_case_id=_exp_plain_output_for_case_id,
    )


@pc.case(id='colorized-html-tag-output', tags=['expectations', 'layout'])
def case_layout_styling_expectations_colorized_html_tag(
    colorized_html_tag: Annotated[OutputPropertyType,
                                  pc.fixture]) -> StylizedPanelOutputExpectations:
    def _exp_plain_output_for_case_id(case_id: str) -> str:

        lightbulb_dark_color_style_with_bg = 'color: #d4d2c8; background-color: #1d2331; '
        lightbulb_dark_color_style_no_bg = 'color: #d4d2c8; '

        omnipy_selenized_light_color_style_with_bg = 'color: #53676d; background-color: #fbf3db; '
        omnipy_selenized_light_color_style_no_bg = 'color: #53676d; '

        match case_id:
            case 'no-frame-dark-color':
                return fill_html_tag_template(
                    data=('<span style="color: #7e8aa1; text-decoration-color: #7e8aa1; '
                          'background-color: #1d2331">╭─────────┬─────────╮</span>\n'
                          '<span style="color: #7e8aa1; text-decoration-color: #7e8aa1; '
                          'background-color: #1d2331">│ </span>'
                          '<span style="color: #000080; text-decoration-color: #000080; '
                          'background-color: #1d2331; font-weight: bold">Panel_1</span>'
                          '<span style="color: #7e8aa1; text-decoration-color: #7e8aa1; '
                          'background-color: #1d2331"> │ </span>'
                          '<span style="color: #000080; text-decoration-color: #000080; '
                          'background-color: #1d2331; font-weight: bold">Panel_2</span>'
                          '<span style="color: #7e8aa1; text-decoration-color: #7e8aa1; '
                          'background-color: #1d2331"> │</span>\n'
                          '<span style="color: #7e8aa1; text-decoration-color: #7e8aa1; '
                          'background-color: #1d2331">│ </span>'
                          '<span style="color: #000080; text-decoration-color: #000080; '
                          'background-color: #1d2331; font-weight: bold">Content</span>'
                          '<span style="color: #7e8aa1; text-decoration-color: #7e8aa1; '
                          'background-color: #1d2331"> │ </span>'
                          '<span style="color: #000080; text-decoration-color: #000080; '
                          'background-color: #1d2331; font-weight: bold">Content</span>'
                          '<span style="color: #7e8aa1; text-decoration-color: #7e8aa1; '
                          'background-color: #1d2331"> │</span>\n'
                          '<span style="color: #7e8aa1; text-decoration-color: #7e8aa1; '
                          'background-color: #1d2331">╰─────────┴─────────╯</span>'),
                    color_style=lightbulb_dark_color_style_with_bg,
                    case_id=case_id,
                )

            case 'no-frame-dark-color-no-bg-show-style':
                return fill_html_tag_template(
                    data=('<span style="color: #7e8aa1; text-decoration-color: #7e8aa1">'
                          '╭─────────┬─────────╮</span>\n'
                          '<span style="color: #7e8aa1; text-decoration-color: #7e8aa1">│ </span>'
                          '<span style="color: #000080; text-decoration-color: #000080; '
                          'font-weight: bold">Panel_1</span>'
                          '<span style="color: #7e8aa1; text-decoration-color: #7e8aa1"> │ </span>'
                          '<span style="color: #000080; text-decoration-color: #000080; '
                          'font-weight: bold">Panel_2</span>'
                          '<span style="color: #7e8aa1; text-decoration-color: #7e8aa1"> │</span>\n'
                          '<span style="color: #7e8aa1; text-decoration-color: #7e8aa1">│ </span>'
                          '<span style="color: #000080; text-decoration-color: #000080; '
                          'font-weight: bold">Content</span>'
                          '<span style="color: #7e8aa1; text-decoration-color: #7e8aa1"> │ </span>'
                          '<span style="color: #000080; text-decoration-color: #000080; '
                          'font-weight: bold">Content</span>'
                          '<span style="color: #7e8aa1; text-decoration-color: #7e8aa1"> │</span>\n'
                          '<span style="color: #7e8aa1; text-decoration-color: #7e8aa1">'
                          '╰─────────┴─────────╯</span>\n'
                          '<span style="color: #7e8aa1; text-decoration-color: #7e8aa1; '
                          'font-style: italic">   lightbulb-pygments</span>'),
                    color_style=lightbulb_dark_color_style_no_bg,
                    case_id=case_id,
                )

            case 'frame-title-light-color':
                return fill_html_tag_template(
                    data=('<span style="color: #808c8a; text-decoration-color: #808c8a; '
                          'background-color: #fbf3db">'
                          '╭────────────┬──────────────────────────╮</span>\n'
                          '<span style="color: #808c8a; text-decoration-color: #808c8a; '
                          'background-color: #fbf3db">│ </span>'
                          '<span style="color: #000080; text-decoration-color: #000080; '
                          'background-color: #fbf3db; font-weight: bold">True</span>'
                          '<span style="color: #808c8a; text-decoration-color: #808c8a; '
                          'background-color: #fbf3db">       │ </span>'
                          '<span style="color: #000080; text-decoration-color: #000080; '
                          'background-color: #fbf3db; font-weight: bold">Some</span>'
                          '<span style="color: #808c8a; text-decoration-color: #808c8a; '
                          'background-color: #fbf3db"> </span>'
                          '<span style="color: #000080; text-decoration-color: #000080; '
                          'background-color: #fbf3db; font-weight: bold">longer</span>'
                          '<span style="color: #808c8a; text-decoration-color: #808c8a; '
                          'background-color: #fbf3db"> </span>'
                          '<span style="color: #000080; text-decoration-color: #000080; '
                          'background-color: #fbf3db; font-weight: bold">content</span>'
                          '<span style="color: #808c8a; text-decoration-color: #808c8a; '
                          'background-color: #fbf3db"> </span>'
                          '<span style="color: #000080; text-decoration-color: #000080; '
                          'background-color: #fbf3db; font-weight: bold">here</span>'
                          '<span style="color: #808c8a; text-decoration-color: #808c8a; '
                          'background-color: #fbf3db"> │</span>\n'
                          '<span style="color: #808c8a; text-decoration-color: #808c8a; '
                          'background-color: #fbf3db">│ </span>'
                          '<span style="color: #a78300; text-decoration-color: #a78300; '
                          'background-color: #fbf3db; font-style: italic">          </span>'
                          '<span style="color: #808c8a; text-decoration-color: #808c8a; '
                          'background-color: #fbf3db"> │ </span>'
                          '<span style="color: #a78300; text-decoration-color: #a78300; '
                          'background-color: #fbf3db; font-style: italic">                        '
                          '</span>'
                          '<span style="color: #808c8a; text-decoration-color: #808c8a; '
                          'background-color: #fbf3db"> │</span>\n'
                          '<span style="color: #808c8a; text-decoration-color: #808c8a; '
                          'background-color: #fbf3db">│ </span>'
                          '<span style="color: #a78300; text-decoration-color: #a78300; '
                          'background-color: #fbf3db; font-style: italic">The title </span>'
                          '<span style="color: #808c8a; text-decoration-color: #808c8a; '
                          'background-color: #fbf3db"> │ </span>'
                          '<span style="color: #a78300; text-decoration-color: #a78300; '
                          'background-color: #fbf3db; font-style: italic">                        '
                          '</span>'
                          '<span style="color: #808c8a; text-decoration-color: #808c8a; '
                          'background-color: #fbf3db"> │</span>\n'
                          '<span style="color: #808c8a; text-decoration-color: #808c8a; '
                          'background-color: #fbf3db">│ </span>'
                          '<span style="color: #a78300; text-decoration-color: #a78300; '
                          'background-color: #fbf3db; font-style: italic">of Panel 1</span>'
                          '<span style="color: #808c8a; text-decoration-color: #808c8a; '
                          'background-color: #fbf3db"> │ </span>'
                          '<span style="color: #a78300; text-decoration-color: #a78300; '
                          'background-color: #fbf3db; font-style: italic">        Panel 2         '
                          '</span>'
                          '<span style="color: #808c8a; text-decoration-color: #808c8a; '
                          'background-color: #fbf3db"> │</span>\n'
                          '<span style="color: #808c8a; text-decoration-color: #808c8a; '
                          'background-color: #fbf3db">'
                          '╰────────────┴──────────────────────────╯</span>'),
                    color_style=omnipy_selenized_light_color_style_with_bg,
                    case_id=case_id,
                )

            case 'frame-title-light-color-no-bg-show-style':
                return fill_html_tag_template(
                    data=('<span style="color: #808c8a; text-decoration-color: #808c8a">'
                          '╭────────────┬──────────────────────────╮</span>\n'
                          '<span style="color: #808c8a; text-decoration-color: #808c8a">│ </span>'
                          '<span style="color: #000080; text-decoration-color: #000080; '
                          'font-weight: bold">True</span>'
                          '<span style="color: #808c8a; text-decoration-color: #808c8a">       │ '
                          '</span>'
                          '<span style="color: #000080; text-decoration-color: #000080; '
                          'font-weight: bold">Some</span>'
                          '<span style="color: #808c8a; text-decoration-color: #808c8a"> </span>'
                          '<span style="color: #000080; text-decoration-color: #000080; '
                          'font-weight: bold">longer</span>'
                          '<span style="color: #808c8a; text-decoration-color: #808c8a"> </span>'
                          '<span style="color: #000080; text-decoration-color: #000080; '
                          'font-weight: bold">content</span>'
                          '<span style="color: #808c8a; text-decoration-color: #808c8a"> </span>'
                          '<span style="color: #000080; text-decoration-color: #000080; '
                          'font-weight: bold">here</span>'
                          '<span style="color: #808c8a; text-decoration-color: #808c8a"> │</span>\n'
                          '<span style="color: #808c8a; text-decoration-color: #808c8a">│ </span>'
                          '<span style="color: #a78300; text-decoration-color: #a78300; '
                          'font-style: italic">          </span>'
                          '<span style="color: #808c8a; text-decoration-color: #808c8a"> │ </span>'
                          '<span style="color: #a78300; text-decoration-color: #a78300; '
                          'font-style: italic">                        </span>'
                          '<span style="color: #808c8a; text-decoration-color: #808c8a"> │</span>\n'
                          '<span style="color: #808c8a; text-decoration-color: #808c8a">│ </span>'
                          '<span style="color: #a78300; text-decoration-color: #a78300; '
                          'font-style: italic">The title </span>'
                          '<span style="color: #808c8a; text-decoration-color: #808c8a"> │ </span>'
                          '<span style="color: #a78300; text-decoration-color: #a78300; '
                          'font-style: italic">                        </span>'
                          '<span style="color: #808c8a; text-decoration-color: #808c8a"> │</span>\n'
                          '<span style="color: #808c8a; text-decoration-color: #808c8a">│ </span>'
                          '<span style="color: #a78300; text-decoration-color: #a78300; '
                          'font-style: italic">of Panel 1</span>'
                          '<span style="color: #808c8a; text-decoration-color: #808c8a"> │ </span>'
                          '<span style="color: #a78300; text-decoration-color: #a78300; '
                          'font-style: italic">        Panel 2         </span>'
                          '<span style="color: #808c8a; text-decoration-color: #808c8a"> │</span>\n'
                          '<span style="color: #808c8a; text-decoration-color: #808c8a">'
                          '╰────────────┴──────────────────────────╯</span>\n'
                          '<span style="color: #808c8a; text-decoration-color: #808c8a; '
                          'font-style: italic">            Style: omnipy-selenized-light</span>'),
                    color_style=omnipy_selenized_light_color_style_no_bg,
                    case_id=case_id,
                )

            case 'tiny-cropped-table-dark-color':
                return fill_html_tag_template(
                    data=('<span style="color: #7e8aa1; text-decoration-color: #7e8aa1; '
                          'background-color: #1d2331">╭┬</span>\n'
                          '<span style="color: #7e8aa1; text-decoration-color: #7e8aa1; '
                          'background-color: #1d2331">╰┴</span>'),
                    color_style=lightbulb_dark_color_style_with_bg,
                    case_id=case_id,
                )

            case 'tiny-cropped-table-dark-color-no-bg-show-style':
                return fill_html_tag_template(
                    data=('<span style="color: #7e8aa1; text-decoration-color: #7e8aa1">╭┬</span>\n'
                          '<span style="color: #7e8aa1; text-decoration-color: #7e8aa1; '
                          'font-style: italic">li</span>'),
                    color_style=lightbulb_dark_color_style_no_bg,
                    case_id=case_id,
                )

            case _:
                raise ValueError(f'Unexpected case_id: {case_id}')

    return StylizedPanelOutputExpectations(
        get_output_property=colorized_html_tag,
        exp_plain_output_for_case_id=_exp_plain_output_for_case_id,
    )


@pc.case(id='plain-html-page-output', tags=['expectations', 'layout'])
def case_layout_styling_expectations_plain_html_page(
        plain_html_page: Annotated[OutputPropertyType,
                                   pc.fixture]) -> StylizedPanelOutputExpectations:
    light_body_style = f"""
      body {{
        color: #000000;
        background-color: #ffffff;
        {FONT_RENDER_BODY_STYLE}
      }}"""

    no_frame_dark_color_exp_output = ('╭─────────┬─────────╮\n'
                                      '│ Panel_1 │ Panel_2 │\n'
                                      '│ Content │ Content │\n'
                                      '╰─────────┴─────────╯')

    no_frame_dark_color_no_bg_show_style_exp_output = (
        no_frame_dark_color_exp_output + '\n'
        '   lightbulb-pygments')

    frame_title_light_color_exp_output = ('╭────────────┬──────────────────────────╮\n'
                                          '│ True       │ Some longer content here │\n'
                                          '│            │                          │\n'
                                          '│ The title  │                          │\n'
                                          '│ of Panel 1 │         Panel 2          │\n'
                                          '╰────────────┴──────────────────────────╯')

    frame_title_light_color_no_bg_show_style_exp_output = (
        frame_title_light_color_exp_output + '\n'
        '            Style: omnipy-selenized-light')

    tiny_cropped_table_dark_color_exp_output = ('╭┬\n'
                                                '╰┴')

    tiny_cropped_table_dark_color_no_bg_show_style_exp_output = ('╭┬\n'
                                                                 'li')

    def _exp_plain_output_for_case_id(case_id: str) -> str:
        match case_id:
            case 'no-frame-dark-color':
                return fill_html_page_template(
                    style=light_body_style,
                    data=no_frame_dark_color_exp_output,
                    case_id=case_id,
                )

            case 'no-frame-dark-color-no-bg-show-style':
                return fill_html_page_template(
                    style=light_body_style,
                    data=no_frame_dark_color_no_bg_show_style_exp_output,
                    case_id=case_id,
                )

            case 'frame-title-light-color':
                return fill_html_page_template(
                    style=light_body_style,
                    data=frame_title_light_color_exp_output,
                    case_id=case_id,
                )

            case 'frame-title-light-color-no-bg-show-style':
                return fill_html_page_template(
                    style=light_body_style,
                    data=frame_title_light_color_no_bg_show_style_exp_output,
                    case_id=case_id,
                )

            case 'tiny-cropped-table-dark-color':
                return fill_html_page_template(
                    style=light_body_style,
                    data=tiny_cropped_table_dark_color_exp_output,
                    case_id=case_id,
                )

            case 'tiny-cropped-table-dark-color-no-bg-show-style':
                return fill_html_page_template(
                    style=light_body_style,
                    data=tiny_cropped_table_dark_color_no_bg_show_style_exp_output,
                    case_id=case_id,
                )

            case _:
                raise ValueError(f'Unexpected case_id: {case_id}')

    return StylizedPanelOutputExpectations(
        get_output_property=plain_html_page,
        exp_plain_output_for_case_id=_exp_plain_output_for_case_id,
    )


@pc.case(id='bw-stylized-html-page-output', tags=['expectations', 'layout'])
def case_layout_styling_expectations_bw_stylized_html_page(
    bw_stylized_html_page: Annotated[OutputPropertyType, pc.fixture]
) -> StylizedPanelOutputExpectations:

    bold_style = '\n'.join([
        '.r2 {font-weight: bold}',
    ])

    bold_and_italic_style = '\n'.join([
        '.r2 {font-weight: bold}',
        '.r3 {font-style: italic}',
    ])

    italic_style = '\n'.join([
        '.r2 {font-style: italic}',
    ])

    light_body_style = f"""
      body {{
        color: #000000;
        background-color: #ffffff;
        {FONT_RENDER_BODY_STYLE}
      }}"""

    no_frame_dark_color_exp_output = ('<span class="r1">╭─────────┬─────────╮</span>\n'
                                      '<span class="r1">│ </span><span class="r2">Panel_1</span>'
                                      '<span class="r1"> │ </span><span class="r2">Panel_2</span>'
                                      '<span class="r1"> │</span>\n'
                                      '<span class="r1">│ </span><span class="r2">Content</span>'
                                      '<span class="r1"> │ </span><span class="r2">Content</span>'
                                      '<span class="r1"> │</span>\n'
                                      '<span class="r1">╰─────────┴─────────╯</span>')

    no_frame_dark_color_no_bg_show_style_exp_output = (
        no_frame_dark_color_exp_output + '\n'
        '<span class="r3">   lightbulb-pygments</span>')

    frame_title_light_color_exp_output = (
        '<span class="r1">╭────────────┬──────────────────────────╮</span>\n'
        '<span class="r1">│ </span><span class="r2">True</span>'
        '<span class="r1">       │ </span><span class="r2">Some</span>'
        '<span class="r1"> </span><span class="r2">longer</span>'
        '<span class="r1"> </span><span class="r2">content</span>'
        '<span class="r1"> </span><span class="r2">here</span>'
        '<span class="r1"> │</span>\n'
        '<span class="r1">│ </span><span class="r3">          </span>'
        '<span class="r1"> │ </span>'
        '<span class="r3">                        </span>'
        '<span class="r1"> │</span>\n'
        '<span class="r1">│ </span><span class="r3">The title </span>'
        '<span class="r1"> │ </span>'
        '<span class="r3">                        </span>'
        '<span class="r1"> │</span>\n'
        '<span class="r1">│ </span><span class="r3">of Panel 1</span>'
        '<span class="r1"> │ </span>'
        '<span class="r3">        Panel 2         </span>'
        '<span class="r1"> │</span>\n'
        '<span class="r1">╰────────────┴──────────────────────────╯</span>')

    frame_title_light_color_no_bg_show_style_exp_output = (
        frame_title_light_color_exp_output + '\n'
        '<span class="r3">            Style: omnipy-selenized-light</span>')

    tiny_cropped_table_dark_color_exp_output = ('<span class="r1">╭┬</span>\n'
                                                '<span class="r1">╰┴</span>')

    tiny_cropped_table_dark_color_no_bg_show_style_exp_output = ('<span class="r1">╭┬</span>\n'
                                                                 '<span class="r2">li</span>')

    def _exp_plain_output_for_case_id(case_id: str) -> str:
        match case_id:
            case 'no-frame-dark-color':
                return fill_html_page_template(
                    style=bold_style + light_body_style,
                    data=no_frame_dark_color_exp_output,
                    case_id=case_id,
                )

            case 'no-frame-dark-color-no-bg-show-style':
                return fill_html_page_template(
                    style=bold_and_italic_style + light_body_style,
                    data=no_frame_dark_color_no_bg_show_style_exp_output,
                    case_id=case_id,
                )

            case 'frame-title-light-color':
                return fill_html_page_template(
                    style=bold_and_italic_style + light_body_style,
                    data=frame_title_light_color_exp_output,
                    case_id=case_id,
                )

            case 'frame-title-light-color-no-bg-show-style':
                return fill_html_page_template(
                    style=bold_and_italic_style + light_body_style,
                    data=frame_title_light_color_no_bg_show_style_exp_output,
                    case_id=case_id,
                )

            case 'tiny-cropped-table-dark-color':
                return fill_html_page_template(
                    style=light_body_style,
                    data=tiny_cropped_table_dark_color_exp_output,
                    case_id=case_id,
                )

            case 'tiny-cropped-table-dark-color-no-bg-show-style':
                return fill_html_page_template(
                    style=italic_style + light_body_style,
                    data=tiny_cropped_table_dark_color_no_bg_show_style_exp_output,
                    case_id=case_id,
                )

            case _:
                raise ValueError(f'Unexpected case_id: {case_id}')

    return StylizedPanelOutputExpectations(
        get_output_property=bw_stylized_html_page,
        exp_plain_output_for_case_id=_exp_plain_output_for_case_id,
    )


@pc.case(id='colorized-html-page-output', tags=['expectations', 'layout'])
def case_layout_styling_expectations_colorized_html_page(
    colorized_html_page: Annotated[OutputPropertyType,
                                   pc.fixture]) -> StylizedPanelOutputExpectations:
    lightbulb_dark_style_with_bg = (
        '.r1 {color: #7e8aa1; text-decoration-color: #7e8aa1; background-color: #1d2331}')

    lightbulb_dark_bold_style_with_bg = (
        '\n.r2 {color: #000080; text-decoration-color: #000080; background-color: #1d2331; '
        'font-weight: bold}')

    lightbulb_dark_style_no_bg = ('.r1 {color: #7e8aa1; text-decoration-color: #7e8aa1}')

    lightbulb_dark_style_no_bg_show_style_bold_italic_extra = (
        '\n.r2 {color: #000080; text-decoration-color: #000080; font-weight: bold}'
        '\n.r3 {color: #7e8aa1; text-decoration-color: #7e8aa1; font-style: italic}')

    lightbulb_dark_style_no_bg_show_style_italic_extra = (
        '\n.r2 {color: #7e8aa1; text-decoration-color: #7e8aa1; font-style: italic}')

    lightbulb_dark_body_style_with_bg = f"""
      body {{
        color: #d4d2c8;
        background-color: #1d2331;
        {FONT_RENDER_BODY_STYLE}
      }}"""

    lightbulb_dark_body_style_no_bg = f"""
      body {{
        color: #d4d2c8;
        background-color: #000000;
        {FONT_RENDER_BODY_STYLE}
      }}"""

    omnipy_selenized_light_style_with_bg = '\n'.join([
        '.r1 {color: #808c8a; text-decoration-color: #808c8a; background-color: #fbf3db}',
        '.r2 {color: #000080; text-decoration-color: #000080; background-color: #fbf3db; '
        'font-weight: bold}',
        '.r3 {color: #a78300; text-decoration-color: #a78300; background-color: #fbf3db; '
        'font-style: italic}',
    ])

    omnipy_selenized_light_style_no_bg_show_style = '\n'.join([
        '.r1 {color: #808c8a; text-decoration-color: #808c8a}',
        '.r2 {color: #000080; text-decoration-color: #000080; font-weight: bold}',
        '.r3 {color: #a78300; text-decoration-color: #a78300; font-style: italic}',
        '.r4 {color: #808c8a; text-decoration-color: #808c8a; font-style: italic}',
    ])

    omnipy_selenized_light_body_style_with_bg = f"""
      body {{
        color: #53676d;
        background-color: #fbf3db;
        {FONT_RENDER_BODY_STYLE}
      }}"""

    omnipy_selenized_light_body_style_no_bg = f"""
      body {{
        color: #53676d;
        background-color: #ffffff;
        {FONT_RENDER_BODY_STYLE}
      }}"""

    no_frame_dark_color_exp_output = ('<span class="r1">╭─────────┬─────────╮</span>\n'
                                      '<span class="r1">│ </span><span class="r2">Panel_1</span>'
                                      '<span class="r1"> │ </span><span class="r2">Panel_2</span>'
                                      '<span class="r1"> │</span>\n'
                                      '<span class="r1">│ </span><span class="r2">Content</span>'
                                      '<span class="r1"> │ </span><span class="r2">Content</span>'
                                      '<span class="r1"> │</span>\n'
                                      '<span class="r1">╰─────────┴─────────╯</span>')

    no_frame_dark_color_no_bg_show_style_exp_output = (
        no_frame_dark_color_exp_output + '\n<span class="r3">   lightbulb-pygments</span>')

    frame_title_light_color_exp_output = (
        '<span class="r1">╭────────────┬──────────────────────────╮</span>\n'
        '<span class="r1">│ </span><span class="r2">True</span>'
        '<span class="r1">       │ </span><span class="r2">Some</span>'
        '<span class="r1"> </span><span class="r2">longer</span>'
        '<span class="r1"> </span><span class="r2">content</span>'
        '<span class="r1"> </span><span class="r2">here</span>'
        '<span class="r1"> │</span>\n'
        '<span class="r1">│ </span><span class="r3">          </span>'
        '<span class="r1"> │ </span><span class="r3">                        </span>'
        '<span class="r1"> │</span>\n'
        '<span class="r1">│ </span><span class="r3">The title </span>'
        '<span class="r1"> │ </span><span class="r3">                        </span>'
        '<span class="r1"> │</span>\n'
        '<span class="r1">│ </span><span class="r3">of Panel 1</span>'
        '<span class="r1"> │ </span><span class="r3">        Panel 2         </span>'
        '<span class="r1"> │</span>\n'
        '<span class="r1">╰────────────┴──────────────────────────╯</span>')

    frame_title_light_color_no_bg_show_style_exp_output = (
        frame_title_light_color_exp_output
        + '\n<span class="r4">            Style: omnipy-selenized-light</span>')

    tiny_cropped_table_dark_color_exp_output = ('<span class="r1">╭┬</span>\n'
                                                '<span class="r1">╰┴</span>')

    tiny_cropped_table_dark_color_no_bg_show_style_exp_output = ('<span class="r1">╭┬</span>\n'
                                                                 '<span class="r2">li</span>')

    def _exp_plain_output_for_case_id(case_id: str) -> str:
        match case_id:
            case 'no-frame-dark-color':
                return fill_html_page_template(
                    style=(lightbulb_dark_style_with_bg + lightbulb_dark_bold_style_with_bg
                           + lightbulb_dark_body_style_with_bg),
                    data=no_frame_dark_color_exp_output,
                )

            case 'no-frame-dark-color-no-bg-show-style':
                return fill_html_page_template(
                    style=(lightbulb_dark_style_no_bg
                           + lightbulb_dark_style_no_bg_show_style_bold_italic_extra
                           + lightbulb_dark_body_style_no_bg),
                    data=no_frame_dark_color_no_bg_show_style_exp_output,
                )

            case 'frame-title-light-color':
                return fill_html_page_template(
                    style=(omnipy_selenized_light_style_with_bg
                           + omnipy_selenized_light_body_style_with_bg),
                    data=frame_title_light_color_exp_output,
                    case_id=case_id,
                )

            case 'frame-title-light-color-no-bg-show-style':
                return fill_html_page_template(
                    style=(omnipy_selenized_light_style_no_bg_show_style
                           + omnipy_selenized_light_body_style_no_bg),
                    data=frame_title_light_color_no_bg_show_style_exp_output,
                    case_id=case_id,
                )

            case 'tiny-cropped-table-dark-color':
                return fill_html_page_template(
                    style=lightbulb_dark_style_with_bg + lightbulb_dark_body_style_with_bg,
                    data=tiny_cropped_table_dark_color_exp_output,
                    case_id=case_id,
                )

            case 'tiny-cropped-table-dark-color-no-bg-show-style':
                return fill_html_page_template(
                    style=(lightbulb_dark_style_no_bg
                           + lightbulb_dark_style_no_bg_show_style_italic_extra
                           + lightbulb_dark_body_style_no_bg),
                    data=tiny_cropped_table_dark_color_no_bg_show_style_exp_output,
                    case_id=case_id,
                )

            case _:
                raise ValueError(f'Unexpected case_id: {case_id}')

    return StylizedPanelOutputExpectations(
        get_output_property=colorized_html_page,
        exp_plain_output_for_case_id=_exp_plain_output_for_case_id,
    )
