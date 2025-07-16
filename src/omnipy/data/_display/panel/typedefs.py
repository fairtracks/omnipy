from typing_extensions import TypeVar

from omnipy.data._display.frame import AnyFrame

FrameT = TypeVar('FrameT', bound=AnyFrame, default=AnyFrame, covariant=True)
OtherFrameT = TypeVar('OtherFrameT', bound=AnyFrame, default=AnyFrame, covariant=True)
FrameInvT = TypeVar('FrameInvT', bound=AnyFrame, default=AnyFrame)
