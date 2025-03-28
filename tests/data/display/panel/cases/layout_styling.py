from textwrap import dedent
from typing import Annotated

import pytest_cases as pc

from data.display.helpers.classes import MockPanel
from data.display.panel.cases.text_styling import _fill_html_page_template, _fill_html_tag_template
from omnipy.data._display.config import (ConsoleColorSystem,
                                         DarkHighContrastColorStyles,
                                         OutputConfig)
from omnipy.data._display.dimensions import Dimensions
from omnipy.data._display.frame import Frame
from omnipy.data._display.layout import Layout

from ..helpers import (OutputPropertyType,
                       PanelOutputPropertyExpectations,
                       PanelOutputTestCase,
                       PanelOutputTestCaseSetup)


@pc.parametrize(
    'frame, expected_within_frame_width, expected_within_frame_height', (
        (None, None, None),
        (Frame(Dimensions(width=15, height=5)), True, True),
    ),
    ids=('no_frame', 'larger_frame'))
@pc.case(id='single_panel', tags=['grids_and_frames', 'layout_styling'])
def case_layout_styling_single_panel_no_frame(
    frame: Frame | None,
    output_format_accessor: Annotated[OutputPropertyType, pc.fixture],
    expected_within_frame_width: bool | None,
    expected_within_frame_height: bool | None,
) -> PanelOutputTestCase[Layout]:
    return PanelOutputTestCase(
        content=Layout({'panel': MockPanel(content='Some Content')}),
        frame=frame,
        config=None,
        get_output_property=output_format_accessor,
        expected_output=('╭─────────╮\n'
                         '│ Some    │\n'
                         '│ Content │\n'
                         '╰─────────╯\n'),
        expected_dims_width=11,
        expected_dims_height=4,
        expected_within_frame_width=expected_within_frame_width,
        expected_within_frame_height=expected_within_frame_height,
    )


#
# @pc.case(id='single_panel', tags=['grids_and_frames', 'layout_styling'])
# def case_layout_styling_single_panel_smaller_frame(
#     output_format_accessor: Annotated[OutputPropertyType, pc.fixture],) -> PanelOutputTestCase:
#     return PanelOutputTestCase(
#         content=Layout({'panel': MockPanel(content='Some Content')}),
#         frame=Frame(Dimensions(width=10, height=3)),
#         config=None,
#         get_output_property=output_format_accessor,
#         expected_output=('╭─────────╮\n'
#                          '│ Some    │\n'
#                          '│ Content │\n'
#                          '╰─────────╯\n'),
#         expected_dims_width=11,
#         expected_dims_height=4,
#         expected_within_frame_width=True,
#         expected_within_frame_height=True,
#     )


@pc.parametrize('transparent_background', [False, True])
@pc.case(id='no-frame-dark-color', tags=['setup', 'layout_styling'])
def case_layout_styling_setup_no_frame_or_configs(
        transparent_background: bool) -> PanelOutputTestCaseSetup[Layout]:
    # Create a simple layout with mock panels
    layout = Layout()
    layout['first'] = MockPanel(content='Panel_1 Content')
    layout['second'] = MockPanel(content='Panel_2 Content')

    # Create stylized output with default config (should use Table grid)
    return PanelOutputTestCaseSetup(
        case_id='no-frame-dark-color' + ('-no-bg' if transparent_background else ''),
        content=layout,
        config=OutputConfig(
            console_color_system=ConsoleColorSystem.ANSI_RGB,
            color_style=DarkHighContrastColorStyles.LIGHTBULB,
            transparent_background=transparent_background),
    )


@pc.case(id='plain-terminal-output', tags=['expectations', 'layout_styling'])
def case_layout_styling_expectations_plain_terminal(
        plain_terminal: Annotated[OutputPropertyType,
                                  pc.fixture]) -> PanelOutputPropertyExpectations:
    def _expected_output_for_case_id(case_id: str) -> str:
        match case_id:
            case 'no-frame-dark-color' \
                 | 'no-frame-dark-color-no-bg':
                return dedent("""\
                    ╭─────────┬─────────╮
                    │ Panel_1 │ Panel_2 │
                    │ Content │ Content │
                    ╰─────────┴─────────╯
                    """)
            case _:
                raise ValueError(f'Unexpected case_id: {case_id}')

    return PanelOutputPropertyExpectations(
        get_output_property=plain_terminal,
        expected_output_for_case_id=_expected_output_for_case_id,
    )


