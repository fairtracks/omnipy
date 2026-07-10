# Async And Sub-Flow Testing Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add engine-first async and nested-flow test coverage with an exhaustive per-production-engine 3×4 parent-flow/callable matrix, representative child-flow and parameter-routing coverage, and only the smallest proven production seam if red tests require one.

**Architecture:** Keep `tests/engine/` as the coverage authority by adding reusable composite-flow cases, richer builder helpers, and thin parametrized engine tests over `LocalRunner` and `PrefectEngine`. Use `tests/compute/` only for construction/refine/revise callable-type validation if red tests prove a missing consistency check, and add only a few realistic `tests/integration/` confirmations instead of another matrix.

**Tech Stack:** Python, pytest, pytest-cases, asyncio, Omnipy flow/task templates, LocalRunner, PrefectEngine

---

## File map

- Create: `tests/engine/cases/flows.py`
  - Composite and nested flow cases for the engine harness.
- Modify: `tests/engine/cases/raw/functions.py`
  - Add only missing primitive single-thread callables needed for nested async and parameter-routing cases.
- Modify: `tests/engine/helpers/classes.py`
  - Add a composed-flow case carrier instead of stuffing new topology fields into thin top-level tests.
- Modify: `tests/engine/helpers/functions.py`
  - Generalize builders from “two func tasks” to “task and/or flow children”, and keep state/assert helpers reusable.
- Modify: `tests/engine/conftest.py`
  - Add parametrized fixtures for the exhaustive flow matrix and semantic-floor cases across production engines.
- Modify: `tests/engine/test_all_engines.py`
  - Add thin async parametrized tests that consume the new fixtures.
- Modify only if red tests require it: `tests/compute/test_flow.py`
  - Validation-only tests for terminal-child callable-type consistency on construction, `refine()`, and `revise()`.
- Modify only if red tests require it: `src/omnipy/compute/_joblist_job.py`
  - Small callable-type/validation seam for child-job-list flows.
- Modify only if red tests require it: `src/omnipy/engine/run_spec.py`
  - Small async-resolution seam if nested async behavior is correct in intent but not lifted consistently.
- Create: `tests/integration/reused/compute/test_async_and_subflows_with_all_engines.py`
  - A few realistic confirming scenarios, not another cartesian matrix.

## Coverage ledger

- Exhaustive per production engine: `LinearFlow`, `DagFlow`, `FuncFlow` × sync function / sync generator / async coroutine / async generator → **Task 2**
- Linear/DAG with real multiple children, including child tasks and child flows → **Tasks 2–3**
- Child flows of each existing flow type under linear/DAG parents at least once overall → **Task 3**
- `FuncFlow` cases that call tasks and separate cases that call flows → **Task 3**
- Mixed sync/async compositions, nested async behavior, and at least one nested async failure/support-gap case → **Task 3**
- Nested parameter routing across parent/child flow boundaries → **Tasks 3 and 5**
- Validation-only compute coverage for construction + `refine()` / `revise()` if a small seam is needed → **Task 4**
- Selective integration confirmations only → **Task 5**
- Explicit support-gap handling (`xfail`, engine-specific expectation, or intentionally retained red test) → **Tasks 3, 4, and 6**

## Support-gap policy for implementation

- Known external engine limitations: prefer engine-specific `xfail(strict=True)` with a short reason.
- Claimed-supported but uncovered behavior: keep the failing signal narrow; use plain red committed tests only when visible red coverage is the point.
- Temporary TDD-red during development: acceptable locally, but each retained gap must be deliberately classified before the slice is declared done.

## User Check-in markers

- **User Check-in A:** If Task 3 exposes a likely production seam, stop before editing `src/omnipy/compute/_joblist_job.py` or `src/omnipy/engine/run_spec.py` and confirm the smallest intended fix.
- **User Check-in B:** If any case seems to require more than a localized callable-type/testability seam, pause and open a follow-up design/planning step instead of expanding scope here.

### Task 1: Scaffold composite-flow engine cases without growing bespoke top-level tests

