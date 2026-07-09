## Summary

Design a testing schema for existing asynchronous flows and nested/composed flows with the
engine harness as the primary authority. The design extends existing engine test infrastructure
instead of introducing new runtime concepts or APIs.

## Goals

- Thoroughly test existing async-flow behavior across all existing engines, including Prefect.
- Thoroughly test existing nested/composed flow behavior where child jobs may be tasks or flows.
- Reuse and extend the current `tests/engine/` case/helper/fixture infrastructure as the main
  testing surface.
- Confirm a smaller set of representative behaviors in `tests/compute/` and
  `tests/integration/`.
- Allow failing committed tests when they document real support gaps in behavior that is believed
  to be supported today.

## Non-goals

- No new public APIs.
- No introduction of explicit `AsyncFlow` or `SubFlow` concepts.
- No major production refactors.
- No frozen full cartesian matrix in the spec.

## Current context

- Async behavior is already implicit in existing job/callable machinery rather than represented by
  dedicated async flow classes.
- Nested flow behavior is already modeled by composing the existing flow types rather than by a
  dedicated subflow abstraction.
- Existing engine tests already provide reusable callable-type cases and engine parametrization, but
  primarily exercise tasks and flows with task children.
- Existing compute tests cover flow lifecycle and composition basics, but not the intended async and
  nested-flow breadth.

## Design

### 1. Engine harness is the primary coverage owner

`tests/engine/` should own the main async/nested-flow expansion.

The design should extend the current `JobCase` + builder/helper + fixture pipeline so that it can
construct and run not only tasks and flows with task children, but also flows whose children are
other flows. Top-level engine tests should stay thin and parametrized; complexity should live in
reusable case modules and helpers.

This keeps the existing harness style intact while making composition breadth testable across all
engines.

### 2. Coverage scope

The schema should organize coverage around:

- parent flow kind
- child job kind
- callable-type behavior
- engine parity

The spec should not prescribe an exhaustive cartesian matrix. Instead, it should require a defined
minimum coverage floor plus a thorough representative matrix above that floor, with the planner
choosing exact combinations based on Python callable edge cases, engine behavior, and duplication
control.

#### Required scope constraints

- Linear and DAG flow coverage should assume real composition with multiple children, not trivial
  one-child wrappers.
- Child jobs for linear and DAG flow coverage must include both tasks and flows.
- Across the engine harness, linear and DAG parent coverage must each include child-flow cases using
  `LinearFlow`, `DagFlow`, and `FuncFlow` at least once.
- Async-flow coverage is required and should include async child jobs inside flows, mixed
  sync/async compositions, and nested async behavior through child flows.
- Parent `FuncFlow` coverage must include bodies that call tasks and bodies that call flows; the
  planner chooses exact combinations, but both roles are required in the final plan.

#### Callable-type expectations to verify

- For linear and DAG flows, “last child” means the last declared entry in `child_job_templates`,
  which is also the terminal child by current execution order and returned result semantics.
- Linear and DAG flows should follow the effective callable type of that terminal child.
- The current implementation may not fully enforce this intended rule for all async combinations;
  the test plan should treat this as a likely gap-discovery area and allow narrow consistency fixes
  if needed.
- Func flows should be tested according to their authored body semantics rather than any rule that
  they must mirror child callable types.
- Mixed sync/async coverage should explicitly include at least:
  - sync-leading compositions whose terminal child is async
  - async work earlier in the composition chain
  - nested async flow children inside otherwise mixed parent flows
- If a small consistency check or validation seam is missing, a small supporting production fix is
  allowed, but only if it stays within the existing API and behavior intent.

### 3. Minimum required coverage

This section defines the required floor. The planner may exceed it, but not go below it.

#### Engine floor

- Engine parity must be demonstrated for the production engines (`LocalRunner` and `PrefectEngine`).
- Mock-runner coverage remains useful for run-state and harness assertions, but mock-only coverage
  does not satisfy the parity requirement.

#### Flow-kind floor

For each production engine, the final plan must include at least:

- one passing `LinearFlow` composition case
- one passing `DagFlow` composition case
- one passing `FuncFlow` parent case
- one passing nested-flow case where the parent uses a child flow rather than only task children
- one passing async-flow case involving nested or composed flow behavior
- one passing mixed sync/async composition case without requiring a full cartesian parity matrix
- one passing nested parameter-routing case across a parent/child flow boundary

#### Semantic floor

Across the full plan, coverage must include:

- linear and DAG parents with multiple children
- child tasks and child flows in the engine harness
- child flows of each existing flow type (`LinearFlow`, `DagFlow`, `FuncFlow`) under linear/DAG
  parents at least once overall
- parent `FuncFlow` cases that call tasks and separate parent `FuncFlow` cases that call flows
- at least one nested async failure-path or support-gap case, preferably with observable run-state
  assertions where the harness can support them
- at least one targeted refine/revise case involving child flows

### 4. Required assertion domains

The planned tests should not only assert end results. They should cover, where each layer can do so
cleanly:

