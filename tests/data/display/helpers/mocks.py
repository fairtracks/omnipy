from abc import ABC, abstractmethod
from dataclasses import field
from functools import cached_property
from typing import Any, ClassVar

from typing_extensions import override

from omnipy.data._display.config import OutputConfig
from omnipy.data._display.dimensions import Dimensions, DimensionsWithWidthAndHeight
from omnipy.data._display.frame import AnyFrame, Frame
from omnipy.data._display.helpers import soft_wrap_words
from omnipy.data._display.panel.base import OutputVariant
from omnipy.data._display.panel.draft.base import (DimensionsAwareDraftPanel,
                                                   DraftPanel,
                                                   FullyRenderedDraftPanel)
from omnipy.data._display.panel.styling.output import OutputMode
from omnipy.util import pydantic as pyd


@pyd.dataclass(init=False, frozen=True)
class MockPanelBase(DraftPanel[str, AnyFrame]):
    _dims_aware_panel_cls: ClassVar[type[DimensionsAwareDraftPanel]] = field(init=False)

    def __init__(self, content: str = '', frame=None, title='', constraints=None, config=None):
        super().__init__(
            content=content,
            frame=frame,
            title=title,
            constraints=constraints,
            config=config,
        )

    @override
    def render_next_stage(self) -> DimensionsAwareDraftPanel[Any, AnyFrame]:
        frame_width = self.frame.dims.width if self.frame else None
        if frame_width is None:
            return self._dims_aware_panel_cls(
                content=self.content,
                frame=self.frame,
                title=self.title,
                constraints=self.constraints,
                config=self.config,
            )
        else:
            return self._dims_aware_panel_cls(
                '\n'.join(soft_wrap_words(self.content.split(), frame_width)),
                frame=self.frame,
                title=self.title,
                constraints=self.constraints,
                config=self.config,
            )


@pyd.dataclass(init=False, frozen=True)
class MockDimsAwarePanelBase(DimensionsAwareDraftPanel[Any, AnyFrame], ABC):
    _fully_rendered_panel_cls: ClassVar[type[FullyRenderedDraftPanel]] = field(init=False)

    @override
    def render_next_stage(self) -> FullyRenderedDraftPanel[Any, AnyFrame]:
        return self._fully_rendered_panel_cls(
            content=self.content,
            frame=self.frame,
            title=self.title,
            constraints=self.constraints,
            config=self.config,
        )

    @cached_property
    @abstractmethod
    def _content_lines(self) -> list[str]:
        ...

    @cached_property
    def dims(self) -> DimensionsWithWidthAndHeight:
        return Dimensions(
            width=max(len(line) for line in self._content_lines),
            height=len(self._content_lines),
        )


class MockOutputVariantBase(OutputVariant):
    def __init__(
        self,
        content_lines: list[str],
        frame: Frame,
        config: OutputConfig,
        output_mode: OutputMode.Literals,
    ) -> None:
        self._cropped_lines = self._crop_to_frame(content_lines, frame, config)
        self._output_mode = output_mode

    @abstractmethod
    def _crop_to_frame(
        self,
        lines: list[str],
        frame: Frame,
        config: OutputConfig,
    ) -> list[str]:
        ...


@pyd.dataclass(init=False, frozen=True)
class MockFullyRenderedPanelBase(FullyRenderedDraftPanel[Any, AnyFrame], MockDimsAwarePanelBase):
    _output_variant_cls: ClassVar[type[MockOutputVariantBase]] = field(init=False)

    @cached_property
    def plain(self) -> OutputVariant:
        return self._output_variant_cls(self._content_lines,
                                        self.frame,
                                        self.config,
                                        OutputMode.PLAIN)

    @cached_property
    def bw_stylized(self) -> OutputVariant:
        return self._output_variant_cls(self._content_lines,
                                        self.frame,
                                        self.config,
                                        OutputMode.BW_STYLIZED)

    @cached_property
    def colorized(self) -> OutputVariant:
        return self._output_variant_cls(self._content_lines,
                                        self.frame,
                                        self.config,
                                        OutputMode.COLORIZED)
