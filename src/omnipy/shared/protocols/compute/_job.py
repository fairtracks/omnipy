from datetime import datetime
from inspect import BoundArguments
from types import MappingProxyType
from typing import Any, Callable, Iterable, Mapping, ParamSpec, Protocol, runtime_checkable

from typing_extensions import TypeVar

from omnipy.shared._typedefs import (_JobT,
                                     _JobTemplateT,
                                     _TaskTemplateContraT,
                                     _TaskTemplateCovT,
                                     _TaskTemplateT)
from omnipy.shared.enums import (OutputStorageProtocolOptions,
                                 PersistOutputsOptions,
                                 RestoreOutputsOptions)
from omnipy.shared.protocols.compute.job_creator import IsJobCreator
from omnipy.shared.protocols.compute.mixins import IsUniquelyNamedJob
from omnipy.shared.protocols.config import IsJobConfig
from omnipy.shared.protocols.data import IsDataset
from omnipy.shared.protocols.engine.base import IsEngine
from omnipy.shared.protocols.hub.log import CanLog
from omnipy.shared.typedefs import GeneralDecorator

_CallP = ParamSpec('_CallP')
_RetCovT = TypeVar('_RetCovT', covariant=True)
_RetContraT = TypeVar('_RetContraT', contravariant=True)


class IsJobBase(CanLog, IsUniquelyNamedJob, Protocol[_JobTemplateT, _JobT, _CallP, _RetCovT]):
    """"""
    @property
    def _job_creator(self) -> IsJobCreator:
        ...

    @property
    def config(self) -> IsJobConfig:
        ...

    @property
    def engine(self) -> IsEngine | None:
        ...

    @property
    def in_flow_context(self) -> bool:
        ...

    def __eq__(self, other: object) -> bool:
        ...

    @classmethod
    def _create_job_template(cls, *args: object, **kwargs: object) -> _JobTemplateT:
        ...

    @classmethod
    def _create_job(cls, *args: object, **kwargs: object) -> _JobT:
        ...

    def _apply(self) -> _JobT:
        ...

    def _refine(self, *args: Any, update: bool = True, **kwargs: object) -> _JobTemplateT:
        ...

    def _revise(self) -> _JobTemplateT:
        ...

    def _call_job_template(self, *args: _CallP.args, **kwargs: _CallP.kwargs) -> _RetCovT:
        ...

    def _call_job(self, *args: _CallP.args, **kwargs: _CallP.kwargs) -> _RetCovT:
        ...


class IsJobBaseCallable(IsJobBase[_JobTemplateT, _JobT, _CallP, _RetCovT],
                        Protocol[_JobTemplateT, _JobT, _CallP, _RetCovT]):
    def __call__(self, *args: _CallP.args, **kwargs: _CallP.kwargs) -> _RetCovT:
        ...


@runtime_checkable
class IsJob(IsJobBaseCallable[_JobTemplateT, _JobT, _CallP, _RetCovT],
            Protocol[_JobTemplateT, _JobT, _CallP, _RetCovT]):
    """"""
    @property
    def time_of_cur_toplevel_flow_run(self) -> datetime | None:
        ...

    @classmethod
    def create_job(cls, *args: object, **kwargs: object) -> _JobT:
        ...

    def revise(self) -> _JobTemplateT:
        ...

    def _apply_engine_decorator(self, engine: IsEngine) -> None:
        ...


@runtime_checkable
class IsJobTemplate(IsJobBaseCallable[_JobTemplateT, _JobT, _CallP, _RetCovT],
                    Protocol[_JobTemplateT, _JobT, _CallP, _RetCovT]):
    """"""
    @classmethod
    def create_job_template(cls, *args: object, **kwargs: object) -> _JobTemplateT:
        ...

    def run(self, *args: _CallP.args, **kwargs: _CallP.kwargs) -> _RetCovT:
        ...

    def apply(self) -> _JobT:
        ...


class IsFuncArgJobBase(Protocol):
    """"""
    @property
    def param_signatures(self) -> MappingProxyType:
        ...

    @property
    def return_type(self) -> type:
        ...

    @property
    def iterate_over_data_files(self) -> bool:
        ...

    @property
    def output_dataset_param(self) -> str | None:
        ...

    @property
    def output_dataset_cls(self) -> type[IsDataset] | None:
        ...

    @property
    def auto_async(self) -> bool:
        ...

    @property
    def persist_outputs(self) -> PersistOutputsOptions | None:
        ...

    @property
    def restore_outputs(self) -> RestoreOutputsOptions | None:
        ...

    @property
    def output_storage_protocol(self) -> OutputStorageProtocolOptions | None:
        ...

    @property
    def will_persist_outputs(self) -> PersistOutputsOptions:
        ...

    @property
    def will_restore_outputs(self) -> RestoreOutputsOptions:
        ...

    @property
    def output_storage_protocol_to_use(self) -> OutputStorageProtocolOptions:
        ...

    @property
    def result_key(self) -> str | None:
        ...

    @property
    def fixed_params(self) -> MappingProxyType[str, object]:
        ...

    @property
    def param_key_map(self) -> MappingProxyType[str, str]:
        ...

    def has_coroutine_func(self) -> bool:
        ...

    def get_bound_args(self, *args: object, **kwargs: object) -> BoundArguments:
        ...


