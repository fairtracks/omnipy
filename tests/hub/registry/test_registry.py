from copy import copy
from datetime import datetime, timedelta
from io import StringIO
from time import sleep
from typing import Annotated

import pytest

from omnipy.hub._registry import RunStateRegistry
from omnipy.shared.enums.job import RunState
from omnipy.shared.protocols.compute.job import IsDagFlow, IsTask
from omnipy.shared.protocols.hub.runtime import IsRuntime

from ...engine.helpers.mocks import (MockDagFlow,
                                     MockDagFlowTemplate,
                                     MockJobRunnerSubclass,
                                     MockTask,
                                     MockTaskTemplate)
from ..helpers.functions import read_log_lines_from_stream


@pytest.fixture(scope='module')
def task_template_a() -> MockTaskTemplate:
    MockTaskTemplate.job_creator.engine = MockJobRunnerSubclass()

    @MockTaskTemplate(name='a')
    def concat_a(s: str) -> str:
        return s + 'a'

    return concat_a


@pytest.fixture(scope='module')
def task_template_b() -> MockTaskTemplate:
    MockTaskTemplate.job_creator.engine = MockJobRunnerSubclass()

    @MockTaskTemplate(name='b')
    def concat_b(s: str) -> str:
        return s + 'b'

    return concat_b


@pytest.fixture(scope='module')
def task_a(task_template_a) -> MockTask:
    return task_template_a.apply()


@pytest.fixture(scope='module')
def task_b(task_template_b) -> MockTask:
    return task_template_b.apply()


@pytest.fixture(scope='module')
def dag_flow_a(task_template_a, task_template_b) -> MockDagFlow:
    @MockDagFlowTemplate(task_template_a, task_template_b, name='a')
    def concat_a(s: str) -> str:
        ...

    return concat_a.apply()


@pytest.fixture(scope='module')
def dag_flow_b(task_template_a, task_template_b) -> MockDagFlow:
    @MockDagFlowTemplate(task_template_a, task_template_b, name='b')
    def concat_b(s: str) -> str:
        ...

    return concat_b.apply()


def test_job_state_transitions(
    task_a: Annotated[IsTask, pytest.fixture],
    task_b: Annotated[IsTask, pytest.fixture],
    dag_flow_a: Annotated[IsDagFlow, pytest.fixture],
    dag_flow_b: Annotated[IsDagFlow, pytest.fixture],
):
    for job_a, job_b in [(task_a, task_b), (dag_flow_a, dag_flow_b)]:
        registry = RunStateRegistry()

        registry.set_job_state(job_a, RunState.INITIALIZED)
        assert registry.get_job_state(job_a) == RunState.INITIALIZED
        assert registry.all_jobs() == (job_a,)
        assert registry.all_jobs(RunState.INITIALIZED) == (job_a,)
        assert registry.all_jobs(RunState.RUNNING) == ()
        assert registry.all_jobs(RunState.FINISHED) == ()

        registry.set_job_state(job_a, RunState.RUNNING)
        assert registry.get_job_state(job_a) == RunState.RUNNING
        assert registry.all_jobs() == (job_a,)
        assert registry.all_jobs(RunState.INITIALIZED) == ()
        assert registry.all_jobs(RunState.RUNNING) == (job_a,)
        assert registry.all_jobs(RunState.FINISHED) == ()

        registry.set_job_state(job_b, RunState.INITIALIZED)
        assert registry.get_job_state(job_b) == RunState.INITIALIZED
        assert registry.all_jobs() == (job_a, job_b)
        assert registry.all_jobs(RunState.INITIALIZED) == (job_b,)
        assert registry.all_jobs(RunState.RUNNING) == (job_a,)
        assert registry.all_jobs(RunState.FINISHED) == ()

        registry.set_job_state(job_b, RunState.RUNNING)
        assert registry.get_job_state(job_b) == RunState.RUNNING
        assert registry.all_jobs() == (job_a, job_b)
        assert registry.all_jobs(RunState.INITIALIZED) == ()
        assert registry.all_jobs(RunState.RUNNING) == (job_a, job_b)
        assert registry.all_jobs(RunState.FINISHED) == ()

        registry.set_job_state(job_b, RunState.FINISHED)
        assert registry.get_job_state(job_b) == RunState.FINISHED
        assert registry.all_jobs() == (job_a, job_b)
        assert registry.all_jobs(RunState.INITIALIZED) == ()
        assert registry.all_jobs(RunState.RUNNING) == (job_a,)
        assert registry.all_jobs(RunState.FINISHED) == (job_b,)

        registry.set_job_state(job_a, RunState.FINISHED)
        assert registry.get_job_state(job_b) == RunState.FINISHED
        assert registry.all_jobs() == (job_a, job_b)
        assert registry.all_jobs(RunState.INITIALIZED) == ()
        assert registry.all_jobs(RunState.RUNNING) == ()
        assert registry.all_jobs(RunState.FINISHED) == (job_b, job_a)


