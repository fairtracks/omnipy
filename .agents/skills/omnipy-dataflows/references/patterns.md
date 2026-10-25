# Dataflow patterns and API details

Paths below are relative to the repository root. Check the current implementation
when extending these patterns; the examples describe the APIs available when this
guidance was written.

## Readable contracts and documentation reuse

The dataflow is both executable code and an inspectable contract for agent output.
A human should be able to read the models and flow declarations to understand
what the agent has implemented: accepted inputs, validated relationships,
transformations, external operations, batch boundaries, and expected outputs.
Make those choices visible in the types, validators, named stages, and routing.
Tests verify that the implementation fulfills that contract.

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
setup and expected results can remain test-specific; an example should be able to
construct its input and invoke the same implementation without depending on pytest.
Reuse or extract the tested definitions where practical, rather than maintain a
second implementation for the tutorial. Follow root `AGENTS.md` for documentation
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
| An Omnipy batch of processing items | `Dataset[ItemModel]` | Item identity and dataset operations; an item can itself contain structured data |
| A collection of actual Omnipy batches | `Dataset[Dataset[ItemModel]]`, optionally using named subclasses | Use when both batch and item levels need Dataset semantics |
| Fixed aggregate of different members | Pydantic schema containing typed datasets/models, wrapped in `Model` | Each member has a specific type |
| A sequence intrinsic to one value or an external payload | `Model[list[...]]` or a suitable existing model | Preserve value/payload structure; workflow batches use datasets |
| Tabular wrangling | Existing table/Pandas models and datasets | Use the component's operations |
| Schema translation | `ConverterModel[Source, Target]` | Reusable typed conversion |

A heterogeneous dataset is useful when its varying members are genuinely data
items. It is a poor default for a fixed record whose string keys are being used as
field names and whose union type forces casts at every access.

Choose an item's boundary from the workflow operations, not from every collection
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

For workflows that actually need batches within a collection, for example,
`class SampleBatch(Dataset[SampleModel]): ...` and
`class SampleBatches(Dataset[SampleBatch]): ...` express those two levels. Then
`batches['batch-1']['sample-A']` accesses a sample Model through their keyed
boundaries. Use this structure when it serves the workflow; do not introduce it
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

The user's intended direction is to extend this batch abstraction to parallel
execution and streaming through async generators. Keep Dataset central when
designing batch contracts so those execution models can build on the same
structure. This is future direction, not a claim that the current iteration
decorator supplies those modes or that their APIs have been decided.

Use existing domain primitives before inventing regex checks in tasks, for example
`DateModel` and `HostUrlModel` subclasses. A validator can fill a missing value from
another field, such as a filename from a source URL. Do not duplicate those rules
in a normalization task. Honor field order, missing earlier fields, and default
validation behavior in the repository's Pydantic API.

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

## Identity and relationship contracts

The intended pattern is that Dataset keys serialize the primary keys of their
contents. Container lookup and a record's primary-key field serve different uses,
but they represent the same identity. An external service's assigned identifier
can remain a separate attribute; receiving it does not change the chosen primary
key of the internal record.

In the submission example, `local_sample_alias` is the sample's primary key. Use
the lowercase Dataset key `sample-a` while retaining raw input
`local_sample_alias='Sample-A'` to demonstrate Model normalization. After parsing:

```python
assert submission.samples['sample-a'].local_sample_alias == 'sample-a'
```

The [input and expected-output fixtures](../../../../tests/integration/novel/full/sequence_data_brokering/conftest.py)
use matching normalized keys. The
[integration test](../../../../tests/integration/novel/full/sequence_data_brokering/test_sequence_submission_brokering.py)
checks alias normalization immediately after Model construction and compares the
full enriched output. The former `Sample-A` Dataset key was an inconsistency to
correct, not a pattern to preserve. Do not lowercase the raw alias values as well:
doing so would remove this normalization example.

