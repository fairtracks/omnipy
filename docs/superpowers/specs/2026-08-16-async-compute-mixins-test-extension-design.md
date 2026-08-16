# Async Compute-Mixins Test Extension Design

## Summary

Add a small, representative async-focused test extension for compute mixins in `omnipy`.
The new coverage should target the two recently untested risk areas called out by the user:

- commit `48906e4a9a38ff1fe8b0fa77b9afbea19cf7f921` (`serialize` support for async jobs)
- commit `a2d700631f24bdd2d99e4bdf3f34594d7a6b828a` (mixin reorder in `FuncArgJobBase`)

The extension should reuse existing test infrastructure and add only a carefully chosen subset of
async task/flow cases that are most likely to fail if async mixin composition regresses again.

## Goals

- Catch regressions in async compute-mixin behavior without attempting a full cartesian matrix.
- Cover all four job types at least once in the new async slice: `Task`, `FuncFlow`,
  `LinearFlow`, and `DagFlow`.
- Put slightly more weight on `serialize` and `auto_async`, while still spreading coverage across
  other order-sensitive mixins.
- Exercise the mixin interactions most exposed by the current order in
  `src/omnipy/compute/_func_job.py`:
  - `SerializerFuncJobBaseMixin`
  - `AutoAsyncJobBaseMixin`
  - `IterateFuncJobBaseMixin`
  - `ParamsFuncJobBaseMixin`
  - `ResultKeyFuncJobBaseMixin`
- Explicitly document which callable-type × job-type cells are covered and which are deliberately
  omitted.
- Keep the first implementation pass test-only: add tests, run them, report failures and suggested
  fixes in chat, and stop for manual review before any production fix work.

## Non-goals

- No attempt to cover every callable-type × job-type × mixin combination.
- No production code fixes in the first pass.
- No new flow-context integration slice beyond what is already exercised naturally by the selected
  flow cases.
- No broad engine-harness expansion in this slice.
- No attempt to turn this into a comprehensive async-generator test program.

## Current context

### Existing risk points in production code

- `src/omnipy/compute/_func_job.py` composes callable mixins in a specific order and warns that the
  order dependencies may not be fully tested.
- `src/omnipy/compute/_mixins/serialize.py` has separate persistence paths for:
  - plain synchronous dataset results
  - `asyncio.Task` results
  - generic awaitable results
- `src/omnipy/compute/_mixins/auto_async.py` only auto-runs coroutine functions, and it suppresses
  top-level auto-execution while the job is inside flow context.

### Current coverage gaps

- `tests/compute/mixins/test_auto_async.py` verifies only basic sync-vs-async task behavior and
  does not combine `auto_async` with `serialize`, `iterate`, `params`, or `result_key`.
- `tests/compute/mixins/test_mixin_integration.py` currently covers only sync-oriented mixin
  interactions.
- `tests/integration/novel/serialize/test_serialize.py` exercises serialize behavior for existing
  task/flow fixtures, but not for async jobs.
- Reusable async flow cases already exist elsewhere in the repo, but they do not currently serve as
  direct regression coverage for the compute-mixin order and async serialization paths above.

## Design

### Files likely to change

Primary expected test surfaces:

- `tests/compute/mixins/test_mixin_integration.py`
- `tests/integration/novel/serialize/test_serialize.py`

Likely supporting fixtures/helpers if the existing ones are insufficient:

- `tests/integration/novel/serialize/cases/functions.py`
- `tests/integration/novel/serialize/cases/jobs.py`
- `tests/compute/cases/raw/functions.py`

The design should prefer extending existing fixture/case modules over creating new parallel test
subsystems.

### Coverage-selection principles

1. **Bias toward order-sensitive async paths.**
   Prefer cases that would fail if `serialize`, `auto_async`, `iterate`, `params`, or
   `result_key` execute in the wrong order.

2. **Cover each job type once before deepening any one job type.**
   The new slice should touch task, function flow, linear flow, and DAG flow before adding more
   variants of the same shape.

3. **Use dataset-returning async jobs for serialize coverage.**
   `serialize` is only meaningful when the job returns a dataset, so the serialize-heavy cases
   should stay dataset-based.

4. **Keep one non-dataset async case.**
   Include one targeted async case whose value is mixin interaction rather than persistence,
   especially for `params` and `result_key`.

5. **Prefer one dense compatible-mixin case over many thin near-duplicates.**
   At least one selected test should intentionally stack as many compatible mixins as possible.

### Selected representative subset

The planned spec should drive a subset with the following intent.

#### A. Async task + serialize + auto_async

Add one async dataset-returning task integration case that persists outputs under a running event
loop.

Why this matters:

