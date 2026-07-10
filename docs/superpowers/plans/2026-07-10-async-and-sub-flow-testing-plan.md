# Async And Sub-Flow Testing Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add engine-first async and nested-flow test coverage with a complete per-production-engine 3×4 parent-flow/callable matrix, child-flow semantic-floor coverage, a child-flow refine/revise slice, and only a narrow production seam if red tests prove one is needed.

**Architecture:** Keep `tests/engine/` as the main authority, but build the new parity cases with the real `TaskTemplate` / `LinearFlowTemplate` / `DagFlowTemplate` / `FuncFlowTemplate` classes under `LocalRunner` and `PrefectEngine`, because mock flow templates do not model nested child-flow composition, `param_key_map`, or `result_key` behavior. Replace the thin `ComposedFlowCase` metadata idea with a concrete `build_job_func` closure per case so each case owns its exact child topology, routing, and refine/revise behavior while the helper layer only injects the engine, registry, and applied job.

**Tech Stack:** Python, pytest, pytest-cases, asyncio, Omnipy task/flow templates, LocalRunner, PrefectEngine

---

## File map

- Create: `tests/engine/cases/flows.py`
  - Real-engine composed-flow cases, assertion helpers, and builder closures for matrix + semantic-floor coverage.
- Modify: `tests/engine/cases/tasks.py`
  - Keep this file as the main source of primitive callable behavior by adding only the new single-thread primitives reused by `flows.py`.
- Modify: `tests/engine/helpers/classes.py`
  - Add `ComposedFlowCase` with a concrete `build_job_func` closure instead of thin topology metadata.
- Modify: `tests/engine/helpers/functions.py`
  - Add `apply_composed_flow_case()` and widen `run_job_test()` to accept `JobCase | ComposedFlowCase`.
- Modify: `tests/engine/conftest.py`
  - Add production-engine fixtures for matrix cases and semantic-floor cases that use real template classes.
- Modify: `tests/engine/test_all_engines.py`
  - Add two thin async parametrized tests that consume the new fixtures.
- Modify only if red tests require it: `tests/compute/test_flow.py`
  - Validation-only callable-type checks for child-flow composition changes during construction, `refine()`, and `revise()`.
- Modify only if red tests require it: `src/omnipy/compute/_joblist_job.py`
  - Narrow callable-type consistency seam for child-job-list flows.
- Modify only if red tests require it: `src/omnipy/engine/run_spec.py`
  - Narrow async-resolution seam if nested async child flows are intended to work but are not drained consistently.
- Create: `tests/integration/reused/compute/test_async_and_subflows_with_all_engines.py`
  - Three end-to-end confirmations: nested async child flow, parent/child parameter routing, and child-flow refine/revise replacement.

## Coverage ledger

- Exhaustive per production engine: `LinearFlow`, `DagFlow`, `FuncFlow` × sync function / sync generator / async coroutine / async generator → **Tasks 2–4**
- Linear and DAG parents with multiple children across the matrix → **Tasks 2–3**
- Child flows of each existing flow type under linear and DAG parents at least once overall → **Tasks 5–6**
- Parent `FuncFlow` bodies that call tasks and separate parent `FuncFlow` bodies that call flows → **Tasks 4 and 7**
- Mixed sync/async composition with async terminal child → **Task 7**
- Nested async support-gap case with explicit expectation handling → **Task 7**
- Nested parameter routing across a parent/child flow boundary → **Tasks 6 and 9**
- Targeted refine/revise case involving child-flow replacement inside a DAG parent → **Tasks 6, 8, and 9**
- Optional compute validation only if red tests prove a seam is needed → **Task 8**
- Selective integration confirmations only → **Task 9**

## Support-gap policy for implementation

- Known external engine limitations use engine-specific `pytest.xfail(strict=True)` with a one-line reason.
- Claimed-supported behavior that stays red after investigation uses one narrow committed failing case or `xfail(strict=True)`, chosen deliberately per case.
- Temporary local TDD-red is fine during a slice, but every retained gap must be classified before the slice is handed off.

## User Check-in markers

- **User Check-in A:** If Task 7 or Task 8 points to a production seam, stop before editing `src/omnipy/compute/_joblist_job.py` or `src/omnipy/engine/run_spec.py` and confirm the exact seam.
- **User Check-in B:** If any failing case needs a broader behavior change than callable-type lifting or nested-result draining, pause and open a follow-up design/planning step.

### Task 1: Replace thin flow metadata with a real-template composed-case pipeline

**Files:**
- Create: `tests/engine/cases/flows.py`
- Modify: `tests/engine/helpers/classes.py`
- Modify: `tests/engine/helpers/functions.py`
- Modify: `tests/engine/conftest.py`
- Modify: `tests/engine/test_all_engines.py`
- Test: `tests/engine/test_all_engines.py`

- [ ] **Step 1: Write the failing thin engine tests**

```python
@pc.parametrize(
    'job_case',
    [pc.fixture_ref('all_flow_matrix_cases_all_engines_assert_runstate_mock_reg')],
    ids=[''],
)
@pytest.mark.asyncio
async def test_flow_matrix_all_production_engines(job_case: JobCase | ComposedFlowCase) -> None:
    await run_job_test(job_case)


@pc.parametrize(
    'job_case',
    [pc.fixture_ref('nested_flow_semantic_floor_cases_all_engines_assert_runstate_mock_reg')],
    ids=[''],
)
@pytest.mark.asyncio
async def test_nested_flow_semantic_floor_all_production_engines(
    job_case: JobCase | ComposedFlowCase,
) -> None:
    await run_job_test(job_case)
```

- [ ] **Step 2: Run the engine file and confirm missing-fixture red**

Run: `uv run pytest tests/engine/test_all_engines.py -v --mypy-pyproject-toml-file=pyproject.toml`

Expected: collection fails because the two new fixture names and `ComposedFlowCase` do not exist yet.

- [ ] **Step 3: Add the concrete case carrier**

```python
from dataclasses import dataclass, field
from typing import Awaitable, Callable, Generic, ParamSpec, TypeVar

from omnipy.shared.enums.job import JobType
from omnipy.shared.protocols.compute.job import IsJob
from omnipy.shared.protocols.engine.base import IsEngine
from omnipy.shared.protocols.hub.registry import IsRunStateRegistry
from omnipy.util.callable_types import CallableType

CallP = ParamSpec('CallP')
ReturnT = TypeVar('ReturnT')


@dataclass
class ComposedFlowCase(Generic[CallP, ReturnT]):
    name: str
    build_job_func: Callable[[IsEngine, IsRunStateRegistry | None], IsJob]
    run_and_assert_results_func: Callable[[IsJob], None | Awaitable[None]]
    parent_job_type: JobType.Literals
    expected_callable_type: CallableType.Literals
    call_args: tuple[object, ...] = ()
    call_kwargs: dict[str, object] = field(default_factory=dict)
    job: IsJob | None = None
```

- [ ] **Step 4: Add the composed-case apply helper**

```python
from typing import Callable, cast

from omnipy.compute.flow import DagFlowTemplate, FuncFlowTemplate, LinearFlowTemplate
from omnipy.compute.task import TaskTemplate
from omnipy.shared.protocols.compute.job import HasJobCreator, IsJob
from omnipy.shared.protocols.engine.base import IsEngine
from omnipy.shared.protocols.hub.registry import IsRunStateRegistry
from omnipy.util.helpers import resolve

from .classes import ComposedFlowCase, JobCase


def apply_composed_flow_case(
    job_case: ComposedFlowCase,
    engine: IsEngine,
    engine_decorator: Callable[[IsEngine], IsEngine] | None,
    registry: IsRunStateRegistry | None,
) -> ComposedFlowCase:
    if engine_decorator:
        engine = engine_decorator(engine)
    if registry:
        engine.set_registry(registry)

    cast(HasJobCreator, TaskTemplate).job_creator.set_engine(engine)
    cast(HasJobCreator, LinearFlowTemplate).job_creator.set_engine(engine)
    cast(HasJobCreator, DagFlowTemplate).job_creator.set_engine(engine)
    cast(HasJobCreator, FuncFlowTemplate).job_creator.set_engine(engine)

    job_case.job = job_case.build_job_func(engine, registry)
    return job_case


async def run_job_test(job_case: JobCase | ComposedFlowCase) -> None:
    assert job_case.job is not None
    await resolve(job_case.run_and_assert_results_func(job_case.job))
```

