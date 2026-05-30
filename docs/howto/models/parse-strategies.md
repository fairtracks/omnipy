# Parse strategies

--8<-- "_includes/maturity_labels.md"

> [!NOTE]
> **Status: Now**

## Parse, don't validate in practice

### Let built-in coercion handle straightforward cases

```pycon exec="1" source="console"
>>> from omnipy import Model
>>> Model[list[int]](['1', 2, 3.0]).to_data()
```

### Add custom normalization with `_parse_data`

```pycon exec="1" source="console"
>>> from omnipy import Model
>>> class IntListFromAnything(Model[list[int]]):
...     @classmethod
...     def _parse_data(cls, data):
...         if isinstance(data, tuple):
...             data = list(data)
...         return data
>>> IntListFromAnything(('1', 2, 3.0)).to_data()
```

## Guidance

- Normalize obvious ambiguities (whitespace, separators).
- Do not silently guess semantics you cannot justify.

## Links

- Learn: [Parse don't validate](../../parse_dont_validate.md)
- How-to: [Define models](define-models.md)
