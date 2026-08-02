from typing import (Callable,
                    Concatenate,
                    Iterable,
                    Mapping,
                    overload,
                    ParamSpec,
                    Protocol,
                    TypedDict)

from typing_extensions import TypeVar

from omnipy.shared.enums.job import PersistOutputsOptions, RestoreOutputsOptions
from omnipy.shared.protocols.compute.job import (IsDagFlowTemplate,
                                                 IsFuncFlowTemplate,
                                                 IsLinearFlowTemplate,
                                                 IsTaskTemplate)
from omnipy.shared.protocols.data import IsDataset, IsModel

_CallP = ParamSpec('_CallP')
_InT = TypeVar('_InT')
_InModelT = TypeVar('_InModelT', bound=IsModel)
_RetT = TypeVar('_RetT')
_RetModelT = TypeVar('_RetModelT', bound=IsModel)
_RetDatasetClsT = TypeVar('_RetDatasetClsT', bound=IsDataset)
_RetDatasetClsCovT = TypeVar('_RetDatasetClsCovT', bound=IsDataset, covariant=True)


class JobCommonKwargs(TypedDict, total=False):
    name: str | None
    output_dataset_param: str | None
    auto_async: bool
    result_key: str | None
    fixed_params: Mapping[str, object] | Iterable[tuple[str, object]] | None
    param_key_map: Mapping[str, str] | Iterable[tuple[str, str]] | None
    persist_outputs: PersistOutputsOptions.Literals
    restore_outputs: RestoreOutputsOptions.Literals


class TaskTemplateIterDecorator(Protocol[_CallP]):
    @overload
    def __call__(
        self,
        func: Callable[Concatenate[_InModelT, _CallP], _RetModelT],
    ) -> IsTaskTemplate[Concatenate[IsDataset[_InModelT], _CallP], IsDataset[_RetModelT]]:
        ...

    @overload  # pyright: ignore[reportOverlappingOverload]
    def __call__(
        self,
        func: Callable[Concatenate[_InT, _CallP], _RetT],
    ) -> IsTaskTemplate[Concatenate[IsDataset[IsModel[_InT]], _CallP], IsDataset[IsModel[_RetT]]]:
        ...


class TaskTemplateIterWithDatasetClsDecorator(Protocol[_RetDatasetClsT]):
    @overload
    def __call__(
        self,
        func: Callable[Concatenate[_InModelT, _CallP], object],
    ) -> IsTaskTemplate[Concatenate[IsDataset[_InModelT], _CallP], _RetDatasetClsT]:
        ...

    @overload  # pyright: ignore[reportOverlappingOverload]
    def __call__(
        self,
        func: Callable[Concatenate[_InT, _CallP], object],
    ) -> IsTaskTemplate[Concatenate[IsDataset[IsModel[_InT]], _CallP], _RetDatasetClsT]:
        ...


class TaskTemplatePlainDecorator(Protocol):
    def __call__(
        self,
        func: Callable[_CallP, _RetT],
    ) -> IsTaskTemplate[_CallP, _RetT]:
        ...


class LinearFlowTemplateIterDecorator(Protocol[_CallP]):
    @overload
    def __call__(
        self,
        func: Callable[Concatenate[_InModelT, _CallP], _RetModelT],
    ) -> IsLinearFlowTemplate[Concatenate[IsDataset[_InModelT], _CallP], IsDataset[_RetModelT]]:
        ...

    @overload  # pyright: ignore[reportOverlappingOverload]
    def __call__(
        self,
        func: Callable[Concatenate[_InT, _CallP], _RetT],
    ) -> IsLinearFlowTemplate[Concatenate[IsDataset[IsModel[_InT]], _CallP],
                              IsDataset[IsModel[_RetT]]]:
        ...


