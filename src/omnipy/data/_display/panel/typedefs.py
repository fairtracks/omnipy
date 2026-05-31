"""Generic type variables shared by panel, frame, and content abstractions.

Type Aliases:
    FrameT: Covariant frame type parameter.
    OtherFrameT: Secondary covariant frame type parameter.
    FrameInvT: Invariant frame type parameter for constructors and copying.
    ContentT: Covariant content type parameter.
    ContentInvT: Invariant content type parameter for copying.
"""

from typing_extensions import TypeVar

from omnipy.data._display.frame import AnyFrame

FrameT = TypeVar('FrameT', bound=AnyFrame, default=AnyFrame, covariant=True)
OtherFrameT = TypeVar('OtherFrameT', bound=AnyFrame, default=AnyFrame, covariant=True)
FrameInvT = TypeVar('FrameInvT', bound=AnyFrame, default=AnyFrame)
ContentT = TypeVar('ContentT', bound=object, default=object, covariant=True)
ContentInvT = TypeVar('ContentInvT', bound=object, default=object)