The [table primary-key specification](../../../../docs/superpowers/specs/2026-10-16-table-model-architecture-and-conversions.md#primary-keys)
extends this concept to tables. It defines deterministic serialization, retained
visible key fields, and rejection of serialized-key collisions. Single string
keys serialize to themselves; composite keys use the specified escaping and
delimiter rules. Its
[Dataset interoperability section](../../../../docs/superpowers/specs/2026-10-16-table-model-architecture-and-conversions.md#dataset-interoperability)
describes how keyed rows become Dataset items. These table APIs and automatic
re-keying are planned functionality, not capabilities to assume in generated code.
Use the identity invariant now while constructing keys explicitly with current
APIs. Changing or normalizing a primary key must preserve agreement with the
Dataset key and must not silently collapse records with colliding keys.

Place relationship validation where its inputs are available. Concrete examples
in the [submission models](../../../../tests/integration/novel/full/sequence_data_brokering/models.py)
include:

- `SubmissionSampleSchema.local_sample_alias` uses `StrippedLowerStr` to normalize
  the local primary key. `SubmissionFileSchema` constrains file roles, checksum
  format, and URL types; `_extract_file_name_from_source_storage_uri` derives the
  filename within that record.
- `SubmissionRecord._file_sample_aliases_exist` has access to both sample and file
  Datasets and checks that each file's normalized reference identifies a sample.
- `SubmissionRecord._samples_have_one_read1_and_one_read2` checks the paired-file
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
or role names.

## Validation through Model boundaries

Omnipy Models validate when their content changes through the Model interface.
This includes supported mutating methods, item assignment, and attribute
assignment. Treat validation as part of normal typed operations, not an optional
cleanup step after a task. For example, appending through a list Model validates
and coerces the new element:

```python
import omnipy as om
import omnipy.util.pydantic as pyd

numbers = om.Model[list[int]]([2, 4, 5])
numbers.append('7')
assert numbers.content == [2, 4, 5, 7]
```

The exception is two or more container levels with no Model between them.
With the default dynamic element conversion disabled, indexing a
`Model[list[list[int]]]` returns a bare inner list. Calling that list's `append`
does not pass through the outer Model, so the string remains unvalidated:

```python
nested = om.Model[list[list[int]]]([[2, 4, 5]])
nested[0].append('7')
assert nested.content == [[2, 4, 5, '7']]
```

Put a Model between the container levels to make inner mutations validate:

```python
nested = om.Model[list[om.Model[list[int]]]]([[2, 4, 5]])
nested[0].append('7')
assert nested[0].content == [2, 4, 5, 7]
```

Apply this rule to nested mutable containers generally, including dictionaries.
Model boundaries belong where mutations need validation; lists of scalar values
need only the Model around the list. Explicit nested Models also make the intended
boundaries independent of optional dynamic element conversion. These list examples
describe value structure, not a change to the Dataset rule for workflow batches.

For Models wrapping Pydantic records, Omnipy supplies nested wrappers, so normal
field access and changes validate throughout the record. Appending a record and
assigning one of its fields both validate in this example:

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
lists at runtime and does not have the bare-inner-list limitation above:

```python
class GroupedB(pyd.BaseModel):
    aa: list[list[A]]


grouped = om.Model[GroupedB]({'aa': [[{'a': 3, 'b': 'abc'}]]})
inner = grouped.aa[0]
assert isinstance(inner, om.Model)
inner.append({'a': '4', 'b': 123})
assert inner[1].a == 4
```

The rule concerns actual Model boundaries, not the number of brackets in the
source annotation. Use the current wrapping behavior rather than preserving an
older limitation in generated schemas. Directly mutating an unwrapped object
obtained through `.content` can bypass validation; keep updates on the Model
interface. The `.content` assertions above inspect stored values to demonstrate
coercion or its absence, rather than extracting data for processing. String inputs
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


class NonEmptyListsDataset(om.Dataset[NonEmptyList[ItemT]], Generic[ItemT]):
    ...


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

Preserve type relationships across reusable operations. For example, a factory
accepting `dataset_cls: type[DatasetT]` and constructing that class should return
`DatasetT`, so the chosen class determines the output type. The existing
`create_dataset_from_args` task in `src/omnipy/components/general/tasks.py`
demonstrates this. Bind a concrete Dataset class through `fixed_params` to reuse
that task in a flow; a type variable alone is not a runtime constructor.

State capabilities needed by generic code through appropriate bounds or protocols.
An unconstrained type parameter does not promise domain fields or methods. Preserve
concrete specializations at workflow boundaries so the resulting declarations
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
directly. A bare parameterized `tuple[...]` is not a supported `ConverterModel`
source type; declaring the Model type does not require explicit wrapping at every
call site.

Keep pure mapping separate from I/O. A mapper can translate vocabulary, select
fields, and combine item data with shared metadata. The service call belongs in
the task or service adapter, not in a model validator/converter that may run again
during validation.

Existing models and dataset classes can be placed directly in linear/DAG child
lists when construction expresses the conversion. Reuse general collection tasks
and component flows where appropriate; do not add a one-line task solely to call
an already suitable model constructor.

Structural conversion can also be expressed within nested types. For example,
`Dataset[RecordMapper]` maps the records in one batch, and
`Dataset[Dataset[RecordMapper]]` describes collections of such batches. A genuine
list-shaped value/payload can use `Model[list[ElementMapper]]`. These declarations
describe parsing/conversion; they do not introduce a task invocation per nested
element. Keep pure structural conversion separate from repeated service operations.

## External API contracts

An external service's request/response schemas and operation semantics define
the boundary the workflow must satisfy. They have significance independently of
how the service is implemented in a tutorial or test. Preserve the API's field
names, meanings, validation requirements, and success/failure semantics; a local
stand-in is not permission to reshape that API around convenient internal data.

The BioSampleVault submission type (currently named
`BioSampleVaultSampleSubmissionSchema`) represents the external service's actual
submission contract. It is not merely an internal convenience record. For example,
the API uses `geolocation` and `sampling_date`, while the internal sample uses
`collection_site` and `sampled_at`. The schema mapper owns that translation and
combines the sample with the shared submission metadata.

`SampleAndMetadataToBioSampleVaultSubmissionMapper` targets this external schema
and is decorated with `@mimics(BioSampleVaultSampleSubmissionSchema)`. Constructing
the mapper produces a Model wrapping the converted request, which can be used in
place of the request model:

```python
request = SampleAndMetadataToBioSampleVaultSubmissionMapper((sample, metadata))
response = await register_sample_with_biosamplevault(request)
sample.biosample_vault_sample_id = response.biosample_vault_sample_id
```

The service function's parameter is annotated with the external schema. Keep that
contract; do not change it to require the workflow's mapper type, sample/metadata
tuple, or enclosing submission Model. Runtime mimicking lets the wrapper provide
the target interface, and `@mimics` exposes that interface to supported static
checkers. Passing the mapper directly does not require `.convert()`, `.content`,
or `.to_data()` solely to reach this coroutine boundary.

The current coroutine in `services.py` implements the simulated API operation.
The user expects it will likely become mocked API endpoints; that is future work,
not an endpoint implementation already present. Moving to HTTP should preserve
the external schema and the mapper's role. A client/transport adapter can encode
the request and parse the response as required by that transport. Direct use of
a Model by the coroutine does not imply that an HTTP client accepts that Python
object without encoding. Use the returned response rather than depending on the
current stand-in mutating and returning the same request object.

Tests and mocks should exercise the external contract, including relevant request
fields and returned outcomes, while the internal workflow remains free to use its
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
use `.run(...)` or an applied job. The current implementation internally delegates
the in-flow call to `.run()` and still permits explicit `.run()` there; the rule
describes the intended authoring API. In linear/DAG declarations, supply child
templates directly and let the composition invoke them.

### Specialization with modifiers

Put behavior intrinsic to a reusable job on its base decorator. Put settings
specific to its surrounding workflow in `.refine(...)` at the composition site.
For example, a job designed to process datasets can declare iteration on its base
template; a general one-item operation can instead gain iteration in a refinement.
Use meaningful function names and set `name` for distinct specializations.

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
This modifier does not make synchronous work asynchronous or consume async
generators. Keep the callable contract and execution context clear instead of
probing results with `isawaitable()`.

Use persistence and restoration modifiers when the workflow needs those behaviors;
inspect their current semantics before promising caching or recovery. DAG-specific
input retention (`consume_kwargs_from_results`) is covered with routing below.

## Routing rules that matter

Use the shared modifiers above together with these composition rules:

| Mechanism | Meaning |
| --- | --- |
| `LinearFlowTemplate(a, b, c)` | Each child receives the preceding child's result; the last result is returned. |
| Linear flow keyword-only inputs | Available by matching name to children. Positional-capable flow arguments are bound and passed positionally to the first child, even if the caller used keyword syntax. Use `*` for shared configuration. |
| `DagFlowTemplate(...)` | Routes by parameter names from accumulated inputs/results. Children currently execute in declaration order; a DAG declaration does not imply concurrent branches. |
| A nonempty dictionary result | Its entries update the DAG's available named results. A plain dictionary is appropriate for this routing purpose; its values can remain typed objects. |
| Other DAG results | Stored under the child's job name unless explicitly wrapped with `result_key`. The overall return is the last child's result, not the whole result store. |
| `consume_kwargs_from_results=True` (default) | Removes routed arguments from the DAG result store when consumed. |
| `consume_kwargs_from_results=False` | Keeps routed arguments available for later children; results can still replace values under the same keys. Use when extraction and later collection both need the aggregate, or several children reuse a value. |

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
declares the public signature while their child list defines the execution. The
outer callable type is validated when the template is created:

- any async child makes the composed flow asynchronous, even if the terminal
  collector is synchronous;
- the terminal child determines whether the result is a single value or a stream;
  a supported generator-like terminal return annotation can also establish the
  streaming contract;
- a mismatch raises `TypeError` when the template is created, rather than leaving
  callers to discover the wrong calling convention at runtime.

Thus an async fetch followed by synchronous normalization and collection is still
an `async def` flow returning one result:

```python
import omnipy as om


@om.LinearFlowTemplate(fetch_async, normalize, collect)
async def load_records(source: str) -> list[str]:
    ...
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
workflow. Exhaustive callable-type × job-type coverage belongs in the framework's
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
appropriate failed/pending-item API and choose a policy before finalization. A
service-declared failure stored in a record's status/error fields is distinct from
an exception recorded as `FailedData`; account for whichever forms the workflow
uses. Do not add a retry policy just because an example is asynchronous.

Direct typed updates are the preferred expression when a task owns the record it
enriches. Collect returned datasets back into the aggregate through typed
assignments, and express derived summaries in validators. Keep nested updates
within the [Model boundaries described above](#validation-through-model-boundaries).
If snapshot isolation is needed, make it explicit instead of serializing/rebuilding
everything by default.

## Example: publish a catalog

This compact example shows the pattern outside submission brokering. It is
executable as one module; the comments indicate where to split it in a real
package. Its service is a deterministic async stand-in. Publication identifiers
are observable results; the final receipt is created only after all items succeed.
`CatalogDataset` represents the record batch; `PublicationModel` is the surrounding
composite record that combines that dataset with metadata and a receipt.
Each catalog record's primary key is `record_id`, and its Dataset key is that
same string. The service-assigned `publication_id` is a separate identifier.

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
class CatalogModel(om.Model[CatalogSchema]):
    ...


class CatalogDataset(om.Dataset[CatalogModel]):
    ...


class PublicationMetadataSchema(pyd.BaseModel):
    catalog_name: str


@om.mimics(PublicationMetadataSchema)
class MetadataModel(om.Model[PublicationMetadataSchema]):
    ...


class PublicationSchema(pyd.BaseModel):
    records: CatalogDataset
    metadata: MetadataModel
    receipt: str | None = None


@om.mimics(PublicationSchema)
class PublicationModel(om.Model[PublicationSchema]):
    ...


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
    # Accessing failed/pending items raises; missing identifiers also block completion.
    if not all(record.publication_id for record in publication.records.values()):
        raise ValueError('Every catalog record needs a publication identifier')
    publication.receipt = (
        f'{publication.metadata.catalog_name}: {len(publication.records)} records published'
    )
    return publication


# flows.py
@om.DagFlowTemplate(
    extract_publication,
    publish_records.refine(param_key_map={'dataset': 'records'}, result_key='records'),
    collect_publication,
    consume_kwargs_from_results=False,
)
async def publish_catalog_records(publication: PublicationModel) -> PublicationModel:
    ...


@om.LinearFlowTemplate(publish_catalog_records, create_receipt)
async def publish_catalog(publication: PublicationModel) -> PublicationModel:
    ...
```

The `publication` input must survive `extract_publication` for `collect_publication`
to use it. The iterated result replaces `records` in the DAG store. The synchronous last task in
`publish_catalog` does not make the parent synchronous. An empty catalog produces
a zero-item receipt here; decide whether that is appropriate in the actual domain.

The repository-test shape is `completed = await publish_catalog.apply()(publication)`
under the existing runtime fixture, followed by expected enriched-output and
relevant run-state assertions. Use Dataset keys equal to the records' `record_id`
values, with distinct IDs and titles so accidental item swapping is visible. A
failure-path check can replace the service with a raising stand-in and verify that
no completion receipt is produced.

## Status from facts and acknowledgements

Tasks record what an operation established. Models derive the status implied by
those facts. Distinguish a recorded outcome from a computed summary even when
both use the same status vocabulary.

Choose where status lives according to the use case. A small record may keep
`transfer_status` and `error` inline; a record with several related statuses may
group them under a typed `status` member. A separate structure can fit when status
has distinct ownership, reuse, or reporting requirements. These are design options,
not a rule that item status must be inline or aggregate status must be separate.
Choose the simplest layout that serves the data's consumers and contracts. Wherever
the resulting status is stored, its derivation needs access to the authoritative
inputs; storage placement and validator placement are related but distinct choices.

In the submission example, the registration task stores the returned identifier:

```python
sample.biosample_vault_sample_id = bsv_submission.biosample_vault_sample_id
```

The enclosing model derives registration readiness from the sample identifiers.
The task does not also set an aggregate registration flag. Similarly, the
allocation task records `metadata.sequence_depot_submission_id`; the enclosing
model derives `sequence_depot_submission_id_status` from its presence.

A transfer outcome cannot be inferred merely from a prepared destination URL.
The transfer task records the service's result on its own file:

```python
file.transfer_status = status
file.error = error
```

The aggregate's transfer status is then derived from its files' outcomes. Put
that validator on the model containing the files, not on a status-only record
with no access to them. Iterated tasks update and return individual items; the
collector assigns the returned Dataset to the aggregate. This separates per-item
outcomes from the aggregate summary without a shared status counter in async tasks.

Use normal Model operations for these updates. Model validation is part of the
contract and maintains computed status through the typed interface; no routine
`validate_content()` call, serialization/reconstruction, or separate "refresh
status" task is needed. Keep mutable nested containers within the
[Model boundaries](#validation-through-model-boundaries) already described.
Derivation should be repeatable and depend on the current facts, including when
an identifier is absent or an outcome changes. Validators must not perform service
calls or fabricate successful operation results.

Define aggregate status policy explicitly when it matters. For example, the
submission's transfer summary gives failure precedence over pending work and uses
`N/A` for no files. Those are domain choices, not universal semantics for every
workflow. Account for the Dataset's failed/pending items as well as any recorded
service failures before declaring readiness.

Readiness and confirmed completion are separate. Having the required identifiers
and completed transfers makes a submission ready for its final service call.
`sequence_depot_submission_status` becomes `completed` only after that service
confirms acceptance. Preserve such non-inferable outcomes as explicit state, or
derive their display status from a recorded acknowledgement when one is stored.
A finished job alone does not prove domain success.

Keep status derivation and service contracts separate. If derived fields must be
omitted or frozen at a service boundary, select an appropriate outbound schema;
do not require a second model hierarchy in every workflow.

## Validation and narrative tests

Assert the authoritative outputs and acknowledgements as well as their derived
statuses. A test that checks only a task-written `completed` flag can pass without
proving the required operation happened. Exercise relevant mixed or incomplete
outcomes to verify the chosen aggregation and finalization policy.

Validate relationships using the declared primary keys, with Dataset keys
representing their serialized values. A uniqueness check must compare like types;
coverage/cardinality rules must consider records with no children as well as
records that do have children. See the
[concrete relationship examples](#identity-and-relationship-contracts). Keep the
intended invariant separate from historical implementation mistakes.

Use independent expected data in fixtures, not the same mapper under test to
generate the expected result. In the scenario, call the actual flow and service
adapters; assertions inside fixture-specific tasks cannot substitute for testing
their observable output. Service spies are useful when transmitted payloads or
calls are part of the contract. Keep the main narrative short, and add focused
negative cases for the specific validators or completion policy being introduced.

Isolate mutable stub state per test. The reference scenario uses a `ContextVar`
holding an ID iterator and resets its token in a fixture. Use that pattern when
async contexts need it; a stateless stub needs no context machinery. Avoid relying
on concurrent service-call order to correlate returned IDs with input records.

## Source map

- Complete composition: `tests/integration/novel/full/sequence_data_brokering/`.
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
- Pydantic compatibility: `src/omnipy/util/pydantic.py`.