- top-level async tasks are the clearest way to hit the `asyncio.Task` persistence callback path in
  `SerializerFuncJobBaseMixin`
- this directly guards the behavior fixed by commit `48906e4a...`
- it also verifies that `AutoAsyncJobBaseMixin` and `SerializerFuncJobBaseMixin` cooperate in the
  intended order

#### B. Async function flow + serialize in flow context

Add one async dataset-returning `FuncFlow` serialize case.

Why this matters:

- inside flow context, auto-async should not eagerly consume the coroutine at the outer boundary
- this should exercise the non-`Task` awaitable path in `SerializerFuncJobBaseMixin`
- it confirms that serialize support works both outside and inside flow context

#### C. Async linear flow + iterate + auto_async

Add one async `LinearFlow` case whose terminal child uses dataset iteration semantics.

Why this matters:

- this is the strongest representative for the `AutoAsyncJobBaseMixin` →
  `IterateFuncJobBaseMixin` ordering risk
- it spreads coverage away from serialize-only assertions
- it gives the slice one concrete async dataset transformation flow rather than only persistence
  checks

#### D. Async DAG flow + params/result_key (non-dataset)

Add one async `DagFlow` case that emphasizes `fixed_params` and/or `param_key_map` together with
  `result_key` on a non-dataset result.

Why this matters:

- it covers DAG flow in the new async slice
- it adds the requested non-dataset case
- it exercises the `params`/`result_key` ordering relationship without involving serialize

#### E. One maximal compatible-mixin case

Include one intentionally dense async test that combines as many compatible mixins as possible.

Recommended shape:

- async task or async linear-flow case
- `iterate_over_data_files=True`
- `auto_async=True`
- `fixed_params`
- `param_key_map`
- output-dataset option (`output_dataset_param` or `output_dataset_cls`)
- serialize enabled if the return contract remains dataset-shaped

Important constraint:

`serialize` and `result_key` should not be forced into the same test if doing so changes the return
contract away from a dataset and makes the test artificial. In that case, the dense mixin case may
exclude `result_key`, while the non-dataset DAG case above covers `result_key` separately.

### Callable-type × job-type matrix for this slice

This table is for the **new async extension work**, not for overall historical repo coverage.

| Callable type \ Job type | Task | Func flow | Linear flow | Dag flow |
| --- | --- | --- | --- | --- |
| Sync function | Omitted — already well covered by existing compute/serialize tests and not the async regression target | Omitted — same rationale | Omitted — same rationale | Omitted — same rationale |
| Sync generator | Omitted — lower value than async-coroutine cases for the two named commits | Omitted — lower value than async-coroutine cases | Omitted — lower value than async-coroutine cases | Omitted — lower value than async-coroutine cases |
| Async coroutine | **Covered** — serialize + auto_async dataset task | **Covered** — serialize + flow-context awaitable path | **Covered** — iterate + auto_async representative flow | **Covered** — params/result_key non-dataset representative flow |
| Async generator | Omitted — `auto_async` does not target async-generator callables, and serialize coverage is better spent on dataset-returning coroutine jobs | Omitted — same rationale | Omitted — same rationale | Omitted — same rationale |

### Why the omitted cells are acceptable

- The user requested a representative subset rather than exhaustive coverage.
- The two named risky commits are both more directly exercised by async-coroutine cases than by
  sync or async-generator cases.
- Async-generator behavior is not ignored globally in the repo, but it is intentionally not the
  best value-per-test target for this specific compute-mixin extension.
- Existing sync coverage already protects many non-async invariants, so the new slice should spend
  its budget on the async gaps instead.

## First-pass execution policy

### Required first pass

The first implementation pass must:

- add the selected tests
- run the relevant test subset
- report all failing tests in chat
- include suggested fixes in chat
- stop for user review before changing production code

### Forbidden in the first pass

- no production bug fixes
- no opportunistic refactors
- no broadening of the selected test matrix without a follow-up approval

## Acceptance criteria

The design is satisfied when the later implementation plan produces a first-pass test slice with
all of the following properties:

- new async coverage exists for all four job types: task, function flow, linear flow, and DAG flow
- serialize coverage includes both:
  - one top-level async task path
  - one async flow-context path
- the non-serialize spread includes:
  - one `iterate`-sensitive async case
  - one `params`/`result_key`-sensitive async case
- at least one test intentionally stacks multiple compatible mixins in the same async scenario
- the callable-type × job-type table is preserved in the spec/plan so omitted cells remain explicit
- first-pass execution reports failures and suggested fixes in chat before any production fix work

## User Check-in

Pause after the first-pass tests are added and run.

At that point, present:

- which new tests passed
- which new tests failed
- a brief suggested-fix list

Then wait for explicit user approval before implementing any production fixes.
