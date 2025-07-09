import asyncio
from datetime import datetime, timedelta
from time import sleep
from typing import Callable, cast, Type

from omnipy.shared.enums import RunState
from omnipy.shared.protocols.compute._job import IsJob, IsJobBase
from omnipy.shared.protocols.compute.job import (IsDagFlow,
                                                 IsDagFlowTemplate,
                                                 IsFlowTemplate,
                                                 IsFuncFlowTemplate,
                                                 IsLinearFlow,
                                                 IsLinearFlowTemplate,
                                                 IsTask,
                                                 IsTaskTemplate)
from omnipy.shared.protocols.engine.base import IsEngine
from omnipy.shared.protocols.engine.job_runner import (IsDagFlowRunnerEngine,
                                                       IsFuncFlowRunnerEngine,
                                                       IsLinearFlowRunnerEngine,
                                                       IsTaskRunnerEngine)
from omnipy.shared.protocols.hub.registry import IsRunStateRegistry
from omnipy.util.helpers import resolve

from .classes import JobCase, JobType


def extract_engine(job: IsJobBase) -> IsEngine:
    engine = job.__class__.job_creator.engine
    if hasattr(engine, '_engine'):  # TaskRunnerStateChecker
        engine = engine._engine  # noqa
    return engine


def extract_job_run_state(job: IsJob) -> RunState.Literals | None:
    engine = extract_engine(cast(IsJobBase, job))
    registry = engine.registry
    if registry:
        return registry.get_job_state(job)


def assert_job_state(job: IsJob, states: list[RunState.Literals]):
    job_state = extract_job_run_state(job)
    if job_state:
        assert job_state in states, job_state


def _check_timeout(
    start_time: datetime,
    timeout_secs: float,
    job: IsJob,
    states: list[RunState.Literals],
):
    if datetime.now() - start_time >= timedelta(seconds=timeout_secs):
        current_state = extract_job_run_state(job)
        current_state_text = (
            RunState.name_for_value(current_state) if current_state else 'Unable to extract state')
        raise TimeoutError(f'Run state of "{job.name}" not set to '
                           f'{[RunState.name_for_value(state) for state in states]} '
                           f'until timeout: {timeout_secs} sec(s). '
                           f'Current state: {current_state_text}')


def sync_wait_for_job_state(job: IsJob, states: list[RunState.Literals], timeout_secs: float = 1):
    start_time = datetime.now()
    while extract_job_run_state(job) not in states:
        sleep(0.001)
        _check_timeout(start_time, timeout_secs, job, states)


async def async_wait_for_job_state(job: IsJob,
                                   states: list[RunState.Literals],
                                   timeout_secs: float = 1):
    start_time = datetime.now()
    while extract_job_run_state(job) not in states:
        await asyncio.sleep(0.001)
        _check_timeout(start_time, timeout_secs, job, states)


def get_sync_assert_results_wait_a_bit_func(job: IsJob):
    def sync_assert_results_wait_a_bit(seconds: float) -> None:
        assert job(seconds) == seconds

    return sync_assert_results_wait_a_bit


def get_async_assert_results_wait_a_bit_func(job: IsJob):
    async def async_assert_results_wait_a_bit(seconds: float) -> None:
        assert await resolve(job(seconds)) == seconds

    return async_assert_results_wait_a_bit


def check_engine_cls(job: IsJob, engine_cls: type[IsEngine]):
    return isinstance(extract_engine(job), engine_cls)


def create_task_with_func(
    name: str,
    func: Callable,
    task_template_cls: type[IsTaskTemplate],
    engine: IsTaskRunnerEngine,
    registry: IsRunStateRegistry | None,
) -> IsTask:

    task_template = task_template_cls(name=name)(func)

    task_template_cls.job_creator.set_engine(engine)
    if registry:
        engine.set_registry(registry)

    return task_template.apply()


