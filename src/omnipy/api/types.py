from __future__ import annotations

from typing import Callable, Optional, Tuple, TypeAlias, TypeVar, Union

GeneralDecorator = Callable[[Callable], Callable]
LocaleType: TypeAlias = Union[str, Tuple[Optional[str], Optional[str]]]
JobConfigT = TypeVar('JobConfigT', covariant=True)
JobT = TypeVar('JobT', covariant=True)
JobTemplateT = TypeVar('JobTemplateT', covariant=True)
TaskTemplateT = TypeVar('TaskTemplateT')
TaskTemplateContraT = TypeVar('TaskTemplateContraT', contravariant=True)
TaskTemplateCovT = TypeVar('TaskTemplateCovT', covariant=True)
DecoratorClassT = TypeVar('DecoratorClassT', covariant=True)
