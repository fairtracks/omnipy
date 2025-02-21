from textwrap import dedent
from typing import Callable, NamedTuple

import pytest_cases as pc

from omnipy.data._display.config import (HorizontalOverflowMode,
                                         LowerContrastLightColorStyles,
                                         OutputConfig,
                                         VerticalOverflowMode)
from omnipy.data._display.dimensions import Dimensions
from omnipy.data._display.frame import Frame
from omnipy.data._display.styling import StylizedMonospacedOutput

# Classes


class OutputTestCaseSetup(NamedTuple):
    case_index: int
    content: str
    frame: Frame | None = None
    config: OutputConfig | None = None


class OutputPropertyExpectations(NamedTuple):
    get_output_property: Callable[[StylizedMonospacedOutput], str]
    expected_outputs: list[str]


# Output test cases


@pc.case(id='no-frame-or-configs', tags=['setup'])
def case_setup_no_frame_or_configs() -> OutputTestCaseSetup:
    return OutputTestCaseSetup(
        case_index=0,
        content="MyClass({'abc': [123, 234]})",
    )


@pc.case(id='no-frame-color-config', tags=['setup'])
def case_setup_no_frame_color_config() -> OutputTestCaseSetup:
    return OutputTestCaseSetup(
        case_index=1,
        content="MyClass({'abc': [123, 234]})",
        config=OutputConfig(color_style=LowerContrastLightColorStyles.MURPHY),
    )


@pc.case(id='small-frame-color-and-overflow-config', tags=['setup'])
def case_setup_small_frame_color_and_overflow_config() -> OutputTestCaseSetup:
    return OutputTestCaseSetup(
        case_index=2,
        content="MyClass({'abc': [123, 234]})",
        frame=Frame(Dimensions(9, 3)),
        config=OutputConfig(
            color_style=LowerContrastLightColorStyles.MURPHY,
            horizontal_overflow_mode=HorizontalOverflowMode.WORD_WRAP,
            vertical_overflow_mode=VerticalOverflowMode.CROP_TOP,
        ),
    )


# Output property expectations per output test case


@pc.case(id='plain-terminal', tags=['expectations'])
def case_expectations_plain_terminal() -> OutputPropertyExpectations:
    return OutputPropertyExpectations(
        get_output_property=lambda output: output.plain.terminal,
        expected_outputs=[
            "MyClass({'abc': [123, 234]})\n",
            "MyClass({'abc': [123, 234]})\n",
            dedent("""\
                'abc': 
                [123, 
                234]})
                """),  # noqa: W291
        ],
    )


@pc.case(id='bw-stylized-terminal', tags=['expectations'])
def case_expectations_bw_stylized_terminal() -> OutputPropertyExpectations:
    return OutputPropertyExpectations(
        get_output_property=lambda output: output.bw_stylized.terminal,
        expected_outputs=[
            "MyClass({'abc': [123, 234]})\n",
            "MyClass({'abc': [\x1b[1m123\x1b[0m, \x1b[1m234\x1b[0m]})\n",
            dedent("""\
                'abc': 
                [\x1b[1m123\x1b[0m, 
                \x1b[1m234\x1b[0m]})
                """),  # noqa: W291
        ],
    )