**Files:**
- Create: `tests/engine/cases/flows.py`
- Modify: `tests/engine/helpers/classes.py`
- Modify: `tests/engine/helpers/functions.py`
- Modify: `tests/engine/conftest.py`
- Modify: `tests/engine/test_all_engines.py`
- Test: `tests/engine/test_all_engines.py`

- [ ] **Step 1: Write the first failing thin engine-harness test**

```python
@pc.parametrize(
    'job_case',
    [pc.fixture_ref('all_flow_matrix_cases_all_engines_assert_runstate_mock_reg')],
    ids=[''],
)
@pytest.mark.asyncio
async def test_flow_matrix_all_production_engines(job_case: JobCase) -> None:
    await run_job_test(job_case)


@pc.parametrize(
    'job_case',
    [pc.fixture_ref('nested_flow_semantic_floor_cases_all_engines_assert_runstate_mock_reg')],
    ids=[''],
)
@pytest.mark.asyncio
async def test_nested_flow_semantic_floor_all_production_engines(job_case: JobCase) -> None:
    await run_job_test(job_case)
```

- [ ] **Step 2: Run the engine test to verify the harness fails for the right reason**

Run: `uv run pytest tests/engine/test_all_engines.py -v --mypy-pyproject-toml-file=pyproject.toml`

Expected: collection fails because the new fixtures/case module do not exist yet, not because of unrelated import or environment issues.

- [ ] **Step 3: Add only the minimum scaffolding to make the new tests collect**

Use a dedicated composed-flow case carrier in `tests/engine/helpers/classes.py` so the new axes stay out of top-level tests:

```python
from collections.abc import Sequence


@dataclass
class ComposedFlowCase(JobCase[CallP, ReturnT]):
    parent_job_type: JobType.Literals
    expected_callable_type: CallableType.Literals
    child_job_kinds: Sequence[JobType.Literals]
```

Generalize `tests/engine/helpers/functions.py` around a builder entry point instead of one helper per “two task” shape:

```python
def create_linear_flow_with_children(
    name: str,
    flow_func: Callable,
    child_job_templates: tuple[IsFuncArgJobTemplate, ...],
    linear_flow_template_cls: type[IsLinearFlowTemplate],
    engine: IsLinearFlowRunnerEngine,
    registry: IsRunStateRegistry | None,
) -> IsLinearFlow:
    linear_flow_template = linear_flow_template_cls(*child_job_templates, name=name)(flow_func)
    linear_flow_template_cls.job_creator.set_engine(engine)  # type: ignore[attr-defined]
    if registry:
        engine.set_registry(registry)
    return linear_flow_template.apply()


def create_dag_flow_with_children(
    name: str,
    flow_func: Callable,
    child_job_templates: tuple[IsFuncArgJobTemplate, ...],
    dag_flow_template_cls: type[IsDagFlowTemplate],
    engine: IsDagFlowRunnerEngine,
    registry: IsRunStateRegistry | None,
) -> IsDagFlow:
    dag_flow_template = dag_flow_template_cls(*child_job_templates, name=name)(flow_func)
    dag_flow_template_cls.job_creator.set_engine(engine)  # type: ignore[attr-defined]
    if registry:
        engine.set_registry(registry)
    return dag_flow_template.apply()


def create_func_flow_with_body(
    flow_template: IsFuncFlowTemplate,
    engine: IsFuncFlowRunnerEngine,
    registry: IsRunStateRegistry | None,
) -> IsFuncFlow:
    type(flow_template).job_creator.set_engine(engine)  # type: ignore[attr-defined]
    if registry:
        engine.set_registry(registry)
    return flow_template.apply()
```

In `tests/engine/conftest.py`, add the two new fixture families and keep them parametrized over `all_engines`, `assert_runstate`, and `mock_registry`.

- [ ] **Step 4: Re-run the targeted engine test and require behavioral failures only**

Run: `uv run pytest tests/engine/test_all_engines.py -v --mypy-pyproject-toml-file=pyproject.toml`

Expected: tests now collect; any failures are about missing case definitions or current async/subflow behavior, not missing fixtures/helpers.