- [ ] **Step 5: Add the matrix fixture family**

```python
@pc.fixture(scope='function')
@pc.parametrize_with_cases('job_case', cases='.cases.flows', has_tag='matrix')
@pc.parametrize('engine', [all_engines], ids=[''])
@pc.parametrize('engine_decorator', [assert_runstate_engine_decorator])
@pc.parametrize('registry', [mock_registry], ids=[''])
def all_flow_matrix_cases_all_engines_assert_runstate_mock_reg(
    job_case: ComposedFlowCase,
    engine: IsEngine,
    engine_decorator: Callable[[IsEngine], IsEngine] | None,
    registry: IsRunStateRegistry | None,
):
    return apply_composed_flow_case(job_case, engine, engine_decorator, registry)
```

- [ ] **Step 6: Add the semantic-floor fixture family**

```python
@pc.fixture(scope='function')
@pc.parametrize_with_cases('job_case', cases='.cases.flows', has_tag='semantic-floor')
@pc.parametrize('engine', [all_engines], ids=[''])
@pc.parametrize('engine_decorator', [assert_runstate_engine_decorator])
@pc.parametrize('registry', [mock_registry], ids=[''])
def nested_flow_semantic_floor_cases_all_engines_assert_runstate_mock_reg(
    job_case: ComposedFlowCase,
    engine: IsEngine,
    engine_decorator: Callable[[IsEngine], IsEngine] | None,
    registry: IsRunStateRegistry | None,
):
    return apply_composed_flow_case(job_case, engine, engine_decorator, registry)
```

- [ ] **Step 7: Re-run the engine file and require only missing-case red**

Run: `uv run pytest tests/engine/test_all_engines.py -v --mypy-pyproject-toml-file=pyproject.toml`

Expected: tests collect; failures point to missing case definitions in `tests/engine/cases/flows.py`.

- [ ] **Step 8: Commit the scaffolding slice**

```bash
git add tests/engine/cases/flows.py tests/engine/helpers/classes.py tests/engine/helpers/functions.py tests/engine/conftest.py tests/engine/test_all_engines.py
git commit -m "test: scaffold real-engine async subflow cases"
```

### Task 2: Add the four linear-parent matrix cases

**Files:**
- Modify: `tests/engine/cases/tasks.py`
- Modify: `tests/engine/cases/flows.py`
- Test: `tests/engine/test_all_engines.py`

- [ ] **Step 1: Add the shared primitive callables to `tests/engine/cases/tasks.py`**

```python
def sync_identity(number: int) -> int:
    return number


def sync_increment(number: int) -> int:
    return number + 1


def sync_double(number: int) -> int:
    return number * 2


def sync_square(number: int) -> int:
    return number * number


async def async_double(number: int) -> int:
    return number * 2


def sync_number_range(number: int):
    yield from range(number + 1)


async def async_number_range(number: int):
    for value in range(number + 1):
        await asyncio.sleep(0)
        yield value


def sync_seed_with_plus(number: int) -> dict[str, int]:
    return {'number': number, 'plus': 2}


def sync_add(number: int, plus: int) -> int:
    return number + plus
```

- [ ] **Step 2: Add the assertion helpers**

```python
def _assert_sync_result(
    expected_callable_type: CallableType.Literals,
    args: tuple[object, ...],
    expected_result: object,
) -> Callable[[IsJob], None]:
    def _run(job: IsJob) -> None:
        assert job.callable_type is expected_callable_type
        assert job(*args) == expected_result
        assert_job_state(job, [RunState.FINISHED])

    return _run


def _assert_async_result(
    expected_callable_type: CallableType.Literals,
    args: tuple[object, ...],
    expected_result: object,
) -> Callable[[IsJob], Awaitable[None]]:
    async def _run(job: IsJob) -> None:
        assert job.callable_type is expected_callable_type
        assert await resolve(job(*args)) == expected_result
        assert_job_state(job, [RunState.FINISHED])

    return _run


def _assert_sync_generator(
    expected_callable_type: CallableType.Literals,
    args: tuple[object, ...],
    expected_result: list[object],
) -> Callable[[IsJob], None]:
    def _run(job: IsJob) -> None:
        assert job.callable_type is expected_callable_type
        assert list(job(*args)) == expected_result
        assert_job_state(job, [RunState.RUNNING, RunState.FINISHED])

    return _run


def _assert_async_generator(
    expected_callable_type: CallableType.Literals,
    args: tuple[object, ...],
    expected_result: list[object],
) -> Callable[[IsJob], Awaitable[None]]:
    async def _run(job: IsJob) -> None:
        assert job.callable_type is expected_callable_type
        assert [item async for item in job(*args)] == expected_result
        assert_job_state(job, [RunState.RUNNING, RunState.FINISHED])

    return _run
```

- [ ] **Step 3: Add the linear parent builder**

```python
def _build_linear_parent(
    name: str,
    terminal_child: IsFuncArgJobTemplate,
) -> IsLinearFlow:
    start_tmpl = TaskTemplate(name=f'{name}_start')(sync_increment)

    @LinearFlowTemplate(start_tmpl, terminal_child, name=name)
    def linear_parent(number: int):
        ...

    return linear_parent.apply()
```

- [ ] **Step 4: Add `case_linear_flow_sync_function_terminal_child`**

```python
@pc.case(id='linear-flow-sync-function-terminal-child', tags=['matrix', 'linearflow'])
def case_linear_flow_sync_function_terminal_child() -> ComposedFlowCase[[int], int]:
    def build_job_func(engine: IsEngine, registry: IsRunStateRegistry | None) -> IsJob:
        terminal_tmpl = TaskTemplate(name='linear_sync_terminal')(sync_double)
        return _build_linear_parent('linear_flow_sync_function_terminal_child', terminal_tmpl)

    return ComposedFlowCase(
        name='linear_flow_sync_function_terminal_child',
        build_job_func=build_job_func,
        run_and_assert_results_func=_assert_sync_result(CallableType.SYNC_FUNCTION, (4,), 10),
        parent_job_type=JobType.LINEAR_FLOW,
        expected_callable_type=CallableType.SYNC_FUNCTION,
        call_args=(4,),
    )
```

- [ ] **Step 5: Run the sync-function linear case**

Run: `uv run pytest tests/engine/test_all_engines.py -k "linear-flow-sync-function-terminal-child" -v --mypy-pyproject-toml-file=pyproject.toml`

Expected: the sync-function linear case runs across both production engines.

- [ ] **Step 6: Add `case_linear_flow_sync_generator_terminal_child`**

```python
@pc.case(id='linear-flow-sync-generator-terminal-child', tags=['matrix', 'linearflow'])
def case_linear_flow_sync_generator_terminal_child() -> ComposedFlowCase[[int], Generator]:
    def build_job_func(engine: IsEngine, registry: IsRunStateRegistry | None) -> IsJob:
        terminal_tmpl = TaskTemplate(name='linear_sync_generator_terminal')(sync_number_range)
        return _build_linear_parent('linear_flow_sync_generator_terminal_child', terminal_tmpl)

    return ComposedFlowCase(
        name='linear_flow_sync_generator_terminal_child',
        build_job_func=build_job_func,
        run_and_assert_results_func=_assert_sync_generator(
            CallableType.SYNC_GENERATOR,
            (4,),
            [0, 1, 2, 3, 4],
        ),
        parent_job_type=JobType.LINEAR_FLOW,
        expected_callable_type=CallableType.SYNC_GENERATOR,
        call_args=(4,),
    )
```

- [ ] **Step 7: Run the sync-generator linear case**

Run: `uv run pytest tests/engine/test_all_engines.py -k "linear-flow-sync-generator-terminal-child" -v --mypy-pyproject-toml-file=pyproject.toml`

Expected: the sync-generator linear case runs across both production engines.

- [ ] **Step 8: Add `case_linear_flow_async_coroutine_terminal_child`**

