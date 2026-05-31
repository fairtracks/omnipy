# Domain format parsing guide

--8<-- "_includes/maturity_labels.md"

!!! note
    **Status: Now**

Model-based tabular parsing for domain formats follows a stable three-step pattern.

## 1) Parse rows from text

```pycon exec="1" source="console"
>>> import omnipy as om
>>> text = "a\tb\n1\t2\n"
>>> om.TsvTableModel(text).content
```

## 2) Apply typed row spec

```pycon exec="1" source="console"
>>> import omnipy as om
>>> import pydantic as pyd
>>> class Row(pyd.v1.BaseModel):
...     a: int
...     b: int
>>> om.Model[list[Row]](om.TsvTableModel("a\tb\n1\t2\n").content).content
```

## 3) Convert to downstream representation

For table workflows, convert parsed records to table/pandas-oriented structures as needed.
