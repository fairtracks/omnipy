# Continuous validation

--8<-- "_includes/maturity_labels.md"

> [!NOTE]
> **Status: Now**

## 1) What it solves

You parse data once, then keep working with it. Without continuous checks, later edits can silently
break assumptions.

## 2) The idea

`Model[T]` parses input into `T` and continues enforcing that type as you mutate the object.
Omnipy models also mimic the behavior of the wrapped type (for example, list methods).

## 3) Example

```pycon exec="1" source="console"
>>> from omnipy import Model
>>> vals = Model[list[int]]((1, '2', 3.0))
>>> vals.append('4')
>>> vals.to_data()
```

## 4) Output / display

```pycon exec="1" source="console"
>>> from omnipy import Model
>>> vals = Model[list[int]]((1, '2', 3.0))
>>> print(vals._docs())
```

## 5) When to use / when not

Use it when data stays mutable across several steps (notebooks, scripts, small pipelines).

Skip it when you parse once and immediately serialize out without in-memory edits.

## 6) Gotchas

- Continuous validation is independent from rollback behavior.
- Rollback safety is controlled by `runtime.config.data.model.interactive`.

## 7) Links

- Feature: [Snapshots & rollbacks](snapshots-rollbacks.md)
- How-to: [Define models](../howto/models/define-models.md)
