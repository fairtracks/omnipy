from __future__ import annotations

from datetime import datetime
from types import MappingProxyType
from typing import Any, Callable, Dict, Mapping, Optional, Protocol, Tuple, Type

from omnipy.api.enums import PersistOutputsOptions, RestoreOutputsOptions
from omnipy.api.protocols.private import IsEngine, IsUniquelyNamedJob
from omnipy.api.protocols.public.runtime import IsJobConfig, IsJobConfigHolder
from omnipy.api.types import FuncJobTemplateT, GeneralDecorator, TaskTemplatesFlowTemplateT


class IsJob(IsUniquelyNamedJob, Protocol):
    """"""
    name: str
    config: Optional[IsJobConfig]
    in_flow_context: bool
    time_of_cur_toplevel_flow_run: datetime

    @classmethod
    def create(cls, *init_args: object, **init_kwargs: object) -> 'IsJob':
        ...

    def revise(self) -> 'IsJobTemplate':
        ...

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        ...

    def __eq__(self, other: object):
        ...


class IsJobTemplate(Protocol):
    """"""
    config: Optional[IsJobConfig]
    engine: Optional[IsEngine]
    in_flow_context: bool

    @classmethod
    def create(cls, *init_args: object, **init_kwargs: object) -> 'IsJobTemplate':
        ...

    def run(self, *args: object, **kwargs: object) -> object:
        ...

    def apply(self) -> IsJob:
        ...

    def refine(self, *args: object, update: bool = True, **kwargs: object) -> 'IsJobTemplate':
        ...

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        ...


class IsFuncJob(IsJob, Protocol):
    """"""
    param_signatures: MappingProxyType
    return_type: Type[object]
    iterate_over_data_files: bool
    fixed_params: MappingProxyType[str, object]
    param_key_map: MappingProxyType[str, str]
    result_key: Optional[str]
    persist_outputs: Optional[PersistOutputsOptions]
    restore_outputs: Optional[RestoreOutputsOptions]
    will_persist_outputs: PersistOutputsOptions
    will_restore_outputs: RestoreOutputsOptions

    def has_coroutine_func(self) -> bool:
        ...

    def get_call_args(self, *args: object, **kwargs: object) -> Dict[str, object]:
        ...


class IsFuncJobTemplate(IsJobTemplate, Protocol):
    """"""
    name: str
    unique_name: str
    param_signatures: MappingProxyType
    return_type: Type[object]
    iterate_over_data_files: bool
    fixed_params: MappingProxyType[str, object]
    param_key_map: MappingProxyType[str, str]
    result_key: Optional[str]
    persist_outputs: Optional[PersistOutputsOptions]
    restore_outputs: Optional[RestoreOutputsOptions]
    will_persist_outputs: PersistOutputsOptions
    will_restore_outputs: RestoreOutputsOptions

    def apply(self) -> IsFuncJob:
        ...

    def refine(self,
               update: bool = True,
               name: Optional[str] = None,
               iterate_over_data_files: bool = False,
               fixed_params: Optional[Mapping[str, object]] = None,
               param_key_map: Optional[Mapping[str, str]] = None,
               result_key: Optional[str] = None,
               persist_outputs: Optional[PersistOutputsOptions] = None,
               restore_outputs: Optional[RestoreOutputsOptions] = None,
               **kwargs: object) -> 'IsFuncJobTemplate':
        ...

    def regenerate_unique_name(self) -> None:
        ...


class IsTask(IsFuncJob, Protocol):
    """"""
    ...


class IsTaskTemplate(IsFuncJobTemplate, Protocol):
    """"""
    def apply(self) -> IsTask:
        ...


class IsFlow(IsFuncJob, Protocol):
    """"""
    flow_context: IsNestedContext
    time_of_last_run: datetime


class IsFlowTemplate(IsFuncJobTemplate, Protocol):
    """"""
    def apply(self) -> IsFlow:
        ...


class IsTaskTemplatesFlow(IsFlow, Protocol):
    """"""
    task_templates: Tuple[IsTaskTemplate, ...]

    def _accept_call_func_decorator(self, call_func_decorator: GeneralDecorator) -> None:
        ...


class IsTaskTemplatesFlowTemplate(IsFuncJobTemplate, Protocol):
    """"""
    task_templates: Tuple[IsTaskTemplate, ...]

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
               **kwargs: object) -> 'IsTaskTemplatesFlowTemplate':
        ...


class IsLinearFlow(IsTaskTemplatesFlow, Protocol):
    """"""
    ...


class IsLinearFlowTemplate(IsLinearFlow, IsTaskTemplatesFlowTemplate, Protocol):
    """"""
    def apply(self) -> IsLinearFlow:
        ...


class IsDagFlow(IsTaskTemplatesFlow, Protocol):
    """"""
    ...


class IsDagFlowTemplate(IsDagFlow, IsTaskTemplatesFlowTemplate, Protocol):
    """"""
    def apply(self) -> IsDagFlow:
        ...


class IsFuncFlow(IsFlow, Protocol):
    """"""
    ...


class IsFuncFlowTemplate(IsFuncFlow, IsFlowTemplate, Protocol):
    """"""
    def apply(self) -> IsFuncFlow:
        ...


class IsFuncJobTemplateCallable(Protocol[FuncJobTemplateT]):
    """"""
    def __call__(
        self,
        name: Optional[str] = None,
        iterate_over_data_files: bool = False,
        fixed_params: Optional[Mapping[str, object]] = None,
        param_key_map: Optional[Mapping[str, str]] = None,
        result_key: Optional[str] = None,
        persist_outputs: Optional[PersistOutputsOptions] = None,
        restore_outputs: Optional[RestoreOutputsOptions] = None,
        **kwargs: object,
    ) -> Callable[[Callable], FuncJobTemplateT]:
        ...


class IsTaskTemplatesFlowTemplateCallable(Protocol[TaskTemplatesFlowTemplateT]):
    """"""
    def __call__(
        self,
        *task_templates: 'TaskTemplate',
        name: Optional[str] = None,
        iterate_over_data_files: bool = False,
        fixed_params: Optional[Mapping[str, object]] = None,
        param_key_map: Optional[Mapping[str, str]] = None,
        result_key: Optional[str] = None,
        persist_outputs: Optional[PersistOutputsOptions] = None,
        restore_outputs: Optional[RestoreOutputsOptions] = None,
        **kwargs: object,
    ) -> Callable[[Callable], TaskTemplatesFlowTemplateT]:
        ...


class IsNestedContext(Protocol):
    """"""
    def __enter__(self):
        ...

    def __exit__(self, exc_type, exc_value, traceback):
        ...


class IsJobCreator(IsNestedContext, IsJobConfigHolder, Protocol):
    """"""
    nested_context_level: int
    time_of_cur_toplevel_nested_context_run: datetime
