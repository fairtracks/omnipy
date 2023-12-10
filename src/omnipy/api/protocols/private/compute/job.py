from datetime import datetime
from types import MappingProxyType
from typing import Any, Callable, Mapping, Protocol, Type

from omnipy.api.enums import (OutputStorageProtocolOptions,
                              PersistOutputsOptions,
                              RestoreOutputsOptions)
from omnipy.api.protocols.private.compute.job_creator import IsJobCreator
from omnipy.api.protocols.private.compute.mixins import IsUniquelyNamedJob
from omnipy.api.protocols.private.engine import IsEngine
from omnipy.api.protocols.private.log import CanLog
from omnipy.api.protocols.public.config import IsJobConfig
from omnipy.api.typedefs import (GeneralDecorator,
                                 JobT,
                                 JobTemplateT,
                                 TaskTemplateContraT,
                                 TaskTemplateCovT,
                                 TaskTemplateT)


class IsJobBase(CanLog, IsUniquelyNamedJob, Protocol):
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

    def __eq__(self, other: object):
        ...

    @classmethod
    def _create_job_template(cls, *args: object, **kwargs: object) -> 'IsJobTemplate':
        ...

    @classmethod
    def _create_job(cls, *args: object, **kwargs: object) -> 'IsJob':
        ...

    def _apply(self) -> 'IsJob':
        ...

    def _refine(self, *args: Any, update: bool = True, **kwargs: object) -> 'IsJobTemplate':
        ...

    def _revise(self) -> 'IsJobTemplate':
        ...

    def _call_job_template(self, *args: object, **kwargs: object) -> object:
        ...

    def _call_job(self, *args: object, **kwargs: object) -> object:
        ...


class IsJob(IsJobBase, Protocol):
    """"""
    @property
    def time_of_cur_toplevel_flow_run(self) -> datetime | None:
        ...

    @classmethod
    def create_job(cls, *args: object, **kwargs: object) -> 'IsJob':
        ...

    def __call__(self, *args: object, **kwargs: object) -> object:
        ...

    def _apply_engine_decorator(self, engine: IsEngine) -> None:
        ...


class IsJobTemplate(IsJobBase, Protocol):
    """"""
    @classmethod
    def create_job_template(cls, *args: object, **kwargs: object) -> 'IsJobTemplate':
        ...

    def run(self, *args: object, **kwargs: object) -> object:
        ...


class IsFuncArgJobBase(IsJob, Protocol):
    """"""
    @property
    def param_signatures(self) -> MappingProxyType:
        ...

    @property
    def return_type(self) -> Type[object]:
        ...

    @property
    def iterate_over_data_files(self) -> bool:
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

    def get_call_args(self, *args: object, **kwargs: object) -> dict[str, object]:
        ...


class IsPlainFuncArgJobBase(Protocol):
    """"""
    _job_func: Callable

    def _accept_call_func_decorator(self, call_func_decorator: GeneralDecorator) -> None:
        ...


class IsFuncArgJob(IsFuncArgJobBase, Protocol[JobT]):
    """"""
    def revise(self) -> JobT:
        ...


class IsFuncArgJobTemplateCallable(Protocol[JobTemplateT]):
    """"""
    def __call__(
        self,
        name: str | None = None,
        iterate_over_data_files: bool = False,
        persist_outputs: PersistOutputsOptions | None = None,
        restore_outputs: RestoreOutputsOptions | None = None,
        result_key: str | None = None,
        fixed_params: Mapping[str, object] | None = None,
        param_key_map: Mapping[str, str] | None = None,
        **kwargs: object,
    ) -> Callable[[Callable], JobTemplateT]:
        ...


class IsFuncArgJobTemplate(IsJobTemplate, IsFuncArgJobBase, Protocol[JobTemplateT, JobT]):
    """"""
    def refine(self,
               *args: Any,
               update: bool = True,
               name: str | None = None,
               iterate_over_data_files: bool = False,
               persist_outputs: PersistOutputsOptions | None = None,
               restore_outputs: RestoreOutputsOptions | None = None,
               result_key: str | None = None,
               fixed_params: Mapping[str, object] | None = None,
               param_key_map: Mapping[str, str] | None = None,
               **kwargs: object) -> JobTemplateT:
        ...

    def apply(self) -> JobT:
        ...


class IsTaskTemplateArgsJobBase(IsFuncArgJobBase, Protocol[TaskTemplateCovT]):
    """"""
    @property
    def task_templates(self) -> tuple[TaskTemplateCovT, ...]:
        ...


class IsTaskTemplateArgsJob(IsTaskTemplateArgsJobBase[TaskTemplateCovT],
                            IsFuncArgJob[JobT],
                            Protocol[TaskTemplateCovT, JobT]):
    """"""


class IsTaskTemplateArgsJobTemplateCallable(Protocol[TaskTemplateContraT, JobTemplateT]):
    """"""
    def __call__(
        self,
        *task_templates: TaskTemplateContraT,
        name: str | None = None,
        iterate_over_data_files: bool = False,
        persist_outputs: PersistOutputsOptions | None = None,
        restore_outputs: RestoreOutputsOptions | None = None,
        result_key: str | None = None,
        fixed_params: Mapping[str, object] | None = None,
        param_key_map: Mapping[str, str] | None = None,
        **kwargs: object,
    ) -> Callable[[Callable], JobTemplateT]:
        ...


class IsTaskTemplateArgsJobTemplate(IsFuncArgJobTemplate[JobTemplateT, JobT],
                                    IsTaskTemplateArgsJobBase[TaskTemplateT],
                                    Protocol[TaskTemplateT, JobTemplateT, JobT]):
    """"""
    def refine(self,
               *task_templates: TaskTemplateT,
               update: bool = True,
               name: str | None = None,
               iterate_over_data_files: bool = False,
               fixed_params: Mapping[str, object] | None = None,
               param_key_map: Mapping[str, str] | None = None,
               result_key: str | None = None,
               persist_outputs: PersistOutputsOptions | None = None,
               restore_outputs: RestoreOutputsOptions | None = None,
               **kwargs: object) -> JobTemplateT:
        ...
