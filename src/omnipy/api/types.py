from __future__ import annotations

from typing import Callable, Optional, Tuple, TypeAlias, TypeVar, Union

GeneralDecorator = Callable[[Callable], Callable]
LocaleType: TypeAlias = Union[str, Tuple[Optional[str], Optional[str]]]
JobT = TypeVar('JobT', covariant=True)
JobTemplateT = TypeVar('JobTemplateT', covariant=True)
DecoratorClassT = TypeVar('DecoratorClassT', covariant=True)
