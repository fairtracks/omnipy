<style>
@page {
    size: letter landscape;
}
</style>

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
| A union-valued `SubmissionPackage` dataset stores tables and a metadata record under fixed string keys. | `SubmissionModel` wraps a record with typed sample/file datasets, metadata, and logistics (service settings and status). | Model a fixed heterogeneous aggregate as a record; use datasets for collections of independently addressable items. |
| Helpers repeatedly call `.to_data()`, cast dictionaries, clone the package, and rebuild it after updates. | Tasks access fields such as `submission.metadata.seq_depot_submission_id` and return enriched models. | Keep typed data intact between processing boundaries; serialization is not the default mutation API. |
| Link checks occur in a helper called by a normalization task; storage checks inspect string prefixes. | Models contain constrained strings, date/URL types, derived filenames, and relationship validators. | Make intrinsic data validity part of the data contract. |
| The submission alias is repeated on every row and sample aliases are separately listed in metadata. | Shared submission context lives on the aggregate; files refer to samples by local alias. | Place metadata at its natural scope and avoid redundant relationships without a contract requiring them. |
| Request dictionaries are built by untyped helper functions. | `SubmissionToSeqDepotPresubmitMapper` and `SampleAndMetadataToBioSampleVaultSubmissionMapper` convert typed inputs to service schemas. | Give schema mapping an explicit reusable model boundary, including multi-input mappings. |
| An imperative `FuncFlowTemplate` manually calls and awaits six steps. | A `LinearFlowTemplate` declares four meaningful stages, including two DAG child flows. | Expose fixed topology through composition; reserve authored control flow for algorithms that need it. |
| Whole-package tasks loop through rows and manufacture all their enriched data. | Iterated async tasks process a single sample or file with shared metadata. | Choose the smallest independently processable unit and use framework iteration. |
| Tasks contain simulated service work and fixture-specific payload assertions. | Tasks map, post to the endpoint URLs in `logistics.services`, and apply results; mocked HTTP endpoints in `conftest.py` implement the services. | Separate external behavior, orchestration, and test expectations. |
| Step labels, transfer tickets, and archive states are updated manually throughout. | Item results support derived readiness states; final submission records explicit acceptance. | Derive state from authoritative facts, and record outcomes that cannot be inferred. |
| No child flows expose the internal coordination. | Extract/process/collect DAGs route models with `param_key_map`, `result_key`, and retained kwargs. | Make subflows meaningful reusable stages, and preserve values needed downstream. |
| The test file contains flow/task definitions plus large literal expectations. | `models.py`, `tasks.py`, `flows.py`, and `conftest.py` leave a short execution/assertion narrative. | Organize by responsibility so the implementation can stand outside the test. |
| The test conditionally awaits a result of uncertain shape. | The test directly awaits the declared async flow and checks output plus `RunState.FINISHED`. | Make the callable contract deliberate and verify it through the appropriate harness. |

## The historical spec was also revised in practice

The requested source documents are:

- `docs/agents/technical/specs/2026-07-09-async-and-sub-flow-testing-schema-design.md`
- `docs/agents/technical/plans/2026-07-10-async-and-sub-flow-testing-plan.md`

Task 9 in the July 10 plan redirects the integration slice to
`docs/agents/technical/plans/2026-07-11-async-and-sub-flow-integration-test-slice-plan.md`.
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

