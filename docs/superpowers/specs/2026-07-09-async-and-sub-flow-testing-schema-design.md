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

The spec should not prescribe an exhaustive cartesian matrix. Instead, it should require a thorough
representative matrix, with the planner choosing exact combinations based on Python callable edge
cases, engine behavior, and duplication control.

#### Required scope constraints

- Linear and DAG flow coverage should assume real composition with multiple children, not trivial
  one-child wrappers.
- Child jobs for linear and DAG flow coverage must include both tasks and flows.
- Flow children should include `LinearFlow`, `DagFlow`, and `FuncFlow` where meaningful.
- Async-flow coverage is required and should include async child jobs inside flows, mixed
  sync/async compositions, and nested async behavior through child flows.

#### Callable-type expectations to verify

- Linear and DAG flows should follow the effective callable type of the last child.
- Func flows should be tested according to their authored body semantics rather than any rule that
  they must mirror child callable types.
- If a small consistency check or validation seam is missing, a small supporting production fix is
  allowed, but only if it stays within the existing API and behavior intent.

### 3. Concrete test-schema direction

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

- callable-type derivation for linear and DAG flows from the last child
- nested flow lifecycle/context expectations
- refine/revise behavior when child jobs include flows
- small validation tests if a tiny supporting production fix is introduced

#### `tests/integration/`

Integration coverage should remain selective and confirm the engine-harness conclusions with a few
realistic scenarios.

Good fits include:

- one async nested-flow scenario
- one nested/composed parameter-routing scenario
- one lifecycle/refine/revise scenario if that is better proven end-to-end than in the harness

### 4. Boundaries for supporting code changes

Small supporting production changes are allowed only when needed to make the existing intended
behavior testable or consistently enforced.

Examples of acceptable changes:

- simple callable-type consistency or validation checks for linear/DAG composition
- tiny helper/introspection seams needed for nested-flow tests

Anything larger should be deferred to a follow-up design/planning step with explicit human
interaction.

## Success criteria

This design is successful if the resulting plan leads to:

1. Engine-first parity coverage for async and nested flows across all existing engines.
2. Child-flow coverage for linear and DAG flows, including child func flows.
3. Clear verification of callable-type expectations for linear/DAG flows versus func flows.
4. Representative async cases that expose current support gaps.
5. Committed failing tests being acceptable where they document real unsupported-yet-claimed
   behavior.

## Risks and mitigations

### Risk: test explosion and duplication

Mitigation:

- keep the spec matrix high-level rather than frozen
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
- failing tests are acceptable when they document current gaps
