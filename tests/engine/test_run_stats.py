from typing import Annotated

import pytest

from unifair.engine.protocols import TaskProtocol
from unifair.engine.stats import RunStats, State


def test_task_state_transitions(task_a: Annotated[TaskProtocol, pytest.fixture],
                                task_b: Annotated[TaskProtocol, pytest.fixture]):
    run_stats = RunStats()

    run_stats.set_task_state(task_a, State.INITIALIZED)
    assert run_stats.get_task_state(task_a) == State.INITIALIZED
    assert run_stats.all_tasks() == (task_a,)
    assert run_stats.all_tasks(State.INITIALIZED) == (task_a,)
    assert run_stats.all_tasks(State.RUNNING) == ()
    assert run_stats.all_tasks(State.FINISHED) == ()

    run_stats.set_task_state(task_a, State.RUNNING)
    assert run_stats.get_task_state(task_a) == State.RUNNING
    assert run_stats.all_tasks() == (task_a,)
    assert run_stats.all_tasks(State.INITIALIZED) == ()
    assert run_stats.all_tasks(State.RUNNING) == (task_a,)
    assert run_stats.all_tasks(State.FINISHED) == ()

    run_stats.set_task_state(task_b, State.INITIALIZED)
    assert run_stats.get_task_state(task_b) == State.INITIALIZED
    assert run_stats.all_tasks() == (task_a, task_b)
    assert run_stats.all_tasks(State.INITIALIZED) == (task_b,)
    assert run_stats.all_tasks(State.RUNNING) == (task_a,)
    assert run_stats.all_tasks(State.FINISHED) == ()

    run_stats.set_task_state(task_b, State.RUNNING)
    assert run_stats.get_task_state(task_b) == State.RUNNING
    assert run_stats.all_tasks() == (task_a, task_b)
    assert run_stats.all_tasks(State.INITIALIZED) == ()
    assert run_stats.all_tasks(State.RUNNING) == (task_a, task_b)
    assert run_stats.all_tasks(State.FINISHED) == ()

    run_stats.set_task_state(task_b, State.FINISHED)
    assert run_stats.get_task_state(task_b) == State.FINISHED
    assert run_stats.all_tasks() == (task_a, task_b)
    assert run_stats.all_tasks(State.INITIALIZED) == ()
    assert run_stats.all_tasks(State.RUNNING) == (task_a,)
    assert run_stats.all_tasks(State.FINISHED) == (task_b,)

    run_stats.set_task_state(task_a, State.FINISHED)
    assert run_stats.get_task_state(task_b) == State.FINISHED
    assert run_stats.all_tasks() == (task_a, task_b)
    assert run_stats.all_tasks(State.INITIALIZED) == ()
    assert run_stats.all_tasks(State.RUNNING) == ()
    assert run_stats.all_tasks(State.FINISHED) == (task_b, task_a)


def test_fail_task_state_transitions(task_a: Annotated[TaskProtocol, pytest.fixture],
                                     task_b: Annotated[TaskProtocol, pytest.fixture]):
    run_stats = RunStats()

    with pytest.raises(ValueError):
        run_stats.set_task_state(task_a, State.FINISHED)

    with pytest.raises(ValueError):
        run_stats.set_task_state(task_a, State.RUNNING)

    run_stats.set_task_state(task_a, State.INITIALIZED)

    with pytest.raises(ValueError):
        run_stats.set_task_state(task_a, State.INITIALIZED)

    with pytest.raises(ValueError):
        run_stats.set_task_state(task_a, State.FINISHED)

    run_stats.set_task_state(task_a, State.RUNNING)

    with pytest.raises(ValueError):
        run_stats.set_task_state(task_a, State.INITIALIZED)

    with pytest.raises(ValueError):
        run_stats.set_task_state(task_a, State.RUNNING)

    run_stats.set_task_state(task_a, State.FINISHED)

    with pytest.raises(ValueError):
        run_stats.set_task_state(task_a, State.INITIALIZED)

    with pytest.raises(ValueError):
        run_stats.set_task_state(task_a, State.RUNNING)

    with pytest.raises(ValueError):
        run_stats.set_task_state(task_a, State.FINISHED)


def test_fail_task_same_name_different_task(task_a: Annotated[TaskProtocol, pytest.fixture],
                                            task_b: Annotated[TaskProtocol, pytest.fixture]):
    task_b.name = task_a.name

    run_stats = RunStats()
    run_stats.set_task_state(task_a, State.INITIALIZED)

    with pytest.raises(ValueError):
        run_stats.set_task_state(task_b, State.INITIALIZED)

    with pytest.raises(ValueError):
        run_stats.set_task_state(task_b, State.RUNNING)