The user also requested explicit names for refined job templates. Refinement with
the default `update=True` inherits the original job name unless `name` is supplied;
a new variable name does not change it. The `.run()` lifecycle rule is now enforced:
it raises inside flows, where direct template calls apply and execute the child.
The async execution review confirmed that `auto_async` adapts coroutine functions
only; async-generator jobs remain lazy streams requiring an async consumer with
either setting. The [execution guidance](patterns.md#execution-policy) distinguishes
these callable forms.

Component packages also supply the structural template. The user clarified that
applied instances should use `_task` or `_flow`, that `Record` primarily denotes
a table-row schema, and that relative imports within and between components are
an in-Omnipy guideline supporting potential extraction into separate repositories.
The component file structure will also be the basis of Omnipy's future plugin
architecture.
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

The typing review clarified that agents should assume correct runtime mimicking,
including for explicitly annotated Models. Report discrepancies and/or suggest
fixes rather than working around them. Static checker limitations are separate;
an Omnipy mypy plugin is future work. The user clarified that `StationListModel`
should inherit `IsListContent[StationModel]`, following `SplitToItemsModelBase`,
not introduce nested lists. The [typing guidance](typing.md) now compares explicit
protocol inheritance in a `TYPE_CHECKING` facade with `mimics`: the former supports
mypy but requires aligned static/runtime declarations; the latter is shorter but
does not support mypy. The user prefers mypy support for additions to Omnipy
library code; examples, tutorials, and tests may instead prefer `mimics` for
readability unless mypy compatibility is part of their purpose. Both options are
documented. The guidance also prefers
targeted `type: ignore` or pyright suppressions over catch-all dictionary or `Any`
casts when a checker cannot express a valid runtime operation.

The user emphasized that the BioSampleVault submission type is the external API
contract itself, currently named `BioSampleVaultSampleSubmissionSchema`. The
task posts it over HTTP to an endpoint URL from `logistics.services`, and the tests
implement the service as a mocked API endpoint, replacing an earlier coroutine
stand-in and later client functions in `services.py`. The mapper mimics this request schema and can be passed
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

The user emphasized that Model validation is robust in normal use and deliberately
avoids unnecessary validation. Agents should usually rely on the Model interface
without reasoning about validation timing. The guidance therefore leads with
ordinary updates and keeps the detailed mechanics in a troubleshooting subsection
for surprising behavior. Bare nested containers, dynamic element conversion, and
specific known issues documented in Model tests are the exceptions to investigate
when relevant, not reasons to add routine defensive validation to dataflows.

The user clarified that dynamic element conversion does not repair a missing
stored Model boundary. Indexing creates a temporary wrapper that is not inserted
into the parent, so changes to it are not retained there. Direct `.content`
mutation bypasses validation. Validation runs at the Model receiving the
state-changing operation and does not propagate to parents or siblings; an
existing child Model of the required type can also be accepted without content
revalidation when its parent validates. The validation reference includes the
user's nested-list example showing these distinct effects. Dataset revalidation
belongs to its own dict operations. Automatic revalidation of existing Models
at job input and output boundaries is future work intended to simplify dataflow
development, not a current guarantee.

The status discussion established a division between task-recorded facts and
model-derived summaries, with acknowledgement required for external completion.
The user clarified that inline, nested, or separate status storage depends on the
use case. Dataset `PendingData` and `FailedData` markers are also an alternative
to direct record status updates; the use case may require either representation
or both. The [status examples](patterns.md#status-from-facts-and-acknowledgements)
explain these choices and the role of Model validation. Atomic rollback of jobs
is planned future work. The general component's `require_all_items` task supplies
the current check for failed/pending entries before stages requiring complete data.
Item-completion policies could later become job modifiers; no such modifier API
is currently implemented.

The user clarified that straightforward Model validations already act as
executable assertions and reduce the need for separate test assertions. Narrative
tests should demonstrate the scenario's outcome; focused cases remain useful for
complex validation logic. Plain-data comparisons through `to_data()` are often
appropriate, especially when nested JSON Model structure is not under test.

The brokering example previously used a sequential service ID counter isolated per
test, allocating IDs after an async yield. Its expected payload fixes IDs to particular
samples, so changing the relative waits or HTTP request order can change those
assignments. This concerns the fixture's allocation policy, not Omnipy's
association of each task result with its Dataset key.
A controlled 20 ms wait for `sample-a` before allocation in the actual brokering
flow reversed the two sample IDs while preserving their request/response associations.
The service now looks up IDs in a per-test mapping keyed by normalized sample
alias. An event-controlled check during development made `sample-b` register before
`sample-a` and verified the same expected submission payload. The user removed
that temporary regression test and its fixture from the final implementation.

Dataset keys are intended to serialize the primary keys of their contents. The
earlier interpretation of `Sample-A` as a deliberately independent Dataset key
beside the normalized `sample-a` alias was incorrect. The sample fixtures and
expected output now use lowercase Dataset keys while retaining mixed-case input
aliases, so normalization remains visible and tested. At the user's request,
top-level validators now enforce key/content agreement for both samples and files,
replacing the proposed test-only alias assertions.

The [table model specification](../../../../docs/agents/technical/specs/2026-10-16-table-model-architecture-and-conversions.md#primary-keys)
extends this identity invariant to keyed tables and Dataset conversion. Its APIs
and automatic re-keying remain planned functionality. The
[identity and relationship examples](patterns.md#identity-and-relationship-contracts)
link the fixtures, validators, and intended failure cases.

The user subsequently preferred a Dataset-native feature over the proposed shared
Model validator, with a dedicated type parameter for primary-key declarations.
The [revised proposal](../../../../docs/agents/technical/specs/2026-10-25-dataset-primary-key-validation-proposal.md)
covers Datasets of dicts or Pydantic records, iterators of key/value pairs or
Pydantic records, and key checks/derivation after item parsing without losing
duplicate occurrences. Rekeying and continuous key maintenance are now in scope,
not a deferred extension. The implemented
[`PrimaryKeyDatasetModel`](../../../../src/omnipy/components/general/models.py)
supplies the intermediate conversion approach, using shared declarations and
serialization from [`data.primary_key`](../../../../src/omnipy/data/primary_key.py).
It supersedes the example-local prototype's first-field-only conversion and
overwrite behavior: composite keys and serialized-key collision rejection are
implemented and covered by
[component tests](../../../../tests/components/general/test_models.py). Key
recomputation occurs during conversion; continuous maintenance and the broader
Dataset-native input contract remain planned.

The user explained why Dataset is the batch abstraction: current async concurrency
and gathering operate across its items through `iterate_over_data_files=True`.
Collections of actual batches may therefore need nested Datasets; domain grouping
alone does not imply that structure. See
[batch boundaries](patterns.md#choose-data-structures-by-their-role). The user
subsequently corrected the description of streaming: async-generator streaming is
already supported. Parallel execution remains an intended extension; future APIs
and implementation coverage are not inferred from that direction.

The user also clarified that typed Dataset blueprints are planned for fixed
aggregates with different member types. The current recommendation to use a
wrapped Pydantic schema applies until that functionality is available. Conversion
guidance covers scalars, collections, and other supported types as well as Pydantic
schemas. Existing Pydantic types belong alongside Omnipy's domain primitives, and
named field types make shared contracts reusable.

The Dataset-validator example previously checked duplicate loan references across
pages. The user identified pagination as a separate fetching concern: combine
pages into one container, then validate domain records and collection-wide rules.
The example now demonstrates key/content agreement on a record Dataset. The
[fetching guidance](remote-loading.md#merge-response-pages-into-a-typed-dataset)
explains preserving duplicate occurrences through concatenation and detecting
collisions before constructing a mapping keyed by normalized record identity.
Response validation can still happen during loading.

For task iteration, the agreed future direction is to name the outer dataset
parameter and identify the inner item parameter by name, instead of requiring it
to be first. One pair-valued modifier versus two modifiers is an open design
decision. This is not an implemented API or authorization to change the runtime
as part of the guidance work.

Replacing the brokering coroutine stand-ins with mocked HTTP endpoints produced
several decisions. Service clients that call job templates are not a reuse problem
just because direct template calls require a flow context: calling templates inside
flows and using `.run()` outside them is Omnipy's API. In an integration test, a
plain HTTP client would bypass the Omnipy functionality the test should exercise.
The user chose `Model.post()` and `Dataset.post()` as the request counterpart of
`load()`: a single URL for all Dataset items, a `response_cls` for the service's
response contract, JSON only for now, and `post_to_url`/`async_post_to_url` tasks
next to `load_urls`. POST requests got separate retry statuses in the host
configuration, as they are not idempotent. `post_json_to_api_endpoint` previously
posted one body to many URLs; it now posts each data item to one URL. Posting each
item to the URL with the same key in an `HttpUrlDataset` will be needed, but the user
postponed its design; it is future work, not an available API.

Passing each service URL to the brokering flow as a separate keyword was replaced
by settings in the submission. The user chose to group the service settings with
the status in a `logistics` member, separate from the content sent to the Sequence
Depot, as the place for other broker-side settings such as authentication. The
name was chosen over `brokering`, `handling`, `control` and `admin` because it
reads well in paths such as `submission.logistics.services.biosamplevault.urls['samples']`
and is understandable in a tutorial. Each service has its own schema, so per-service
settings have an obvious place. Secrets handling is a missing Omnipy feature, to
be designed separately: until then, do not store credentials in dataflow data,
which is printed, compared and possibly persisted with job outputs.

Moving the status into `logistics` exposed that Models of Pydantic models revalidated
their whole content on every attribute read, converting it to raw data and parsing
it again. Every read thus replaced all nested objects, disconnecting references to
nested Models taken earlier, and cost time proportional to the content (about 0.1 ms
per Dataset item per read). The revalidation predates the wrapping of nested
Pydantic models in Omnipy Models, which now validate their own changes. Its
remaining effect was to rerun the validators of the parent after nested in-place
changes, which no other Model or Dataset does. The user chose to remove it, so that
Models of Pydantic models behave like other Models: a change validates the Model
receiving it, and the validators of parents rerun only on changes through the parent
or explicit validation.

Rerunning the validators of the parents is instead planned at job boundaries, as a
job modifier. It must rerun the parents' own validators rather than only accept
already validated nested Models, and it must validate inputs as well as outputs, to
also catch changes made outside of jobs. Derived fields are planned as
`@computed_field`s with Pydantic v2, computed on access. Pydantic v2 does not itself
rerun parent validators after nested changes, so it does not remove the need for the
modifier. Propagating validation from changed nested Models to their parents was
considered and set aside: it requires links from nested Models to possibly several
parents, revalidates all ancestors on every change (quadratic in loops over large
Datasets), and interacts with the snapshot machinery. Its remaining benefit, errors
at the line of the change rather than at the job boundary, mainly matters in
interactive use. The user chose to cover it explicitly with `Model.updating()`, a
context manager rerunning the validators once when the block ends, with rollback in
interactive mode. Its rollback point is prepared lazily, like other state-changing
operations, rather than by validating when the block starts. Datasets currently have
neither `validate_content()` nor `updating()`. The
[investigation summary](../../../../docs/agents/technical/explorations/2026-11-11-nested-model-validation-and-parent-validators.md)
records the findings, alternatives, decisions and possible future improvements.

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
