# Parse strategies

--8<-- "_includes/maturity_labels.md"

!!! note
    **Status: Now**

## Parse, don't validate in practice

### Let built-in coercion handle straightforward cases

```pycon exec="1" source="console"
>>> import omnipy as om
>>> om.Model[list[int]](['1', 2, 3.0])
```

### Add custom normalization with `_parse_data`

```pycon exec="1" source="console"
>>> import omnipy as om
>>> class IntListFromAnything(om.Model[list[int]]):
...     @classmethod
...     def _parse_data(cls, data):
...         if isinstance(data, tuple):
...             data = list(data)
...         return data
>>> IntListFromAnything(('1', 2, 3.0))
```

## Guidance

- Normalize obvious ambiguities (whitespace, separators).
- Do not silently guess semantics you cannot justify.

## Links

- Learn: [Parse don't validate](../../parse_dont_validate.md)
- How-to: [Define models](define-models.md)
