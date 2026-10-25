# Evidence and limits of the design guidance

This comparison treats the complete trees at these commits as the two designs:

- Agent implementation: `5541d1d2914506efb0ecea789c0056779c07565a`.
- User's preferred refactor: `a62c57e530b8ba8cbac35d9475394fd43548a4bd`.

The latter commit's own diff is mainly module reorganization; the redesign also
includes preceding commits. Looking only at `a62c57e5^..a62c57e5` misses most of the
lesson. Current framework capabilities, including subsequent fixes, are available.

## What changed and what to generalize

| Agent design | Preferred design | Transferable principle |
| --- | --- | --- |
| A union-valued `SubmissionPackage` dataset stores tables and a metadata record under fixed string keys. | `SubmissionModel` wraps a record with typed sample/file datasets, metadata, and status. | Model a fixed heterogeneous aggregate as a record; use datasets for collections of independently addressable items. |
| Helpers repeatedly call `.to_data()`, cast dictionaries, clone the package, and rebuild it after updates. | Tasks access fields such as `submission.metadata.sequence_depot_submission_id` and return enriched models. | Keep typed data intact between processing boundaries; serialization is not the default mutation API. |
| Link checks occur in a helper called by a normalization task; storage checks inspect string prefixes. | Models contain constrained strings, date/URL types, derived filenames, and relationship validators. | Make intrinsic data validity part of the data contract. |
| The submission alias is repeated on every row and sample aliases are separately listed in metadata. | Shared submission context lives on the aggregate; files refer to samples by local alias. | Place metadata at its natural scope and avoid redundant relationships without a contract requiring them. |
| Request dictionaries are built by untyped helper functions. | `SubmissionToSequenceDepotRequestMapper` and `SampleAndMetadataToBioSampleVaultSubmissionMapper` convert typed inputs to service schemas. | Give schema mapping an explicit reusable model boundary, including multi-input mappings. |
| An imperative `FuncFlowTemplate` manually calls and awaits six steps. | A `LinearFlowTemplate` declares four meaningful stages, including two DAG child flows. | Expose fixed topology through composition; reserve authored control flow for algorithms that need it. |
| Whole-package tasks loop through rows and manufacture all their enriched data. | Iterated async tasks process a single sample or file with shared metadata. | Choose the smallest independently processable unit and use framework iteration. |
| Tasks contain simulated service work and fixture-specific payload assertions. | Typed service stand-ins live in `services.py`; tasks map, call, and apply results. | Separate external behavior, orchestration, and test expectations. |
| Step labels, transfer tickets, and archive states are updated manually throughout. | Item results support derived readiness states; final submission records explicit acceptance. | Derive state from authoritative facts, and record outcomes that cannot be inferred. |
| No child flows expose the internal coordination. | Extract/process/collect DAGs route models with `param_key_map`, `result_key`, and retained kwargs. | Make subflows meaningful reusable stages, and preserve values needed downstream. |
| The test file contains flow/task definitions plus large literal expectations. | `models.py`, `tasks.py`, `flows.py`, `services.py`, and `conftest.py` leave a short execution/assertion narrative. | Organize by responsibility so the implementation can stand outside the test. |
| The test conditionally awaits a result of uncertain shape. | The test directly awaits the declared async flow and checks output plus `RunState.FINISHED`. | Make the callable contract deliberate and verify it through the appropriate harness. |

## The historical spec was also revised in practice

The requested source documents are:

- `docs/superpowers/specs/2026-07-09-async-and-sub-flow-testing-schema-design.md`
- `docs/superpowers/plans/2026-07-10-async-and-sub-flow-testing-plan.md`

Task 9 in the July 10 plan redirects the integration slice to
`docs/superpowers/plans/2026-07-11-async-and-sub-flow-integration-test-slice-plan.md`.
The documents called for a top-level dataset with `submission_samples`,
`submission_files`, and `submission_metadata`, and for process state to be combined
with metadata. The preferred code instead uses a composite model, shorter member
names, and a separate status member. The old plan also placed transfer before
registration; the preferred linear flow places registration before transfer while
still gating final submission on both.

For this training task the user explicitly identifies the later design as the
target, so those earlier structural details are superseded evidence, not rules to
preserve. A future agent should not silently override a new user's explicit
contract merely because this example used a different shape or order.

The original spec's terminal-child wording is incomplete for current async
composition: current code makes any async child lift the flow to async while the
terminal output governs generator behavior. Follow the current implementation and
tests; do not restore an old limitation or invent `AsyncFlow`/`SubFlow` classes.

## Capabilities to use rather than emulate

The interval added or improved model/dataset children in flows, dataset-iteration
typing, retained DAG kwargs, `ConverterModel`, `DateModel`, `HostUrlModel`, nested
Pydantic wrapping, `mimics`, and linear-flow argument routing. The earlier agent's
code is not evidence that these are unavailable now. The reference patterns point
to the current code instead of asking an agent to rebuild those mechanisms.

The companion water-sample harmonization example corroborates the approach in a
different domain: refined collection subflows, typed schema mappers, reusable
collection operations, and model/dataset constructors as flow children.

## Clarifications from the user review

