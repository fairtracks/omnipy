# Table model architecture and conversions

## Status and scope

This specification records the agreed direction for Omnipy table models, their public
representations, conversions, Pydantic integration, Pandas integration, and Dataset
interoperability. It is a design document; it does not itself change implementation.

The design prioritizes explicit physical data shapes, conversion-oriented models, and
composable type-aware conversion routes. It avoids public facades that secretly substitute
unrelated runtime model classes.

## Goals

- Support positional, named row-wise, column-wise, primary-keyed, Pydantic-record, and
  Pandas-backed tables.
- Keep physical root content visible in each public model type.
- Preserve sparse JSON-like row backing data while exposing a logical rectangular table view.
- Preserve row order in all table conversions.
- Treat primary keys as a portable table identity concept, separate from Pandas indexes.
- Support direct structural conversions where root data matches, and declare only genuine
  semantic conversions.
- Make list-to-Dataset identity creation explicit.
- Permit future backend integrations without multiplying hidden or ambiguous conversion behavior.
- Keep `to_data()` and `to_json()` output strictly JSON-compatible in all table families.

## Terminology and invariants

| Term | Meaning |
|---|---|
| Column name | A unique `str` identifying a logical named column. |
| Row position | Ordered integer row location. Row order is significant. |
| Primary key | One or more visible named fields uniquely identifying a row. |
| Serialized primary key | Deterministic `str` representation used for keyed mappings and Dataset keys. |
| Cell type | Logical ordinary cell type, for example `JsonScalar`. |
| Record type | A Pydantic `BaseModel` describing one complete logical row. |
| Missing value | A value denoting a missing cell: `None` for nullable cells, `NaN` for non-nullable float cells, and `pd.NA` in Pandas-backed models. |
| Default value | The `CellT`-dependent value used for an absent logical cell or to pad a rectangular cell table. |

Omnipy uses **primary key**, not index, for its portable row-identity concept. A Pandas
index is backend-specific and may be configured to mirror a primary key.

### Named-column policy

Named Omnipy table models require unique string column names. Import of duplicate or
non-string external column labels should initially fail rather than silently normalize or
reinterpret header data. Lossless label normalization is deferred.

### JSON interoperability

JSON is the interoperability backbone of Omnipy:

- `to_data()` outputs only Python types that correspond to JSON types (`None`, `bool`, `int`,
  `float`, `str`, `list`, `dict`);
- `to_json()` outputs strict JSON. Non-finite floats (`NaN`, `Infinity`, `-Infinity`) are not
  allowed;
- a missing value is `null` in JSON and `None` in `to_data()` output, in all model families.

Consequences for parsing and serialization:

| Value | JSON-typed cells (cell type includes `None`, for example `JsonScalar`) | Non-nullable float cell types |
|---|---|---|
| Float `NaN` input | Parsed as `None` (missing). | Kept as `NaN` (the in-memory missing value). |
| `None` input | Kept as `None`. | Parsed as `NaN`. |
| In-memory missing value in `to_data()`/`to_json()` | `None` / `null` | `None` / `null` |
| `Infinity`, `-Infinity` | Rejected. | Rejected. |

The `NaN` rule applies to float values only, including `NaN` from lenient JSON parsing and from
Pandas. A string `'NaN'` in a `str`-typed cell stays a string. In float-typed cells, Pydantic
coerces the string `'NaN'` to a float `NaN`, which is then handled as above, consistent with
Pandas `read_csv()` defaults. The rules apply at every nesting level: no `NaN` exists anywhere in
JSON-typed content, including values nested inside list or dict cells (for example
`JsonMaxLevel1Types`) and the content of JSON models.

`JsonScalar` is used directly as a type in table models, not wrapped in `JsonScalarModel`, for
efficiency. Model-level parsing therefore does not reach table cells. The preferred
implementation is a custom Pydantic float type with a validator inside the `JsonScalar` type
alias, so that one rule applies to JSON models and table cells alike, at the cost of one extra
validator call per float. This requires adapting code that inspects cell types, such as
`ColumnModel.default_value()`, which currently checks for `float` in union arguments. If that
proves impractical, every table family must implement the rule explicitly.

