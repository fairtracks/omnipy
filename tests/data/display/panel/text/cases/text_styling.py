from textwrap import dedent
from typing import Annotated

import pytest_cases as pc

from omnipy import PrettyPrinterLib, SyntaxLanguageSpec
from omnipy.data._display.config import OutputConfig
from omnipy.data._display.dimensions import Dimensions
from omnipy.data._display.frame import Frame
from omnipy.shared.enums.colorstyles import DarkLowContrastColorStyles, LightLowContrastColorStyles
from omnipy.shared.enums.display import (DisplayColorSystem,
                                         HorizontalOverflowMode,
                                         VerticalOverflowMode)

from ...helpers.case_setup import (OutputPropertyType,
                                   PanelOutputTestCase,
                                   StylizedPanelOutputExpectations,
                                   StylizedPanelTestCaseSetup,
                                   WithinFrameExp)
from ...helpers.panel_assert import (fill_html_page_template,
                                     fill_html_tag_template,
                                     FONT_RENDER_BODY_STYLE)


@pc.case(id='wrap_horizontal', tags=['overflow_modes', 'syntax_text'])
def case_syntax_styling_wrap_horizontal(
        common_content: Annotated[str, pc.fixture]) -> PanelOutputTestCase[str]:
    return PanelOutputTestCase(  # pyright: ignore [reportCallIssue]
        content=common_content,
        frame=Frame(Dimensions(22, None)),
        config=OutputConfig(h_overflow=HorizontalOverflowMode.WRAP),
        exp_plain_output=dedent("""\
            [MyClass({'abc': [123,
            234]}),
             MyClass({'def': [345,
            456]})]
            """),
        exp_dims=Dimensions(width=22, height=4),
        exp_within_frame=WithinFrameExp(width=True, height=None, both=None),
    )


@pc.case(id='ellipsis_horizontal', tags=['overflow_modes', 'syntax_text'])
def case_syntax_styling_ellipsis_horizontal(
        common_text_content: Annotated[str, pc.fixture]) -> PanelOutputTestCase[str]:
    return PanelOutputTestCase(
        content=common_text_content,
        frame=Frame(Dimensions(22, None)),
        config=OutputConfig(h_overflow=HorizontalOverflowMode.ELLIPSIS),
        exp_plain_output=dedent("""\
            [MyClass({'abc': [123…
             MyClass({'def': [345…
            """),
        exp_dims=Dimensions(width=22, height=2),
        exp_within_frame=WithinFrameExp(width=True, height=None, both=None),
    )


@pc.case(id='crop_horizontal', tags=['overflow_modes', 'syntax_text'])
def case_syntax_styling_crop_horizontal(
        common_text_content: Annotated[str, pc.fixture]) -> PanelOutputTestCase[str]:
    return PanelOutputTestCase(
        content=common_text_content,
        frame=Frame(Dimensions(22, None)),
        config=OutputConfig(h_overflow=HorizontalOverflowMode.CROP),
        exp_plain_output=dedent("""\
            [MyClass({'abc': [123,
             MyClass({'def': [345,
            """),
        exp_dims=Dimensions(width=22, height=2),
        exp_within_frame=WithinFrameExp(width=True, height=None, both=None),
    )


@pc.case(id='wrap_small_frame', tags=['overflow_modes', 'syntax_text'])
def case_syntax_styling_wrap_small_frame(
        common_text_content: Annotated[str, pc.fixture]) -> PanelOutputTestCase[str]:
    return PanelOutputTestCase(
        content=common_text_content,
        frame=Frame(Dimensions(10, 8)),
        config=OutputConfig(h_overflow=HorizontalOverflowMode.WRAP),
        exp_plain_output=dedent("""\
            [MyClass({
            'abc': 
            [123, 
            234]}),
             MyClass({
            'def': 
            [345, 
            456]})]
            """),  # noqa: W291
        exp_dims=Dimensions(width=10, height=8),
        exp_within_frame=WithinFrameExp(width=True, height=True, both=None),
    )


@pc.case(id='wrap_crop_bottom', tags=['overflow_modes', 'syntax_text'])
def case_syntax_styling_wrap_crop_bottom(
        common_text_content: Annotated[str, pc.fixture]) -> PanelOutputTestCase[str]:
    return PanelOutputTestCase(
        content=common_text_content,
        frame=Frame(Dimensions(10, 4)),
        config=OutputConfig(
            h_overflow=HorizontalOverflowMode.WRAP,
            v_overflow=VerticalOverflowMode.CROP_BOTTOM,
        ),
        exp_plain_output=dedent("""\
            [MyClass({
            'abc': 
            [123, 
            234]}),
            """),  # noqa: W291
        exp_dims=Dimensions(width=10, height=4),
        exp_within_frame=WithinFrameExp(width=True, height=True, both=True),
    )


