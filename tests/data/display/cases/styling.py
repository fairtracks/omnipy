from textwrap import dedent
from typing import Annotated, Callable, NamedTuple

import pytest_cases as pc

from omnipy.data._display.config import (ConsoleColorSystem,
                                         DarkLowContrastColorStyles,
                                         HorizontalOverflowMode,
                                         LightLowContrastColorStyles,
                                         OutputConfig,
                                         VerticalOverflowMode)
from omnipy.data._display.dimensions import Dimensions
from omnipy.data._display.frame import Frame
from omnipy.data._display.styling import StylizedMonospacedOutput

# Classes


class OutputTestCase(NamedTuple):
    content: str
    frame: Frame
    config: OutputConfig
    get_output_property: Callable[[StylizedMonospacedOutput], str]
    expected_output: str
    expected_within_frame_width: bool | None
    expected_within_frame_height: bool | None


class OutputTestCaseSetup(NamedTuple):
    case_id: str
    content: str
    frame: Frame | None = None
    config: OutputConfig | None = None


class OutputPropertyExpectations(NamedTuple):
    get_output_property: Callable[[StylizedMonospacedOutput], str]
    expected_output_for_case_id: Callable[[str], str]


# Output test cases


@pc.case(id='word_wrap_horizontal', tags=['overflow_modes'])
def case_word_wrap_horizontal(
    common_content: Annotated[str, pc.fixture],
    output_format_accessor: Annotated[Callable[[StylizedMonospacedOutput], str], pc.fixture],
) -> OutputTestCase:
    return OutputTestCase(
        content=common_content,
        frame=Frame(Dimensions(22, None)),
        config=OutputConfig(horizontal_overflow_mode=HorizontalOverflowMode.WORD_WRAP),
        get_output_property=output_format_accessor,
        expected_output=dedent("""\
            [MyClass({'abc': [123,
            234]}),
             MyClass({'def': [345,
            456]})]
            """),
        expected_within_frame_width=True,
        expected_within_frame_height=None,
    )


@pc.case(id='ellipsis_horizontal', tags=['overflow_modes'])
def case_ellipsis_horizontal(
    common_content: Annotated[str, pc.fixture],
    output_format_accessor: Annotated[Callable[[StylizedMonospacedOutput], str], pc.fixture],
) -> OutputTestCase:
    return OutputTestCase(
        content=common_content,
        frame=Frame(Dimensions(22, None)),
        config=OutputConfig(horizontal_overflow_mode=HorizontalOverflowMode.ELLIPSIS),
        get_output_property=output_format_accessor,
        expected_output=dedent("""\
            [MyClass({'abc': [123…
             MyClass({'def': [345…
            """),
        expected_within_frame_width=True,
        expected_within_frame_height=None,
    )


@pc.case(id='crop_horizontal', tags=['overflow_modes'])
def case_crop_horizontal(
    common_content: Annotated[str, pc.fixture],
    output_format_accessor: Annotated[Callable[[StylizedMonospacedOutput], str], pc.fixture],
) -> OutputTestCase:
    return OutputTestCase(
        content=common_content,
        frame=Frame(Dimensions(22, None)),
        config=OutputConfig(horizontal_overflow_mode=HorizontalOverflowMode.CROP),
        get_output_property=output_format_accessor,
        expected_output=dedent("""\
            [MyClass({'abc': [123,
             MyClass({'def': [345,
            """),
        expected_within_frame_width=True,
        expected_within_frame_height=None,
    )


