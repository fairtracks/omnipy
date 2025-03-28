import re
from typing import Callable, Generic, TypeAlias

from typing_extensions import NamedTuple, TypeVar

from omnipy.data._display.config import OutputConfig
from omnipy.data._display.frame import Frame
from omnipy.data._display.layout import Layout
from omnipy.data._display.panel.styling.layout import StylizedLayoutPanel
from omnipy.data._display.panel.styling.text import SyntaxStylizedTextPanel

OutputPropertyType: TypeAlias = Callable[[SyntaxStylizedTextPanel | StylizedLayoutPanel], str]
ContentT = TypeVar('ContentT', bound=str | Layout)


class PanelOutputTestCase(NamedTuple, Generic[ContentT]):
    content: ContentT
    frame: Frame | None
    config: OutputConfig | None
    get_output_property: OutputPropertyType
    expected_output: str
    expected_dims_width: int
    expected_dims_height: int
    expected_within_frame_width: bool | None
    expected_within_frame_height: bool | None


class PanelOutputTestCaseSetup(NamedTuple, Generic[ContentT]):
    case_id: str
    content: ContentT
    frame: Frame | None = None
    config: OutputConfig | None = None


class PanelOutputPropertyExpectations(NamedTuple):
    get_output_property: OutputPropertyType
    expected_output_for_case_id: Callable[[str], str]


def _strip_html(html: str) -> str:
    matches = re.findall(r'<code[^>]*>([\S\s]*)</code>', html, re.MULTILINE)
    if not matches:
        return html

    code_no_tags = re.sub(r'<[^>]+>', '', matches[0])

    def _to_char(match: re.Match) -> str:
        import sys
        byte_as_str = match[1]
        return int(byte_as_str, 16).to_bytes(length=1, byteorder=sys.byteorder).decode()

    code_no_escapes = re.sub(r'&#x(\d+);', _to_char, code_no_tags)
    return code_no_escapes


def _strip_ansi(text: str) -> str:
    return re.sub(r'\x1b\[[^m]+m', '', text)


def prepare_panel(
    text_panel: SyntaxStylizedTextPanel | StylizedLayoutPanel,
    get_output_property: OutputPropertyType,
) -> str:
    return _strip_ansi(_strip_html(get_output_property(text_panel)))
