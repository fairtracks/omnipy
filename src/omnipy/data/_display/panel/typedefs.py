from typing_extensions import TypeVar

from omnipy.data._display.frame import AnyFrame

FrameT = TypeVar('FrameT', bound=AnyFrame, default=AnyFrame, covariant=True)
OtherFrameT = TypeVar('OtherFrameT', bound=AnyFrame, default=AnyFrame, covariant=True)
FrameInvT = TypeVar('FrameInvT', bound=AnyFrame, default=AnyFrame)
ContentT = TypeVar('ContentT', bound=object, default=object, covariant=True)
ContentInvT = TypeVar('ContentInvT', bound=object, default=object)
