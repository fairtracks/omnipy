# Shared Dataset primary-key validation

Status: proposal for discussion; the APIs below are not implemented in Omnipy.

The sequence-submission example repeats the same key/content check for samples
and files. The catalog example needs it too. Extract the invariant once and make
each containing schema declare which fields form the primary key. Keep the
declaration visible in the schema, as in the existing top-level validators.

## Proposed use

```python
# Proposed API, not an available import yet.
from omnipy.data.validators import dataset_primary_key_validator


class PublicationSchema(pyd.BaseModel):
    records: CatalogDataset
    metadata: MetadataModel
    receipt: str | None = None

    _record_keys = dataset_primary_key_validator('records', key_fields=('record_id',))
```

The sequence-submission schema would replace its two repeated validator bodies
with:

```python
_sample_keys = dataset_primary_key_validator(
    'samples', key_fields=('local_sample_alias',))
_file_keys = dataset_primary_key_validator('files', key_fields=('file_id',))
```

A composite key uses the same declaration:

```python
_measurement_keys = dataset_primary_key_validator(
    'measurements', key_fields=('station_id', 'measured_at'))
```

These are schema declarations, not workflow jobs. Item schemas still own
normalization and field validity. Key validation runs after those schemas have
parsed their values. It checks outer keys against normalized content and rejects
mismatches rather than silently changing identities.

## Implementation shape

Use three small pieces:

1. `serialize_primary_key(components) -> str`: one serialization implementation
   shared with the planned table architecture. Model components use `to_data()`
   here because this is explicitly a serialization boundary. Follow the
   [table key-serialization contract](2026-10-16-table-model-architecture-and-conversions.md#key-serialization):
   preserve single-component strings, escape `%` and `|` in composite components,
   join with `|`, and reject default address-based object representations.
2. `validate_dataset_primary_keys(dataset, *, key_fields)`: a generic validator
   returning the same Dataset object/type after checking its available records.
   Extract named attributes through the record Models' interfaces; do not
   serialize/rebuild whole records. Report the offending outer key, expected
   serialized key, and selected fields. An empty Dataset is valid for this
   invariant; minimum cardinality is a separate rule.
3. `dataset_primary_key_validator(field, *, key_fields)`: a thin Pydantic adapter
   that registers the reusable check on the containing schema. The current
   compatibility API uses `pyd.validator(field, allow_reuse=True)`. A future v2
   migration changes this adapter, leaving the serializer and invariant intact.

Proposed location: `src/omnipy/data/validators.py` for the shared check and adapter,
with a dependency-neutral key serializer shared by Dataset and table code. The
first implementation needs record attributes; table code can extract its own
logical cells and call the same serializer. It does not need a universal record
access abstraction yet.

The essential adapter and check would look like this; the serializer is specified
separately above:

```python
from typing import TypeVar

from omnipy.data.dataset import Dataset
import omnipy.util.pydantic as pyd

_DatasetT = TypeVar('_DatasetT', bound=Dataset)


def validate_dataset_primary_keys(
    dataset: _DatasetT, *, key_fields: tuple[str, ...],
) -> _DatasetT:
    if not key_fields or len(set(key_fields)) != len(key_fields):
        raise ValueError('Specify one or more distinct primary-key fields')
    for dataset_key, record in dataset.available_data.items():
        try:
            components = tuple(getattr(record, name) for name in key_fields)
        except AttributeError as error:
            raise ValueError(
                f'Missing primary-key field in Dataset entry {dataset_key!r}') from error
        expected = serialize_primary_key(components)
        if dataset_key != expected:
            raise ValueError(
                f'Dataset key {dataset_key!r} must match primary key {expected!r} '
                f'from {key_fields!r}')
    return dataset


def dataset_primary_key_validator(field: str, *, key_fields: tuple[str, ...]):
    def validate(cls, dataset):
        return validate_dataset_primary_keys(dataset, key_fields=key_fields)

    return pyd.validator(field, allow_reuse=True)(validate)
```

Validate the declaration itself when building the adapter, too: a nonempty tuple
of distinct nonempty field names. Preserve Pydantic's field-local error reporting.
Do not add guards for unrelated missing fields; this validator depends only on
its own Dataset field. Keep foreign-key and paired-file validators separate.

## Behavior that must stay explicit

- Pending and failed entries have no current record whose primary key can be
  checked. Validate available records and leave the task markers intact. This
  does not certify that a batch is complete; completion checks own that policy.
  The pure check can inspect a Dataset containing markers, but the adapter does
  not make every aggregate assignment accept them: current Model assignment may
  call Dataset `to_data()` and raise first. Inspect failures before collection.
- A mapping with unique outer keys that all equal the serialized primary keys
  necessarily has unique serialized keys. When deriving a Dataset from a sequence,
  check collisions before constructing the mapping: a validator cannot recover
  entries already overwritten by a dictionary comprehension.
- Reusing this schema adapter does not attach a primary-key declaration to every
  standalone instance of the Dataset class. The containing Model is the chosen
  validation boundary. Moving the invariant into a reusable keyed Dataset type
  is a later extension, sharing the same check and serializer.
- Automatic re-keying is outside this change. Do not imply that changing a
  record's primary key renames the Dataset key. Verify how mutation reaches the
  containing Model's validators, including held references, before promising
  continuously maintained aggregate invariants. Primary-key changes should be
  explicit operations with collision checks and atomic behavior.
- Keep the future table API's `PrimaryKey[Literal[...]]` declaration distinct from
  this value-level validator configuration. The serializer and semantics should
  converge; this proposal does not implement the table API or require its generic
  machinery as a prerequisite.

## Focused verification before landing

Cover normalized scalar IDs, matching and mismatching keys, composite escaping,
missing fields, invalid declarations, empty Datasets, and stable/nonstable key
components. Check wrapped scalar components (including integers) and collisions
such as `1` and `'1'` at the sequence-to-Dataset boundary. Verify same-type return,
preserved pending/failed markers, and error locations under the containing field.

Exercise construction, whole-Dataset replacement, item insertion, and nested
primary-key mutation through the containing Model. Inspect resulting data after
failed mutations: immediate rejection and atomic rollback must be demonstrated,
not inferred from successful construction tests.

A temporary prototype on the current checkout accepted a normalized key and
rejected mismatches on construction. Changing a contained item's primary key
through `group.records['a'].local_id = 'b'` did not immediately invoke the
containing key validator: the serialized aggregate retained outer key `'a'` and
inner key `'b'`. Assigning the Dataset through `group.records = ...` then rejected
the mismatch. This is why the proposed adapter consolidates boundary validation
without claiming continuous key maintenance.

After agreement and implementation, replace the repeated sequence validators
and add the catalog declaration using this helper. Keep generated dataflows on
current APIs until then; the skill should not teach this proposal as available.
