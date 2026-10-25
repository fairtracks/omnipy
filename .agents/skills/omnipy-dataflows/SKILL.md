---
name: omnipy-dataflows
description: Design, implement, or review Omnipy dataflows in any domain using typed models, datasets, reusable tasks, and composed flow templates. Applies to application flows and narrative integration examples; use the existing engine harness for exhaustive execution-semantics testing.
---

# Design Omnipy dataflows

Make the data contract explain the domain and the flow declaration explain the
workflow. Human readability is a design requirement. The models and flows are
also an inspectable contract for the agent's output: a reviewer should be able to
understand the promised data shapes, constraints, operations, and composition by
reading their declarations and relevant validators.

Reuse is a core selling point. "Omnipy" comes from "omnify": to make universal.
At each design step, ask: **Is there general functionality here that could be
omnified for reuse elsewhere?** Search for existing components first. Extract
reusable operations and stages with explicit contracts, and express variation
through type parameters, supported Model/Dataset settings, and job composition
and modifiers. Keep useful domain specializations readable at their composition
sites; renaming a domain-specific helper does not make it general. Let concrete
operations and contracts guide the abstraction.

Narrative integration tests also serve as tutorials and should be reusable in
documentation. Make Omnipy's declarative syntax, model-defined contracts, Model
mimicking, Dataset batches, and composition of job/callable types visible in the
implementation. Prefer declarative conversion and batch operations over explicit
processing loops. Choose the capabilities that make the example clear; each
tutorial need not demonstrate every feature. These are defaults for dataflow work,
not restrictions on engine implementation or a requirement to turn every Python
function into a job.

Read [patterns.md](references/patterns.md) when choosing the data shape or wiring
tasks and flows; it includes an executable example outside the original domain.
Read [design-rationale.md](references/design-rationale.md) when reviewing why
these defaults exist or resolving a conflict with the historical test plans.

## Establish the contract before writing orchestration

Identify the records and their identities, collections, shared metadata,
relationships, external operations, and observable completion conditions. Sketch
their types and a short flow declaration before expanding implementation details.
Every stage should perform a meaningful transformation or operation; merely
appending an event or fabricating a successful status is not evidence of that work.

Distinguish what the user requires from incidental details of an example. Preserve
an explicit input/output contract. If an architectural improvement changes that
contract, explain the concrete change and resolve it with the user. Ask about
unclear domain invariants or consequential alternatives, not routine syntax.

Use the current checkout's APIs. Search nearby components and representative
flows before introducing helpers or assuming a framework capability is missing.
Historical plans explain intent; their former API limitations are not a reason to
reimplement capabilities now available.

## Keep data typed throughout the workflow

- Use a Pydantic record for a fixed set of named fields and an Omnipy `Model`
  around that record. Use `Dataset[ItemModel]` for a batch of items; an item may
  be a record, a response containing several records, or a table. Keep item
  identities as dataset keys. A composite record can contain datasets plus
  metadata and status models. Lists can describe an item's intrinsic structure
  or payload, including groups of measurements processed together. Choose tables
  when the operations are actually tabular.