def test_fail_job_state_transitions(
    task_a: Annotated[IsTask, pytest.fixture],
    dag_flow_a: Annotated[IsDagFlow, pytest.fixture],
):
    for job_a in [task_a, dag_flow_a]:
        registry = RunStateRegistry()

        with pytest.raises(ValueError):
            registry.set_job_state(job_a, RunState.FINISHED)

        with pytest.raises(ValueError):
            registry.set_job_state(job_a, RunState.RUNNING)

        registry.set_job_state(job_a, RunState.INITIALIZED)

        with pytest.raises(ValueError):
            registry.set_job_state(job_a, RunState.INITIALIZED)

        with pytest.raises(ValueError):
            registry.set_job_state(job_a, RunState.FINISHED)

        registry.set_job_state(job_a, RunState.RUNNING)

        with pytest.raises(ValueError):
            registry.set_job_state(job_a, RunState.INITIALIZED)

        with pytest.raises(ValueError):
            registry.set_job_state(job_a, RunState.RUNNING)

        registry.set_job_state(job_a, RunState.FINISHED)

        with pytest.raises(ValueError):
            registry.set_job_state(job_a, RunState.INITIALIZED)

        with pytest.raises(ValueError):
            registry.set_job_state(job_a, RunState.RUNNING)

        with pytest.raises(ValueError):
            registry.set_job_state(job_a, RunState.FINISHED)


def test_datetime_of_state_change_event(
    task_a: Annotated[IsTask, pytest.fixture],
    dag_flow_a: Annotated[IsDagFlow, pytest.fixture],
):
    for job_a in [task_a, dag_flow_a]:
        registry = RunStateRegistry()
        cur_time = datetime.now()

        sleep(0.001)
        registry.set_job_state(job_a, RunState.INITIALIZED)
        init_time = registry.get_job_state_datetime(job_a, RunState.INITIALIZED)
        assert timedelta() < init_time - cur_time < timedelta(seconds=1)

        sleep(0.001)
        registry.set_job_state(job_a, RunState.RUNNING)
        assert registry.get_job_state_datetime(job_a, RunState.INITIALIZED) == init_time
        run_time = registry.get_job_state_datetime(job_a, RunState.RUNNING)
        assert timedelta() < run_time - init_time < timedelta(seconds=1)

        sleep(0.001)
        registry.set_job_state(job_a, RunState.FINISHED)
        assert registry.get_job_state_datetime(job_a, RunState.INITIALIZED) == init_time
        assert registry.get_job_state_datetime(job_a, RunState.RUNNING) == run_time
        finish_time = registry.get_job_state_datetime(job_a, RunState.FINISHED)
        assert timedelta() < finish_time - run_time < timedelta(seconds=1)

        assert cur_time < init_time < run_time < finish_time


