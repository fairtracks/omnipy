from functools import cached_property
import re

from omnipy.data._display.dimensions import Dimensions, DimensionsWithWidthAndHeight, has_height
from omnipy.data._display.frame import AnyFrame, Frame
from omnipy.data._display.helpers import soft_wrap_words, UnicodeCharWidthMap
from omnipy.data._display.panel.base import DimensionsAwarePanel, FullyRenderedPanel, OutputVariant
from omnipy.data._display.panel.draft.base import DraftPanel
from omnipy.data._display.panel.draft.monospaced import (crop_content_lines_for_resizing,
                                                         crop_content_with_extra_wide_chars)
from omnipy.data._display.panel.styling.output import OutputMode
import omnipy.util._pydantic as pyd


@pyd.dataclass(init=False, frozen=True)
class MockPanel(DraftPanel[str, AnyFrame]):
    def __init__(self, content: str = '', frame=None, constraints=None, config=None):
        super().__init__(content=content, frame=frame, constraints=constraints, config=config)

    def render_next_stage(self) -> 'DimensionsAwarePanel[AnyFrame]':
        frame_width = self.frame.dims.width if self.frame else None
        if frame_width is None:
            return MockPanelStage2(
                content=self.content,
                frame=self.frame,
                constraints=self.constraints,
                config=self.config,
            )
        else:
            return MockPanelStage2(
                '\n'.join(soft_wrap_words(self.content.split(), frame_width)),
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
    def _content_lines(self) -> list[str]:
        all_content_lines = self.content.split('\n')
        all_content_lines = crop_content_lines_for_resizing(all_content_lines, self.frame)
        all_content_lines = crop_content_with_extra_wide_chars(
            all_content_lines,
            self.frame,
            self.config,
            UnicodeCharWidthMap(),
        )
        return all_content_lines

    @cached_property
    def dims(self) -> DimensionsWithWidthAndHeight:
        return Dimensions(
            width=max(len(line) for line in self._content_lines),
            height=len(self._content_lines),
        )


class MockOutputVariant(OutputVariant):
    def __init__(self, content_lines: list[str], frame: Frame, output_mode: OutputMode) -> None:
        self._cropped_lines = self._crop_to_frame(content_lines, frame)
        self._output_mode = output_mode

    def _crop_to_frame(self, content_lines: list[str], frame: Frame) -> list[str]:
        cropped_lines = []
        for line_num, line in enumerate(content_lines):
            if has_height(frame.dims) and line_num >= frame.dims.height:
                break
            else:
                cropped_lines.append(line[:frame.dims.width])
        return cropped_lines

    @cached_property
    def terminal(self) -> str:
        content = '\n'.join(self._cropped_lines)
        match self._output_mode:
            case OutputMode.PLAIN:
                return content
            case OutputMode.BW_STYLIZED:
                return re.sub(r'(\S+)', '\x1b[1m\\1\x1b[0m', content)
            case OutputMode.COLORIZED:
                return re.sub(r'(\S+)', '\x1b[1;34m\\1\x1b[0m', content)

    @cached_property
    def html_tag(self) -> str:
        html_core = '<br>'.join(self._cropped_lines)
        match self._output_mode:
            case OutputMode.PLAIN:
                return html_core
            case OutputMode.BW_STYLIZED:
                return f'<strong>{html_core}</strong>'
            case OutputMode.COLORIZED:
                return f'<strong style="color: blue">{html_core}</strong>'

    @cached_property
    def html_page(self) -> str:
        html_core = '<br>'.join(self._cropped_lines)
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
        return MockOutputVariant(self._content_lines, self.frame, OutputMode.PLAIN)

    @cached_property
    def bw_stylized(self) -> OutputVariant:
        return MockOutputVariant(self._content_lines, self.frame, OutputMode.BW_STYLIZED)

    @cached_property
    def colorized(self) -> OutputVariant:
        return MockOutputVariant(self._content_lines, self.frame, OutputMode.COLORIZED)
