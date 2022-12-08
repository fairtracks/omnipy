import asyncio
from datetime import datetime, timedelta
import inspect
from io import StringIO
import logging
import os
from time import sleep
from typing import Awaitable, Callable, cast, List, Optional, Type

from unifair.compute.job import JobConfig
from unifair.engine.base import Engine
from unifair.engine.constants import RunState
from unifair.engine.protocols import (IsDagFlow,
                                      IsDagFlowRunnerEngine,
                                      IsDagFlowTemplate,
                                      IsEngine,
                                      IsFlowTemplate,
                                      IsJob,
                                      IsRunStateRegistry,
                                      IsTask,
                                      IsTaskRunnerEngine,
                                      IsTaskTemplate)
from unifair.util.helpers import resolve

from .classes import JobCase, JobType


def read_log_lines_from_stream(str_stream: StringIO) -> List[str]:
    str_stream.seek(0)
    log_lines = [line.rstrip(os.linesep) for line in str_stream.readlines()]
    str_stream.seek(0)
    str_stream.truncate(0)
    return log_lines


def read_log_line_from_stream(str_stream: StringIO) -> str:
    log_lines = read_log_lines_from_stream(str_stream)
    if len(log_lines) == 1:
        return log_lines[0]
    else:
        assert len(log_lines) == 0
        return ''


def extract_engine(job: JobConfig):
    engine = job.__class__.job_creator.engine
    if hasattr(engine, '_engine'):  # TaskRunnerStateChecker
        engine = engine._engine  # noqa
    return engine


def extract_job_run_state(job: IsJob):
    engine = extract_engine(cast(JobConfig, job))
    registry = engine._registry  # noqa
    if registry:
        return registry.get_job_state(job)


def assert_job_state(job: IsJob, states: List[RunState]):
    job_state = extract_job_run_state(job)
    if job_state:
        assert job_state in states, job_state


def _check_timeout(start_time: datetime, timeout_secs: float, job: IsJob, states: List[RunState]):
    if datetime.now() - start_time >= timedelta(seconds=timeout_secs):
        raise TimeoutError(
            f'Run state of "{job.name}" not set to {[state.name for state in states]} '
            f'until timeout: {timeout_secs} sec(s). '
            f'Current state: {extract_job_run_state(job).name}')


def sync_wait_for_job_state(job: IsJob, states: List[RunState], timeout_secs: float = 1):
    start_time = datetime.now()
    while extract_job_run_state(job) not in states:
        sleep(0.001)
        _check_timeout(start_time, timeout_secs, job, states)


async def async_wait_for_job_state(job: IsJob, states: List[RunState], timeout_secs: float = 1):
    start_time = datetime.now()
    while extract_job_run_state(job) not in states:
        await asyncio.sleep(0.001)
        _check_timeout(start_time, timeout_secs, job, states)


def get_sync_assert_results_wait_a_bit_func(job: IsJob):
    def sync_assert_results_wait_a_bit(seconds: float) -> None:
        assert job(seconds) == seconds

    return sync_assert_results_wait_a_bit


def get_async_assert_results_wait_a_bit_func(job: IsJob):
    async def async_assert_results_wait_a_bit(seconds: float) -> Awaitable:
        assert await resolve(job(seconds)) == seconds

    return async_assert_results_wait_a_bit


def check_engine_cls(job: IsJob, engine_cls: type[Engine]):
    return isinstance(extract_engine(job), engine_cls)


def add_logger_to_registry(registry: IsRunStateRegistry) -> IsRunStateRegistry:
    logger = logging.getLogger('uniFAIR')
    logger.setLevel(logging.INFO)
    registry.set_logger(logger)
    return registry


def create_task_with_func(
    name: str,
    func: Callable,
    task_template_cls: type(IsTaskTemplate),
    engine: IsTaskRunnerEngine,
    registry: Optional[IsRunStateRegistry],
) -> IsTask:

    task_template = task_template_cls(name=name)(func)

    task_template_cls.job_creator.set_engine(engine)
    if registry:
        engine.set_registry(registry)

    return task_template.apply()


def create_dag_flow_with_two_func_tasks(
    name: str,
    func: Callable,
    task_template_cls: type(IsTaskTemplate),
    dag_flow_template_cls: type(IsDagFlowTemplate),
    engine: IsDagFlowRunnerEngine,
    registry: Optional[IsRunStateRegistry],
) -> IsDagFlow:

    task_template = task_template_cls(name=name)(func)
    dag_flow_template = dag_flow_template_cls(task_template, task_template, name=name)(func)

    task_template_cls.job_creator.set_engine(engine)
    if registry:
        engine.set_registry(registry)

    return dag_flow_template.apply()


def update_job_case_with_job(
    job_case: JobCase,
    job_type: JobType,
    task_template_cls: Type[IsTaskTemplate],
    flow_template_cls: Optional[Type[IsFlowTemplate]],
    engine: Type[IsEngine],
    engine_decorator: Optional[Callable[[IsEngine], IsEngine]],
    registry: Optional[IsRunStateRegistry],
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

    return job_case


async def run_job_test(job_case: JobCase):
    await resolve(job_case.run_and_assert_results_func(job_case.job))
