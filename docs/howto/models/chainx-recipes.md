# ChainX recipes

--8<-- "_includes/maturity_labels.md"

!!! note
    **Status: Now**

## Recipe: parse tabular text to rows

```pycon exec="1" source="console"
>>> import omnipy as om
>>> tsv = "a\tb\n1\t2\n3\t4\n"
>>> om.TsvTableModel(tsv).content
```

## Recipe: follow with typed row conversion

```pycon exec="1" source="console"
>>> import omnipy as om
>>> import pydantic as pyd
>>> class Row(pyd.v1.BaseModel):
...     a: int
...     b: int
>>> om.Model[list[Row]](om.TsvTableModel("a\tb\n1\t2\n").content).content
```

## When to switch to compute flows

If transformation requires branching/joins, use dataflow Tasks/Flows instead of linear model chains.