- [ ] **Step 5: Commit the scaffolding slice**

```bash
git add tests/engine/cases/flows.py tests/engine/helpers/classes.py tests/engine/helpers/functions.py tests/engine/conftest.py tests/engine/test_all_engines.py
git commit -m "test: scaffold async subflow engine cases"
```

### Task 2: Add the exhaustive 3×4 parent-flow/callable matrix for each production engine

**Files:**
- Modify: `tests/engine/cases/flows.py`
- Modify: `tests/engine/cases/raw/functions.py`
- Modify: `tests/engine/conftest.py`
- Modify: `tests/engine/test_all_engines.py`
- Test: `tests/engine/test_all_engines.py`

- [ ] **Step 1: Write failing matrix cases before adding builders or primitives**

Define cases in `tests/engine/cases/flows.py` so each parent flow type has all four top-level callable outcomes:

```python
@pc.case(id='linear-flow-sync-function-terminal-child', tags=['linearflow', 'sync', 'function'])
def case_linear_flow_sync_function_terminal_child() -> ComposedFlowCase[[int, int], int]:
    def run_and_assert_results(job: IsJob) -> None:
        assert job.callable_type is CallableType.SYNC_FUNCTION
        assert job(4, 2) == 16
        assert_job_state(job, [RunState.FINISHED])

    return ComposedFlowCase(
        'linear_flow_sync_function_terminal_child',
        sync_power,
        run_and_assert_results,
        parent_job_type=JobType.LINEAR_FLOW,
        expected_callable_type=CallableType.SYNC_FUNCTION,
        child_job_kinds=[JobType.TASK, JobType.TASK],
    )


@pc.case(id='linear-flow-async-generator-terminal-child', tags=['linearflow', 'async', 'generator'])
@pytest.mark.asyncio
def case_linear_flow_async_generator_terminal_child() -> ComposedFlowCase[[int], AsyncGenerator]:
    async def run_and_assert_results(job: IsJob) -> None:
        assert job.callable_type is CallableType.ASYNC_GENERATOR
        assert [item async for item in job(5)] == [0, 1, 2, 3, 4]
        assert_job_state(job, [RunState.FINISHED])

    return ComposedFlowCase(
        'linear_flow_async_generator_terminal_child',
        async_range,
        run_and_assert_results,
        parent_job_type=JobType.LINEAR_FLOW,
        expected_callable_type=CallableType.ASYNC_GENERATOR,
        child_job_kinds=[JobType.TASK, JobType.TASK],
    )
```

Add the other ten cases with these exact ids so the per-engine matrix is explicit and reviewable:

- `linear-flow-sync-generator-terminal-child`
- `linear-flow-async-coroutine-terminal-child`
- `dag-flow-sync-function-terminal-child`
- `dag-flow-sync-generator-terminal-child`
- `dag-flow-async-coroutine-terminal-child`
- `dag-flow-async-generator-terminal-child`
- `func-flow-sync-function-body`
- `func-flow-sync-generator-body`
- `func-flow-async-coroutine-body`
- `func-flow-async-generator-body`

For linear and DAG cases, use multiple children and make the terminal child the callable-type driver.

- [ ] **Step 2: Run only the matrix test and confirm genuine red behavior**

Run: `uv run pytest tests/engine/test_all_engines.py::test_flow_matrix_all_production_engines -v --mypy-pyproject-toml-file=pyproject.toml`

Expected: failures identify missing cases, missing primitive callables, or current callable-type mismatches; no new failure should come from multithread or multiprocess paths.

- [ ] **Step 3: Add only the primitive single-thread callables needed to express the matrix cleanly**

Extend `tests/engine/cases/raw/functions.py` conservatively, for example with parameter-preserving pass-throughs or tiny async wrappers:

```python
def sync_identity(value: object) -> object:
    return value


async def async_identity(value: object) -> object:
    return value
```

Reuse existing `sync_range`, `async_range`, `sync_power`, and `async_wait_a_bit` wherever they already model the needed callable type.

