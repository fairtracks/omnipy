---
name: omnipy-dataflows
description: Design, implement, or review Omnipy dataflows in any domain using typed models, datasets, reusable tasks, and composed flow templates. Applies to application flows and narrative integration examples; use the existing engine harness for exhaustive execution-semantics testing.
---

# Design Omnipy dataflows

Make the data contract explain the domain and the flow declaration explain the
dataflow. Human readability is a design requirement. The models and flows are
also an inspectable contract for the agent's output: a reviewer should be able to
understand the promised data shapes, constraints, operations, and composition by
reading their declarations and relevant validators.
Use "dataflow" consistently in explanations and documentation.

Use blank lines to separate groups with distinct purposes in implementations,
fixtures, and assertions. Extract a cohesive block into a small, clearly named
function when it has a distinct responsibility, is repeated, or obscures its
caller. Keep the flow declaration and the test's input → execution → verification
story visible; helper extraction should improve understanding at both levels.

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

Consult the relevant sections of [patterns.md](references/patterns.md) when choosing
the data shape or wiring tasks and flows. Its navigation table points to API
details and an executable catalog example.
Read the [design evidence](references/design-rationale.md) for the comparison
and review history behind these defaults. The guidance here describes how to
design flows using the current APIs.

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
Check plans against those APIs before reimplementing an available capability.

Treat preferred examples as architectural evidence. Suggest fixes for obvious
bugs and verify the intended invariant; do not promote implementation mistakes
into design rules.

## Keep data typed throughout the dataflow

- Use a Pydantic record for a fixed set of named fields and an Omnipy `Model`
  around that record. Use `Dataset[ItemModel]` for a batch of items; an item may
  be a record, hierarchical data, a response containing several records, or a
  table. Keep item identities as dataset keys. A composite record can contain
  datasets plus metadata and status models. Lists can describe an item's intrinsic structure
  or payload, including groups of measurements processed together. Choose tables
  when the operations are actually tabular.
