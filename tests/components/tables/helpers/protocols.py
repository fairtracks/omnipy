from collections.abc import Iterable
from typing import Mapping, Protocol

from omnipy.shared.protocols.typing import IsMapping


class AssertRowIter(Protocol):
    def __call__(
        self,
        row_idx: int,
        row: Mapping[str, object],
    ) -> None:
        ...


class AssertColumnWiseMappings(Protocol):
    def __call__(
        self,
        a: IsMapping[str, Iterable[object]],
        b: IsMapping[str, Iterable[object]],
    ) -> None:
        ...
