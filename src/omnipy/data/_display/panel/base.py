from abc import ABC, abstractmethod
from enum import Enum
from functools import cached_property
from typing import cast, Generic

from typing_extensions import TypeVar

from omnipy.data._display.frame import AnyFrame, empty_frame, Frame
import omnipy.util._pydantic as pyd

FrameT = TypeVar('FrameT', bound=AnyFrame, default=AnyFrame, covariant=True)


@pyd.dataclass(init=False, config=pyd.ConfigDict(extra=pyd.Extra.forbid, validate_assignment=True))
class Panel(Generic[FrameT]):
    """Base panel class that only contains frame information."""
    frame: FrameT

    def __init__(self, frame: FrameT | None = None):
        self.frame = frame or cast(FrameT, empty_frame())

    @pyd.validator('frame')
    def _copy_frame(cls, frame: Frame) -> Frame:
        return Frame(dims=frame.dims)


class OutputMode(str, Enum):
    PLAIN = 'plain'
    BW_STYLIZED = 'bw_stylized'
    COLORIZED = 'colorized'


class OutputVariant(ABC):
    @cached_property
    @abstractmethod
    def terminal(self) -> str:
        """
        Returns the terminal representation of the output, encoded according
        to the current console color system.
        """

    @cached_property
    @abstractmethod
    def html_tag(self) -> str:
        """
        Returns a representation of the output as an HTML tag for inclusion
        in a web page.
        """

    @cached_property
    @abstractmethod
    def html_page(self) -> str:
        """
        Returns a representation of the output as an independent HTML page,
        for viewing in a web browser.
        """
