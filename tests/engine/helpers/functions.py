"""Helper functions for engine tests."""

import asyncio
from datetime import datetime, timedelta
from time import sleep
from typing import Callable, cast, Type

from omnipy.shared.enums.job import JobType, RunState
from omnipy.shared.protocols.compute.job import (HasJobCreator,
                                                 IsDagFlow,
                                                 IsDagFlowTemplate,
                                                 IsFlowTemplate,
                                                 IsFuncArgJob,
                                                 IsFuncArgJobTemplate,
                                                 IsFuncFlow,
                                                 IsFuncFlowTemplate,
                                                 IsJob,
                                                 IsJobBase,
                                                 IsLinearFlow,
                                                 IsLinearFlowTemplate,
                                                 IsTask,
                                                 IsTaskTemplate)
from omnipy.shared.protocols.engine.base import IsEngine
from omnipy.shared.protocols.engine.job_runner import IsJobRunnerEngine
from omnipy.shared.protocols.hub.registry import IsRunStateRegistry
from omnipy.util.callable_types import CallableType
from omnipy.util.helpers import resolve

from .classes import ComposedFlowCase, JobCase


def extract_engine(job: IsJobBase) -> IsEngine:
    engine = cast(HasJobCreator, job.__class__).job_creator.engine
    assert engine is not None
    if engine and hasattr(engine, '_engine'):  # TaskRunnerStateChecker
        engine = engine._engine  # pyright: ignore[reportAttributeAccessIssue]
    return engine


def extract_job_run_state(job: IsJob) -> RunState.Literals | None:
    """Provide extract job run state for test reuse."""
    engine = extract_engine(cast(IsJobBase, job))
    registry = engine.registry
    if registry:
        return registry.get_job_state(job)


def assert_job_state(job: IsJob, states: list[RunState.Literals]):
    """Assert job state."""
    job_state = extract_job_run_state(job)
    if job_state:
        assert job_state in states, job_state


def apply_job(
    template: IsFuncArgJobTemplate,
    engine: IsEngine,
    registry: IsRunStateRegistry | None,
):
    """Apply a template with engine and registry wiring."""
    cast(HasJobCreator, type(template)).job_creator.set_engine(engine)
    if registry:
        engine.set_registry(registry)
    return template.apply()


def _check_timeout(
    start_time: datetime,
    timeout_secs: float,
    job: IsJob,
    states: list[RunState.Literals],
):
    """Provide check timeout for test reuse."""
    if datetime.now() - start_time >= timedelta(seconds=timeout_secs):
        current_state = extract_job_run_state(job)
        current_state_text = (
            RunState.name_for_value(current_state) if current_state else 'Unable to extract state')
        raise TimeoutError(f'Run state of "{job.name}" not set to '
                           f'{[RunState.name_for_value(state) for state in states]} '
                           f'until timeout: {timeout_secs} sec(s). '
                           f'Current state: {current_state_text}')


def sync_wait_for_job_state(job: IsJob, states: list[RunState.Literals], timeout_secs: float = 1):
    """Provide sync wait for job state for test reuse."""
    start_time = datetime.now()
    while extract_job_run_state(job) not in states:
        sleep(0.001)
        _check_timeout(start_time, timeout_secs, job, states)


async def async_wait_for_job_state(job: IsJob,
                                   states: list[RunState.Literals],
                                   timeout_secs: float = 1):
    """Provide async wait for job state for test reuse."""
    start_time = datetime.now()
    while extract_job_run_state(job) not in states:
        await asyncio.sleep(0.001)
        _check_timeout(start_time, timeout_secs, job, states)


def get_sync_assert_results_wait_a_bit_func(job: IsJob):
    """Return sync assert results wait a bit func."""
    def sync_assert_results_wait_a_bit(seconds: float) -> None:
        assert job(seconds) == seconds

    return sync_assert_results_wait_a_bit


def get_async_assert_results_wait_a_bit_func(job: IsJob):
    """Return async assert results wait a bit func."""
    async def async_assert_results_wait_a_bit(seconds: float) -> None:
        assert await resolve(job(seconds)) == seconds

    return async_assert_results_wait_a_bit


def check_engine_cls(job: IsJob, engine_cls: type[IsEngine]):
    """Check engine class."""
    return isinstance(extract_engine(job), engine_cls)


def create_task_with_func(
    name: str,
    func: Callable,
    task_template_cls: type[IsTaskTemplate],
    engine: IsJobRunnerEngine,
    registry: IsRunStateRegistry | None,
) -> IsTask:
    """Provide create task with func for test reuse."""
    task_template = task_template_cls(name=name)(func)

    task_template_cls.job_creator.set_engine(engine)  # type: ignore[attr-defined]
    if registry:
        engine.set_registry(registry)

    return task_template.apply()