- [ ] **Step 4: Make each matrix case assert both behavior and exposed callable type**

Each `run_and_assert_results_func` should verify:

```python
assert job.callable_type is expected_callable_type
assert_job_state(job, [RunState.RUNNING, RunState.FINISHED])
```

and then execute the flow using the correct sync/async/generator path.

- [ ] **Step 5: Re-run the matrix and keep the result classification explicit**

Run: `uv run pytest tests/engine/test_all_engines.py::test_flow_matrix_all_production_engines -v --mypy-pyproject-toml-file=pyproject.toml`

Expected: each production engine now exercises the full 3×4 matrix; any remaining red entries are explicitly tagged as support gaps or known engine limitations.

- [ ] **Step 6: Commit the matrix slice**

```bash
git add tests/engine/cases/flows.py tests/engine/cases/raw/functions.py tests/engine/conftest.py tests/engine/test_all_engines.py
git commit -m "test: add async flow callable matrix"
```

### Task 3: Cover nested child flows, mixed sync/async behavior, parameter routing, and support gaps

**Files:**
- Modify: `tests/engine/cases/flows.py`
- Modify: `tests/engine/helpers/functions.py`
- Modify: `tests/engine/test_all_engines.py`
- Test: `tests/engine/test_all_engines.py`

- [ ] **Step 1: Write the semantic-floor cases first**

Add failing cases that cover the spec floor beyond the 3×4 matrix:

```python
@pc.case(id='linear-parent-with-child-funcflow', tags=['linearflow', 'child-flow', 'funcflow'])
def case_linear_parent_with_child_funcflow() -> ComposedFlowCase[[int, int], int]:
    def run_and_assert_results(job: IsJob) -> None:
        assert job.callable_type is CallableType.SYNC_FUNCTION
        assert job(3, 2) == 9

    return ComposedFlowCase(
        'linear_parent_with_child_funcflow',
        sync_power,
        run_and_assert_results,
        parent_job_type=JobType.LINEAR_FLOW,
        expected_callable_type=CallableType.SYNC_FUNCTION,
        child_job_kinds=[JobType.TASK, JobType.FUNC_FLOW],
    )


@pc.case(id='dag-parent-nested-async-parameter-routing', tags=['dagflow', 'async', 'routing'])
@pytest.mark.asyncio
def case_dag_parent_nested_async_parameter_routing() -> ComposedFlowCase[[int], Awaitable[int]]:
    async def run_and_assert_results(job: IsJob) -> None:
        assert job.callable_type is CallableType.ASYNC_COROUTINE
        assert await resolve(job(5)) == 12

    return ComposedFlowCase(
        'dag_parent_nested_async_parameter_routing',
        async_identity,
        run_and_assert_results,
        parent_job_type=JobType.DAG_FLOW,
        expected_callable_type=CallableType.ASYNC_COROUTINE,
        child_job_kinds=[JobType.TASK, JobType.LINEAR_FLOW, JobType.TASK],
    )


@pc.case(id='funcflow-body-calls-child-flow', tags=['funcflow', 'child-flow'])
def case_funcflow_body_calls_child_flow() -> ComposedFlowCase[[int, int], int]:
    def run_and_assert_results(job: IsJob) -> None:
        assert job.callable_type is CallableType.SYNC_FUNCTION
        assert job(4, 2) == 16

    return ComposedFlowCase(
        'funcflow_body_calls_child_flow',
        sync_power,
        run_and_assert_results,
        parent_job_type=JobType.FUNC_FLOW,
        expected_callable_type=CallableType.SYNC_FUNCTION,
        child_job_kinds=[JobType.LINEAR_FLOW],
    )
```

Required minimums for this task:
- one linear parent using a child `LinearFlow`
- one linear parent using a child `DagFlow`
- one linear parent using a child `FuncFlow`
- one DAG parent using a child `LinearFlow`
- one DAG parent using a child `DagFlow`
- one DAG parent using a child `FuncFlow`
- one parent `FuncFlow` body calling tasks
- one separate parent `FuncFlow` body calling flows
- one mixed sync/async composition where the terminal child is async
- one nested async support-gap or failure-path case
- one nested parent/child parameter-routing case

