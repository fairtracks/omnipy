# Define models

--8<-- "_includes/maturity_labels.md"

!!! note
    **Status: Now**

## Quick patterns

### Pattern 1: `Model[T]` directly

```pycon exec="1" source="console"
>>> import omnipy as om
>>> om.Model[list[int]]((1, '2', 3.0))
```

### Pattern 2: subclass for reusable names

```pycon exec="1" source="console"
>>> import omnipy as om
>>> class IntList(om.Model[list[int]]):
...     ...
>>> IntList(['1', 2, 3.0])
```

### Pattern 3: nested type parameters

```pycon exec="1" source="console"
>>> import omnipy as om
>>> om.Model[dict[str, list[int]]]({'a': [1, '2'], 'b': [3.0]})
```

## Links

- How-to: [Parse strategies](parse-strategies.md)
- How-to: [Parametrized models](parametrized-models.md)