```python
@pc.case(id='linear-flow-async-coroutine-terminal-child', tags=['matrix', 'linearflow'])
def case_linear_flow_async_coroutine_terminal_child() -> ComposedFlowCase[[int], Awaitable[int]]:
    def build_job_func(engine: IsEngine, registry: IsRunStateRegistry | None) -> IsJob:
        terminal_tmpl = TaskTemplate(name='linear_async_terminal')(async_double)
        return _build_linear_parent('linear_flow_async_coroutine_terminal_child', terminal_tmpl)

    return ComposedFlowCase(
        name='linear_flow_async_coroutine_terminal_child',
        build_job_func=build_job_func,
        run_and_assert_results_func=_assert_async_result(CallableType.ASYNC_COROUTINE, (4,), 10),
        parent_job_type=JobType.LINEAR_FLOW,
        expected_callable_type=CallableType.ASYNC_COROUTINE,
        call_args=(4,),
    )
```

- [ ] **Step 9: Run the async-coroutine linear case**

Run: `uv run pytest tests/engine/test_all_engines.py -k "linear-flow-async-coroutine-terminal-child" -v --mypy-pyproject-toml-file=pyproject.toml`

Expected: the async-coroutine linear case runs across both production engines.

- [ ] **Step 10: Add `case_linear_flow_async_generator_terminal_child`**

```python
@pc.case(id='linear-flow-async-generator-terminal-child', tags=['matrix', 'linearflow'])
def case_linear_flow_async_generator_terminal_child() -> ComposedFlowCase[[int], AsyncGenerator]:
    def build_job_func(engine: IsEngine, registry: IsRunStateRegistry | None) -> IsJob:
        terminal_tmpl = TaskTemplate(name='linear_async_generator_terminal')(async_number_range)
        return _build_linear_parent('linear_flow_async_generator_terminal_child', terminal_tmpl)

    return ComposedFlowCase(
        name='linear_flow_async_generator_terminal_child',
        build_job_func=build_job_func,
        run_and_assert_results_func=_assert_async_generator(
            CallableType.ASYNC_GENERATOR,
            (4,),
            [0, 1, 2, 3, 4],
        ),
        parent_job_type=JobType.LINEAR_FLOW,
        expected_callable_type=CallableType.ASYNC_GENERATOR,
        call_args=(4,),
    )
```

- [ ] **Step 11: Run the async-generator linear case**

Run: `uv run pytest tests/engine/test_all_engines.py -k "linear-flow-async-generator-terminal-child" -v --mypy-pyproject-toml-file=pyproject.toml`

Expected: the async-generator linear case runs across both production engines.

- [ ] **Step 12: Re-run the full linear slice**

Run: `uv run pytest tests/engine/test_all_engines.py -k "linear-flow" -v --mypy-pyproject-toml-file=pyproject.toml`

Expected: all four linear matrix cases execute across `LocalRunner` and `PrefectEngine`; remaining red comes from missing DAG and `FuncFlow` matrix cases.

- [ ] **Step 13: Commit the linear slice**

```bash
git add tests/engine/cases/tasks.py tests/engine/cases/flows.py
git commit -m "test: add linear flow callable matrix"
```

### Task 3: Add the four DAG-parent matrix cases

**Files:**
- Modify: `tests/engine/cases/flows.py`
- Test: `tests/engine/test_all_engines.py`

- [ ] **Step 1: Add the DAG parent builder**

```python
def _build_dag_parent(
    name: str,
    terminal_child: IsFuncArgJobTemplate,
) -> IsDagFlow:
    seed_tmpl = TaskTemplate(name=f'{name}_seed')(sync_identity).refine(result_key='number')

    @DagFlowTemplate(seed_tmpl, terminal_child, name=name)
    def dag_parent(number: int):
        ...

    return dag_parent.apply()
```

- [ ] **Step 2: Add `case_dag_flow_sync_function_terminal_child`**

```python
@pc.case(id='dag-flow-sync-function-terminal-child', tags=['matrix', 'dagflow'])
def case_dag_flow_sync_function_terminal_child() -> ComposedFlowCase[[int], int]:
    def build_job_func(engine: IsEngine, registry: IsRunStateRegistry | None) -> IsJob:
        terminal_tmpl = TaskTemplate(name='dag_sync_terminal')(sync_double)
        return _build_dag_parent('dag_flow_sync_function_terminal_child', terminal_tmpl)

    return ComposedFlowCase(
        name='dag_flow_sync_function_terminal_child',
        build_job_func=build_job_func,
        run_and_assert_results_func=_assert_sync_result(CallableType.SYNC_FUNCTION, (4,), 8),
        parent_job_type=JobType.DAG_FLOW,
        expected_callable_type=CallableType.SYNC_FUNCTION,
        call_args=(4,),
    )
```

- [ ] **Step 3: Run the sync-function DAG case**

Run: `uv run pytest tests/engine/test_all_engines.py -k "dag-flow-sync-function-terminal-child" -v --mypy-pyproject-toml-file=pyproject.toml`

Expected: the sync-function DAG case runs across both production engines.

- [ ] **Step 4: Add `case_dag_flow_sync_generator_terminal_child`**

```python
@pc.case(id='dag-flow-sync-generator-terminal-child', tags=['matrix', 'dagflow'])
def case_dag_flow_sync_generator_terminal_child() -> ComposedFlowCase[[int], Generator]:
    def build_job_func(engine: IsEngine, registry: IsRunStateRegistry | None) -> IsJob:
        terminal_tmpl = TaskTemplate(name='dag_sync_generator_terminal')(sync_number_range)
        return _build_dag_parent('dag_flow_sync_generator_terminal_child', terminal_tmpl)

    return ComposedFlowCase(
        name='dag_flow_sync_generator_terminal_child',
        build_job_func=build_job_func,
        run_and_assert_results_func=_assert_sync_generator(
            CallableType.SYNC_GENERATOR,
            (4,),
            [0, 1, 2, 3, 4],
        ),
        parent_job_type=JobType.DAG_FLOW,
        expected_callable_type=CallableType.SYNC_GENERATOR,
        call_args=(4,),
    )
```

- [ ] **Step 5: Run the sync-generator DAG case**

Run: `uv run pytest tests/engine/test_all_engines.py -k "dag-flow-sync-generator-terminal-child" -v --mypy-pyproject-toml-file=pyproject.toml`

Expected: the sync-generator DAG case runs across both production engines.

- [ ] **Step 6: Add `case_dag_flow_async_coroutine_terminal_child`**

```python
@pc.case(id='dag-flow-async-coroutine-terminal-child', tags=['matrix', 'dagflow'])
def case_dag_flow_async_coroutine_terminal_child() -> ComposedFlowCase[[int], Awaitable[int]]:
    def build_job_func(engine: IsEngine, registry: IsRunStateRegistry | None) -> IsJob:
        terminal_tmpl = TaskTemplate(name='dag_async_terminal')(async_double)
        return _build_dag_parent('dag_flow_async_coroutine_terminal_child', terminal_tmpl)

    return ComposedFlowCase(
        name='dag_flow_async_coroutine_terminal_child',
        build_job_func=build_job_func,
        run_and_assert_results_func=_assert_async_result(CallableType.ASYNC_COROUTINE, (4,), 8),
        parent_job_type=JobType.DAG_FLOW,
        expected_callable_type=CallableType.ASYNC_COROUTINE,
        call_args=(4,),
    )
```

- [ ] **Step 7: Run the async-coroutine DAG case**

Run: `uv run pytest tests/engine/test_all_engines.py -k "dag-flow-async-coroutine-terminal-child" -v --mypy-pyproject-toml-file=pyproject.toml`

Expected: the async-coroutine DAG case runs across both production engines.

- [ ] **Step 8: Add `case_dag_flow_async_generator_terminal_child`**