- [ ] **Step 2: Run the semantic-floor test and verify it fails on real missing behavior**

Run: `uv run pytest tests/engine/test_all_engines.py::test_nested_flow_semantic_floor_all_production_engines -v --mypy-pyproject-toml-file=pyproject.toml`

Expected: failures come from missing child-flow builder support, missing routing assertions, or real engine behavior gaps.

- [ ] **Step 3: Extend the helper builders just enough for task and flow children**

The helper layer should be able to assemble:

```python
linear_flow_template_cls(child_task_tmpl, child_flow_tmpl, terminal_child_tmpl, name=name)(flow_func)
dag_flow_template_cls(child_task_tmpl, child_flow_tmpl.refine(result_key='value'), terminal_child_tmpl)(flow_func)
```

Do not add a new public abstraction; keep the complexity in `tests/engine/helpers/functions.py` and `tests/engine/cases/flows.py`.

- [ ] **Step 4: Classify every remaining red case deliberately**

Use one of these outcomes per retained gap:

```python
pytest.xfail('Prefect external limitation: async generator subflow result is not drained correctly')

@pytest.mark.xfail(strict=True, reason='Claimed-supported nested async child-flow gap')

# plain failure retained only when visible red coverage is intentional
```

Known Prefect generator limitations should follow the existing engine-specific pattern already used in `tests/engine/cases/tasks.py`.

- [ ] **Step 5: Re-run the full engine file and verify the harness-level contract**

Run: `uv run pytest tests/engine/test_all_engines.py -v --mypy-pyproject-toml-file=pyproject.toml`

Expected: the file now demonstrates run-state assertions, terminal-child result propagation, nested parameter routing, and explicit gap handling across both production engines.

- [ ] **Step 6: Commit the semantic-floor slice**

```bash
git add tests/engine/cases/flows.py tests/engine/helpers/functions.py tests/engine/test_all_engines.py
git commit -m "test: cover nested flow engine semantics"
```

### Task 4: Add validation-only compute coverage and the smallest production seam only if red tests prove it

**Files:**
- Modify: `tests/compute/test_flow.py`
- Modify only if needed: `src/omnipy/compute/_joblist_job.py`
- Modify only if needed: `src/omnipy/engine/run_spec.py`
- Test: `tests/compute/test_flow.py`
- Test: `tests/engine/test_all_engines.py`

- [ ] **Step 1: Write failing compute tests that pin the missing contract before touching production code**

Add focused validation tests only if Task 3 exposes a real callable-type inconsistency:

```python
def test_linear_flow_callable_type_follows_terminal_child_template() -> None:
    @TaskTemplate()
    def sync_prefix(number: int) -> int:
        return number + 1

    @TaskTemplate()
    async def async_terminal(number: int) -> int:
        return number * 2

    @LinearFlowTemplate(sync_prefix, async_terminal)
    def linear_flow_tmpl(number: int) -> int:
        return -1

    linear_flow = linear_flow_tmpl.apply()
    assert linear_flow_tmpl.callable_type is CallableType.ASYNC_COROUTINE
    assert linear_flow.callable_type is CallableType.ASYNC_COROUTINE


def test_dag_flow_refine_rechecks_terminal_child_callable_type() -> None:
    @TaskTemplate()
    def sync_prefix(number: int) -> int:
        return number + 1

    @TaskTemplate()
    async def async_terminal(number: int) -> int:
        return number * 2

    dag_flow_tmpl = DagFlowTemplate(sync_prefix)(sync_prefix._job_func)
    refined_tmpl = dag_flow_tmpl.refine(sync_prefix, async_terminal)

    assert refined_tmpl.callable_type is CallableType.ASYNC_COROUTINE


def test_dag_flow_revise_preserves_child_flow_callable_type_consistency() -> None:
    @TaskTemplate()
    async def async_terminal(number: int) -> int:
        return number * 2

    dag_flow_tmpl = DagFlowTemplate(async_terminal)(async_terminal._job_func)
    revised_tmpl = dag_flow_tmpl.apply().revise()

    assert revised_tmpl.callable_type is CallableType.ASYNC_COROUTINE
```