@pc.case(id='colorized-terminal', tags=['expectations'])
def case_expectations_colorized_terminal() -> OutputPropertyExpectations:
    return OutputPropertyExpectations(
        get_output_property=lambda output: output.colorized.terminal,
        expected_outputs=[
            ("\x1b[49mMyClass({\x1b[0m\x1b[33;49m'\x1b[0m\x1b[33;49mabc\x1b[0m\x1b[33;49m'"
             '\x1b[0m\x1b[49m: [\x1b[0m\x1b[34;49m123\x1b[0m\x1b[49m, \x1b[0m\x1b[34;49m234'
             '\x1b[0m\x1b[49m]})\x1b[0m\n'),
            ('\x1b[38;2;0;0;0;49mMyClass\x1b[0m\x1b[38;2;0;0;0;49m(\x1b[0m\x1b[38;2;0;0;0;49m{'
             "\x1b[0m\x1b[38;2;0;0;0;49m'\x1b[0m\x1b[38;2;0;0;0;49mabc\x1b[0m\x1b[38;2;0;0;0;49m'"
             '\x1b[0m\x1b[38;2;0;0;0;49m:\x1b[0m\x1b[38;2;0;0;0;49m \x1b[0m\x1b[38;2;0;0;0;49m['
             '\x1b[0m\x1b[1;38;2;102;102;255;49m123\x1b[0m\x1b[38;2;0;0;0;49m,'
             '\x1b[0m\x1b[38;2;0;0;0;49m \x1b[0m\x1b[1;38;2;102;102;255;49m234'
             '\x1b[0m\x1b[38;2;0;0;0;49m]\x1b[0m\x1b[38;2;0;0;0;49m}\x1b[0m\x1b[38;2;0;0;0;49m)'
             '\x1b[0m\n'),
            ("\x1b[38;2;0;0;0;49m'\x1b[0m\x1b[38;2;0;0;0;49mabc\x1b[0m\x1b[38;2;0;0;0;49m'"
             '\x1b[0m\x1b[38;2;0;0;0;49m:\x1b[0m\x1b[38;2;0;0;0;49m \x1b[0m\n'
             '\x1b[38;2;0;0;0;49m[\x1b[0m\x1b[1;38;2;102;102;255;49m123'
             '\x1b[0m\x1b[38;2;0;0;0;49m,\x1b[0m\x1b[38;2;0;0;0;49m \x1b[0m\n'
             '\x1b[1;38;2;102;102;255;49m234\x1b[0m\x1b[38;2;0;0;0;49m]'
             '\x1b[0m\x1b[38;2;0;0;0;49m}\x1b[0m\x1b[38;2;0;0;0;49m)\x1b[0m\n'),
        ],
    )


def _fill_full_html_template(style: str, data: str) -> str:
    FULL_HTML_TEMPLATE = dedent("""\
        <!DOCTYPE html>
        <html>
        <head>
        <meta charset="UTF-8">
        <style>
        {style}
        </style>
        </head>
        <body>
            <pre style="font-family:{font_family}"><code style="font-family:inherit">{data}
        </code></pre>
        </body>
        </html>
        """)

    font_family = "Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"

    return FULL_HTML_TEMPLATE.format(style=style, font_family=font_family, data=data)


@pc.case(id='plain-full-html', tags=['expectations'])
def case_expectations_plain_full_html() -> OutputPropertyExpectations:
    body_style = dedent("""
        body {
            color: #000000;
            background-color: #ffffff;
        }""")

    return OutputPropertyExpectations(
        get_output_property=lambda output: output.plain.html,
        expected_outputs=[
            _fill_full_html_template(
                style=body_style,
                data='MyClass({&#x27;abc&#x27;: [123, 234]})',
            ),
            _fill_full_html_template(
                style=body_style,
                data='MyClass({&#x27;abc&#x27;: [123, 234]})',
            ),
            _fill_full_html_template(
                style=body_style,
                data=dedent("""\
                    MyClass({
                    &#x27;abc&#x27;: 
                    [123, 
                    234]})"""),  # noqa: W291
            ),
        ],
    )


@pc.case(id='bw-stylized-full-html', tags=['expectations'])
def case_expectations_bw_stylized_full_html() -> OutputPropertyExpectations:
    body_style = dedent("""
        body {
            color: #000000;
            background-color: #ffffff;
        }""")
    bold_plus_body_style = '.r2 {font-weight: bold}' + body_style

    return OutputPropertyExpectations(
        get_output_property=lambda output: output.bw_stylized.html,
        expected_outputs=[
            _fill_full_html_template(
                style=body_style,
                data='<span class="r1">MyClass({&#x27;abc&#x27;: [123, 234]})</span>',
            ),
            _fill_full_html_template(
                style=bold_plus_body_style,
                data=('<span class="r1">MyClass({&#x27;abc&#x27;: [</span>'
                      '<span class="r2">123</span>'
                      '<span class="r1">, </span>'
                      '<span class="r2">234</span>'
                      '<span class="r1">]})</span>'),
            ),
            _fill_full_html_template(
                style=bold_plus_body_style,
                data=dedent("""\
                    <span class="r1">MyClass({</span>
                    <span class="r1">&#x27;abc&#x27;: </span>
                    <span class="r1">[</span><span class="r2">123</span><span class="r1">, </span>
                    <span class="r2">234</span><span class="r1">]})</span>"""),
            ),
        ],
    )
