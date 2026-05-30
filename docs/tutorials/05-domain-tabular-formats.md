# Tutorial 5: Domain tabular formats

--8<-- "_includes/maturity_labels.md"

> [!NOTE]
> **Status: Now**
>
> Row-based parsing is **Now**. Column-based parsing support is **Preview**.

This tutorial shows BED/GFF-style row parsing using typed model specs.

## Step 1: Parse BED-like rows

```pycon exec="1" source="console"
>>> from omnipy import TsvTableModel
>>> bed = "chrom\tstart\tend\tname\nchr1\t10\t20\tgeneA\nchr2\t5\t9\tgeneB\n"
>>> rows = TsvTableModel(bed)
>>> rows.to_data()
```

## Step 2: Define row model spec

```pycon exec="1" source="console"
>>> from omnipy.util import pydantic as pyd
>>> class BedRow(pyd.BaseModel):
...     chrom: str
...     start: int
...     end: int
...     name: str | None = None
```

## Step 3: Parse into typed records

```pycon exec="1" source="console"
>>> from omnipy import Model, TsvTableModel
>>> from omnipy.util import pydantic as pyd
>>> class BedRow(pyd.BaseModel):
...     chrom: str
...     start: int
...     end: int
...     name: str | None = None
>>> rows = TsvTableModel("chrom\tstart\tend\tname\nchr1\t10\t20\tgeneA\n")
>>> typed_rows = Model[list[BedRow]](rows.to_data())
>>> typed_rows.to_data()
```

## Optional: convert for table tooling

```pycon exec="1" source="console"
>>> from omnipy import Model, RowWiseTableWithColNamesModel, PandasModel, TsvTableModel
>>> from omnipy.util import pydantic as pyd
>>> class BedRow(pyd.BaseModel):
...     chrom: str
...     start: int
...     end: int
...     name: str | None = None
>>> rows = TsvTableModel("chrom\tstart\tend\tname\nchr1\t10\t20\tgeneA\n")
>>> typed_rows = Model[list[BedRow]](rows.to_data())
>>> RowWiseTableWithColNamesModel(typed_rows.to_data()).to(PandasModel).to_data()
```
