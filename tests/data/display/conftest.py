from typing import Annotated

import pytest
import pytest_cases as pc

from omnipy.shared.protocols.hub.runtime import IsRuntime

from .panel.helpers.case_setup import FrameVariant, OutputPropertyType


# Override autouse_runtime_data_config_variants fixture in tests.data.conftest
@pytest.fixture(scope='function', autouse=True)
def autouse_runtime_data_config_variants(
        runtime: Annotated[IsRuntime, pytest.fixture]) -> IsRuntime:
    return runtime


@pc.fixture(scope='function')
@pc.parametrize(
    'frame_variant',
    (
        FrameVariant(True, False),
        FrameVariant(False, True),
        FrameVariant(True, True),
    ),
    ids=('only_width', 'only_height', 'standard'),
)
def per_frame_variant(frame_variant: FrameVariant) -> FrameVariant:
    return frame_variant


@pc.fixture
def plain_terminal() -> OutputPropertyType:
    return lambda output: output.plain.terminal


@pc.fixture
def plain_html_tag() -> OutputPropertyType:
    return lambda output: output.plain.html_tag


@pc.fixture
def plain_html_page() -> OutputPropertyType:
    return lambda output: output.plain.html_page


@pc.fixture
def bw_stylized_terminal() -> OutputPropertyType:
    return lambda output: output.bw_stylized.terminal


@pc.fixture
def bw_stylized_html_tag() -> OutputPropertyType:
    return lambda output: output.bw_stylized.html_tag


@pc.fixture
def bw_stylized_html_page() -> OutputPropertyType:
    return lambda output: output.bw_stylized.html_page


@pc.fixture
def colorized_terminal() -> OutputPropertyType:
    return lambda output: output.colorized.terminal


@pc.fixture
def colorized_html_tag() -> OutputPropertyType:
    return lambda output: output.colorized.html_tag


@pc.fixture
def colorized_html_page() -> OutputPropertyType:
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
        getter_func: Annotated[OutputPropertyType, pc.fixture]) -> OutputPropertyType:
    """Parametrized fixture that provides access to all output format accessors."""
    return getter_func