@pc.case(id='bw-stylized-terminal-output', tags=['expectations', 'layout_styling'])
def case_layout_styling_expectations_bw_stylized_terminal(
    bw_stylized_terminal: Annotated[OutputPropertyType,
                                    pc.fixture]) -> PanelOutputPropertyExpectations:
    def _expected_output_for_case_id(case_id: str) -> str:
        match case_id:
            case 'no-frame-dark-color' \
                 | 'no-frame-dark-color-no-bg':
                return dedent("""\
                    ╭─────────┬─────────╮
                    │ \x1b[1mPanel_1\x1b[0m │ \x1b[1mPanel_2\x1b[0m │
                    │ \x1b[1mContent\x1b[0m │ \x1b[1mContent\x1b[0m │
                    ╰─────────┴─────────╯
                    """)
            case _:
                raise ValueError(f'Unexpected case_id: {case_id}')

    return PanelOutputPropertyExpectations(
        get_output_property=bw_stylized_terminal,
        expected_output_for_case_id=_expected_output_for_case_id,
    )


@pc.case(id='colorized-terminal-output', tags=['expectations', 'layout_styling'])
def case_layout_styling_expectations_colorized_terminal(
    colorized_terminal: Annotated[OutputPropertyType,
                                  pc.fixture]) -> PanelOutputPropertyExpectations:
    def _expected_output_for_case_id(case_id: str) -> str:
        match case_id:
            case 'no-frame-dark-color':
                return ('\x1b[38;2;212;210;200;48;2;29;35;49m╭─────────┬─────────╮\x1b[0m\n'
                        '\x1b[38;2;212;210;200;48;2;29;35;49m│\x1b[0m \x1b[1;34mPanel_1\x1b[0m '
                        '\x1b[38;2;212;210;200;48;2;29;35;49m│\x1b[0m \x1b[1;34mPanel_2\x1b[0m '
                        '\x1b[38;2;212;210;200;48;2;29;35;49m│\x1b[0m\n'
                        '\x1b[38;2;212;210;200;48;2;29;35;49m│\x1b[0m \x1b[1;34mContent\x1b[0m '
                        '\x1b[38;2;212;210;200;48;2;29;35;49m│\x1b[0m \x1b[1;34mContent\x1b[0m '
                        '\x1b[38;2;212;210;200;48;2;29;35;49m│\x1b[0m\n'
                        '\x1b[38;2;212;210;200;48;2;29;35;49m╰─────────┴─────────╯\x1b[0m\n')

            case 'no-frame-dark-color-no-bg':
                return ('\x1b[38;2;212;210;200m╭─────────┬─────────╮\x1b[0m\n'
                        '\x1b[38;2;212;210;200m│\x1b[0m \x1b[1;34mPanel_1\x1b[0m '
                        '\x1b[38;2;212;210;200m│\x1b[0m \x1b[1;34mPanel_2\x1b[0m '
                        '\x1b[38;2;212;210;200m│\x1b[0m\n'
                        '\x1b[38;2;212;210;200m│\x1b[0m \x1b[1;34mContent\x1b[0m '
                        '\x1b[38;2;212;210;200m│\x1b[0m \x1b[1;34mContent\x1b[0m '
                        '\x1b[38;2;212;210;200m│\x1b[0m\n'
                        '\x1b[38;2;212;210;200m╰─────────┴─────────╯\x1b[0m\n')
            case _:
                raise ValueError(f'Unexpected case_id: {case_id}')

    return PanelOutputPropertyExpectations(
        get_output_property=colorized_terminal,
        expected_output_for_case_id=_expected_output_for_case_id,
    )


@pc.case(id='plain-html-tag-output', tags=['expectations', 'layout_styling'])
def case_layout_styling_expectations_plain_html_tag(
        plain_html_tag: Annotated[OutputPropertyType,
                                  pc.fixture]) -> PanelOutputPropertyExpectations:
    def _expected_output_for_case_id(case_id: str) -> str:
        match case_id:
            case 'no-frame-dark-color' | 'no-frame-dark-color-no-bg':
                return _fill_html_tag_template(
                    data=('╭─────────┬─────────╮\n'
                          '│ Panel_1 │ Panel_2 │\n'
                          '│ Content │ Content │\n'
                          '╰─────────┴─────────╯'),
                    case_id=case_id,
                )
            case _:
                raise ValueError(f'Unexpected case_id: {case_id}')

    return PanelOutputPropertyExpectations(
        get_output_property=plain_html_tag,
        expected_output_for_case_id=_expected_output_for_case_id,
    )


@pc.case(id='bw-stylized-html-tag-output', tags=['expectations', 'layout_styling'])
def case_layout_styling_expectations_bw_stylized_html_tag(
    bw_stylized_html_tag: Annotated[OutputPropertyType,
                                    pc.fixture]) -> PanelOutputPropertyExpectations:
    def _expected_output_for_case_id(case_id: str) -> str:
        match case_id:
            case 'no-frame-dark-color' | 'no-frame-dark-color-no-bg':
                return _fill_html_tag_template(
                    data=('╭─────────┬─────────╮\n'
                          '│ <span style="font-weight: bold">Panel_1</span> '
                          '│ <span style="font-weight: bold">Panel_2</span> │\n'
                          '│ <span style="font-weight: bold">Content</span> '
                          '│ <span style="font-weight: bold">Content</span> │\n'
                          '╰─────────┴─────────╯'),
                    case_id=case_id,
                )
            case _:
                raise ValueError(f'Unexpected case_id: {case_id}')

    return PanelOutputPropertyExpectations(
        get_output_property=bw_stylized_html_tag,
        expected_output_for_case_id=_expected_output_for_case_id,
    )


