# Conversions with `.to()`

--8<-- "_includes/maturity_labels.md"

!!! note
    **Status: Now**

## Convert dataset types

```pycon exec="1" source="console"
>>> import omnipy as om
>>> records = om.JsonListOfDictsDataset({'rows': [{'id': 'a', 'value': '1'}, {'id': 'b', 'value': 2}]})
>>> records.to(om.PandasDataset).json()
```

## Convert model types

```pycon exec="1" source="console"
>>> import omnipy as om
>>> table = om.JsonListOfDictsModel([{'id': 'a', 'x': 1}, {'id': 'b', 'x': 3}])
>>> table.to(om.PandasModel).content
```

## Chaining conversions

Prefer explicit checkpoints:

1. `.json()` to inspect shape
2. `.to(Target)` to convert
3. `.json()` again to confirm

## Links

- Feature: [Declarative conversions](../../feature/declarative-conversions.md)
