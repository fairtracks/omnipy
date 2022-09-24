from datetime import datetime
import logging
from typing import Any, Callable, Optional, Protocol, Tuple, Type

from unifair.engine.constants import EngineChoice, RunState


class IsEngineConfig(Protocol):
    ...


class IsLocalRunnerConfig(IsEngineConfig, Protocol):
    ...


class IsPrefectEngineConfig(IsEngineConfig, Protocol):
    ...


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
    local: 'IsEngine'
    prefect: 'IsEngine'

    def __init__(
            self,
            logger: Optional[logging.Logger] = None,  # noqa
            registry: Optional['IsRunStateRegistry'] = None,  # noqa
            local: Optional['IsEngine'] = None,  # noqa
            prefect: Optional['IsEngine'] = None,  # noqa
            *args: Any,
            **kwargs: Any) -> None:
        ...


class IsRuntimeClasses(IsConfigPublisher, Protocol):
    task_template: Type['IsTaskTemplate']

    def __init__(
            self,
            task: Type['IsTaskTemplate'] = None,  # noqa
            *args: Any,
            **kwargs: Any) -> None:
        ...


class IsRuntime(IsConfigPublisher, Protocol):
    object: IsRuntimeObjects
    classes: IsRuntimeClasses
    config: IsRuntimeConfig

    def __init__(
            self,
            object: Optional[IsRuntimeObjects] = None,  # noqa
            classes: Optional[IsRuntimeClasses] = None,  # noqa
            config: Optional[IsRuntimeConfig] = None,  # noqa
            *args: Any,
            **kwargs: Any) -> None:
        ...


class IsTask(Protocol):
    name: str

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        ...

    def _call_func(self, *args: Any, **kwargs: Any) -> Any:
        ...

    def has_coroutine_task_func(self) -> bool:
        ...

    @classmethod
    def set_engine(cls, engine: 'IsEngine') -> None:
        ...


class IsTaskTemplate(IsTask, Protocol):
    def apply(self) -> IsTask:
        ...


class IsRunStateRegistry(Protocol):
    def __init__(self) -> None:
        ...

    def get_task_state(self, task: IsTask) -> RunState:
        ...

    def get_task_state_datetime(self, task: IsTask, state: RunState) -> datetime:
        ...

    def all_tasks(self, state: Optional[RunState] = None) -> Tuple[IsTask, ...]:  # noqa
        ...

    def set_task_state(self, task: IsTask, state: RunState) -> None:
        ...

    def set_logger(self, logger: Optional[logging.Logger]) -> None:
        ...

    def set_config(self, config: IsRunStateRegistryConfig) -> None:
        ...


class IsEngine(Protocol):
    def __init__(self) -> None:
        ...

    @classmethod
    def get_config_cls(cls) -> Type[IsEngineConfig]:
        ...

    def set_config(self, config: IsEngineConfig) -> None:
        ...

    def set_registry(self, registry: Optional[IsRunStateRegistry]) -> None:
        ...


class IsTaskRunnerEngine(IsEngine, Protocol):
    def task_decorator(self, task: IsTask) -> IsTask:
        ...