```python
@pc.case(id='dag-flow-async-generator-terminal-child', tags=['matrix', 'dagflow'])
def case_dag_flow_async_generator_terminal_child() -> ComposedFlowCase[[int], AsyncGenerator]:
    def build_job_func(engine: IsEngine, registry: IsRunStateRegistry | None) -> IsJob:
        terminal_tmpl = TaskTemplate(name='dag_async_generator_terminal')(async_number_range)
        return _build_dag_parent('dag_flow_async_generator_terminal_child', terminal_tmpl)

    return ComposedFlowCase(
        name='dag_flow_async_generator_terminal_child',
        build_job_func=build_job_func,
        run_and_assert_results_func=_assert_async_generator(
            CallableType.ASYNC_GENERATOR,
            (4,),
            [0, 1, 2, 3, 4],
        ),
        parent_job_type=JobType.DAG_FLOW,
        expected_callable_type=CallableType.ASYNC_GENERATOR,
        call_args=(4,),
    )
```

- [ ] **Step 9: Run the async-generator DAG case**

Run: `uv run pytest tests/engine/test_all_engines.py -k "dag-flow-async-generator-terminal-child" -v --mypy-pyproject-toml-file=pyproject.toml`

Expected: the async-generator DAG case runs across both production engines.

- [ ] **Step 10: Re-run the full DAG slice**

Run: `uv run pytest tests/engine/test_all_engines.py -k "dag-flow" -v --mypy-pyproject-toml-file=pyproject.toml`

Expected: all four DAG matrix cases execute across both production engines; remaining red comes from missing `FuncFlow` matrix cases.

- [ ] **Step 11: Commit the DAG slice**

```bash
git add tests/engine/cases/flows.py
git commit -m "test: add dag flow callable matrix"
```

### Task 4: Add the four `FuncFlow` matrix cases whose bodies call tasks

**Files:**
- Modify: `tests/engine/cases/flows.py`
- Test: `tests/engine/test_all_engines.py`

- [ ] **Step 1: Add `case_func_flow_sync_function_body_calls_tasks`**

```python
@pc.case(id='func-flow-sync-function-body-calls-tasks', tags=['matrix', 'funcflow'])
def case_func_flow_sync_function_body_calls_tasks() -> ComposedFlowCase[[int], int]:
    def build_job_func(engine: IsEngine, registry: IsRunStateRegistry | None) -> IsJob:
        increment_tmpl = TaskTemplate(name='func_sync_increment')(sync_increment)
        double_tmpl = TaskTemplate(name='func_sync_double')(sync_double)

        @FuncFlowTemplate(name='func_flow_sync_function_body_calls_tasks')
        def func_parent(number: int) -> int:
            return double_tmpl(increment_tmpl(number))

        return func_parent.apply()

    return ComposedFlowCase(
        name='func_flow_sync_function_body_calls_tasks',
        build_job_func=build_job_func,
        run_and_assert_results_func=_assert_sync_result(CallableType.SYNC_FUNCTION, (4,), 10),
        parent_job_type=JobType.FUNC_FLOW,
        expected_callable_type=CallableType.SYNC_FUNCTION,
        call_args=(4,),
    )
```

- [ ] **Step 2: Run the sync-function `FuncFlow` case**

Run: `uv run pytest tests/engine/test_all_engines.py -k "func-flow-sync-function-body-calls-tasks" -v --mypy-pyproject-toml-file=pyproject.toml`

Expected: the sync-function `FuncFlow` case runs across both production engines.

- [ ] **Step 3: Add `case_func_flow_sync_generator_body_calls_tasks`**

```python
@pc.case(id='func-flow-sync-generator-body-calls-tasks', tags=['matrix', 'funcflow'])
def case_func_flow_sync_generator_body_calls_tasks() -> ComposedFlowCase[[int], Generator]:
    def build_job_func(engine: IsEngine, registry: IsRunStateRegistry | None) -> IsJob:
        increment_tmpl = TaskTemplate(name='func_sync_generator_increment')(sync_increment)
        range_tmpl = TaskTemplate(name='func_sync_generator_range')(sync_number_range)

        @FuncFlowTemplate(name='func_flow_sync_generator_body_calls_tasks')
        def func_parent(number: int):
            yield from range_tmpl(increment_tmpl(number))

        return func_parent.apply()

    return ComposedFlowCase(
        name='func_flow_sync_generator_body_calls_tasks',
        build_job_func=build_job_func,
        run_and_assert_results_func=_assert_sync_generator(
            CallableType.SYNC_GENERATOR,
            (4,),
            [0, 1, 2, 3, 4],
        ),
        parent_job_type=JobType.FUNC_FLOW,
        expected_callable_type=CallableType.SYNC_GENERATOR,
        call_args=(4,),
    )
```

- [ ] **Step 4: Run the sync-generator `FuncFlow` case**

Run: `uv run pytest tests/engine/test_all_engines.py -k "func-flow-sync-generator-body-calls-tasks" -v --mypy-pyproject-toml-file=pyproject.toml`

Expected: the sync-generator `FuncFlow` case runs across both production engines.

- [ ] **Step 5: Add `case_func_flow_async_coroutine_body_calls_tasks`**

```python
@pc.case(id='func-flow-async-coroutine-body-calls-tasks', tags=['matrix', 'funcflow'])
def case_func_flow_async_coroutine_body_calls_tasks() -> ComposedFlowCase[[int], Awaitable[int]]:
    def build_job_func(engine: IsEngine, registry: IsRunStateRegistry | None) -> IsJob:
        increment_tmpl = TaskTemplate(name='func_async_increment')(sync_increment)
        double_tmpl = TaskTemplate(name='func_async_double')(async_double)

        @FuncFlowTemplate(name='func_flow_async_coroutine_body_calls_tasks')
        async def func_parent(number: int) -> int:
            return await resolve(double_tmpl(increment_tmpl(number)))

        return func_parent.apply()

    return ComposedFlowCase(
        name='func_flow_async_coroutine_body_calls_tasks',
        build_job_func=build_job_func,
        run_and_assert_results_func=_assert_async_result(CallableType.ASYNC_COROUTINE, (4,), 10),
        parent_job_type=JobType.FUNC_FLOW,
        expected_callable_type=CallableType.ASYNC_COROUTINE,
        call_args=(4,),
    )
```

- [ ] **Step 6: Run the async-coroutine `FuncFlow` case**

Run: `uv run pytest tests/engine/test_all_engines.py -k "func-flow-async-coroutine-body-calls-tasks" -v --mypy-pyproject-toml-file=pyproject.toml`

Expected: the async-coroutine `FuncFlow` case runs across both production engines.

- [ ] **Step 7: Add `case_func_flow_async_generator_body_calls_tasks`**

```python
@pc.case(id='func-flow-async-generator-body-calls-tasks', tags=['matrix', 'funcflow'])
def case_func_flow_async_generator_body_calls_tasks() -> ComposedFlowCase[[int], AsyncGenerator]:
    def build_job_func(engine: IsEngine, registry: IsRunStateRegistry | None) -> IsJob:
        increment_tmpl = TaskTemplate(name='func_async_generator_increment')(sync_increment)
        range_tmpl = TaskTemplate(name='func_async_generator_range')(async_number_range)

        @FuncFlowTemplate(name='func_flow_async_generator_body_calls_tasks')
        async def func_parent(number: int):
            async for item in range_tmpl(increment_tmpl(number)):
                yield item

        return func_parent.apply()

    return ComposedFlowCase(
        name='func_flow_async_generator_body_calls_tasks',
        build_job_func=build_job_func,
        run_and_assert_results_func=_assert_async_generator(
            CallableType.ASYNC_GENERATOR,
            (4,),
            [0, 1, 2, 3, 4],
        ),
        parent_job_type=JobType.FUNC_FLOW,
        expected_callable_type=CallableType.ASYNC_GENERATOR,
        call_args=(4,),
    )
```

- [ ] **Step 8: Run the async-generator `FuncFlow` case**

Run: `uv run pytest tests/engine/test_all_engines.py -k "func-flow-async-generator-body-calls-tasks" -v --mypy-pyproject-toml-file=pyproject.toml`

Expected: the async-generator `FuncFlow` case runs across both production engines.

- [ ] **Step 9: Re-run the full matrix test**

Run: `uv run pytest tests/engine/test_all_engines.py::test_flow_matrix_all_production_engines -v --mypy-pyproject-toml-file=pyproject.toml`

Expected: the full 3×4 matrix runs across both production engines; any remaining red is an actual behavior gap rather than a missing matrix entry.

- [ ] **Step 10: Commit the `FuncFlow` slice**