def test_fail_job_key_error(
    task_a: Annotated[IsTask, pytest.fixture],
    task_b: Annotated[IsTask, pytest.fixture],
    dag_flow_a: Annotated[IsDagFlow, pytest.fixture],
    dag_flow_b: Annotated[IsDagFlow, pytest.fixture],
):
    for job_a, job_b in [(task_a, task_b), (dag_flow_a, dag_flow_b)]:
        registry = RunStateRegistry()

        with pytest.raises(KeyError):
            registry.get_job_state(job_a)

        with pytest.raises(KeyError):
            registry.get_job_state_datetime(job_a, RunState.INITIALIZED)

        registry.set_job_state(job_a, RunState.INITIALIZED)
        registry.get_job_state(job_a)
        registry.get_job_state_datetime(job_a, RunState.INITIALIZED)

        with pytest.raises(KeyError):
            registry.get_job_state(job_b)

        with pytest.raises(KeyError):
            registry.get_job_state_datetime(job_a, RunState.RUNNING)

        with pytest.raises(KeyError):
            registry.get_job_state_datetime(job_b, RunState.INITIALIZED)


def test_same_unique_name_different_job(
    task_a: Annotated[IsTask, pytest.fixture],
    task_b: Annotated[IsTask, pytest.fixture],
    dag_flow_a: Annotated[IsDagFlow, pytest.fixture],
    dag_flow_b: Annotated[IsDagFlow, pytest.fixture],
):
    for job_a, job_b in [(task_a, task_b), (dag_flow_a, dag_flow_b)]:
        job_b = copy(job_b)
        job_b.name = job_a.name
        job_b.unique_name = job_a.unique_name

        registry = RunStateRegistry()
        registry.set_job_state(job_a, RunState.INITIALIZED)
        registry.set_job_state(job_b, RunState.INITIALIZED)

        assert job_b.name == job_a.name
        assert job_b.unique_name != job_a.unique_name

        prev_unique_name = job_b.unique_name
        registry.set_job_state(job_b, RunState.RUNNING)
        assert job_b.name == job_a.name
        assert job_b.unique_name == prev_unique_name


def test_state_change_logging(
    runtime: Annotated[IsRuntime, pytest.fixture],
    task_a: Annotated[IsTask, pytest.fixture],
    task_b: Annotated[IsTask, pytest.fixture],
    dag_flow_a: Annotated[IsDagFlow, pytest.fixture],
    dag_flow_b: Annotated[IsDagFlow, pytest.fixture],
):
    my_stdout = StringIO()
    runtime.config.root_log.stdout = my_stdout

    for job_a, job_b in [(task_a, task_b), (dag_flow_a, dag_flow_b)]:
        registry = RunStateRegistry()

        events = [
            (job_a, RunState.INITIALIZED),
            (job_a, RunState.RUNNING),
            (job_b, RunState.INITIALIZED),
            (job_a, RunState.FINISHED),
            (job_b, RunState.RUNNING),
            (job_b, RunState.FINISHED),
        ]

        for job, state in events:
            registry.set_job_state(job, state)

        log_lines = read_log_lines_from_stream(my_stdout)

        assert len(log_lines) == 6

        assert log_lines[0].endswith('INFO: '
                                     f'Initialized "{job_a.unique_name}" '
                                     f'(omnipy.hub._registry.RunStateRegistry)')
        assert log_lines[1].endswith(f'INFO: '
                                     f'Started running "{job_a.unique_name}"... '
                                     f'(omnipy.hub._registry.RunStateRegistry)')
        assert log_lines[2].endswith(f'INFO: '
                                     f'Initialized "{job_b.unique_name}" '
                                     f'(omnipy.hub._registry.RunStateRegistry)')
        assert log_lines[3].endswith(f'INFO: '
                                     f'Finished running "{job_a.unique_name}"! '
                                     f'(omnipy.hub._registry.RunStateRegistry)')
        assert log_lines[4].endswith(f'INFO: '
                                     f'Started running "{job_b.unique_name}"... '
                                     f'(omnipy.hub._registry.RunStateRegistry)')
        assert log_lines[5].endswith(f'INFO: '
                                     f'Finished running "{job_b.unique_name}"! '
                                     f'(omnipy.hub._registry.RunStateRegistry)')
