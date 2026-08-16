# Async Compute-Mixins Test Extension Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a small async-focused compute-mixins test extension that first lands representative tests for the highest-risk async/mixin-order scenarios, reports any failures, and pauses for manual review before any production fixes.

**Architecture:** Keep `tests/compute/mixins/test_mixin_integration.py` as the main behavioral surface for curated cross-mixin scenarios, and keep `tests/integration/novel/serialize/test_serialize.py` as the serialization authority because persistence requires runtime-backed integration coverage. Reuse existing task/flow/helper patterns and add only a representative mini-matrix that stresses `serialize`, `auto_async`, `iterate`, `params`, and `result_key` where the current mixin order is most brittle.

**Tech Stack:** Python, pytest, pytest-cases, asyncio/anyio, Omnipy `TaskTemplate` / `FuncFlowTemplate` / `LinearFlowTemplate` / `DagFlowTemplate`, runtime-backed serialization fixtures

**Spec:** `docs/superpowers/specs/2026-08-16-async-compute-mixins-test-extension-design.md`

## Global Constraints

- First pass is **test-only**: add tests, run them, report failures and suggested fixes in chat, and stop before touching `src/`.
- Keep the new async slice representative rather than exhaustive; do not attempt the full callable-type × job-type × mixin matrix.
- Cover all four job types at least once in the new async slice: `Task`, `FuncFlow`, `LinearFlow`, and `DagFlow`.
- Explicitly test the supported `serialize` + `result_key` composition instead of treating it as an excluded combination.
- Verify at least one top-level `auto_async` scenario both without a running event loop and inside an already-running event loop.
- Add explicit sync-generator and async-generator representatives where outward return/yield shape is part of the risk.
- Keep serialize coverage in `tests/integration/novel/serialize/test_serialize.py`; do not create a parallel serialize harness under `tests/compute/`.
- Audit nearby sync coverage and add only the smallest missing sync sentinel if a real adjacent gap remains.
- Preserve the selected callable-type × job-type matrix in the implementation notes/report so the omitted cells stay explicit.

---

## File map

- Modify: `tests/compute/mixins/test_mixin_integration.py`
  - Add the curated async mixin-interaction tests for linear-flow, DAG-flow, generator-sensitive, and dense-compatible-mixin scenarios.
- Modify: `tests/integration/novel/serialize/test_serialize.py`
  - Add runtime-backed async serialize integration coverage for the top-level task path and the flow-context awaitable path.
- Modify only if the new tests become materially clearer by reusing helpers instead of local inline callables:
  - `tests/compute/cases/raw/functions.py`
  - `tests/integration/novel/serialize/cases/functions.py`
  - `tests/integration/novel/serialize/cases/jobs.py`
- Modify only if the sync-gap audit finds a nearby callable-type or generator-shape hole that belongs with existing flow construction assertions:
  - `tests/compute/test_flow.py`

## Selected representative matrix for this implementation slice

| Callable type \ Job type | Task | Func flow | Linear flow | Dag flow |
| --- | --- | --- | --- | --- |
| Sync function | Audit existing coverage; add only if the sync-gap audit finds a real nearby hole | Audit existing coverage; add only if the sync-gap audit finds a real nearby hole | Audit existing coverage; add only if the sync-gap audit finds a real nearby hole | Audit existing coverage; add only if the sync-gap audit finds a real nearby hole |
| Sync generator | Not required in the first serialize slice | Add only if needed to keep generator assertions symmetric | Covered by generator-sensitive terminal-child sentinel | Covered by generator-sensitive routing/result sentinel |
| Async coroutine | Covered by `serialize` + `result_key` + `auto_async` task in both loop contexts | Covered by `serialize` + `result_key` flow-context awaitable path | Covered by representative `iterate` + `auto_async` dataset transform case | Covered by representative `params` + `result_key` non-dataset case |
| Async generator | Add only if needed to keep task helper symmetry | Add only if needed to keep generator assertions symmetric | Covered by generator-sensitive terminal-child sentinel | Covered by generator-sensitive routing/result sentinel |

## Tasks

### Task 1: Add the representative async compute-mixins behavioral slice

**Test level:** Behavioral integration-style tests at the compute layer. These tests should pin down observable job/flow behavior, not internal helper implementation details.

**Files:**
- Modify: `tests/compute/mixins/test_mixin_integration.py`
- Modify only if repeated helper callables make the test file noisy: `tests/compute/cases/raw/functions.py`
- Modify only if the sync-gap audit belongs with existing flow callable-type assertions: `tests/compute/test_flow.py`

