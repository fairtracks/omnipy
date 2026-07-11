# Async And Sub-Flow Testing Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add engine-first async and nested-flow test coverage with a complete per-production-engine 3×4 parent-flow/callable matrix, child-flow semantic-floor coverage, scenario-based integration tests that can later seed tutorials, and only a narrow production seam if red tests prove one is needed.

**Architecture:** Keep `tests/engine/` as the main authority, but build the new parity cases with real `TaskTemplate`, `LinearFlowTemplate`, `DagFlowTemplate`, and `FuncFlowTemplate` jobs under `LocalRunner` and `PrefectEngine`. Use a concrete `ComposedFlowCase` with a `build_job_func` closure per case so each case owns its topology, routing, and assertions while the helper layer only wires engine, registry, and applied job.

**Tech Stack:** Python, pytest, pytest-cases, asyncio, Omnipy task/flow templates, LocalRunner, PrefectEngine

---

## File map

- Create: `tests/engine/cases/flows.py`
  - Real-engine composed-flow cases, shared assertions, and builder closures for the matrix and semantic-floor coverage.
- Modify: `tests/engine/cases/tasks.py`
  - Add only the new single-thread primitive callables reused by `flows.py`.
- Modify: `tests/engine/helpers/classes.py`
  - Add `ComposedFlowCase` with a concrete `build_job_func` closure.
- Modify: `tests/engine/helpers/functions.py`
  - Add `apply_job()` for shared engine/registry wiring, add `apply_composed_flow_case()`, and widen `run_job_test()` to accept `JobCase | ComposedFlowCase`.
- Modify: `tests/engine/conftest.py`
  - Add production-engine fixtures for matrix cases and semantic-floor cases using real template classes.
- Modify: `tests/engine/test_all_engines.py`
  - Add two thin async parametrized tests that consume the new fixtures.
- Modify only if red tests require it: `tests/compute/test_flow.py`
  - Validation-only callable-type checks for child-flow composition changes during construction, `refine()`, and `revise()`.
- Create: `src/omnipy/compute/helpers.py`
  - Public `Void` helper for generator and async-generator placeholder bodies used by flow templates.
- Modify only if red tests require it: `src/omnipy/compute/_joblist_job.py`
  - Narrow callable-type consistency seam for child-job-list flows.
- Modify only if red tests require it: `src/omnipy/engine/run_spec.py`
  - Narrow async-resolution seam if nested async child flows are intended to work but are not drained consistently.
- Create: `tests/integration/novel/full/test_environmental_monitoring_harmonization.py`
  - Scenario A: mock-GET environmental monitoring harmonization using `Dataset.load()` and Omnipy flattening, returning `samples` and `measurements` as `PandasDataset` members.
- Create: `tests/integration/novel/full/test_sequence_submission_brokering.py`
  - Scenario B+C: typed Dataset-centric submission brokering for `BioSampleVault` and `Sequence Depot`, with JSON-shaped external adapters and final receipt state.
- Create: `tests/integration/novel/full/test_flow_callable_type_validation.py`
  - Separate readable integration coverage for callable-type lifting and `refine()` / `revise()` revalidation interactions.
- Modify or remove: `tests/integration/novel/full/test_async_subflow_scenarios.py`
  - Replace the current mixed showcase with the new split integration coverage; keep no hard-to-follow scenario branching.
- Create as needed under `tests/integration/novel/full/helpers/`
  - Extracted mock aiohttp services, URL fixtures, payload builders, and shared typed models/helpers for the new narrative tests.

## Coverage ledger

