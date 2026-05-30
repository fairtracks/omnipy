# Domain format parsing guide

--8<-- "_includes/maturity_labels.md"

> [!NOTE]
> **Status: Now**

Model-based tabular parsing for domain formats follows a stable three-step pattern.

## 1) Parse rows from text

```pycon exec="1" source="console"
>>> from omnipy import TsvTableModel
>>> text = "a\tb\n1\t2\n"
>>> TsvTableModel(text).to_data()
```

## 2) Apply typed row spec

```pycon exec="1" source="console"
>>> from omnipy import Model, TsvTableModel
>>> from omnipy.util import pydantic as pyd
>>> class Row(pyd.BaseModel):
...     a: int
...     b: int
>>> Model[list[Row]](TsvTableModel("a\tb\n1\t2\n").to_data()).to_data()
```

## 3) Convert to downstream representation

For table workflows, convert parsed records to table/pandas-oriented structures as needed.