**Consumes:**
- Existing mixin/public construction surfaces from:
  - `omnipy.compute.task.TaskTemplate`
  - `omnipy.compute.flow.FuncFlowTemplate`
  - `omnipy.compute.flow.LinearFlowTemplate`
  - `omnipy.compute.flow.DagFlowTemplate`
- Existing representative compute helpers already present in:
  - `tests/compute/cases/raw/functions.py`
  - `tests/compute/mixins/test_auto_async.py`
  - `tests/compute/test_flow.py`

**Produces:**
- One async `LinearFlow` representative that stresses `iterate_over_data_files` + `auto_async` on a dataset-returning path.
- One async `DagFlow` representative that stresses `fixed_params` and/or `param_key_map` together with `result_key` on a non-dataset path.
- One dense compatible-mixin representative that stacks as many honest, compatible modifiers as possible in a single async scenario.
- One parameterized generator-sensitive sentinel that exercises both sync-generator and async-generator outward shapes where mixin order can leak into the public result.
- A short sync-gap audit note in comments or naming, and exactly one sync backfill only if the audit finds a nearby uncovered invariant.

- [ ] **Step 1: Add the selected async behavioral tests before adding new helpers**

Write the new tests in `tests/compute/mixins/test_mixin_integration.py` first so the public contracts are fixed before any helper extraction. Keep the new section visibly mapped to the spec scenarios: linear-flow iterate/auto-async, DAG params/result-key, dense compatible stack, and generator-sensitive sentinels.

Representative test sketch:

```python
@pytest.mark.anyio
@pytest.mark.parametrize('generator_kind', ['sync', 'async'])
async def test_async_linear_flow_iterate_auto_async_preserves_generator_sensitive_output(
    generator_kind: str,
) -> None:
    ...


@pytest.mark.anyio
async def test_async_dag_flow_params_and_result_key_preserve_public_non_dataset_shape() -> None:
    ...
```

- [ ] **Step 2: Run only the new compute-mixins tests to verify the intended red state**

Run one or more focused commands that target only the newly added tests.

Run:

```bash
uv run pytest tests/compute/mixins/test_mixin_integration.py -v --mypy-pyproject-toml-file=pyproject.toml
```

Expected on the first run: the new assertions fail because current async mixin behavior is still unproven and may still contain the regressions described in the spec.

- [ ] **Step 3: Add the smallest helper callables needed to express the tests cleanly**

Prefer tiny local callables inside the test file. Only move helpers into `tests/compute/cases/raw/functions.py` if at least two tests need the same callable shape. Do not create a new helper subsystem.

If helper extraction is needed, keep it to the smallest possible surface, for example:

```python
async def async_dataset_transform(...):
    ...


def sync_generator_terminal(...):
    yield ...


async def async_generator_terminal(...):
    yield ...
```

- [ ] **Step 4: Re-run the compute slice and stop if failures point into `src/`**

Run the focused command again after the tests and any helper extraction are in place.

Run:

```bash
uv run pytest tests/compute/mixins/test_mixin_integration.py -v --mypy-pyproject-toml-file=pyproject.toml
```

If failures now point to `src/omnipy/compute/_func_job.py`, `src/omnipy/compute/_mixins/auto_async.py`, `src/omnipy/compute/_mixins/result_key.py`, or `src/omnipy/compute/_mixins/params.py`, record them for the later fix phase and do not patch production code yet.

- [ ] **Step 5: Run the adjacent sync-gap audit command**

Run the nearest existing tests that should already protect the sync side of the same invariants. Add exactly one sync sentinel only if that run shows the async slice would otherwise leave a real neighboring hole.

Run:

```bash
uv run pytest tests/compute/mixins/test_auto_async.py tests/compute/mixins/test_iterate.py tests/compute/test_flow.py -v --mypy-pyproject-toml-file=pyproject.toml
```

### Task 2: Add the async serialize integration slice

**Test level:** Integration/contract tests with real runtime-backed persistence behavior.

**Files:**
- Modify: `tests/integration/novel/serialize/test_serialize.py`
- Modify only if shared fixtures make the new tests materially clearer:
  - `tests/integration/novel/serialize/cases/functions.py`
  - `tests/integration/novel/serialize/cases/jobs.py`

