from datetime import datetime
import inspect
from types import MappingProxyType
from typing import Any, Callable, Iterable, Mapping, ParamSpec, Protocol, runtime_checkable, TypeVar

from omnipy.shared._typedefs import _JobT, _JobTemplateT
from omnipy.shared.enums.job import (OutputStorageProtocolOptions,
                                     PersistOutputsOptions,
                                     RestoreOutputsOptions)
from omnipy.shared.protocols.compute.job_creator import IsJobCreator
from omnipy.shared.protocols.compute.mixins import IsNestedContext, IsUniquelyNamedJob
from omnipy.shared.protocols.config import IsJobConfig
from omnipy.shared.protocols.data import IsDataset
from omnipy.shared.protocols.engine.base import IsEngine
from omnipy.shared.protocols.hub.log import CanLog
from omnipy.shared.typedefs import GeneralDecorator
from omnipy.util.callable_types import CallableType

_CallP = ParamSpec('_CallP')
_RetT = TypeVar('_RetT')
_RetCovT = TypeVar('_RetCovT', covariant=True)
_RetContraT = TypeVar('_RetContraT', contravariant=True)


class HasJobCreator(Protocol):
    @property
    def job_creator(self) -> IsJobCreator:
        ...


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


class IsFuncArgJobBase(Protocol):
    """"""
    @property
    def param_signatures(self) -> MappingProxyType[str, inspect.Parameter]:
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
    def persist_outputs(self) -> PersistOutputsOptions.Literals:
        ...

    @property
    def restore_outputs(self) -> RestoreOutputsOptions.Literals:
        ...

    @property
    def output_storage_protocol(self) -> OutputStorageProtocolOptions.Literals:
        ...

    @property
    def will_persist_outputs(self) -> PersistOutputsOptions.Literals:
        ...

    @property
    def will_restore_outputs(self) -> RestoreOutputsOptions.Literals:
        ...

    @property
    def output_storage_protocol_to_use(self) -> OutputStorageProtocolOptions.Literals:
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

    @property
    def callable_type(self) -> CallableType.Literals:
        """
        The effective callable type of the job function.

        The callable type captures both the synchronous/asynchronous and
        plain/generator dimensions of the wrapped callable.

        Returns:
            CallableType.Literals: The effective callable type of the job
                function.
        """
        ...

    def get_bound_args(self, *args: object, **kwargs: object) -> inspect.BoundArguments:
        ...


class IsPlainFuncArgJobBase(Protocol):
    """"""

    _job_func: Callable

    def _accept_call_func_decorator(self, call_func_decorator: GeneralDecorator) -> None:
        ...


_CallableT = TypeVar('_CallableT', bound=Callable)


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


class IsFuncArgJobTemplate(IsJobTemplate[_JobTemplateT, _JobT, _CallP, _RetCovT],
                           IsFuncArgJobBase,
                           Protocol[_JobTemplateT, _JobT, _CallP, _RetCovT]):
    """"""
    def refine(
            self,
            *args: Any,
            update: bool = True,
            name: str | None = None,
            iterate_over_data_files: bool = False,
            output_dataset_param: str | None = None,
            output_dataset_cls: type[IsDataset] | None = None,
            auto_async: bool = True,
            result_key: str | None = None,
            fixed_params: Mapping[str, object] | Iterable[tuple[str, object]] | None = None,
            param_key_map: Mapping[str, str] | Iterable[tuple[str, str]] | None = None,
            persist_outputs: PersistOutputsOptions.Literals = PersistOutputsOptions.FOLLOW_CONFIG,
            restore_outputs: RestoreOutputsOptions.Literals = RestoreOutputsOptions.FOLLOW_CONFIG,
            **kwargs: object) -> _JobTemplateT:
        ...


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
        result_key: str | None = None,
        fixed_params: Mapping[str, object] | Iterable[tuple[str, object]] | None = None,
        param_key_map: Mapping[str, str] | Iterable[tuple[str, str]] | None = None,
        persist_outputs: PersistOutputsOptions.Literals = PersistOutputsOptions.FOLLOW_CONFIG,
        restore_outputs: RestoreOutputsOptions.Literals = RestoreOutputsOptions.FOLLOW_CONFIG,
        **kwargs: object,
    ) -> _JobTemplateT:
        ...


class IsChildJobListArgJobBase(IsFuncArgJobBase, Protocol):
    """"""
    @property
    def child_job_templates(self) -> tuple[IsFuncArgJobTemplate, ...]:
        ...


class HasChildJobListArgJobTemplateInit(Protocol[_JobTemplateT, _CallP, _RetContraT]):
    """"""
    def __call__(
        self,
        job_func: Callable[_CallP, _RetContraT],
        /,
        *child_job_templates: IsFuncArgJobTemplate,
        name: str | None = None,
        iterate_over_data_files: bool = False,
        output_dataset_param: str | None = None,
        output_dataset_cls: type[IsDataset] | None = None,
        auto_async: bool = True,
        result_key: str | None = None,
        fixed_params: Mapping[str, object] | Iterable[tuple[str, object]] | None = None,
        param_key_map: Mapping[str, str] | Iterable[tuple[str, str]] | None = None,
        persist_outputs: PersistOutputsOptions.Literals = PersistOutputsOptions.FOLLOW_CONFIG,
        restore_outputs: RestoreOutputsOptions.Literals = RestoreOutputsOptions.FOLLOW_CONFIG,
        **kwargs: object,
    ) -> _JobTemplateT:
        ...


