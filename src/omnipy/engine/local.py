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
        """Initialize local-runner-specific engine state.

        Args:
            None.

        Returns:
            None.

        Raises:
            None.

        Example:
            >>> # LocalRunner currently has no extra initialization.
            >>> True
            True
        """
        ...

    def _update_from_config(self) -> None:
        """Apply updates when local runner config changes.

        Args:
            None.

        Returns:
            None.

        Raises:
            None.

        Example:
            >>> # LocalRunner currently has no config-dependent state.
            >>> True
            True
        """
        ...

    @classmethod
    def get_config_cls(cls) -> Type[IsLocalRunnerConfig]:
        """Return the config class used by the local runner engine.

        Args:
            cls: Local runner class.

        Returns:
            Type[IsLocalRunnerConfig]: Concrete local-runner config class.

        Raises:
            None.

        Example:
            >>> from omnipy.engine.local import LocalRunner
            >>> LocalRunner.get_config_cls().__name__
            'LocalRunnerConfig'
        """
        return LocalRunnerConfig

    def _init_task(self, task: TaskRunSpec) -> object:
        ...

    def _run_task(self, state: Any, task: TaskRunSpec, *args, **kwargs) -> object:
        return task.create_default_run_callable()(*args, **kwargs)

    def _init_flow(self, flow: FlowRunSpec) -> object:
        ...

    def _run_flow(self, state: Any, flow: FlowRunSpec, *args, **kwargs) -> object:
        return flow.create_default_run_callable()(*args, **kwargs)
