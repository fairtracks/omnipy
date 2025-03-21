from functools import cached_property

from omnipy.data._display.dimensions import Dimensions, DimensionsWithWidthAndHeight
from omnipy.data._display.panel.base import FullyRenderedPanel, OutputMode, OutputVariant, Panel
from omnipy.util import _pydantic as pyd


@pyd.dataclass(init=False)
class MockPanel(Panel):
    contents: str = ''

    def __init__(self, contents: str = '') -> None:
        super().__init__()
        self.contents = contents

    def render_next_stage(self) -> Panel:
        return MockPanelStage2(self.contents)

    def is_fully_rendered(self) -> bool:
        return False

    @cached_property
    def dims(self) -> DimensionsWithWidthAndHeight:
        split_lines = self.contents.split('\n')
        return Dimensions(width=max(len(line) for line in split_lines), height=len(split_lines))


@pyd.dataclass(init=False)
class MockPanelStage2(MockPanel):
    @pyd.validator('contents')
    def words_into_lines(cls, contents: str) -> str:
        return '\n'.join(contents.split())

    def render_next_stage(self) -> Panel:
        return MockPanelStage3(contents=self.contents)

    def is_fully_rendered(self) -> bool:
        return False


class MockOutputVariant(OutputVariant):
    def __init__(self, contents: str, output_mode: OutputMode) -> None:
        self._contents = contents
        self._output_mode = output_mode

    @cached_property
    def terminal(self) -> str:
        match self._output_mode:
            case OutputMode.PLAIN:
                return self._contents
            case OutputMode.BW_STYLIZED:
                return '\n'.join(f'\x1b[1m{word}\x1b[0m' for word in self._contents.split())
            case OutputMode.COLORIZED:
                return '\n'.join(f'\x1b[1;34m{word}\x1b[0m' for word in self._contents.split())

    @cached_property
    def html_tag(self) -> str:
        html_core = self._contents.replace('\n', '<br>')
        match self._output_mode:
            case OutputMode.PLAIN:
                return html_core
            case OutputMode.BW_STYLIZED:
                return f'<strong>{html_core}</strong>'
            case OutputMode.COLORIZED:
                return f'<strong style="color: blue">{html_core}</strong>'

    @cached_property
    def html_page(self) -> str:
        html_core = self._contents.replace('\n', '<br>')
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


@pyd.dataclass(init=False)
class MockPanelStage3(FullyRenderedPanel, MockPanelStage2):
    @cached_property
    def plain(self) -> OutputVariant:
        return MockOutputVariant(self.contents, OutputMode.PLAIN)

    @cached_property
    def bw_stylized(self) -> OutputVariant:
        return MockOutputVariant(self.contents, OutputMode.BW_STYLIZED)

    @cached_property
    def colorized(self) -> OutputVariant:
        return MockOutputVariant(self.contents, OutputMode.COLORIZED)
