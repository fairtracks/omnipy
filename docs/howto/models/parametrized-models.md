# Parametrized models

--8<-- "_includes/maturity_labels.md"

!!! note
    **Status: Now**

## Common pattern: `Dataset[Model[T]]`

```pycon exec="1" source="console"
>>> from omnipy import Dataset, Model
>>> ds = Dataset[Model[int]]({'a': '1', 'b': 2.0})
>>> ds.json()
```

## Reuse shape, vary inner type

```pycon exec="1" source="console"
>>> import omnipy as om
>>> om.Model[list[str]]([1, '2', 3])
```

## Current limitations

- Deeply nested generics can be hard to debug from traceback alone.
- Prefer introducing named subclasses at major boundaries.
