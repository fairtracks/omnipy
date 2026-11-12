# Dataflow patterns and API details

Paths below are relative to the repository root. Check the current implementation
when extending these patterns; the examples describe the APIs available when this
guidance was written.

Read the sections relevant to the current design decision:

| Decision | Sections |
| --- | --- |
| Data shape and identity | [Structures and batches](#choose-data-structures-by-their-role), [constrained fields](#constrained-field-contracts), [primary keys and relationships](#identity-and-relationship-contracts), [validators reading other fields](#validators-depending-on-other-fields), [Dataset validators](#dataset-level-validation), [mutation validation](#validation-through-model-boundaries) |
| Data reuse and boundaries | [Generic Models/Datasets](#reusable-models-and-datasets), [conversions](#model-transformations), [external APIs](#external-api-contracts) |
| Static interfaces and HTTP ingestion | [Runtime mimicking and typing](typing.md), [paging URLs and Dataset loading](remote-loading.md) |
| Execution and composition | [Templates and modifiers](#reusable-jobs-templates-and-modifiers), [routing](#routing-rules-that-matter), [callable types](#callable-types-and-composed-flows), [iteration and ownership](#dataset-iteration-and-ownership) |
| State and completion | [Failure inspection](#inspect-current-failure-and-pending-results), [status from facts and acknowledgements](#status-from-facts-and-acknowledgements) |
| Implementation | [Catalog example](#example-publish-a-catalog), [component structure and naming](structure-and-naming.md) |
| Review and verification | [Readability](#readable-contracts-and-documentation-reuse), [narrative tests](#validation-and-narrative-tests), [mock services](#mock-services-and-failure-scenarios), [source map](#source-map) |

## Readable contracts and documentation reuse

The dataflow is both executable code and an inspectable contract for agent output.
A human should be able to read the models and flow declarations to understand
what the agent has implemented: accepted inputs, validated relationships,
transformations, external operations, batch boundaries, and expected outputs.
Make those choices visible in the types, validators, named stages, and routing.
Tests verify that the implementation fulfills that contract.

Organize code into cohesive groups separated by blank lines: input preparation,
flow invocation, output comparisons, external-call evidence, and execution state
are different concerns. Keep assertions about the same concern together. Apply
the same grouping to schema fields, validators, fixtures, and task bodies where
it makes their responsibilities easier to see.

Use small functions with a clear responsibility and an intention-revealing name.
When a block grows complex, repeats, or needs its own explanation, consider
extracting it into a function, fixture, task, or child flow appropriate to its
role. Keep the main scenario readable at one level of abstraction. Do not split
every assertion into a helper or hide the contract in an opaque `check_everything`
function; the reader should still see what is executed and what is verified.

Conventions from the brokering example, which make the modules readable as a
tutorial without a separate text:

- The module docstring of `models.py` explains abbreviations used in names, such
  as `SeqDepot` for the Sequence Depot. Introduce an abbreviation only for a long
  name used in many places, and use it consistently.
- Schemas and reusable classes carry a one-line docstring saying what they hold
  and where their contents come from, e.g. "Samples keyed by their local id, from
  a list of samples or a Dataset."
- Fields with different roles are separated by blank lines and a comment, e.g.
  "Settings, provided as input and only read by the dataflow" and "State, derived
  from the submission content as the dataflow proceeds" in `LogisticsSchema`.
- `tasks.py` groups its task templates under comment headings, e.g. "Helper task
  templates" for extraction and collection and "Core task templates" for the
  operations.
- A task names the URL and the mapped request in variables, then makes the call,
  then applies the response, each group separated by a blank line.
- A derived value, such as a staging path built from several fields, is one
  expression, e.g. a chain of `//` on the URL path, rather than a sequence of
  statements.
- Comments explain a non-obvious reason, such as why a guard is needed, and are
  omitted where the names already say what happens.

Integration scenarios also serve as tutorials. Their readability should reveal
the characteristic Omnipy mechanisms rather than bury them inside general Python
helpers:

| Mechanism | What a reader should see |
| --- | --- |
| Declarative composition | A flow's child list and refinements describe the stages and how data moves between them. |
| Models as contracts | Schemas, constraints, validators, and converter source/target types explain data meaning and transformations. |
| Model mimicking | Ordinary field access, indexing, and supported operations work directly on typed wrappers. |
| Dataset batches | Types and iteration modifiers express processing across items without authored per-item orchestration loops. |
| Mixed job types | Tasks, subflows, and Model/Dataset constructors are composed directly where they fit the work. |
| Mixed callable types | Synchronous work and asynchronous I/O retain their natural forms; supported generators are used when the scenario needs them. |

For example, the sequence-submission flow's four children expose allocation,
registration, transfer, and final submission. Its child DAGs reveal the
extract/process/collect structure. The water-sample flow combines an async fetch,
synchronous collection tasks, and a Dataset class as a conversion stage. These
are readable demonstrations of composition without making every child the same
job or callable type. Follow the current routing/callable rules when composing
functions, coroutines, generators, or async generators.

Prefer model-based conversion, Dataset operations, existing collection tasks, and
iteration modifiers to handwritten batch-processing loops. A Python loop inside
a domain algorithm or relationship validator can still be the clearest expression
of that rule. The aim is for the dataflow's processing structure to be declarative
and directly visible. Moving an orchestration loop into an opaque helper does not
achieve that aim.

Keep the tested model/task/flow definitions reusable in documentation. Fixture
setup and expected results can remain test-specific; the implementation modules
should be importable without depending on pytest. For a test deliverable, use the
pytest scenario as the execution example. Do not generate a standalone demo
runner to demonstrate reusability. Documentation can reuse or extract the tested
definitions and invocation without a second execution harness.
Follow root `AGENTS.md` for documentation
imports, setup, and output display. Preserve the external API contracts when
demonstrating their simulated implementations.

Choose a focused teaching scope. An introductory example should reveal its useful
combinations of features without adding Dataset hierarchies, callable variants,
or abstractions solely for completeness. Human review should be possible at the
top-level flow first, then through meaningful subflows and their data contracts.

For module responsibilities, class and operation names, and component import
conventions, see [structure and naming](structure-and-naming.md).

## Choose data structures by their role

| Role | Default representation | Reason |
| --- | --- | --- |
| A record with named, constrained fields | Pydantic schema wrapped in `Model[Schema]` | Validation and direct field access |
| An Omnipy batch of processing items | `Dataset[ItemModel]` | Item identity and dataset operations; an item can be a record, hierarchical data, a response, or a table |
| A collection of actual Omnipy batches | `Dataset[Dataset[ItemModel]]`, optionally using named subclasses | Use when both batch and item levels need Dataset semantics |
| Fixed aggregate of different members | Pydantic schema containing typed datasets/models, wrapped in `Model` | Each member has a specific type; typed Dataset blueprints are planned |
| A sequence intrinsic to one value or an external payload | `Model[list[...]]` or a suitable existing model | Preserve value/payload structure; dataflow batches use datasets |
| Tabular wrangling | Existing table/Pandas models and datasets | Use the component's operations |
| Type conversion, including schema translation | `ConverterModel[Source, Target]` | Reusable typed conversion of scalars, collections, records, and other supported types |

A heterogeneous dataset is useful when its varying members are genuinely data
items. With current APIs, it is a poor default for a fixed record whose string keys
are being used as field names and whose union type forces casts at every access.
Planned typed Dataset blueprints will give fixed members their own declared types;
until that functionality is available, use a wrapped Pydantic schema for this role.

Choose an item's boundary from the dataflow operations, not from every collection
in its schema. A sample may contain several measurements from one time and place.
Those measurements can remain a list inside the sample record when they are
received and transformed together. A response page can likewise contain several
sample records without becoming an inner Dataset.

Use distinct terminology in tutorials:

| Term | Meaning in the water-sample example |
| --- | --- |
| Sample | A domain record containing measurements from one time and place |
| Page | One response to a URL request; the fixture can return several samples per page |
| Batch | The Dataset of items processed together by Omnipy, such as a set of URLs or fetched responses |

The water-sample harmonization example is intended as an introduction. Keep its
single Dataset level: fetch URL pages, combine their sample lists, normalize the
records, and flatten them into tables. Its list-valued Models describe structured
data within the items. The two source groups can remain dataset items containing
normalized sample lists; neither the sample's measurements nor the source grouping
requires a Dataset of Datasets. Calling a domain record a "batch" obscures this
distinction; prefer "sample" in authored names. Preserve externally imposed field
names when required by a real service contract, explaining the terminology instead
of silently changing that contract.

For dataflows that actually need batches within a collection, for example,
`class SampleBatch(Dataset[SampleModel]): ...` and
`class SampleBatches(Dataset[SampleBatch]): ...` express those two levels. Then
`batches['batch-1']['sample-A']` accesses a sample Model through their keyed
boundaries. Use this structure when it serves the dataflow; do not introduce it
solely to mirror domain grouping or to demonstrate every available feature.

The reason for this batch rule is execution as well as representation. Today an
async job with `iterate_over_data_files=True` creates a coroutine task per dataset
item, gathers their completion, and records each result or failure under its input
key. The Dataset defines the batch; the iterated job supplies the scheduling and
result collection. Constructing a Dataset by itself does not start execution.

For a Dataset containing three URL Models, the framework can coordinate three
requests. Each response may contain many measurements; their count does not
change the request count. A hand-written request loop over several URLs buried
inside one dataset item would hide those requests from framework iteration.
Conversely, a pure mapper transforming measurements within one response does not
need a separate job for each measurement. If a later stage needs independently
scheduled operations on individual samples, expose those samples as dataset items
at that stage. Dataset boundaries can change between stages to match the work.
Nested Datasets preserve actual batch boundaries; nesting alone does not request
recursive scheduling of every level.

Streaming through async generators is already supported by tasks and flows; see
[callable types and composed flows](#callable-types-and-composed-flows) for the
current composition rules. Parallel execution remains an intended extension of
the batch abstraction. Keep Dataset central when designing batch contracts so
execution models can build on the same structure, while checking the supported
iteration and callable combinations for the chosen execution mode.

Use existing domain primitives before inventing regex checks in tasks, for example
`DateModel` and `HostUrlModel` subclasses, and Pydantic types such as `PositiveInt`,
`NonNegativeFloat`, and `AnyHttpUrl`. A `HostUrlModel` subclass restricts a URL
field to the schemes of its storage or service by overriding `_get_scheme_filter()`,
as `S3UrlModel` and `FtpUrlModel` do in the brokering models; `HostUrlDataset` holds
named URLs of mixed schemes. A validator can fill a missing value from
another field, such as a filename from a source URL. Do not duplicate those rules
in a normalization task. Honor field order, missing earlier fields, and default
validation behavior in the repository's Pydantic API; see
[validators depending on other fields](#validators-depending-on-other-fields).

Repository implementation schemas currently use `import omnipy.util.pydantic as
pyd`, which exposes the v1-shaped compatibility API, including `validator`. Do not
assume a TODO about Pydantic v2 computed fields means they are available through
this wrapper. User-documentation imports follow root `AGENTS.md`; verify that
their Pydantic version matches the example before adapting implementation code.

Operate through the Model's supported mimicked interface, including direct field
updates, container indexing/iteration, tuple unpacking, and domain methods or
operators. Keep these wrappers between stages instead of calling `.to_data()` to
process the data or `.content` whenever another function is called. Unwrap only
when the consumer requires the underlying object or a plain-data representation.

`Model` supplies runtime mimicking. `om.mimics(Schema)` makes a concrete wrapper's
interface visible to supported static checkers; it does not enable mimicking or
perform validation itself. Mypy does not support this typing technique; use the
configured basedpyright check and avoid dictionary casts as a substitute for
understanding a typing limitation.
See [typing examples](typing.md) for built-in collection support, custom typed
Models and Datasets, and protocols for generic interfaces and reusable consumers.

## Constrained field contracts

Choose the most specific type supported by the actual contract. A currency or
state with a known set of values belongs in an Enum or Literal; an identifier
should not accept an empty string when the contract requires an identity. Numeric
fields should express bounds and whether non-finite values are meaningful.
Apply these choices to internal records and external request/response schemas,
preserving each contract's accepted values.

Prefer named types for reusable contracts: an Enum, a type alias, a constrained
Pydantic type, or an Omnipy Model can give the same meaning and constraints to
fields in several schemas and to task signatures. Define a shared contract once
and specialize it where a consumer needs different constraints. Field-local
constraints remain useful for rules specific to one field.

For example, if a service supports exactly NOK and EUR and allows a zero amount:

```python
from typing import Literal

import omnipy.util.pydantic as pyd


class RegistrationRequestSchema(pyd.BaseModel):
    exhibition: str = pyd.Field(min_length=1)
    reference: str = pyd.Field(min_length=1)
    title: str = pyd.Field(min_length=1)

    amount: float = pyd.Field(ge=0, allow_inf_nan=False)
    currency: Literal['NOK', 'EUR']
```

Use `NonNegativeFloat` for a simple nonnegative bound, or combine constraints in
`Field` as above. Use `PositiveFloat` or `gt=0` when zero is invalid; do not weaken
an explicitly positive-value requirement to nonnegative. Normalize identifiers
before validating their canonical form; `min_length=1` alone does not reject
whitespace-only strings. Add a regex when the domain defines an identifier
grammar, not merely because the fixture IDs happen to share a prefix or shape.
A three-uppercase-letter pattern checks currency-code shape, not membership in
the supported currency set. Do not infer that set from the currencies present in
one test. Prefer existing domain types where they already encode the contract.

## Identity and relationship contracts

The intended pattern is that Dataset keys serialize the primary keys of their
contents. Container lookup and a record's primary-key field serve different uses,
but they represent the same identity. An external service's assigned identifier
can remain a separate attribute; receiving it does not change the chosen primary
key of the internal record.

In the submission example, `local_sample_id` is the sample's primary key. The
[input fixtures](../../../../tests/integration/novel/full/sequence_data_brokering/conftest.py)
are lists of records with raw ids such as `local_sample_id='Sample-A'`. The
`samples` and `files` fields of `SeqDepotSubmissionPayloadSchema` are `PrimaryKeyDatasetModel`
subclasses (see below), so the item schema normalizes each id and the Dataset is
keyed by the result, e.g. `sample-a`. Keys are derived rather than written twice
in the input. The
[integration test](../../../../tests/integration/novel/full/sequence_data_brokering/test_sequence_submission_brokering.py)
constructs the Model through that validation and compares the full enriched output,
keyed by the normalized ids. Retain mixed-case raw ids so the scenario exercises
normalization.

The [table primary-key specification](../../../../docs/agents/technical/specs/2026-10-16-table-model-architecture-and-conversions.md#primary-keys)
extends this concept to tables. It defines deterministic serialization, retained
visible key fields, and rejection of serialized-key collisions. Single string
keys serialize to themselves; composite keys use the specified escaping and
delimiter rules. Its
[Dataset interoperability section](../../../../docs/agents/technical/specs/2026-10-16-table-model-architecture-and-conversions.md#dataset-interoperability)
describes how keyed rows become Dataset items. These table APIs and automatic
re-keying are planned functionality, not capabilities to assume in generated code.
Use the identity invariant now while constructing keys explicitly with current
APIs. Changing or normalizing a primary key must preserve agreement with the
Dataset key and must not silently collapse records with colliding keys.

The [Dataset primary-key proposal](../../../../docs/agents/technical/specs/2026-10-25-dataset-primary-key-validation-proposal.md)
places the declaration on Dataset through a dedicated primary-key type parameter,
not a shared validator on containing Models. Its scope includes dict and Pydantic
record items, keyed-pair and record iterators, post-parse key validation/derivation,
explicit rekeying, and continuous maintenance through supported mutations. This
is planned functionality, not a current Dataset API.

Until then, `PrimaryKeyDatasetModel` in
[`omnipy.components.general.models`](../../../../src/omnipy/components/general/models.py) supplies intermediate
conversion from a Dataset or list Model of Pydantic records to a Dataset keyed
by record fields. Declare ordered fields with `PrimaryKey[Literal['field'], ...]`
from [`omnipy.data.primary_key`](../../../../src/omnipy/data/primary_key.py).
The converter supports composite keys and rejects serialized-key collisions
before constructing the result. It recomputes input Dataset keys without changing
the source mapping; it does not continuously maintain keys after conversion.
As a field of a containing Model, keys are recomputed whenever that Model
validates, e.g. on assignment or at the end of `updating()`. Decorate a subclass
with `@mimics(...)` of the corresponding Dataset class for static typing, as
`SubmissionSamplesDataset` does. Dict-valued item Models and direct iterator input are part of the planned
Dataset-native feature, not guarantees of this converter. See the
[component tests](../../../../tests/components/general/test_models.py) for current behavior.

Place relationship validation where its inputs are available. Concrete examples
in the [submission models](../../../../tests/integration/novel/full/sequence_data_brokering/models.py)
include:

- `SubmissionSampleSchema.local_sample_id` uses `StrippedLowerStr` to normalize
  the local primary key. `SeqDepotSubmissionFileSchema` constrains file roles, checksum
  format, and URL types; `_extract_file_name_from_source_storage_uri` derives the
  filename within that record.
- `SubmissionSamplesDataset` and `SubmissionFilesDataset` key samples and
  files by their normalized local ids, keeping keys and contents in agreement.
  For other reusable Dataset-local invariants, prefer validators on the Dataset
  subclass; see [Dataset-level validation](#dataset-level-validation).
- `SeqDepotSubmissionPayloadSchema._file_sample_ids_exist` has access to both sample and file
  Datasets and checks that each file's normalized reference identifies a sample.
- `SeqDepotSubmissionPayloadSchema._samples_have_one_read1_and_one_read2` checks the paired-file
  rule at the same aggregate boundary: it rejects duplicate roles while reading
  files, then checks every declared sample, including samples with no files.

For a contract requiring exactly one `read1` and one `read2` file per sample,
the expected validation cases are:

| Files associated with a required sample | Expected result |
| --- | --- |
| One `read1`, one `read2` | Accept |
| Two `read1`, one `read2` | Reject the duplicate role |
| Only `read1` | Reject the missing role |
| No files | Reject missing coverage |
| A file references an absent sample | Reject the invalid reference |

Check coverage over all required parent records, including those with no children.
Check duplicate occurrences before reducing children to a set of roles. These
cases are enforced by the submission example's paired-file validator. Generalize
the relationship and coverage principles, not this domain's exact number of files
or role names. Focused tests cover duplicate roles, a sample without files and a
BioSample Vault id assigned to two samples.

### Validators depending on other fields

With the repository's Pydantic v1 API, a field validator receives the fields
declared before it in `values`. A field that failed validation is left out of
`values`, and the later validators still run, so a validator reading an earlier
field must allow for its absence. Put the guard around the dependent block, and
say in a comment why the field can be missing, so that the guard is not mistaken
for an optional field:

```python
class _SubmissionDict(TypedDict):
    samples: SubmissionSamplesDataset
    files: SubmissionFilesDataset
    metadata: SubmissionMetadataModel


class SubmissionSchema(SeqDepotSubmissionPayloadSchema):
    ...

    @pyd.validator('logistics')
    def _update_biosamplevault_status(
        cls,
        logistics: LogisticsModel,
        values: _SubmissionDict,
    ) -> LogisticsModel:
        # Missing if the samples failed validation, which is reported separately
        if 'samples' in values:
            status = logistics.status
            samples = values['samples'].values()
            if len(samples) == 0:
                status.biosamplevault_status = 'N/A'
            elif all(sample.biosamplevault_sample_id is not None for sample in samples):
                status.biosamplevault_status = 'completed'
            else:
                status.biosamplevault_status = 'pending'

        return logistics
```

A `TypedDict` of the earlier fields types `values`, giving typed access to
the Models in it instead of `dict`. Declare the dependent field after the fields
it reads, and give it a default or `always=True` when the validator must also run
without an input value. A `root_validator(skip_on_failure=True)` is the alternative
when the rule concerns the record as a whole rather than one field.

## Dataset-level validation

Prefer a validator on a Dataset subclass when all inputs to the invariant are
within that Dataset: uniqueness across items, key/content agreement,
or relationships among its entries. Dataset is already a Pydantic-backed data
contract. With the current compatibility API, `@pyd.validator('data')` receives
the parsed mapping of keys to item Models; return that mapping after checking it.

For example, given a `LoanModel` whose schema normalizes `loan_ref`, check that
each Dataset key matches its record's normalized reference:

```python
import omnipy as om
import omnipy.util.pydantic as pyd


class LoanDataset(om.Dataset[LoanModel]):
    @pyd.validator('data')
    def _keys_match_loan_references(
        cls,
        loans: dict[str, LoanModel],
    ) -> dict[str, LoanModel]:
        for key, loan in loans.items():
            if key != loan.loan_ref:
                raise ValueError(
                    f'Dataset key {key!r} does not match loan reference {loan.loan_ref!r}'
                )
        return loans
```

The flow can use `LoanDataset` directly as its validating constructor, and
downstream operations can accept that Dataset type. The loop expresses the
invariant; it does not schedule per-item work. Fetching, combining pages, and
detecting duplicate records before keying belong to the
[page-to-record stages](remote-loading.md#merge-response-pages-into-a-typed-dataset).

Avoid adding a separate `Model[LoanDataset]` solely to use `_parse_data()`.
An outer Model should have an independent contract or conversion purpose that
justifies the additional type. A Dataset validator keeps the batch interface
directly available without another wrapper or `mimics` declaration.

Keep normalization and individual-record constraints in item Models. Keep checks
that need several Datasets or shared metadata on the containing schema. A
Dataset-local rule belongs on the reusable Dataset even when a particular flow
also puts that Dataset inside an aggregate.

The example accepts completed record data. If such a Dataset is used as a live
async output, design how its validators handle `PendingData` and `FailedData`;
markers are not record Models. Alternatively, construct the constrained Dataset
after checking completion as in [failure inspection](#inspect-current-failure-and-pending-results).
See [Validation through Model boundaries](#validation-through-model-boundaries)
for normal updates and guidance on investigating unexpected validation behavior.

## Validation through Model boundaries

Rely on Model validation in normal dataflow code. Supported methods, item
assignment, and attribute assignment through the Model interface maintain valid
data automatically. The design avoids unnecessary validation by reusing already
validated Models. Agents generally do not need to track when validation runs or
add manual revalidation steps, except for the validators of parents after in-place
changes to nested Models, described at the end of this section.

For example, appending through a list Model validates and coerces the new element:

```python
import omnipy as om
import omnipy.util.pydantic as pyd

numbers = om.Model[list[int]]([2, 4, 5])
numbers.append('7')
assert numbers.content == [2, 4, 5, 7]
```

For nested mutable containers declared directly in a Model, put a Model between
the container levels so that inner updates use the same validated interface:

```python
nested = om.Model[list[om.Model[list[int]]]]([[2, 4, 5]])
nested[0].append('7')
assert nested[0].content == [2, 4, 5, 7]
```

This applies to nested dictionaries too; lists of scalar values need only the
Model around the list. These list examples describe value structure, not a change
to the Dataset rule for dataflow batches.

For Models wrapping Pydantic records, Omnipy supplies stored nested wrappers.
Field and container updates therefore have a Model boundary at which to validate.
Appending a record and assigning one of its fields both validate in this example:

```python
class A(pyd.BaseModel):
    a: int
    b: str


class B(pyd.BaseModel):
    aa: list[A]


record = om.Model[B]({'aa': [{'a': 3, 'b': 'abc'}]})
record.aa.append({'a': '4', 'b': 123})
assert record.aa[1].a == 4
assert record.aa[1].b == '123'

record.aa[0].a = '5'
assert record.aa[0].a == 5
```

The current implementation recursively wraps container types in Pydantic fields,
too. Consequently, a field declared as `list[list[A]]` has a Model between its
lists at runtime, so mutations reach a stored Model:

```python
class GroupedB(pyd.BaseModel):
    aa: list[list[A]]


grouped = om.Model[GroupedB]({'aa': [[{'a': 3, 'b': 'abc'}]]})
inner = grouped.aa[0]
assert isinstance(inner, om.Model)
inner.append({'a': '4', 'b': 123})
assert inner[1].a == 4
```

Validation runs at the Model receiving a change. Changing a nested Model in place
validates that Model, but does not rerun the validators of its parents: neither the
rules of a parent Model or Dataset, nor the fields a parent derives with validators.
When those depend on the changed data, make the change through the parent: assign
the changed member back, or make the change inside `with model.updating():`, which
reruns the validators of the Model when the block ends. This is how the brokering
example's allocation task lets the submission derive its status:

```python
with submission.updating():
    submission.metadata.seq_depot_submission_id = response.seq_depot_submission_id
```

The block can also group changes in several steps, validating the Model once when it
ends. Changes inside the block can pass through states breaking its rules. Renaming a sample changes its local id and the references from
its files, and the submission is only valid again after both. The Dataset key
follows the local id when the block ends.
In interactive mode, the Model is reverted to its state at the start of the block if
validation fails or the block raises:

```python
with submission.updating():
    submission.samples['sample-a'].local_sample_id = 'sample-c'
    for file in submission.files.values():
        if file.local_sample_id == 'sample-a':
            file.local_sample_id = 'sample-c'
```

`validate_content()` reruns the validators of a parent Model directly. Datasets have
neither method yet, so assign the changed item. The behavior is pinned by
`test_parent_validators_rerun_only_on_validation_of_or_changes_through_the_parent`
and `test_derived_fields_of_pydantic_model_update_only_on_changes_through_the_parent`
in `tests/data/test_model.py`, and
`test_dataset_validators_rerun_only_on_changes_through_the_dataset` in
`tests/data/test_dataset.py`. Validation at job boundaries, rerunning the validators
of the parents of job inputs and outputs, is planned as a job modifier; see the
known-issue test `test_job_boundaries_validate_parents_of_changed_nested_models_known_issue`
in `tests/compute/test_task.py`. With Pydantic v2, `@computed_field` is planned for
derived fields, which removes the need to rerun validators to update them.

These patterns are sufficient for ordinary dataflow development. The details in
[Troubleshooting unexpected validation behavior](#troubleshooting-unexpected-validation-behavior)
are for investigating surprising results.

### Troubleshooting unexpected validation behavior

Consult these details when an update does not behave as expected. Local validation
and reuse of existing Models are intentional ways to avoid unnecessary work.
The known limitations involving bare nested containers and dynamic element
conversion are described here; other specific known issues are documented in
`tests/data/test_model.py`. Use the relevant case when diagnosing an issue rather
than adding defensive validation to every stage of a dataflow.

#### Bare nested containers and dynamic element conversion

Two or more container levels without a stored Model between them do not provide
a validation boundary for inner mutations. With dynamic element conversion
disabled (the default), indexing a `Model[list[list[int]]]` returns a bare inner
list. Calling that list's `append` does not pass through the outer Model, so the
string remains unvalidated:

```python
nested = om.Model[list[list[int]]]([[2, 4, 5]])
nested[0].append('7')
assert nested.content == [[2, 4, 5, '7']]
```

Enabling dynamic element conversion does not fix this structure. `__getitem__()`
then creates a new Model for the returned inner list, but does not insert it into
the parent. Mutating that temporary Model validates its own content; the changes
are not retained in the parent. For example, with conversion enabled,
`nested[0].append('7')` leaves `nested.content` unchanged. Use stored nested Models
as shown in [Validation through Model boundaries](#validation-through-model-boundaries).
Pydantic fields receive these wrappers automatically; the issue concerns actual
Model boundaries, not the number of brackets in the source annotation.

#### Direct content mutation and validation scope

Directly mutating an unwrapped object obtained through `.content` will bypass
validation; assigning to `.content` also bypasses it. The following diagnostic
example deliberately bypasses the normal interface to show which later operations
validate which levels:

```python
parent = om.Model[list[om.Model[list[int]]]]([[1, 2, 3], [5, 6, 7]])

parent[0].content.append('4')  # Direct content mutation bypasses validation.
assert parent.to_data() == [[1, 2, 3, '4'], [5, 6, 7]]

# The second child's method validates that child. Parent indexing is read-only.
parent[1].append('8')
assert parent.to_data() == [[1, 2, 3, '4'], [5, 6, 7, 8]]

parent.content += [('9',)]  # Content mutation and assignment both bypass validation.
assert parent.to_data() == [[1, 2, 3, '4'], [5, 6, 7, 8], ('9',)]

# The parent's method validates the outer list and converts the newly added values.
parent.append(['10'])
assert parent.to_data() == [[1, 2, 3, '4'], [5, 6, 7, 8], [9], [10]]
```

Validation runs at the level of the Model receiving a state-changing operation
and does not propagate to its parents or siblings. Proxied methods are assumed
to change state unless recognized as read-only; `__getitem__()` on a parent is
not a state-changing operation.

The first child already has the required type `Model[list[int]]`, so validation
of the outer list accepts that existing Model without revalidating its content.
Reusing a correctly typed Model avoids redundant work in normal use. Here its
unvalidated `'4'` survives both the sibling's mutation and the parent's method
call because the example deliberately changed its content outside that validated
interface. Operation-triggered validation at one Model boundary is not recursive
revalidation of every existing Model below it.

Validation can also be triggered explicitly with `model.validate_content()`, which
revalidates that Model's current content in place.

Dataset revalidation happens through its own dict operations, such as assigning
raw data to an entry. Accessing an item or mutating its content does not revalidate
the containing Dataset. These mapping operations do not all perform full
revalidation: an existing item Model of the required type can be reused without
revalidating it. Changing a primary-key field through a Dataset item can therefore
leave its outer key inconsistent until the containing contract is validated again.
Collect returned Datasets through typed assignments as described in
[Dataset iteration and ownership](#dataset-iteration-and-ownership); item mutation
does not trigger automatic re-keying or parent and sibling validation.

Automatic revalidation of existing Models at job input and output boundaries is
not yet implemented. It is planned work intended to add checks at job handoffs
and further reduce the need to reason about validation scope. Currently, passing
a Model through a task or flow does not itself revalidate its content.

The `.content` and `.to_data()` assertions inspect stored values to demonstrate
coercion or its absence; they are not preparation for processing. String inputs
for integer fields are intentional demonstrations of runtime coercion.

## Reusable Models and Datasets

Specialize existing generic components first. For example, given compatible
Pydantic record schemas, the existing table Dataset can serve different domains:

```python
import omnipy as om

SampleTables = om.TableOfPydanticRecordsDataset[SampleRecord]
InstrumentTables = om.TableOfPydanticRecordsDataset[InstrumentRecord]
```

Both reuse the table machinery while their record schemas supply fields and
validators. See `src/omnipy/components/tables/datasets.py` and its corresponding
Models in `src/omnipy/components/tables/models.py`. Use the repository's compatible
Pydantic API for those schemas, as described under
[data structures](#choose-data-structures-by-their-role).

When introducing reusable functionality, identify the invariant, transformation,
or capability shared across uses. Parameterize its varying types and implement
the shared rule once. For example, these list-valued items share a nonempty
requirement while their element types vary:

```python
from typing import Generic

from typing_extensions import TypeVar

import omnipy as om


ItemT = TypeVar('ItemT')


class NonEmptyList(om.Model[list[ItemT]], Generic[ItemT]):
    @classmethod
    def _parse_data(cls, data: list[ItemT]) -> list[ItemT]:
        if not data:
            raise ValueError('At least one item is required')
        return data


class NonEmptyListsDataset(om.Dataset[NonEmptyList[ItemT]], Generic[ItemT]): ...


NumericSeries = NonEmptyListsDataset[float]
LabelLists = NonEmptyListsDataset[str]

readings = NumericSeries({'sensor-1': ['1.5', 2]})
labels = LabelLists({'report-1': ['draft', 'reviewed']})

assert readings['sensor-1'][0] == 1.5
assert labels['report-1'][1] == 'reviewed'
readings['sensor-1'].append('3.5')
assert readings['sensor-1'][2] == 3.5
```

`ItemT` passes through the Dataset to its item Model. Both specializations enforce
the nonempty rule, and the concrete element type controls parsing and validation.
The rule applies to each item's list payload; an empty Dataset is still permitted.
A named generic Dataset is useful when the family deserves a public name. Direct
composition such as `om.Dataset[NonEmptyList[float]]` also works. Choose according
to the reusable contract and readability; a new class is not required at every
composition point. Existing [batch](#choose-data-structures-by-their-role) and
[mutation](#validation-through-model-boundaries) rules still apply.

Omnipy supports default values for type variables. A generic Model used without
an explicit specialization uses the declared default type; a Dataset containing
that Model uses the same default:

```python
ValueT = TypeVar('ValueT', default=int)


class ValuesModel(om.Model[list[ValueT]], Generic[ValueT]): ...


assert ValuesModel(['7']).content == [7]
assert ValuesModel[str]([7]).content == ['7']

values = om.Dataset[ValuesModel]({'sample': ['7']})
assert values['sample'].content == [7]
```

Concrete defaults are applied automatically. Defaults that contain forward
references retain the existing `update_forward_refs()` resolution path once those
names are available. Explicit specialization overrides the default.

Preserve type relationships across reusable operations. For example, a factory
accepting `dataset_cls: type[DatasetT]` and constructing that class should return
`DatasetT`, so the chosen class determines the output type. The existing
`create_dataset_from_args` task in `src/omnipy/components/general/tasks.py`
demonstrates this. Bind a concrete Dataset class through `fixed_params` to reuse
that task in a flow; a type variable alone is not a runtime constructor.

State capabilities needed by generic code through appropriate bounds or protocols.
An unconstrained type parameter does not promise domain fields or methods. Preserve
concrete specializations at dataflow boundaries so the resulting declarations
remain inspectable contracts. Verify representative specializations and their
shared rule, including invalid inputs, and check static typing where it matters
to callers.

Distinguish varying types from varying configuration values. Some existing Models
and Datasets expose validated class-level `Params` and `.adjust(...)` for settings
such as delimiters. For example:

```python
SpaceSeparated = om.SplitToItemsModel.adjust(
    'SpaceSeparated',
    delimiter=' ',
)
words = SpaceSeparated('alpha beta')
assert words[0] == 'alpha'
assert words[1] == 'beta'
```

Adjustment creates a configured class while preserving the original class's
settings. Use it where the component supports it, alongside generic specialization,
instead of duplicating parsing code to change a setting. Follow the existing
`Params`/adjustment pattern when implementing that capability for a new component;
see `src/omnipy/data/param.py` and the raw Models and Datasets.

## Model transformations

`ConverterModel[Source, Target]` converts general types, including scalars,
collections, Omnipy Models, and Pydantic schemas. Neither side has to be a
Pydantic model. For example, a collection-to-scalar conversion can use the
wrapped list's ordinary interface:

```python
import omnipy as om


class ItemCountMapper(om.ConverterModel[om.Model[list[str]], int]):
    @classmethod
    def _convert(cls, data: om.Model[list[str]]) -> int:
        return len(data)


count = ItemCountMapper(['alpha', 'beta'])
assert count.content == 2
```

Parameterized source types such as `list[str]` and `tuple[int, int]` need a Model
wrapper in the declaration. `Model[list[str]]` supplies that source type without
requiring callers to construct the wrapper explicitly, as the example shows.
The current restriction is on parameterized **source** types; it is not a
requirement that the target be a Pydantic schema.

Implement `_convert()` as a classmethod returning the target type. Prefer
`Mapper(source)`, which produces a model-wrapped converted value that can mimic
the target's interface. Decorate the concrete mapper with `@om.mimics(Target)`
where static visibility is needed. A service that only accesses target fields can
work through that wrapper; a schema-shaped parameter alone is not a reason to
unwrap it. `Mapper.convert(source)` returns `.content`; use it when the consumer
specifically needs that underlying value.

Several typed inputs can be declared as
`Model[tuple[ItemModel, MetadataModel]]`. The caller can pass `(item, metadata)`
directly to the mapper constructor, and `_convert()` can unpack the input Model
directly.

Keep pure mapping separate from I/O. A mapper can translate vocabulary, select
fields, and combine item data with shared metadata. The service call belongs in
the task or service adapter, not in a model validator/converter that may run again
during validation.

Model and Dataset classes, including mapper classes derived from `ConverterModel`,
can be placed directly in linear/DAG child lists when construction expresses the
conversion. For example, use `ItemCountMapper` directly as a linear-flow child:

```python
@om.LinearFlowTemplate(ItemCountMapper)
def count_items(items: list[str]) -> ItemCountMapper: ...


assert count_items.run(['alpha', 'beta']).content == 2
```

The result remains a mapper Model wrapping the converted value. Linear flows
supply positional source values; DAG flows construct data-class children with
routed keyword arguments, so the mapper's source must accept that input shape.
Reuse general collection tasks and component flows where appropriate; do not add
a one-line task solely to call an already suitable Model or mapper constructor.

Structural conversion can also be expressed within nested types. For example,
`Dataset[RecordMapper]` maps the records in one batch, and
`Dataset[Dataset[RecordMapper]]` describes collections of such batches. A genuine
list-shaped value/payload can use `Model[list[ElementMapper]]`. These declarations
describe parsing/conversion; they do not introduce a task invocation per nested
element. Keep pure structural conversion separate from repeated service operations.

## External API contracts

An external service's request/response schemas and operation semantics define
the boundary the dataflow must satisfy. A narrative integration example declares
that contract in its service types and behavior, and tests the dataflow against
it. Preserve the API's field names, meanings, validation requirements, and
success/failure semantics; a local stand-in is not permission to reshape that API
around convenient internal data.

The BioSampleVault submission type (currently named
`BioSampleVaultSampleSubmissionSchema`) represents the external service's actual
submission contract. It is not merely an internal convenience record. For example,
the API uses `geolocation` and `sampling_date`, while the internal sample uses
`collection_site` and `sampled_at`. The schema mapper owns that translation and
combines the sample with the shared submission metadata.

`SampleAndMetadataToBioSampleVaultSubmissionMapper` targets this external schema
and is decorated with `@mimics(BioSampleVaultSampleSubmissionSchema)`. Constructing
the mapper produces a Model wrapping the converted request, which can be used in
place of the request model. The task posts it directly with `.post()`, parsing the
response with the service's response schema:

```python
samples_api_url = services.biosamplevault.urls['samples']
sample_submission = SampleAndMetadataToBioSampleVaultSubmissionMapper((sample, metadata))

response = await resolve(
    sample_submission.post(
        samples_api_url,
        response_cls=Model[BioSampleVaultSampleSubmissionSchema],
    )
)

sample.biosamplevault_sample_id = response.biosamplevault_sample_id
```

Posting the mapper sends the converted request; it does not require `.convert()`,
`.content`, or `.to_data()` to reach the service boundary. Keep the external schema
as the request contract; do not reshape it around the dataflow's mapper type,
sample/metadata tuple, or enclosing submission Model. Runtime mimicking lets the
wrapper provide the target interface, and `@mimics` exposes that interface to
supported static checkers.

In the tests, a mocked HTTP endpoint implements the service. The service URLs are
settings in the submission's `logistics` member, which keeps the broker's settings
and state apart from the content sent to the Sequence Depot. Each service has a
`HostUrlDataset` of its URLs by name, so the tasks post to complete URLs instead of
building them from a base URL. The Sequence Depot URLs also include the FTPS
`staging` area. `FileAndMetadataToFileTransferRequestMapper` derives the per-file
target URI below it, and the task records the URI returned by the transfer service as
`staging_storage_uri` only when the transfer has completed. The defaults are the URLs in
production, and the test replaces them with those of the mock services. The explode
task passes `services` on to the per-item tasks, like the shared `metadata`. Use the
returned response rather than depending on the service mutating and returning the same
request object. See [posting requests](remote-loading.md#post-requests-to-a-service).

Tests and mocks should exercise the external contract, including relevant request
fields and returned outcomes, while the internal dataflow remains free to use its
own data organization. Existing clients, remote tasks, and loaders may already
provide the required boundary; add an adapter when it has a concrete responsibility.

## Reusable jobs, templates, and modifiers

Look for a reusable operation or stage before writing a scenario-specific job.
Check existing component tasks and flows, then specialize or compose them. The
shared job modifiers apply to tasks **and flows**: a whole collection pipeline
can be reused with different inputs and model conversions. Keep a reusable job's
contract explicit so a reader can understand each specialization at its use site.

### Templates and executable jobs

A job template stores the callable definition, child composition where applicable,
and modifiers. Applying it creates an executable job and attaches the configured
engine's execution machinery. Creation and specialization do not execute the work.

| Operation | Result and purpose |
| --- | --- |
| `template.refine(...)` | A new template with specialized modifiers or child composition; the original template is unchanged. |
| `template.apply()` | An executable job, retained when the caller needs a job reference, for example to inspect run state. |
| `job.revise()` | A new template retaining that job's definition and modifiers, ready for further refinement and application. It does not undo execution. |
| `job(...)` | Executes the applied job according to its callable form and execution modifiers. |
| `template.run(...)` | Shorthand for `template.apply()(...)`, convenient at an entry point outside a flow. |
| `template(...)` inside a flow | Applies and calls the template in the flow context. Use this form in authored flow bodies. |

For example, specialize one operation without copying its body:

```python
import omnipy as om


@om.TaskTemplate()
def append_suffix(text: str, *, suffix: str) -> str:
    return f'{text}{suffix}'


exclaim = append_suffix.refine(name='exclaim', fixed_params={'suffix': '!'})
exclaim_task = exclaim.apply()
assert exclaim_task('hello') == 'hello!'
assert exclaim.run('hello') == 'hello!'

question = exclaim_task.revise().refine(name='question', fixed_params={'suffix': '?'})
assert question.run('hello') == 'hello?'


@om.FuncFlowTemplate()
def maybe_exclaim(text: str, *, enabled: bool) -> str:
    if enabled:
        return exclaim(text)
    return text


assert maybe_exclaim.run('hello', enabled=True) == 'hello!'
assert maybe_exclaim.run('hello', enabled=False) == 'hello'
```

Inside a flow, **call job templates instead of using their `.run()` method**.
Use `await child(...)` for coroutine children and the corresponding iteration
syntax for generators. Direct template calls require a flow context; outside one,
use `.run(...)` or an applied job. Calling `.run()` inside a flow raises
`JobStateException` with guidance to call the template directly. In linear/DAG
declarations, supply child templates directly and let the composition invoke them.

### Specialization with modifiers

Put behavior intrinsic to a reusable job on its base decorator. Put settings
specific to its surrounding dataflow in `.refine(...)` at the composition site.
For example, a job designed to process datasets can declare iteration on its base
template; a general one-item operation can instead gain iteration in a refinement.
Use meaningful function names, and give refined task and flow templates a
descriptive `name` in `.refine(name=..., ...)`. Assigning the refined template to a
new Python variable does not rename the job; without an explicit `name`, refinement
with the default `update=True` retains the original name.

| Modifier | Contract expressed |
| --- | --- |
| `name='collect_river_samples'` | Identifies the specialized job; also supplies the default DAG storage key for results not routed as dictionary entries. |
| `param_key_map={'dataset': 'records'}` | Maps internal parameter name to external input name. The surrounding flow supplies `records`; the iterated child receives `dataset`. |
| `fixed_params={'suffix': '!'}` | Binds configuration using internal parameter names. A fixed value is not an overridable default; use a normal parameter or function default when the caller should choose. |
| `result_key='records'` | Wraps the job's result in a dictionary under this key for downstream routing. It does not rename Dataset item keys. |
| `iterate_over_data_files=True` | Lifts a one-item operation to work across Dataset items; see [iteration and ownership](#dataset-iteration-and-ownership). |
| `output_dataset_cls=RecordDataset` | Selects the Dataset class collecting an iterated job's results; requires iteration to be enabled. |

The water-sample flow demonstrates specialization of a complete child flow:

```python
collect_and_normalize_samples.refine(
    name='collect_and_normalize_river_samples',
    param_key_map={'sample_page_urls': 'river_urls'},
    fixed_params={
        'mapper_dataset_cls': Dataset[Model[list[NormalizedRiverSampleRecordMapper]]],
        'concat_pages_key': 'all_river_samples',
    },
)
```

This child takes `river_urls` from the enclosing flow and binds the mapper and
collection key internally. The wastewater specialization uses the same pipeline
with a different mapper, input name, and collection key. See
`tests/integration/novel/full/water_sample_harmonization/flows.py` for both uses.
The reusable operation is fetching, normalizing, and collecting samples; the
domain-specific mapper and routing remain visible in the declaration.

Refinement creates a new template and defaults to `update=True`: omitted modifiers
are inherited, and mapping-valued modifiers such as `fixed_params` and
`param_key_map` are merged, with new values replacing matching keys. Consequently,
`.refine(fixed_params={})` does **not** clear existing bindings. With `update=False`,
old modifier settings are not inherited; unspecified modifiers take their defaults.
Respecify every modifier that the new template must retain. Positional arguments
to `.refine(...)` can replace a linear/DAG template's child list; the resulting
composition must still satisfy its declared callable contract.

### Execution policy

Routing modifiers describe how data is supplied and returned. Choose execution
modifiers for the actual execution requirement as well. In particular,
`auto_async=True` (the default) adapts **outermost coroutine job calls** to the
calling context:

| Context | Behavior with `auto_async=True` |
| --- | --- |
| Outside a flow, no running event loop | Runs the coroutine to completion with `asyncio.run` and returns its result. |
| Outside a flow, running event loop | Schedules the coroutine and returns an `asyncio.Task`; await it for the result. |
| Inside a flow | Leaves coroutine handling to the flow; an authored body awaits coroutine children explicitly. |

With `auto_async=False`, the outer caller also handles the coroutine explicitly.
This modifier does not make synchronous work asynchronous.

**Async-generator jobs remain lazy with either `auto_async` setting.** Calling
one returns an async generator, both inside and outside flows, whether or not an
event loop is already running. Consume it with `async for`; do not await the
generator itself. `auto_async` does not schedule its iteration or collect its
items. At a synchronous entry point, run an async consumer with `asyncio.run(...)`;
inside async code, consume the stream directly. If a coroutine job returns an
async generator, `auto_async` handles the coroutine call as described in the table,
but the returned stream still needs a consumer. See
[callable types and composed flows](#callable-types-and-composed-flows) for declaring
streaming linear/DAG flows. Keep the callable contract and execution context clear
instead of probing results with `isawaitable()`.

Use persistence and restoration modifiers when the dataflow needs those behaviors;
inspect their current semantics before promising caching or recovery. DAG-specific
input retention (`consume_kwargs_from_results`) is covered in
[Routing rules that matter](#routing-rules-that-matter).

## Routing rules that matter

Use the [shared modifiers](#specialization-with-modifiers) together with these
composition rules:

| Mechanism | Meaning |
| --- | --- |
| `LinearFlowTemplate(a, b, c)` | Passes each child's result to the next child as a positional argument. Tuple results remain one argument; the last child's result is returned. |
| Linear flow keyword-only inputs | Declare shared configuration after `*` in the flow signature, for example `flow(data, *, suffix)`. This makes `suffix` keyword-only: callers supply `suffix='!'`, and its value remains available to every child accepting that parameter name. |
| `DagFlowTemplate(...)` | Routes by parameter names from accumulated inputs/results. Children currently execute in declaration order. Concurrent execution of independent branches is future work. |
| A nonempty dictionary result | Its entries update the DAG's available named results. A plain dictionary is appropriate for this routing purpose; its values can remain typed objects. |
| Other DAG results | Stored under the child's job name unless explicitly wrapped with `result_key`. The overall return is the last child's result, not the whole result store. |
| `consume_kwargs_from_results=True` (default) | Removes routed arguments from the DAG result store when consumed. |
| `consume_kwargs_from_results=False` | Keeps routed arguments available for later children; results can still replace values under the same keys. Use when extraction and later collection both need the aggregate, or several children reuse a value. |

An intermediate result is passed as **one positional argument**,
including when it is a tuple: returning `(left, right)` supplies that tuple to the
next child, rather than unpacking it into two arguments. A child can accept the
tuple and unpack it in its body.

This rule keeps routing simple and preserves tuples as data. Automatically
unpacking tuple results would make a single tuple-valued parameter ambiguous:
the framework could not distinguish that value from several positional arguments.
Multiple values can already travel together in a tuple, with packing and unpacking
explicit in the child functions. Routing therefore needs no separate convention
for multiple positional results. For example, a child returning `(lower, upper)`
can feed a child accepting `bounds: tuple[int, int]`, whose body starts with
`lower, upper = bounds`.

Multiple positional arguments supplied to the flow itself are forwarded
individually to the **first** child; this is distinct from forwarding a child
result. Flow parameters that accept positional arguments are forwarded this way
even when the caller supplies them by keyword. Shared keyword-only inputs remain
available to children by matching name.
These semantics are implemented by `LinearFlowRunSpec` in
`src/omnipy/engine/run_spec.py` and covered by
`tests/compute/test_flow.py::test_linear_flow_only_first_positional`.

See [callable types and composed flows](#callable-types-and-composed-flows) for
how child callable forms determine a linear/DAG flow's outer callable contract.

## Callable types and composed flows

Choose a callable form from the operation's actual contract. These are distinct
public interfaces, not interchangeable implementation details.

| Callable form | Caller consumes it with | Appropriate operation |
| --- | --- | --- |
| Sync function | Direct call | One immediate result, such as local conversion or collection |
| Coroutine | `await` | One eventual result after asynchronous work, such as a service call |
| Sync generator | `for` | A synchronous stream of values |
| Async generator | `async for` | A stream of values arriving through asynchronous work |

These describe the underlying callable contracts. For an outermost coroutine job,
the default `auto_async` modifier can run or schedule it on the caller's behalf;
see [execution policy](#execution-policy) for the context-dependent return behavior.

`TaskTemplate` and `FuncFlowTemplate` execute their authored bodies. Use a task
for one self-contained operation. Use a function flow when the algorithm itself
requires Python control flow, such as data-dependent branching, dynamic iteration,
or explicit coordination. Keep each one's natural synchronous, coroutine,
generator, or async-generator form. Do not mark local work `async` merely because
another stage awaits I/O, and do not create a generator merely to demonstrate
streaming.

`LinearFlowTemplate` and `DagFlowTemplate` are different: their outer callable
declares the public signature while their child list defines the execution:

- The terminal (last) child determines the flow's returned data and return type:
  a regular value, such as a Model or Dataset, or a stream of values. Declare the
  flow's return annotation to match that output.
- Any async child makes the composed flow asynchronous, even if the last child
  is synchronous. The flow is then a coroutine for a regular result, or an async
  generator for a stream. An entirely synchronous composition uses a regular
  function or generator, respectively.
- A mismatch between the declared callable form and the composition raises
  `TypeError` when the template is created.

Streaming flow calls return real Python generator or async-generator objects.
If the last child simply returns an existing generator, its return annotation
must identify the stream, for example `Iterator[int]` or `AsyncIterator[int]`, so
Omnipy can determine the flow's callable form.

Thus an async fetch followed by synchronous normalization and collection is still
an `async def` flow returning one result:

```python
import omnipy as om


@om.LinearFlowTemplate(fetch_async, normalize, collect)
async def load_records(source: str) -> list[str]: ...
```

For ordinary function and coroutine linear/DAG flows, `...` makes clear that the
child list does the work. A flow whose validated public contract is a generator
needs a generator-shaped declaration. Use `Void` only for these signature-only
bodies; it is an empty iterable and does not perform the flow's work:

```python
from collections.abc import AsyncIterator, Iterator

import omnipy as om


@om.LinearFlowTemplate(emit_records)
def record_stream(source: str) -> Iterator[str]:
    yield from om.Void()


@om.DagFlowTemplate(stream_events)
async def event_stream(url: str) -> AsyncIterator[str]:
    async for event in om.Void():
        yield event
```

Do not add `isawaitable()` branches to conceal an unclear contract. A narrative
integration example should use only callable forms that belong naturally to its
dataflow. Exhaustive callable-type × job-type coverage belongs in the framework's
compute test harness.

## Dataset iteration and ownership

In the current API, with `iterate_over_data_files=True`, annotate the function's
first argument and return type as **one item**. The exposed job signature replaces that first
argument with `dataset` and lifts the return type to a dataset. The inner argument
can have a singular name such as `record`; use `dataset` in `param_key_map` for the
outer call. Set `output_dataset_cls` when a named result dataset class is useful.
Dataset iteration preserves keys; ordinary field normalization does not currently
rename them. Construct keys consistent with the parsed primary keys as described
under [identity and relationships](#identity-and-relationship-contracts).

The hardcoded `dataset` name and first-parameter restriction are current mechanics,
not the intended naming principle. Prefer a singular name for the inner item and a
plural name for the exposed collection. A future API should let the author name
the outer dataset parameter and select the inner parameter by name, regardless of
position. Whether this uses one pair-valued modifier or two modifiers remains
undecided; neither form is implemented. Until then, use the supported mapping when
needed and do not invent a new modifier in generated code.

Async item calls run concurrently. Do not depend on their completion order or
mutate shared aggregate state from each item. Concurrency limits, rate limits, or
ordered processing are additional requirements to design explicitly when needed;
iteration alone does not supply those policies.

Async iteration records exceptions as `FailedData` in the output dataset. A
successful await is therefore not enough to establish complete success. Check the
APIs in [failure inspection](#inspect-current-failure-and-pending-results) and choose
a policy before finalization. A
service-declared failure stored in a record's status/error fields is distinct from
an exception recorded as `FailedData`; account for whichever forms the dataflow
uses. Do not add a retry policy just because an example is asynchronous.

Choose result ownership and status representation for the use case. Updating a
record's typed status fields is one option; using Dataset `PendingData` and
`FailedData` markers to track unfinished or failed work is another. Some contracts
need both execution markers and domain-specific outcomes. See
[status from facts and acknowledgements](#status-from-facts-and-acknowledgements)
for these choices.

When a task enriches a record it owns, use Model operations for typed updates.
When the design calls for collecting returned datasets into an aggregate, use
typed assignments and derive summaries from the authoritative results. Keep nested
updates within the boundaries described in
[Validation through Model boundaries](#validation-through-model-boundaries).
If snapshot isolation is needed, make it explicit instead of serializing/rebuilding
everything by default.

## Inspect current failure and pending results

Current Dataset APIs expose available results and task markers. Full failure and
recovery handling is largely future work, including planned support for atomic
rollback of jobs. These methods let a flow inspect the present result; they do
not implement retry, rollback, resumption, cancellation, or exactly-once external
effects.

| API | Current meaning |
| --- | --- |
| `dataset.available_data` | Same-type filtered Dataset of available entries, retaining keys |
| `dataset.failed_data` | Same-type filtered Dataset containing failure markers |
| `dataset.pending_data` | Same-type filtered Dataset containing pending markers |
| `dataset.failed_task_details()` | Mapping from keys to failure markers, including `.exception`, `.job_name`, and `.job_unique_name` |
| `dataset.pending_task_details()` | Mapping from keys to pending markers with producing-job details |

These are filtered copies, not live subscriptions or deep snapshots of the item
Models. Accessing a failed or pending item normally raises `FailedDataError` or
`PendingDataError`, including through a filtered marker Dataset. Use `.keys()` to
inspect their identities and the detail methods to inspect their markers.

For example, after awaiting an iterated operation:

```python
# `results` is the Dataset returned by the operation.
successful = results.available_data
failures = results.failed_task_details()
pending = results.pending_task_details()

# If a key failed, failures[key].exception contains its underlying exception.
# Keep `results` or the keyed details alongside `successful` when reporting a
# partial outcome; filtering must not silently redefine the expected batch.
```

For an all-items-required policy, use the general component's `require_all_items`
task, also exported as `om.require_all_items`:

```python
import omnipy as om

# At an entry point, check the Dataset returned by an operation.
complete_results = om.require_all_items.run(results)
```

This task returns the original Dataset unchanged when all its entries are
available, including for an empty Dataset. Otherwise it raises `ValueError` with
the failed and pending keys. It checks the Dataset's own entries without copying
it or traversing nested Datasets. It does not check for absent expected keys or
service-specific success conditions.

Item-completion policies could also become job modifiers in the future, for
example to require all items before accepting a job's result. This is a possible
extension, not an implemented modifier; use the explicit task with current APIs.

Place `om.require_all_items` directly in a linear/DAG child list, or call
`om.require_all_items(results)` inside an authored flow. Put it before stages
that require a complete Dataset, including collection into an aggregate Model.
Current Model attribute assignment may
convert a Dataset via `to_data()` internally; a Dataset with `FailedData` can
raise there before a later finalization guard runs. For an all-items-required
dataflow, the order is **iterated operation → require all items → collect →
finalize**. Inspect or retain the original Dataset before that assignment if
the caller needs keyed failure details and successful results. The task's error
reports keys; a dataflow that needs the result after raising can use
a dedicated exception carrying that Dataset or an explicit partial-result contract.

A partial-results
use case may instead pass `available_data` onward while reporting the excluded
keys. Neither choice proves domain success: a service may return a rejected
response as ordinary data without raising. Check the required response fields or
acknowledgements too. Preserve original inputs separately if a deliberately
designed recovery operation needs them; failure markers are not retry inputs.

Inspect `src/omnipy/data/_mixins/task.py` and
`tests/data/test_dataset.py` (`test_dataset_pending_and_failed_data*`) for current
behavior. The remote loader has its own configured HTTP retries; those do not
constitute a general dataflow recovery mechanism.

## Example: publish a catalog

This example composes typed catalog records, a request mapper, an iterated async
publishing task, and an extract/publish/collect flow. It is executable as one
module; the comments indicate where to split it in a real package. Its service is
a deterministic async stand-in. A Model validator requires every record to have
a publication identifier before a receipt can be assigned.
`CatalogDataset` represents the record batch; `PublicationModel` is the surrounding
composite record that combines that dataset with metadata and a receipt.
Each catalog record's primary key is `record_id`, and its Dataset key is that
same string. The service-assigned `publication_id` is a separate identifier.
The example currently expects matching keys without validating that invariant.
When adapting it, prefer a validator on `CatalogDataset` as described under
[Dataset-level validation](#dataset-level-validation). A shared
validator has been proposed; do not assume it is already an available API.

```python
import asyncio

import omnipy as om
import omnipy.util.pydantic as pyd


# models.py
class CatalogSchema(pyd.BaseModel):
    record_id: str
    title: str
    publication_id: str | None = None


@om.mimics(CatalogSchema)
class CatalogModel(om.Model[CatalogSchema]): ...


class CatalogDataset(om.Dataset[CatalogModel]): ...


class PublicationMetadataSchema(pyd.BaseModel):
    catalog_name: str


@om.mimics(PublicationMetadataSchema)
class MetadataModel(om.Model[PublicationMetadataSchema]): ...


class PublicationSchema(pyd.BaseModel):
    records: CatalogDataset
    metadata: MetadataModel
    receipt: str | None = None

    @pyd.root_validator(skip_on_failure=True)
    def _receipt_requires_publication_ids(cls, values: dict) -> dict:
        if values['receipt'] is not None:
            if not all(record.publication_id for record in values['records'].values()):
                raise ValueError('Every catalog record needs a publication identifier')
        return values


@om.mimics(PublicationSchema)
class PublicationModel(om.Model[PublicationSchema]): ...


class PublishRequest(pyd.BaseModel):
    catalog: str
    label: str


@om.mimics(PublishRequest)
class PublicationMapper(
    om.ConverterModel[om.Model[tuple[CatalogModel, MetadataModel]], PublishRequest]
):
    @classmethod
    def _convert(cls, data: om.Model[tuple[CatalogModel, MetadataModel]]) -> PublishRequest:
        record, metadata = data
        return PublishRequest(catalog=metadata.catalog_name, label=record.title)


# services.py
async def publish_record(request: PublishRequest) -> str:
    await asyncio.sleep(0)
    return f'{request.catalog}:{request.label}'


# tasks.py
@om.TaskTemplate()
def extract_publication(publication: PublicationModel) -> dict[str, object]:
    return {'records': publication.records, 'metadata': publication.metadata}


@om.TaskTemplate(iterate_over_data_files=True, output_dataset_cls=CatalogDataset)
async def publish_records(record: CatalogModel, *, metadata: MetadataModel) -> CatalogModel:
    request = PublicationMapper((record, metadata))
    record.publication_id = await publish_record(request)
    return record


@om.TaskTemplate()
def collect_publication(records: CatalogDataset, publication: PublicationModel) -> PublicationModel:
    publication.records = records
    return publication


@om.TaskTemplate()
def create_receipt(publication: PublicationModel) -> PublicationModel:
    publication.receipt = (
        f'{publication.metadata.catalog_name}: {len(publication.records)} records published'
    )
    return publication


# flows.py
@om.DagFlowTemplate(
    extract_publication,
    publish_records.refine(
        param_key_map={'dataset': 'records'},
        result_key='records',
    ),
    collect_publication,
    consume_kwargs_from_results=False,
)
async def publish_catalog_records(publication: PublicationModel) -> PublicationModel: ...


@om.LinearFlowTemplate(publish_catalog_records, create_receipt)
async def publish_catalog(publication: PublicationModel) -> PublicationModel: ...
```

The receipt requirement belongs to `PublicationSchema`, so `create_receipt` only
constructs and assigns the receipt. Inputs without publication IDs remain valid
while `receipt` is `None`; assigning a receipt triggers the relationship validator.
The example also raises on failed/pending items during collection. When callers
need explicit failure reporting, insert `require_all_items` before the collector,
as described in [failure inspection](#inspect-current-failure-and-pending-results).

The `publication` input must survive `extract_publication` for `collect_publication`
to use it. The publisher reads the extracted `records` and stores its Dataset result
under the same key with `result_key`, replacing the extracted Dataset, so the
collector takes `records` without a mapping of its own. The alternative is to leave
the result under the publisher's job name and map the collector's parameter to it
with `param_key_map`; the brokering flows use `result_key`. The synchronous last task
in `publish_catalog` does not make the parent synchronous. An empty catalog produces
a zero-item receipt here; decide whether that is appropriate in the actual domain.

For a service reached over HTTP, `publish_records` would instead name the URL and
the request, post the mapper with `.post(url, response_cls=...)`, and store the
identifier from the parsed response, as in the
[external-contract example](#external-api-contracts).

The repository-test shape is `completed = await publish_catalog.apply()(publication)`
under the existing runtime fixture, followed by a comparison with the expected
published data, for example through `completed.to_data()`. Use Dataset keys equal
to the records' `record_id` values. The receipt validator already enforces the
identifier requirement; the scenario test need not repeat it as per-record asserts.

## Status from facts and acknowledgements

Choose status representation according to the use case. Dataset `PendingData`
and `FailedData` markers can provide the required execution status without
updating status fields on each record. Use their inspection APIs to report
unfinished work, failures, and available results. Explicit typed status fields
are another option when the domain or consumer needs them; markers and domain
status can also coexist. Neither approach is a universal default.

Tasks and the framework record what an operation established. When a summary can
be derived from domain facts, express that derivation in the relevant Model.
Distinguish a recorded outcome from a computed summary even when both use the
same status vocabulary. A returned service rejection is ordinary data unless
the task raises; it needs the domain-specific checks described in
[failure inspection](#inspect-current-failure-and-pending-results).

For explicit status data, choose its location according to the use case. A small
record may keep `transfer_status` and `error` inline; one with several related statuses may
group them under a typed `status` member. A separate structure can fit when status
has distinct ownership, reuse, or reporting requirements. These are design options,
not a rule that item status must be inline or aggregate status must be separate.
Choose the simplest layout that serves the data's consumers and contracts. Wherever
the resulting status is stored, its derivation needs access to the authoritative
inputs; storage placement and validator placement are related but distinct choices.

The submission example groups its aggregate `status` with the service settings in a
`logistics` member: the broker's handling of the submission, not part of the content
sent to the Sequence Depot. Its validators stay on the submission schema, which
contains the samples, files and metadata they derive the status from.

The per-file transfer outcome is broker state as well. `SubmissionFileSchema` extends
the payload's `SeqDepotSubmissionFileSchema` with `transfer_status` and `error`, in the
same way as `SubmissionSchema` extends `SeqDepotSubmissionPayloadSchema` with
`logistics`, overriding its `files` field. Constructing the payload Model from the
submission's files validates them against the payload schema, leaving the broker's
fields out of the request.

The submission example uses explicit domain fields. Its registration task stores
the returned identifier:

```python
sample.biosamplevault_sample_id = response.biosamplevault_sample_id
```

The enclosing model derives registration readiness from the sample identifiers.
The task does not also set an aggregate registration flag. Similarly, the
allocation task records `metadata.seq_depot_submission_id`; the enclosing
model derives `seq_depot_submission_id_status` from its presence.

A transfer outcome cannot be inferred merely from a prepared destination URL.
The transfer task records the service's result on its own file:

```python
file.transfer_status = response.status
file.error = response.error
```

The aggregate's transfer status is then derived from its files' outcomes. Put
that validator on the model containing the files, not on a status-only record
with no access to them. Iterated tasks update and return individual items; the
collector assigns the returned Dataset to the aggregate. This separates per-item
outcomes from the aggregate summary without a shared status counter in async tasks.

Use normal Model operations for these updates. Changing wrapped data through the
interface of the Model holding the status validators reruns them, maintaining
computed status. Changing a nested member in place does not; make the change inside
`with model.updating():` or assign the member back through that Model, as described
under [Validation through Model boundaries](#validation-through-model-boundaries).
No serialization/reconstruction or separate "refresh status" task is needed. Keep mutable nested containers within the
[Model boundaries](#validation-through-model-boundaries) already described.
Derivation should be repeatable and depend on the current facts, including when
an identifier is absent or an outcome changes. Validators must not perform service
calls or fabricate successful operation results.

Define aggregate status policy explicitly when it matters. For example, the
submission's transfer summary gives failure precedence over pending work and uses
`N/A` for no files. Those are domain choices, not universal semantics for every
dataflow. Account for the Dataset's failed/pending items as well as any recorded
service failures before declaring readiness.

Readiness and confirmed completion are separate. Having the required identifiers
and completed transfers makes a submission ready for its final service call.
`seq_depot_submission_status` becomes `completed` only after that service
confirms acceptance. Preserve such non-inferable outcomes as explicit state, or
derive their display status from a recorded acknowledgement when one is stored.
A finished job alone does not prove domain success.

Keep status derivation and service contracts separate. If derived fields must be
omitted or frozen at a service boundary, select an appropriate outbound schema;
do not require a second model hierarchy in every dataflow.

Model validators already enforce the declared status relationships during normal
operations. Scenario tests need not restate straightforward rules as assertions;
use focused tests for complex derivation, such as precedence among mixed outcomes.

## Validation and narrative tests

Model validation reduces the assertions needed in dataflow tests. Straightforward
constraints, such as required fields, valid values, or a receipt requiring
publication IDs, already act as executable assertions when the Model validates.
Do not repeat them as per-field checks in every scenario. Test complex validators
and their meaningful edge cases directly, especially cross-record relationships,
cardinality rules, or mixed-status aggregation. See the
[relationship examples](#identity-and-relationship-contracts) for validations
whose logic warrants focused tests.

Keep a narrative test centered on its scenario's observable result. Comparing
`to_data()`-serialized output with an expected payload is often appropriate:

```python
assert result.to_data() == expected_payload
```

Direct Model comparisons are also useful when their equality semantics match the
contract. Choose the representation that expresses what the test needs to check.
Outside the JSON component's own tests, a hierarchical Model's plain-data output
usually suffices; there is little reason to assert the exact nested JSON Model
classes. Assert wrapper types or structure when those are the behavior under test.
Add separate checks for computed properties, external calls, or execution state
only when they matter to the scenario and are not already covered.

Keep expected data independent of the mapper or conversion being tested. Put
inputs and expectations in `conftest.py` fixtures or `pytest_cases` case modules.
A complete expected payload or request-list comparison can replace many individual
assertions. If request order is unspecified, compare in a stable order by identity
while preserving duplicates; check order only when it is part of the contract.

Call the actual flow and use the existing runtime/engine fixtures. Mock external
services while exercising real Omnipy functionality. Check transmitted requests
when they are part of the scenario's contract; a spy is not required for every
service call. For HTTP ingestion, use a local fixture endpoint and the actual
loader; see [HTTP test boundaries](remote-loading.md#test-against-a-local-service).
Keep fixture-specific assertions outside tasks and flows. Choose focused failure
cases for the behavior being introduced instead of expanding every narrative
example into a comprehensive validation suite.

### Mock services and failure scenarios

A coroutine stand-in in `services.py`, typed with the service's request and
response schemas, is enough when the lesson is the dataflow itself; the catalog
example below uses one. Mock the service as an HTTP endpoint when the dataflow's
HTTP behavior is part of the lesson: concurrent requests from iterated tasks,
posting with `.post()`, response parsing, or failures reported by the service.
Omnipy's remote functionality then runs for real, as for loading; see
[HTTP test boundaries](remote-loading.md#test-against-a-local-service).

The brokering [conftest](../../../../tests/integration/novel/full/sequence_data_brokering/conftest.py)
shows the shape, built on the `aiohttp_server` fixture:

- One app factory per service, e.g. `_create_biosamplevault_app(sample_ids,
  response_delay_secs)`, whose parameters are the behavior the tests control.
  The handlers implement the declared contract and nothing more; a small response
  delay simulates latency while keeping the run short.
- A shared middleware records the request bodies per endpoint path, so a test can
  compare the requests a service received with the expected ones.
- A `MockService` dataclass per running server, with `endpoint_url(path)` for the
  settings passed to the dataflow and `requests` for the recorded bodies.
- A `services` fixture building the dataflow's service settings from the mock
  services. The expected output fixture reuses it, since the settings are part of
  the output.
- Behavior a scenario varies is a fixture of its own with a default, e.g.
  `failing_source_uris` returning an empty collection. A test overrides it with
  `pytest.mark.parametrize('failing_source_uris', [...])`, and the service fixture
  takes it as a parameter. No global or context state is needed.

When exact fixture IDs matter, let the mock service assign them from a mapping
keyed by request identity, such as the normalized local sample id. Sequential ID
allocation can assign different IDs to requests when waits before allocation or
HTTP arrival order change, even though each response still belongs to the correct
input. If IDs are intentionally allocated dynamically, capture request/response
associations and check the required relationships without assuming allocation
order. Compare concurrently sent requests in a stable order by identity.

Test a failure scenario on the child flow that handles it, when the scenario
concerns one stage. The brokering test of a failed file transfer runs
`coordinate_external_file_transfer.apply()` on its own and checks the per-file
outcome and the derived aggregate status, rather than running the complete
brokering flow up to the stage that would reject the submission.

## Source map

- Complete composition: `tests/integration/novel/full/sequence_data_brokering/`;
  mocked HTTP services and per-test configuration in its `conftest.py`.
- Another domain, with model classes as children and refined source pipelines:
  `tests/integration/novel/full/water_sample_harmonization/flows.py`.
- Conversion: `src/omnipy/components/general/models.py`, `ConverterModel`.
- Generic data contracts: `src/omnipy/components/tables/models.py` and `datasets.py`;
  generic Dataset coverage in `tests/data/test_dataset.py`, including
  `test_generic_dataset_two_typevars`.
- Generic factories: `src/omnipy/components/general/tasks.py`;
  configurable data classes: `src/omnipy/data/param.py`,
  `src/omnipy/components/raw/models.py`, and `datasets.py`.
- Field typing: `src/omnipy/data/_typing/helpers.py`, `mimics`.
- Mutation validation and recursive Pydantic wrapping: `src/omnipy/data/model.py`,
  `_special_method`, `__setattr__`, `create_pydantic_model_subclass_with_wrappers`,
  and `_wrap_nested_pydantic_models`; nested-container and nested-Pydantic tests in
  `tests/data/test_model.py`.
- Routing: `src/omnipy/engine/run_spec.py`, `LinearFlowRunSpec`, `DagFlowRunSpec`.
- Template/job lifecycle and refinement: `src/omnipy/compute/_job.py`.
- Shared job modifiers: `src/omnipy/compute/_mixins/params.py`, `name.py`,
  `result_key.py`, and `auto_async.py`; behavior coverage in
  `tests/compute/mixins/` and `tests/compute/test_flow.py`.
- Callable forms and flow validation: `src/omnipy/util/callable_types.py`,
  `src/omnipy/compute/_joblist_job.py`; signature-only generator helper:
  `src/omnipy/compute/helpers.py`, `Void`.
- Iteration and per-item failure: `src/omnipy/compute/_mixins/iterate.py`;
  dataset failure accessors in `src/omnipy/data/dataset.py`.
- HTTP posting: `src/omnipy/data/_mixins/post.py`, `PostMixin.post`;
  `src/omnipy/components/remote/tasks.py`, `post_json_to_api_endpoint`,
  `open_host_retry_client`, `post_to_url`; coverage in
  `tests/integration/novel/io/test_posting.py`.
- Pydantic compatibility: `src/omnipy/util/pydantic.py`.