@pc.case(id='word_wrap_small_frame', tags=['overflow_modes'])
def case_word_wrap_small_frame(
    common_content: Annotated[str, pc.fixture],
    output_format_accessor: Annotated[Callable[[StylizedMonospacedOutput], str], pc.fixture],
) -> OutputTestCase:
    return OutputTestCase(
        content=common_content,
        frame=Frame(Dimensions(10, 8)),
        config=OutputConfig(horizontal_overflow_mode=HorizontalOverflowMode.WORD_WRAP),
        get_output_property=output_format_accessor,
        expected_output=dedent("""\
            [MyClass({
            'abc': 
            [123, 
            234]}),
             MyClass({
            'def': 
            [345, 
            456]})]
            """),  # noqa: W291
        expected_within_frame_width=True,
        expected_within_frame_height=True,
    )


@pc.case(id='word_wrap_crop_bottom', tags=['overflow_modes'])
def case_word_wrap_crop_bottom(
    common_content: Annotated[str, pc.fixture],
    output_format_accessor: Annotated[Callable[[StylizedMonospacedOutput], str], pc.fixture],
) -> OutputTestCase:
    return OutputTestCase(
        content=common_content,
        frame=Frame(Dimensions(10, 4)),
        config=OutputConfig(
            horizontal_overflow_mode=HorizontalOverflowMode.WORD_WRAP,
            vertical_overflow_mode=VerticalOverflowMode.CROP_BOTTOM,
        ),
        get_output_property=output_format_accessor,
        expected_output=dedent("""\
            [MyClass({
            'abc': 
            [123, 
            234]}),
            """),  # noqa: W291
        expected_within_frame_width=True,
        expected_within_frame_height=True,
    )


@pc.case(id='word_wrap_crop_top', tags=['overflow_modes'])
def case_word_wrap_crop_top(
    common_content: Annotated[str, pc.fixture],
    output_format_accessor: Annotated[Callable[[StylizedMonospacedOutput], str], pc.fixture],
) -> OutputTestCase:
    return OutputTestCase(
        content=common_content,
        frame=Frame(Dimensions(10, 1)),
        config=OutputConfig(
            horizontal_overflow_mode=HorizontalOverflowMode.WORD_WRAP,
            vertical_overflow_mode=VerticalOverflowMode.CROP_TOP,
        ),
        get_output_property=output_format_accessor,
        expected_output=dedent("""\
            456]})]
            """),  # noqa: W291
        expected_within_frame_width=True,
        expected_within_frame_height=True,
    )


@pc.parametrize('transparent_background', [False, True])
@pc.case(id='no-frame-default-color', tags=['setup'])
def case_setup_no_frame_or_configs(transparent_background: bool) -> OutputTestCaseSetup:
    return OutputTestCaseSetup(
        case_id='no-frame-default-color' + ('-no-bg' if transparent_background else ''),
        content="MyClass({'abc': [123, 234]})",
        config=OutputConfig(
            console_color_system=ConsoleColorSystem.ANSI_RGB,
            transparent_background=transparent_background),
    )


@pc.parametrize('transparent_background', [False, True])
@pc.case(id='no-frame-light-color', tags=['setup'])
def case_setup_no_frame_color_config(transparent_background: bool) -> OutputTestCaseSetup:
    return OutputTestCaseSetup(
        case_id='no-frame-light-color' + ('-no-bg' if transparent_background else ''),
        content="MyClass({'abc': [123, 234]})",
        config=OutputConfig(
            console_color_system=ConsoleColorSystem.ANSI_RGB,
            color_style=LightLowContrastColorStyles.MURPHY,
            transparent_background=transparent_background),
    )


@pc.parametrize('color_system',
                [ConsoleColorSystem.AUTO, ConsoleColorSystem.ANSI_256, ConsoleColorSystem.ANSI_RGB])
