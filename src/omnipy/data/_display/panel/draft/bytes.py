from typing import Generic

from omnipy.data._display.panel.draft.base import DraftPanel
from omnipy.data._display.panel.typedefs import FrameT
import omnipy.util._pydantic as pyd


@pyd.dataclass(
    init=False, frozen=True, config=pyd.ConfigDict(extra=pyd.Extra.forbid, validate_all=True))
class BytesDraftPanel(
        DraftPanel[bytes, FrameT],
        Generic[FrameT],
):
    ...
