from __future__ import annotations

from datetime import datetime
from logging import INFO, Logger
from types import MappingProxyType
from typing import Any, Callable, Dict, Mapping, Optional, Protocol, Tuple, Type

from omnipy.api.enums import PersistOutputsOptions, RestoreOutputsOptions
from omnipy.api.protocols.private import IsEngine, IsUniquelyNamedJob
from omnipy.api.protocols.public.runtime import IsJobConfig, IsJobConfigHolder
from omnipy.api.types import JobT, JobTemplateT


class CanLog(Protocol):
    @property
    def logger(self) -> Logger:
        ...

    def log(self, log_msg: str, level: int = INFO, datetime_obj: Optional[datetime] = None):
        ...


class IsJobBase(CanLog, IsUniquelyNamedJob, Protocol):
    @property
    def _job_creator(self) -> IsJobCreator:
        ...

    @property
    def config(self) -> Optional[IsJobConfig]:
        ...

    @property
    def engine(self) -> Optional[IsEngine]:
        ...

    @property
    def in_flow_context(self) -> bool:
        ...

    def __eq__(self, other: object):
        ...

    @classmethod
    def _create_job_template(cls, *args: object, **kwargs: object) -> IsJobTemplate:
        ...

    @classmethod
    def _create_job(cls, *args: object, **kwargs: object) -> IsJob:
        ...

    def _apply(self) -> IsJob:
        ...

    def _refine(self, *args: Any, update: bool = True, **kwargs: object) -> IsJobTemplate:
        ...

    def _revise(self) -> IsJobTemplate:
        ...

    def _call_job_template(self, *args: object, **kwargs: object) -> object:
        ...

    def _call_job(self, *args: object, **kwargs: object) -> object:
        ...


class IsJob(IsJobBase, Protocol):
    """"""
    @property
    def time_of_cur_toplevel_flow_run(self) -> Optional[datetime]:
        ...

    @classmethod
    def create_job(cls, *args: object, **kwargs: object) -> IsJob:
        ...

    def __call__(self, *args: object, **kwargs: object) -> object:
        ...

    def _apply_engine_decorator(self, engine: IsEngine) -> None:
        ...


class IsJobTemplate(IsJobBase, Protocol):
    """"""
    @classmethod
    def create_job_template(cls, *args: object, **kwargs: object) -> IsJobTemplate:
        ...

    def run(self, *args: object, **kwargs: object) -> object:
        ...


class IsFuncJobBase(IsJob, Protocol):
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
    def persist_outputs(self) -> Optional[PersistOutputsOptions]:
        ...

    @property
    def restore_outputs(self) -> Optional[RestoreOutputsOptions]:
        ...

    @property
    def will_persist_outputs(self) -> PersistOutputsOptions:
        ...

    @property
    def will_restore_outputs(self) -> RestoreOutputsOptions:
        ...

    @property
    def result_key(self) -> Optional[str]:
        ...

    @property
    def fixed_params(self) -> MappingProxyType[str, object]:
        ...

    @property
    def param_key_map(self) -> MappingProxyType[str, str]:
        ...

    def has_coroutine_func(self) -> bool:
        ...

    def get_call_args(self, *args: object, **kwargs: object) -> Dict[str, object]:
        ...


class IsFuncJob(IsFuncJobBase, Protocol[JobT]):
    """"""
    def revise(self) -> JobT:
        ...


class IsFuncJobTemplateCallable(Protocol[JobTemplateT]):
    """"""
    def __call__(
        self,
        name: Optional[str] = None,
        iterate_over_data_files: bool = False,
        persist_outputs: Optional[PersistOutputsOptions] = None,
        restore_outputs: Optional[RestoreOutputsOptions] = None,
        result_key: Optional[str] = None,
        fixed_params: Optional[Mapping[str, object]] = None,
        param_key_map: Optional[Mapping[str, str]] = None,
        **kwargs: object,
    ) -> Callable[[Callable], JobTemplateT]:
        ...