@pc.case(id='wrap_crop_top', tags=['overflow_modes', 'syntax_text'])
def case_syntax_styling_wrap_crop_top(
        common_text_content: Annotated[str, pc.fixture]) -> PanelOutputTestCase[str]:
    return PanelOutputTestCase(
        content=common_text_content,
        frame=Frame(Dimensions(10, 1)),
        config=OutputConfig(
            h_overflow=HorizontalOverflowMode.WRAP,
            v_overflow=VerticalOverflowMode.CROP_TOP,
        ),
        exp_plain_output=dedent("""\
            456]})]
            """),  # noqa: W291
        exp_dims=Dimensions(width=7, height=1),
        exp_within_frame=WithinFrameExp(width=True, height=True, both=True),
    )


@pc.parametrize('solid_background', [True, False])
@pc.case(id='no-frame-default-color', tags=['setup', 'syntax_text'])
def case_syntax_styling_setup_no_frame_or_configs(
        solid_background: bool) -> StylizedPanelTestCaseSetup[str]:
    return StylizedPanelTestCaseSetup(
        case_id='no-frame-default-color' + ('-no-bg' if not solid_background else ''),
        content="MyClass({'abc': [123, 234]})",
        config=OutputConfig(
            printer=PrettyPrinterLib.TEXT,
            syntax=SyntaxLanguageSpec.PYTHON,
            system=DisplayColorSystem.ANSI_RGB,
            bg=solid_background),
    )


@pc.parametrize(
    'css_font_families, css_font_size, css_font_weight, css_line_height',
    [[[], None, None, None], [[], None, 500, 1.0], [('monospace',), 15, 600, 1.1]],
    ids=['no-fonts', 'font-styling-only', 'full-font-conf'])
@pc.parametrize('solid_background', [True, False])
@pc.case(id='no-frame-light-color', tags=['setup', 'syntax_text'])
def case_syntax_styling_setup_no_frame_color_config(
        css_font_families: tuple[str, ...],
        css_font_size: int | None,
        css_font_weight: int | None,
        css_line_height: float | None,
        solid_background: bool) -> StylizedPanelTestCaseSetup[str]:
    case_id = 'no-frame-light-color' \
              + ('-no-fonts' if css_font_weight is None else '') \
              + ('-font-styling-only' if css_font_weight == 500 else '') \
              + ('-full-font-conf' if css_font_families == ('monospace',) else '') \
              + ('-no-bg' if not solid_background else '')

    return StylizedPanelTestCaseSetup(
        case_id=case_id,
        content="MyClass({'abc': [123, 234]})",
        config=OutputConfig(
            printer=PrettyPrinterLib.TEXT,
            syntax=SyntaxLanguageSpec.PYTHON,
            fonts=css_font_families,
            font_size=css_font_size,
            font_weight=css_font_weight,
            line_height=css_line_height,
            system=DisplayColorSystem.ANSI_RGB,
            style=LightLowContrastColorStyles.MURPHY_PYGMENTS,
            bg=solid_background),
    )


@pc.parametrize('color_system',
                [DisplayColorSystem.AUTO, DisplayColorSystem.ANSI_256, DisplayColorSystem.ANSI_RGB])
@pc.parametrize('solid_background', [True, False])
@pc.case(id='w-frame-dark-color-w-wrap', tags=['setup', 'syntax_text'])
def case_syntax_styling_setup_small_frame_color_and_overflow_config(
    color_system: DisplayColorSystem.Literals,
    solid_background: bool,
) -> StylizedPanelTestCaseSetup[str]:

    case_id = f'w-frame-dark-color-w-wrap-{color_system}' + \
              ('-no-bg' if not solid_background else '')

    return StylizedPanelTestCaseSetup(
        case_id=case_id,
        content="MyClass({'abc': [123, 234]})",
        frame=Frame(Dimensions(9, 3)),
        config=OutputConfig(
            printer=PrettyPrinterLib.TEXT,
            syntax=SyntaxLanguageSpec.PYTHON,
            system=color_system,
            style=DarkLowContrastColorStyles.ZENBURN_PYGMENTS,
            bg=solid_background,
            h_overflow=HorizontalOverflowMode.WRAP,
            v_overflow=VerticalOverflowMode.CROP_TOP,
        ),
    )


# Output property expectations per output test case


@pc.case(id='plain-terminal-output', tags=['expectations', 'syntax_text'])
def case_syntax_styling_expectations_plain_terminal(
        plain_terminal: Annotated[OutputPropertyType,
                                  pc.fixture]) -> StylizedPanelOutputExpectations:
    def _exp_plain_output_for_case_id(case_id: str) -> str:
        match case_id:
            case 'no-frame-default-color' \
                 | 'no-frame-default-color-no-bg' \
                 | 'no-frame-light-color-no-fonts' \
                 | 'no-frame-light-color-font-styling-only' \
                 | 'no-frame-light-color-full-font-conf' \
                 | 'no-frame-light-color-no-fonts-no-bg' \
                 | 'no-frame-light-color-font-styling-only-no-bg' \
                 | 'no-frame-light-color-full-font-conf-no-bg':
                return "MyClass({'abc': [123, 234]})\n"
            case 'w-frame-dark-color-w-wrap-auto' \
                 | 'w-frame-dark-color-w-wrap-256' \
                 | 'w-frame-dark-color-w-wrap-truecolor':
                return ("'abc':   \n"
                        '[123,    \n'
                        '234]})   \n')
            case 'w-frame-dark-color-w-wrap-auto-no-bg' | 'w-frame-dark-color-w-wrap-256-no-bg' \
                    | 'w-frame-dark-color-w-wrap-truecolor-no-bg':
                return ("'abc': \n"
                        '[123, \n'
                        '234]})\n')
            case _:
                raise ValueError(f'Unexpected case_id: {case_id}')

    return StylizedPanelOutputExpectations(
        get_output_property=plain_terminal,
        exp_plain_output_for_case_id=_exp_plain_output_for_case_id,
    )