@pc.parametrize('transparent_background', [False, True])
@pc.case(id='w-frame-dark-color-w-wrap', tags=['setup'])
def case_setup_small_frame_color_and_overflow_config(
        color_system: ConsoleColorSystem, transparent_background: bool) -> OutputTestCaseSetup:

    case_id = f'w-frame-dark-color-w-wrap-{color_system.value}' + \
              ('-no-bg' if transparent_background else '')

    return OutputTestCaseSetup(
        case_id=case_id,
        content="MyClass({'abc': [123, 234]})",
        frame=Frame(Dimensions(9, 3)),
        config=OutputConfig(
            console_color_system=color_system,
            color_style=DarkLowContrastColorStyles.ZENBURN,
            transparent_background=transparent_background,
            horizontal_overflow_mode=HorizontalOverflowMode.WORD_WRAP,
            vertical_overflow_mode=VerticalOverflowMode.CROP_TOP,
        ),
    )


# Output property expectations per output test case


@pc.case(id='plain-terminal-output', tags=['expectations'])
def case_expectations_plain_terminal(
    plain_terminal: Annotated[Callable[[StylizedMonospacedOutput], str], pc.fixture]
) -> OutputPropertyExpectations:
    def _expected_output_for_case_id(case_id: str) -> str:
        match case_id:
            case 'no-frame-default-color' \
                 | 'no-frame-default-color-no-bg' \
                 | 'no-frame-light-color' \
                 | 'no-frame-light-color-no-bg':
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

    return OutputPropertyExpectations(
        get_output_property=plain_terminal,
        expected_output_for_case_id=_expected_output_for_case_id,
    )


@pc.case(id='bw-stylized-terminal-output', tags=['expectations'])
def case_expectations_bw_stylized_terminal(
    bw_stylized_terminal: Annotated[Callable[[StylizedMonospacedOutput], str], pc.fixture]
) -> OutputPropertyExpectations:
    def _expected_output_for_case_id(case_id: str) -> str:
        match case_id:
            case 'no-frame-default-color' \
                 | 'no-frame-default-color-no-bg':
                return "MyClass({'abc': [123, 234]})\n"
            case 'no-frame-light-color' \
                 | 'no-frame-light-color-no-bg':
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

    return OutputPropertyExpectations(
        get_output_property=bw_stylized_terminal,
        expected_output_for_case_id=_expected_output_for_case_id,
    )


