# Shared Dataset primary-key validation

Status: revised proposal for discussion. Dataset-native primary-key declarations,
rekeying, and continuous key maintenance below are not implemented in Omnipy.

## Direction and interim support

The sequence-submission example repeats the same key/content check for samples
and files. The catalog example needs it too. Make primary-key handling a Dataset
feature, rather than a shared validator attached to containing Models. A Dataset
must enforce its own identity contract both standalone and inside an aggregate.
Foreign-key and paired-file relationships spanning Datasets remain on the type
that contains their inputs.

This supersedes the earlier proposal for `dataset_primary_key_validator()` and
a shared Model-validator module. The implemented
[`PrimaryKeyDatasetModel`](../../../../src/omnipy/components/nested/models.py)
provides the intermediate conversion approach until Dataset-native support lands.
It accepts a Dataset of wrapped Pydantic records or a list Model of Pydantic
records and constructs a Dataset keyed from record fields. Import it from
`omnipy.components.nested.models`, and `PrimaryKey` from
`omnipy.data.primary_keys`; these are available in the current checkout, not
top-level `omnipy` exports.

The converter handles all declared key fields in order, validates field names,
and rejects duplicate serialized keys before constructing the output Dataset.
It recomputes supplied Dataset keys rather than rejecting mismatches, without
renaming keys in the source Dataset. The
[component tests](../../../../tests/components/nested/test_models.py) cover
composite escaping, serialized-key collisions, and recomputation. Unlike the
earlier example-local prototype, it does not silently overwrite duplicate keys.
It remains a conversion boundary, not a continuously maintained Dataset invariant;
dict-valued item Models and direct iterator input remain in the native feature's
planned scope below.

## Dataset primary-key declaration

Add a dedicated primary-key type parameter, separate from the item Model type.
Use a `PrimaryKeyT` TypeVar exclusively for the ordered key-field declaration,
building on `PrimaryKey[Literal['field'], ...]` from the interim model and planned
table architecture. Do not encode the declaration in a union of possible item
types or require a wrapper Model merely to retain it.

An illustrative specialization is
`Dataset[CatalogRecordModel, PrimaryKey[Literal['record_id']]]`; samples would
declare `local_sample_alias`, files `file_id`, and measurements could declare
`PrimaryKey[Literal['station_id'], Literal['measured_at']]`. This syntax is
proposed, not an available API; finalize parameter placement and the no-key
default while preserving existing `Dataset[ItemModel]` behavior. Ordinary
Datasets must remain usable without a primary-key declaration.

Validate the declaration at specialization: one or more distinct, nonempty string
field names in a fixed order. Preserve the declaration through subclassing,
copying, serialization/loading into the declared Dataset type, and typed Dataset
operations. Prefer mypy-compatible typing for this library feature and verify
basedpyright support too. Share declaration semantics and serialization with the
table work without requiring implementation of the entire table API.

## Supported records and input forms

Support both dict-valued item Models and Models wrapping Pydantic records. Read
selected fields by mapping lookup for dicts and attribute access for records,
through the Model interface in each case. Item Models own normalization and
intrinsic validity; derive or check keys from their parsed values, not raw input.
Do not serialize or rebuild whole records just to access key fields.

| Input | Required behavior |
| --- | --- |
| Existing Dataset or mapping whose values are dicts or Pydantic records, including their Models | Parse values through the declared item Model, then validate supplied outer keys against normalized primary keys. Preserve available entries and task markers. |
| Iterator/iterable of `(key, value)` pairs | Preserve each occurrence until its value is parsed and its supplied key and uniqueness are checked. Do not collapse pairs into a dict first. Values may be dicts, Pydantic records, or their Models. |
| Iterator/iterable of Pydantic records, including their Models | Parse records, derive serialized keys from their normalized fields, reject collisions, then store them in the Dataset. Do not require callers to invent temporary keys. |

Consume one-shot iterators once. Dataset parsing may first produce parsed records
and then validate/derive their keys, provided duplicate occurrences survive until
the collision check. A post-parse validator cannot recover entries lost during
earlier mapping construction. For explicitly supplied keys, ordinary construction
rejects mismatches; intentional canonicalization belongs to rekeying rather than
silently overriding caller identities.

## Shared key serialization and errors