@pc.case(id='bw-stylized-terminal-output', tags=['expectations', 'syntax_text'])
def case_syntax_styling_expectations_bw_stylized_terminal(
    bw_stylized_terminal: Annotated[OutputPropertyType,
                                    pc.fixture]) -> StylizedPanelOutputExpectations:
    def _exp_plain_output_for_case_id(case_id: str) -> str:
        match case_id:
            case 'no-frame-default-color' \
                 | 'no-frame-default-color-no-bg':
                return "MyClass({'abc': [123, 234]})\n"
            case 'no-frame-light-color-no-fonts' \
                 | 'no-frame-light-color-font-styling-only' \
                 | 'no-frame-light-color-full-font-conf' \
                 | 'no-frame-light-color-no-fonts-no-bg' \
                 | 'no-frame-light-color-font-styling-only-no-bg' \
                 | 'no-frame-light-color-full-font-conf-no-bg':
                return "MyClass({'abc': [\x1b[1m123\x1b[0m, \x1b[1m234\x1b[0m]})\n"
            case 'w-frame-dark-color-w-wrap-auto' \
                 | 'w-frame-dark-color-w-wrap-256' \
                 | 'w-frame-dark-color-w-wrap-truecolor':
                return ("'abc':   \n"
                        '[123,    \n'
                        '234]})   \n')
            case 'w-frame-dark-color-w-wrap-auto-no-bg' \
                 | 'w-frame-dark-color-w-wrap-256-no-bg' \
                 | 'w-frame-dark-color-w-wrap-truecolor-no-bg':
                return ("'abc': \n"
                        '[123, \n'
                        '234]})\n')
            case _:
                raise ValueError(f'Unexpected case_id: {case_id}')

    return StylizedPanelOutputExpectations(
        get_output_property=bw_stylized_terminal,
        exp_plain_output_for_case_id=_exp_plain_output_for_case_id,
    )