def create_linear_flow_with_two_func_tasks(
    name: str,
    func: Callable,
    task_template_cls: type[IsTaskTemplate],
    linear_flow_template_cls: type[IsLinearFlowTemplate],
    engine: IsLinearFlowRunnerEngine,
    registry: IsRunStateRegistry | None,
) -> IsLinearFlow:
    @task_template_cls
    def passthrough_task(arg):
        return arg

    task_template_func = task_template_cls(name=name)(func)
    linear_flow_template = linear_flow_template_cls(
        task_template_func,
        passthrough_task,
        name=name,
    )(func,)

    task_template_cls.job_creator.set_engine(engine)
    if registry:
        engine.set_registry(registry)

    return linear_flow_template.apply()


def create_dag_flow_with_two_func_tasks(
    name: str,
    func: Callable,
    task_template_cls: type[IsTaskTemplate],
    dag_flow_template_cls: type[IsDagFlowTemplate],
    engine: IsDagFlowRunnerEngine,
    registry: IsRunStateRegistry | None,
) -> IsDagFlow:

    task_template = task_template_cls(name=name)(func)
    dag_flow_template = dag_flow_template_cls(task_template, task_template, name=name)(func)

    task_template_cls.job_creator.set_engine(engine)
    if registry:
        engine.set_registry(registry)

    return dag_flow_template.apply()


def create_func_flow_with_two_func_tasks(
    name: str,
    func: Callable,
    task_template_cls: type[IsTaskTemplate],
    func_flow_template_cls: type[IsFuncFlowTemplate],
    engine: IsFuncFlowRunnerEngine,
    registry: IsRunStateRegistry | None,
) -> IsDagFlow:

    task_template = task_template_cls(name=name)(func)

    @func_flow_template_cls(name=name)
    def func_flow_template(*args: object, **kwargs: object) -> object:
        for i in range(2):
            result = task_template(*args, **kwargs)
        return result  # noqa

    task_template_cls.job_creator.set_engine(engine)
    if registry:
        engine.set_registry(registry)

    return func_flow_template.apply()


def update_job_case_with_job(
    job_case: JobCase,
    job_type: JobType,
    task_template_cls: Type[IsTaskTemplate],
    flow_template_cls: Type[IsFlowTemplate] | None,
    engine: IsEngine,
    engine_decorator: Callable[[IsEngine], IsEngine] | None,
    registry: IsRunStateRegistry | None,
):
    if engine_decorator:
        engine = engine_decorator(engine)

    job_case.job_type = job_type
    if job_type.value == JobType.task.value:
        job_case.job = create_task_with_func(
            job_case.name,
            job_case.job_func,
            task_template_cls,
            cast(IsTaskRunnerEngine, engine),
            registry,
        )
    elif job_type.value == JobType.linear_flow.value:
        engine = cast(IsLinearFlowRunnerEngine, engine)
        job_case.job = create_linear_flow_with_two_func_tasks(
            job_case.name,
            job_case.job_func,
            task_template_cls,
            flow_template_cls,
            cast(IsLinearFlowRunnerEngine, engine),
            registry,
        )
    elif job_type.value == JobType.dag_flow.value:
        engine = cast(IsDagFlowRunnerEngine, engine)
        job_case.job = create_dag_flow_with_two_func_tasks(
            job_case.name,
            job_case.job_func,
            task_template_cls,
            flow_template_cls,
            cast(IsDagFlowRunnerEngine, engine),
            registry,
        )
    elif job_type.value == JobType.func_flow.value:
        engine = cast(IsFuncFlowRunnerEngine, engine)
        job_case.job = create_func_flow_with_two_func_tasks(
            job_case.name,
            job_case.job_func,
            task_template_cls,
            flow_template_cls,
            cast(IsFuncFlowRunnerEngine, engine),
            registry,
        )

    return job_case


async def run_job_test(job_case: JobCase):
    await resolve(job_case.run_and_assert_results_func(job_case.job))