```bash
git add tests/engine/cases/flows.py
git commit -m "test: add func flow callable matrix"
```

### Task 5: Add the linear-parent child-flow semantic-floor cases

**Files:**
- Modify: `tests/engine/cases/flows.py`
- Test: `tests/engine/test_all_engines.py`

- [ ] **Step 1: Add the child linear-flow builder**

```python
def _child_linear_double_template(name: str) -> IsLinearFlowTemplate:
    increment_tmpl = TaskTemplate(name=f'{name}_increment')(sync_increment)
    double_tmpl = TaskTemplate(name=f'{name}_double')(sync_double)

    @LinearFlowTemplate(increment_tmpl, double_tmpl, name=name)
    def child_linear(number: int):
        ...

    return child_linear
```

- [ ] **Step 2: Add the child DAG-flow builder**

```python
def _child_dag_double_template(name: str) -> IsDagFlowTemplate:
    seed_tmpl = TaskTemplate(name=f'{name}_seed')(sync_identity).refine(result_key='number')
    double_tmpl = TaskTemplate(name=f'{name}_double')(sync_double)

    @DagFlowTemplate(seed_tmpl, double_tmpl, name=name)
    def child_dag(number: int):
        ...

    return child_dag
```

- [ ] **Step 3: Add the child `FuncFlow` builder**

```python
def _child_func_double_template(name: str) -> IsFuncFlowTemplate:
    increment_tmpl = TaskTemplate(name=f'{name}_increment')(sync_increment)
    double_tmpl = TaskTemplate(name=f'{name}_double')(sync_double)

    @FuncFlowTemplate(name=name)
    def child_func(number: int) -> int:
        return double_tmpl(increment_tmpl(number))

    return child_func
```

- [ ] **Step 4: Add `case_linear_parent_child_linearflow`**

```python
@pc.case(id='linear-parent-child-linearflow', tags=['semantic-floor', 'linearflow', 'child-flow'])
def case_linear_parent_child_linearflow() -> ComposedFlowCase[[int], int]:
    def build_job_func(engine: IsEngine, registry: IsRunStateRegistry | None) -> IsJob:
        return _build_linear_parent('linear_parent_child_linearflow', _child_linear_double_template('child_linear'))

    return ComposedFlowCase(
        name='linear_parent_child_linearflow',
        build_job_func=build_job_func,
        run_and_assert_results_func=_assert_sync_result(CallableType.SYNC_FUNCTION, (4,), 10),
        parent_job_type=JobType.LINEAR_FLOW,
        expected_callable_type=CallableType.SYNC_FUNCTION,
        call_args=(4,),
    )
```

- [ ] **Step 5: Run the linear-parent/child-linearflow case**

Run: `uv run pytest tests/engine/test_all_engines.py -k "linear-parent-child-linearflow" -v --mypy-pyproject-toml-file=pyproject.toml`

Expected: the linear-parent/child-linearflow case runs across both production engines.

- [ ] **Step 6: Add `case_linear_parent_child_dagflow`**

```python
@pc.case(id='linear-parent-child-dagflow', tags=['semantic-floor', 'linearflow', 'child-flow'])
def case_linear_parent_child_dagflow() -> ComposedFlowCase[[int], int]:
    def build_job_func(engine: IsEngine, registry: IsRunStateRegistry | None) -> IsJob:
        return _build_linear_parent('linear_parent_child_dagflow', _child_dag_double_template('child_dag'))

    return ComposedFlowCase(
        name='linear_parent_child_dagflow',
        build_job_func=build_job_func,
        run_and_assert_results_func=_assert_sync_result(CallableType.SYNC_FUNCTION, (4,), 10),
        parent_job_type=JobType.LINEAR_FLOW,
        expected_callable_type=CallableType.SYNC_FUNCTION,
        call_args=(4,),
    )
```

- [ ] **Step 7: Run the linear-parent/child-dagflow case**

Run: `uv run pytest tests/engine/test_all_engines.py -k "linear-parent-child-dagflow" -v --mypy-pyproject-toml-file=pyproject.toml`

Expected: the linear-parent/child-dagflow case runs across both production engines.

- [ ] **Step 8: Add `case_linear_parent_child_funcflow`**

```python
@pc.case(id='linear-parent-child-funcflow', tags=['semantic-floor', 'linearflow', 'child-flow'])
def case_linear_parent_child_funcflow() -> ComposedFlowCase[[int], int]:
    def build_job_func(engine: IsEngine, registry: IsRunStateRegistry | None) -> IsJob:
        return _build_linear_parent('linear_parent_child_funcflow', _child_func_double_template('child_func'))

    return ComposedFlowCase(
        name='linear_parent_child_funcflow',
        build_job_func=build_job_func,
        run_and_assert_results_func=_assert_sync_result(CallableType.SYNC_FUNCTION, (4,), 10),
        parent_job_type=JobType.LINEAR_FLOW,
        expected_callable_type=CallableType.SYNC_FUNCTION,
        call_args=(4,),
    )
```

- [ ] **Step 9: Run the linear-parent/child-funcflow case**

Run: `uv run pytest tests/engine/test_all_engines.py -k "linear-parent-child-funcflow" -v --mypy-pyproject-toml-file=pyproject.toml`

Expected: the linear-parent/child-funcflow case runs across both production engines.

- [ ] **Step 10: Re-run the full linear child-flow slice**

Run: `uv run pytest tests/engine/test_all_engines.py -k "linear-parent-child" -v --mypy-pyproject-toml-file=pyproject.toml`

Expected: the three linear-parent child-flow cases run across both production engines.

- [ ] **Step 11: Commit the linear child-flow slice**

```bash
git add tests/engine/cases/flows.py
git commit -m "test: add linear parent child flow cases"
```

### Task 6: Add the DAG-parent child-flow, routing, and child-flow refine/revise semantic-floor cases

**Files:**
- Modify: `tests/engine/cases/flows.py`
- Test: `tests/engine/test_all_engines.py`

- [ ] **Step 1: Add `case_dag_parent_child_linearflow`**

```python
@pc.case(id='dag-parent-child-linearflow', tags=['semantic-floor', 'dagflow', 'child-flow'])
def case_dag_parent_child_linearflow() -> ComposedFlowCase[[int], int]:
    def build_job_func(engine: IsEngine, registry: IsRunStateRegistry | None) -> IsJob:
        child_tmpl = _child_linear_double_template('dag_child_linear').refine(
            param_key_map={'number': 'number'},
            result_key='number',
        )
        seed_tmpl = TaskTemplate(name='dag_parent_linear_seed')(sync_identity).refine(result_key='number')

        @DagFlowTemplate(seed_tmpl, child_tmpl, name='dag_parent_child_linearflow')
        def dag_parent(number: int):
            ...

        return dag_parent.apply()

    return ComposedFlowCase(
        name='dag_parent_child_linearflow',
        build_job_func=build_job_func,
        run_and_assert_results_func=_assert_sync_result(CallableType.SYNC_FUNCTION, (4,), 10),
        parent_job_type=JobType.DAG_FLOW,
        expected_callable_type=CallableType.SYNC_FUNCTION,
        call_args=(4,),
    )
```

- [ ] **Step 2: Run the DAG-parent/child-linearflow case**

Run: `uv run pytest tests/engine/test_all_engines.py -k "dag-parent-child-linearflow" -v --mypy-pyproject-toml-file=pyproject.toml`

Expected: the DAG-parent/child-linearflow case runs across both production engines.

- [ ] **Step 3: Add `case_dag_parent_child_dagflow`**

```python
@pc.case(id='dag-parent-child-dagflow', tags=['semantic-floor', 'dagflow', 'child-flow'])
def case_dag_parent_child_dagflow() -> ComposedFlowCase[[int], int]:
    def build_job_func(engine: IsEngine, registry: IsRunStateRegistry | None) -> IsJob:
        child_tmpl = _child_dag_double_template('dag_child_dag').refine(
            param_key_map={'number': 'number'},
            result_key='number',
        )
        seed_tmpl = TaskTemplate(name='dag_parent_dag_seed')(sync_identity).refine(result_key='number')

        @DagFlowTemplate(seed_tmpl, child_tmpl, name='dag_parent_child_dagflow')
        def dag_parent(number: int):
            ...

        return dag_parent.apply()

    return ComposedFlowCase(
        name='dag_parent_child_dagflow',
        build_job_func=build_job_func,
        run_and_assert_results_func=_assert_sync_result(CallableType.SYNC_FUNCTION, (4,), 10),
        parent_job_type=JobType.DAG_FLOW,
        expected_callable_type=CallableType.SYNC_FUNCTION,
        call_args=(4,),
    )
```

