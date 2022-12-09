from datetime import datetime
import logging
from typing import Any, Callable, Dict, Optional, Protocol, runtime_checkable, Tuple, Type

from unifair.engine.constants import EngineChoice, RunState


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
    engine: EngineChoice
    local: IsLocalRunnerConfig
    prefect: IsPrefectEngineConfig
    registry: IsRunStateRegistryConfig

    def __init__(
            self,
            engine: EngineChoice = EngineChoice.LOCAL,  # noqas
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
    object: IsRuntimeObjects
    config: IsRuntimeConfig

    def __init__(
            self,
            object: Optional[IsRuntimeObjects] = None,  # noqa
            config: Optional[IsRuntimeConfig] = None,  # noqa
            *args: Any,
            **kwargs: Any) -> None:
        ...


class IsJobCreator(Protocol):
    engine: Optional['IsTaskRunnerEngine']

    def set_engine(self, engine: 'IsTaskRunnerEngine') -> None:
        ...


class IsJob(Protocol):
    name: str
    unique_name: str
    flow_context: IsJobCreator
    in_flow_context: bool

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        ...

    def _call_func(self, *args: Any, **kwargs: Any) -> Any:
        ...

    def regenerate_unique_name(self) -> None:
        ...


class IsJobTemplate(Protocol):
    job_creator: IsJobCreator
    in_flow_context: bool

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        pass


class IsTask(IsJob, Protocol):
    def has_coroutine_func(self) -> bool:
        ...


class IsTaskTemplate(IsJobTemplate, Protocol):
    def apply(self) -> IsTask:
        ...


class IsFlow(IsJob, Protocol):
    def has_coroutine_func(self) -> bool:
        ...


class IsFlowTemplate(IsJobTemplate, Protocol):
    def apply(self) -> IsFlow:
        ...


class IsLinearFlow(IsFlow, Protocol):
    task_templates: Tuple[IsTaskTemplate]

    def has_coroutine_func(self) -> bool:
        ...

    def get_call_args(self, *args, **kwargs) -> Dict[str, object]:
        ...


class IsLinearFlowTemplate(IsLinearFlow, IsFlowTemplate, Protocol):
    ...


class IsDagFlow(IsFlow, Protocol):
    task_templates: Tuple[IsTaskTemplate]

    def has_coroutine_func(self) -> bool:
        ...

    def get_call_args(self, *args, **kwargs) -> Dict[str, object]:
        ...


class IsDagFlowTemplate(IsDagFlow, IsFlowTemplate, Protocol):
    ...


class IsFuncFlow(IsFlow, Protocol):
    ...


class IsFuncFlowTemplate(IsFuncFlow, IsFlowTemplate, Protocol):
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