class IsTaskTemplate(IsFuncArgJobTemplate['IsTaskTemplate[_CallP, _RetT]',
                                          'IsTask[_CallP, _RetT]',
                                          _CallP,
                                          _RetT],
                     Protocol[_CallP, _RetT]):
    """
    Loosely coupled type replacement for the :py:class:`~omnipy.compute.task.TaskTemplate` class
    """
    ...


class IsFuncArgJob(IsJob[_JobTemplateT, _JobT, _CallP, _RetCovT],
                   IsFuncArgJobBase,
                   Protocol[_JobTemplateT, _JobT, _CallP, _RetCovT]):
    """"""


class IsTask(IsFuncArgJob['IsTaskTemplate[_CallP, _RetT]', 'IsTask[_CallP, _RetT]', _CallP, _RetT],
             Protocol[_CallP, _RetT]):
    """"""
    ...


class IsFlowTemplate(Protocol):
    """"""
    ...


class IsFlow(Protocol):
    """"""
    @property
    def flow_context(self) -> IsNestedContext:
        ...

    @property
    def time_of_last_run(self) -> datetime | None:
        ...


class IsChildJobListArgJobTemplate(IsFuncArgJobTemplate[_JobTemplateT, _JobT, _CallP, _RetCovT],
                                   IsChildJobListArgJobBase,
                                   Protocol[_JobTemplateT, _JobT, _CallP, _RetCovT]):
    """"""
    def refine(
            self,
            *child_job_templates: IsFuncArgJobTemplate,
            update: bool = True,
            name: str | None = None,
            iterate_over_data_files: bool = False,
            output_dataset_param: str | None = None,
            output_dataset_cls: type[IsDataset] | None = None,
            auto_async: bool = True,
            result_key: str | None = None,
            fixed_params: Mapping[str, object] | Iterable[tuple[str, object]] | None = None,
            param_key_map: Mapping[str, str] | Iterable[tuple[str, str]] | None = None,
            persist_outputs: PersistOutputsOptions.Literals = PersistOutputsOptions.FOLLOW_CONFIG,
            restore_outputs: RestoreOutputsOptions.Literals = RestoreOutputsOptions.FOLLOW_CONFIG,
            **kwargs: object) -> _JobTemplateT:
        ...


class IsLinearFlowTemplate(IsChildJobListArgJobTemplate['IsLinearFlowTemplate[_CallP, _RetCovT]',
                                                        'IsLinearFlow[_CallP, _RetCovT]',
                                                        _CallP,
                                                        _RetCovT],
                           IsFlowTemplate,
                           Protocol[_CallP, _RetCovT]):
    """"""
    ...


class IsChildJobListArgJob(IsChildJobListArgJobBase,
                           IsFuncArgJob[_JobTemplateT, _JobT, _CallP, _RetCovT],
                           Protocol[_JobTemplateT, _JobT, _CallP, _RetCovT]):
    """"""


class IsLinearFlow(IsChildJobListArgJob['IsLinearFlowTemplate[_CallP, _RetCovT]',
                                        'IsLinearFlow[_CallP, _RetCovT]',
                                        _CallP,
                                        _RetCovT],
                   IsFlow,
                   Protocol[_CallP, _RetCovT]):
    """"""
    ...


class IsDagFlowTemplate(IsChildJobListArgJobTemplate['IsDagFlowTemplate[_CallP, _RetCovT]',
                                                     'IsDagFlow[_CallP, _RetCovT]',
                                                     _CallP,
                                                     _RetCovT],
                        IsFlowTemplate,
                        Protocol[_CallP, _RetCovT]):
    """"""
    ...


class IsDagFlow(IsChildJobListArgJob['IsDagFlowTemplate[_CallP, _RetCovT]',
                                     'IsDagFlow[_CallP, _RetCovT]',
                                     _CallP,
                                     _RetCovT],
                IsFlow,
                Protocol[_CallP, _RetCovT]):
    """"""
    ...


class IsFuncFlowTemplate(IsFuncArgJobTemplate['IsFuncFlowTemplate[_CallP, _RetCovT]',
                                              'IsFuncFlow[_CallP, _RetCovT]',
                                              _CallP,
                                              _RetCovT],
                         IsFlowTemplate,
                         Protocol[_CallP, _RetCovT]):
    """"""
    ...


class IsFuncFlow(IsFuncArgJob['IsFuncFlowTemplate[_CallP, _RetCovT]',
                              'IsFuncFlow[_CallP, _RetCovT]',
                              _CallP,
                              _RetCovT],
                 IsFlow,
                 Protocol[_CallP, _RetCovT]):
    """"""
    ...


class IsAnyFlowTemplate(IsFuncArgJobTemplate['IsAnyFlowTemplate[_CallP, _RetCovT]',
                                             'IsAnyFlow[_CallP, _RetCovT]',
                                             _CallP,
                                             _RetCovT],
                        IsFlowTemplate,
                        Protocol[_CallP, _RetCovT]):
    """"""
    ...


class IsAnyFlow(IsFuncArgJob['IsAnyFlowTemplate[_CallP, _RetCovT]',
                             'IsAnyFlow[_CallP, _RetCovT]',
                             _CallP,
                             _RetCovT],
                IsFlow,
                Protocol[_CallP, _RetCovT]):
    """"""
    ...