**Consumes:**
- Existing serialize runtime fixtures from `tests/conftest.py`
- Existing serialize data fixtures from `tests/integration/novel/serialize/cases/datasets.py`
- Existing serialize job/case patterns from `tests/integration/novel/serialize/cases/functions.py` and `tests/integration/novel/serialize/cases/jobs.py`
- The persistence behavior in `src/omnipy/compute/_mixins/serialize.py`

**Produces:**
- One async `Task` coverage point for `persist_outputs='enabled'` + `result_key` + `auto_async=True`, executed both outside an event loop and inside an already-running event loop with the same behavioral assertions.
- One async `FuncFlow` coverage point for `serialize` + `result_key` inside flow context, exercising the non-`asyncio.Task` awaitable persistence path.
- Assertions that the outward return value is result-key wrapped while the persisted tarball still represents the underlying dataset result.
- A small helper for discovering the newly persisted tarball from `runtime.config.job.output_storage.local.persist_data_dir_path` without depending on an exact timestamp string.

- [ ] **Step 1: Write the async serialize tests first**

Start in `tests/integration/novel/serialize/test_serialize.py` with the two high-value scenarios from the spec: top-level async task in both loop contexts, and async function-flow in flow context.

Representative test sketch:

```python
def test_async_task_serialize_then_result_key_without_running_loop(...) -> None:
    ...


@pytest.mark.anyio
async def test_async_task_serialize_then_result_key_inside_running_loop(...) -> None:
    ...


@pytest.mark.anyio
async def test_async_func_flow_serialize_then_result_key_in_flow_context(...) -> None:
    ...
```

- [ ] **Step 2: Run the serialize file to verify the intended red state**

Run:

```bash
uv run pytest tests/integration/novel/serialize/test_serialize.py -v --mypy-pyproject-toml-file=pyproject.toml
```

Expected on the first run: the new tests fail if async result persistence or `serialize`/`result_key` composition still regresses.

- [ ] **Step 3: Add only the minimal shared fixture/case support needed by the new tests**

If the new tests are clearer with reusable factories, extend the existing serialize case modules rather than inventing new directories. Keep the async shape explicit in names such as `async_*_func` or `async_*_flow_tmpl` so the new coverage is easy to audit later.

Suggested helper shape if extraction is needed:

```python
@pytest.fixture
def async_json_dataset_func(...) -> Callable[[], JsonDataset]:
    async def _async_json_dataset_func() -> JsonDataset:
        ...
    return _async_json_dataset_func
```

- [ ] **Step 4: Assert both outward result shape and persisted artifact shape**

Each new serialize test should make both contracts explicit:

```python
assert result == {'wrapped_key': expected_dataset_or_payload}
assert discovered_tar_files == ['00_expected_job_name.tar.gz']
assert restored_dataset.to_data() == expected_dataset.to_data()
```

Do not hard-code the timestamp directory name. Discover the created tarball by walking `runtime.config.job.output_storage.local.persist_data_dir_path` and asserting one new `.tar.gz` file for the selected job.

- [ ] **Step 5: Re-run the serialize slice and stop if the failures are in production code**

Run:

```bash
uv run pytest tests/integration/novel/serialize/test_serialize.py -v --mypy-pyproject-toml-file=pyproject.toml
```

If failures now point to the `asyncio.Task` callback path or generic awaitable path in `src/omnipy/compute/_mixins/serialize.py`, record them for the fix phase and stop there.

### Task 3: Execute the first-pass verification run and prepare the manual-review handoff

**Files:**
- No new files required.
- Modify existing test files only if small assertion cleanup is required to make the intended contract readable.

**Consumes:**
- The new tests from Tasks 1 and 2.

**Produces:**
- A pass/fail report grouped by representative scenario.
- A concise suggested-fix list keyed to likely production files.
- An explicit user check-in before any production change.

- [ ] **Step 1: Run the full first-pass test slice**

Run:

```bash
uv run pytest \
  tests/compute/mixins/test_mixin_integration.py \
  tests/integration/novel/serialize/test_serialize.py \
  -v --mypy-pyproject-toml-file=pyproject.toml
```

If Task 1 needed a sync sentinel in `tests/compute/test_flow.py`, add that file to this verification command as well.

- [ ] **Step 2: Summarize outcomes by scenario instead of by traceback order**

Prepare a short report with one line each for:

