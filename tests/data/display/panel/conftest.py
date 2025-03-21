from typing import Annotated, Callable

import pytest_cases as pc

from omnipy.data._display.panel.styling import SyntaxStylizedTextPanel


@pc.fixture
def common_content() -> str:
    return ("[MyClass({'abc': [123, 234]}),\n"
            " MyClass({'def': [345, 456]})]")


@pc.fixture
def plain_terminal() -> Callable[[SyntaxStylizedTextPanel], str]:
    return lambda output: output.plain.terminal


@pc.fixture
def plain_html_tag() -> Callable[[SyntaxStylizedTextPanel], str]:
    return lambda output: output.plain.html_tag


@pc.fixture
def plain_html_page() -> Callable[[SyntaxStylizedTextPanel], str]:
    return lambda output: output.plain.html_page


@pc.fixture
def bw_stylized_terminal() -> Callable[[SyntaxStylizedTextPanel], str]:
    return lambda output: output.bw_stylized.terminal


@pc.fixture
def bw_stylized_html_tag() -> Callable[[SyntaxStylizedTextPanel], str]:
    return lambda output: output.bw_stylized.html_tag


@pc.fixture
def bw_stylized_html_page() -> Callable[[SyntaxStylizedTextPanel], str]:
    return lambda output: output.bw_stylized.html_page


@pc.fixture
def colorized_terminal() -> Callable[[SyntaxStylizedTextPanel], str]:
    return lambda output: output.colorized.terminal


@pc.fixture
def colorized_html_tag() -> Callable[[SyntaxStylizedTextPanel], str]:
    return lambda output: output.colorized.html_tag


@pc.fixture
def colorized_html_page() -> Callable[[SyntaxStylizedTextPanel], str]:
    return lambda output: output.colorized.html_page


@pc.fixture
@pc.parametrize('getter_func',
                [
                    plain_terminal,
                    plain_html_tag,
                    plain_html_page,
                    bw_stylized_terminal,
                    bw_stylized_html_tag,
                    bw_stylized_html_page,
                    colorized_terminal,
                    colorized_html_tag,
                    colorized_html_page
                ])
def output_format_accessor(
    getter_func: Annotated[Callable[[SyntaxStylizedTextPanel], str], pc.fixture]
) -> Callable[[SyntaxStylizedTextPanel], str]:
    """Parametrized fixture that provides access to all output format accessors."""
    return getter_func