@pc.case(id='colorized-terminal-output', tags=['expectations', 'syntax_text'])
def case_syntax_styling_expectations_colorized_terminal(
    colorized_terminal: Annotated[OutputPropertyType,
                                  pc.fixture]) -> StylizedPanelOutputExpectations:
    def _exp_plain_output_for_case_id(case_id: str) -> str:
        match case_id:
            case 'no-frame-default-color' \
                 | 'no-frame-default-color-no-bg':
                return ("MyClass({\x1b[33m'\x1b[0m\x1b[33mabc\x1b[0m"
                        "\x1b[33m'\x1b[0m: [\x1b[94m123\x1b[0m, "
                        '\x1b[94m234\x1b[0m]})\n')
            case 'no-frame-light-color-no-fonts' \
                 | 'no-frame-light-color-font-styling-only' \
                 | 'no-frame-light-color-full-font-conf':
                return ('\x1b[38;2;0;0;0;48;2;255;255;255mMyClass\x1b[0m'
                        '\x1b[38;2;0;0;0;48;2;255;255;255m(\x1b[0m'
                        '\x1b[38;2;0;0;0;48;2;255;255;255m{\x1b[0m'
                        "\x1b[38;2;0;0;0;48;2;224;224;255m'\x1b[0m"
                        '\x1b[38;2;0;0;0;48;2;224;224;255mabc\x1b[0m'
                        "\x1b[38;2;0;0;0;48;2;224;224;255m'\x1b[0m"
                        '\x1b[38;2;0;0;0;48;2;255;255;255m:\x1b[0m'
                        '\x1b[38;2;0;0;0;48;2;255;255;255m \x1b[0m'
                        '\x1b[38;2;0;0;0;48;2;255;255;255m[\x1b[0m'
                        '\x1b[1;38;2;102;102;255;48;2;255;255;255m123\x1b[0m'
                        '\x1b[38;2;0;0;0;48;2;255;255;255m,\x1b[0m'
                        '\x1b[38;2;0;0;0;48;2;255;255;255m \x1b[0m'
                        '\x1b[1;38;2;102;102;255;48;2;255;255;255m234\x1b[0m'
                        '\x1b[38;2;0;0;0;48;2;255;255;255m]\x1b[0m'
                        '\x1b[38;2;0;0;0;48;2;255;255;255m}\x1b[0m'
                        '\x1b[38;2;0;0;0;48;2;255;255;255m)\x1b[0m\n')
            case 'no-frame-light-color-no-fonts-no-bg' \
                 | 'no-frame-light-color-font-styling-only-no-bg' \
                 | 'no-frame-light-color-full-font-conf-no-bg':
                return ('\x1b[38;2;0;0;0mMyClass\x1b[0m'
                        '\x1b[38;2;0;0;0m(\x1b[0m'
                        '\x1b[38;2;0;0;0m{\x1b[0m'
                        "\x1b[38;2;0;0;0;48;2;224;224;255m'\x1b[0m"
                        '\x1b[38;2;0;0;0;48;2;224;224;255mabc\x1b[0m'
                        "\x1b[38;2;0;0;0;48;2;224;224;255m'\x1b[0m"
                        '\x1b[38;2;0;0;0m:\x1b[0m'
                        '\x1b[38;2;0;0;0m \x1b[0m'
                        '\x1b[38;2;0;0;0m[\x1b[0m'
                        '\x1b[1;38;2;102;102;255m123\x1b[0m'
                        '\x1b[38;2;0;0;0m,\x1b[0m'
                        '\x1b[38;2;0;0;0m \x1b[0m'
                        '\x1b[1;38;2;102;102;255m234\x1b[0m'
                        '\x1b[38;2;0;0;0m]\x1b[0m'
                        '\x1b[38;2;0;0;0m}\x1b[0m'
                        '\x1b[38;2;0;0;0m)\x1b[0m\n')
            case 'w-frame-dark-color-w-wrap-auto':
                return ("\x1b[37;100m'\x1b[0m\x1b[37;100mabc\x1b[0m"
                        "\x1b[37;100m'\x1b[0m\x1b[97;100m:\x1b[0m"
                        '\x1b[97;100m \x1b[0m\x1b[100m  \x1b[0m\n'
                        '\x1b[97;100m[\x1b[0m\x1b[37;100m123\x1b[0m'
                        '\x1b[97;100m,\x1b[0m\x1b[97;100m \x1b[0m'
                        '\x1b[100m   \x1b[0m\n'
                        '\x1b[37;100m234\x1b[0m\x1b[97;100m]\x1b[0m'
                        '\x1b[97;100m}\x1b[0m\x1b[97;100m)\x1b[0m'
                        '\x1b[100m   \x1b[0m\n')
            case 'w-frame-dark-color-w-wrap-256':
                return ("\x1b[38;5;174;48;5;237m'\x1b[0m"
                        '\x1b[38;5;174;48;5;237mabc\x1b[0m'
                        "\x1b[38;5;174;48;5;237m'\x1b[0m"
                        '\x1b[38;5;230;48;5;237m:\x1b[0m'
                        '\x1b[38;5;188;48;5;237m \x1b[0m'
                        '\x1b[48;5;237m  \x1b[0m\n'
                        '\x1b[38;5;230;48;5;237m[\x1b[0m'
                        '\x1b[38;5;116;48;5;237m123\x1b[0m'
                        '\x1b[38;5;230;48;5;237m,\x1b[0m'
                        '\x1b[38;5;188;48;5;237m \x1b[0m'
                        '\x1b[48;5;237m   \x1b[0m\n'
                        '\x1b[38;5;116;48;5;237m234\x1b[0m'
                        '\x1b[38;5;230;48;5;237m]\x1b[0m'
                        '\x1b[38;5;230;48;5;237m}\x1b[0m'
                        '\x1b[38;5;230;48;5;237m)\x1b[0m'
                        '\x1b[48;5;237m   \x1b[0m\n')
            case 'w-frame-dark-color-w-wrap-truecolor':
                return ("\x1b[38;2;204;147;147;48;2;63;63;63m'\x1b[0m"
                        '\x1b[38;2;204;147;147;48;2;63;63;63mabc\x1b[0m'
                        "\x1b[38;2;204;147;147;48;2;63;63;63m'\x1b[0m"
                        '\x1b[38;2;240;239;208;48;2;63;63;63m:\x1b[0m'
                        '\x1b[38;2;220;220;204;48;2;63;63;63m \x1b[0m'
                        '\x1b[48;2;63;63;63m  \x1b[0m\n'
                        '\x1b[38;2;240;239;208;48;2;63;63;63m[\x1b[0m'
                        '\x1b[38;2;140;208;211;48;2;63;63;63m123\x1b[0m'
                        '\x1b[38;2;240;239;208;48;2;63;63;63m,\x1b[0m'
                        '\x1b[38;2;220;220;204;48;2;63;63;63m \x1b[0m'
                        '\x1b[48;2;63;63;63m   \x1b[0m\n'
                        '\x1b[38;2;140;208;211;48;2;63;63;63m234\x1b[0m'
                        '\x1b[38;2;240;239;208;48;2;63;63;63m]\x1b[0m'
                        '\x1b[38;2;240;239;208;48;2;63;63;63m}\x1b[0m'
                        '\x1b[38;2;240;239;208;48;2;63;63;63m)\x1b[0m'
                        '\x1b[48;2;63;63;63m   \x1b[0m\n')
            case 'w-frame-dark-color-w-wrap-auto-no-bg':
                return ("\x1b[37m'\x1b[0m\x1b[37mabc\x1b[0m\x1b[37m'\x1b[0m"
                        '\x1b[97m:\x1b[0m\x1b[97m \x1b[0m\n'
                        '\x1b[97m[\x1b[0m\x1b[37m123\x1b[0m\x1b[97m,\x1b[0m'
                        '\x1b[97m \x1b[0m\n'
                        '\x1b[37m234\x1b[0m\x1b[97m]\x1b[0m\x1b[97m}\x1b[0m'
                        '\x1b[97m)\x1b[0m\n')
            case 'w-frame-dark-color-w-wrap-256-no-bg':
                return ("\x1b[38;5;174m'\x1b[0m\x1b[38;5;174mabc\x1b[0m"
                        "\x1b[38;5;174m'\x1b[0m\x1b[38;5;230m:\x1b[0m"
                        '\x1b[38;5;188m \x1b[0m\n'
                        '\x1b[38;5;230m[\x1b[0m\x1b[38;5;116m123\x1b[0m'
                        '\x1b[38;5;230m,\x1b[0m\x1b[38;5;188m \x1b[0m\n'
                        '\x1b[38;5;116m234\x1b[0m\x1b[38;5;230m]\x1b[0m'
                        '\x1b[38;5;230m}\x1b[0m\x1b[38;5;230m)\x1b[0m\n')
            case 'w-frame-dark-color-w-wrap-truecolor-no-bg':
                return ("\x1b[38;2;204;147;147m'\x1b[0m"
                        '\x1b[38;2;204;147;147mabc\x1b[0m'
                        "\x1b[38;2;204;147;147m'\x1b[0m"
                        '\x1b[38;2;240;239;208m:\x1b[0m'
                        '\x1b[38;2;220;220;204m \x1b[0m\n'
                        '\x1b[38;2;240;239;208m[\x1b[0m'
                        '\x1b[38;2;140;208;211m123\x1b[0m'
                        '\x1b[38;2;240;239;208m,\x1b[0m'
                        '\x1b[38;2;220;220;204m \x1b[0m\n'
                        '\x1b[38;2;140;208;211m234\x1b[0m'
                        '\x1b[38;2;240;239;208m]\x1b[0m'
                        '\x1b[38;2;240;239;208m}\x1b[0m'
                        '\x1b[38;2;240;239;208m)\x1b[0m\n')
            case _:
                raise ValueError(f'Unexpected case_id: {case_id}')

    return StylizedPanelOutputExpectations(
        get_output_property=colorized_terminal,
        exp_plain_output_for_case_id=_exp_plain_output_for_case_id,
    )