@pc.case(id='colorized-terminal-output', tags=['expectations'])
def case_expectations_colorized_terminal(
    colorized_terminal: Annotated[Callable[[StylizedMonospacedOutput], str], pc.fixture]
) -> OutputPropertyExpectations:
    def _expected_output_for_case_id(case_id: str) -> str:
        match case_id:
            case 'no-frame-default-color' \
                 | 'no-frame-default-color-no-bg':
                return ("MyClass({\x1b[33m'\x1b[0m\x1b[33mabc\x1b[0m\x1b[33m'\x1b[0m: [\x1b[94m123"
                        '\x1b[0m, \x1b[94m234\x1b[0m]})\n')
            case 'no-frame-light-color':
                return ('\x1b[38;2;0;0;0;48;2;255;255;255mMyClass'
                        '\x1b[0m\x1b[38;2;0;0;0;48;2;255;255;255m('
                        '\x1b[0m\x1b[38;2;0;0;0;48;2;255;255;255m{'
                        "\x1b[0m\x1b[38;2;0;0;0;48;2;224;224;255m'"
                        '\x1b[0m\x1b[38;2;0;0;0;48;2;224;224;255mabc'
                        "\x1b[0m\x1b[38;2;0;0;0;48;2;224;224;255m'"
                        '\x1b[0m\x1b[38;2;0;0;0;48;2;255;255;255m:'
                        '\x1b[0m\x1b[38;2;0;0;0;48;2;255;255;255m '
                        '\x1b[0m\x1b[38;2;0;0;0;48;2;255;255;255m['
                        '\x1b[0m\x1b[1;38;2;102;102;255;48;2;255;255;255m123'
                        '\x1b[0m\x1b[38;2;0;0;0;48;2;255;255;255m,'
                        '\x1b[0m\x1b[38;2;0;0;0;48;2;255;255;255m '
                        '\x1b[0m\x1b[1;38;2;102;102;255;48;2;255;255;255m234'
                        '\x1b[0m\x1b[38;2;0;0;0;48;2;255;255;255m]'
                        '\x1b[0m\x1b[38;2;0;0;0;48;2;255;255;255m}'
                        '\x1b[0m\x1b[38;2;0;0;0;48;2;255;255;255m)'
                        '\x1b[0m\n')
            case 'no-frame-light-color-no-bg':
                return ('\x1b[38;2;0;0;0mMyClass'
                        '\x1b[0m\x1b[38;2;0;0;0m('
                        '\x1b[0m\x1b[38;2;0;0;0m{'
                        "\x1b[0m\x1b[38;2;0;0;0;48;2;224;224;255m'"
                        '\x1b[0m\x1b[38;2;0;0;0;48;2;224;224;255mabc'
                        "\x1b[0m\x1b[38;2;0;0;0;48;2;224;224;255m'"
                        '\x1b[0m\x1b[38;2;0;0;0m:'
                        '\x1b[0m\x1b[38;2;0;0;0m '
                        '\x1b[0m\x1b[38;2;0;0;0m['
                        '\x1b[0m\x1b[1;38;2;102;102;255m123'
                        '\x1b[0m\x1b[38;2;0;0;0m,'
                        '\x1b[0m\x1b[38;2;0;0;0m '
                        '\x1b[0m\x1b[1;38;2;102;102;255m234'
                        '\x1b[0m\x1b[38;2;0;0;0m]'
                        '\x1b[0m\x1b[38;2;0;0;0m}'
                        '\x1b[0m\x1b[38;2;0;0;0m)'
                        '\x1b[0m\n')
            case 'w-frame-dark-color-w-wrap-auto':
                return ("'abc':   \n"
                        '[123,    \n'
                        '234]})   \n')
            case 'w-frame-dark-color-w-wrap-256':
                return ("\x1b[38;5;174;48;5;237m'"
                        '\x1b[0m\x1b[38;5;174;48;5;237mabc'
                        "\x1b[0m\x1b[38;5;174;48;5;237m'"
                        '\x1b[0m\x1b[38;5;230;48;5;237m:'
                        '\x1b[0m\x1b[38;5;188;48;5;237m '
                        '\x1b[0m\x1b[48;5;237m  '
                        '\x1b[0m\n'
                        '\x1b[38;5;230;48;5;237m['
                        '\x1b[0m\x1b[38;5;116;48;5;237m123'
                        '\x1b[0m\x1b[38;5;230;48;5;237m,'
                        '\x1b[0m\x1b[38;5;188;48;5;237m '
                        '\x1b[0m\x1b[48;5;237m   '
                        '\x1b[0m\n'
                        '\x1b[38;5;116;48;5;237m234'
                        '\x1b[0m\x1b[38;5;230;48;5;237m]'
                        '\x1b[0m\x1b[38;5;230;48;5;237m}'
                        '\x1b[0m\x1b[38;5;230;48;5;237m)'
                        '\x1b[0m\x1b[48;5;237m   '
                        '\x1b[0m\n')
            case 'w-frame-dark-color-w-wrap-truecolor':
                return ("\x1b[38;2;204;147;147;48;2;63;63;63m'"
                        '\x1b[0m\x1b[38;2;204;147;147;48;2;63;63;63mabc'
                        "\x1b[0m\x1b[38;2;204;147;147;48;2;63;63;63m'"
                        '\x1b[0m\x1b[38;2;240;239;208;48;2;63;63;63m:'
                        '\x1b[0m\x1b[38;2;220;220;204;48;2;63;63;63m '
                        '\x1b[0m\x1b[48;2;63;63;63m  '
                        '\x1b[0m\n'
                        '\x1b[38;2;240;239;208;48;2;63;63;63m['
                        '\x1b[0m\x1b[38;2;140;208;211;48;2;63;63;63m123'
                        '\x1b[0m\x1b[38;2;240;239;208;48;2;63;63;63m,'
                        '\x1b[0m\x1b[38;2;220;220;204;48;2;63;63;63m '
                        '\x1b[0m\x1b[48;2;63;63;63m   '
                        '\x1b[0m\n'
                        '\x1b[38;2;140;208;211;48;2;63;63;63m234'
                        '\x1b[0m\x1b[38;2;240;239;208;48;2;63;63;63m]'
                        '\x1b[0m\x1b[38;2;240;239;208;48;2;63;63;63m}'
                        '\x1b[0m\x1b[38;2;240;239;208;48;2;63;63;63m)'
                        '\x1b[0m\x1b[48;2;63;63;63m   '
                        '\x1b[0m\n')
            case 'w-frame-dark-color-w-wrap-auto-no-bg':
                return ("'abc': \n"
                        '[123, \n'
                        '234]})\n')
            case 'w-frame-dark-color-w-wrap-256-no-bg':
                return ("\x1b[38;5;174m'"
                        '\x1b[0m\x1b[38;5;174mabc'
                        "\x1b[0m\x1b[38;5;174m'"
                        '\x1b[0m\x1b[38;5;230m:'
                        '\x1b[0m\x1b[38;5;188m '
                        '\x1b[0m\n'
                        '\x1b[38;5;230m[\x1b['
                        '0m\x1b[38;5;116m123'
                        '\x1b[0m\x1b[38;5;230m,'
                        '\x1b[0m\x1b[38;5;188m '
                        '\x1b[0m\n'
                        '\x1b[38;5;116m234'
                        '\x1b[0m\x1b[38;5;230m]'
                        '\x1b[0m\x1b[38;5;230m}'
                        '\x1b[0m\x1b[38;5;230m)'
                        '\x1b[0m\n')
            case 'w-frame-dark-color-w-wrap-truecolor-no-bg':
                return ("\x1b[38;2;204;147;147m'"
                        '\x1b[0m\x1b[38;2;204;147;147mabc'
                        "\x1b[0m\x1b[38;2;204;147;147m'"
                        '\x1b[0m\x1b[38;2;240;239;208m:'
                        '\x1b[0m\x1b[38;2;220;220;204m '
                        '\x1b[0m\n'
                        '\x1b[38;2;240;239;208m['
                        '\x1b[0m\x1b[38;2;140;208;211m123'
                        '\x1b[0m\x1b[38;2;240;239;208m,'
                        '\x1b[0m\x1b[38;2;220;220;204m '
                        '\x1b[0m\n'
                        '\x1b[38;2;140;208;211m234'
                        '\x1b[0m\x1b[38;2;240;239;208m]'
                        '\x1b[0m\x1b[38;2;240;239;208m}'
                        '\x1b[0m\x1b[38;2;240;239;208m)'
                        '\x1b[0m\n')
            case _:
                raise ValueError(f'Unexpected case_id: {case_id}')

    return OutputPropertyExpectations(
        get_output_property=colorized_terminal,
        expected_output_for_case_id=_expected_output_for_case_id,
    )


