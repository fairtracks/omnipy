# Conversions with `.to()`

--8<-- "_includes/maturity_labels.md"

> [!NOTE]
> **Status: Now**

## Convert dataset types

```pycon exec="1" source="console"
>>> from omnipy import JsonListOfDictsDataset, PandasDataset
>>> records = JsonListOfDictsDataset({'rows': [{'id': 'a', 'value': '1'}, {'id': 'b', 'value': 2}]})
>>> records.to(PandasDataset).to_data()
```

## Convert model types

```pycon exec="1" source="console"
>>> from omnipy import JsonListOfDictsModel, PandasModel
>>> table = JsonListOfDictsModel([{'id': 'a', 'x': 1}, {'id': 'b', 'x': 3}])
>>> table.to(PandasModel).to_data()
```

## Chaining conversions

Prefer explicit checkpoints:

1. `.to_data()` to inspect shape
2. `.to(Target)` to convert
3. `.to_data()` again to confirm

## Links

- Feature: [Declarative conversions](../../feature/declarative-conversions.md)
