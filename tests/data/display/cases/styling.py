from textwrap import dedent
from typing import Callable, NamedTuple

import pytest_cases as pc

from omnipy.data._display.config import (HorizontalOverflowMode,
                                         LightLowContrastColorStyles,
                                         OutputConfig,
                                         VerticalOverflowMode)
from omnipy.data._display.dimensions import Dimensions
from omnipy.data._display.frame import Frame
from omnipy.data._display.styling import StylizedMonospacedOutput

# Classes


class OutputTestCaseSetup(NamedTuple):
    case_id: str
    content: str
    frame: Frame | None = None
    config: OutputConfig | None = None


class OutputPropertyExpectations(NamedTuple):
    get_output_property: Callable[[StylizedMonospacedOutput], str]
    expected_outputs: dict[str, str]


# Output test cases


@pc.parametrize('transparent_background', [False, True])
@pc.case(id='no-frame-no-color', tags=['setup'])
def case_setup_no_frame_or_configs(transparent_background: bool) -> OutputTestCaseSetup:
    return OutputTestCaseSetup(
        case_id='no-frame-no-color' + ('-no-bg' if transparent_background else ''),
        content="MyClass({'abc': [123, 234]})",
        config=OutputConfig(transparent_background=transparent_background),
    )


@pc.parametrize('transparent_background', [False, True])
@pc.case(id='no-frame-w-color', tags=['setup'])
def case_setup_no_frame_color_config(transparent_background: bool) -> OutputTestCaseSetup:
    return OutputTestCaseSetup(
        case_id='no-frame-w-color' + ('-no-bg' if transparent_background else ''),
        content="MyClass({'abc': [123, 234]})",
        config=OutputConfig(
            color_style=LightLowContrastColorStyles.MURPHY,
            transparent_background=transparent_background),
    )


@pc.parametrize('transparent_background', [False, True])
@pc.case(id='w-frame-w-color-w-wrap', tags=['setup'])
def case_setup_small_frame_color_and_overflow_config(
        transparent_background: bool) -> OutputTestCaseSetup:
    return OutputTestCaseSetup(
        case_id='w-frame-w-color-w-wrap' + ('-no-bg' if transparent_background else ''),
        content="MyClass({'abc': [123, 234]})",
        frame=Frame(Dimensions(9, 3)),
        config=OutputConfig(
            color_style=LightLowContrastColorStyles.MURPHY,
            transparent_background=transparent_background,
            horizontal_overflow_mode=HorizontalOverflowMode.WORD_WRAP,
            vertical_overflow_mode=VerticalOverflowMode.CROP_TOP,
        ),
    )


# Output property expectations per output test case


@pc.case(id='plain-terminal', tags=['expectations'])
def case_expectations_plain_terminal() -> OutputPropertyExpectations:
    return OutputPropertyExpectations(
        get_output_property=lambda output: output.plain.terminal,
        expected_outputs={
            'no-frame-no-color': "MyClass({'abc': [123, 234]})\n",
            'no-frame-no-color-no-bg': "MyClass({'abc': [123, 234]})\n",
            'no-frame-w-color': "MyClass({'abc': [123, 234]})\n",
            'no-frame-w-color-no-bg': "MyClass({'abc': [123, 234]})\n",
            'w-frame-w-color-w-wrap': ("'abc':   \n"
                                       '[123,    \n'
                                       '234]})   \n'),
            'w-frame-w-color-w-wrap-no-bg': ("'abc': \n"
                                             '[123, \n'
                                             '234]})\n'),
        },
    )


@pc.case(id='bw-stylized-terminal', tags=['expectations'])
def case_expectations_bw_stylized_terminal() -> OutputPropertyExpectations:
    return OutputPropertyExpectations(
        get_output_property=lambda output: output.bw_stylized.terminal,
        expected_outputs={
            'no-frame-no-color':
                "MyClass({'abc': [123, 234]})\n",
            'no-frame-no-color-no-bg':
                "MyClass({'abc': [123, 234]})\n",
            'no-frame-w-color':
                "MyClass({'abc': [\x1b[1m123\x1b[0m, \x1b[1m234\x1b[0m]})\n",
            'no-frame-w-color-no-bg':
                "MyClass({'abc': [\x1b[1m123\x1b[0m, \x1b[1m234\x1b[0m]})\n",
            'w-frame-w-color-w-wrap': ("'abc':   \n"
                                       '[\x1b[1m123\x1b[0m,    \n'
                                       '\x1b[1m234\x1b[0m]})   \n'),
            'w-frame-w-color-w-wrap-no-bg': ("'abc': \n"
                                             '[\x1b[1m123\x1b[0m, \n'
                                             '\x1b[1m234\x1b[0m]})\n'),
        },
    )


