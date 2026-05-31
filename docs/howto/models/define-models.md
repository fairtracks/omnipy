# Define models

--8<-- "_includes/maturity_labels.md"

!!! note
    **Status: Now**

## Quick patterns

### Pattern 1: `Model[T]` directly

```pycon exec="1" source="console"
>>> from omnipy import Model
>>> Model[list[int]]((1, '2', 3.0)).to_data()
```

### Pattern 2: subclass for reusable names

```pycon exec="1" source="console"
>>> from omnipy import Model
>>> class IntList(Model[list[int]]):
...     ...
>>> IntList(['1', 2, 3.0]).to_data()
```

### Pattern 3: nested type parameters

```pycon exec="1" source="console"
>>> from omnipy import Model
>>> Model[dict[str, list[int]]]({'a': [1, '2'], 'b': [3.0]}).to_data()
```

## Links

- How-to: [Parse strategies](parse-strategies.md)
- How-to: [Parametrized models](parametrized-models.md)
