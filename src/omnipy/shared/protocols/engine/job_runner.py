"""Protocols for engines that decorate runnable jobs."""

import os
from textwrap import dedent
from typing import Callable, Protocol, runtime_checkable

from omnipy.shared.enums.job import JobType
from omnipy.shared.protocols.compute.job import IsFuncArgJob
from omnipy.shared.protocols.engine.base import IsEngine
from omnipy.util.helpers import is_package_editable

if is_package_editable('omnipy'):
    os.environ['OMNIPY_MACRO_ISTASKRUNNERENGINE_APPLY_TASK_DECORATOR_SUMMARY'] = (
        'Attach a state-aware decorator to a task callback endpoint.')
    os.environ['OMNIPY_MACRO_ISTASKRUNNERENGINE_APPLY_TASK_DECORATOR_DETAILS'] = dedent("""\
        Args:
            task: Task object being prepared for execution.
            job_callback_accept_decorator: Consumer that accepts a task decorator.
    """)

    os.environ['OMNIPY_MACRO_ISLINEARFLOWRUNNERENGINE_APPLY_LINEAR_FLOW_DECORATOR_SUMMARY'] = (
        'Attach a state-aware decorator to a linear-flow callback endpoint.')
    os.environ['OMNIPY_MACRO_ISLINEARFLOWRUNNERENGINE_APPLY_LINEAR_FLOW_DECORATOR_DETAILS'] = (
        dedent("""\
        Args:
            linear_flow: Linear flow object being prepared for execution.
            job_callback_accept_decorator: Consumer that accepts a flow decorator.
    """))

    os.environ['OMNIPY_MACRO_ISDAGFLOWRUNNERENGINE_APPLY_DAG_FLOW_DECORATOR_SUMMARY'] = (
        'Attach a state-aware decorator to a DAG-flow callback endpoint.')
    os.environ['OMNIPY_MACRO_ISDAGFLOWRUNNERENGINE_APPLY_DAG_FLOW_DECORATOR_DETAILS'] = (
        dedent("""\
        Args:
            dag_flow: DAG flow object being prepared for execution.
            job_callback_accept_decorator: Consumer that accepts a flow decorator.
    """))

    os.environ['OMNIPY_MACRO_ISFUNCFLOWRUNNERENGINE_APPLY_FUNC_FLOW_DECORATOR_SUMMARY'] = (
        'Attach a state-aware decorator to a function-flow callback endpoint.')
    os.environ['OMNIPY_MACRO_ISFUNCFLOWRUNNERENGINE_APPLY_FUNC_FLOW_DECORATOR_DETAILS'] = (
        dedent("""\
        Args:
            func_flow: Function flow object being prepared for execution.
            job_callback_accept_decorator: Consumer that accepts a flow decorator.
    """))


@runtime_checkable
class IsJobRunnerEngine(IsEngine, Protocol):
    """"""
    supported_job_types: frozenset[JobType.Literals]

    def supports(self, job_type: JobType.Literals) -> bool:
        """Return whether the engine can initialize and run ``job_type`` jobs.

        Args:
            job_type: Job category to test.

        Returns:
            bool: ``True`` when ``job_type`` is supported by the engine.
        """
        ...

    def apply_job_decorator(
        self,
        job_type: JobType.Literals,
        job: IsFuncArgJob,
        job_callback_accept_decorator: Callable,
    ) -> None:
        """Attach the engine's execution decorator to a job callback endpoint.

        Args:
            job_type: Job category selecting the run behavior.
            job: Job instance being prepared for execution.
            job_callback_accept_decorator: Consumer that accepts the engine-provided
                decorator.
        """
        ...
