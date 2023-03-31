from __future__ import annotations

from datetime import datetime
from types import MappingProxyType
from typing import Any, Callable, Dict, Mapping, Optional, Protocol, Tuple, Type, TypeVar

from omnipy.api.enums import PersistOutputsOptions, RestoreOutputsOptions
from omnipy.api.protocols.private.compute.job_creator import IsJobCreator
from omnipy.api.protocols.private.compute.mixins import IsUniquelyNamedJob
from omnipy.api.protocols.private.config import IsJobConfigBase
from omnipy.api.protocols.private.engine import IsEngine
from omnipy.api.protocols.private.log import CanLog
from omnipy.api.types import (GeneralDecorator,
                              JobT,
                              JobTemplateT,
                              TaskTemplateContraT,
                              TaskTemplateCovT,
                              TaskTemplateT)

C = TypeVar('C', bound=Callable)


class IsJobBase(CanLog, IsUniquelyNamedJob, Protocol[C]):
    """"""
    @property
    def _job_creator(self) -> IsJobCreator:
        ...

    @property
    def config(self) -> Optional[IsJobConfigBase]:
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
    def _create_job_template(cls, *args: object, **kwargs: object) -> IsJobTemplate[C]:
        ...

    @classmethod
    def _create_job(cls, *args: object, **kwargs: object) -> IsJob[C]:
        ...

    def _apply(self) -> IsJob[C]:
        ...

    def _refine(self, *args: Any, update: bool = True, **kwargs: object) -> IsJobTemplate[C]:
        ...

    def _revise(self) -> IsJobTemplate[C]:
        ...

    _call_job_template: C
    _call_job: C


class IsJobBaseCallable(IsJobBase[C], Protocol[C]):
    __call__: C


class IsJob(IsJobBaseCallable[C], Protocol[C]):
    """"""
    @property
    def time_of_cur_toplevel_flow_run(self) -> Optional[datetime]:
        ...

    @classmethod
    def create_job(cls, *args: object, **kwargs: object) -> IsJob[C]:
        ...

    def _apply_engine_decorator(self, engine: IsEngine) -> None:
        ...


class IsJobTemplate(IsJobBaseCallable[C], Protocol[C]):
    """"""
    @classmethod
    def create_job_template(cls, *args: object, **kwargs: object) -> IsJobTemplate[C]:
        ...

    run: C


class IsFuncArgJobBase(IsJob[C], Protocol[C]):
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


## Change?
class IsPlainFuncArgJobBase(Protocol):
    """"""
    _job_func: Callable

    def _accept_call_func_decorator(self, call_func_decorator: GeneralDecorator) -> None:
        ...


class IsFuncArgJob(IsFuncArgJobBase[C], Protocol[JobT, C]):
    """"""
    def revise(self) -> JobT:
        ...


CC = TypeVar('CC', bound=Callable, contravariant=True)


class IsFuncArgJobTemplateCallable(Protocol[JobTemplateT, CC]):
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
    ) -> Callable[[CC], JobTemplateT]:
        ...


class IsFuncArgJobTemplate(IsJobTemplate[C], IsFuncArgJobBase[C], Protocol[JobTemplateT, JobT, C]):
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


class IsTaskTemplateArgsJobBase(IsFuncArgJobBase[C], Protocol[TaskTemplateCovT, C]):
    """"""
    @property
    def task_templates(self) -> Tuple[TaskTemplateCovT, ...]:
        ...


class IsTaskTemplateArgsJob(IsTaskTemplateArgsJobBase[TaskTemplateCovT, C],
                            IsFuncArgJob[JobT, C],
                            Protocol[TaskTemplateCovT, JobT, C]):
    """"""


class IsTaskTemplateArgsJobTemplateCallable(Protocol[TaskTemplateContraT, JobTemplateT]):
    """"""
    def __call__(
        self,
        *task_templates: TaskTemplateContraT,
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


class IsTaskTemplateArgsJobTemplate(IsFuncArgJobTemplate[JobTemplateT, JobT, C],
                                    IsTaskTemplateArgsJobBase[TaskTemplateT, C],
                                    Protocol[TaskTemplateT, JobTemplateT, JobT, C]):
    """"""
    def refine(self,
               *task_templates: TaskTemplateT,
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
