# ChainX recipes

--8<-- "_includes/maturity_labels.md"

!!! note
    **Status: Now**

## Recipe: parse tabular text to rows

```pycon exec="1" source="console"
>>> from omnipy import TsvTableModel
>>> tsv = "a\tb\n1\t2\n3\t4\n"
>>> TsvTableModel(tsv).to_data()
```

## Recipe: follow with typed row conversion

```pycon exec="1" source="console"
>>> from omnipy.util import pydantic as pyd
>>> from omnipy import Model, TsvTableModel
>>> class Row(pyd.BaseModel):
...     a: int
...     b: int
>>> Model[list[Row]](TsvTableModel("a\tb\n1\t2\n").to_data()).to_data()
```

## When to switch to compute flows

If transformation requires branching/joins, use dataflow Tasks/Flows instead of linear model chains.