- [ ] **Step 4: Run the DAG-parent/child-dagflow case**

Run: `uv run pytest tests/engine/test_all_engines.py -k "dag-parent-child-dagflow" -v --mypy-pyproject-toml-file=pyproject.toml`

Expected: the DAG-parent/child-dagflow case runs across both production engines.

- [ ] **Step 5: Add `case_dag_parent_child_funcflow`**

```python
@pc.case(id='dag-parent-child-funcflow', tags=['semantic-floor', 'dagflow', 'child-flow'])
def case_dag_parent_child_funcflow() -> ComposedFlowCase[[int], int]:
    def build_job_func(engine: IsEngine, registry: IsRunStateRegistry | None) -> IsJob:
        child_tmpl = _child_func_double_template('dag_child_func').refine(
            param_key_map={'number': 'number'},
            result_key='number',
        )
        seed_tmpl = TaskTemplate(name='dag_parent_func_seed')(sync_identity).refine(result_key='number')

        @DagFlowTemplate(seed_tmpl, child_tmpl, name='dag_parent_child_funcflow')
        def dag_parent(number: int):
            ...

        return dag_parent.apply()

    return ComposedFlowCase(
        name='dag_parent_child_funcflow',
        build_job_func=build_job_func,
        run_and_assert_results_func=_assert_sync_result(CallableType.SYNC_FUNCTION, (4,), 10),
        parent_job_type=JobType.DAG_FLOW,
        expected_callable_type=CallableType.SYNC_FUNCTION,
        call_args=(4,),
    )
```

- [ ] **Step 6: Run the DAG-parent/child-funcflow case**

Run: `uv run pytest tests/engine/test_all_engines.py -k "dag-parent-child-funcflow" -v --mypy-pyproject-toml-file=pyproject.toml`

Expected: the DAG-parent/child-funcflow case runs across both production engines.

- [ ] **Step 7: Add `case_dag_parent_nested_async_parameter_routing`**

```python
@pc.case(id='dag-parent-nested-async-parameter-routing', tags=['semantic-floor', 'dagflow', 'routing'])
def case_dag_parent_nested_async_parameter_routing() -> ComposedFlowCase[[int], Awaitable[int]]:
    def build_job_func(engine: IsEngine, registry: IsRunStateRegistry | None) -> IsJob:
        seed_tmpl = TaskTemplate(name='routing_seed')(sync_seed_with_plus)
        child_terminal_tmpl = TaskTemplate(name='routing_async_double')(async_double).refine(result_key='number')

        @DagFlowTemplate(child_terminal_tmpl, name='routing_child_flow')
        def child_flow(number: int):
            ...

        add_tmpl = TaskTemplate(name='routing_add')(sync_add)

        @DagFlowTemplate(
            seed_tmpl,
            child_flow.refine(param_key_map={'number': 'number'}, result_key='number'),
            add_tmpl,
            name='dag_parent_nested_async_parameter_routing',
        )
        def parent_flow(number: int):
            ...

        return parent_flow.apply()

    return ComposedFlowCase(
        name='dag_parent_nested_async_parameter_routing',
        build_job_func=build_job_func,
        run_and_assert_results_func=_assert_async_result(CallableType.ASYNC_COROUTINE, (5,), 12),
        parent_job_type=JobType.DAG_FLOW,
        expected_callable_type=CallableType.ASYNC_COROUTINE,
        call_args=(5,),
    )
```

- [ ] **Step 8: Run the nested routing case**

Run: `uv run pytest tests/engine/test_all_engines.py -k "dag-parent-nested-async-parameter-routing" -v --mypy-pyproject-toml-file=pyproject.toml`

Expected: the nested routing case runs across both production engines.

- [ ] **Step 9: Add `case_dag_parent_revise_child_flow_composition`**

```python
@pc.case(id='dag-parent-revise-child-flow-composition', tags=['semantic-floor', 'dagflow', 'refine-revise'])
def case_dag_parent_revise_child_flow_composition() -> ComposedFlowCase[[int], int]:
    def build_job_func(engine: IsEngine, registry: IsRunStateRegistry | None) -> IsJob:
        seed_tmpl = TaskTemplate(name='revise_seed')(sync_identity).refine(result_key='number')
        child_linear = _child_linear_double_template('revise_child_linear').refine(
            param_key_map={'number': 'number'},
            result_key='number',
        )
        child_dag = _child_dag_double_template('revise_child_dag').refine(
            param_key_map={'number': 'number'},
            result_key='number',
        )

        @DagFlowTemplate(seed_tmpl, child_linear, name='dag_parent_revise_child_flow_composition')
        def parent_flow(number: int):
            ...

        revised_parent = parent_flow.apply().revise().refine(
            seed_tmpl,
            child_dag,
            update=False,
            name='dag_parent_revise_child_flow_composition',
        )
        return revised_parent.apply()

    return ComposedFlowCase(
        name='dag_parent_revise_child_flow_composition',
        build_job_func=build_job_func,
        run_and_assert_results_func=_assert_sync_result(CallableType.SYNC_FUNCTION, (4,), 8),
        parent_job_type=JobType.DAG_FLOW,
        expected_callable_type=CallableType.SYNC_FUNCTION,
        call_args=(4,),
    )
```

- [ ] **Step 10: Run the child-flow refine/revise case**

Run: `uv run pytest tests/engine/test_all_engines.py -k "dag-parent-revise-child-flow-composition" -v --mypy-pyproject-toml-file=pyproject.toml`

Expected: the child-flow refine/revise case runs across both production engines.

- [ ] **Step 11: Re-run the full DAG semantic-floor slice**

Run: `uv run pytest tests/engine/test_all_engines.py -k "dag-parent" -v --mypy-pyproject-toml-file=pyproject.toml`

Expected: DAG parent child-flow, routing, and refine/revise cases all execute; any remaining red is a real behavior gap.

- [ ] **Step 12: Commit the DAG semantic-floor slice**

```bash
git add tests/engine/cases/flows.py
git commit -m "test: add dag parent subflow semantics"
```

### Task 7: Add `FuncFlow`-body-calls-flows, mixed sync/async, and nested async support-gap cases

**Files:**
- Modify: `tests/engine/cases/flows.py`
- Test: `tests/engine/test_all_engines.py`

- [ ] **Step 1: Add `case_func_flow_body_calls_child_linearflow`**

```python
@pc.case(id='func-flow-body-calls-child-linearflow', tags=['semantic-floor', 'funcflow', 'child-flow'])
def case_func_flow_body_calls_child_linearflow() -> ComposedFlowCase[[int], int]:
    def build_job_func(engine: IsEngine, registry: IsRunStateRegistry | None) -> IsJob:
        child_flow = _child_linear_double_template('func_body_child_linear')

        @FuncFlowTemplate(name='func_flow_body_calls_child_linearflow')
        def parent_flow(number: int) -> int:
            return child_flow(number)

        return parent_flow.apply()

    return ComposedFlowCase(
        name='func_flow_body_calls_child_linearflow',
        build_job_func=build_job_func,
        run_and_assert_results_func=_assert_sync_result(CallableType.SYNC_FUNCTION, (4,), 10),
        parent_job_type=JobType.FUNC_FLOW,
        expected_callable_type=CallableType.SYNC_FUNCTION,
        call_args=(4,),
    )
```

- [ ] **Step 2: Run the `FuncFlow` body-calls-child-flow case**

Run: `uv run pytest tests/engine/test_all_engines.py -k "func-flow-body-calls-child-linearflow" -v --mypy-pyproject-toml-file=pyproject.toml`

Expected: the `FuncFlow` body-calls-child-flow case runs across both production engines.

- [ ] **Step 3: Add `case_linear_parent_terminal_async_child_funcflow`**

