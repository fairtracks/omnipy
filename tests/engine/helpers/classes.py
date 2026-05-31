"""Helper classes for engine tests."""

from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Generic, ParamSpec, Type, TypeVar

from typing_extensions import override

from omnipy.engine.run_spec import FlowRunSpec, TaskRunSpec
from omnipy.shared.enums.job import JobType, RunState
from omnipy.shared.protocols.compute.job import IsFuncArgJob
from omnipy.shared.protocols.config import IsJobRunnerConfig
from omnipy.shared.protocols.engine.job_runner import IsJobRunnerEngine
from omnipy.shared.protocols.hub.registry import IsRunStateRegistry

CallP = ParamSpec('CallP')
ReturnT = TypeVar('ReturnT')


@dataclass
class JobCase(Generic[CallP, ReturnT]):
    name: str
    job_func: Callable[CallP, ReturnT]
    run_and_assert_results_func: Callable[..., None | Awaitable[None]]
    job_type: JobType.Literals | None = None
    job: IsFuncArgJob | None = None


class JobRunnerStateChecker(IsJobRunnerEngine):
    def __init__(self, engine: IsJobRunnerEngine):
        object.__init__(self)
        self._engine = engine
        self.supported_job_types = self._engine.supported_job_types
        self._engine.__init__()

    def set_config(self, config: IsJobRunnerConfig) -> None:
        self._engine.set_config(config)

    def set_registry(self, registry: IsRunStateRegistry | None) -> None:
        self._engine.set_registry(registry)

    @property
    def config(self) -> IsJobRunnerConfig:
        return self._engine.config

    @property
    def registry(self) -> IsRunStateRegistry | None:
        return self._engine.registry

    @override
    def get_config_cls(self) -> Type[IsJobRunnerConfig]:  # type: ignore[override]
        return self._engine.get_config_cls()  # noqa

    def supports(self, job_type: JobType.Literals) -> bool:
        return self._engine.supports(job_type)

    def apply_job_decorator(self,
                            job_type: JobType.Literals,
                            job: IsFuncArgJob,
                            job_callback_accept_decorator: Callable) -> None:
        return self._engine.apply_job_decorator(job_type, job, job_callback_accept_decorator)

    def _init_task(self, task: TaskRunSpec) -> object:
        from .functions import assert_job_state
        assert_job_state(task._job, [RunState.INITIALIZED])
        return self._engine._init_task(task)  # noqa

    def _run_task(self, state: Any, task: TaskRunSpec, *args, **kwargs) -> object:
        from .functions import assert_job_state
        assert_job_state(task._job, [RunState.RUNNING])
        return self._engine._run_task(state, task, *args, **kwargs)  # noqa

    def _init_flow(self, flow: FlowRunSpec) -> object:
        from .functions import assert_job_state
        assert_job_state(flow._job, [RunState.INITIALIZED])
        return self._engine._init_flow(flow)  # noqa

    def _run_flow(self, state: Any, flow: FlowRunSpec, *args, **kwargs) -> object:
        from .functions import assert_job_state
        assert_job_state(flow._job, [RunState.RUNNING])
        return self._engine._run_flow(state, flow, *args, **kwargs)  # noqa
