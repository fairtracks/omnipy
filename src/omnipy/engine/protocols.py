from datetime import datetime
import logging
from types import MappingProxyType
from typing import Any, Callable, Dict, Mapping, Optional, Protocol, runtime_checkable, Tuple, Type

from omnipy.compute.mixins.serialize import PersistOutputsOptions, RestoreOutputsOptions
from omnipy.config.job import ConfigPersistOutputsOptions, ConfigRestoreOutputsOptions
from omnipy.engine.constants import EngineChoice, RunState


class IsJobConfig(Protocol):
    persist_outputs: ConfigPersistOutputsOptions
    restore_outputs: ConfigRestoreOutputsOptions
    persist_data_dir_path: str


class IsEngineConfig(Protocol):
    ...


class IsLocalRunnerConfig(IsEngineConfig, Protocol):
    ...


class IsPrefectEngineConfig(IsEngineConfig, Protocol):
    use_cached_results: int = False


class IsRunStateRegistryConfig(Protocol):
    verbose: bool = True

    def __init__(
            self,
            verbose: bool = True,  # noqa
            *args: Any,
            **kwargs: Any) -> None:
        ...


class IsConfigPublisher(Protocol):
    def subscribe(self, config_item: str, callback_fun: Callable[[Any], None]):
        ...

    def unsubscribe_all(self) -> None:
        ...


class IsRuntimeConfig(IsConfigPublisher, Protocol):
    job: IsJobConfig
    engine: EngineChoice
    local: IsLocalRunnerConfig
    prefect: IsPrefectEngineConfig
    registry: IsRunStateRegistryConfig

    def __init__(
            self,
            job: Optional[IsJobConfig] = None,  # noqa
            engine: EngineChoice = EngineChoice.LOCAL,  # noqa
            local_config: Optional[IsLocalRunnerConfig] = None,  # noqa
            prefect_config: Optional[IsPrefectEngineConfig] = None,  # noqa
            registry_config: Optional[IsRunStateRegistryConfig] = None,  # noqa
            *args: Any,
            **kwargs: Any) -> None:
        ...


class IsRuntimeObjects(IsConfigPublisher, Protocol):
    logger: logging.Logger
    registry: 'IsRunStateRegistry'
    job_creator: 'IsJobCreator'
    local: 'IsEngine'
    prefect: 'IsEngine'

    def __init__(
            self,
            logger: Optional[logging.Logger] = None,  # noqa
            registry: Optional['IsRunStateRegistry'] = None,  # noqa
            job_creator: Optional['IsJobCreator'] = None,  # noqa
            local: Optional['IsEngine'] = None,  # noqa
            prefect: Optional['IsEngine'] = None,  # noqa
            *args: Any,
            **kwargs: Any) -> None:
        ...


class IsRuntime(IsConfigPublisher, Protocol):
    objects: IsRuntimeObjects
    config: IsRuntimeConfig

    def __init__(
            self,
            objects: Optional[IsRuntimeObjects] = None,  # noqa
            config: Optional[IsRuntimeConfig] = None,  # noqa
            *args: Any,
            **kwargs: Any) -> None:
        ...

    def reset_subscriptions(self):
        ...


class IsNestedContext(Protocol):
    def __enter__(self):
        ...

    def __exit__(self, exc_type, exc_value, traceback):
        ...


class IsJobCreator(IsNestedContext, Protocol):
    engine: Optional['IsTaskRunnerEngine']
    config: Optional[IsJobConfig]
    nested_context_level: int
    time_of_cur_toplevel_nested_context_run: datetime

    def set_config(self, config: IsJobConfig) -> None:
        ...

    def set_engine(self, engine: 'IsTaskRunnerEngine') -> None:
        ...


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
    engine: Optional['IsTaskRunnerEngine']
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

    def _call_func(self, *args: Any, **kwargs: Any) -> Any:
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


class IsTaskRunnerEngine(IsEngine, Protocol):
    def task_decorator(self, task: IsTask) -> IsTask:
        ...


@runtime_checkable
class IsLinearFlowRunnerEngine(IsEngine, Protocol):
    def linear_flow_decorator(self, linear_flow: IsLinearFlow) -> IsLinearFlow:
        ...


@runtime_checkable
class IsDagFlowRunnerEngine(IsEngine, Protocol):
    def dag_flow_decorator(self, dag_flow: IsDagFlow) -> IsDagFlow:
        ...


@runtime_checkable
class IsFuncFlowRunnerEngine(IsEngine, Protocol):
    def func_flow_decorator(self, dag_flow: IsFuncFlow) -> IsFuncFlow:
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

    def set_logger(self, logger: Optional[logging.Logger]) -> None:
        ...

    def set_config(self, config: IsRunStateRegistryConfig) -> None:
        ...
