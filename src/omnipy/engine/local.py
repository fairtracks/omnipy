from typing import Any, Type

from omnipy.config.engine import LocalRunnerConfig
from omnipy.engine.job_runner import JobRunnerEngine
from omnipy.engine.run_spec import FlowRunSpec, TaskRunSpec
from omnipy.shared.enums.job import JobType
from omnipy.shared.protocols.config import IsLocalRunnerConfig


class LocalRunner(JobRunnerEngine):
    """Local job runner"""
    supported_job_types = frozenset({
        JobType.TASK,
        JobType.LINEAR_FLOW,
        JobType.DAG_FLOW,
        JobType.FUNC_FLOW,
    })

    def _init_engine(self) -> None:
        """Initialize local-runner-specific engine state."""
        ...

    def _update_from_config(self) -> None:
        """Apply updates when local runner config changes."""
        ...

    @classmethod
    def get_config_cls(cls) -> Type[IsLocalRunnerConfig]:
        """{{ISENGINE_GET_CONFIG_CLS_SUMMARY}}

        {{ISENGINE_GET_CONFIG_CLS_DETAILS}}"""
        return cast(Type[IsLocalRunnerConfig], LocalRunnerConfig)

    def _init_task(self, task: TaskRunSpec) -> object:
        ...

    def _run_task(self, state: Any, task: TaskRunSpec, *args, **kwargs) -> object:
        return task.create_default_run_callable()(*args, **kwargs)

    def _init_flow(self, flow: FlowRunSpec) -> object:
        ...

    def _run_flow(self, state: Any, flow: FlowRunSpec, *args, **kwargs) -> object:
        return flow.create_default_run_callable()(*args, **kwargs)
