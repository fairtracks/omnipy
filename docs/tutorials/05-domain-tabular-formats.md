# Tutorial 5: Domain tabular formats

--8<-- "_includes/maturity_labels.md"

!!! note
    **Status: Now**

    Row-based parsing is **Now**. Column-based parsing support is **Preview**.

This tutorial shows BED/GFF-style row parsing using typed model specs.

## Step 1: Parse BED-like rows

```pycon exec="1" source="console"
>>> import omnipy as om
>>> bed = "chrom\tstart\tend\tname\nchr1\t10\t20\tgeneA\nchr2\t5\t9\tgeneB\n"
>>> rows = om.TsvTableModel(bed)
>>> rows
```

## Step 2: Define row model spec

```pycon exec="1" source="console"
>>> import pydantic as pyd
>>> class BedRow(pyd.v1.BaseModel):
...     chrom: str
...     start: int
...     end: int
...     name: str | None = None
```

## Step 3: Parse into typed records

```pycon exec="1" source="console"
>>> import omnipy as om
>>> import pydantic as pyd
>>> class BedRow(pyd.v1.BaseModel):
...     chrom: str
...     start: int
...     end: int
...     name: str | None = None
>>> rows = om.TsvTableModel("chrom\tstart\tend\tname\nchr1\t10\t20\tgeneA\n")
>>> typed_rows = om.Model[list[BedRow]](rows)
>>> typed_rows
```

## Optional: convert for table tooling

```pycon exec="1" source="console"
>>> import omnipy as om
>>> import pydantic as pyd
>>> class BedRow(pyd.v1.BaseModel):
...     chrom: str
...     start: int
...     end: int
...     name: str | None = None
>>> rows = om.TsvTableModel("chrom\tstart\tend\tname\nchr1\t10\t20\tgeneA\n")
>>> typed_rows = om.Model[list[BedRow]](rows)
>>> om.RowWiseTableWithColNamesModel(typed_rows).to(om.PandasModel)
```