@pc.case(id='plain-html-tag-output', tags=['expectations', 'syntax_text'])
def case_syntax_styling_expectations_plain_html_tag(
        plain_html_tag: Annotated[OutputPropertyType,
                                  pc.fixture]) -> StylizedPanelOutputExpectations:
    def _exp_plain_output_for_case_id(case_id: str) -> str:
        match case_id:
            case 'no-frame-default-color' \
                 | 'no-frame-default-color-no-bg' \
                 | 'no-frame-light-color-no-fonts' \
                 | 'no-frame-light-color-font-styling-only' \
                 | 'no-frame-light-color-full-font-conf' \
                 | 'no-frame-light-color-no-fonts-no-bg' \
                 | 'no-frame-light-color-font-styling-only-no-bg' \
                 | 'no-frame-light-color-full-font-conf-no-bg':
                return fill_html_tag_template(
                    data='MyClass({&#x27;abc&#x27;: [123, 234]})',
                    case_id=case_id,
                )
            case 'w-frame-dark-color-w-wrap-auto' \
                 | 'w-frame-dark-color-w-wrap-256' \
                 | 'w-frame-dark-color-w-wrap-truecolor' \
                 | 'w-frame-dark-color-w-wrap-auto-no-bg' \
                 | 'w-frame-dark-color-w-wrap-256-no-bg' \
                 | 'w-frame-dark-color-w-wrap-truecolor-no-bg':
                return fill_html_tag_template(data=('&#x27;abc&#x27;: \n'
                                                    '[123, \n'
                                                    '234]})'))
            case _:
                raise ValueError(f'Unexpected case_id: {case_id}')

    return StylizedPanelOutputExpectations(
        get_output_property=plain_html_tag,
        exp_plain_output_for_case_id=_exp_plain_output_for_case_id,
    )


@pc.case(id='bw-stylized-html-tag-output', tags=['expectations', 'syntax_text'])
def case_syntax_styling_expectations_bw_stylized_html_tag(
    bw_stylized_html_tag: Annotated[OutputPropertyType,
                                    pc.fixture]) -> StylizedPanelOutputExpectations:
    def _exp_plain_output_for_case_id(case_id: str) -> str:
        match case_id:
            case 'no-frame-default-color' \
                 | 'no-frame-default-color-no-bg':
                return fill_html_tag_template(data='MyClass({&#x27;abc&#x27;: [123, 234]})')
            case 'no-frame-light-color-no-fonts' \
                 | 'no-frame-light-color-font-styling-only' \
                 | 'no-frame-light-color-full-font-conf' \
                 | 'no-frame-light-color-no-fonts-no-bg' \
                 | 'no-frame-light-color-font-styling-only-no-bg' \
                 | 'no-frame-light-color-full-font-conf-no-bg':
                return fill_html_tag_template(
                    data=('MyClass({&#x27;abc&#x27;: ['
                          '<span style="font-weight: bold">123</span>, '
                          '<span style="font-weight: bold">234</span>]})'),
                    case_id=case_id,
                )
            case 'w-frame-dark-color-w-wrap-auto' \
                 | 'w-frame-dark-color-w-wrap-256' \
                 | 'w-frame-dark-color-w-wrap-truecolor' \
                 | 'w-frame-dark-color-w-wrap-auto-no-bg' \
                 | 'w-frame-dark-color-w-wrap-256-no-bg' \
                 | 'w-frame-dark-color-w-wrap-truecolor-no-bg':
                return fill_html_tag_template(data=('&#x27;abc&#x27;: \n'
                                                    '[123, \n'
                                                    '234]})'))
            case _:
                raise ValueError(f'Unexpected case_id: {case_id}')

    return StylizedPanelOutputExpectations(
        get_output_property=bw_stylized_html_tag,
        exp_plain_output_for_case_id=_exp_plain_output_for_case_id,
    )