_FONT_STYLE = (
    "font-family: 'CommitMonoOmnipy', 'Menlo', 'DejaVu Sans Mono', 'Consolas', 'Courier New', "
    "'monospace'; font-size: 14px; font-weight: 450; line-height: 1.35; ")


def _fill_html_page_template(style: str, data: str) -> str:
    HTML_PAGE_TEMPLATE = dedent("""\
        <!DOCTYPE html>
        <html>
          <head>
            <meta charset="UTF-8">
            <style>
              {style}
            </style>
          </head>
          <body>
            <pre><code style="{font_style}">{data}
        </code></pre>
          </body>
        </html>
        """)

    return HTML_PAGE_TEMPLATE.format(style=style, font_style=_FONT_STYLE, data=data)


def _fill_html_tag_template(data: str, color_style: str = '') -> str:
    HTML_TAG_TEMPLATE = ('<pre>'
                         '<code style="{font_style}{color_style}">'
                         '{data}\n'
                         '</code>'
                         '</pre>')

    return HTML_TAG_TEMPLATE.format(font_style=_FONT_STYLE, color_style=color_style, data=data)


@pc.case(id='plain-html-tag-output', tags=['expectations'])
def case_expectations_plain_html_tag(
    plain_html_tag: Annotated[Callable[[StylizedMonospacedOutput], str], pc.fixture]
) -> OutputPropertyExpectations:
    def _expected_output_for_case_id(case_id: str) -> str:
        match case_id:
            case 'no-frame-default-color' \
                 | 'no-frame-default-color-no-bg' \
                 | 'no-frame-light-color' \
                 | 'no-frame-light-color-no-bg':
                return _fill_html_tag_template(data='MyClass({&#x27;abc&#x27;: [123, 234]})')
            case 'w-frame-dark-color-w-wrap-auto' \
                 | 'w-frame-dark-color-w-wrap-256' \
                 | 'w-frame-dark-color-w-wrap-truecolor' \
                 | 'w-frame-dark-color-w-wrap-auto-no-bg' \
                 | 'w-frame-dark-color-w-wrap-256-no-bg' \
                 | 'w-frame-dark-color-w-wrap-truecolor-no-bg':
                return _fill_html_tag_template(data=('&#x27;abc&#x27;: \n'
                                                     '[123, \n'
                                                     '234]})'))
            case _:
                raise ValueError(f'Unexpected case_id: {case_id}')

    return OutputPropertyExpectations(
        get_output_property=plain_html_tag,
        expected_output_for_case_id=_expected_output_for_case_id,
    )


