# Declarative conversions

--8<-- "_includes/maturity_labels.md"

!!! note
    **Status: Now**

## 1) What it solves

Teams accumulate ad-hoc conversion glue between JSON-like, row-like, and table-like
representations.

## 2) The idea

Use `.to(TargetType)` as an explicit conversion boundary. It keeps conversion intent visible and
typed.

## 3) Example

```pycon exec="1" source="console"
>>> import omnipy as om
>>> ds = om.JsonListOfDictsDataset({'rows': [{'id': 'a', 'value': '1'}, {'id': 'b', 'value': 2}]})
>>> ds_pd = ds.to(om.PandasDataset)
>>> ds_pd.json()
```

## 4) Output / display

```pycon exec="1" result="console" html="true"
>>> import omnipy as om
>>> ds = om.JsonListOfDictsDataset({'rows': [{'id': 'a', 'value': '1'}, {'id': 'b', 'value': 2}]})
>>> print(ds.to(om.PandasDataset)._docs())
```

## 5) When to use / when not

Use it at representation boundaries and in reusable transformation code.

Avoid forcing `.to()` when no target parser exists yet; add a parse/transform step first.

## 6) Gotchas

- Convertibility depends on whether the target can parse the source shape.
- Check `.json()` before and after conversion when debugging.

## 7) Links

- How-to: [Conversions with `.to()`](../howto/models/conversions-to.md)
- Feature: [Dataset batch hierarchies](dataset-batch-hierarchies.md)
