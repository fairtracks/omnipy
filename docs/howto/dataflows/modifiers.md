# Modifiers

--8<-- "_includes/maturity_labels.md"

> [!NOTE]
> **Status: Now**

Modifiers let you adapt task/flow templates without rewriting core function bodies.

## `param_key_map` example

```pycon exec="1" source="console"
>>> from omnipy import TaskTemplate
>>> @TaskTemplate()
... def plus_other(number: int, other: int) -> int:
...     return number + other
>>> plus_x = plus_other.refine(name='plus_x', param_key_map={'other': 'x'})
>>> plus_x.run(number=1, x=2)
```

## `result_key` example

```pycon exec="1" source="console"
>>> from omnipy import TaskTemplate
>>> @TaskTemplate()
... def plus_other(number: int, other: int) -> int:
...     return number + other
>>> plus_one_dict = plus_other.refine(name='plus_one', fixed_params={'other': 1}).refine(result_key='number')
>>> plus_one_dict.run(number=10)
```