@pc.case(id='colorized-html-tag-output', tags=['expectations', 'layout_styling'])
def case_layout_styling_expectations_colorized_html_tag(
    colorized_html_tag: Annotated[OutputPropertyType,
                                  pc.fixture]) -> PanelOutputPropertyExpectations:
    def _expected_output_for_case_id(case_id: str) -> str:

        lightbulb_dark_color_style_with_bg = 'color: #d4d2c8; background-color: #1d2331; '
        lightbulb_dark_color_style_no_bg = 'color: #d4d2c8; '
        match case_id:
            case 'no-frame-dark-color':
                return _fill_html_tag_template(
                    data=('<span style="color: #d4d2c8; text-decoration-color: #d4d2c8; '
                          'background-color: #1d2331">╭─────────┬─────────╮</span>\n'
                          '<span style="color: #d4d2c8; text-decoration-color: #d4d2c8; '
                          'background-color: #1d2331">│</span> '
                          '<span style="color: #000080; text-decoration-color: #000080; '
                          'font-weight: bold">Panel_1</span> '
                          '<span style="color: #d4d2c8; text-decoration-color: #d4d2c8; '
                          'background-color: #1d2331">│</span> '
                          '<span style="color: #000080; text-decoration-color: #000080; '
                          'font-weight: bold">Panel_2</span> '
                          '<span style="color: #d4d2c8; text-decoration-color: #d4d2c8; '
                          'background-color: #1d2331">│</span>\n'
                          '<span style="color: #d4d2c8; text-decoration-color: #d4d2c8; '
                          'background-color: #1d2331">│</span> '
                          '<span style="color: #000080; text-decoration-color: #000080; '
                          'font-weight: bold">Content</span> '
                          '<span style="color: #d4d2c8; text-decoration-color: #d4d2c8; '
                          'background-color: #1d2331">│</span> '
                          '<span style="color: #000080; text-decoration-color: #000080; '
                          'font-weight: bold">Content</span> '
                          '<span style="color: #d4d2c8; text-decoration-color: #d4d2c8; '
                          'background-color: #1d2331">│</span>\n'
                          '<span style="color: #d4d2c8; text-decoration-color: #d4d2c8; '
                          'background-color: #1d2331">╰─────────┴─────────╯</span>'),
                    color_style=lightbulb_dark_color_style_with_bg,
                    case_id=case_id,
                )
            case 'no-frame-dark-color-no-bg':
                return _fill_html_tag_template(
                    data=('<span style="color: #d4d2c8; text-decoration-color: #d4d2c8">'
                          '╭─────────┬─────────╮</span>\n'
                          '<span style="color: #d4d2c8; text-decoration-color: #d4d2c8">│</span> '
                          '<span style="color: #000080; text-decoration-color: #000080; '
                          'font-weight: bold">Panel_1</span> '
                          '<span style="color: #d4d2c8; text-decoration-color: #d4d2c8">│</span> '
                          '<span style="color: #000080; text-decoration-color: #000080; '
                          'font-weight: bold">Panel_2</span> '
                          '<span style="color: #d4d2c8; text-decoration-color: #d4d2c8">│</span>\n'
                          '<span style="color: #d4d2c8; text-decoration-color: #d4d2c8">│</span> '
                          '<span style="color: #000080; text-decoration-color: #000080; '
                          'font-weight: bold">Content</span> '
                          '<span style="color: #d4d2c8; text-decoration-color: #d4d2c8">│</span> '
                          '<span style="color: #000080; text-decoration-color: #000080; '
                          'font-weight: bold">Content</span> '
                          '<span style="color: #d4d2c8; text-decoration-color: #d4d2c8">│</span>\n'
                          '<span style="color: #d4d2c8; text-decoration-color: #d4d2c8">'
                          '╰─────────┴─────────╯</span>'),
                    color_style=lightbulb_dark_color_style_no_bg,
                    case_id=case_id,
                )
            case _:
                raise ValueError(f'Unexpected case_id: {case_id}')

    return PanelOutputPropertyExpectations(
        get_output_property=colorized_html_tag,
        expected_output_for_case_id=_expected_output_for_case_id,
    )


