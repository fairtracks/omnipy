from datetime import datetime
from inspect import BoundArguments
from types import MappingProxyType
from typing import Any, Callable, Iterable, Mapping, ParamSpec, Protocol, runtime_checkable

from typing_extensions import TypeVar

from omnipy.api.enums import (OutputStorageProtocolOptions,
                              PersistOutputsOptions,
                              RestoreOutputsOptions)
from omnipy.api.protocols.private.compute.job_creator import IsJobCreator
from omnipy.api.protocols.private.compute.mixins import IsUniquelyNamedJob
from omnipy.api.protocols.private.engine import IsEngine
from omnipy.api.protocols.private.log import CanLog
from omnipy.api.protocols.public.config import IsJobConfig
from omnipy.api.protocols.public.data import IsDataset
from omnipy.api.typedefs import (GeneralDecorator,
                                 JobT,
                                 JobTemplateT,
                                 TaskTemplateContraT,
                                 TaskTemplateCovT,
                                 TaskTemplateT)

CallP = ParamSpec('CallP')
RetCovT = TypeVar('RetCovT', covariant=True)
RetContraT = TypeVar('RetContraT', contravariant=True)


class IsJobBase(CanLog, IsUniquelyNamedJob, Protocol[JobTemplateT, JobT, CallP, RetCovT]):
    """"""
    @property
    def _job_creator(self) -> IsJobCreator:
        ...

    @property
    def config(self) -> IsJobConfig | None:
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
    def _create_job_template(cls, *args: object, **kwargs: object) -> JobTemplateT:
        ...

    @classmethod
    def _create_job(cls, *args: object, **kwargs: object) -> JobT:
        ...

    def _apply(self) -> JobT:
        ...

    def _refine(self, *args: Any, update: bool = True, **kwargs: object) -> JobTemplateT:
        ...

    def _revise(self) -> JobTemplateT:
        ...

    def _call_job_template(self, *args: CallP.args, **kwargs: CallP.kwargs) -> RetCovT:
        ...

    def _call_job(self, *args: CallP.args, **kwargs: CallP.kwargs) -> RetCovT:
        ...


class IsJobBaseCallable(IsJobBase[JobTemplateT, JobT, CallP, RetCovT],
                        Protocol[JobTemplateT, JobT, CallP, RetCovT]):
    def __call__(self, *args: CallP.args, **kwargs: CallP.kwargs) -> RetCovT:
        ...


@runtime_checkable
class IsJob(IsJobBaseCallable[JobTemplateT, JobT, CallP, RetCovT],
            Protocol[JobTemplateT, JobT, CallP, RetCovT]):
    """"""
    @property
    def time_of_cur_toplevel_flow_run(self) -> datetime | None:
        ...

    @classmethod
    def create_job(cls, *args: object, **kwargs: object) -> JobT:
        ...

    def revise(self) -> JobTemplateT:
        ...

    def _apply_engine_decorator(self, engine: IsEngine) -> None:
        ...


@runtime_checkable
class IsJobTemplate(IsJobBaseCallable[JobTemplateT, JobT, CallP, RetCovT],
                    Protocol[JobTemplateT, JobT, CallP, RetCovT]):
    """"""
    @classmethod
    def create_job_template(cls, *args: object, **kwargs: object) -> JobTemplateT:
        ...

    def run(self, *args: CallP.args, **kwargs: CallP.kwargs) -> RetCovT:
        ...

    def apply(self) -> JobT:
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


CallableT = TypeVar('CallableT', bound=Callable)


class HasFuncArgJobTemplateInit(Protocol[JobTemplateT, CallP, RetContraT]):
    """"""
    def __call__(
        self,
        job_func: Callable[CallP, RetContraT],
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
    ) -> JobTemplateT:
        ...


class IsFuncArgJobTemplate(IsJobTemplate[JobTemplateT, JobT, CallP, RetCovT],
                           IsFuncArgJobBase,
                           Protocol[JobTemplateT, JobT, CallP, RetCovT]):
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
               **kwargs: object) -> JobTemplateT:
        ...


class IsFuncArgJob(IsJob[JobTemplateT, JobT, CallP, RetCovT],
                   IsFuncArgJobBase,
                   Protocol[JobTemplateT, JobT, CallP, RetCovT]):
    """"""


class IsTaskTemplateArgsJobBase(IsFuncArgJobBase, Protocol[TaskTemplateCovT]):
    """"""
    @property
    def task_templates(self) -> tuple[TaskTemplateCovT, ...]:
        ...


class IsTaskTemplateArgsJob(IsTaskTemplateArgsJobBase[TaskTemplateCovT],
                            IsFuncArgJob[JobTemplateT, JobT, CallP, RetCovT],
                            Protocol[TaskTemplateCovT, JobTemplateT, JobT, CallP, RetCovT]):
    """"""


class HasTaskTemplateArgsJobTemplateInit(Protocol[JobTemplateT,
                                                  TaskTemplateContraT,
                                                  CallP,
                                                  RetContraT]):
    """"""
    def __call__(
        self,
        job_func: Callable[CallP, RetContraT],
        /,
        *task_templates: TaskTemplateContraT,
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
    ) -> JobTemplateT:
        ...


class IsTaskTemplateArgsJobTemplate(IsFuncArgJobTemplate[JobTemplateT, JobT, CallP, RetCovT],
                                    IsTaskTemplateArgsJobBase[TaskTemplateT],
                                    Protocol[TaskTemplateT, JobTemplateT, JobT, CallP, RetCovT]):
    """"""
    def refine(self,
               *task_templates: TaskTemplateT,
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
               **kwargs: object) -> JobTemplateT:
        ...