Encoding non-finite floats as strings is future work (see "Schema representation and
serialization").

## Public table model families

Separate public models are required whenever the root content shape differs: positional vs named
rows, list-root vs mapping-root, row-wise vs column-wise, or ordinary cells vs Pydantic records.
Primary-key specialization of an unchanged root shape is not a separate model; it is expressed as
the `PKT` type parameter. Private mixins and helpers may share implementation, but public generic
facades that dispatch through `__class_getitem__()` to unrelated implementations are
explicitly rejected.

### Shorthand

```text
RP[CellT]          Row-wise positional table
RH[CellT]          Row-wise first-row-as-header conversion table

R[CellT]           Row-wise cell table
RK[CellT, PK]      Row-wise cell table with primary key

RR[RecT]           Row-wise Pydantic-record table
RRK[RecT, PK]      Row-wise Pydantic-record table with primary key

C[CellT, PKT]      Column-wise cell table
CR[RecT, PKT]      Column-wise Pydantic-record table

PS[CellT]          Pandas Series model (the column model of PST)
PD[CellT, PKT]     Pandas DataFrame cell table
PDR[RecT, PKT]     Pandas DataFrame Pydantic-record table
PST[RecT, PKT]     Pandas Series-table Pydantic-record helper

DS[ItemT]          Dataset
```

`PK` denotes a primary-key specialization such as:

```text
PrimaryKey[Literal['sample_id']]
```

or:

```text
PrimaryKey[
	Literal['project_id'],
	Literal['sample_id'],
]
```

`PrimaryKey['sample_id']` is used as shorthand for `PrimaryKey[Literal['sample_id']]`.

`No PK` is shorthand in this document for the implementation sentinel `NoPrimaryKey`. `PKT` is the
primary-key type parameter of families that may or may not have a key: `PKT` is either a `PK` or
`No PK`. `RK` and `RRK` always have a key, so they take `PK` and cannot be given `No PK`.

`RH[CellT]` uses adjusted-model parameters to control header-relative row parsing:

```text
Params.extra_columns = AddExtraColumns     Default permissive policy.
Params.extra_columns = RejectExtraColumns  Strict policy.

Params.short_rows   = AcceptMissingColumns  Default permissive policy.
Params.short_rows   = RejectShortRows       Strict policy.
```

### Proposed public classes

```text
RowWisePositionalTableModel[CellT]
RowWiseTableFirstRowAsColNamesModel[CellT]

RowWiseTableModel[CellT]
RowWiseTableWithPrimaryKeyModel[CellT, PKT]

RowWiseTableOfPydanticRecordsModel[RecT]
RowWiseTableOfPydanticRecordsWithPrimaryKeyModel[RecT, PKT]

ColumnWiseTableModel[ColModelT, ColItemT, PKT]
ColumnWiseTableOfPydanticRecordsModel[
	RecT,
	ColWiseTableModelT,
	ColModelT,
	ColItemT,
	PKT,
]

PandasSeriesModel[CellT]
PandasDataFrameModel[CellT, PKT]
PandasDataFrameOfPydanticRecordsModel[RecT, PKT]
PandasSeriesTableOfPydanticRecordsModel[RecT, PKT]
```

### Root content shapes

| Shorthand | Root content |
|---|---|
| `RP[CellT]` | `list[list[CellT]]` |
| `RH[CellT]` | `list[dict[str, CellT]]` (structurally the same as `R[CellT]`) |
| `R[CellT]` | `list[dict[str, CellT]]` |
| `RK[CellT, PK]` | `dict[str, dict[str, CellT]]` |
| `RR[RecT]` | `list[PydanticRecordModel[RecT]]` |
| `RRK[RecT, PK]` | `dict[str, PydanticRecordModel[RecT]]` |
| `C[CellT, PKT]` | `dict[str, ColModelT]` |
| `CR[RecT, PKT]` | `dict[str, ColModelT]`, validated per logical row |
| `PS[CellT]` | `pd.Series` |
| `PD[...]` / `PDR[...]` | `pd.DataFrame` |
| `PST[...]` | `dict[str, PS[object]]` |

### Cell and record variants

`CellT` and `RecT` are conceptually alternative schema modes, but they have separate public
model families:

- `CellT` describes ordinary homogeneous logical cell values.
- `RecT` describes Pydantic-validated heterogeneous logical records.

For column-wise models, a logical `CellT` maps to implementation-level type parameters. `C` takes
`ColModelT` and `ColItemT`; `CR` additionally takes `ColWiseTableModelT`, the table type that
record validation instantiates for its output:

| Logical cell type (`ColItemT`) | `ColModelT` | `ColWiseTableModelT` (`CR` only) |
|---|---|---|
| `JsonScalar` | `JsonScalarColumnModel` | `JsonScalarColumnWiseTableWithColNamesModel` |
| `JsonMaxLevel1Types` | `JsonMaxLevel1ColumnModel` | `JsonMaxLevel1ColumnWiseTableWithColNamesModel` |
| `JsonMaxLevel2Types` | `JsonMaxLevel2ColumnModel` | `JsonMaxLevel2ColumnWiseTableWithColNamesModel` |
| Future `int` specialization | Future `IntColumnModel` | Future `IntColumnWiseTableModel` |

`ColItemT` is the item type of the column model, that is, the logical cell type. `ColModelT` and
`ColWiseTableModelT` determine which column and table implementations instantiate, pad,
concatenate, and validate that cell type. These remain implementation details and are omitted from
the conceptual shorthand. The table lists the current class names; the `WithColNames` names are to
be renamed together with `ColumnWiseTableWithColNamesModel` (see TODOs).

## Positional and header-aware tables

### Positional rows

`RP[CellT]` stores positional rows:

```text
[
	['s1', 10],
	['s2', 20],
]
```

It supports raw delimited parsing, matrix-like data, and future backend-specific variants. A
future NumPy-backed positional table should be a separate family, for example:

```text
NumpyRowWisePositionalTableModel[CellT]
```

rather than a higher-kinded generic over arbitrary nested array types.

`RP[CellT]` intentionally does **not** require equal row lengths. It is a parse-oriented
representation of positional sequences, so both inputs below are valid positional data:

```text
[
	['s1', 10],
	['s2'],
]

[
	['s1', 10],
	['s2', 20, 'extra'],
]
```

Whether those rows are rectangular is determined only by a later conversion target:

| Target family | Rectangularity responsibility |
|---|---|
| `RH[CellT]` | Parses short rows as missing header fields; its `extra_columns` parameter decides how longer rows are handled. |
| `RR[RecT]` / `RRK[RecT, PK]` | Cells map to `RecT` fields in declaration order. Short rows must cover all required fields; extra cells of longer rows are passed to Pydantic under generated names, and the extra-field policy of `RecT` decides (see "Positional rows into records"). |
| `C[CellT, PKT]` / `CR[RecT, PKT]` | All physical columns must have equal length. |
| `PD[...]` / `PDR[...]` | A DataFrame is inherently rectangular. |
| `PST[RecT, PKT]` | Series columns must share one positional row length. |

This keeps `RP` aligned with parse-don't-validate: it retains incoming positional structure until
a schema, header policy, columnar representation, or backend imposes additional table invariants.

### Header interpretation

`RH[CellT]` is conversion-oriented. It accepts positional data where the first row becomes
column names:

```text
[
	['sample_id', 'count'],
	['s1', 10],
]
```

and stores named rows:

```text
[
	{'sample_id': 's1', 'count': 10},
]
```

It remains useful in declarative `Chain3` models such as CSV/TSV parsing. It should remain
until future conversion syntax or annotated type declarations can express the same conversion
more directly.

#### Extra positional cells

`RH[CellT].Params.extra_columns = AddExtraColumns` is the default. It preserves a data row that
is longer than the declared header by discovering generated columns instead of silently dropping
trailing cells:

```text
header: ['sample_id', 'count']
row:    ['s1', 10, 'extra']

parses to:
[
	{'sample_id': 's1', 'count': 10, 'column_3': 'extra'},
]
```

Generated columns are appended after declared headers in positional order. The generated-name
scheme must be stable and collision-free; `column_3` is the illustrative name for the third
positional field.

`AcceptMissingColumns` treats cells absent from a short positional row as missing named fields.
`RH` emits the canonical sparse representation used by `R`; it does not pad the named-row
backing data with explicit `None` values:

```text
header: ['sample_id', 'count']
rows:   ['s1', 10]
        ['s2']

emits backing data:
[
	{'sample_id': 's1', 'count': 10},
	{'sample_id': 's2'},
]
```

After conversion to `R[CellT]`, or when viewed as a logical named table, the missing field is
still observable:

```text
table[1]['count'] is None
```

This holds for nullable `CellT`. In general the absent cell reads as the cell type's default value
(see "Cell default values"); for example, in `RH[str]`, as used by CSV/TSV parsing, it reads as
`''`.

A header column that no data row reaches is not retained, and header-only input produces no
columns at all. See "Columns without stored cells" below.

Explicit padding occurs only in a later target that requires rectangular data, such as conversion
to `C[CellT, PKT]` (see "Missing-cell padding" below) or validation/materialization through
`CR[RecT, PKT]`.

`RejectExtraColumns` rejects rows longer than the header. `RejectShortRows` rejects rows shorter
than the header. `CsvTableModel` and `TsvTableModel` should inherit or mix in the same header
parsing parameters but use strict defaults for both policies:

```text
StrictHeaderRows = RH[CellT].adjust(
	'StrictHeaderRows',
	extra_columns=RejectExtraColumns,
	short_rows=RejectShortRows,
)
```

The shared parameter mixin keeps header behavior consistent across direct header conversion and
delimited-text parsing while allowing callers to create an explicitly lenient CSV/TSV parser when
needed.

#### Headerless CSV and TSV

CSV and TSV parser families should also support input without a header line. Headerless parsing
returns positional rows rather than silently inventing column names:

```text
's1,10\ns2,20\n'

==>

RP[str]:
[
	['s1', '10'],
	['s2', '20'],
]
```

The caller can subsequently select a deliberate interpretation:

```text
RP[str] --> RH[str]       Interpret the first row as headers.
RP[str] --> RR[RecT]      Map positions to `RecT` field order.
RP[str] --> other parser  Apply a domain-specific positional schema.
```

Headerless parser variants should have their own concrete output models, such as
`CsvTableWithoutHeaderModel` and `TsvTableWithoutHeaderModel`, rather than making one public
CSV/TSV model claim both positional and named-row root content. Header-relative `extra_columns`
and `short_rows` policies do not apply until a later header or schema conversion establishes an
expected width.

To use externally provided column names, convert through `RR[RecT]`, which takes field names from
`RecT` (see "Positional rows into records").

### Positional rows into records

`RP[CellT] --> RR[RecT]` maps cell *i* of each positional row to field *i* of `RecT`, in field
declaration order, and then validates the record:

- Short rows are accepted if they cover all required fields; the remaining fields take their
  Pydantic defaults. Positional mapping therefore requires all required fields of `RecT` to
  precede all optional fields. This constraint applies to positional input only; named input
  does not need it.
- Long rows: extra cells get generated names, using the same scheme as `RH` (for example
  `column_3`), and are passed to Pydantic as extra fields. The extra-field policy of `RecT`
  decides: `Extra.ignore` (the Pydantic v1 default) drops them, `Extra.forbid` rejects the row,
  and `Extra.allow` keeps them. There is no separate Omnipy parameter for this.

```text
class SampleRecord:
	sample_id: str
	count: int | None = None

RP[str]:
[
	['s1', '10'],
	['s2'],
	['s3', '30', 'extra'],
]

--> RR[SampleRecord]:
[
	SampleRecord(sample_id='s1', count=10),
	SampleRecord(sample_id='s2', count=None),
	SampleRecord(sample_id='s3', count=30),    # 'column_3' dropped by Extra.ignore
]
```

### Named rows to positional rows

`R[CellT] --> RP[CellT]` emits row values in the inferred logical column order. `RP` is mainly an
import/export representation, and two adjusted-model parameters of `RP` control this export:

```text
Params.header_row = HeaderRowIfSupported  Default: emit a header row if CellT can hold str.
Params.header_row = IncludeHeaderRow      Always emit a header row; fail if CellT cannot hold str.
Params.header_row = NoHeaderRow           Emit data rows only.

Params.short_rows = PadShortRows          Default: pad every row to full width.
Params.short_rows = KeepShortRows         Omit trailing cells that are absent from the backing row.
```

With the default, whether `RP[CellT]` has a header row follows from its visible cell type: for
example, `R[JsonScalar] --> RP[JsonScalar]` emits a header row, while `R[int] --> RP[int]` does
not. The header row, when emitted, always lists all known columns.

Absent cells before the last stored cell of a row must always be filled, to keep positions
aligned. They are filled with the cell type's default value (see "Cell default values"). With
`PadShortRows`, trailing absent cells are filled the same way, so all rows have full width. With
`KeepShortRows`, trailing absent cells are omitted, producing ragged rows like the input of `RH`.

```text
R[JsonScalar]:
[
	{'sample_id': 's1', 'count': 10},
	{'sample_id': 's2'},
]

--> RP[JsonScalar]:
[
	['sample_id', 'count'],
	['s1', 10],
	['s2', None],
]

--> RP[JsonScalar] with short_rows=KeepShortRows:
[
	['sample_id', 'count'],
	['s1', 10],
	['s2'],
]
```

`RH` must not coerce non-`str` header cells into column names. Its header row is validated as
`str` values only, so a positional table without a header row, for example from `RP[int]`, fails
instead of silently turning its first data row into column names.

## Sparse row behavior, ordering, and column deletion

### Missing values and sparse backing

`None` denotes a logically missing cell. Absent cells in a logical table view read as the cell
type's default value, which is `None` for nullable cell types (see "Cell default values"). Sparse
backing is a property of the ordinary named row-wise cell-table families only:

| Model family | Raw backing policy | Logical table view |
|---|---|---|
| `R[CellT]` | Sparse `list[dict[str, CellT]]` backing is supported and preserved by `to_data()`/`to_json()`. | Rectangular named rows; absent known cells read as the cell type's default value (`None` for nullable `CellT`). |
| `RK[CellT, PK]` | Sparse inner row mappings are supported and preserved by `to_data()`/`to_json()`. | Rectangular named rows plus primary-key lookup. |
| `RH[CellT]` | Conversion-oriented named-row result. Header conversion determines its produced fields; it is not the general sparse-storage model. | Converts structurally to `R[CellT]`. |
| `RR[RecT]` / `RRK[RecT, PK]` | Store validated Pydantic record models, not sparse raw row dictionaries. | Fields/defaults are represented by the record schema. |
| `C[CellT, PKT]` / `CR[RecT, PKT]` | Column arrays are rectangular; every column has one value per row. | Missing cells are explicit column values. `C` pads them with the cell type's default value (see "Missing-cell padding"); `CR` uses record field defaults. |
| `RP[CellT]` | Positional row sequences; row lengths may differ and no named sparse-cell semantics apply before header parsing. | Column identity remains positional. |
| `PD[...]`, `PDR[...]`, `PST[...]` | Backend-native DataFrame/Series storage. | Backend missing values are normalized at declared conversion boundaries. |

Example sparse `R[JsonScalar]` backing:

```text
[
	{'sample_id': 's1', 'count': 10},
	{'sample_id': 's2'},
]
```

Its table-facing rows are logically rectangular:

```text
table[1]['count']  # None
dict(table[1])     # {'sample_id': 's2', 'count': None}
```

Raw backing data and `to_data()` remain sparse:

```text
table.to_data()
# [
#     {'sample_id': 's1', 'count': 10},
#     {'sample_id': 's2'},
# ]
```

An absent cell in a known column returns the cell type's default value (`None` for nullable
`CellT`); an unknown column name raises `KeyError`.