@pc.case(id='colorized-html-tag-output', tags=['expectations', 'syntax_text'])
def case_syntax_styling_expectations_colorized_html_tag(
    colorized_html_tag: Annotated[OutputPropertyType,
                                  pc.fixture]) -> StylizedPanelOutputExpectations:

    no_frame_default_color_exp_output = (
        'MyClass({'
        '<span style="color: #808000; text-decoration-color: #808000">'
        '&#x27;abc&#x27;</span>: ['
        '<span style="color: #0000ff; text-decoration-color: #0000ff">123</span>, '
        '<span style="color: #0000ff; text-decoration-color: #0000ff">234</span>]})')

    no_frame_light_color_exp_output = (
        '<span style="color: #000000; text-decoration-color: #000000">'
        'MyClass({</span>'
        '<span style="color: #000000; text-decoration-color: #000000; '
        'background-color: #e0e0ff">&#x27;abc&#x27;</span>'
        '<span style="color: #000000; text-decoration-color: #000000">: [</span>'
        '<span style="color: #6666ff; text-decoration-color: #6666ff; '
        'font-weight: bold">123</span>'
        '<span style="color: #000000; text-decoration-color: #000000">, </span>'
        '<span style="color: #6666ff; text-decoration-color: #6666ff; '
        'font-weight: bold">234</span>'
        '<span style="color: #000000; text-decoration-color: #000000">]})</span>')

    w_frame_dark_color_exp_output = (
        '<span style="color: #cc9393; text-decoration-color: #cc9393">'
        '&#x27;abc&#x27;</span>'
        '<span style="color: #f0efd0; text-decoration-color: #f0efd0">:</span>'
        '<span style="color: #dcdccc; text-decoration-color: #dcdccc"> </span>\n'
        '<span style="color: #f0efd0; text-decoration-color: #f0efd0">[</span>'
        '<span style="color: #8cd0d3; text-decoration-color: #8cd0d3">123</span>'
        '<span style="color: #f0efd0; text-decoration-color: #f0efd0">,</span>'
        '<span style="color: #dcdccc; text-decoration-color: #dcdccc"> </span>\n'
        '<span style="color: #8cd0d3; text-decoration-color: #8cd0d3">234</span>'
        '<span style="color: #f0efd0; text-decoration-color: #f0efd0">]})</span>')

    ansi_dark_color_style_with_bg = 'color: #ffffff; background-color: #000000; '
    ansi_dark_color_style_no_bg = 'color: #ffffff; '
    murphy_light_color_style_with_bg = 'color: #000000; background-color: #ffffff; '
    murphy_light_color_style_no_bg = 'color: #000000; '
    zenburn_dark_color_style_with_bg = 'color: #dcdccc; background-color: #3f3f3f; '
    zenburn_dark_color_style_no_bg = 'color: #dcdccc; '

    def _exp_plain_output_for_case_id(case_id: str) -> str:
        match case_id:
            case 'no-frame-default-color':
                return fill_html_tag_template(
                    data=no_frame_default_color_exp_output,
                    color_style=ansi_dark_color_style_with_bg,
                )
            case 'no-frame-default-color-no-bg':
                return fill_html_tag_template(
                    data=no_frame_default_color_exp_output,
                    color_style=ansi_dark_color_style_no_bg,
                )
            case 'no-frame-light-color-no-fonts' \
                 | 'no-frame-light-color-font-styling-only' \
                 | 'no-frame-light-color-full-font-conf':
                return fill_html_tag_template(
                    data=no_frame_light_color_exp_output,
                    color_style=murphy_light_color_style_with_bg,
                    case_id=case_id,
                )
            case 'no-frame-light-color-no-fonts-no-bg' \
                 | 'no-frame-light-color-font-styling-only-no-bg' \
                 | 'no-frame-light-color-full-font-conf-no-bg':
                return fill_html_tag_template(
                    data=no_frame_light_color_exp_output,
                    color_style=murphy_light_color_style_no_bg,
                    case_id=case_id,
                )
            case 'w-frame-dark-color-w-wrap-auto' \
                 | 'w-frame-dark-color-w-wrap-256' \
                 | 'w-frame-dark-color-w-wrap-truecolor':
                return fill_html_tag_template(
                    data=w_frame_dark_color_exp_output,
                    color_style=zenburn_dark_color_style_with_bg,
                )
            case 'w-frame-dark-color-w-wrap-auto-no-bg' \
                 | 'w-frame-dark-color-w-wrap-256-no-bg' \
                 | 'w-frame-dark-color-w-wrap-truecolor-no-bg':
                return fill_html_tag_template(
                    data=w_frame_dark_color_exp_output,
                    color_style=zenburn_dark_color_style_no_bg,
                )
            case _:
                raise ValueError(f'Unexpected case_id: {case_id}')

    return StylizedPanelOutputExpectations(
        get_output_property=colorized_html_tag,
        exp_plain_output_for_case_id=_exp_plain_output_for_case_id,
    )


