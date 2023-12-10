from typing import Callable, TypeAlias, TypeVar

GeneralDecorator = Callable[[Callable], Callable]
LocaleType: TypeAlias = str | tuple[str | None, str | None]

DecoratorClassT = TypeVar('DecoratorClassT', covariant=True)
JobConfigT = TypeVar('JobConfigT', covariant=True)
JobT = TypeVar('JobT', covariant=True)
JobTemplateT = TypeVar('JobTemplateT', covariant=True)
TaskTemplateT = TypeVar('TaskTemplateT')
TaskTemplateContraT = TypeVar('TaskTemplateContraT', contravariant=True)
TaskTemplateCovT = TypeVar('TaskTemplateCovT', covariant=True)
