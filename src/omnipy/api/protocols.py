from __future__ import annotations

from datetime import datetime
import logging
from logging.handlers import TimedRotatingFileHandler
from types import MappingProxyType
from typing import (Any,
                    Callable,
                    Dict,
                    Mapping,
                    Optional,
                    Protocol,
                    runtime_checkable,
                    Tuple,
                    Type,
                    TypeVar)

from omnipy.api.enums import (ConfigPersistOutputsOptions,
                              ConfigRestoreOutputsOptions,
                              EngineChoice,
                              PersistOutputsOptions,
                              RestoreOutputsOptions,
                              RunState)
from omnipy.api.types import GeneralDecorator, LocaleType


class IsNestedContext(Protocol):
    def __enter__(self):
        ...

    def __exit__(self, exc_type, exc_value, traceback):
        ...


class IsJobConfigHolder(Protocol):
    engine: Optional[IsEngine]
    config: Optional[IsJobConfig]

    def set_config(self, config: IsJobConfig) -> None:
        ...

    def set_engine(self, engine: IsEngine) -> None:
        ...


class IsJobCreator(IsNestedContext, IsJobConfigHolder, Protocol):
    nested_context_level: int
    time_of_cur_toplevel_nested_context_run: datetime


class IsJob(Protocol):
    name: str
    unique_name: str
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

    def regenerate_unique_name(self) -> None:
        ...

    def __eq__(self, other: object):
        ...


class IsJobTemplate(Protocol):
    config: Optional[IsJobConfig]
    engine: Optional[IsTaskRunnerEngine]
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
    ...


class IsTaskTemplate(IsFuncJobTemplate, Protocol):
    def apply(self) -> IsTask:
        ...


class IsFlow(IsFuncJob, Protocol):
    flow_context: IsNestedContext
    time_of_last_run: datetime


class IsFlowTemplate(IsFuncJobTemplate, Protocol):
    def apply(self) -> IsFlow:
        ...


class IsTaskTemplatesFlow(IsFlow, Protocol):
    task_templates: Tuple[IsTaskTemplate, ...]

    def _accept_call_func_decorator(self, call_func_decorator: GeneralDecorator) -> None:
        ...


class IsTaskTemplatesFlowTemplate(IsFuncJobTemplate, Protocol):
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
    ...


class IsLinearFlowTemplate(IsLinearFlow, IsTaskTemplatesFlowTemplate, Protocol):
    def apply(self) -> IsLinearFlow:
        ...


class IsDagFlow(IsTaskTemplatesFlow, Protocol):
    ...


class IsDagFlowTemplate(IsDagFlow, IsTaskTemplatesFlowTemplate, Protocol):
    def apply(self) -> IsDagFlow:
        ...


class IsFuncFlow(IsFlow, Protocol):
    ...


class IsFuncFlowTemplate(IsFuncFlow, IsFlowTemplate, Protocol):
    def apply(self) -> IsFuncFlow:
        ...


JobBaseT = TypeVar('JobBaseT', bound='JobBase', covariant=True)
JobT = TypeVar('JobT', bound='Job', covariant=True)
JobTemplateT = TypeVar('JobTemplateT', bound='JobTemplate', covariant=True)
FuncJobTemplateT = TypeVar('FuncJobTemplateT', bound='FuncJobTemplate', covariant=True)


class IsFuncJobTemplateCallable(Protocol[FuncJobTemplateT]):
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


TaskTemplatesFlowTemplateT = TypeVar(
    'TaskTemplatesFlowTemplateT', bound='TaskTemplatesFlowTemplate', covariant=True)


class IsTaskTemplatesFlowTemplateCallable(Protocol[TaskTemplatesFlowTemplateT]):
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


FlowT = TypeVar('FlowT', bound='Flow', covariant=True)
FlowBaseT = TypeVar('FlowBaseT', bound='FlowBase', covariant=True)
FlowTemplateT = TypeVar('FlowTemplateT', bound='FlowTemplate', covariant=True)


@runtime_checkable
class IsEngine(Protocol):
    def __init__(self) -> None:
        ...

    @classmethod
    def get_config_cls(cls) -> Type[IsEngineConfig]:
        ...

    def set_config(self, config: IsEngineConfig) -> None:
        ...

    def set_registry(self, registry: Optional['IsRunStateRegistry']) -> None:
        ...


@runtime_checkable
class IsTaskRunnerEngine(IsEngine, Protocol):
    def apply_task_decorator(self, task: IsTask, job_callback_accept_decorator: Callable) -> None:
        ...


