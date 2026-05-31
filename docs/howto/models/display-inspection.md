# Display & inspection

--8<-- "_includes/maturity_labels.md"

!!! note
    **Status: Now**

## `_docs()` for stable rendered output

```pycon exec="1" source="console"
>>> from omnipy import Model
>>> m = Model[dict[str, list[int]]]({'a': [1, 2], 'b': [3, 4]})
>>> print(m._docs())
```

## `peek()` / `full()` / `browse()` usage

```python
from omnipy import Model

m = Model[list[int]]([1, 2, 3])
m.peek()
m.full()
m.browse()
```

!!! tip
    `browse()` is best for notebook or local GUI sessions.

## Try it in a notebook

Run `m.peek()`, `m.full()`, and `m.browse()` in Jupyter to compare outputs side-by-side.