- exposed callable type / sync-vs-async-vs-generator behavior
- parameter routing across nested flow boundaries
- result propagation and terminal-child output behavior
- run-state transitions in harness-driven engine tests
- flow context / lifecycle propagation in compute-focused tests
- refine/revise behavior when child jobs include flows
- support-gap or failure-path behavior for at least one nested async scenario

### 5. Support-gap test policy

The plan must classify uncovered behavior gaps explicitly rather than mixing them with ordinary
regressions.

#### A. Known external engine limitations

When a behavior is blocked by a known external engine limitation rather than an Omnipy regression,
prefer engine-specific `xfail` or equivalent targeted expectation with a reason. Existing Prefect 3
generator limitations are the model here.

#### B. Claimed-supported but not yet working behavior

Because the user explicitly allows committed failing tests for this slice, isolated committed gap
tests are allowed when they document behavior that is believed to be supported but is not yet green.

Planner guidance:

- Prefer targeted, easy-to-diagnose gap cases rather than broad noisy failures.
- Prefer `xfail(strict=True)` or engine-specific expectations when that preserves suite usability
  without hiding the gap.
- Use plain failing committed tests only when keeping the gap visibly red is the point, and keep
  those failures narrowly scoped.

#### C. Temporary TDD-red tests

During implementation, temporary red tests are expected. They are not, by themselves, the long-term
documentation policy for support gaps; the planner should still decide whether each retained gap is
best represented as plain failure, `xfail`, or engine-specific expectation.

### 6. Concrete test-schema direction

#### `tests/engine/`

This is the main expansion area.

- Keep `tests/engine/cases/tasks.py` as the main source of primitive callable behavior.
- It is allowed to add a limited number of new primitive task callables there if they materially
  improve async/nested-flow coverage.
- Add new engine case-building layers for flow composition and nesting.
- Extend helper builders so parent flows can be assembled from task and/or flow children.
- Reuse existing top-level parametrized engine tests where possible, rather than growing many new
  bespoke test entry points.

The important design direction is to push complexity into reusable builders, case modules, and
fixtures rather than into large hand-written test bodies.

#### `tests/compute/`

Keep compute coverage targeted and semantic rather than exhaustive.

Good fits include:

- callable-type derivation for linear and DAG flows from the terminal child
- nested flow lifecycle/context expectations
- parameter-routing expectations across nested boundaries when easier to specify here than in the
  full engine harness
- refine/revise behavior when child jobs include flows
- small validation tests if a tiny supporting production fix is introduced

#### `tests/integration/`

Integration coverage should remain selective and confirm the engine-harness conclusions with a few
realistic scenarios.

Good fits include:

- one async nested-flow scenario
- one nested/composed parameter-routing scenario
- one lifecycle/refine/revise scenario if that is better proven end-to-end than in the harness
- reuse of known engine-specific expectation patterns where external limitations already exist

### 7. Boundaries for supporting code changes

Small supporting production changes are allowed only when needed to make the existing intended
behavior testable or consistently enforced.

For this spec, “small” means localized, single-purpose changes that:

- do not introduce new public APIs or new flow concepts
- do not broaden feature scope beyond existing async/nested-flow intent
- stay near the touched compute/engine seam
- mainly add consistency checks, expose existing metadata, or correct narrow behavior mismatches
  revealed by the new tests

Examples of acceptable changes:

- simple callable-type consistency or validation checks for linear/DAG composition
- tiny helper/introspection seams needed for nested-flow tests
- narrow fixes that align actual callable-type lifting with the intended terminal-child rule

Anything larger should be deferred to a follow-up design/planning step with explicit human
interaction.

## Success criteria

This design is successful if the resulting plan leads to:

1. Engine-first parity coverage for async and nested flows across all existing engines.
2. Child-flow coverage for linear and DAG flows, including child func flows.
3. Clear verification of callable-type expectations for linear/DAG flows versus func flows.
4. A defined minimum coverage floor that the planner cannot silently shrink.
5. Representative async cases that expose current support gaps.
6. Explicit support-gap handling so committed failing tests, `xfail`, and engine-specific
   expectations are used intentionally rather than ambiguously.
7. Committed failing tests being acceptable where they document real unsupported-yet-claimed
   behavior.

## Risks and mitigations

### Risk: test explosion and duplication

Mitigation:

- keep the spec matrix high-level rather than frozen
- define a clear minimum floor so “representative” does not become underspecified
- centralize complexity in reusable builders and fixtures
- let planning choose representative combinations instead of enumerating every combination here

### Risk: hidden semantics drift from “small fixes”

Mitigation:

- restrict supporting code changes to tiny consistency/testability seams
- defer any broader behavior-shaping work to follow-up human-approved work

## User check-in

Before implementation planning, the plan should preserve these decisions:

- engine harness is the main authority
- no new public concepts or APIs
- async-flow coverage and child-flow coverage are both first-class requirements
- the planner must preserve the minimum coverage floor and explicit support-gap policy
- failing tests are acceptable when they document current gaps