Reuse the implemented `serialize_primary_key(components) -> str` in
[`omnipy.data.primary_keys`](../../../../src/omnipy/data/primary_keys.py), shared
with the interim converter, for Dataset and the planned table architecture. Model
components use `to_data()` here because this is a serialization boundary. Follow
the [table key-serialization contract](2026-10-16-table-model-architecture-and-conversions.md#key-serialization):

- Preserve single-component strings; stringify other supported components.
- Escape `%` and `|` in composite components and join them with `|`.
- Reject unstable default address-based object representations.
- Reject collisions of serialized strings, even for different typed values such
  as `1` and `'1'`; never append generated uniqueness suffixes.
- Keep key fields visible in the record. Never recover them by parsing outer keys.

Report missing fields, invalid components, key mismatches, and collisions with
the input position or outer key, selected fields, and expected serialized key.
Retain field-local locations when a Dataset is used in a Pydantic schema. Empty
Datasets satisfy this invariant; minimum cardinality remains a separate rule.

## Rekeying and continuous maintenance

Rekeying and continuous key maintenance are part of this work, not a deferred
extension. They apply to Datasets with an explicit primary-key declaration.

- Provide an explicit rekeying operation that recomputes keys from parsed record
  fields, including when converting an existing Dataset with arbitrary keys.
  Plan the complete target mapping before replacing it: detect all collisions
  before any record can be overwritten. Finalize the operation's public name and
  return/in-place contract during API design.
- Maintain key/content agreement after construction, item insertion/replacement,
  bulk updates, and successful changes to stored records' key fields through
  supported Model/Dataset interfaces. Pydantic attribute assignments, dict-item
  assignments, and mutations of mutable key components must all be covered.
- A normalized primary-key change moves the existing item from its old Dataset
  key to its new serialized key. Remove the old lookup, retain the record and
  non-key fields, and preserve the item's relative iteration position. A change
  normalizing to the same serialized key does not create another entry.
- Reject conflicting or invalid changes atomically: both the record's data and
  the Dataset mapping must remain unchanged, including through held Model
  references. Bulk rekeying checks the final key set, so key swaps do not fail
  merely because of an intermediate ordering. This is local mutation atomicity,
  not transactional rollback of whole jobs.
- Track changes through held references to stored item Models, not only
  `dataset[key]` expressions or assignments of the whole Dataset to a parent.
  Specify ownership/subscriptions for shared Models, copies, replacement, and
  removal; detached records must not keep updating their former Dataset. Resolve
  the policy for an item shared across Datasets before promising the invariant.
- Direct mutation of raw `.content` or an external unwrapped object bypasses
  Model validation; do not promise interception of arbitrary external writes.
  Explicit rekeying must detect or reconcile such stale keys without data loss.
- Pending/failed markers have no record fields to inspect. Preserve their keys
  and status, reserve those occupied slots during collision checks, and enforce
  the invariant when a record replaces a marker. Primary-key validity does not
  certify completion or make aggregate assignment accept markers automatically.

Dataset-level validation after parsing supplies the construction boundary, but
does not by itself implement ongoing maintenance. A previous Model-validator
prototype accepted normalized construction and rejected mismatches, yet a change
through `group.records['a'].local_id = 'b'` left outer key `'a'` unchanged until
whole-Dataset reassignment. Use this as a regression case for the new feature,
not evidence that containing Model validators maintain Dataset identities.

## Focused verification before landing

1. Cover Dataset/mapping inputs with dict and Pydantic items, key/value iterators,
   and record-only iterators, including one-shot generators and wrapped items.
   Verify normalization precedes key checks/derivation and no input is silently
   dropped or consumed twice.
2. Cover scalar and composite keys, escaping, wrapped scalar components,
   mismatches, missing fields, invalid declarations, empty Datasets, unstable
   components, duplicate supplied keys, and serialized collisions such as `1`
   versus `'1'`. Test collisions before any mapping reduction can hide them.
3. Exercise explicit rekeying, whole-Dataset replacement, insertion, bulk update,
   direct dict-key and Pydantic-field mutation, and nested mutable key components.
   Check held references, normalized no-op changes, key swaps, iteration order,
   copies, shared ownership, removal, and serialization of the resulting keys.
4. Verify rollback of both record values and outer keys on every failing mutation
   path; test pending/failed slot collisions and completion with parsed records.
   Keep foreign-key validation and batch-completion policy separate.
5. Verify the default preserves existing unkeyed Dataset behavior, specialized
   item types and key declarations survive operations, and mypy/basedpyright
   see the intended constructor and item-access contracts.

After agreement and implementation, replace the repeated sequence validators
and interim `PrimaryKeyDatasetModel` conversions where Dataset-native support
applies. Until then, keep generated dataflows on current APIs and distinguish
the implemented intermediate converter from this planned Dataset feature.