- Reserve "batch" for the Dataset processing abstraction in explanations and
  tutorial names. Domain groups and response pages can remain structured items.
  Nest Datasets for collections of actual batches; keep introductory examples to
  the structure needed for their lesson. See
  [data structures and batch boundaries](references/patterns.md#choose-data-structures-by-their-role),
  including the water-sample example's deliberate single Dataset level.
- The Dataset boundary also determines the units available to framework-managed
  execution. With `iterate_over_data_files=True`, an async job schedules work
  across the dataset's items and gathers results back under their keys. Keep
  independently scheduled units visible as dataset items instead of burying
  them in list Models that require manual orchestration. Internal measurements
  processed together do not thereby become separate jobs. The reference distinguishes
  current async concurrency and async-generator streaming from intended parallel
  execution extensions.
- Encode normalization and intrinsic validity in types and validators: constrained
  identifiers, dates, URLs, enumerated states, and relationships between records.
  Prefer specific field contracts to bare `str`/`float`: Enum or Literal for
  supported currencies/states, nonnegative or positive finite amounts as required,
  non-empty identifiers, and regex constraints when the identifier has a defined
  format. Derive constraints from the domain and external contracts, not just the
  fixture values. See [constrained fields](references/patterns.md#constrained-field-contracts).
  Put a relationship validator on the smallest data type containing both sides.
  Validation should occur through the data contract, not only in a preparatory task.
- Prefer validators on the Dataset subclass for invariants within that Dataset,
  such as uniqueness across items or key/content agreement. Use the current
  `@pyd.validator('data')` hook; avoid adding a `Model[SomeDataset]` solely to gain
  `Model._parse_data()`. Keep item rules in item Models and relationships spanning
  multiple Datasets in their containing schema. See
  [Dataset-level validation](references/patterns.md#dataset-level-validation).
- Operate on Models through their mimicked interfaces: attributes, indexing,
  iteration, methods, and supported operators. This applies beyond Pydantic
  records to wrapped containers and other values. `Model` supplies the runtime
  behavior for wrapped classes generally; common scalar/collection shapes have
  built-in static typing support. Assume runtime mimicking works correctly,
  including for explicitly annotated Models; report discrepancies and/or suggest
  fixes rather than designing around them. Expose a particular Model's interface
  with mypy-compatible typing, such as a protocol-inheriting `TYPE_CHECKING`
  facade, in additions to Omnipy library code. In examples, tutorials, and tests,
  `@om.mimics(...)` may be preferred for readability unless mypy support is part
  of their purpose. Use protocols to describe reusable capabilities. See
  [runtime mimicking and static typing](references/typing.md) for concrete Model
  and Dataset examples, generic-interface limitations, and checker verification.
  Use `.content` when a consumer specifically needs the underlying object and
  `.to_data()` when a boundary needs a plain-data representation. Neither is
  routine preparation for processing. Avoid dictionary casts and package rebuilds
  that merely compensate for failing to use the Model interface.
- Rely on Model validation when changing data through its mimicked interface.
  Normal updates maintain valid data automatically, while reuse of already
  validated Models avoids unnecessary work. Agents generally do not need to track
  validation timing or add manual revalidation. Declare stored Models between
  nested mutable containers; Pydantic-record wrapping supplies them recursively.
  See the
  [mutation examples](references/patterns.md#validation-through-model-boundaries).
  If an update behaves unexpectedly, consult the
  [troubleshooting details](references/patterns.md#troubleshooting-unexpected-validation-behavior)
  for known nested-container/dynamic-conversion limitations and validation scope.
- Specialize existing generic Models and Datasets before writing new components.
  Generalize shared validation/conversion rules by parameterizing the varying
  types, preserving type relationships through Dataset items and job outputs.
  Distinguish type parameters from configuration values: use `Params` and
  `.adjust(...)` where a component supports them. See
  [reusable Models and Datasets](references/patterns.md#reusable-models-and-datasets)
  for examples and when a named generic class is useful.
- Express reusable type conversions with `ConverterModel[Source, Target]`,
  including scalars, collections, and Pydantic schemas. Wrap parameterized source
  types such as `list[int]` or `tuple[...]` in `Model[...]`; see
  [conversion details](references/patterns.md#model-transformations).
  Give service requests their own types when their contract differs from the
  internal one. Converters own conversion logic; tasks own service calls and response updates.
  Prefer `Mapper(source)` to keep the converted value model-wrapped; use
  `Mapper.convert(source)` when the underlying target value is specifically needed.
- Keep shared metadata at the appropriate aggregate level. Dataset keys should
  serialize the primary keys of their contents. For a record whose primary key is
  a normalized string, use that string as its Dataset key; external identifiers
  can remain separate fields. Prefer Dataset validators for key/content agreement;
  existing aggregate validators also enforce it at their containing boundary. See
  [identity and relationship contracts](references/patterns.md#identity-and-relationship-contracts)
  for examples and the future table design. Do not assume automatic key derivation
  or re-keying is implemented by an ordinary Dataset. Dataset-native primary-key
  typing, rekeying, and continuous key maintenance are planned together. The
  implemented `PrimaryKeyDatasetModel` in `omnipy.components.nested.models`
  supplies interim conversion of Pydantic records, including composite keys and
  collision rejection. It recomputes keys at conversion, not continuously; see
  the reference for defining-module imports and supported inputs.
- Tasks record authoritative operation results. When deriving domain status from
  those results, put the validator on the Model that contains its inputs.
  Changes to wrapped data through the Model interface trigger
  validation, maintaining derived status at that Model boundary. Readiness to
  submit does not establish service acceptance: record that outcome only after
  acknowledgement. See the
  [status examples](references/patterns.md#status-from-facts-and-acknowledgements).
  Do not maintain duplicate task-written flags or a second dataflow history solely
  to prove that stages ran.
- Choose status representation for the use case. Dataset `PendingData` and
  `FailedData` markers can track execution status; explicit typed fields can
  represent domain outcomes. Use either or both as needed. For explicit status,
  inline fields, a nested status model, or a separate structure can all fit.
  Consider readability, ownership, reuse, and input/output contracts. The
  distinction between recorded and derived status does not prescribe a layout.

## Compose jobs at the level of the work

- Prefer `LinearFlowTemplate` for a sequence passing results forward positionally,
  and `DagFlowTemplate` for routing named inputs and intermediate results. Their
  bodies declare the signature (`...` for ordinary function/coroutine flows); their child
  lists declare the composition.
- Use `FuncFlowTemplate` when the algorithm needs authored Python control flow,
  such as data-dependent branching, dynamic iteration, or explicit coordination.
  A fixed series of calls alone usually belongs in a linear flow.
- Make meaningful stages reusable child flows. For work on a subset of a composite
  record, consider **extract typed members → process a dataset → collect members**.
  Keep the enclosing record available where collection needs it.
- Compose compatible job types and callable types directly. Tasks, child flows,
  and Model/Dataset constructors can participate in the same flow. Callable forms
  include synchronous functions, coroutines, synchronous generators, and async
  generators. Retain each child's natural form, and let child composition determine
  the outer linear/DAG callable form. See
  [callable types and composed flows](references/patterns.md#callable-types-and-composed-flows).
- Write one-item tasks for independent record operations and lift them with
  `iterate_over_data_files=True`. Shared metadata is a separate keyword-only input.
  Do not hand-write dataset loops and scheduling that the decorator already supplies.
- Reuse and specialize whole child flows as well as tasks. Put stable behavior on
  the base template and dataflow-specific modifiers at the composition site with
  `.refine(...)`. Give each refined template a descriptive `name`; a new Python
  variable name does not rename the job. Modifiers are part of the inspectable job
  contract. Read
  [reusable jobs, templates, and modifiers](references/patterns.md#reusable-jobs-templates-and-modifiers)
  for their meanings and refinement's merge/reset semantics.
- A template describes a job; `.apply()` produces an executable job, and
  `.revise()` returns a template from a job. Outside flows, `.run(...)` is shorthand
  for `.apply()(...)`. Inside an authored flow body, call templates directly:
  `child(...)` or `await child(...)`, according to the callable contract. Supply
  templates as children of linear/DAG flows without eagerly applying or running
  them. See the lifecycle example in the same reference.
- Check routing explicitly: parameter-map direction, where each result is stored,
  which inputs remain available, and the last child's output. See the reference
  before relying on DAG retention or async iteration.

## Make service and state boundaries visible

For common HTTP ingestion, build paging URLs through `HttpUrlModel`'s structured
fields, collect them in `HttpUrlDataset`, and load responses with the intended
Dataset class's `.load(...)` or the existing remote loading templates. Reuse their
HTTP policies and preserve the distinction between response pages and domain
items. See [paging URLs and Dataset loading](references/remote-loading.md) for
sync/async usage, a composed example, and combining pages into validated records
before constructing a Dataset keyed by record identity.

Treat external API contracts as requirements in their own right: request and
response schemas, field meanings, and operation outcomes. Adapt internal data to
the service's contract. A convenient local stand-in must not silently redefine
that contract to accept the dataflow's internal records or mapper classes.

A task maps the request, calls the service through a typed function or suitable
existing client/loader, and applies the response to the relevant record. A mapper
that mimics the external request schema can be passed directly in place of that
request; the service contract remains expressed in its own schema. Serialize at
the transport boundary when required. See the
[external-contract example](references/patterns.md#external-api-contracts).

In a narrative integration test, declare the example's external contract through
its request/response types and service behavior, and verify that contract in the
test. A coroutine stand-in in `services.py` or a mocked HTTP endpoint can implement
it. Replacing one with the other should preserve the declared field meanings and
operation outcomes. Keep fixture-specific expected values out of tasks and flows,
and identify simulated I/O as such.

For independent asynchronous items, each task owns its result; aggregate at
collection. Choose Dataset task markers or explicit domain status updates to
match the contract. Shared metadata should be treated as read-only during that
work. Use the resulting datasets, not assumptions about object identity or
in-place propagation. Inspect failed/pending entries before assigning a returned
Dataset into an aggregate Model: that assignment can raise on task markers.
Collect accepted results through typed assignments and use model validators to
maintain derived state. Item validation alone does not imply that a containing
schema's aggregate validators rerun. Copy deliberately when ownership or rollback
requires isolation, rather than applying a whole-package cloning convention.

Completion means the required outputs and service acknowledgements exist. Decide
how incomplete or failed items affect finalization; a coroutine returning does not
by itself prove every item succeeded. Use the current
[failure inspection APIs](references/patterns.md#inspect-current-failure-and-pending-results)
to retain successful results and inspect failures by key. Use the general
`require_all_items` task before stages requiring all entries to be available.
Item-completion policies could later be expressed as job modifiers; that API is
not implemented.
Full recovery handling, including atomic rollback of jobs, is largely future
work; inspection methods do not supply that behavior.

## Structure and name reusable components

Use existing `omnipy.components` packages as the template for module
responsibilities and naming. This file structure will be the basis of Omnipy's
future plugin architecture. Grow large modules into same-named packages. Prefer
`Schema` for Pydantic schemas generally and `Record` primarily for table-row schemas;
use `Model`, `Dataset`, and `Mapper` to identify those roles. Give tasks and flows
operation names; when distinguishing applied instances, use `_task` or `_flow`
rather than `_job`. In Omnipy component code, use relative imports within and
between components to support potential extraction into separate repositories.
Keep that import guideline scoped to in-Omnipy code. See
[structure and naming](references/structure-and-naming.md) for layout examples,
dependency boundaries, and import conventions.

## Keep implementations usable outside their test

When the requested deliverable is a test, use pytest and the repository's existing
runtime, engine, and service-fixture machinery. Do not add a standalone `demo.py`
runner or a parallel execution harness. Reusable implementation modules and a
clear pytest scenario provide the tutorial material.

Use these four principles for narrative integration tests and their tutorial reuse:

1. **Keep the execution story visible.** Construct typed input, invoke the flow
   according to its declared callable contract, and compare the meaningful output.
   Check run state when it matters to the scenario. Keep declarations readable and
   reusable in documentation without depending on pytest. Show the actual tested
   implementation, using repository documentation conventions.
2. **Keep expectations independent and setup isolated.** Put scenario inputs,
   independently specified expected results, and scoped service-state resets in
   `conftest.py` or `pytest_cases` case modules. Create new case modules when they
   help organize the scenarios. Compare complete outputs or service requests using
   Model equality or `to_data()`-serialized values, whichever expresses the test's
   contract. Add separate checks only for relevant behavior not already covered.
   Do not generate expected output with the mapper being tested. Keep fixture-specific
   values and lifecycle setup out of reusable task and flow bodies.
3. **Verify relevant external behavior at its boundary.** Exercise the actual flow.
   Check requests and returned outcomes when they are part of the scenario's
   contract, using spies or mocked endpoints as needed.
   Mock external services, keeping Omnipy's functionality real. For HTTP flows,
   serve fixture responses from a local test endpoint so `Dataset.load()`, remote
   tasks, decoding, and model validation run normally. Do not replace Omnipy's
   loader, tasks, or orchestration with fixture implementations. See
   [HTTP test boundaries](references/remote-loading.md#test-the-real-loader-against-a-mocked-service).
   An event label or a task-written completion flag alone does not prove the
   operation happened. Keep fixture-specific assertions out of tasks and flows.
4. **Choose coverage that supports the lesson.** Demonstrate useful combinations
   of models, datasets, jobs, and callable types through a coherent scenario.
   Straightforward Model validations already act as executable assertions; do not
   restate them as field checks in every test. Test complex validators and relevant
   failure policies with focused cases. Check wrapper structure only when it is
   the behavior under test. Reuse existing engine fixtures; keep exhaustive
   engine/callable combinations in the framework harness.

See [readability and reuse](references/patterns.md#readable-contracts-and-documentation-reuse)
and [test details](references/patterns.md#validation-and-narrative-tests).

Before handing over a dataflow, check that:

- a human can inspect the model contracts and flow declarations to understand
  the data, actual stages, dependencies, and external operations;
- declarative conversion, mimicking Models, and Dataset operations replace
  unnecessary unpacking, processing loops, and manual orchestration;
- task and service boundaries could be reused with different input records;
- the narrative implementation can be reused as documentation/tutorial code;
- tests demonstrate the scenario's outcome and complex behavior without repeating
  straightforward Model validations as assertions;
- the code uses the current framework rather than compensating for old limitations.

Use root `AGENTS.md` for repository tooling, verification, and documentation rules.