```python
@pc.case(id='linear-parent-terminal-async-child-funcflow', tags=['semantic-floor', 'linearflow', 'async'])
def case_linear_parent_terminal_async_child_funcflow() -> ComposedFlowCase[[int], Awaitable[int]]:
    def build_job_func(engine: IsEngine, registry: IsRunStateRegistry | None) -> IsJob:
        increment_tmpl = TaskTemplate(name='mixed_async_increment')(sync_increment)
        async_double_tmpl = TaskTemplate(name='mixed_async_double')(async_double)

        @FuncFlowTemplate(name='mixed_async_child_funcflow')
        async def child_flow(number: int) -> int:
            return await resolve(async_double_tmpl(number))

        @LinearFlowTemplate(increment_tmpl, child_flow, name='linear_parent_terminal_async_child_funcflow')
        def parent_flow(number: int):
            ...

        return parent_flow.apply()

    return ComposedFlowCase(
        name='linear_parent_terminal_async_child_funcflow',
        build_job_func=build_job_func,
        run_and_assert_results_func=_assert_async_result(CallableType.ASYNC_COROUTINE, (4,), 10),
        parent_job_type=JobType.LINEAR_FLOW,
        expected_callable_type=CallableType.ASYNC_COROUTINE,
        call_args=(4,),
    )
```

- [ ] **Step 4: Run the mixed sync/async case**

Run: `uv run pytest tests/engine/test_all_engines.py -k "linear-parent-terminal-async-child-funcflow" -v --mypy-pyproject-toml-file=pyproject.toml`

Expected: the mixed sync/async terminal-child case runs across both production engines.

- [ ] **Step 5: Add `case_linear_parent_async_generator_child_funcflow_gap`**

```python
@pc.case(id='linear-parent-async-generator-child-funcflow-gap', tags=['semantic-floor', 'linearflow', 'async-gap'])
def case_linear_parent_async_generator_child_funcflow_gap() -> ComposedFlowCase[[int], AsyncGenerator]:
    def build_job_func(engine: IsEngine, registry: IsRunStateRegistry | None) -> IsJob:
        increment_tmpl = TaskTemplate(name='gap_increment')(sync_increment)
        async_range_tmpl = TaskTemplate(name='gap_async_range')(async_number_range)

        @FuncFlowTemplate(name='gap_async_generator_child_funcflow')
        async def child_flow(number: int):
            async for item in async_range_tmpl(number):
                yield item

        @LinearFlowTemplate(increment_tmpl, child_flow, name='linear_parent_async_generator_child_funcflow_gap')
        def parent_flow(number: int):
            ...

        return parent_flow.apply()

    async def run_and_assert_results(job: IsJob) -> None:
        from omnipy.components.prefect.engine.prefect import PrefectEngine

        if check_engine_cls(job, PrefectEngine):
            pytest.xfail(strict=True, reason='PrefectEngine does not drain async-generator child flows correctly')

        assert job.callable_type is CallableType.ASYNC_GENERATOR
        assert [item async for item in job(4)] == [0, 1, 2, 3, 4]
        assert_job_state(job, [RunState.RUNNING, RunState.FINISHED])

    return ComposedFlowCase(
        name='linear_parent_async_generator_child_funcflow_gap',
        build_job_func=build_job_func,
        run_and_assert_results_func=run_and_assert_results,
        parent_job_type=JobType.LINEAR_FLOW,
        expected_callable_type=CallableType.ASYNC_GENERATOR,
        call_args=(4,),
    )
```

- [ ] **Step 6: Run the nested async-generator support-gap case**

Run: `uv run pytest tests/engine/test_all_engines.py -k "linear-parent-async-generator-child-funcflow-gap" -v --mypy-pyproject-toml-file=pyproject.toml`

Expected: the nested async-generator case is green on supported engines and explicitly classified on `PrefectEngine`.

- [ ] **Step 7: Re-run the full semantic-floor test**

Run: `uv run pytest tests/engine/test_all_engines.py::test_nested_flow_semantic_floor_all_production_engines -v --mypy-pyproject-toml-file=pyproject.toml`

Expected: semantic-floor coverage now includes child-flow `FuncFlow`, mixed sync/async composition, and one explicit nested async support-gap classification.

- [ ] **Step 8: Commit the remaining semantic-floor slice**

```bash
git add tests/engine/cases/flows.py
git commit -m "test: classify nested async subflow coverage"
```

### Task 8: Add validation-only compute coverage and a narrow production seam only if red tests prove one is needed

**Files:**
- Modify: `tests/compute/test_flow.py`
- Modify only if needed: `src/omnipy/compute/_joblist_job.py`
- Modify only if needed: `src/omnipy/engine/run_spec.py`
- Test: `tests/compute/test_flow.py`
- Test: `tests/engine/test_all_engines.py`

- [ ] **Step 1: Write `test_linear_flow_child_flow_terminal_callable_type_follows_async_child`**

```python
def test_linear_flow_child_flow_terminal_callable_type_follows_async_child() -> None:
    @TaskTemplate()
    def sync_start(number: int) -> int:
        return number + 1

    @TaskTemplate()
    async def async_terminal(number: int) -> int:
        return number * 2

    @FuncFlowTemplate()
    async def child_async_flow(number: int) -> int:
        return await resolve(async_terminal(number))

    @LinearFlowTemplate(sync_start, child_async_flow)
    def linear_flow_tmpl(number: int) -> int:
        ...

    linear_flow = linear_flow_tmpl.apply()
    assert linear_flow_tmpl.callable_type is CallableType.ASYNC_COROUTINE
    assert linear_flow.callable_type is CallableType.ASYNC_COROUTINE
```

- [ ] **Step 2: Write `test_dag_flow_refine_rechecks_child_flow_callable_type`**

```python
def test_dag_flow_refine_rechecks_child_flow_callable_type() -> None:
    @TaskTemplate()
    def sync_start(number: int) -> int:
        return number

    @TaskTemplate()
    async def async_terminal(number: int) -> int:
        return number * 2

    @FuncFlowTemplate()
    async def child_async_flow(number: int) -> int:
        return await resolve(async_terminal(number))

    dag_flow_tmpl = DagFlowTemplate(sync_start.refine(result_key='number'))(sync_start)
    refined_tmpl = dag_flow_tmpl.refine(
        sync_start.refine(result_key='number'),
        child_async_flow.refine(param_key_map={'number': 'number'}, result_key='number'),
        update=False,
    )

    assert refined_tmpl.callable_type is CallableType.ASYNC_COROUTINE
```

- [ ] **Step 3: Write `test_dag_flow_revise_rechecks_replaced_child_flow_callable_type`**

```python
def test_dag_flow_revise_rechecks_replaced_child_flow_callable_type() -> None:
    @TaskTemplate()
    def sync_start(number: int) -> int:
        return number

    @TaskTemplate()
    async def async_terminal(number: int) -> int:
        return number * 2

    @FuncFlowTemplate()
    async def child_async_flow(number: int) -> int:
        return await resolve(async_terminal(number))

    dag_flow_tmpl = DagFlowTemplate(sync_start.refine(result_key='number'))(sync_start)
    revised_tmpl = dag_flow_tmpl.apply().revise().refine(
        sync_start.refine(result_key='number'),
        child_async_flow.refine(param_key_map={'number': 'number'}, result_key='number'),
        update=False,
    )

    assert revised_tmpl.callable_type is CallableType.ASYNC_COROUTINE
```

- [ ] **Step 4: Run the focused compute slice**

Run: `uv run pytest tests/compute/test_flow.py -k "child_flow_callable_type or refine_rechecks or revise_rechecks" -v --mypy-pyproject-toml-file=pyproject.toml`

Expected: failure points to callable-type lifting or revalidation, not unrelated flow behavior.

- [ ] **Step 5: User Check-in A — pause before any production edit**

Summarize the exact failing seam with one sentence:

- `ChildJobListArgJobBase` reports callable type from the authored body instead of the terminal child flow.
- `ChildJobListArgJobBase._refine()` keeps stale callable-type metadata after child-flow replacement.
- `run_spec` resolves async child-flow results inconsistently for the targeted nested case.

- [ ] **Step 6: Apply the callable-type seam if the red tests point to `ChildJobListArgJobBase`**