def create_linear_flow_with_two_func_tasks(
    name: str,
    func: Callable,
    task_template_cls: type[IsTaskTemplate],
    linear_flow_template_cls: type[IsLinearFlowTemplate],
    engine: IsJobRunnerEngine,
    registry: IsRunStateRegistry | None,
) -> IsLinearFlow:
    """Provide create linear flow with two func tasks for test reuse."""
    @task_template_cls()
    def _passthrough_task(arg):
        return arg

    @task_template_cls()
    def _passthrough_generator_task(arg):
        yield from arg

    task_template_func = task_template_cls(name=name)(func)
    if task_template_func.callable_type is CallableType.SYNC_GENERATOR:
        # This is needed as Prefect 3 coerces returned generators from
        # regular synchronous functions to lists. If the task is instead
        # wrapping a generator function, the generator is recognized and
        # handled.
        passthrough_task = _passthrough_generator_task
    else:
        passthrough_task = _passthrough_task

    linear_flow_template = linear_flow_template_cls(
        task_template_func,
        passthrough_task,
        name=name,
    )(func,)

    cast(HasJobCreator, task_template_cls).job_creator.set_engine(engine)
    if registry:
        engine.set_registry(registry)

    return linear_flow_template.apply()


def create_dag_flow_with_two_func_tasks(
    name: str,
    func: Callable,
    task_template_cls: type[IsTaskTemplate],
    dag_flow_template_cls: type[IsDagFlowTemplate],
    engine: IsJobRunnerEngine,
    registry: IsRunStateRegistry | None,
) -> IsDagFlow:
    """Provide create dag flow with two func tasks for test reuse."""
    task_template = task_template_cls(name=name)(func)
    dag_flow_template = dag_flow_template_cls(task_template, task_template, name=name)(func)

    cast(HasJobCreator, task_template_cls).job_creator.set_engine(engine)
    if registry:
        engine.set_registry(registry)

    return dag_flow_template.apply()


def create_func_flow_with_two_func_tasks(
    name: str,
    func: Callable,
    task_template_cls: type[IsTaskTemplate],
    func_flow_template_cls: type[IsFuncFlowTemplate],
    engine: IsJobRunnerEngine,
    registry: IsRunStateRegistry | None,
) -> IsFuncFlow:

    """Provide create func flow with two func tasks for test reuse."""
    task_template = task_template_cls(name=name)(func)

    task_template_cls.job_creator.set_engine(engine)  # type: ignore[attr-defined]
    if registry:
        engine.set_registry(registry)

    if task_template.callable_type is CallableType.SYNC_GENERATOR:

        @func_flow_template_cls(name=name)
        def sync_generator_func_flow_template(*args: object, **kwargs: object):
            task_template(*args, **kwargs)
            yield from task_template(*args, **kwargs)

        return sync_generator_func_flow_template.apply()

    else:

        @func_flow_template_cls(name=name)
        def plain_func_flow_template(*args: object, **kwargs: object) -> object:
            task_template(*args, **kwargs)
            return task_template(*args, **kwargs)

        return plain_func_flow_template.apply()


def update_job_case_with_job(
    job_case: JobCase,
    job_type: JobType.Literals,
    task_template_cls: Type[IsTaskTemplate],
    flow_template_cls: Type[IsFlowTemplate] | None,
    engine: IsJobRunnerEngine,
    engine_decorator: Callable[[IsJobRunnerEngine], IsJobRunnerEngine] | None,
    registry: IsRunStateRegistry | None,
):
    """Provide update job case with job for test reuse."""
    if engine_decorator:
        engine = engine_decorator(engine)

    job_case.job_type = job_type
    if job_type == JobType.TASK:
        job_case.job = create_task_with_func(
            job_case.name,
            job_case.job_func,
            task_template_cls,
            engine,
            registry,
        )
    elif job_type == JobType.LINEAR_FLOW:
        job_case.job = create_linear_flow_with_two_func_tasks(
            job_case.name,
            job_case.job_func,
            task_template_cls,
            cast(type[IsLinearFlowTemplate], flow_template_cls),
            engine,
            registry,
        )
    elif job_type == JobType.DAG_FLOW:
        job_case.job = create_dag_flow_with_two_func_tasks(
            job_case.name,
            job_case.job_func,
            task_template_cls,
            cast(type[IsDagFlowTemplate], flow_template_cls),
            engine,
            registry,
        )
    elif job_type == JobType.FUNC_FLOW:
        job_case.job = create_func_flow_with_two_func_tasks(
            job_case.name,
            job_case.job_func,
            task_template_cls,
            cast(type[IsFuncFlowTemplate], flow_template_cls),
            engine,
            registry,
        )

    return job_case


def apply_composed_flow_case(
    job_case: ComposedFlowCase,
    engine: IsEngine,
    registry: IsRunStateRegistry | None,
) -> IsFuncArgJob:
    job_case.job = job_case.build_job_func(engine, registry)
    return job_case.job


async def run_job_test(job_case: JobCase | ComposedFlowCase):
    """Provide run job test for test reuse."""
    assert job_case.job is not None
    await resolve(job_case.run_and_assert_results_func(job_case.job))