- Reserve "batch" for the Dataset processing abstraction in explanations and
  tutorial names. Distinguish domain groups (such as a sample's measurements)
  and transport units (such as response pages) from Omnipy batches. Nest Datasets
  when the workflow needs a collection of actual batches, not merely because the
  domain or JSON is nested. Keep introductory examples to the structure needed
  for their lesson; the water-sample harmonization example should use a single
  Dataset level, with lists inside its Models.
- The Dataset boundary also determines the units available to framework-managed
  execution. With `iterate_over_data_files=True`, an async job schedules work
  across the dataset's items and gathers results back under their keys. Keep
  independently scheduled units visible as dataset items instead of burying
  them in list Models that require manual orchestration. A fetched response's
  internal measurements do not thereby become separate jobs. The intended
  extensions are parallel execution and async-generator streaming, with Dataset
  remaining the central batch abstraction; their future interfaces are not
  specified here.
- Encode normalization and intrinsic validity in types and validators: constrained
  identifiers, dates, URLs, enumerated states, and relationships between records.
  Put a relationship validator on the smallest model containing both sides.
  Validation should occur through the data contract, not only in a preparatory task.
- Operate on Models through their mimicked interfaces: attributes, indexing,
  iteration, methods, and supported operators. This applies beyond Pydantic
  records to wrapped containers and other values. `Model` supplies the runtime
  behavior; `@om.mimics(...)` exposes the interface to supported static checkers.
  Use `.content` when a consumer specifically needs the underlying object and
  `.to_data()` when a boundary needs a plain-data representation. Neither is
  routine preparation for processing. Avoid dictionary casts and package rebuilds
  that merely compensate for failing to use the Model interface.
- Rely on Model validation when changing data through its mimicked interface.
  The structural exception is nested containers without a Model between them:
  mutating a bare inner container bypasses the outer Model. Insert Model boundaries
  between those containers. Current Pydantic-record wrapping inserts them
  recursively, including for nested container fields. See
  [mutation examples](references/patterns.md#validation-through-model-boundaries).
  Do not add routine serialization/reconstruction or manual validation calls to
  compensate for overlooking these boundaries.
- Specialize existing generic Models and Datasets before writing new components.
  Generalize shared validation/conversion rules by parameterizing the varying
  types, preserving type relationships through Dataset items and job outputs.
  Distinguish type parameters from configuration values: use `Params` and
  `.adjust(...)` where a component supports them. See
  [reusable Models and Datasets](references/patterns.md#reusable-models-and-datasets)
  for examples and when a named generic class is useful.
- Express reusable schema transformations with `ConverterModel[Source, Target]`.
  Give service requests their own types when their contract differs from the
  internal one. Converters own field mapping; tasks own calls and response updates.
  Prefer `Mapper(source)` to keep the converted value model-wrapped; use
  `Mapper.convert(source)` when the underlying target value is specifically needed.
- Keep shared metadata at the appropriate aggregate level. Dataset keys should
  serialize the primary keys of their contents. For a record whose primary key is
  a normalized string, use that string as its Dataset key. The container key and
  record field have different uses but must express the same primary-key value;
  externally assigned identifiers can remain separate fields. See
  [identity and relationship contracts](references/patterns.md#identity-and-relationship-contracts)
  for examples and the future table design. Do not assume automatic key derivation
  or re-keying is implemented by an ordinary Dataset.
- Tasks record authoritative operation results; model validators derive the
  statuses implied by those results. Put aggregate derivation on the model that
  contains its inputs, and rely on validation through Model interfaces to maintain
  it. Readiness to submit does not establish service acceptance: record that
  outcome only after acknowledgement. See the
  [status examples](references/patterns.md#status-from-facts-and-acknowledgements).
  Do not maintain duplicate task-written flags or a second workflow history solely
  to prove that stages ran.
- Choose status placement for the use case: inline fields, a nested status model,
  or a separate structure can all fit. Consider readability, ownership, reuse,
  and input/output contracts. The distinction between recorded and derived status
  does not prescribe a particular storage layout.

## Compose jobs at the level of the work

- Prefer `LinearFlowTemplate` for a sequence carrying one result forward, and
  `DagFlowTemplate` for routing named inputs and intermediate results. Their bodies
  declare the signature (`...` for ordinary function/coroutine flows); their child
  lists declare the composition.
- Use `FuncFlowTemplate` when the algorithm needs authored Python control flow,
  such as data-dependent branching, dynamic iteration, or explicit coordination.
  A fixed series of calls alone usually belongs in a linear flow.
- Make meaningful stages reusable child flows. For work on a subset of a composite
  record, consider **extract typed members → process a dataset → collect members**.
  Keep the enclosing record available where collection needs it.
- Compose compatible job types and callable types directly. Tasks, child flows,
  and Model/Dataset constructors can participate in the same flow. Retain each
  child's natural callable form, and let child composition determine the outer
  linear/DAG callable form. See
  [callable types and composed flows](references/patterns.md#callable-types-and-composed-flows).
- Write one-item tasks for independent record operations and lift them with
  `iterate_over_data_files=True`. Shared metadata is a separate keyword-only input.
  Do not hand-write dataset loops and scheduling that the decorator already supplies.
- Reuse and specialize whole child flows as well as tasks. Put stable behavior on
  the base template and workflow-specific modifiers at the composition site with
  `.refine(...)`. Modifiers are part of the inspectable job contract. Read
  [reusable jobs, templates, and modifiers](references/patterns.md#reusable-jobs-templates-and-modifiers)
  for their meanings and refinement's merge/reset semantics.
- A template describes a job; `.apply()` produces an executable job, and
  `.revise()` returns a template from a job. Outside flows, `.run(...)` is shorthand
  for `.apply()(...)`. Inside an authored flow body, call templates directly:
  `child(...)` or `await child(...)`, according to the callable contract. Supply
  templates as children of linear/DAG flows without eagerly applying or running
  them. See the lifecycle example in the same reference.
- Nested model/dataset types can express structural conversion within a stage.
  Use Datasets for processing batches and nested lists for an item's payload or
  intrinsic value structure; mapping nested values does not require nested jobs.
- Check routing explicitly: parameter-map direction, where each result is stored,
  which inputs remain available, and the last child's output. See the reference
  before relying on DAG retention or async iteration.

## Make service and state boundaries visible

Treat external API contracts as requirements in their own right: request and
response schemas, field meanings, and operation outcomes. Adapt internal data to
the service's contract. A convenient local stand-in must not silently redefine
that contract to accept the workflow's internal records or mapper classes.

A task maps the request, calls the service through a typed function or suitable
existing client/loader, and applies the response to the relevant record. A mapper
that mimics the external request schema can be passed directly in place of that
request; the service contract remains expressed in its own schema. Serialize at
the transport boundary when required. See the
[external-contract example](references/patterns.md#external-api-contracts).

In a narrative test, a coroutine stand-in in `services.py` or a mocked HTTP endpoint
should implement the same external contract. The current implementation mechanism
does not define the contract. Keep fixture-specific expected values out of tasks
and flows, and identify simulated I/O as such.

For independent asynchronous items, update each item's own result and return it;
aggregate at collection. Shared metadata should be treated as read-only during
that work. Use the resulting datasets, not assumptions about object identity or
in-place propagation. Collect them through typed assignments and use model
validators to maintain derived state. Copy deliberately when ownership or rollback
requires isolation, rather than applying a whole-package cloning convention.

Completion means the required outputs and service acknowledgements exist. Decide
how incomplete or failed items affect finalization; a coroutine returning does not
by itself prove every item succeeded.

## Structure and name reusable components

Use existing `omnipy.components` packages as the template for module responsibilities
and naming. Grow large modules into same-named packages. Prefer `Schema` for
Pydantic schemas generally and `Record` primarily for table-row schemas; use
`Model`, `Dataset`, and `Mapper` to identify those roles. Give tasks and flows
operation names; when distinguishing applied instances, use `_task` or `_flow`
rather than `_job`. In Omnipy component code, use relative imports within and
between components to support potential extraction into separate repositories.
Keep that import guideline scoped to in-Omnipy code. See
[structure and naming](references/structure-and-naming.md) for layout examples,
dependency boundaries, and import conventions.

## Keep implementations usable outside their test

Put scenario inputs, expected results, and scoped service resets in `conftest.py`
or established case modules. Keep the reusable implementation in the component-style
modules described above.

Use these four principles for narrative integration tests and their tutorial reuse:

1. **Keep the execution story visible.** Construct typed input, invoke the flow
   according to its declared callable contract, and assert meaningful output and
   relevant run state. Keep the models, tasks, and flow declarations readable and
   reusable in documentation without depending on pytest. Show the actual tested
   implementation, using repository documentation conventions.
2. **Keep expectations independent and setup isolated.** Put scenario inputs,
   independently specified expected results, and service-state resets in fixtures
   or established case modules. Do not generate expected output with the mapper
   being tested. Keep fixture-specific values and lifecycle setup out of reusable
   task and flow bodies.
3. **Verify the external contract at its boundary.** Exercise the actual flow and
   its service calls. Assert relevant request fields and returned outcomes through
   tests, spies, or mocked endpoints that implement the declared external API.
   An event label or a task-written completion flag alone does not prove the
   operation happened. Keep fixture-specific assertions out of workflow tasks.
4. **Choose coverage that supports the lesson.** Demonstrate useful combinations
   of models, datasets, jobs, and callable types through a coherent scenario.
   Add focused normalization, relationship, and failure cases that protect its
   contract, such as a failed transfer preventing final submission. Reuse existing
   engine fixtures; keep exhaustive engine/callable combinations in the framework
   harness. Verify domain success as well as job execution state.

See [readability and reuse](references/patterns.md#readable-contracts-and-documentation-reuse)
and [test details](references/patterns.md#validation-and-narrative-tests).

Before handing over a dataflow, check that:

- a human can inspect the model contracts and flow declarations to understand
  the data, actual stages, dependencies, and external operations;
- declarative conversion, mimicking Models, and Dataset operations replace
  unnecessary unpacking, processing loops, and manual orchestration;
- task and service boundaries could be reused with different input records;
- the narrative implementation can be reused as documentation/tutorial code;
- output identity, required enrichment, and failure/completion semantics are tested;
- the code uses the current framework rather than compensating for old limitations.

Use root `AGENTS.md` for repository tooling, verification, and documentation rules.
