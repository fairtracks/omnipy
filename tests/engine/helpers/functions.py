import asyncio
from datetime import datetime, timedelta
from inspect import isawaitable
from io import StringIO
import logging
import os
from time import sleep
from typing import Awaitable, Callable, cast, List, Optional, Type

from unifair.compute.job import JobConfig
from unifair.engine.base import Engine
from unifair.engine.constants import RunState
from unifair.engine.protocols import (IsEngine,
                                      IsFlow,
                                      IsJobTemplate,
                                      IsRunStateRegistry,
                                      IsTask,
                                      IsTaskRunnerEngine,
                                      IsTaskTemplate)

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


def extract_run_state(task: IsTask):
    engine = extract_engine(task)
    registry = engine._registry
    if registry:
        return registry.get_task_state(task)


def assert_task_state(task: IsTask, states: List[RunState]):
    task_state = extract_run_state(task)
    if task_state:
        assert task_state in states, task_state


def _check_timeout(start_time: datetime, timeout_secs: float, task: IsTask, states: List[RunState]):
    if datetime.now() - start_time >= timedelta(seconds=timeout_secs):
        raise TimeoutError(
            f'Run state of "{task.name}" not set to {[state.name for state in states]} '
            f'until timeout: {timeout_secs} sec(s). '
            f'Current state: {extract_run_state(task).name}')


def sync_wait_for_task_state(task: IsTask, states: List[RunState], timeout_secs: float = 1):
    start_time = datetime.now()
    while extract_run_state(task) not in states:
        sleep(0.001)
        _check_timeout(start_time, timeout_secs, task, states)


async def async_wait_for_task_state(task: IsTask, states: List[RunState], timeout_secs: float = 1):
    start_time = datetime.now()
    while extract_run_state(task) not in states:
        await asyncio.sleep(0.001)
        _check_timeout(start_time, timeout_secs, task, states)


async def resolve(val):
    if isawaitable(val):
        return await val
    else:
        return val


def get_sync_assert_results_wait_a_bit_func(task: IsTask):
    def sync_assert_results_wait_a_bit(seconds: float) -> None:
        assert task(seconds) == seconds

    return sync_assert_results_wait_a_bit


def get_async_assert_results_wait_a_bit_func(task: IsTask):
    async def async_assert_results_wait_a_bit(seconds: float) -> Awaitable:
        assert await resolve(task(seconds)) == seconds

    return async_assert_results_wait_a_bit


def check_engine_cls(task: IsTask, engine_cls: type[Engine]):
    return isinstance(extract_engine(task), engine_cls)


def add_logger_to_registry(registry: IsRunStateRegistry) -> IsRunStateRegistry:
    logger = logging.getLogger('uniFAIR')
    logger.setLevel(logging.INFO)
    registry.set_logger(logger)
    return registry


def convert_func_to_task(
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


# def convert_func_to_dag_flow(
#     name: str,
#     func: Callable,
#     task_template_cls: type(IsTaskTemplate),
#     engine: IsTaskRunnerEngine,
#     registry: Optional[IsRunStateRegistry],
# ) -> IsTask:
#     task_template = task_template_cls(name, func)
#     task_template_cls.job_creator.set_engine(engine)
#     if registry:
#         engine.set_registry(registry)
#     return task_template.apply()


def update_job_case_with_job(
    job_case: JobCase,
    job_type: JobType,
    job_template_cls: Type[IsJobTemplate],
    engine: Type[IsEngine],
    engine_decorator: Optional[Callable[[IsEngine], IsEngine]],
    registry: Optional[IsRunStateRegistry],
):
    if engine_decorator:
        engine = engine_decorator(engine)

    if job_type.value == JobType.task.value:
        engine = cast(IsTaskRunnerEngine, engine)
        job_case.job = convert_func_to_task(
            job_case.name,
            job_case.job_func,
            job_template_cls,
            engine,
            registry,
        )

    return job_case


async def run_job_test(job_case: JobCase):
    result = job_case.run_and_assert_results_func(job_case.job)
    if result and isawaitable(result):
        await result