@runtime_checkable
class IsLinearFlowRunnerEngine(IsEngine, Protocol):
    def apply_linear_flow_decorator(self,
                                    linear_flow: IsLinearFlow,
                                    job_callback_accept_decorator: Callable) -> None:
        ...


@runtime_checkable
class IsDagFlowRunnerEngine(IsEngine, Protocol):
    def apply_dag_flow_decorator(self, dag_flow: IsDagFlow,
                                 job_callback_accept_decorator: Callable) -> None:
        ...


@runtime_checkable
class IsFuncFlowRunnerEngine(IsEngine, Protocol):
    def apply_func_flow_decorator(self,
                                  func_flow: IsFuncFlow,
                                  job_callback_accept_decorator: Callable) -> None:
        ...


class IsRunStateRegistry(Protocol):
    def __init__(self) -> None:
        ...

    def get_job_state(self, job: IsJob) -> RunState:
        ...

    def get_job_state_datetime(self, job: IsJob, state: RunState) -> datetime:
        ...

    def all_jobs(self, state: Optional[RunState] = None) -> Tuple[IsJob, ...]:  # noqa
        ...

    def set_job_state(self, job: IsJob, state: RunState) -> None:
        ...


class IsEngineConfig(Protocol):
    ...


class IsLocalRunnerConfig(IsEngineConfig, Protocol):
    ...


class IsPrefectEngineConfig(IsEngineConfig, Protocol):
    use_cached_results: int = False


class IsDataPublisher(Protocol):
    def subscribe(self, config_item: str, callback_fun: Callable[[Any], None]):
        ...

    def unsubscribe_all(self) -> None:
        ...


class IsJobConfig(Protocol):
    persist_outputs: ConfigPersistOutputsOptions
    restore_outputs: ConfigRestoreOutputsOptions
    persist_data_dir_path: str


class IsRootLogConfig(Protocol):
    log_format_str: str
    locale: LocaleType
    log_to_stdout: bool
    log_to_stderr: bool
    log_to_file: bool
    stdout_log_min_level: int
    stderr_log_min_level: int
    file_log_min_level: int
    file_log_dir_path: str


class IsRootLogObjects(Protocol):
    formatter: Optional[logging.Formatter] = None
    stdout_handler: Optional[logging.StreamHandler] = None
    stderr_handler: Optional[logging.StreamHandler] = None
    file_handler: Optional[TimedRotatingFileHandler] = None

    def set_config(self, config: IsRootLogConfig) -> None:
        ...


class IsRootLogConfigEntryPublisher(IsRootLogConfig, IsDataPublisher, Protocol):
    ...


class IsRuntimeConfig(IsDataPublisher, Protocol):
    job: IsJobConfig
    engine: EngineChoice
    local: IsLocalRunnerConfig
    prefect: IsPrefectEngineConfig
    root_log: IsRootLogConfigEntryPublisher

    def __init__(
            self,
            job: Optional[IsJobConfig] = None,  # noqa
            engine: EngineChoice = EngineChoice.LOCAL,  # noqa
            local: Optional[IsLocalRunnerConfig] = None,  # noqa
            prefect: Optional[IsPrefectEngineConfig] = None,  # noqa
            root_log: Optional[IsRootLogConfigEntryPublisher] = None,  # noqa
            *args: Any,
            **kwargs: Any) -> None:
        ...


class IsRuntimeObjects(IsDataPublisher, Protocol):
    job_creator: IsJobConfigHolder
    local: IsEngine
    prefect: IsEngine
    registry: IsRunStateRegistry
    root_log: IsRootLogObjects

    def __init__(
            self,
            job_creator: Optional[IsJobConfigHolder] = None,  # noqa
            local: Optional[IsEngine] = None,  # noqa
            prefect: Optional[IsEngine] = None,  # noqa
            registry: Optional[IsRunStateRegistry] = None,  # noqa
            root_log: Optional[IsRootLogObjects] = None,  # noqa
            *args: Any,
            **kwargs: Any) -> None:
        ...


class IsRuntime(IsDataPublisher, Protocol):
    config: IsRuntimeConfig
    objects: IsRuntimeObjects

    def __init__(
            self,
            config: Optional[IsRuntimeConfig] = None,  # noqa
            objects: Optional[IsRuntimeObjects] = None,  # noqa
            *args: Any,
            **kwargs: Any) -> None:
        ...

    def reset_subscriptions(self):
        ...