@pc.case(id='plain-html-page-output', tags=['expectations', 'syntax_text'])
def case_syntax_styling_expectations_plain_html_page(
        plain_html_page: Annotated[OutputPropertyType,
                                   pc.fixture]) -> StylizedPanelOutputExpectations:
    bw_light_body_style = f"""
      body {{
        color: #000000;
        background-color: #ffffff;
        {FONT_RENDER_BODY_STYLE}
      }}"""

    def _exp_plain_output_for_case_id(case_id: str) -> str:
        match case_id:
            case 'no-frame-default-color' \
                 | 'no-frame-default-color-no-bg' \
                 | 'no-frame-light-color-no-fonts' \
                 | 'no-frame-light-color-font-styling-only' \
                 | 'no-frame-light-color-full-font-conf' \
                 | 'no-frame-light-color-no-fonts-no-bg' \
                 | 'no-frame-light-color-font-styling-only-no-bg' \
                 | 'no-frame-light-color-full-font-conf-no-bg':
                return fill_html_page_template(
                    style=bw_light_body_style,
                    data='MyClass({&#x27;abc&#x27;: [123, 234]})',
                    case_id=case_id,
                )
            case 'w-frame-dark-color-w-wrap-auto' \
                 | 'w-frame-dark-color-w-wrap-256' \
                 | 'w-frame-dark-color-w-wrap-truecolor'\
                 | 'w-frame-dark-color-w-wrap-auto-no-bg' \
                 | 'w-frame-dark-color-w-wrap-256-no-bg' \
                 | 'w-frame-dark-color-w-wrap-truecolor-no-bg':
                return fill_html_page_template(
                    style=bw_light_body_style,
                    data=('&#x27;abc&#x27;: \n'
                          '[123, \n'
                          '234]})'),
                )
            case _:
                raise ValueError(f'Unexpected case_id: {case_id}')

    return StylizedPanelOutputExpectations(
        get_output_property=plain_html_page,
        exp_plain_output_for_case_id=_exp_plain_output_for_case_id,
    )


@pc.case(id='bw-stylized-html-page-output', tags=['expectations', 'syntax_text'])
def case_syntax_styling_expectations_bw_stylized_html_page(
    bw_stylized_html_page: Annotated[OutputPropertyType, pc.fixture]
) -> StylizedPanelOutputExpectations:
    bold_style = '.r2 {font-weight: bold}'

    bw_light_body_style = f"""
      body {{
        color: #000000;
        background-color: #ffffff;
        {FONT_RENDER_BODY_STYLE}
      }}"""

    def _exp_plain_output_for_case_id(case_id: str) -> str:
        match case_id:
            case 'no-frame-default-color' \
                 | 'no-frame-default-color-no-bg':
                return fill_html_page_template(
                    style=bw_light_body_style,
                    data=('MyClass({'
                          '<span class="r1">&#x27;abc&#x27;</span>: ['
                          '<span class="r1">123</span>, '
                          '<span class="r1">234</span>]})'),
                )
            case 'no-frame-light-color-no-fonts' \
                 | 'no-frame-light-color-font-styling-only' \
                 | 'no-frame-light-color-full-font-conf' \
                 | 'no-frame-light-color-no-fonts-no-bg' \
                 | 'no-frame-light-color-font-styling-only-no-bg' \
                 | 'no-frame-light-color-full-font-conf-no-bg':
                return fill_html_page_template(
                    style=bold_style + bw_light_body_style,
                    data=('<span class="r1">MyClass({&#x27;abc&#x27;: [</span>'
                          '<span class="r2">123</span>'
                          '<span class="r1">, </span>'
                          '<span class="r2">234</span>'
                          '<span class="r1">]})</span>'),
                    case_id=case_id,
                )
            case 'w-frame-dark-color-w-wrap-auto' \
                 | 'w-frame-dark-color-w-wrap-256' \
                 | 'w-frame-dark-color-w-wrap-truecolor'\
                 | 'w-frame-dark-color-w-wrap-auto-no-bg' \
                 | 'w-frame-dark-color-w-wrap-256-no-bg' \
                 | 'w-frame-dark-color-w-wrap-truecolor-no-bg':
                return fill_html_page_template(
                    style=bw_light_body_style,
                    data=('<span class="r1">&#x27;abc&#x27;: </span>\n'
                          '<span class="r1">[123, </span>\n'
                          '<span class="r1">234]})</span>'),
                )
            case _:
                raise ValueError(f'Unexpected case_id: {case_id}')

    return StylizedPanelOutputExpectations(
        get_output_property=bw_stylized_html_page,
        exp_plain_output_for_case_id=_exp_plain_output_for_case_id,
    )