@pc.case(id='colorized-terminal', tags=['expectations'])
def case_expectations_colorized_terminal() -> OutputPropertyExpectations:
    return OutputPropertyExpectations(
        get_output_property=lambda output: output.colorized.terminal,
        expected_outputs={
            'no-frame-no-color':
                ("MyClass({\x1b[33m'\x1b[0m\x1b[33mabc\x1b[0m\x1b[33m'\x1b[0m: [\x1b[94m123"
                 '\x1b[0m, \x1b[94m234\x1b[0m]})\n'),
            'no-frame-no-color-no-bg':
                ("MyClass({\x1b[33m'\x1b[0m\x1b[33mabc\x1b[0m\x1b[33m'\x1b[0m: [\x1b[94m123"
                 '\x1b[0m, \x1b[94m234\x1b[0m]})\n'),
            'no-frame-w-color': ('\x1b[38;2;0;0;0;48;2;255;255;255mMyClass'
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
                                 '\x1b[0m\n'),
            'no-frame-w-color-no-bg': ('\x1b[38;2;0;0;0mMyClass'
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
                                       '\x1b[0m\n'),
            'w-frame-w-color-w-wrap': ("\x1b[38;2;0;0;0;48;2;224;224;255m'"
                                       '\x1b[0m\x1b[38;2;0;0;0;48;2;224;224;255mabc'
                                       "\x1b[0m\x1b[38;2;0;0;0;48;2;224;224;255m'"
                                       '\x1b[0m\x1b[38;2;0;0;0;48;2;255;255;255m:'
                                       '\x1b[0m\x1b[38;2;0;0;0;48;2;255;255;255m '
                                       '\x1b[0m\x1b[48;2;255;255;255m  '
                                       '\x1b[0m\n'
                                       '\x1b[38;2;0;0;0;48;2;255;255;255m['
                                       '\x1b[0m\x1b[1;38;2;102;102;255;48;2;255;255;255m123'
                                       '\x1b[0m\x1b[38;2;0;0;0;48;2;255;255;255m,'
                                       '\x1b[0m\x1b[38;2;0;0;0;48;2;255;255;255m '
                                       '\x1b[0m\x1b[48;2;255;255;255m   '
                                       '\x1b[0m\n'
                                       '\x1b[1;38;2;102;102;255;48;2;255;255;255m234'
                                       '\x1b[0m\x1b[38;2;0;0;0;48;2;255;255;255m]'
                                       '\x1b[0m\x1b[38;2;0;0;0;48;2;255;255;255m}'
                                       '\x1b[0m\x1b[38;2;0;0;0;48;2;255;255;255m)'
                                       '\x1b[0m\x1b[48;2;255;255;255m   '
                                       '\x1b[0m\n'),
            'w-frame-w-color-w-wrap-no-bg': ("\x1b[38;2;0;0;0;48;2;224;224;255m'"
                                             '\x1b[0m\x1b[38;2;0;0;0;48;2;224;224;255mabc'
                                             "\x1b[0m\x1b[38;2;0;0;0;48;2;224;224;255m'"
                                             '\x1b[0m\x1b[38;2;0;0;0m:'
                                             '\x1b[0m\x1b[38;2;0;0;0m '
                                             '\x1b[0m\n'
                                             '\x1b[38;2;0;0;0m['
                                             '\x1b[0m\x1b[1;38;2;102;102;255m123'
                                             '\x1b[0m\x1b[38;2;0;0;0m,'
                                             '\x1b[0m\x1b[38;2;0;0;0m '
                                             '\x1b[0m\n'
                                             '\x1b[1;38;2;102;102;255m234'
                                             '\x1b[0m\x1b[38;2;0;0;0m]'
                                             '\x1b[0m\x1b[38;2;0;0;0m}'
                                             '\x1b[0m\x1b[38;2;0;0;0m)'
                                             '\x1b[0m\n'),
        },
    )


