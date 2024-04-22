from types import UnionType
from typing import (_AnnotatedAlias,
                    _GenericAlias,
                    _LiteralGenericAlias,
                    _SpecialForm,
                    _UnionGenericAlias,
                    Callable,
                    TypeAlias,
                    TypeVar)

GeneralDecorator = Callable[[Callable], Callable]
LocaleType: TypeAlias = str | tuple[str | None, str | None]

DecoratorClassT = TypeVar('DecoratorClassT', covariant=True)
JobConfigT = TypeVar('JobConfigT', covariant=True)
JobT = TypeVar('JobT', covariant=True)
JobTemplateT = TypeVar('JobTemplateT', covariant=True)
TaskTemplateT = TypeVar('TaskTemplateT')
TaskTemplateContraT = TypeVar('TaskTemplateContraT', contravariant=True)
TaskTemplateCovT = TypeVar('TaskTemplateCovT', covariant=True)

# TODO: While waiting for https://github.com/python/mypy/issues/9773
TypeForm: TypeAlias = (
    type | UnionType | _UnionGenericAlias | _AnnotatedAlias | _GenericAlias | _LiteralGenericAlias
    | _SpecialForm)