@pc.case(id='bw-stylized-html-tag-output', tags=['expectations'])
def case_expectations_bw_stylized_html_tag(
    bw_stylized_html_tag: Annotated[Callable[[StylizedMonospacedOutput], str], pc.fixture]
) -> OutputPropertyExpectations:
    def _expected_output_for_case_id(case_id: str) -> str:
        match case_id:
            case 'no-frame-default-color' | 'no-frame-default-color-no-bg':
                return _fill_html_tag_template(data='MyClass({&#x27;abc&#x27;: [123, 234]})')
            case 'no-frame-light-color' | 'no-frame-light-color-no-bg':
                return _fill_html_tag_template(
                    data=('MyClass({&#x27;abc&#x27;: ['
                          '<span style="font-weight: bold">123</span>, '
                          '<span style="font-weight: bold">234</span>]})'))
            case 'w-frame-dark-color-w-wrap-auto' \
                 | 'w-frame-dark-color-w-wrap-256' \
                 | 'w-frame-dark-color-w-wrap-truecolor' \
                 | 'w-frame-dark-color-w-wrap-auto-no-bg' \
                 | 'w-frame-dark-color-w-wrap-256-no-bg' \
                 | 'w-frame-dark-color-w-wrap-truecolor-no-bg':
                return _fill_html_tag_template(data=('&#x27;abc&#x27;: \n'
                                                     '[123, \n'
                                                     '234]})'))
            case _:
                raise ValueError(f'Unexpected case_id: {case_id}')

    return OutputPropertyExpectations(
        get_output_property=bw_stylized_html_tag,
        expected_output_for_case_id=_expected_output_for_case_id,
    )


