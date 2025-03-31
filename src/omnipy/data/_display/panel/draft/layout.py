from functools import cached_property
from typing import Generic

from typing_extensions import override

from omnipy.data._display.dimensions import Dimensions
from omnipy.data._display.layout import Layout
from omnipy.data._display.panel.base import FrameT
from omnipy.data._display.panel.draft.monospaced import MonospacedDraftPanel
from omnipy.shared.exceptions import ShouldNotOccurException
import omnipy.util._pydantic as pyd


@pyd.dataclass(
    init=False, frozen=True, config=pyd.ConfigDict(extra=pyd.Extra.forbid, validate_all=True))
class ResizedLayoutDraftPanel(
        MonospacedDraftPanel[Layout, FrameT],
        Generic[FrameT],
):
    @cached_property
    @override
    def dims(self) -> Dimensions[pyd.NonNegativeInt, pyd.NonNegativeInt]:
        dimensions_aware_panels = self.content.render_until_dimensions_aware()
        if dimensions_aware_panels:
            return Dimensions(
                width=(sum(panel.dims.width for panel in dimensions_aware_panels.values())
                       + len(dimensions_aware_panels) * 3 + 1),
                height=max(panel.dims.height for panel in dimensions_aware_panels.values()) + 2,
            )
        else:
            return Dimensions(width=0, height=1)

    @cached_property
    def _content_lines(self) -> list[str]:
        raise ShouldNotOccurException()