- Exhaustive per production engine: `LinearFlow`, `DagFlow`, `FuncFlow` × sync function / sync generator / async coroutine / async generator → **Tasks 2–4**
- Linear and DAG parents with multiple children across the matrix → **Tasks 2–3**
- Child flows of each existing flow type under linear and DAG parents at least once overall → **Tasks 5–6**
- Parent `FuncFlow` bodies that call tasks and separate parent `FuncFlow` bodies that call flows → **Tasks 4 and 7**
- Mixed sync/async composition with async terminal child → **Task 7**
- Nested async support-gap case with explicit expectation handling → **Task 7**
- Nested parameter routing across a parent/child flow boundary → **Tasks 6 and 9**
- Targeted refine/revise case involving child-flow replacement inside a DAG parent → **Tasks 6, 8, and 9**
- Construction-time and child-composition `refine()` / `revise()` callable-type validation exercised by the third integration test → **Tasks 8 and 9**
- Optional compute validation only if red tests prove a seam is needed → **Task 8**
- Selective narrative integration coverage only → **Task 9**

## Acceptance criteria

- `tests/engine/test_all_engines.py::test_flow_matrix_all_production_engines` runs the full 3×4 matrix across `LocalRunner` and `PrefectEngine`.
- `tests/engine/test_all_engines.py::test_nested_flow_semantic_floor_all_production_engines` covers child-flow composition, mixed sync/async behavior, nested routing, and explicit support-gap classification.
- `tests/compute/test_flow.py` only grows if red engine tests prove a callable-type or async-resolution seam.
- `tests/integration/novel/full/` holds three readable integration tests: scenario A, scenario B+C, and a separate callable-type / `refine()` / `revise()` slice, without recreating the engine matrix.
- The third integration test only asserts callable-type validation behavior that already exists or that Task 8 adds as the narrow validation seam; it must not invent a second validation path.
- Final verification is green except for deliberately documented support gaps, preferably expressed as engine-specific `xfail(strict=True)`.

## Support-gap policy for implementation

- Known external engine limitations use engine-specific `pytest.xfail(strict=True)` with a one-line reason.
- Claimed-supported behavior that stays red after investigation uses one narrow committed failing case or `xfail(strict=True)`, chosen deliberately per case.
- Temporary local TDD-red is fine during a slice, but every retained gap must be classified before the slice is handed off.

## Case implementation guidelines

### Case implementation guidelines for `build_job_func` closures

All test cases in `tests/engine/cases/flows.py` must follow these patterns:

1. **Decorator syntax for local functions** — When defining task/flow functions locally, use `@TaskTemplate()`, `@LinearFlowTemplate(...)`, `@DagFlowTemplate(...)`, and `@FuncFlowTemplate()` decorator syntax instead of `SomeTemplate(name='x')(func)`.
2. **No `task_template_cls` variable** — Use the concrete class (`TaskTemplate`, `LinearFlowTemplate`, `DagFlowTemplate`, `FuncFlowTemplate`) directly instead of assigning it to a temporary variable.
3. **Meaningful variable names** — Variable names should describe behavior and align with the task/flow identity, which defaults to the function name when `name=` is omitted.
4. **Naming** — Only pass `name=` when reusing a function under a different identity. Otherwise rely on the function name, and ensure the name truthfully describes what the task/flow does.
5. **`parent` means the flow** — In composed cases, the flow template is the parent; the first child is not the parent. Name variables accordingly.
6. **Tasks and flows must make behavioral sense** — Mix sync and async tasks within the same flow when the case is testing mixed-mode composition, ensure DAG branches actually change the result so routing is real, ensure async tasks actually use `async`/`await`, and keep names truthful about sync vs async behavior.
7. **Spacing and comments** — Use blank lines between logical sections such as `# Tasks` and `# DAG Flow`, and keep comments readable enough that each closure's topology is easy to scan.
8. **Helper for common engine wiring** — Replace the repeated engine/registry/apply pattern with a shared helper such as `apply_job(template, engine, registry)` instead of inlining:

   ```python
   cast(HasJobCreator, TaskTemplate).job_creator.set_engine(engine)
   if registry:
       engine.set_registry(registry)
   return template.apply()
   ```