_FONT_STYLE = (
    "font-family: 'CommitMonoOmnipy', 'Menlo', 'DejaVu Sans Mono', 'Consolas', 'Courier New', "
    "'monospace'; font-weight: 450; font-size: 14px; line-height: 1.35")


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
            <pre style="{font_style}"><code style="font-family:inherit">{data}
        </code></pre>
          </body>
        </html>
        """)

    return HTML_PAGE_TEMPLATE.format(style=style, font_style=_FONT_STYLE, data=data)


def _fill_html_tag_template(data: str) -> str:
    HTML_TAG_TEMPLATE = ('<pre style="{font_style}">'
                         '<code style="font-family:inherit">'
                         '{data}\n'
                         '</code>'
                         '</pre>')

    return HTML_TAG_TEMPLATE.format(font_style=_FONT_STYLE, data=data)


@pc.case(id='plain-html-tag', tags=['expectations'])
def case_expectations_plain_html_tag() -> OutputPropertyExpectations:
    return OutputPropertyExpectations(
        get_output_property=lambda output: output.plain.html_tag,
        expected_outputs={
            'no-frame-no-color':
                _fill_html_tag_template(data='MyClass({&#x27;abc&#x27;: [123, 234]})'),
            'no-frame-no-color-no-bg':
                _fill_html_tag_template(data='MyClass({&#x27;abc&#x27;: [123, 234]})'),
            'no-frame-w-color':
                _fill_html_tag_template(data='MyClass({&#x27;abc&#x27;: [123, 234]})'),
            'no-frame-w-color-no-bg':
                _fill_html_tag_template(data='MyClass({&#x27;abc&#x27;: [123, 234]})'),
            'w-frame-w-color-w-wrap':
                _fill_html_tag_template(data=('&#x27;abc&#x27;:   \n'
                                              '[123,    \n'
                                              '234]})   '),),
            'w-frame-w-color-w-wrap-no-bg':
                _fill_html_tag_template(data=('&#x27;abc&#x27;: \n'
                                              '[123, \n'
                                              '234]})'),),
        },
    )


@pc.case(id='bw-stylized-html-tag', tags=['expectations'])
def case_expectations_bw_stylized_html_tag() -> OutputPropertyExpectations:
    return OutputPropertyExpectations(
        get_output_property=lambda output: output.bw_stylized.html_tag,
        expected_outputs={
            'no-frame-no-color':
                _fill_html_tag_template(data='MyClass({&#x27;abc&#x27;: [123, 234]})'),
            'no-frame-no-color-no-bg':
                _fill_html_tag_template(data='MyClass({&#x27;abc&#x27;: [123, 234]})'),
            'no-frame-w-color':
                _fill_html_tag_template(
                    data=('MyClass({&#x27;abc&#x27;: ['
                          '<span style="font-weight: bold">123</span>, '
                          '<span style="font-weight: bold">234</span>]})')),
            'no-frame-w-color-no-bg':
                _fill_html_tag_template(
                    data=('MyClass({&#x27;abc&#x27;: ['
                          '<span style="font-weight: bold">123</span>, '
                          '<span style="font-weight: bold">234</span>]})')),
            'w-frame-w-color-w-wrap':
                _fill_html_tag_template(
                    data=('&#x27;abc&#x27;:   \n'
                          '[<span style="font-weight: bold">123</span>,    \n'
                          '<span style="font-weight: bold">234</span>]})   '),),
            'w-frame-w-color-w-wrap-no-bg':
                _fill_html_tag_template(
                    data=('&#x27;abc&#x27;: \n'
                          '[<span style="font-weight: bold">123</span>, \n'
                          '<span style="font-weight: bold">234</span>]})'),),
        },
    )


@pc.case(id='colorized-html-tag', tags=['expectations'])
def case_expectations_colorized_html_tag() -> OutputPropertyExpectations:
    return OutputPropertyExpectations(
        get_output_property=lambda output: output.colorized.html_tag,
        expected_outputs={
            'no-frame-no-color':
                _fill_html_tag_template(
                    data=(
                        'MyClass({'
                        '<span style="color: #808000; text-decoration-color: #808000">'
                        '&#x27;abc&#x27;</span>: ['
                        '<span style="color: #0000ff; text-decoration-color: #0000ff">123</span>, '
                        '<span style="color: #0000ff; text-decoration-color: #0000ff">234</span>]})'
                    )),
            'no-frame-no-color-no-bg':
                _fill_html_tag_template(
                    data=(
                        'MyClass({'
                        '<span style="color: #808000; text-decoration-color: #808000">'
                        '&#x27;abc&#x27;</span>: ['
                        '<span style="color: #0000ff; text-decoration-color: #0000ff">123</span>, '
                        '<span style="color: #0000ff; text-decoration-color: #0000ff">234</span>]})'
                    )),
            'no-frame-w-color':
                _fill_html_tag_template(
                    data=('<span style="color: #000000; text-decoration-color: #000000; '
                          'background-color: #ffffff">MyClass({</span>'
                          '<span style="color: #000000; text-decoration-color: #000000; '
                          'background-color: #e0e0ff">&#x27;abc&#x27;</span>'
                          '<span style="color: #000000; text-decoration-color: #000000; '
                          'background-color: #ffffff">: [</span>'
                          '<span style="color: #6666ff; text-decoration-color: #6666ff; '
                          'background-color: #ffffff; font-weight: bold">123</span>'
                          '<span style="color: #000000; text-decoration-color: #000000; '
                          'background-color: #ffffff">, </span>'
                          '<span style="color: #6666ff; text-decoration-color: #6666ff; '
                          'background-color: #ffffff; font-weight: bold">234</span>'
                          '<span style="color: #000000; text-decoration-color: #000000; '
                          'background-color: #ffffff">]})</span>')),
            'no-frame-w-color-no-bg':
                _fill_html_tag_template(
                    data=('<span style="color: #000000; text-decoration-color: #000000">'
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
                ),
            'w-frame-w-color-w-wrap':
                _fill_html_tag_template(
                    data=('<span style="color: #000000; text-decoration-color: #000000; '
                          'background-color: #e0e0ff">&#x27;abc&#x27;</span>'
                          '<span style="color: #000000; text-decoration-color: #000000; '
                          'background-color: #ffffff">: </span>'
                          '<span style="background-color: #ffffff">  </span>\n'
                          '<span style="color: #000000; text-decoration-color: #000000; '
                          'background-color: #ffffff">[</span>'
                          '<span style="color: #6666ff; text-decoration-color: #6666ff; '
                          'background-color: #ffffff; font-weight: bold">123</span>'
                          '<span style="color: #000000; text-decoration-color: #000000; '
                          'background-color: #ffffff">, </span>'
                          '<span style="background-color: #ffffff">   </span>\n'
                          '<span style="color: #6666ff; text-decoration-color: #6666ff; '
                          'background-color: #ffffff; font-weight: bold">234</span>'
                          '<span style="color: #000000; text-decoration-color: #000000; '
                          'background-color: #ffffff">]})</span>'
                          '<span style="background-color: #ffffff">   </span>')),
            'w-frame-w-color-w-wrap-no-bg':
                _fill_html_tag_template(
                    data=('<span style="color: #000000; text-decoration-color: #000000; '
                          'background-color: #e0e0ff">&#x27;abc&#x27;</span>'
                          '<span style="color: #000000; text-decoration-color: #000000">: </span>\n'
                          '<span style="color: #000000; text-decoration-color: #000000">[</span>'
                          '<span style="color: #6666ff; text-decoration-color: #6666ff; '
                          'font-weight: bold">123</span>'
                          '<span style="color: #000000; text-decoration-color: #000000">, </span>\n'
                          '<span style="color: #6666ff; text-decoration-color: #6666ff; '
                          'font-weight: bold">234</span>'
                          '<span style="color: #000000; text-decoration-color: #000000">]})</span>')
                ),
        },
    )


@pc.case(id='plain-html-page', tags=['expectations'])
def case_expectations_plain_html_page() -> OutputPropertyExpectations:
    body_style = """
      body {
        color: #000000;
        background-color: #ffffff;
      }"""

    return OutputPropertyExpectations(
        get_output_property=lambda output: output.plain.html_page,
        expected_outputs={
            'no-frame-no-color':
                _fill_html_page_template(
                    style=body_style,
                    data='MyClass({&#x27;abc&#x27;: [123, 234]})',
                ),
            'no-frame-no-color-no-bg':
                _fill_html_page_template(
                    style=body_style,
                    data='MyClass({&#x27;abc&#x27;: [123, 234]})',
                ),
            'no-frame-w-color':
                _fill_html_page_template(
                    style=body_style,
                    data='MyClass({&#x27;abc&#x27;: [123, 234]})',
                ),
            'no-frame-w-color-no-bg':
                _fill_html_page_template(
                    style=body_style,
                    data='MyClass({&#x27;abc&#x27;: [123, 234]})',
                ),
            'w-frame-w-color-w-wrap':
                _fill_html_page_template(
                    style=body_style, data=('&#x27;abc&#x27;:   \n'
                                            '[123,    \n'
                                            '234]})   ')),
            'w-frame-w-color-w-wrap-no-bg':
                _fill_html_page_template(
                    style=body_style, data=('&#x27;abc&#x27;: \n'
                                            '[123, \n'
                                            '234]})')),
        },
    )


@pc.case(id='bw-stylized-html-page', tags=['expectations'])
def case_expectations_bw_stylized_html_page() -> OutputPropertyExpectations:
    bold_style = '.r2 {font-weight: bold}'

    body_style = """
      body {
        color: #000000;
        background-color: #ffffff;
      }"""

    return OutputPropertyExpectations(
        get_output_property=lambda output: output.bw_stylized.html_page,
        expected_outputs={
            'no-frame-no-color':
                _fill_html_page_template(
                    style=body_style,
                    data=('MyClass({'
                          '<span class="r1">&#x27;abc&#x27;</span>: ['
                          '<span class="r1">123</span>, '
                          '<span class="r1">234</span>]})'),
                ),
            'no-frame-no-color-no-bg':
                _fill_html_page_template(
                    style=body_style,
                    data=('MyClass({'
                          '<span class="r1">&#x27;abc&#x27;</span>: ['
                          '<span class="r1">123</span>, '
                          '<span class="r1">234</span>]})'),
                ),
            'no-frame-w-color':
                _fill_html_page_template(
                    style=bold_style + body_style,
                    data=('<span class="r1">MyClass({&#x27;abc&#x27;: [</span>'
                          '<span class="r2">123</span>'
                          '<span class="r1">, </span>'
                          '<span class="r2">234</span>'
                          '<span class="r1">]})</span>'),
                ),
            'no-frame-w-color-no-bg':
                _fill_html_page_template(
                    style=bold_style + body_style,
                    data=('<span class="r1">MyClass({&#x27;abc&#x27;: [</span>'
                          '<span class="r2">123</span>'
                          '<span class="r1">, </span>'
                          '<span class="r2">234</span>'
                          '<span class="r1">]})</span>'),
                ),
            'w-frame-w-color-w-wrap':
                _fill_html_page_template(
                    style=bold_style + body_style,
                    data=('<span class="r1">&#x27;abc&#x27;: </span>'
                          '<span class="r1">  </span>\n'
                          '<span class="r1">[</span>'
                          '<span class="r2">123</span>'
                          '<span class="r1">, </span>'
                          '<span class="r1">   </span>\n'
                          '<span class="r2">234</span>'
                          '<span class="r1">]})</span>'
                          '<span class="r1">   </span>'),
                ),
            'w-frame-w-color-w-wrap-no-bg':
                _fill_html_page_template(
                    style=bold_style + body_style,
                    data=('<span class="r1">&#x27;abc&#x27;: </span>\n'
                          '<span class="r1">[</span>'
                          '<span class="r2">123</span>'
                          '<span class="r1">, </span>\n'
                          '<span class="r2">234</span>'
                          '<span class="r1">]})</span>'),
                ),
        },
    )


@pc.case(id='colorized-html-page', tags=['expectations'])
def case_expectations_colorized_html_page() -> OutputPropertyExpectations:
    ansi_light_style_no_bg = '\n'.join([
        '.r1 {color: #808000; text-decoration-color: #808000}',
        '.r2 {color: #0000ff; text-decoration-color: #0000ff}',
    ])

    murphy_style_with_bg = '\n'.join([
        '.r1 {color: #000000; text-decoration-color: #000000; background-color: #ffffff}',
        '.r2 {color: #000000; text-decoration-color: #000000; background-color: #e0e0ff}',
        ('.r3 {color: #6666ff; text-decoration-color: #6666ff; background-color: #ffffff; '
         'font-weight: bold}'),
    ])

    murphy_style_with_bg_extra_space = '\n'.join([
        '.r1 {color: #000000; text-decoration-color: #000000; background-color: #ffffff}',
        '.r2 {color: #000000; text-decoration-color: #000000; background-color: #e0e0ff}',
        '.r3 {background-color: #ffffff}',
        ('.r4 {color: #6666ff; text-decoration-color: #6666ff; background-color: #ffffff; '
         'font-weight: bold}'),
    ])

    murphy_style_no_bg = '\n'.join([
        '.r1 {color: #000000; text-decoration-color: #000000}',
        '.r2 {color: #000000; text-decoration-color: #000000; background-color: #e0e0ff}',
        '.r3 {color: #6666ff; text-decoration-color: #6666ff; font-weight: bold}',
    ])

    body_style = """
      body {
        color: #000000;
        background-color: #ffffff;
      }"""

    return OutputPropertyExpectations(
        get_output_property=lambda output: output.colorized.html_page,
        expected_outputs={
            'no-frame-no-color':
                _fill_html_page_template(
                    style=ansi_light_style_no_bg + body_style,
                    data=('MyClass({'
                          '<span class="r1">&#x27;abc&#x27;</span>: ['
                          '<span class="r2">123</span>, '
                          '<span class="r2">234</span>]})'),
                ),
            'no-frame-no-color-no-bg':
                _fill_html_page_template(
                    style=ansi_light_style_no_bg + body_style,
                    data=('MyClass({'
                          '<span class="r1">&#x27;abc&#x27;</span>: ['
                          '<span class="r2">123</span>, '
                          '<span class="r2">234</span>]})'),
                ),
            'no-frame-w-color':
                _fill_html_page_template(
                    style=murphy_style_with_bg + body_style,
                    data=('<span class="r1">MyClass({</span>'
                          '<span class="r2">&#x27;abc&#x27;</span>'
                          '<span class="r1">: [</span>'
                          '<span class="r3">123</span>'
                          '<span class="r1">, </span>'
                          '<span class="r3">234</span>'
                          '<span class="r1">]})</span>'),
                ),
            'no-frame-w-color-no-bg':
                _fill_html_page_template(
                    style=murphy_style_no_bg + body_style,
                    data=('<span class="r1">MyClass({</span>'
                          '<span class="r2">&#x27;abc&#x27;</span>'
                          '<span class="r1">: [</span>'
                          '<span class="r3">123</span>'
                          '<span class="r1">, </span>'
                          '<span class="r3">234</span>'
                          '<span class="r1">]})</span>'),
                ),
            'w-frame-w-color-w-wrap':
                _fill_html_page_template(
                    style=murphy_style_with_bg_extra_space + body_style,
                    data=('<span class="r2">&#x27;abc&#x27;</span>'
                          '<span class="r1">: </span>'
                          '<span class="r3">  </span>\n'
                          '<span class="r1">[</span>'
                          '<span class="r4">123</span>'
                          '<span class="r1">, </span>'
                          '<span class="r3">   </span>\n'
                          '<span class="r4">234</span>'
                          '<span class="r1">]})</span>'
                          '<span class="r3">   </span>'),
                ),
            'w-frame-w-color-w-wrap-no-bg':
                _fill_html_page_template(
                    style=murphy_style_no_bg + body_style,
                    data=('<span class="r2">&#x27;abc&#x27;</span>'
                          '<span class="r1">: </span>\n'
                          '<span class="r1">[</span>'
                          '<span class="r3">123</span>'
                          '<span class="r1">, </span>\n'
                          '<span class="r3">234</span>'
                          '<span class="r1">]})</span>'),
                ),
        },
    )
