# Async Compute-Mixins Test Extension Design

## Summary

Add a small, representative async-focused test extension for compute mixins in `omnipy`.
The new coverage should target the two recently untested risk areas called out by the user:

- commit `48906e4a9a38ff1fe8b0fa77b9afbea19cf7f921` (`serialize` support for async jobs)
- commit `a2d700631f24bdd2d99e4bdf3f34594d7a6b828a` (mixin reorder in `FuncArgJobBase`)

The extension should reuse existing test infrastructure and add only a carefully chosen subset of
task/flow cases that are most likely to fail if mixin composition regresses again, with primary
focus on async behavior, generator brittleness, and supported `serialize` + `result_key`
composition.

## Goals

- Catch regressions in async compute-mixin behavior without attempting a full cartesian matrix.
- Cover all four job types at least once in the new async slice: `Task`, `FuncFlow`,
  `LinearFlow`, and `DagFlow`.
- Put slightly more weight on `serialize` and `auto_async`, while still spreading coverage across
  other order-sensitive mixins.
- Verify the supported `serialize` + `result_key` composition where serialization sees dataset
  results before `result_key` wraps the outward return value.
- Verify `auto_async` behavior both with and without an already-running event loop, preferably by
  reusing the same assertions for both contexts.
- Add explicit sync-generator and async-generator coverage for mixin combinations where outward
  return or yield behavior is brittle.
- Audit nearby sync coverage and add a minimal sync backfill when an important mixin interaction is
  still underrepresented.
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
- No attempt to exhaust every generator combination across every mixin and job shape.

## Current context

### Existing risk points in production code

- `src/omnipy/compute/_func_job.py` composes callable mixins in a specific order and warns that the
  order dependencies may not be fully tested.
- `src/omnipy/compute/_mixins/serialize.py` has separate persistence paths for:
  - plain synchronous dataset results
  - `asyncio.Task` results
  - generic awaitable results
- `src/omnipy/compute/_mixins/result_key.py` wraps the value returned by deeper mixins, so under
  the current mixin order a supported `serialize` + `result_key` stack should allow serialization to
  operate on dataset results before the outward result is wrapped under the configured key.
- `src/omnipy/compute/_mixins/auto_async.py` only auto-runs coroutine functions, and it suppresses
  top-level auto-execution while the job is inside flow context.

### Current coverage gaps

- `tests/compute/mixins/test_auto_async.py` verifies only basic sync-vs-async task behavior and
  does not combine `auto_async` with `serialize`, `iterate`, `params`, or `result_key`, and it does
  not prove the same scenario both with and without a running event loop.
- `tests/compute/mixins/test_mixin_integration.py` currently covers only sync-oriented mixin
  interactions.
- `tests/integration/novel/serialize/test_serialize.py` exercises serialize behavior for existing
  task/flow fixtures, but not for async jobs.
- Reusable async flow cases already exist elsewhere in the repo, but they do not currently serve as
  direct regression coverage for the compute-mixin order and async serialization paths above.
- The current compute-mixin slice appears light on generator-focused interaction tests, especially
  for sync generators and async generators whose outward yielded values are more fragile than plain
  coroutine returns.

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

6. **Treat generators as a first-class risk area.**
   Sync generators and async generators should be represented wherever mixin behavior depends on
   the outward yielded/returned shape rather than only on plain coroutine completion.

7. **Reuse identical assertions across loop contexts when possible.**
   For top-level `auto_async` scenarios, prefer one parameterized test shape that runs both outside
   an event loop and inside an already-running event loop.

8. **Backfill sync only when it closes a real nearby gap.**
   The slice remains async-led, but if the same representative mixin interaction is missing in sync
   form and current coverage would not catch a regression there, add the smallest sync sentinel
   needed.

### Selected representative subset

The planned spec should drive a subset with the following intent.

Planned execution approach for the approved plan: **sub-agent-driven** task execution, with review
between implementation slices.

#### A. Async task + serialize + result_key + auto_async

Add one async dataset-returning task integration case that combines `persist_outputs`,
`result_key`, and `auto_async`, and run that same behavioral test both with and without a running
event loop.

Why this matters:

- top-level async tasks are the clearest way to hit the `asyncio.Task` persistence callback path in
  `SerializerFuncJobBaseMixin`
- this directly guards the behavior fixed by commit `48906e4a...`
- it also verifies that `AutoAsyncJobBaseMixin` and `SerializerFuncJobBaseMixin` cooperate in the
  intended order
- it verifies the supported nesting where `serialize` operates on the dataset result before
  `result_key` wraps the outward value

Recommended shape:

- one parameter controls whether the exact same scenario runs:
  - from synchronous top-level code with no pre-existing loop
  - from inside an already-running event loop
- the assertions should confirm both outward return behavior and persisted serialized output
- persisted-artifact checks should use deterministic discovery of the newly written tarball rather
  than brittle timestamp/path literals

#### B. Async function flow + serialize + result_key in flow context

Add one async dataset-returning `FuncFlow` case that combines `serialize` and `result_key` while
executing in flow context.

Why this matters:

- inside flow context, auto-async should not eagerly consume the coroutine at the outer boundary
- this should exercise the non-`Task` awaitable path in `SerializerFuncJobBaseMixin`
- it confirms that serialize support works both outside and inside flow context
- it proves the supported `serialize` + `result_key` composition in a flow, not only in a task