9. **Generator placeholder bodies** — For flow templates whose body exists only to define a generator or async-generator callable signature, use the public `Void()` helper instead of `if False: yield ...`:

   Sync generator:
   ```python
   yield from Void()  # For generator signature only; never run.
   ```

   Async generator:
   ```python
   async for _ in Void():  # For generator signature only; never run.
       yield _
   ```

   Import `Void` from `omnipy`:
   ```python
   from omnipy import Void
   ```

## Constraints

- Keep `tests/engine/` as the primary authority for this slice.
- Use real template classes under real production engines; do not fall back to mock-only flow-template coverage for nested composition.
- Add new primitive callables in `tests/engine/cases/tasks.py`, not `tests/engine/cases/raw/functions.py`.
- Keep top-level tests tiny; put topology in `tests/engine/cases/flows.py` and fixture plumbing in `tests/engine/conftest.py`.
- Do not broaden this slice into multithread or multiprocess coverage.
- If Task 8 activates, make the compute test fail first and the engine case fail first before changing production code.

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

- [ ] Add two thin async parametrized engine tests: one for the 3×4 matrix fixture family and one for the semantic-floor fixture family.
- [ ] Introduce `ComposedFlowCase`, `apply_composed_flow_case()`, and the fixture wiring needed to build real template-based jobs under a supplied engine and registry.
- [ ] Keep helper responsibility narrow: engine injection, registry wiring, and applied-job creation only.
- [ ] Run: `uv run pytest tests/engine/test_all_engines.py -v --mypy-pyproject-toml-file=pyproject.toml`
  - Expected first red: missing fixture and/or missing case definitions.
- [ ] Re-run the same command after scaffolding.
  - Expected next red: only missing case implementations or genuine async/subflow behavior gaps.

### Task 2: Add the four linear-parent matrix cases

**Files:**
- Modify: `tests/engine/cases/tasks.py`
- Modify: `tests/engine/cases/flows.py`
- Test: `tests/engine/test_all_engines.py`

- [ ] Add or reuse the primitive single-thread callables needed for linear-parent coverage: sync function, sync generator, async coroutine, and async generator terminal behavior.
- [ ] Add the four linear-parent cases in `tests/engine/cases/flows.py` and keep each case responsible for its builder closure, callable-type expectation, and result assertion.
- [ ] Ensure the linear-parent matrix uses multiple children where needed so the terminal child really determines the exposed callable type.
- [ ] Run: `uv run pytest tests/engine/test_all_engines.py -k "linear-flow" -v --mypy-pyproject-toml-file=pyproject.toml`
  - Expected: all four linear matrix cases execute across both production engines; any remaining red is specific to unsupported behavior, not missing scaffolding.

### Task 3: Add the four DAG-parent matrix cases

**Files:**
- Modify: `tests/engine/cases/flows.py`
- Test: `tests/engine/test_all_engines.py`

- [ ] Add the four DAG-parent cases so the full callable matrix exists for `DagFlow` as well.
- [ ] Use real DAG routing, including `result_key` handling where needed, rather than test-only shortcuts.
- [ ] Keep assertions focused on callable type, result propagation, and run-state expectations.
- [ ] Run: `uv run pytest tests/engine/test_all_engines.py -k "dag-flow" -v --mypy-pyproject-toml-file=pyproject.toml`
  - Expected: all four DAG matrix cases execute across `LocalRunner` and `PrefectEngine`; any remaining red is an actual behavior gap.

### Task 4: Add the four `FuncFlow` matrix cases whose bodies call tasks

**Files:**
- Modify: `tests/engine/cases/flows.py`
- Test: `tests/engine/test_all_engines.py`

- [ ] Add four `FuncFlow` parent cases whose bodies call tasks and expose the four callable outcomes: sync function, sync generator, async coroutine, and async generator.
- [ ] Keep these cases separate from Task 7 so the matrix remains focused on task-calling `FuncFlow` bodies.
- [ ] Run: `uv run pytest tests/engine/test_all_engines.py::test_flow_matrix_all_production_engines -v --mypy-pyproject-toml-file=pyproject.toml`
  - Expected: the complete 3×4 matrix now runs across both production engines; any red is a real semantic gap rather than a missing matrix entry.

