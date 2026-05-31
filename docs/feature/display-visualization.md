# Display & visualization

--8<-- "_includes/maturity_labels.md"

!!! note
    **Status: Now**

## 1) What it solves

Typed data is only useful if you can inspect it quickly while iterating.

## 2) The idea

Omnipy models and datasets expose a shared display surface: `peek()`, `full()`, `browse()`, and
`_docs()`.

## 3) Example

```pycon exec="1" source="console"
>>> from omnipy import Model
>>> m = Model[dict[str, list[int]]]({'a': [1, 2], 'b': [3, 4]})
>>> m.to_data()
```

## 4) Output / display

```pycon exec="1" source="console"
>>> from omnipy import Model
>>> m = Model[dict[str, list[int]]]({'a': [1, 2], 'b': [3, 4]})
>>> print(m._docs())
```

## 5) When to use / when not

Use in notebooks, terminal debugging, and docs examples.

Avoid `browse()` in headless environments.

## 6) Gotchas

- Display output depends on UI environment (terminal vs notebook).
- Keep runnable docs examples on `_docs()`/`to_data()` for deterministic output.

## 7) Links

- How-to: [Display & inspection](../howto/models/display-inspection.md)
- Feature: [Continuous validation](continuous-validation.md)