#### C. Linear flow + iterate + auto_async + generator-sensitive terminals

Add at least one async `LinearFlow` case whose terminal child uses dataset iteration semantics, and
include generator-sensitive coverage where the terminal callable is a sync generator and/or async
generator when the outward return shape is the risk being exercised.

Why this matters:

- this is the strongest representative for the `AutoAsyncJobBaseMixin` →
  `IterateFuncJobBaseMixin` ordering risk
- it spreads coverage away from serialize-only assertions
- it gives the slice one concrete async dataset transformation flow rather than only persistence
  checks
- linear-flow terminal behavior is a natural place for generator brittleness to surface

#### D. Dag flow + params/result_key + generator-sensitive returns

Add one async `DagFlow` case that emphasizes `fixed_params` and/or `param_key_map` together with
`result_key` on a non-dataset result, and use DAG coverage to include generator-sensitive return
shapes where they are more fragile than plain scalar returns.

Why this matters:

- it covers DAG flow in the new async slice
- it adds the requested non-dataset case
- it exercises the `params`/`result_key` ordering relationship without involving serialize
- DAG result routing is another place where generator return semantics can break subtly

#### E. One maximal compatible-mixin case

Include one intentionally dense async test that combines as many compatible mixins as possible.

Recommended shape:

- async task or async linear-flow case
- `iterate_over_data_files=True`
- `auto_async=True`
- `fixed_params`
- `param_key_map`
- `result_key`
- output-dataset option (`output_dataset_param` or `output_dataset_cls`)
- serialize enabled if the return contract remains dataset-shaped

Important constraint:

The dense case should prefer the real supported `serialize` + `result_key` combination rather than
avoiding it. Only split the mixins apart when a specific generator or non-dataset scenario would no
longer exercise the intended contract honestly.

#### F. Generator-focused stress cases

Add explicit sync-generator and async-generator representatives for each mixin family where the
outward yielded/returned shape is part of the risk:

- `result_key`
- `iterate`
- flow terminal-child return behavior
- `serialize`, but only when the result contract remains meaningfully serializable rather than being
  forced into an artificial case

The planner should minimize duplication by parameterizing generator type where the same assertions
fit both sync-generator and async-generator forms.

#### G. Sync-gap audit and minimal backfill

Before finalizing the plan, inspect whether the chosen representative interactions are already well
protected in sync form. If an important adjacent sync case is still underrepresented — especially
for `serialize` + `result_key` or generator-sensitive behavior — add the smallest sync sentinel test
needed to close that gap.

### Callable-type × job-type matrix for this slice

This table is for the **new async extension work**, not for overall historical repo coverage.

| Callable type \ Job type | Task | Func flow | Linear flow | Dag flow |
| --- | --- | --- | --- | --- |
| Sync function | Audit existing coverage; add only if a critical nearby mixin gap remains | Audit existing coverage; add only if a critical nearby mixin gap remains | Audit existing coverage; add only if a critical nearby mixin gap remains | Audit existing coverage; add only if a critical nearby mixin gap remains |
| Sync generator | **Covered** — return-sensitive generator mixin case | **Covered** — generator-sensitive flow-body case | **Covered** — generator-sensitive terminal-child case | **Covered** — generator-sensitive routing/result case |
| Async coroutine | **Covered** — serialize + result_key + auto_async dataset task, loop/no-loop contexts | **Covered** — serialize + result_key + flow-context awaitable path | **Covered** — iterate + auto_async representative flow | **Covered** — params/result_key non-dataset representative flow |
| Async generator | **Covered** — return-sensitive generator mixin case | **Covered** — generator-sensitive flow-body case | **Covered** — generator-sensitive terminal-child case | **Covered** — generator-sensitive routing/result case |

### Why the sync-function cells are audit-only

- The user requested a representative subset rather than exhaustive coverage.
- The two named risky commits are still most directly exercised by async-coroutine cases, so sync
  functions stay secondary unless the audit shows a real nearby hole.
- Generator rows are no longer treated as low priority because their outward behavior is brittle and
  more likely to expose mixin-order mistakes.
- Existing sync coverage may already protect some sync-function invariants; the audit step keeps the
  slice from duplicating them blindly while still allowing focused backfills.

## First-pass execution policy

### Required first pass

The first implementation pass must:

- add the selected tests
- run the relevant test subset
- report all failing tests in chat
- include suggested fixes in chat
- stop for **User Check-in A** before changing production code

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
- supported `serialize` + `result_key` composition is explicitly tested rather than treated as an
  excluded combination
- at least one top-level `auto_async` scenario is verified in both contexts:
  - no already-running event loop
  - inside an already-running event loop
- the non-serialize spread includes:
  - one `iterate`-sensitive async case
  - one `params`/`result_key`-sensitive async case
- sync-generator and async-generator coverage exists for the return-sensitive mixin interactions in
  this slice
- at least one test intentionally stacks multiple compatible mixins in the same async scenario
- the callable-type × job-type table is preserved in the spec/plan so omitted cells remain explicit
- sync-function coverage has been audited and a minimal backfill added if a critical nearby gap was
  found
- first-pass execution reports failures and suggested fixes in chat before any production fix work

## User Check-in A

Pause after the first-pass tests are added and run.

At that point, present:

- which new tests passed
- which new tests failed
- a brief suggested-fix list

Then wait for explicit user approval before implementing any production fixes.

✅ Approved by  2026-08-16