These tests should use real flow/task templates and avoid duplicating engine-harness assertions.

- [ ] **Step 2: Run the compute tests and verify the failure is specific**

Run: `uv run pytest tests/compute/test_flow.py -k "callable_type or refine or revise" -v --mypy-pyproject-toml-file=pyproject.toml`

Expected: failures point to terminal-child callable-type lifting or missing revalidation, not unrelated flow behavior.

- [ ] **Step 3: User Check-in A — pause before any production edit**

Summarize the smallest red-driven seam, for example:
- child-job-list flows expose callable type from the authored body instead of the terminal child
- nested async resolution only detects `ASYNC_COROUTINE` and misses another supported async path

Do not edit production files until this checkpoint is acknowledged.

- [ ] **Step 4: Implement the smallest seam that makes the red tests express the intended existing behavior**

Keep the change localized. The only acceptable production directions in this slice are shaped like:

```python
class ChildJobListArgJobBase:
    @property
    def callable_type(self) -> CallableType.Literals:
        return self.child_job_templates[-1].callable_type
```

or a similarly small validation hook near `refine()` / `revise()` or async result draining in `src/omnipy/engine/run_spec.py`.

- [ ] **Step 5: Re-run compute plus engine coverage immediately after the seam**

Run: `uv run pytest tests/compute/test_flow.py tests/engine/test_all_engines.py -v --mypy-pyproject-toml-file=pyproject.toml`

Expected: compute tests are green, and engine tests either go green or remain explicitly classified as known support gaps.

- [ ] **Step 6: Commit only if this task was activated**

```bash
git add tests/compute/test_flow.py src/omnipy/compute/_joblist_job.py src/omnipy/engine/run_spec.py tests/engine/test_all_engines.py
git commit -m "fix: align async subflow callable semantics"
```

### Task 5: Add a few realistic integration confirmations and no extra matrix

**Files:**
- Create: `tests/integration/reused/compute/test_async_and_subflows_with_all_engines.py`
- Test: `tests/integration/reused/compute/test_async_and_subflows_with_all_engines.py`

- [ ] **Step 1: Write the integration tests first**

Create three direct scenarios, no more unless one replaces another:

```python
@pytest.mark.asyncio
async def test_nested_async_flow_with_all_engines() -> None:
    @TaskTemplate()
    async def async_double(number: int) -> int:
        return number * 2

    @LinearFlowTemplate(async_double)
    def child_flow_tmpl(number: int) -> int:
        return -1

    @FuncFlowTemplate()
    async def parent_flow_tmpl(number: int) -> int:
        return await resolve(child_flow_tmpl(number))

    assert await resolve(parent_flow_tmpl.apply()(4)) == 8


def test_nested_parameter_routing_with_all_engines() -> None:
    @TaskTemplate()
    def start(number: int) -> dict[str, int]:
        return {'number': number, 'plus': 2}

    @TaskTemplate()
    def add(number: int, plus: int) -> int:
        return number + plus

    @DagFlowTemplate(start, add)
    def child_flow_tmpl(number: int) -> int:
        return -1

    @FuncFlowTemplate()
    def parent_flow_tmpl(number: int) -> int:
        return child_flow_tmpl(number)

    assert parent_flow_tmpl.apply()(5) == 7


def test_child_flow_refine_or_revise_with_all_engines() -> None:
    @TaskTemplate()
    def start(number: int) -> int:
        return number

    @TaskTemplate()
    def plus_one(number: int) -> int:
        return number + 1

    linear_flow_tmpl = LinearFlowTemplate(start, plus_one)(start._job_func)
    revised_flow_tmpl = linear_flow_tmpl.apply().revise()

    assert revised_flow_tmpl.apply()(4) == 5
```

If the refine/revise lifecycle is already fully proven by Task 4 and does not add end-to-end value here, keep only the first two tests.