class IsFuncJobTemplate(IsJobTemplate, IsFuncJobBase, Protocol[JobTemplateT, JobT]):
    """"""
    def refine(self,
               *args: Any,
               update: bool = True,
               name: Optional[str] = None,
               iterate_over_data_files: bool = False,
               persist_outputs: Optional[PersistOutputsOptions] = None,
               restore_outputs: Optional[RestoreOutputsOptions] = None,
               result_key: Optional[str] = None,
               fixed_params: Optional[Mapping[str, object]] = None,
               param_key_map: Optional[Mapping[str, str]] = None,
               **kwargs: object) -> JobTemplateT:
        ...

    def apply(self) -> JobT:
        ...


class IsTaskTemplateArgsJobBase(IsFuncJobBase, Protocol):
    """"""
    @property
    def task_templates(self) -> Tuple[IsTaskTemplate, ...]:
        ...


class IsTaskTemplateArgsJob(IsFuncJob[JobT], Protocol[JobT]):
    """"""


class IsTaskTemplatesFlowTemplateCallable(Protocol[JobTemplateT]):
    """"""
    def __call__(
        self,
        *task_templates: IsTaskTemplate,
        name: Optional[str] = None,
        iterate_over_data_files: bool = False,
        persist_outputs: Optional[PersistOutputsOptions] = None,
        restore_outputs: Optional[RestoreOutputsOptions] = None,
        result_key: Optional[str] = None,
        fixed_params: Optional[Mapping[str, object]] = None,
        param_key_map: Optional[Mapping[str, str]] = None,
        **kwargs: object,
    ) -> Callable[[Callable], JobTemplateT]:
        ...


class IsTaskTemplateArgsJobTemplate(IsFuncJobTemplate[JobTemplateT, JobT],
                                    IsTaskTemplateArgsJobBase,
                                    Protocol[JobTemplateT, JobT]):
    """"""
    def refine(self,
               *task_templates: IsTaskTemplate,
               update: bool = True,
               name: Optional[str] = None,
               iterate_over_data_files: bool = False,
               fixed_params: Optional[Mapping[str, object]] = None,
               param_key_map: Optional[Mapping[str, str]] = None,
               result_key: Optional[str] = None,
               persist_outputs: Optional[PersistOutputsOptions] = None,
               restore_outputs: Optional[RestoreOutputsOptions] = None,
               **kwargs: object) -> JobTemplateT:
        ...


class IsTaskTemplate(IsFuncJobTemplate['IsTaskTemplate', 'IsTask'], Protocol):
    """"""
    ...


class IsTask(IsFuncJob[IsTaskTemplate], Protocol):
    """"""
    ...


class IsFlow(Protocol):
    """"""
    @property
    def flow_context(self) -> IsNestedContext:
        ...

    @property
    def time_of_last_run(self) -> Optional[datetime]:
        ...


class IsFlowTemplate(Protocol):
    """"""
    ...


class IsLinearFlowTemplate(IsTaskTemplateArgsJobTemplate['IsLinearFlowTemplate', 'IsLinearFlow'],
                           IsFlowTemplate,
                           Protocol):
    """"""
    ...


class IsLinearFlow(IsTaskTemplateArgsJob[IsLinearFlowTemplate], IsFlow, Protocol):
    """"""
    ...


class IsDagFlowTemplate(IsTaskTemplateArgsJobTemplate['IsDagFlowTemplate', 'IsDagFlow'],
                        IsFlowTemplate,
                        Protocol):
    """"""
    ...


class IsDagFlow(IsTaskTemplateArgsJob[IsDagFlowTemplate], IsFlow, Protocol):
    """"""
    ...


class IsFuncFlowTemplate(IsFuncJobTemplate['IsFuncFlowTemplate', 'IsFuncFlow'],
                         IsFlowTemplate,
                         Protocol):
    """"""
    ...


class IsFuncFlow(IsFuncJob[IsFuncFlowTemplate], Protocol):
    """"""
    ...


class IsNestedContext(Protocol):
    """"""
    def __enter__(self):
        ...

    def __exit__(self, exc_type, exc_value, traceback):
        ...


class IsJobCreator(IsNestedContext, IsJobConfigHolder, Protocol):
    """"""
    @property
    def nested_context_level(self) -> int:
        ...

    @property
    def time_of_cur_toplevel_nested_context_run(self) -> Optional[datetime]:
        ...