### Task 5: Add the linear-parent child-flow semantic-floor cases

**Files:**
- Modify: `tests/engine/cases/flows.py`
- Test: `tests/engine/test_all_engines.py`

- [ ] Add one linear parent with a child `LinearFlow`, one with a child `DagFlow`, and one with a child `FuncFlow`.
- [ ] Keep these cases representative rather than exhaustive; their job is to establish the child-flow semantic floor for linear parents.
- [ ] Reuse the shared assertion helpers from `tests/engine/cases/flows.py` so these cases only describe topology and expected behavior.
- [ ] Run: `uv run pytest tests/engine/test_all_engines.py -k "linear-parent-child" -v --mypy-pyproject-toml-file=pyproject.toml`
  - Expected: all three linear-parent child-flow cases run across both production engines.

### Task 6: Add the DAG-parent child-flow, routing, and child-flow refine/revise semantic-floor cases

**Files:**
- Modify: `tests/engine/cases/flows.py`
- Test: `tests/engine/test_all_engines.py`

- [ ] Add one DAG parent with a child `LinearFlow`, one with a child `DagFlow`, and one with a child `FuncFlow`.
- [ ] Add a nested parameter-routing case that proves `param_key_map` and `result_key` work across a parent/child flow boundary.
- [ ] Add a targeted refine/revise case where a DAG parent replaces one child flow with another and still reports the correct behavior.
- [ ] Run: `uv run pytest tests/engine/test_all_engines.py -k "dag-parent" -v --mypy-pyproject-toml-file=pyproject.toml`
  - Expected: DAG parent child-flow, routing, and refine/revise cases all execute; any retained red is explicit and intentional.

### Task 7: Add `FuncFlow`-body-calls-flows, mixed sync/async, and nested async support-gap cases

**Files:**
- Modify: `tests/engine/cases/flows.py`
- Test: `tests/engine/test_all_engines.py`

- [ ] Add one parent `FuncFlow` case whose body calls a child flow, distinct from the task-calling matrix cases in Task 4.
- [ ] Add one mixed sync/async case where a parent flow ends in an async child flow and must expose async callable semantics.
- [ ] Add one nested async support-gap case and classify it explicitly per the support-gap policy.
- [ ] If these cases point to a production seam, stop at **User Check-in A** before changing `src/`.
- [ ] Run: `uv run pytest tests/engine/test_all_engines.py::test_nested_flow_semantic_floor_all_production_engines -v --mypy-pyproject-toml-file=pyproject.toml`
  - Expected: semantic-floor coverage now includes child-flow `FuncFlow`, mixed sync/async composition, and one explicit nested async support-gap classification.

### Task 8: Add validation-only compute coverage and a narrow production seam only if red tests prove one is needed

**Ownership note:** Task 8 owns any construction-time or `refine()` / `revise()` callable-type validation routines later exercised readably by Task 9's third integration test. If Task 9 reveals that the validation behavior itself is missing, route that gap back here rather than adding a second validation seam in integration-only code.

**Files:**
- Modify: `tests/compute/test_flow.py`
- Modify only if needed: `src/omnipy/compute/_joblist_job.py`
- Modify only if needed: `src/omnipy/engine/run_spec.py`
- Test: `tests/compute/test_flow.py`
- Test: `tests/engine/test_all_engines.py`

- [ ] Add focused compute tests only if Tasks 6–7 or the Task 9 validation slice expose a callable-type or async-resolution inconsistency.
- [ ] Cover three validation points at most: construction-time callable-type lifting, `refine()` revalidation, and `revise()` revalidation.
- [ ] Pause at **User Check-in A** before any production edit.
- [ ] If needed, implement only the smallest seam in `ChildJobListArgJobBase` or `run_spec` that makes the existing intended behavior explicit.
- [ ] Run: `uv run pytest tests/compute/test_flow.py -k "child_flow_callable_type or refine_rechecks or revise_rechecks" -v --mypy-pyproject-toml-file=pyproject.toml`
  - Expected: failure, if any, points to the narrow seam rather than unrelated flow behavior.