- [ ] **Step 2: Run the new integration file and confirm it fails for the expected reason**

Run: `uv run pytest tests/integration/reused/compute/test_async_and_subflows_with_all_engines.py -v --mypy-pyproject-toml-file=pyproject.toml`

Expected: failures reflect not-yet-landed engine-harness or seam work, not missing engine fixtures.

- [ ] **Step 3: Implement the smallest direct scenarios that confirm the harness conclusions**

Use the same patterns already present in `tests/compute/test_flow.py`, especially `result_key`, `param_key_map`, `refine()`, and nested flow calls. Do not build another helper hierarchy here.

- [ ] **Step 4: Re-run the integration file on both production engines**

Run: `uv run pytest tests/integration/reused/compute/test_async_and_subflows_with_all_engines.py -v --mypy-pyproject-toml-file=pyproject.toml`

Expected: the file is green except for intentionally classified engine-specific support gaps.

- [ ] **Step 5: Commit the integration slice**

```bash
git add tests/integration/reused/compute/test_async_and_subflows_with_all_engines.py
git commit -m "test: confirm async subflows in integration"
```

### Task 6: Final verification, support-gap audit, and handoff evidence

**Files:**
- Modify only if cleanup from earlier tasks is needed: files already touched above

- [ ] **Step 1: Run the focused verification stack**

Run: `uv run pytest tests/engine/test_all_engines.py tests/compute/test_flow.py tests/integration/reused/compute/test_async_and_subflows_with_all_engines.py -v --mypy-pyproject-toml-file=pyproject.toml`

Expected: green or explicitly classified support gaps only.

- [ ] **Step 2: Run the broader engine and integration coverage that this slice depends on**

Run: `uv run pytest tests/engine tests/integration/reused/compute/test_flow_with_all_engines.py tests/integration/reused/compute/test_async_and_subflows_with_all_engines.py -v --mypy-pyproject-toml-file=pyproject.toml`

Expected: no unexpected regressions outside the new async/subflow coverage.

- [ ] **Step 3: Run formatting and hook validation**

Run: `uv run pre-commit run --hook-stage manual --all-files`

Expected: pass, or auto-fixes limited to touched files and re-verified immediately.

- [ ] **Step 4: Audit retained support gaps before declaring the slice done**

Record, in the implementation handoff or PR:
- every engine-specific `xfail` and its reason
- every intentionally retained plain failing test and why visible red is preferred
- whether Task 4 was skipped or activated
- which child-flow combinations satisfy the semantic floor

- [ ] **Step 5: Final commit only if Step 3 changed tracked files**

```bash
git add tests/engine tests/compute/test_flow.py tests/integration/reused/compute/test_async_and_subflows_with_all_engines.py src/omnipy/compute/_joblist_job.py src/omnipy/engine/run_spec.py
git commit -m "chore: finalize async subflow test coverage"
```

## Spec-to-plan self-check

- Engine harness is the authority: Tasks 1–3 keep the main expansion in `tests/engine/`.
- Exhaustive 3×4 per production engine: Task 2 is dedicated to it.
- Child tasks and child flows for linear/DAG, including each child flow type overall: Task 3 requires all six parent/child-flow combinations.
- `FuncFlow` body semantics tested separately from terminal-child rules: Task 3 splits “calls tasks” from “calls flows”.
- Compute stays validation-only and optional: Task 4 is gated by red tests.
- Integration remains selective: Task 5 caps the work at two or three direct scenarios.
- No new multithread/multiprocess coverage: none of the tasks touch those paths.
- Support-gap policy stays explicit: Tasks 3, 4, and 6 classify every retained gap.

## Implementation notes for the executing agent

- Prefer reusing `tests/engine/cases/tasks.py` as the source of primitive callable behavior.
- Keep top-level test bodies tiny; move composition detail into `tests/engine/cases/flows.py` and helper builders.
- Do not broaden scope into new flow concepts, new public APIs, or unrelated cleanup.
- If a production seam is needed, make the engine red test and the compute validation test fail first, then implement the seam, then re-run both.
