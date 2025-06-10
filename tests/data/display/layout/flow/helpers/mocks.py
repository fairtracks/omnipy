from functools import cached_property
from typing import cast, ClassVar

from omnipy.data._display.config import OutputConfig
from omnipy.data._display.frame import Frame
from omnipy.data._display.panel.cropping import (crop_content_line_horizontally,
                                                 crop_content_lines_vertically,
                                                 crop_content_lines_vertically_for_resizing)
from omnipy.data._display.panel.draft.base import DimensionsAwareDraftPanel, FullyRenderedDraftPanel
import omnipy.util._pydantic as pyd

from ....helpers.mocks import (MockDimsAwarePanelBase,
                               MockFullyRenderedPanelBase,
                               MockOutputVariantBase,
                               MockPanelBase)


class MockConfigCropOutputVariant(MockOutputVariantBase):
    def _crop_to_frame(self, lines: list[str], frame: Frame, config: OutputConfig) -> list[str]:
        vert_mode = config.vertical_overflow_mode
        hor_mode = config.horizontal_overflow_mode

        lines = crop_content_lines_vertically(lines, frame.dims.height, vert_mode)
        lines = [crop_content_line_horizontally(_, frame.dims.width, hor_mode) for _ in lines]

        return lines

    @cached_property
    def terminal(self) -> str:
        return '\n'.join(self._cropped_lines)

    @cached_property
    def html_tag(self) -> str:
        return '<br>'.join(self._cropped_lines)

    @cached_property
    def html_page(self) -> str:
        return '<br>'.join(self._cropped_lines)


class SplitAndVerticallyCropContentMixin:
    @cached_property
    def _content_lines(self) -> list[str]:
        _self = cast(DimensionsAwareDraftPanel, self)

        content_lines = _self.content.split('\n')
        content_lines = crop_content_lines_vertically_for_resizing(
            content_lines,
            _self.frame,
            _self.config,
        )
        return content_lines


@pyd.dataclass(init=False, frozen=True)
class MockStylizedConfigCropPanel(SplitAndVerticallyCropContentMixin, MockFullyRenderedPanelBase):
    _output_variant_cls: ClassVar[type[MockOutputVariantBase]] = MockConfigCropOutputVariant


@pyd.dataclass(init=False, frozen=True)
class MockResizedConfigCropPanel(SplitAndVerticallyCropContentMixin, MockDimsAwarePanelBase):
    _fully_rendered_panel_cls: ClassVar[type[FullyRenderedDraftPanel]] = MockStylizedConfigCropPanel


@pyd.dataclass(init=False, frozen=True)
class MockConfigCropPanel(MockPanelBase):
    _dims_aware_panel_cls: ClassVar[type[DimensionsAwareDraftPanel]] = MockResizedConfigCropPanel
