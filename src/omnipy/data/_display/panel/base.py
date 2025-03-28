from abc import ABC, abstractmethod
from functools import cached_property
from typing import cast, Generic

from typing_extensions import TypeIs, TypeVar

from omnipy.data._display.dimensions import Dimensions, DimensionsFit
from omnipy.data._display.frame import AnyFrame, empty_frame, Frame
import omnipy.util._pydantic as pyd

FrameT = TypeVar('FrameT', bound=AnyFrame, default=AnyFrame, covariant=True)


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


@pyd.dataclass(
    init=False,
    frozen=True,
    config=pyd.ConfigDict(extra=pyd.Extra.forbid, validate_assignment=True),
)
class Panel(Generic[FrameT]):
    """Base panel class that only contains frame information."""
    frame: FrameT

    def __init__(self, frame: FrameT | None = None):
        object.__setattr__(self, 'frame', frame or cast(FrameT, empty_frame()))

    @pyd.validator('frame')
    def _copy_frame(cls, frame: Frame) -> Frame:
        return Frame(dims=frame.dims)

    @abstractmethod
    def render_next_stage(self) -> 'Panel[FrameT]':
        ...


def panel_is_dimensions_aware(panel: Panel) -> TypeIs['DimensionsAwarePanel']:
    return isinstance(panel, DimensionsAwarePanel)


def panel_is_fully_rendered(panel: Panel) -> TypeIs['FullyRenderedPanel']:
    return isinstance(panel, FullyRenderedPanel)


class DimensionsAwarePanel(Panel[FrameT], Generic[FrameT]):
    @cached_property
    @abstractmethod
    def dims(self) -> Dimensions[pyd.NonNegativeInt, pyd.NonNegativeInt]:
        ...

    @cached_property
    def within_frame(self) -> DimensionsFit:
        return DimensionsFit(self.dims, self.frame.dims)


class FullyRenderedPanel(DimensionsAwarePanel[FrameT], Generic[FrameT]):
    def render_next_stage(self) -> DimensionsAwarePanel[FrameT]:
        raise NotImplementedError('This panel is fully rendered.')

    @cached_property
    @abstractmethod
    def plain(self) -> OutputVariant:
        """
        Returns an OutputVariant object serving plain text representations
        of the output, without any styling or color. The output is also
        cropped to fit the frame dimensions.
        """

    @cached_property
    @abstractmethod
    def bw_stylized(self) -> OutputVariant:
        """
        Returns an OutputVariant object serving a black-and-white stylized
        representation of the output, allowing formatting such as bold or
        italic, but with no color. The output is also cropped to fit the
        frame dimensions.
        """

    @cached_property
    @abstractmethod
    def colorized(self) -> OutputVariant:
        """
        Returns an OutputVariant object serving a colorized representation
        of the output, with color and styling. The output is also cropped
        to fit the frame dimensions.
        """