The user identifies reuse as a core selling point: "Omnipy" comes from "omnify",
meaning "to make universal". Agents should actively look for general functionality
that can be reused elsewhere. For jobs, the water-sample example makes this
concrete by refining the same collection subflow for different sources. The
[job guidance](patterns.md#reusable-jobs-templates-and-modifiers) explains how
templates, modifiers, and executable jobs support that reuse. The corresponding
[data-type guidance](patterns.md#reusable-models-and-datasets) covers generic
specialization of Models and Datasets, preservation of type relationships, and
the distinction between type parameters and configurable `Params`/`.adjust(...)`.

Component packages also supply the structural template. The user clarified that
applied instances should use `_task` or `_flow`, that `Record` primarily denotes
a table-row schema, and that relative imports within and between components are
an in-Omnipy guideline supporting potential extraction into separate repositories.
See [structure and naming](structure-and-naming.md) for the agreed conventions.

The user made human readability an acceptance criterion: model and flow
declarations form an inspectable contract for agent output. Integration scenarios
also serve as tutorials, showing Omnipy's capabilities within a focused lesson. See
[readability and reuse](patterns.md#readable-contracts-and-documentation-reuse).

The user emphasized Models as working mimicking wrappers, including for
non-Pydantic content. This motivated the catalog example's direct
`PublicationMapper((record, metadata))` construction and `@mimics(PublishRequest)`.
The [conversion guidance](patterns.md#model-transformations) explains the boundary
between retaining the wrapper and requesting its underlying value.

The user emphasized that the BioSampleVault submission type is the external API
contract itself, currently named `BioSampleVaultSampleSubmissionSchema`. The
coroutine in `services.py` is its present implementation; mocked API endpoints
are a likely replacement. The mapper mimics this request schema and can be passed
in its place without redefining the service contract. See the
[external-contract example](patterns.md#external-api-contracts).

Model validation runs on changes made through the Model interface. The user
identified the structural exception: mutating a bare inner container does not enter
the surrounding Model. The
[validation examples](patterns.md#validation-through-model-boundaries) include the
corrected nested-record attribute assignment and the plain nested-list exception.
Checking the current implementation also established that Pydantic fields such as
`list[list[A]]` now receive recursive Model wrappers and validate inner mutations.
That field declaration therefore does not reproduce the bare-container exception
in the current checkout. Validation guarantees and rollback/isolation guarantees
are separate concerns.

The status discussion established a division between task-recorded facts and
model-derived summaries, with acknowledgement required for external completion.
The user clarified that inline, nested, or separate status storage depends on the
use case. The [status examples](patterns.md#status-from-facts-and-acknowledgements)
explain these independent choices and the role of Model validation.

Dataset keys are intended to serialize the primary keys of their contents. The
earlier interpretation of `Sample-A` as a deliberately independent Dataset key
beside the normalized `sample-a` alias was incorrect. The sample fixtures and
expected output now use lowercase Dataset keys while retaining mixed-case input
aliases, so normalization remains visible and tested. At the user's request,
top-level validators now enforce key/content agreement for both samples and files,
replacing the proposed test-only alias assertions.

The [table model specification](../../../../docs/superpowers/specs/2026-10-16-table-model-architecture-and-conversions.md#primary-keys)
extends this identity invariant to keyed tables and Dataset conversion. Its APIs
and automatic re-keying remain planned functionality. The
[identity and relationship examples](patterns.md#identity-and-relationship-contracts)
link the fixtures, validators, and intended failure cases.

The user explained why Dataset is the batch abstraction: current async concurrency
and gathering operate across its items through `iterate_over_data_files=True`.
Collections of actual batches may therefore need nested Datasets; domain grouping
alone does not imply that structure. See
[batch boundaries](patterns.md#choose-data-structures-by-their-role). Parallel
execution and async-generator streaming are intended extensions of this abstraction;
their future APIs and implementation coverage are not inferred from that direction.

For task iteration, the agreed future direction is to name the outer dataset
parameter and identify the inner item parameter by name, instead of requiring it
to be first. One pair-valued modifier versus two modifiers is an open design
decision. This is not an implemented API or authorization to change the runtime
as part of the guidance work.

## Water-sample terminology and introductory scope

`tests/integration/novel/full/water_sample_harmonization/models.py` defines
`NormalizedSamplesDataset` as `Dataset[Model[list[NormalizedSampleRecord]]]`.
Its `flows.py` uses list-wrapped mappers, concatenates fetched pages, and stores
record lists under `all_river_samples` and `all_wastewater_samples`.

The user clarified that "batch" in this domain example means measurements from
the same time and place, obtained together through a URL request. It is not an
Omnipy processing batch. The current fixtures are paginated, and one river page
contains two such sample records. Distinguish the sample, the response page, and
the Dataset of requests/responses instead of conflating their grouping levels.
The existing `sample_key`, `sample_alias`, and final `samples` table make "sample"
a consistent domain name to use in place of "batch".

The user explicitly kept this introductory tutorial to one Dataset level.
The earlier recommendation to introduce nested Datasets was based on an overly
broad reading of "batch" and is withdrawn. Commit `28d6cd9d` changes the domain
terminology to "sample" while retaining list-valued Models. The general
nested-Dataset capability remains covered in
`tests/data/test_dataset.py::test_nested_datasets` for actual collections of batches.

## What this guidance does not infer

- No requirement for exactly four stages, three modules, paired files, specific
  statuses, service names, URL schemes, or fabricated identifier formats.
- No blanket ban on `FuncFlowTemplate`, plain dictionaries, tables, serialization,
  copying, event histories, or helper functions. Their use should follow the
  actual control-flow, data, ownership, audit, or boundary requirement.
- No guarantee of parallel DAG branches, automatic retries, or transactional mutation.
- No requirement to use `ContextVar`, constrain every string, split status into its
  own model, or have a separate final-submission model in every domain.
- No expansion into the full engine matrix for each narrative integration test.

The historical target contained two paired-file validation bugs: it compared a
tuple against a set of role strings and checked only samples represented among
the files. Commit `42862757` fixes both and adds focused regression cases; the
current validator checks duplicate roles and visits every declared sample.
The user explicitly instructed agents to suggest fixing obvious bugs rather than
treat them as a golden standard. Preserve intended relationships, verify their
enforcement, and distinguish historical defects from the corrected checkout.
