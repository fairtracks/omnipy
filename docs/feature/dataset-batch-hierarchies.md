# Dataset batch hierarchies

--8<-- "_includes/maturity_labels.md"

> [!NOTE]
> **Status: Now**

## 1) What it solves

Batch processing often devolves into nested loops with weak typing and unclear structure.

## 2) The idea

`Dataset[...]` gives keyed batch semantics, and datasets can nest to represent hierarchy.

## 3) Example

```pycon exec="1" source="console"
>>> from omnipy import Dataset, Model
>>> Inner = Dataset[Model[int]]
>>> Outer = Dataset[Inner]
>>> grouped = Outer({'group1': {'a': '1', 'b': 2}, 'group2': {'x': 10}})
>>> grouped.to_data()
```

## 4) Output / display

```pycon exec="1" source="console"
>>> from omnipy import Dataset, Model
>>> ds = Dataset[Model[int]]({'a': '1', 'b': 2.0})
>>> print(ds._docs())
```

## 5) When to use / when not

Use it for record sets, grouped records, file collections, or keyed intermediate artifacts.

Skip it when you truly only process one scalar/record and no grouping is needed.

## 6) Gotchas

- Define stable key semantics early (sample id, filename, partition key, etc.).
- Very deep nesting usually means you need a clearer boundary between phases.

## 7) Links

- How-to: [Mapping over datasets](../howto/dataflows/mapping-over-datasets.md)
- How-to: [Parametrized models](../howto/models/parametrized-models.md)