### Dense-to-sparse conversion into `R`

`R[CellT]` uses canonical sparse backing: cells holding a missing value are omitted from backing
row dictionaries. Missing values are `None` and, for non-nullable float cell types, `NaN` (see
"Cell default values"). This applies both to direct construction and to conversions from
column-wise or other dense representations. For example:

```text
C[JsonScalar, No PK]:
{
	'sample_id': ['s1', 's2'],
	'count': [10, None],
}

==>

R[JsonScalar]:
[
	{'sample_id': 's1', 'count': 10},
	{'sample_id': 's2'},
]
```

This is a backing-data normalization only. In the logical table view, both rows still have the
known `count` column and the second row reads as `None`:

```text
table[1]['count'] is None
```

Direct construction follows the same normalization:

```text
R[JsonScalar]([
	{'sample_id': 's2', 'count': None},
]).to_data()

==>

[
	{'sample_id': 's2'},
]
```

This removes an otherwise unobservable backing distinction: explicit `None` and an absent field
both mean the same logical missing cell in `R`. Canonical sparse backing makes equality,
serialization, conversion round trips, and column-order inference deterministic. Deterministic
does not mean lossless; see the following sections.

### Columns without stored cells

In `R[CellT]` and `RK[CellT, PK]`, a column is known only if at least one backing row contains
it. A Pydantic v1 root model has nowhere else to store column names (see "Pydantic v1
limitation"). Combined with canonical sparse backing, a column whose cells are all missing is not
retained:

```text
C[JsonScalar, No PK]:
{'a': [1, 2], 'b': [None, None]}

==> R[JsonScalar]:
[{'a': 1}, {'a': 2}]

==> C[JsonScalar, No PK]:
{'a': [1, 2]}             # column 'b' is lost
```

The same applies to:

- `RH` header columns that no data row reaches;
- header-only input, which produces no rows and therefore no columns;
- mutation: writing `None` into the last non-missing cell of a column removes the column after
  re-validation, and may change the inferred column order.

Declared primary-key fields are exempt: they are always known columns (see "Primary-key
invariants").

This loss is accepted for now. Future work: store known column names as non-serialized private
state under Pydantic v2. Such state is not part of `to_data()`/`to_json()` output, so plain JSON
round trips remain lossy unless combined with Omnipy-specific lossless serialization.

### Cell default values

Every cell type has a default value, provided by one shared helper (conceptually
`cell_default_value(CellT)`, extracted from the current `ColumnModel.default_value()`). The
default value is used wherever a logical cell exists but no value is stored:

- `R[CellT]` and `RK[CellT, PK]` logical views of absent cells in known columns;
- padding in column-wise cell tables (see "Missing-cell padding").

The `R` view and `C` padding therefore always agree.

| `CellT` | Default value | Lossless? |
|---|---|---|
| Nullable (includes `None`; all current `Json*` cell types) | `None` | Yes. `None` is the missing value in all families. |
| Non-nullable, includes `float` (for example `float`, `int \| float`) | `NaN` | No. Defaulted cells are indistinguishable from real `NaN` values. |
| Other non-nullable (for example `int`, `str`) | Type default (for example `0`, `''`) | No. Defaulted cells are indistinguishable from real values. |

Defaults are potentially lossy, depending on `CellT`. This is consistent with
parse-don't-validate: parsing may lose information. Supporting non-nullable cell types without
requiring nullable backend dtypes is important for interoperability with backends that lack
missing-value support.

Rules for sparse row-wise tables:

- Canonical sparse backing omits missing values only: `None`, and `NaN` for non-nullable float cell
  types, where `NaN` is the default value and therefore reads back unchanged. In JSON-typed cells,
  `NaN` never occurs, as it is parsed as `None` (see "JSON interoperability"). Cells equal to any
  other default value (for example `0`) are real data and remain in the backing rows; omitting
  them would hide data in `to_data()`/`to_json()` and would lose columns whose values all equal
  the default.
- `missing_cells` (see "Strict missing-cell mode") does not apply to `R`/`RK`. They are the sparse
  models; strictness applies where padding happens.
- Primary-key serialization uses logical values, including defaults (see "Key serialization").

#### `NaN` defaults

`NaN` is the default for non-nullable float cell types. Consequences:

- `NaN != NaN`. Python containers compare elements by identity before equality, so whether two
  `NaN`-containing tables compare equal depends on whether they share the same `NaN` objects.
  Separately padded or re-parsed tables may compare unequal. This follows from the user-selected
  cell type.
- Snapshot change detection (interactive mode only) compares content with `==` via `all_equals()`
  (`src/omnipy/util/helpers.py`). Deep-copied Python floats keep their identity, so list-based
  snapshots are unaffected. NumPy and Pandas compare element-wise, and `NaN` positions compare
  unequal, so content with NumPy-style `NaN` (for example a `float64` DataFrame column) always
  appears changed relative to its snapshot. Changes are never missed, but every state-changing
  operation then triggers a full re-validation and a new deep-copied snapshot. See also the
  dirty-flag TODO in `Model._prepare_reset_solution_take_snapshot_if_needed()`
  (`src/omnipy/data/model.py`), which would avoid the equality test altogether.
- Pandas treats `NaN` as missing (`isna()`, `dropna()`, and reductions with the default
  `skipna=True`), so `NaN` padding interoperates with Pandas missing-value handling. NumPy treats
  `NaN` as an ordinary float value. Omnipy follows Pandas: `NaN` is the in-memory missing value of
  non-nullable float cell types, so `C --> R` omits `NaN` cells of such types, and the `R` view
  reads them back as `NaN`.
- Strict JSON has no `NaN`. `NaN` in non-nullable float cells is serialized as `null` by
  `to_data()`/`to_json()`, and `None`/`null` input is parsed back as `NaN`, so the JSON round trip
  is lossless (see "JSON interoperability").

### Missing-cell padding

Column-wise cell tables are rectangular, so a cell that is absent in the source must be filled
when converting into `C[CellT, PKT]`, or when concatenating column-wise tables with different
columns. The fill value is the cell type's default value (see "Cell default values"), so padding
is potentially lossy, depending on `CellT`.

#### Strict missing-cell mode

Column-wise cell models have a `missing_cells` adjusted-model parameter:

```text
Params.missing_cells = PadMissingCells     Default: pad with the cell type's default value.
Params.missing_cells = RejectMissingCells  Strict: fail if any cell would need padding.
```

With `RejectMissingCells`, conversion into the model (for example `R --> C` from sparse rows) and
column-wise concatenation with mismatched columns fail atomically instead of padding. Explicit
cell values that are valid for `CellT`, including explicit `None` for nullable cell types, are not
padding and remain accepted.

```text
StrictColumns = C[int, No PK].adjust(
	'StrictColumns',
	missing_cells=RejectMissingCells,
)

R[int]:
[
	{'a': 1, 'b': 2},
	{'a': 3},
]

--> C[int, No PK]:   {'a': [1, 3], 'b': [2, 0]}   # padded, lossy
--> StrictColumns:   fails: row 1 has no 'b'
```

### Inferred column order

For schema-free sparse rows:

1. collect first-seen column positions;
2. collect adjacent within-row order constraints;
3. perform stable topological ordering;
4. use first-seen ordering where constraints do not determine order;
5. break cycles by first-seen ordering;
6. do not weight constraints initially.

Contradictory sparse-row orderings remain valid schema-free data. Strict order validation is
not planned unless real use cases justify it.

Example: first-seen order alone would yield `('b', 'a', 'c')`, but the second row supplies
stronger relative-order evidence that `a` precedes `b`:

```text
[
	{'b': 2},
	{'a': 1, 'b': 3},
	{'c': 4},
]
```

The inferred column order is:

```text
('a', 'b', 'c')
```

Example: conflicting constraints form a cycle. The table remains valid, and ordering inside the
cycle falls back to first-seen order:

```text
[
	{'a': 1, 'b': 2},
	{'b': 3, 'a': 4},
	{'c': 5},
]
```

The inferred order is:

```text
('a', 'b', 'c')
```

### Column deletion

For schema-free row tables, deleting a whole column removes the field from every backing row
and from the inferred schema.

```text
before backing data:
[
	{'a': 2, 'b': 'x'},
	{'a': 5},
]

del table[:, 'b']

after backing data:
[
	{'a': 2},
	{'a': 5},
]

table.col_names == ('a',)
table[0]['b'] raises KeyError
```

For schema-free column-wise tables (`C`, `PD`), deleting a column removes the column key.

For schema-specialized tables (`RR`, `RRK`, `CR`, `PST`, `PDR`), the record type defines the
columns:

- deleting a field declared in `RecT` fails atomically, whether the field is required or
  optional, and leaves the table unchanged;
- deleting an undeclared extra field, which can only be present if `RecT` allows extra fields,
  removes it from every row, as in schema-free tables.

```text
schema:
class Row:
	a: int
	b: str | None = None

del table[:, 'b']    # fails: 'b' is declared in Row; the table is unchanged
```

Clearing the values of an optional field is a different operation from deleting a column. An
explicit operation for it (for example `table.reset_column('b')`) is future work, together with
controlled schema changes.

## Primary keys

### Primary-key invariants

A primary key:

- consists of one or more visible named fields;
- is unique by its serialized string: any two rows whose keys serialize to the same string are
  rejected, whether or not their key tuples are equal;
- keeps all key fields as visible regular row columns;
- makes all key fields always-known logical columns, taken from the `PrimaryKey[...]` type rather
  than from backing data: reading a key cell returns its value, or the cell type's default value
  if the cell is absent from the backing row, and key columns are never lost (see "Columns without
  stored cells");
- may contain any cell values, including `None` and list or dict values;
- is serialized to `str` for keyed row mappings and Dataset keys;
- rejects unstable default `object.__str__()` representations.

### Key serialization

Keys use deterministic string serialization:

1. stringify each component: if the component has a `to_data()` method (for example an Omnipy
   model), stringify its result; otherwise use `str()` directly, failing if the component type
   only has the default `object.__str__()`;
2. for composite keys only, percent-escape reserved delimiter characters in each component;
3. join composite-key components using `|`;
4. reject collisions;
5. never append generated uniqueness suffixes.

Generated suffixes would make keys dependent on insertion order and unrelated rows.

Single-column keys are the stringified component as is, without escaping, so Dataset keys equal
the raw key values. Single-column and composite keys cannot be confused, as the number of key
columns is fixed by the `PrimaryKey[...]` type.

Examples of valid deterministic serialization:

```text
PrimaryKey['sample_id']
	('s1',)                    -> 's1'
	('a|b',)                   -> 'a|b'
	(None,)                    -> 'None'

PrimaryKey['project_id', 'sample_id']
	('p1', 's1')               -> 'p1|s1'
	('project|north', 's1')    -> 'project%7Cnorth|s1'
	('p1', 'sample%1')         -> 'p1|sample%251'
	('p1', None)               -> 'p1|None'
```

The exact reserved-character set is an implementation detail. Serialization is deterministic and
forward-only: outer keys are always recomputed from row fields and checked, never parsed. Given
the field types, a key can often be mapped back to its components, but not in all cases (for
example, a `JsonScalar` key `'1'` may stem from `1` or `'1'`), and nothing in the design relies
on it.

List and dict components are stringified with `str()`, so equal dicts with different key order
serialize differently and count as different keys. If this becomes a problem, list and dict key
components may be rejected later.

Serialization uses logical cell values. A key cell that is absent from a sparse backing row is
serialized as the cell type's default value; for example, an absent `int` key cell serializes as
`'0'`. Collisions are rejected as usual.

Examples of rejected keys:

```text
('p1', 1) and ('p1', '1')
	-> reject if both serialize to 'p1|1'

(None,) and ('None',)
	-> reject if both serialize to 'None'

('p1', SomeObject())
	-> reject when str(SomeObject()) is the default address-based object representation
```

### Keyed row-wise content

For:

```text
PrimaryKey[
	Literal['project_id'],
	Literal['sample_id'],
]
```

the keyed row representation is:

```text
{
	'p1|s1': {
		'project_id': 'p1',
		'sample_id': 's1',
		'count': 10,
	},
}
```

The required invariant is:

```text
outer_key == serialize(row[primary_key_columns])
```

Mutating a primary-key cell automatically re-keys the outer mapping. Duplicate replacement
keys must fail atomically. Re-keying keeps the row at its position: as a mapping key cannot be
renamed in place, the outer mapping is rebuilt in its original order.

### Column-wise keys

Column-wise keyed models retain their column-oriented root data. Key semantics add primary-key
field validation, uniqueness checks, and row-key-to-position lookup.

For example, given:

```text
C[JsonScalar, PrimaryKey['sample_id']]:
{
	'sample_id': ['s1', 's2'],
	'count': [10, 20],
}
```

keyed row selection needs the derived lookup:

```text
{
	's1': 0,
	's2': 1,
}
```

The lookup is not source data. It is fully derivable from:

1. the declared `PrimaryKey[...]` fields;
2. the retained key columns;
3. row position/order; and
4. the primary-key serializer.

### Pydantic v1 limitation

An Omnipy `Model[T]` is implemented as a Pydantic v1 root model: its validated public content is
the single root value `T`. For a column-wise table, that root value is the column mapping:

```text
dict[str, ColModelT]
```

Pydantic v1 root models (with the `__root__` field) cannot have other fields, and do not support
private attributes either. (`Dataset` is not a root model, which is why `MultiModelDataset` can
use `PrivateAttr`.) A column-wise root model therefore cannot hold an internal field such as:

```text
primary_key_to_row_position: dict[str, int]
```

without changing the model shape from a plain mapping into a wrapper structure. Doing so would
break the intended root representation, structural Dataset conversions, ordinary JSON export, and
the distinction between derived lookup state and table data.

The Pydantic v1 implementation should therefore rebuild the lookup on demand, once per operation:

```text
lookup for one operation (for example a multi-key selection):
	for each row position:
		serialize the declared primary-key column values at that position
		map the serialized key to the position
	resolve every requested key through the mapping, then discard the mapping
```

This costs `O(number_of_rows + number_of_requested_keys)` per operation, is correct, and requires
no persistent state.

Do not use a global cache keyed by model or content identity. Copies, reparsing, snapshots,
interactive rollback, and mutation would make lifecycle and invalidation unreliable.

### Pydantic v2 follow-up

Pydantic v2 can support non-serialized private model attributes. A future implementation may use
a lazily built cache such as:

```text
_primary_key_to_row_position: dict[str, int]
```

The cache remains derived state and must be invalidated or rebuilt after any operation that can
change key values, row positions, or row count, including primary-key cell mutation through a
write-through `IterRow`, whole-column replacement, row insertion/deletion, reordering, and
content replacement. Caching is an optimization to add only if benchmarked keyed lookup workloads
justify it.

## Pydantic record models

`RecT` provides field names, order, coercion, defaults, requiredness, aliases, and per-row
validation. It also validates that primary-key fields exist when a primary key is declared.

Primary keys remain table-level specializations rather than Pydantic field metadata.

Cell and record representations have explicit conversion routes:

```text
R[CellT] <-> RR[RecT]
RK[CellT, PK] <-> RRK[RecT, PK]

C[CellT, PKT] <-> CR[RecT, PKT]

PD[CellT, PKT] <-> PDR[RecT, PKT]
```

Forward conversion validates and coerces. Reverse conversion exports ordinary values and drops
record-schema behavior.

For example:

```text
class SampleRecord:
	sample_id: str
	count: int | None = None
	active: bool = True

R[JsonScalar]:
[
	{'sample_id': 's1', 'count': '10'},
	{'sample_id': 's2'},
]

R[JsonScalar] --> RR[SampleRecord]:
[
	SampleRecord(sample_id='s1', count=10, active=True),
	SampleRecord(sample_id='s2', count=None, active=True),
]
```

The record form stores validated records. Converting it back to `R[JsonScalar]` exports ordinary
row data and drops the Pydantic record-model behavior.

### Missing cells, extra columns, and aliases in record tables

These rules apply to every conversion into or validation in a record table family (`RR`, `RRK`,
`CR`, `PST`, `PDR`), so that row-wise and column-wise families behave alike.

**Missing cells.** A missing cell (`None`, `pd.NA`, or `NaN` for non-nullable float cell types) is
left out of the row before it is validated against `RecT`. Pydantic then applies the field
default, or rejects the row if a required field is missing. `R --> RR` and `C --> CR` thereby
behave the same way. (The current column-wise implementation passes missing cells as explicit
`None`, so a field such as `active: bool = True` fails validation instead of taking its default.)

A consequence is that a missing cell of a field such as `count: int | None = 5` becomes `5`, not
`None`. `R` already behaves this way, as it drops `None` cells. To make this visible, a warning is
logged when a record type is loaded for a table in which a field accepts `None` but has a
non-`None` default.

**Extra columns.** The extra-field policy of `RecT` applies in all record families: `Extra.ignore`
drops undeclared columns, `Extra.forbid` rejects them, and `Extra.allow` keeps them. (The current
column-wise implementation keeps undeclared columns regardless of the policy.)

**Aliases.** Columns are named by the field alias when `RecT` defines one, so that data round-trips
with the external column names. Values are written back under the alias, never as a second column
named after the field.

## Pandas architecture

### Separate Series and DataFrame models

The current broad `PandasModel` should conceptually split into distinct models:

```text
PandasSeriesModel[CellT]
PandasDataFrameModel[CellT, PKT]
PandasDataFrameOfPydanticRecordsModel[RecT, PKT]
```

### Dtypes and missing values

All Pandas-backed models normalize their content to Pandas nullable extension dtypes on every
input path, including DataFrames and Series passed in directly:

- dtypes are inferred per column within what the cell type or record type allows: `Int64`,
  `Float64`, `boolean`, `string`, and `object` for mixed content;
- float columns are never converted to integer dtypes. (`DataFrame.convert_dtypes()` does this by
  default for whole-number floats, for example `[1.0, NaN]` to `Int64 [1, <NA>]`.)
- the missing value is `pd.NA` in all columns, including `object` columns. On input, `None`,
  `NaN`, and `NaT` become `pd.NA`.

On output to non-Pandas families and in `to_data()`/`to_json()`, `pd.NA` becomes the target cell
type's default value (see "Cell default values"): `None` for nullable cell types, `NaN` for
non-nullable float cell types (serialized as `null`), and otherwise the type default, which is
lossy, or an error under `RejectMissingCells`. `C --> PD --> C` therefore round-trips for nullable
and float cell types.

Comparisons involving `pd.NA` yield `<NA>`, which `.all()` skips, so the `NaN` snapshot issue (see
"`NaN` defaults") does not arise for normalized Pandas content.

### Index of unkeyed DataFrames

`PD[CellT, No PK]` and `PDR[RecT, No PK]` keep their incoming DataFrame index in memory. When
content is converted to a non-Pandas family, or output by `to_data()`/`to_json()`, the index is
materialized like `DataFrame.reset_index()`:

- a default `RangeIndex` (`0..n-1`) carries no information and is dropped;
- any other index becomes one column per index level, named after the level;
- unnamed levels get the Pandas default names (`'index'`, or `'level_N'` for multiple levels);
- a level name that clashes with an existing column name fails the conversion.

### Serialization

`PD` and `PDR` `to_data()` and `to_json()` both output the column-wise mapping
`dict[str, list]`, the same shape as `C`, so `PD.to_data() == C.to_data()` for the same table.
Missing values are `None`. A primary-key index is omitted, as the key columns are already
present; a non-default unkeyed index is materialized as columns (see "Index of unkeyed
DataFrames"). The current `PandasModel`, whose `to_data()` outputs columns but whose `to_json()`
outputs records, is inconsistent; this is a bug.

### DataFrame primary keys

For a primary-key-specialized DataFrame, primary-key columns remain visible and the DataFrame
index is configured from them, with unnamed index levels:

```text
df = df.set_index(
	primary_key_columns,
	drop=False,
	verify_integrity=True,
)
df.index.names = [None] * len(primary_key_columns)
```

The index levels are left unnamed because Pandas rejects labels that are both an index level name
and a column name as ambiguous: with a level named `sample_id`, `df.groupby('sample_id')`,
`df.sort_values('sample_id')`, and `merge(on='sample_id')` raise `ValueError`. The key column
names are carried by the `PrimaryKey[...]` type and the visible columns.

Adding a primary key (`PD[CellT, No PK] --> PD[CellT, PK]`) first materializes a non-default
index into columns (see "Index of unkeyed DataFrames") and then sets the key index. Removing a
primary key resets the index with `reset_index(drop=True)` to a `RangeIndex`; nothing is lost, as
the key columns remain visible. The same applies to `PDR`.

Default unnamed `RangeIndex` is not primary-key semantics.

For example, a keyed DataFrame keeps the key column visibly available while also using it as the
Pandas index:

```text
before primary-key specialization:

   sample_id  count
0         s1     10
1         s2     20

PD[JsonScalar, PrimaryKey['sample_id']]:

   sample_id  count
s1        s1     10
s2        s2     20
```

The DataFrame index is an implementation of the declared primary key, not a replacement for the
visible `sample_id` column.

### DataFrame record validation

`PDR[RecT, PKT]` is a DataFrame-root model, but it does not implement a second independent
Pydantic table-validation algorithm. It validates through a temporary `PST[RecT, PKT]` instance
and reconstructs a validated DataFrame from the resulting Series columns.

The conversion flow is:

```text
input pd.DataFrame
	-> extract named Series columns
	-> normalize temporary Series indexes to row positions
	-> PST[RecT, PKT] validation
	-> validated/coerced Series columns
	-> reconstruct pd.DataFrame
	-> restore or rebuild DataFrame index
```

Validation may:

- coerce existing cells according to `RecT` fields;
- materialize fields supplied by Pydantic defaults;
- reject rows missing required fields;
- apply the same alias and extra-field behavior as the corresponding `CR[RecT, PKT]` model;
- validate declared primary-key fields after coercion.

The DataFrame index is handled after validation:

| `PDR` specialization | Final index behavior |
|---|---|
| `PDR[RecT, No PK]` | Preserve the incoming DataFrame index after reconstruction. Validation never drops or reorders rows. |
| `PDR[RecT, PK]` | Rebuild a unique index from retained primary-key columns with `drop=False`, `verify_integrity=True`, and unnamed index levels. |

This keeps backend index behavior separate from positional row validation. The temporary `PST`
uses positional rows; the final `PDR` retains the appropriate DataFrame-facing index semantics.

### Series-table helper

`PST[RecT, PKT]` is specifically a Pydantic-record Series-column helper. Its root content is a
mapping of column names to `PS` columns:

```text
dict[str, PS[object]]
```

`PS[CellT]` (`PandasSeriesModel`) wraps a `pd.Series` and implements the column-model interface of
the column-wise table families: positional reads and writes (`.iloc`), `filled()`,
`default_value()` (which returns `pd.NA`), and concatenation with the index reset to row
positions. `PST` uses `PS[object]` columns, as the fields of `RecT` have different types, and the
dtype of each column is inferred (see "Dtypes and missing values"). Selecting a single column from
a `PD` or `PST` returns a `PS`, and `PS` is the item type of a Dataset created from a `PST`.

`PST` is not a general `CellT` table family. It must be an actual subclass of the future
`ColumnWiseTableOfPydanticRecordsModel` (`CR`) base, which has the type parameters
`RecT, ColWiseTableModelT, ColModelT, ColItemT, PKT`. The current
`IteratingPydanticRecordsModel` has no `PKT` parameter and no primary-key behavior; `PST` gets
primary-key behavior only once the `CR` base has it. The Series-backed column model replaces the
ordinary list-like column model:

```text
ColumnWiseTableOfPydanticRecordsModel[
	RecT,
	ColWiseTableModelT,
	ColModelT,
	ColItemT,
	PKT,
]

PST[RecT, PKT]
	inherits ColumnWiseTableOfPydanticRecordsModel[
		RecT,
		<internal table model over PS columns>,
		PS[object],
		object,
		PKT,
	]
```

This is inheritance, not merely semantic reuse. `PST` inherits the column-wise Pydantic-record
parsing, default-column initialization, row iteration, primary-key behavior, and `__add__`/
`__radd__` concatenation machinery of the `CR` base. `PS` supplies the Series-specific column
operations where the base class expects a column model:

1. every Series column is normalized to one positional row axis;
2. all Series columns must have the same length;
3. logical rows are read by position using `.iloc`, never ambiguous Series label indexing;
4. each logical row is validated against `RecT`;
5. coerced values are written back to their Series position;
6. defaulted record fields become newly materialized Series columns of table length;
7. primary-key validation and serialized-key lookup follow the same rules as `CR[RecT, PKT]`.

After validation, coerced values can change a column's type (for example `'10'` to `10`). `PST`
therefore re-applies the dtype normalization (see "Dtypes and missing values") before writing
values back; a validated `None` becomes `pd.NA`.

For example:

```text
PST[SampleRecord, No PK]:
{
	'sample_id': Series(['s1', 's2'], dtype=string),
	'count': Series(['10', <NA>], dtype=string),
}

SampleRecord:
	sample_id: str
	count: int | None = None
	active: bool = True

validated PST content:
{
	'sample_id': Series(['s1', 's2'], dtype=string),
	'count': Series([10, <NA>], dtype=Int64),
	'active': Series([True, True], dtype=boolean),
}
```

`PST` supports row-appending/concatenation because it inherits the column-wise table add
operations. Concatenation of `PS` columns resets to the shared positional row index. Extra-field
and alias handling are inherited from the common Pydantic-record validation base (see "Missing
cells, extra columns, and aliases in record tables"); `PST` must not define a conflicting
Pandas-only interpretation.

## Dataset interoperability

### Structural conversions

```text
RK[CellT, PK] <==> DS[Model[dict[str, CellT]]]
RRK[RecT, PK] <==> DS[Model[RecT]]

C[CellT, PKT] <==> DS[ColModelT]
CR[RecT, PKT] <==> DS[ColModelT]

PST[RecT, PKT] <==> DS[PS]
```

The Dataset target determines whether the corresponding row, record, column, or Series values
are accepted. In the reverse direction, a Dataset whose items fit the table's rows or columns is
validated into the table: the target table checks its own invariants, such as key uniqueness and
`outer_key == serialize(row[primary_key_columns])` for `RK`/`RRK`, equal column lengths for
`C`/`CR`/`PST`, and record validation for `RRK`/`CR`. `PD` and `PDR` are not mapping-root, so
they go through `C`/`CR` (or, in future, `@export_to_type`).

`ItemT` in `DS[ItemT]` stands for any item type accepted by the target Dataset.

For example, keyed rows naturally become Dataset items because their outer mapping already uses
the serialized primary key:

```text
RK[JsonScalar, PrimaryKey['sample_id']]:
{
	's1': {'sample_id': 's1', 'count': 10},
	's2': {'sample_id': 's2', 'count': 20},
}

==>

DS[Model[SampleRecord]]:
{
	's1': Model[SampleRecord](sample_id='s1', count=10),
	's2': Model[SampleRecord](sample_id='s2', count=20),
}
```

By contrast, an ordinary list-root row table has no Dataset item identity until the caller
explicitly selects a primary-key conversion or positional enumeration.

### Explicit enumeration

List-root tables do not automatically become Datasets because position must not silently become
identity. Explicit enumeration remains available:

```text
R[CellT]
	--> EnumeratedListOfTuplesModel
	--> string-keyed mapping
	==> DS[ItemT]

RR[RecT]
	--> EnumeratedListOfTuplesModel
	--> string-keyed mapping
	==> DS[ItemT]
```

## Selection model

The intended selection grammar is:

1. the outermost tuple separates dimensions;
2. table outer-tuple dimensions are ordered `table[row_selector, column_selector]`;
3. a selector nested inside an outer dimension tuple may itself be a tuple, list, or other
   non-string/non-byte iterable selecting multiple elements within that dimension;
4. without an outer dimension tuple, an `int` always selects a row by position, in every table
   family (negative integers count from the end);
5. without an outer dimension tuple, a `str` selects by name in the table's default dimension
   (see below);
6. without an outer dimension tuple, a non-tuple/non-string/non-byte iterable selects multiple
   elements: a list of `int` selects rows, a list of `str` selects names in the default dimension,
   and a list mixing the two is an error; a `slice` selects rows;
7. omitted outer-tuple dimensions imply `:`.

Within an outer tuple, each element addresses its own dimension: in the row dimension an `int` is a
row position and a `str` is a serialized primary key (keyed tables only); in the column dimension
an `int` is a column position and a `str` is a column name.

The model's orientation determines the default dimension for names:

| Model family | Dimension that a `str` selects without an outer tuple |
|---|---|
| `RK`, `RRK` | Rows, by serialized primary key |
| `RP`, `R`, `RR` | Rows have no names, so a bare `str` is an error; use `table[:, 'name']` for columns |
| `C`, `CR`, `PST`, `PD`, `PDR` | Columns, by column name |
| `PS` | Not applicable: a `PS` has no names; an `int` selects a cell by position |

Integers always address rows, so row positions are selected the same way in row-wise and
column-wise tables, and `len(table)` and iteration are row-based in every family (as in the current
column-wise tables). Keyed tables remain mappings, so `keys()` and `items()` expose serialized keys.
A column is selected by position with `table[:, 0]`. Row keys are always `str`, so the key `'1'`
and the position `1` are never confused. Booleans are rejected as selectors until boolean masks are
specified (see "Selection enhancements").

This resolves the earlier ambiguity: the same Python value `('s1', 's2')` has different meaning
depending on whether it is the outer indexing argument or nested inside an outer dimension tuple.

```text
table['s1', 'count']
	outer tuple: row selector 's1', column selector 'count'

table[('s1', 's2'), :]
	outer tuple: select two rows in the first dimension

table[:, ('count', 'active')]
	outer tuple: select two columns in the second dimension
```

Examples:

```text
column_table['count']              # column by name: names select columns in column-wise tables
column_table[0]                    # row 0: an int always selects a row
column_table[['count', 'active']]  # two columns by name
column_table[[0, 1]]               # first two rows
column_table[:, 0]                 # first column by position
column_table[:, ('count', 'active')]  # explicit dimensions: selects two columns

keyed_row_table['s1']              # row by serialized primary key
keyed_row_table[['s1', 's2']]      # two rows by key
keyed_row_table[0]                 # row 0 by position
row_table[0]                       # row 0 (an unkeyed row table has no row names)
row_table[:, 'count']              # complete named column

table[0, 1]                        # cell at row 0, column 1
table[0, :]                        # complete row at position 0
table[:, 'count']                  # complete named column
table[('s1', 's2'), :]             # two keyed rows
table[(0, 1), :]                   # first two positional rows
table[:, ('count', 'active')]      # two named columns
table[('s1', 's2'), ('count', 'active')]  # two-dimensional subset
```

Composite primary keys are serialized strings, avoiding conflict between tuple primary keys and
tuple dimension selectors.

### Selection results

| Selector result | Returns |
|---|---|
| one row and one column | the cell value |
| one row | a row proxy (mapping from column name to cell) |
| one column | the column model (`ColumnModel`, or `PS` in Pandas-backed tables) |
| several rows or columns, or a slice | a table of the same family; keyed tables keep their primary key |

An unknown column name or key raises `KeyError`, and an out-of-range position raises `IndexError`.
`PS[int]` returns a cell, and `PS[slice]` or `PS[list]` returns a `PS`.

### Row and column mutation

Assignment and `del` use the selection grammar:

- `del table[:, 'b']` deletes a whole column (see "Column deletion").
- `del table[i, :]`, `del table[(i, j), :]`, and `del table[a:b, :]` delete rows by position. Keyed
  tables also accept serialized keys: `del table['s1', :]`, and `del keyed_row_table['s1']`.
  Remaining rows keep their order; in keyed DataFrames the primary-key index is rebuilt.
- `table[i, :] = row` replaces a row. Assignment cannot change the shape of the table.
- Rows are inserted with methods, since selection cannot create new positions: `append(row)`,
  `extend(rows)`, and `insert(position, row)`. Rows are mappings from column name to cell. Missing
  columns are padded according to `missing_cells`. For schema-free tables, unknown columns become
  new columns, padded for the existing rows; for record tables, the extra-field policy of `RecT`
  applies.
- For keyed tables, `append(row)` derives the key from the row. `keyed_row_table[key] = row`
  replaces the row with that key, or appends a new row if the key is new; the key must equal the
  serialized key of the row. A duplicate key on `append` is an error.

All mutations are atomic; interactive mode rolls back to the snapshot on failure.

### Tables and Datasets

Tables and Datasets index slightly differently, by design. A Dataset indexes its items, so after
`C <==> DS[ColModelT]` the Dataset's `ds[0]` is the first column, whereas `table[0]` is the first
row. Rows are the common way to address a table, and convenience is a design principle of Omnipy;
the first column of a table is `table[:, 0]`.

Dataset selection adopts the same outer-tuple rule. Omnipy is pre-release software, so this is
applied without a deprecation period: a top-level tuple is no longer accepted as a multi-selector
of Dataset items (`dataset['item_a', 'item_b']` was multi-selection before), and an outer tuple
with more elements than the Dataset has dimensions, currently one, is rejected with an error that
points to the list form. Multi-selection of items uses a non-tuple iterable:

```text
dataset[['item_a', 'item_b']]
```

An explicit one-dimension outer tuple can additionally contain a nested tuple selector:

```text
dataset[('item_a', 'item_b'),]
```

The trailing comma makes this an outer one-dimension tuple whose sole nested tuple selects two
Dataset items. Assignment through `Dataset.__setitem__`, which shares the selector logic, follows
the same rules.

## Conversion system architecture

| Category | Meaning |
|---|---|
| Structural conversion | Source root data matches the target root type. |
| Direct semantic conversion | Declared route that changes orientation, schema, or key semantics. |
| Composed conversion | Deterministic chain of declared/direct routes. |
| Explicit-only conversion | Caller must choose identity, column name, or lossy policy. |

Future conversion registration should support declarations conceptually like:

```text
@convert_from(RowWisePositionalTableModel)
def convert_from_positional_table(
	data: RowWisePositionalTableModel,
) -> Self:
	...
```

Source-side export declarations may later complement target-side imports, especially for
backend-specific DataFrame export.

An explicitly declared direct route is preferred when it preserves schema or key semantics. For
example:

```text
RK[CellT, PK] <-> C[CellT, PK]
```

is preferred over a composition that temporarily drops the primary-key specialization:

```text
RK[CellT, PK] --> R[CellT] --> C[CellT, No PK] --> C[CellT, PK]
```

Composed conversion remains useful where no direct semantic route is needed, for example:

```text
RP[CellT] --> RH[CellT] --> R[CellT] --> C[CellT, No PK]
```

Current `...NoConvertModel` classes remain internal transfer forms. They exist to prevent
circular parsing and are not public conceptual table variants.

## Supported conversion routes

```text
Legend:
  PK  = PrimaryKey[...]
  PKT = PK or No PK
  ==>   = one-way structural conversion when root/item types match
  <==>  = structural conversion in both directions
  -->   = one-way semantic conversion
  <->   = semantic conversion in both directions
  -/->  = unsupported or deferred conversion
  Explicit-only conversions (caller must choose identity, column name, or a lossy policy) have
  no arrow of their own; they are written as chains of the arrows above.

RP[CellT] --> RH[CellT] ==> R[CellT]
RP[CellT] --> RR[RecT]
R[CellT] --> RP[CellT]

R[CellT] <-> RR[RecT]

R[CellT] <-> C[CellT, No PK]
RR[RecT]  <-> CR[RecT,  No PK]

R[CellT] <-> RK[CellT, PK]
RR[RecT]  <-> RRK[RecT,  PK]

C[CellT, No PK] <-> C[CellT, PK]
CR[RecT,  No PK] <-> CR[RecT,  PK]

C[CellT, PKT] <-> CR[RecT, PKT]

RK[CellT, PK] <-> C[CellT, PK]
RRK[RecT,  PK] <-> CR[RecT,  PK]

C[CellT, PKT] <-> PD[CellT, PKT]

CR[RecT, PKT]
	<-> PST[RecT, PKT]
	<-> PDR[RecT, PKT]

PD[CellT, No PK] <-> PD[CellT, PK]
PDR[RecT,  No PK] <-> PDR[RecT,  PK]

PD[CellT, PKT] <-> PDR[RecT, PKT]

RK[CellT, PK] <==> DS[Model[dict[str, CellT]]]
RRK[RecT,  PK] <==> DS[Model[RecT]]

C[CellT, PKT] <==> DS[ColModelT]
CR[RecT,  PKT] <==> DS[ColModelT]

PST[RecT, PKT] <==> DS[PS]

R[CellT]
	--> EnumeratedListOfTuplesModel
	--> string-keyed mapping
	==> DS[ItemT]

RR[RecT]
	--> EnumeratedListOfTuplesModel
	--> string-keyed mapping
	==> DS[ItemT]
```

### Conversion semantics by route family

The route listing above is the authoritative overview of supported paths. This section describes
what each family of routes does to table shape, missing values, schemas, primary keys, and backend
state.

#### Positional parsing and positional export

| Route | Conversion behavior | Preserved | Deliberately changed or lost |
|---|---|---|---|
| `RP[CellT] --> RH[CellT] --> R[CellT]` | Interprets the first positional row as headers. Applies `RH.Params.extra_columns` and `RH.Params.short_rows`. | Data-row order; declared header values; generated extra columns under the permissive policy. | The header row becomes schema rather than a data row. Short rows become sparse missing fields. |
| `RP[CellT] --> RR[RecT]` | Maps each positional row to `RecT` field order and validates it. Short rows must cover all required fields; extra cells of longer rows are passed to Pydantic under generated names, and the extra-field policy of `RecT` decides. | Row order; positional cell order. | Field names are supplied by `RecT`; coercion/defaults/validation apply. |
| `R[CellT] --> RP[CellT]` | Emits row values in the inferred logical column order, with a header row according to `RP.Params.header_row`. | Row order; logical cell values; column names when a header row is emitted. | Without a header row, column names are discarded. Absent cells become default values; trailing absent cells are padded or omitted according to `RP.Params.short_rows` (see "Named rows to positional rows"). |

`RP` itself stays permissive about unequal row lengths. `RH` and `RR` decide how positional width
becomes named/headered/schema-defined table meaning.

#### Row-wise and column-wise reshaping

| Route | Conversion behavior | Missing-cell behavior |
|---|---|---|
| `R[CellT] --> C[CellT, No PK]` | Unions/infer-orders column names and pivots records into columns. | Every column is rectangular; absent row fields are padded with the cell type's default value. Potentially lossy for non-nullable `CellT`; `RejectMissingCells` makes this an error. |
| `C[CellT, No PK] --> R[CellT]` | Materializes positional column cells into named sparse records. | Missing values (`None`; `NaN` for non-nullable float cell types) are omitted from canonical sparse row backing. Other padding values (for example `0`) are retained as ordinary values. |
| `RR[RecT] --> CR[RecT, No PK]` | Converts validated records into columns under the record schema. | Record defaults and requiredness govern column materialization. |
| `CR[RecT, No PK] --> RR[RecT]` | Materializes/validates each logical row as a Pydantic record. | Record fields/defaults define the row result. |

The `R <-> C` route is a physical-orientation conversion. It preserves logical row order and
every column with at least one non-missing cell (see "Columns without stored cells"), but changes
raw representation between sparse records and dense columns. Padding is potentially lossy,
depending on `CellT` (see "Missing-cell padding").

#### Cell-table and Pydantic-record conversion

| Route | Conversion behavior |
|---|---|
| `R[CellT] <-> RR[RecT]` | Forward validates/coerces each row and stores Pydantic records. Reverse exports ordinary row values and drops record behavior. |
| `RK[CellT, PK] <-> RRK[RecT, PK]` | Same validation/export behavior while preserving the keyed outer mapping and primary-key specialization. |
| `C[CellT, PKT] <-> CR[RecT, PKT]` | Forward validates every logical row, coerces cell values, and materializes defaulted columns. Reverse drops record-schema behavior while retaining columns and key configuration. |
| `PD[CellT, PKT] <-> PDR[RecT, PKT]` | Forward validates through temporary `PST` content and reconstructs a DataFrame. Reverse drops record-schema behavior. |

Record conversion is the boundary where Pydantic field coercion, aliases, defaults, requiredness,
and extra-field policy become active.

#### Primary-key specialization and orientation

| Route | Conversion behavior | Primary-key effect |
|---|---|---|
| `R[CellT] <-> RK[CellT, PK]` | Converts list-root sparse records to/from keyed outer mappings. | Forward derives serialized outer keys from visible key fields and validates uniqueness. Reverse drops keyed mapping behavior but retains visible key fields. |
| `RR[RecT] <-> RRK[RecT, PK]` | Equivalent keying/unkeying operation for stored Pydantic records. | Same key derivation and validation after record coercion. |
| `C[CellT, No PK] <-> C[CellT, PK]` | Keeps column root content unchanged. | Forward validates key columns and uniqueness; reverse drops key semantics. |
| `CR[RecT, No PK] <-> CR[RecT, PK]` | Keeps record-validated column root content unchanged. | Key fields must exist in `RecT`; uniqueness is validated after coercion. |
| `RK[CellT, PK] <-> C[CellT, PK]` | Direct keyed row/column reshaping. | Preserves `PK`, visible key fields, key values, and row order. |
| `RRK[RecT, PK] <-> CR[RecT, PK]` | Direct keyed Pydantic-record row/column reshaping. | Preserves record schema, `PK`, visible key fields, and row order. |

Direct keyed orientation routes are preferred over paths that temporarily remove `PK` and then
re-add it.

#### Pandas and Series backend adaptation

| Route | Conversion behavior | Index/column behavior |
|---|---|---|
| `C[CellT, PKT] <-> PD[CellT, PKT]` | Converts ordinary columns to/from DataFrame columns, normalizing dtypes and missing values (see "Dtypes and missing values"). | `C --> PD` gives a `RangeIndex` when unkeyed. `PD --> C` materializes a non-default unkeyed index as columns (see "Index of unkeyed DataFrames"). Keyed DataFrames rebuild/validate the primary-key index from visible key columns. |
| `CR[RecT, PKT] <-> PST[RecT, PKT]` | Substitutes `PS` Series columns into the inherited `CR` machinery. | `PST` normalizes Series to one positional row axis and preserves record-validation semantics. |
| `PST[RecT, PKT] <-> PDR[RecT, PKT]` | Adapts between mapping-of-Series and DataFrame roots. | Unkeyed `PDR` restores the source DataFrame index after validation; keyed `PDR` rebuilds a unique primary-key index. |
| `PD[CellT, No PK] <-> PD[CellT, PK]` | Rebuilds the DataFrame index; columns are unchanged. | Adding a key materializes a non-default index as columns, then sets a unique, unnamed key index from the visible key columns. Removing a key resets to a `RangeIndex`. |
| `PDR[RecT, No PK] <-> PDR[RecT, PK]` | Rebuilds the DataFrame index; validated columns are unchanged. | Same index behavior as for `PD`. |

`PST` is a Series-column implementation of Pydantic-record column-wise validation, not a
general-purpose ordinary cell table.

#### Dataset materialization

| Route | Conversion behavior |
|---|---|
| `RK[CellT, PK] <==> DS[Model[dict[str, CellT]]]` | Outer keyed-row mapping becomes Dataset item mapping; serialized primary keys become Dataset keys. Reverse: items become rows; key invariants are validated. |
| `RRK[RecT, PK] <==> DS[Model[RecT]]` | Same mapping behavior with validated Pydantic records as items. |
| `C[CellT, PKT] <==> DS[ColModelT]` | Outer column mapping becomes Dataset item mapping. Dataset receives independent columns and does not retain table-level key behavior. Reverse: items become columns; equal lengths are validated. |
| `CR[RecT, PKT] <==> DS[ColModelT]` | Same outer column mapping after record-aware validation. |
| `PST[RecT, PKT] <==> DS[PS]` | Outer `PS` column mapping becomes Dataset item mapping. Reverse: `PS` items become Series columns. |
| `R[CellT]` or `RR[RecT]` via enumeration | Explicitly turns list positions into named Dataset identities through `EnumeratedListOfTuplesModel`, then a string-keyed mapping. |

List-root tables never acquire Dataset identities automatically.

## Deferred or intentionally unsupported direct routes

```text
RP[CellT] -/-> DS[ItemT]
R[CellT]  -/-> DS[ItemT]
RR[RecT]  -/-> DS[ItemT]
```

Reason: list position must not silently become Dataset identity. Use a primary-key route or
explicit enumeration.

```text
PD[CellT, PKT] -/-> R[CellT]
PDR[RecT, PKT] -/-> RR[RecT]
PD[CellT, PKT] -/-> RK[CellT, PK]
PDR[RecT, PKT] -/-> RRK[RecT, PK]
```

Reason: exporting from a DataFrame requires source-side export declarations (a future
`@export_to_type` functionality), which are needed to distinguish output to column-wise and
row-wise table types. The index and missing-value rules for such exports are defined (see "Index
of unkeyed DataFrames" and "Dtypes and missing values").

## Implementation TODOs

### Core model work

- Rename current positional `RowWiseTableModel` to `RowWisePositionalTableModel`.
- Rename current named `RowWiseTableWithColNamesModel` to `RowWiseTableModel`.
- Replace the misleading `ColumnWiseTableWithColNamesAndIndexModel` concept with explicit
  row-wise primary-keyed table models.
- Add generic `CellT` support to positional and ordinary row-wise models.
- Add an `extra_columns` `Params` field to header-conversion models, defaulting to
  `AddExtraColumns`.
- Add a `short_rows` `Params` field to header-conversion models, defaulting to
  `AcceptMissingColumns`.
- Implement generated-column discovery for permissive header conversion without discarding long
  positional rows.
- Bind `CsvTableModel` and `TsvTableModel` to shared header parameters with strict
  `RejectExtraColumns` and `RejectShortRows` defaults.
- Add concrete headerless CSV/TSV parser models that return `RP[CellT]` positional output.
- Add a `header_row` `Params` field to `RP`, defaulting to `HeaderRowIfSupported`, for
  `R --> RP` export.
- Add a `short_rows` `Params` field to `RP`, defaulting to `PadShortRows`, for `R --> RP` export.
- Validate the `RH` header row as `str` values without coercion.
- Implement explicit row-wise Pydantic-record and keyed-record model families.
- Pass extra cells of long positional rows to Pydantic record validation under generated names
  shared with `RH`, leaving the outcome to the extra-field policy of `RecT`.
- Restrict the required-before-optional field-order check in
  `PydanticRecordModelMetaclass.header_info` to positional input.
- Refactor `IteratingPydanticRecordsModel` into the explicit column-wise Pydantic-record family.
- Leave missing cells out of rows before record validation in all record families, so that field
  defaults apply and missing required fields are rejected (the current column-wise code passes
  explicit `None`).
- Log a warning when a record type with a field that accepts `None` but has a non-`None` default
  is loaded for a table.
- Apply the extra-field policy of `RecT` in the column-wise record families (the current code keeps
  undeclared columns regardless of the policy).
- Name record-table columns by field alias where defined, and write values back under the alias.
- Preserve implementation-level column generic parameters where required.
- Rename `ColumnWiseTableWithColNamesModel` and its `Json*ColumnWiseTableWithColNamesModel`
  variants to the `ColumnWiseTableModel` naming.
- Decide how `TableOfPydanticRecordsModel` and `CsvTableOfPydanticRecordsModel`, which parse text
  into `list[PydanticRecordModel[RecT]]`, fit the `RR` naming.

### Row access and mutation

- Add a row proxy for row-wise table access.
- Make row proxies logically rectangular over sparse backing data.
- Add `IterRow.__setitem__` with parent write-through behavior.
- Implement atomic automatic re-keying for primary-key cell mutation, rebuilding the outer mapping
  in its original order to preserve row position.
- Decide whether public iteration keeps reusable `IterRow` or yields fixed row proxies.
- Invalidate/recompute derived primary-key lookup after key-affecting mutation.

### Sparse/schema behavior

- Implement sparse column-order inference with adjacent constraints and first-seen fallback.
- Implement schema-aware column deletion: fail atomically for fields declared in `RecT`; remove
  undeclared extra fields.
- Ensure `to_data()` and `to_json()` preserve sparse row backing data.
- Treat declared primary-key fields as always-known columns in keyed row-wise models.
- Extract default-value logic from `ColumnModel.default_value()` into a shared cell-type helper
  used by column models and by `R`/`RK` logical views.
- Fix `ColumnModel.default_value()` so that every non-nullable float cell type defaults to `NaN`
  (plain `float` currently returns `0.0`).
- Make `R`/`RK` logical views return the cell type's default value for absent cells in known
  columns.
- Add a `missing_cells` `Params` field to column-wise cell models, defaulting to
  `PadMissingCells`.
- Implement `RejectMissingCells` for conversion into column-wise cell models and for column-wise
  concatenation.
- Validate equal physical column lengths for `C[CellT, PKT]` and `CR[RecT, PKT]`.
- Validate shared positional Series length for `PST[RecT, PKT]`.

### JSON interoperability

- Make `to_json()` output strict JSON; never emit `NaN`, `Infinity`, or `-Infinity` tokens.
- Parse float `NaN` as `None` in JSON-typed cells, preferably through a custom Pydantic float type
  in the `JsonScalar` type alias; adapt cell-type introspection such as
  `ColumnModel.default_value()` accordingly.
- If the custom type proves impractical, implement the `NaN` rule explicitly in every table family.
- For non-nullable float cell types, serialize `NaN` as `None`/`null` in `to_data()`/`to_json()`
  and parse `None` input as `NaN`.
- Omit `NaN` cells of non-nullable float cell types from canonical sparse row backing.
- Reject `Infinity` and `-Infinity` cell values.

### Primary keys

- Implement deterministic key serialization: stringify the result of `to_data()` if available,
  else use `str()`; percent-escape components of composite keys only.
- Enforce key uniqueness on serialized key strings.
- Reject unstable default `object.__str__()` key components.
- Validate compatibility between `PK` fields and `RecT` fields.
- Rebuild the keyed column lookup once per operation under Pydantic v1.

### Pandas

- Split current `PandasModel` into Series and DataFrame model families.
- Implement Pydantic DataFrame validation through temporary `PST` content.
- Implement `PS[CellT]` as a Series-backed column model: positional reads and writes, `filled()`,
  `default_value()` returning `pd.NA`, and concatenation resetting the index to row positions.
- Implement `PST` as a subclass of the future `CR` base (`ColumnWiseTableOfPydanticRecordsModel`
  with a `PKT` parameter) using `PS[object]` columns, inheriting validation and column-wise
  concatenation rather than duplicating either algorithm. Its primary-key behavior depends on
  the `CR` base getting primary-key support first.
- Re-apply dtype normalization to `PST` columns after record validation.
- Rewrite `_init_col` in `IteratingPydanticRecordsModel` to use the column model's `filled()` and
  `default_value()` (existing TODO in `models.py`); it currently builds plain lists with
  `[default] * length`, which cannot produce Series.
- Make the changed-value check in `_validate_over_all_rows` handle omitted keys and `pd.NA`; the
  comparison `row_dict[key] != validated_val` raises `TypeError` for `pd.NA`.
- Normalize `PST` Series indexes to positional order.
- Validate shared Series length and use `.iloc` for all `PST` row access.
- Reconstruct validated `PDR` DataFrames from `PST` columns, preserving an unkeyed source index
  or rebuilding a keyed index as required.
- Implement DataFrame primary-key index rebuilding with `drop=False`, `verify_integrity=True`, and
  unnamed index levels; reset to a `RangeIndex` when removing a key.
- Implement cell/record conversion between column-wise and Pandas models.
- Normalize all Pandas-backed content to nullable extension dtypes on every input path, inferred
  per column, never converting float columns to integer dtypes.
- Map `None`, `NaN`, and `NaT` to `pd.NA` on input, and `pd.NA` to the target cell type's default
  value on output, including `to_data()`/`to_json()`; the current `PandasModel.to_data()` only
  replaces `pd.NA` and lets NumPy `NaN` through.
- Materialize non-default unkeyed indexes as columns, like `reset_index()`, on output to
  non-Pandas families.
- Make `PD`/`PDR` `to_data()` and `to_json()` both output the column-wise mapping (fixes the
  current `to_data()`/`to_json()` inconsistency).

### Conversion and selection infrastructure

- Implement `@convert_from(...)` declarations.
- Add conversion-path discovery over declared conversion routes.
- Define path costs, ambiguity errors, cycle detection, and a bounded maximum path length.
- Keep no-convert transfer wrappers internal.
- Implement tuple-as-dimensions selection.
- Align Dataset tuple selection behavior with the table selection grammar: reject a top-level
  tuple as a multi-selector and outer tuples longer than the number of Dataset dimensions in
  `select_keys()` (`src/omnipy/data/_selector.py`), with an error pointing to the list form, for
  both `Dataset.__getitem__` and `Dataset.__setitem__`. Update the `select_keys()` error message,
  which says "positive integer" although negative indices work.
- Implement list/iterable same-dimension selection.
- Keep `int` selection, `len()`, and iteration row-based in all table families, including keyed
  row tables (which iterate rows, not keys); reject `bool` selectors until boolean masks are
  specified.
- Implement the selection results: cell, row proxy, column model, and same-family subset table
  (keyed subsets keep their primary key).
- Implement row deletion, row replacement, and row insertion (`append`, `extend`, `insert`, and
  keyed assignment), atomically, with primary-key index rebuilding for keyed DataFrames.
- Implement the structural `Dataset --> table` directions of the `<==>` routes, validated by the
  target table's own invariants.

## Behavior changes relative to the current implementation

The following changes alter behavior of the current code and should be listed in release notes:

- `RH`: extra cells of long rows are kept as generated columns (silently dropped today), and
  absent cells stay absent (padded with `None` today).
- `CsvTableModel`/`TsvTableModel`: strict by default, so ragged files accepted today are rejected.
- `ColumnModel.default_value()`: plain `float` defaults to `NaN` (`0.0` today), and the shared
  helper is also used by `R`/`RK`.
- JSON: `NaN` is parsed as `None`, `Infinity` is rejected, and `to_json()` emits strict JSON.
- Pandas: content is normalized to nullable dtypes on every input path; `to_data()` and
  `to_json()` both output the column-wise mapping (they differ today).
- Record tables: missing cells are omitted before validation (explicit `None` today), the
  extra-field policy of `RecT` applies to column-wise families (undeclared columns are kept
  today), and columns use aliases.
- Column-wise tables: the existing behavior (`str` selects a column, `int` selects a row, and
  `len()` and iteration are row-based) is preserved. The tuple, list, and slice selection, row
  mutation, and positional column access `table[:, 0]` are additions.
- Dataset: a top-level tuple is no longer a multi-selector.
- Renames of the positional, named row-wise, and column-wise table classes (see "Core model
  work").

## Future design issues

These are explicitly deferred questions rather than committed implementation tasks.

### Conversion declaration and path system

- Decide source-side export declaration syntax (`@export_to_type`) and how it complements
  `@convert_from(...)`.
- Decide whether ordinary `.to(Target)` automatically attempts composed conversion paths or only
  direct conversion plus structural compatibility.
- Determine conversion path ranking when several valid routes exist, especially where one route
  is lossy.
- Define whether non-lossy key/schema-preserving direct routes always outrank composed routes.

### Pandas export and index behavior

- Design a factory for deriving `PD[..., PK]` specialization from an existing unique named index
  or MultiIndex.
- Define policy for unnamed, duplicate, or non-string index-level names.
- Extend Pandas dtype mappings beyond the basic nullable dtypes, for example to datetime and
  categorical columns.
- Define the supported interoperable subset of custom Pydantic field behavior if needed.

### Schema representation and serialization

- Investigate use of Pydantic v2 metadata/private fields for richer table schema state.
- Decide whether future Omnipy-specific lossless serialization should include type, schema, and
  primary-key metadata alongside ordinary JSON data.
- Decide how optional explicit schema changes should work, including controlled field deletion
  and clearing the values of optional fields (for example `table.reset_column(...)`).
- Consider future lossless normalization for duplicate/non-string external column labels.
- Encode non-finite floats as JSON strings (for example `'Infinity'`, `'-Infinity'`) and parse
  them back in float-typed cells, instead of rejecting them. Consequences to resolve include
  ambiguity with genuine strings in cells whose type includes both `str` and `float` (for example
  `JsonScalar`), and the type change for consumers reading plain JSON.
- Consider the consequences of `NaN` for snapshot change detection of Pandas-backed content, for
  example by using `NaN`-aware comparison such as `DataFrame.equals()`/`Series.equals()`, or by
  the dirty-flag approach noted in the TODO in
  `Model._prepare_reset_solution_take_snapshot_if_needed()` (`src/omnipy/data/model.py`).

### Additional backends

- Design NumPy positional table models and dtype integration.
- Define future Polars, Arrow, Parquet, Excel, BioNumPy, NetCDF, and SQL-result integrations.
- Determine which backend properties are preserved, normalized, or rejected for each adapter.

### Selection enhancements

- Specify boolean-mask selection. Boolean selectors must be identified before integer selectors
  because `bool` subclasses `int`.
- Extend the shared selector model to higher-dimensional hierarchical content.

### Performance

- Benchmark recomputed primary-key lookup under Pydantic v1.
- Revisit Pydantic v2 private lookup caching only if lookup workloads justify it.
- Revisit weighted sparse-column ordering only if unweighted stable ordering proves unintuitive on
  real data.
