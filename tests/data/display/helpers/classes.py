from functools import cached_property

from omnipy.data._display.dimensions import Dimensions, DimensionsWithWidthAndHeight
from omnipy.data._display.frame import AnyFrame
from omnipy.data._display.panel.base import DimensionsAwarePanel, FullyRenderedPanel, OutputVariant
from omnipy.data._display.panel.draft.base import DraftPanel
from omnipy.data._display.panel.styling.output import OutputMode
import omnipy.util._pydantic as pyd


@pyd.dataclass(init=False, frozen=True)
class MockPanel(DraftPanel[str, AnyFrame]):
    def __init__(self, content: str = '', frame=None, constraints=None, config=None):
        super().__init__(content=content, frame=frame, constraints=constraints, config=config)

    def render_next_stage(self) -> 'DimensionsAwarePanel[AnyFrame]':
        return MockPanelStage2(
            '\n'.join(self.content.split()),
            frame=self.frame,
            constraints=self.constraints,
            config=self.config,
        )


@pyd.dataclass(init=False, frozen=True)
class MockPanelStage2(DimensionsAwarePanel, MockPanel):
    def render_next_stage(self) -> FullyRenderedPanel[AnyFrame]:
        return MockPanelStage3(
            content=self.content,
            frame=self.frame,
            constraints=self.constraints,
            config=self.config,
        )

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