- [ ] Re-run after the seam, if activated: `uv run pytest tests/compute/test_flow.py tests/engine/test_all_engines.py -v --mypy-pyproject-toml-file=pyproject.toml`
  - Expected: compute coverage is green and engine coverage is green or explicitly classified.

### Task 9: Replaced by standalone integration-test slice plan

**Replacement notice:** Task 9 is fully replaced by `docs/superpowers/plans/2026-07-11-async-and-sub-flow-integration-test-slice-plan.md`.

Treat that document as the canonical implementation authority for:
- Scenario A: environmental monitoring harmonization
- Scenario B+C: sequence submission brokering
- Separate callable-type / `refine()` / `revise()` validation coverage

The binding requirements source remains `docs/superpowers/specs/2026-07-09-async-and-sub-flow-testing-schema-design.md`. Any other references to “Task 9” in this plan now mean the replacement plan above.

### Task 10: Final verification, support-gap audit, and handoff evidence

**Files:**
- Modify only if cleanup from earlier tasks is needed: files already touched above

- [ ] Run the focused verification stack: `uv run pytest tests/engine/test_all_engines.py tests/compute/test_flow.py tests/integration/novel/full/test_environmental_monitoring_harmonization.py tests/integration/novel/full/test_sequence_submission_brokering.py tests/integration/novel/full/test_flow_callable_type_validation.py -v --mypy-pyproject-toml-file=pyproject.toml`
  - Expected: green or explicitly classified support gaps only.
- [ ] Run the broader dependency coverage: `uv run pytest tests/engine tests/integration/reused/compute/test_flow_with_all_engines.py tests/integration/novel/full/test_environmental_monitoring_harmonization.py tests/integration/novel/full/test_sequence_submission_brokering.py tests/integration/novel/full/test_flow_callable_type_validation.py -v --mypy-pyproject-toml-file=pyproject.toml`
  - Expected: no unexpected regressions outside the new async/subflow slice.
- [ ] Run formatting and hook validation: `uv run pre-commit run --hook-stage manual --all-files`
  - Expected: pass, or auto-fixes limited to touched files and re-verified immediately.
- [ ] Record the retained-gap audit in the handoff or PR:
  - every engine-specific `xfail` and its reason
  - every intentionally retained plain failing test and why visible red is preferred
  - whether Task 8 was skipped or activated
  - which linear-parent and DAG-parent child-flow cases satisfy the semantic floor
  - which case proves child-flow refine/revise replacement

## Spec-to-plan self-check

- The engine harness remains the main authority, but parity cases use real templates under production engines rather than mock-only flow templates.
- The full 3×4 matrix is explicit and split across Tasks 2–4.
- Linear and DAG parents each get child-flow coverage for `LinearFlow`, `DagFlow`, and `FuncFlow` in Tasks 5–6.
- `FuncFlow` task-body semantics are covered in Task 4; `FuncFlow` body-calls-flow semantics are covered in Task 7.
- Nested parent/child routing is covered in Task 6 and complemented by Scenario A and the callable-type integration slice in Task 9.
- A targeted child-flow refine/revise replacement case is required in Task 6, while Task 9 now isolates the readable integration-level callable-type / `refine()` / `revise()` story rather than folding it into a mixed showcase.
- The validation routines touched by the third integration test were already defined in the earlier plan through Task 8's construction + `refine()` / `revise()` callable-type seam; this update only makes that dependency explicit so Task 9 cannot drift into inventing new validation work.
- Compute coverage stays validation-only and optional in Task 8.
- The plan keeps `tests/engine/cases/tasks.py` as the main primitive-callable source for new flow-case primitives.
- Support-gap handling stays explicit through Tasks 7, 8, 9, and 10.