```python
class ChildJobListArgJobBase(...):
    @property
    def callable_type(self) -> CallableType.Literals:
        if self.child_job_templates:
            return self.child_job_templates[-1].callable_type
        return super().callable_type
```

- [ ] **Step 7: Apply the nested async drain seam if the red tests point to `run_spec`**

```python
async def _drain_async_results(
    run_tasks_gen: Generator[object, object, object],
    resolve_result_func: Callable[[object], Any] = resolve,
) -> object:
    ...
```

- [ ] **Step 8: Re-run compute plus engine coverage immediately after the seam**

Run: `uv run pytest tests/compute/test_flow.py tests/engine/test_all_engines.py -v --mypy-pyproject-toml-file=pyproject.toml`

Expected: compute tests are green, and engine tests are green or explicitly classified as support gaps.

- [ ] **Step 9: Commit only if Task 8 was activated**

```bash
git add tests/compute/test_flow.py src/omnipy/compute/_joblist_job.py src/omnipy/engine/run_spec.py tests/engine/test_all_engines.py
git commit -m "fix: align child-flow callable semantics"
```

### Task 9: Add three selective integration confirmations

**Files:**
- Create: `tests/integration/reused/compute/test_async_and_subflows_with_all_engines.py`
- Test: `tests/integration/reused/compute/test_async_and_subflows_with_all_engines.py`

- [ ] **Step 1: Add `test_nested_async_child_flow_with_all_engines`**

```python
@pytest.mark.asyncio
async def test_nested_async_child_flow_with_all_engines(
    runtime_all_engines: Annotated[None, pytest.fixture],
) -> None:
    @TaskTemplate()
    def sync_start(number: int) -> int:
        return number + 1

    @TaskTemplate()
    async def async_double_tmpl(number: int) -> int:
        return number * 2

    @FuncFlowTemplate()
    async def child_flow_tmpl(number: int) -> int:
        return await resolve(async_double_tmpl(number))

    @LinearFlowTemplate(sync_start, child_flow_tmpl)
    def parent_flow_tmpl(number: int) -> int:
        ...

    assert await resolve(parent_flow_tmpl.apply()(4)) == 10
```

- [ ] **Step 2: Add `test_nested_parameter_routing_across_child_flow_with_all_engines`**

```python
def test_nested_parameter_routing_across_child_flow_with_all_engines(
    runtime_all_engines: Annotated[None, pytest.fixture],
) -> None:
    @TaskTemplate()
    def seed_tmpl(number: int) -> dict[str, int]:
        return {'number': number, 'plus': 2}

    @TaskTemplate()
    def double_tmpl(number: int) -> int:
        return number * 2

    @DagFlowTemplate(double_tmpl.refine(result_key='number'))
    def child_flow_tmpl(number: int) -> int:
        ...

    @TaskTemplate()
    def add_tmpl(number: int, plus: int) -> int:
        return number + plus

    @DagFlowTemplate(
        seed_tmpl,
        child_flow_tmpl.refine(param_key_map={'number': 'number'}, result_key='number'),
        add_tmpl,
    )
    def parent_flow_tmpl(number: int) -> int:
        ...

    assert parent_flow_tmpl.apply()(5) == 12
```

- [ ] **Step 3: Add `test_revise_replaces_child_flow_in_dag_parent_with_all_engines`**

```python
def test_revise_replaces_child_flow_in_dag_parent_with_all_engines(
    runtime_all_engines: Annotated[None, pytest.fixture],
) -> None:
    @TaskTemplate()
    def seed_tmpl(number: int) -> int:
        return number

    @TaskTemplate()
    def double_tmpl(number: int) -> int:
        return number * 2

    @TaskTemplate()
    def square_tmpl(number: int) -> int:
        return number * number

    @LinearFlowTemplate(double_tmpl)
    def child_linear_tmpl(number: int) -> int:
        ...

    @DagFlowTemplate(square_tmpl.refine(result_key='number'))
    def child_dag_tmpl(number: int) -> int:
        ...

    parent_flow_tmpl = DagFlowTemplate(
        seed_tmpl.refine(result_key='number'),
        child_linear_tmpl.refine(param_key_map={'number': 'number'}, result_key='number'),
    )(seed_tmpl)

    revised_parent_flow_tmpl = parent_flow_tmpl.apply().revise().refine(
        seed_tmpl.refine(result_key='number'),
        child_dag_tmpl.refine(param_key_map={'number': 'number'}, result_key='number'),
        update=False,
    )

    assert revised_parent_flow_tmpl.apply()(4) == 16
```

- [ ] **Step 4: Run the integration file**

Run: `uv run pytest tests/integration/reused/compute/test_async_and_subflows_with_all_engines.py -v --mypy-pyproject-toml-file=pyproject.toml`

Expected: the file is green except for any intentionally classified engine-specific support gap.

- [ ] **Step 5: Commit the integration slice**

```bash
git add tests/integration/reused/compute/test_async_and_subflows_with_all_engines.py
git commit -m "test: confirm async subflows in integration"
```

### Task 10: Final verification, support-gap audit, and handoff evidence

**Files:**
- Modify only if cleanup from earlier tasks is needed: files already touched above

- [ ] **Step 1: Run the focused verification stack**

Run: `uv run pytest tests/engine/test_all_engines.py tests/compute/test_flow.py tests/integration/reused/compute/test_async_and_subflows_with_all_engines.py -v --mypy-pyproject-toml-file=pyproject.toml`

Expected: green or explicitly classified support gaps only.

- [ ] **Step 2: Run the broader dependency coverage**

Run: `uv run pytest tests/engine tests/integration/reused/compute/test_flow_with_all_engines.py tests/integration/reused/compute/test_async_and_subflows_with_all_engines.py -v --mypy-pyproject-toml-file=pyproject.toml`

Expected: no unexpected regressions outside the new async/subflow slice.

- [ ] **Step 3: Run formatting and hook validation**

Run: `uv run pre-commit run --hook-stage manual --all-files`

Expected: pass, or auto-fixes limited to touched files and re-verified immediately.

- [ ] **Step 4: Record the retained-gap audit in the handoff or PR**

Record these exact items:

- every engine-specific `xfail` and its reason
- every intentionally retained plain failing test and why visible red is preferred
- whether Task 8 was skipped or activated
- which linear-parent and DAG-parent child-flow cases satisfy the semantic floor
- which case proves child-flow refine/revise replacement

- [ ] **Step 5: Final commit only if Step 3 changed tracked files**

```bash
git add tests/engine tests/compute/test_flow.py tests/integration/reused/compute/test_async_and_subflows_with_all_engines.py src/omnipy/compute/_joblist_job.py src/omnipy/engine/run_spec.py
git commit -m "chore: finalize async subflow test coverage"
```

## Spec-to-plan self-check

- The engine harness remains the main authority, but parity cases use real templates under production engines rather than mock-only flow templates.
- The full 3×4 matrix is explicit and split across Tasks 2–4.
- Linear and DAG parents each get child-flow coverage for `LinearFlow`, `DagFlow`, and `FuncFlow` in Tasks 5–6.
- `FuncFlow` task-body semantics are covered in Task 4; `FuncFlow` body-calls-flow semantics are covered in Task 7.
- Nested parent/child routing is covered in Task 6 and confirmed in Task 9.
- A targeted child-flow refine/revise replacement case is required in Task 6 and confirmed again in Task 9.
- Compute coverage stays validation-only and optional in Task 8.
- The plan keeps `tests/engine/cases/tasks.py` as the main primitive-callable source for new flow-case primitives.
- Support-gap handling stays explicit through Task 7 and Task 10.

## Implementation notes for the executing agent

- Do not add new primitive callables to `tests/engine/cases/raw/functions.py` for this slice; add the new single-thread primitives in `tests/engine/cases/tasks.py` and import them into `tests/engine/cases/flows.py`.
- Keep top-level test bodies tiny; put case topology in `tests/engine/cases/flows.py` and keep fixture logic in `tests/engine/conftest.py`.
- Do not expand into multithread or multiprocess coverage.
- If Task 8 activates, make the compute test fail first, make the engine case fail first, apply the seam, and then rerun both.
