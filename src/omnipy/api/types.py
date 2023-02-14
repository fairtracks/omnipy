from __future__ import annotations

from typing import Callable, Optional, Tuple, TypeAlias, Union

GeneralDecorator = Callable[[Callable], Callable]
LocaleType: TypeAlias = Union[str, Tuple[Optional[str], Optional[str]]]
