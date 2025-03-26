from functools import cached_property
from typing import cast

from omnipy.data._display.dimensions import Dimensions, DimensionsWithWidthAndHeight
from omnipy.data._display.frame import empty_frame
from omnipy.data._display.panel.base import (DimensionsAwarePanel,
                                             FrameT,
                                             FullyRenderedPanel,
                                             OutputMode,
                                             OutputVariant,
                                             Panel)
import omnipy.util._pydantic as pyd


@pyd.dataclass(init=False, frozen=True)
class MockPanel(Panel):
    content: str = ''

    def __init__(self, content: str = '', frame: FrameT | None = None) -> None:
        object.__setattr__(self, 'content', content)
        object.__setattr__(self, 'frame', frame or cast(FrameT, empty_frame()))

    def render_next_stage(self) -> Panel:
        return MockPanelStage2(self.content)


@pyd.dataclass(init=False, frozen=True)
class MockPanelStage2(DimensionsAwarePanel, MockPanel):
    @pyd.validator('content')
    def words_into_lines(cls, content: str) -> str:
        return '\n'.join(content.split())

    def render_next_stage(self) -> Panel:
        return MockPanelStage3(content=self.content)

    @cached_property
    def dims(self) -> DimensionsWithWidthAndHeight:
        split_lines = self.content.split('\n')
        return Dimensions(width=max(len(line) for line in split_lines), height=len(split_lines))


class MockOutputVariant(OutputVariant):
    def __init__(self, content: str, output_mode: OutputMode) -> None:
        self._content = content
        self._output_mode = output_mode

    @cached_property
    def terminal(self) -> str:
        match self._output_mode:
            case OutputMode.PLAIN:
                return self._content
            case OutputMode.BW_STYLIZED:
                return '\n'.join(f'\x1b[1m{word}\x1b[0m' for word in self._content.split())
            case OutputMode.COLORIZED:
                return '\n'.join(f'\x1b[1;34m{word}\x1b[0m' for word in self._content.split())

    @cached_property
    def html_tag(self) -> str:
        html_core = self._content.replace('\n', '<br>')
        match self._output_mode:
            case OutputMode.PLAIN:
                return html_core
            case OutputMode.BW_STYLIZED:
                return f'<strong>{html_core}</strong>'
            case OutputMode.COLORIZED:
                return f'<strong style="color: blue">{html_core}</strong>'

    @cached_property
    def html_page(self) -> str:
        html_core = self._content.replace('\n', '<br>')
        match self._output_mode:
            case OutputMode.PLAIN:
                return (f'<html><body>'
                        f'{html_core}'
                        f'</body></html>')
            case OutputMode.BW_STYLIZED:
                return (f'<html><body>'
                        f'<strong>{html_core}</strong>'
                        '</body></html>')
            case OutputMode.COLORIZED:
                return (f'<html><body style="color: blue">'
                        f'<strong>{html_core}</strong>'
                        '</body></html>')


@pyd.dataclass(init=False, frozen=True)
class MockPanelStage3(FullyRenderedPanel, MockPanelStage2):
    @cached_property
    def plain(self) -> OutputVariant:
        return MockOutputVariant(self.content, OutputMode.PLAIN)

    @cached_property
    def bw_stylized(self) -> OutputVariant:
        return MockOutputVariant(self.content, OutputMode.BW_STYLIZED)

    @cached_property
    def colorized(self) -> OutputVariant:
        return MockOutputVariant(self.content, OutputMode.COLORIZED)