@pc.case(id='colorized-html-page-output', tags=['expectations', 'syntax_text'])
def case_syntax_styling_expectations_colorized_html_page(
    colorized_html_page: Annotated[OutputPropertyType,
                                   pc.fixture]) -> StylizedPanelOutputExpectations:
    ansi_dark_style = '\n'.join([
        '.r1 {color: #808000; text-decoration-color: #808000}',
        '.r2 {color: #0000ff; text-decoration-color: #0000ff}',
    ])

    murphy_light_style = '\n'.join([
        '.r1 {color: #000000; text-decoration-color: #000000}',
        '.r2 {color: #000000; text-decoration-color: #000000; background-color: #e0e0ff}',
        '.r3 {color: #6666ff; text-decoration-color: #6666ff; font-weight: bold}',
    ])

    zenburn_dark_style_no_bg = '\n'.join([
        '.r1 {color: #dcdccc; text-decoration-color: #dcdccc}',
        '.r2 {color: #f0efd0; text-decoration-color: #f0efd0}',
        '.r3 {color: #cc9393; text-decoration-color: #cc9393}',
        '.r4 {color: #8cd0d3; text-decoration-color: #8cd0d3}',
    ])

    ansi_dark_body_style = f"""
      body {{
        color: #ffffff;
        background-color: #000000;
        {FONT_RENDER_BODY_STYLE}
      }}"""

    murphy_light_body_style = f"""
      body {{
        color: #000000;
        background-color: #ffffff;
        {FONT_RENDER_BODY_STYLE}
      }}"""

    zenburn_dark_body_style_with_bg = f"""
      body {{
        color: #dcdccc;
        background-color: #3f3f3f;
        {FONT_RENDER_BODY_STYLE}
      }}"""

    zenburn_dark_body_style_no_bg = f"""
      body {{
        color: #dcdccc;
        background-color: #000000;
        {FONT_RENDER_BODY_STYLE}
      }}"""

    no_frame_default_color_exp_output = ('MyClass({'
                                         '<span class="r1">&#x27;abc&#x27;</span>: ['
                                         '<span class="r2">123</span>, '
                                         '<span class="r2">234</span>]})')

    no_frame_light_color_exp_output = ('<span class="r1">MyClass({</span>'
                                       '<span class="r2">&#x27;abc&#x27;</span>'
                                       '<span class="r1">: [</span>'
                                       '<span class="r3">123</span>'
                                       '<span class="r1">, </span>'
                                       '<span class="r3">234</span>'
                                       '<span class="r1">]})</span>')

    w_frame_dark_color_exp_output = ('<span class="r3">&#x27;abc&#x27;</span>'
                                     '<span class="r2">:</span>'
                                     '<span class="r1"> </span>\n'
                                     '<span class="r2">[</span>'
                                     '<span class="r4">123</span>'
                                     '<span class="r2">,</span>'
                                     '<span class="r1"> </span>\n'
                                     '<span class="r4">234</span>'
                                     '<span class="r2">]})</span>')

    def _exp_plain_output_for_case_id(case_id: str) -> str:
        match case_id:
            case 'no-frame-default-color' \
                 | 'no-frame-default-color-no-bg':
                return fill_html_page_template(
                    style=ansi_dark_style + ansi_dark_body_style,
                    data=no_frame_default_color_exp_output,
                )
            case 'no-frame-light-color-no-fonts' \
                 | 'no-frame-light-color-font-styling-only' \
                 | 'no-frame-light-color-full-font-conf' \
                 | 'no-frame-light-color-no-fonts-no-bg' \
                 | 'no-frame-light-color-font-styling-only-no-bg' \
                 | 'no-frame-light-color-full-font-conf-no-bg':
                return fill_html_page_template(
                    style=murphy_light_style + murphy_light_body_style,
                    data=no_frame_light_color_exp_output,
                    case_id=case_id,
                )
            case 'w-frame-dark-color-w-wrap-auto' \
                 | 'w-frame-dark-color-w-wrap-256' \
                 | 'w-frame-dark-color-w-wrap-truecolor':
                return fill_html_page_template(
                    style=zenburn_dark_style_no_bg + zenburn_dark_body_style_with_bg,
                    data=w_frame_dark_color_exp_output,
                )
            case 'w-frame-dark-color-w-wrap-auto-no-bg' \
                 | 'w-frame-dark-color-w-wrap-256-no-bg' \
                 | 'w-frame-dark-color-w-wrap-truecolor-no-bg':
                return fill_html_page_template(
                    style=zenburn_dark_style_no_bg + zenburn_dark_body_style_no_bg,
                    data=w_frame_dark_color_exp_output,
                )
            case _:
                raise ValueError(f'Unexpected case_id: {case_id}')

    return StylizedPanelOutputExpectations(
        get_output_property=colorized_html_page,
        exp_plain_output_for_case_id=_exp_plain_output_for_case_id,
    )