@pc.case(id='colorized-html-tag-output', tags=['expectations'])
def case_expectations_colorized_html_tag(
    colorized_html_tag: Annotated[Callable[[StylizedMonospacedOutput], str], pc.fixture]
) -> OutputPropertyExpectations:

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

    def _expected_output_for_case_id(case_id: str) -> str:
        match case_id:
            case 'no-frame-default-color':
                return _fill_html_tag_template(
                    data=no_frame_default_color_exp_output,
                    color_style=ansi_dark_color_style_with_bg,
                )
            case 'no-frame-default-color-no-bg':
                return _fill_html_tag_template(
                    data=no_frame_default_color_exp_output,
                    color_style=ansi_dark_color_style_no_bg,
                )
            case 'no-frame-light-color':
                return _fill_html_tag_template(
                    data=no_frame_light_color_exp_output,
                    color_style=murphy_light_color_style_with_bg,
                )
            case 'no-frame-light-color-no-bg':
                return _fill_html_tag_template(
                    data=no_frame_light_color_exp_output,
                    color_style=murphy_light_color_style_no_bg,
                )
            case 'w-frame-dark-color-w-wrap-auto' \
                 | 'w-frame-dark-color-w-wrap-256' \
                 | 'w-frame-dark-color-w-wrap-truecolor':
                return _fill_html_tag_template(
                    data=w_frame_dark_color_exp_output,
                    color_style=zenburn_dark_color_style_with_bg,
                )
            case 'w-frame-dark-color-w-wrap-auto-no-bg' \
                 | 'w-frame-dark-color-w-wrap-256-no-bg' \
                 | 'w-frame-dark-color-w-wrap-truecolor-no-bg':
                return _fill_html_tag_template(
                    data=w_frame_dark_color_exp_output,
                    color_style=zenburn_dark_color_style_no_bg,
                )
            case _:
                raise ValueError(f'Unexpected case_id: {case_id}')

    return OutputPropertyExpectations(
        get_output_property=colorized_html_tag,
        expected_output_for_case_id=_expected_output_for_case_id,
    )


@pc.case(id='plain-html-page-output', tags=['expectations'])
def case_expectations_plain_html_page(
    plain_html_page: Annotated[Callable[[StylizedMonospacedOutput], str], pc.fixture]
) -> OutputPropertyExpectations:
    bw_light_body_style = """
      body {
        color: #000000;
        background-color: #ffffff;
      }"""

    def _expected_output_for_case_id(case_id: str) -> str:
        match case_id:
            case 'no-frame-default-color' \
                 | 'no-frame-default-color-no-bg' \
                 | 'no-frame-light-color' \
                 | 'no-frame-light-color-no-bg':
                return _fill_html_page_template(
                    style=bw_light_body_style,
                    data='MyClass({&#x27;abc&#x27;: [123, 234]})',
                )
            case 'no-frame-light-color' \
                 | 'no-frame-light-color-no-bg' \
                 | 'w-frame-dark-color-w-wrap-auto' \
                 | 'w-frame-dark-color-w-wrap-256' \
                 | 'w-frame-dark-color-w-wrap-truecolor'\
                 | 'w-frame-dark-color-w-wrap-auto-no-bg' \
                 | 'w-frame-dark-color-w-wrap-256-no-bg' \
                 | 'w-frame-dark-color-w-wrap-truecolor-no-bg':
                return _fill_html_page_template(
                    style=bw_light_body_style,
                    data=('&#x27;abc&#x27;: \n'
                          '[123, \n'
                          '234]})'),
                )
            case _:
                raise ValueError(f'Unexpected case_id: {case_id}')

    return OutputPropertyExpectations(
        get_output_property=plain_html_page,
        expected_output_for_case_id=_expected_output_for_case_id,
    )