- async task `serialize` + `result_key` + `auto_async` (no running loop)
- async task `serialize` + `result_key` + `auto_async` (running loop)
- async function-flow `serialize` + `result_key` in flow context
- async linear-flow `iterate` + `auto_async`
- async DAG `params` + `result_key`
- sync-generator sentinel
- async-generator sentinel
- dense compatible-mixin representative

- [ ] **Step 3: Suggest fixes, but do not implement them yet**

For each failing scenario, suggest the smallest likely production change and the most likely file, for example:

- `src/omnipy/compute/_mixins/serialize.py` for `asyncio.Task` callback vs generic awaitable persistence behavior
- `src/omnipy/compute/_func_job.py` for mixin-order regressions
- `src/omnipy/compute/_mixins/auto_async.py` for top-level vs flow-context auto-execution behavior
- `src/omnipy/compute/_mixins/result_key.py` / `params.py` for outward wrapping or remapping order

- [ ] **Step 4: Stop for the required User Check-in**

Do not touch `src/` after the first-pass run. Present the pass/fail report and suggested fixes in chat, then wait for explicit approval before starting any production fix work.

### Task 4: Apply the post-review production fixes (only after explicit user approval)

**Do not start this task until the user explicitly approves moving past the first-pass report.**

**Files:**
- Modify only the smallest necessary production files indicated by the first-pass failures, most likely one or more of:
  - `src/omnipy/compute/_func_job.py`
  - `src/omnipy/compute/_mixins/serialize.py`
  - `src/omnipy/compute/_mixins/auto_async.py`
  - `src/omnipy/compute/_mixins/result_key.py`
  - `src/omnipy/compute/_mixins/params.py`
- Modify touched tests only when the production fix requires tightening the same contract, not broadening scope.

**Consumes:**
- The failing tests and suggested-fix inventory from Task 3.

**Produces:**
- Minimal production fixes that make the approved failing tests pass.
- A mandatory refactor checkpoint with no behavior change.
- Fresh verification evidence on the targeted and adjacent suites.

- [ ] **Step 1: Re-run the specific failing test before each production change**

Use the narrowest failing-node command first so the red state stays proven.

- [ ] **Step 2: Apply the smallest production fix that matches the observed failure**

Keep changes surgical. Do not widen the matrix beyond the approved representative subset.

- [ ] **Step 3: Re-run the failing test, then the focused slice, then the adjacent regression slice**

Run:

```bash
uv run pytest \
  tests/compute/mixins/test_auto_async.py \
  tests/compute/mixins/test_iterate.py \
  tests/compute/mixins/test_mixin_integration.py \
  tests/compute/test_flow.py \
  tests/integration/novel/serialize/test_serialize.py \
  -v --mypy-pyproject-toml-file=pyproject.toml
```

- [ ] **Step 4: Perform the mandatory refactor checkpoint and verify green again**

Review the changed slice for naming, duplication, and boundary clarity. If no refactor is needed, record that conclusion explicitly. Then rerun the same focused command.

- [ ] **Step 5: Run the repo-wide formatting/lint gate for the touched files before final handoff**

Run:

```bash
uv run pre-commit run --hook-stage manual --all-files
```

## User Check-in markers

- **User Check-in A:** After Task 3's first-pass test run and failure inventory, before any production code change.
- **User Check-in B:** During Task 4, if the smallest plausible fix would require broadening the selected matrix, changing supported public behavior, or altering callable-type rules outside the approved slice.

## Spec-to-plan self-check

- The plan keeps the first pass test-only and explicitly stops for manual review before any production fix.
- The plan covers all four job types in the new async slice: task + function flow in serialize integration, linear flow + DAG flow in compute mixin behavior tests.
- The plan makes `serialize` + `result_key` a required supported scenario in both top-level and flow-context async cases.
- The plan preserves the loop/no-loop `auto_async` requirement using the same task behavior in both contexts.
- The plan includes explicit sync-generator and async-generator representatives where outward shape is the risk.
- The plan keeps sync-function coverage audit-only unless a real adjacent gap is found.
- The plan keeps helper changes small and reuses existing test surfaces instead of creating a new harness.
- The plan names the likely production files for later fixes without steering the implementer to patch them before the required red-state review.

Plan complete and saved to `docs/superpowers/plans/2026-08-16-async-compute-mixins-test-extension-plan.md`. Two execution options:

1. Subagent-Driven (recommended) - I dispatch a fresh subagent per task, review between tasks, fast iteration

2. Inline Execution - Execute tasks in this session using executing-plans, batch execution with checkpoints

Which approach?