class LinearFlowTemplateIterWithDatasetClsDecorator(Protocol[_RetDatasetClsCovT]):
    @overload
    def __call__(
        self,
        func: Callable[Concatenate[_InModelT, _CallP], object],
    ) -> IsLinearFlowTemplate[Concatenate[IsDataset[_InModelT], _CallP], _RetDatasetClsCovT]:
        ...

    @overload  # pyright: ignore[reportOverlappingOverload]
    def __call__(
        self,
        func: Callable[Concatenate[_InT, _CallP], object],
    ) -> IsLinearFlowTemplate[Concatenate[IsDataset[IsModel[_InT]], _CallP], _RetDatasetClsCovT]:
        ...


class LinearFlowTemplatePlainDecorator(Protocol):
    def __call__(
        self,
        func: Callable[_CallP, _RetT],
    ) -> IsLinearFlowTemplate[_CallP, _RetT]:
        ...


class DagFlowTemplateIterDecorator(Protocol[_CallP]):
    @overload
    def __call__(
        self,
        func: Callable[Concatenate[_InModelT, _CallP], _RetModelT],
    ) -> IsDagFlowTemplate[Concatenate[IsDataset[_InModelT], _CallP], IsDataset[_RetModelT]]:
        ...

    @overload  # pyright: ignore[reportOverlappingOverload]
    def __call__(
        self,
        func: Callable[Concatenate[_InT, _CallP], _RetT],
    ) -> IsDagFlowTemplate[Concatenate[IsDataset[IsModel[_InT]], _CallP],
                           IsDataset[IsModel[_RetT]]]:
        ...


class DagFlowTemplateIterWithDatasetClsDecorator(Protocol[_RetDatasetClsCovT]):
    @overload
    def __call__(
        self,
        func: Callable[Concatenate[_InModelT, _CallP], object],
    ) -> IsDagFlowTemplate[Concatenate[IsDataset[_InModelT], _CallP], _RetDatasetClsCovT]:
        ...

    @overload  # pyright: ignore[reportOverlappingOverload]
    def __call__(
        self,
        func: Callable[Concatenate[_InT, _CallP], object],
    ) -> IsDagFlowTemplate[Concatenate[IsDataset[IsModel[_InT]], _CallP], _RetDatasetClsCovT]:
        ...


class DagFlowTemplatePlainDecorator(Protocol):
    def __call__(
        self,
        func: Callable[_CallP, _RetT],
    ) -> IsDagFlowTemplate[_CallP, _RetT]:
        ...


class FuncFlowTemplateIterDecorator(Protocol[_CallP]):
    @overload
    def __call__(
        self,
        func: Callable[Concatenate[_InModelT, _CallP], _RetModelT],
    ) -> IsFuncFlowTemplate[Concatenate[IsDataset[_InModelT], _CallP], IsDataset[_RetModelT]]:
        ...

    @overload  # pyright: ignore[reportOverlappingOverload]
    def __call__(
        self,
        func: Callable[Concatenate[_InT, _CallP], _RetT],
    ) -> IsFuncFlowTemplate[Concatenate[IsDataset[IsModel[_InT]], _CallP],
                            IsDataset[IsModel[_RetT]]]:
        ...


class FuncFlowTemplateIterWithDatasetClsDecorator(Protocol[_RetDatasetClsCovT]):
    @overload
    def __call__(
        self,
        func: Callable[Concatenate[_InModelT, _CallP], object],
    ) -> IsFuncFlowTemplate[Concatenate[IsDataset[_InModelT], _CallP], _RetDatasetClsCovT]:
        ...

    @overload  # pyright: ignore[reportOverlappingOverload]
    def __call__(
        self,
        func: Callable[Concatenate[_InT, _CallP], object],
    ) -> IsFuncFlowTemplate[Concatenate[IsDataset[IsModel[_InT]], _CallP], _RetDatasetClsCovT]:
        ...


class FuncFlowTemplatePlainDecorator(Protocol):
    def __call__(
        self,
        func: Callable[_CallP, _RetT],
    ) -> IsFuncFlowTemplate[_CallP, _RetT]:
        ...
