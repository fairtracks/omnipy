# Tasks

--8<-- "_includes/maturity_labels.md"

!!! note
    **Status: Now**

## Define a typed task

```pycon exec="1" source="console"
>>> from omnipy import TaskTemplate
>>> @TaskTemplate()
... def plus_one(number: int) -> int:
...     return number + 1
>>> plus_one.run(10)
```

## Use parameters and return types intentionally

```pycon exec="1" source="console"
>>> from omnipy import TaskTemplate
>>> @TaskTemplate()
... def plus_other(number: int, other: int) -> int:
...     return number + other
>>> plus_other.run(10, 7)
```