# Change?
class IsPlainFuncArgJobBase(Protocol):
    """"""

    _job_func: Callable

    def _accept_call_func_decorator(self, call_func_decorator: GeneralDecorator) -> None:
        ...


_CallableT = TypeVar('_CallableT', bound=Callable)


class HasFuncArgJobTemplateInit(Protocol[_JobTemplateT, _CallP, _RetContraT]):
    """"""
    def __call__(
        self,
        job_func: Callable[_CallP, _RetContraT],
        *,
        name: str | None = None,
        iterate_over_data_files: bool = False,
        output_dataset_param: str | None = None,
        output_dataset_cls: type[IsDataset] | None = None,
        auto_async: bool = True,
        persist_outputs: PersistOutputsOptions | None = None,
        restore_outputs: RestoreOutputsOptions | None = None,
        result_key: str | None = None,
        fixed_params: Mapping[str, object] | Iterable[tuple[str, object]] | None = None,
        param_key_map: Mapping[str, str] | Iterable[tuple[str, str]] | None = None,
        **kwargs: object,
    ) -> _JobTemplateT:
        ...


class IsFuncArgJobTemplate(IsJobTemplate[_JobTemplateT, _JobT, _CallP, _RetCovT],
                           IsFuncArgJobBase,
                           Protocol[_JobTemplateT, _JobT, _CallP, _RetCovT]):
    """"""
    def refine(self,
               *args: Any,
               update: bool = True,
               name: str | None = None,
               iterate_over_data_files: bool = False,
               output_dataset_param: str | None = None,
               output_dataset_cls: type[IsDataset] | None = None,
               auto_async: bool = True,
               persist_outputs: PersistOutputsOptions | None = None,
               restore_outputs: RestoreOutputsOptions | None = None,
               result_key: str | None = None,
               fixed_params: Mapping[str, object] | Iterable[tuple[str, object]] | None = None,
               param_key_map: Mapping[str, str] | Iterable[tuple[str, str]] | None = None,
               **kwargs: object) -> _JobTemplateT:
        ...


class IsFuncArgJob(IsJob[_JobTemplateT, _JobT, _CallP, _RetCovT],
                   IsFuncArgJobBase,
                   Protocol[_JobTemplateT, _JobT, _CallP, _RetCovT]):
    """"""


class IsTaskTemplateArgsJobBase(IsFuncArgJobBase, Protocol[_TaskTemplateCovT]):
    """"""
    @property
    def task_templates(self) -> tuple[_TaskTemplateCovT, ...]:
        ...


class IsTaskTemplateArgsJob(IsTaskTemplateArgsJobBase[_TaskTemplateCovT],
                            IsFuncArgJob[_JobTemplateT, _JobT, _CallP, _RetCovT],
                            Protocol[_TaskTemplateCovT, _JobTemplateT, _JobT, _CallP, _RetCovT]):
    """"""


class HasTaskTemplateArgsJobTemplateInit(Protocol[_JobTemplateT,
                                                  _TaskTemplateContraT,
                                                  _CallP,
                                                  _RetContraT]):
    """"""
    def __call__(
        self,
        job_func: Callable[_CallP, _RetContraT],
        /,
        *task_templates: _TaskTemplateContraT,
        name: str | None = None,
        iterate_over_data_files: bool = False,
        output_dataset_param: str | None = None,
        output_dataset_cls: type[IsDataset] | None = None,
        auto_async: bool = True,
        persist_outputs: PersistOutputsOptions | None = None,
        restore_outputs: RestoreOutputsOptions | None = None,
        result_key: str | None = None,
        fixed_params: Mapping[str, object] | Iterable[tuple[str, object]] | None = None,
        param_key_map: Mapping[str, str] | Iterable[tuple[str, str]] | None = None,
        **kwargs: object,
    ) -> _JobTemplateT:
        ...


class IsTaskTemplateArgsJobTemplate(IsFuncArgJobTemplate[_JobTemplateT, _JobT, _CallP, _RetCovT],
                                    IsTaskTemplateArgsJobBase[_TaskTemplateT],
                                    Protocol[_TaskTemplateT, _JobTemplateT, _JobT, _CallP,
                                             _RetCovT]):
    """"""
    def refine(self,
               *task_templates: _TaskTemplateT,
               update: bool = True,
               name: str | None = None,
               iterate_over_data_files: bool = False,
               output_dataset_param: str | None = None,
               output_dataset_cls: type[IsDataset] | None = None,
               auto_async: bool = True,
               fixed_params: Mapping[str, object] | Iterable[tuple[str, object]] | None = None,
               param_key_map: Mapping[str, str] | Iterable[tuple[str, str]] | None = None,
               result_key: str | None = None,
               persist_outputs: PersistOutputsOptions | None = None,
               restore_outputs: RestoreOutputsOptions | None = None,
               **kwargs: object) -> _JobTemplateT:
        ...