@pc.case(id='bw-stylized-html-page-output', tags=['expectations'])
def case_expectations_bw_stylized_html_page(
    bw_stylized_html_page: Annotated[Callable[[StylizedMonospacedOutput], str], pc.fixture]
) -> OutputPropertyExpectations:
    bold_style = '.r2 {font-weight: bold}'

    bw_light_body_style = """
      body {
        color: #000000;
        background-color: #ffffff;
      }"""

    def _expected_output_for_case_id(case_id: str) -> str:
        match case_id:
            case 'no-frame-default-color' | 'no-frame-default-color-no-bg':
                return _fill_html_page_template(
                    style=bw_light_body_style,
                    data=('MyClass({'
                          '<span class="r1">&#x27;abc&#x27;</span>: ['
                          '<span class="r1">123</span>, '
                          '<span class="r1">234</span>]})'),
                )
            case 'no-frame-light-color' | 'no-frame-light-color-no-bg':
                return _fill_html_page_template(
                    style=bold_style + bw_light_body_style,
                    data=('<span class="r1">MyClass({&#x27;abc&#x27;: [</span>'
                          '<span class="r2">123</span>'
                          '<span class="r1">, </span>'
                          '<span class="r2">234</span>'
                          '<span class="r1">]})</span>'),
                )
            case 'w-frame-dark-color-w-wrap-auto' \
                 | 'w-frame-dark-color-w-wrap-256' \
                 | 'w-frame-dark-color-w-wrap-truecolor'\
                 | 'w-frame-dark-color-w-wrap-auto-no-bg' \
                 | 'w-frame-dark-color-w-wrap-256-no-bg' \
                 | 'w-frame-dark-color-w-wrap-truecolor-no-bg':
                return _fill_html_page_template(
                    style=bw_light_body_style,
                    data=('<span class="r1">&#x27;abc&#x27;: </span>\n'
                          '<span class="r1">[123, </span>\n'
                          '<span class="r1">234]})</span>'),
                )
            case _:
                raise ValueError(f'Unexpected case_id: {case_id}')

    return OutputPropertyExpectations(
        get_output_property=bw_stylized_html_page,
        expected_output_for_case_id=_expected_output_for_case_id,
    )


@pc.case(id='colorized-html-page-output', tags=['expectations'])
def case_expectations_colorized_html_page(
    colorized_html_page: Annotated[Callable[[StylizedMonospacedOutput], str], pc.fixture]
) -> OutputPropertyExpectations:
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

    ansi_dark_body_style = """
      body {
        color: #ffffff;
        background-color: #000000;
      }"""

    murphy_light_body_style = """
      body {
        color: #000000;
        background-color: #ffffff;
      }"""

    zenburn_dark_body_style_with_bg = """
      body {
        color: #dcdccc;
        background-color: #3f3f3f;
      }"""

    zenburn_dark_body_style_no_bg = """
      body {
        color: #dcdccc;
        background-color: #000000;
      }"""

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

    def _expected_output_for_case_id(case_id: str) -> str:
        match case_id:
            case 'no-frame-default-color' | 'no-frame-default-color-no-bg':
                return _fill_html_page_template(
                    style=ansi_dark_style + ansi_dark_body_style,
                    data=no_frame_default_color_exp_output,
                )
            case 'no-frame-light-color' | 'no-frame-light-color-no-bg':
                return _fill_html_page_template(
                    style=murphy_light_style + murphy_light_body_style,
                    data=no_frame_light_color_exp_output,
                )
            case 'w-frame-dark-color-w-wrap-auto' \
                 | 'w-frame-dark-color-w-wrap-256' \
                 | 'w-frame-dark-color-w-wrap-truecolor':
                return _fill_html_page_template(
                    style=zenburn_dark_style_no_bg + zenburn_dark_body_style_with_bg,
                    data=w_frame_dark_color_exp_output,
                )
            case 'w-frame-dark-color-w-wrap-auto-no-bg' \
                 | 'w-frame-dark-color-w-wrap-256-no-bg' \
                 | 'w-frame-dark-color-w-wrap-truecolor-no-bg':
                return _fill_html_page_template(
                    style=zenburn_dark_style_no_bg + zenburn_dark_body_style_no_bg,
                    data=w_frame_dark_color_exp_output,
                )
            case _:
                raise ValueError(f'Unexpected case_id: {case_id}')

    return OutputPropertyExpectations(
        get_output_property=colorized_html_page,
        expected_output_for_case_id=_expected_output_for_case_id,
    )