@pc.case(id='plain-html-page-output', tags=['expectations', 'layout_styling'])
def case_layout_styling_expectations_plain_html_page(
        plain_html_page: Annotated[OutputPropertyType,
                                   pc.fixture]) -> PanelOutputPropertyExpectations:
    light_body_style = """
      body {
        color: #000000;
        background-color: #ffffff;
      }"""

    def _expected_output_for_case_id(case_id: str) -> str:
        match case_id:
            case 'no-frame-dark-color' | 'no-frame-dark-color-no-bg':
                return _fill_html_page_template(
                    style=light_body_style,
                    data=('╭─────────┬─────────╮\n'
                          '│ Panel_1 │ Panel_2 │\n'
                          '│ Content │ Content │\n'
                          '╰─────────┴─────────╯'),
                    case_id=case_id,
                )
            case _:
                raise ValueError(f'Unexpected case_id: {case_id}')

    return PanelOutputPropertyExpectations(
        get_output_property=plain_html_page,
        expected_output_for_case_id=_expected_output_for_case_id,
    )


@pc.case(id='bw-stylized-html-page-output', tags=['expectations', 'layout_styling'])
def case_layout_styling_expectations_bw_stylized_html_page(
    bw_stylized_html_page: Annotated[OutputPropertyType, pc.fixture]
) -> PanelOutputPropertyExpectations:
    bold_style = '\n'.join([
        '.r2 {font-weight: bold}',
    ])

    light_body_style = """
      body {
        color: #000000;
        background-color: #ffffff;
      }"""

    def _expected_output_for_case_id(case_id: str) -> str:
        match case_id:
            case 'no-frame-dark-color' | 'no-frame-dark-color-no-bg':
                return _fill_html_page_template(
                    style=bold_style + light_body_style,
                    data=('<span class="r1">╭─────────┬─────────╮</span>\n'
                          '<span class="r1">│</span> <span class="r2">Panel_1</span> '
                          '<span class="r1">│</span> <span class="r2">Panel_2</span> '
                          '<span class="r1">│</span>\n'
                          '<span class="r1">│</span> <span class="r2">Content</span> '
                          '<span class="r1">│</span> <span class="r2">Content</span> '
                          '<span class="r1">│</span>\n'
                          '<span class="r1">╰─────────┴─────────╯</span>'),
                    case_id=case_id,
                )
            case _:
                raise ValueError(f'Unexpected case_id: {case_id}')

    return PanelOutputPropertyExpectations(
        get_output_property=bw_stylized_html_page,
        expected_output_for_case_id=_expected_output_for_case_id,
    )


@pc.case(id='colorized-html-page-output', tags=['expectations', 'layout_styling'])
def case_layout_styling_expectations_colorized_html_page(
    colorized_html_page: Annotated[OutputPropertyType,
                                   pc.fixture]) -> PanelOutputPropertyExpectations:
    lightbulb_dark_style_with_bg = '\n'.join([
        '.r1 {color: #d4d2c8; text-decoration-color: #d4d2c8; background-color: #1d2331}',
        '.r2 {color: #000080; text-decoration-color: #000080; font-weight: bold}',
    ])

    lightbulb_dark_style_no_bg = '\n'.join([
        '.r1 {color: #d4d2c8; text-decoration-color: #d4d2c8}',
        '.r2 {color: #000080; text-decoration-color: #000080; font-weight: bold}',
    ])

    lightbulb_dark_body_style_with_bg = """
      body {
        color: #d4d2c8;
        background-color: #1d2331;
      }"""

    lightbulb_dark_body_style_no_bg = """
      body {
        color: #d4d2c8;
        background-color: #000000;
      }"""

    no_frame_default_color_exp_output = (
        '<span class="r1">╭─────────┬─────────╮</span>\n'
        '<span class="r1">│</span> <span class="r2">Panel_1</span> '
        '<span class="r1">│</span> <span class="r2">Panel_2</span> '
        '<span class="r1">│</span>\n'
        '<span class="r1">│</span> <span class="r2">Content</span> '
        '<span class="r1">│</span> <span class="r2">Content</span> '
        '<span class="r1">│</span>\n'
        '<span class="r1">╰─────────┴─────────╯</span>')

    def _expected_output_for_case_id(case_id: str) -> str:
        match case_id:
            case 'no-frame-dark-color':
                return _fill_html_page_template(
                    style=lightbulb_dark_style_with_bg + lightbulb_dark_body_style_with_bg,
                    data=no_frame_default_color_exp_output,
                )
            case 'no-frame-dark-color-no-bg':
                return _fill_html_page_template(
                    style=lightbulb_dark_style_no_bg + lightbulb_dark_body_style_no_bg,
                    data=no_frame_default_color_exp_output,
                )
            case _:
                raise ValueError(f'Unexpected case_id: {case_id}')

    return PanelOutputPropertyExpectations(
        get_output_property=colorized_html_page,
        expected_output_for_case_id=_expected_output_for_case_id,
    )
