from functools import cached_property
import re
from typing import cast, ClassVar

from omnipy.data._display.config import OutputConfig
from omnipy.data._display.dimensions import has_height, has_width
from omnipy.data._display.frame import AnyFrame, Frame
from omnipy.data._display.panel.draft.base import DimensionsAwareDraftPanel, FullyRenderedDraftPanel
from omnipy.data._display.panel.styling.output import OutputMode
from omnipy.shared.exceptions import ShouldNotOccurException
import omnipy.util._pydantic as pyd

from ...helpers.mocks import (MockDimsAwarePanelBase,
                              MockFullyRenderedPanelBase,
                              MockOutputVariantBase,
                              MockPanelBase)


class MockPlainCropOutputVariant(MockOutputVariantBase):
    def _crop_to_frame(
        self,
        lines: list[str],
        frame: Frame,
        config: OutputConfig,
    ) -> list[str]:
        cropped_lines = []
        for line_num, line in enumerate(lines):
            if has_height(frame.dims) and line_num >= frame.dims.height:
                break
            if has_width(frame.dims) and len(line) > frame.dims.width:
                cropped_lines.append(line[:frame.dims.width])
            else:
                cropped_lines.append(line)
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
            case _:
                raise ShouldNotOccurException(f'Unexpected output mode: {self._output_mode}')

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
            case _:
                raise ShouldNotOccurException(f'Unexpected output mode: {self._output_mode}')

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
            case _:
                raise ShouldNotOccurException(f'Unexpected output mode: {self._output_mode}')


class SplitContentMixin:
    @cached_property
    def _content_lines(self) -> list[str]:
        _self = cast(DimensionsAwareDraftPanel[str, AnyFrame], self)
        return _self.content.split('\n')


@pyd.dataclass(init=False, frozen=True)
class MockStylizedPlainCropPanel(SplitContentMixin, MockFullyRenderedPanelBase):
    _output_variant_cls: ClassVar[type[MockOutputVariantBase]] = MockPlainCropOutputVariant


@pyd.dataclass(init=False, frozen=True)
class MockResizedStylablePlainCropPanel(SplitContentMixin, MockDimsAwarePanelBase):
    _fully_rendered_panel_cls: ClassVar[type[FullyRenderedDraftPanel]] = MockStylizedPlainCropPanel


@pyd.dataclass(init=False, frozen=True)
class MockStylablePlainCropPanel(MockPanelBase):
    _dims_aware_panel_cls: ClassVar[
        type[DimensionsAwareDraftPanel]] = MockResizedStylablePlainCropPanel
