# Running flows

--8<-- "_includes/maturity_labels.md"

!!! note
    **Status: Now**

## Run with local engine defaults

```pycon exec="1" source="console"
>>> from omnipy import TaskTemplate, LinearFlowTemplate
>>> @TaskTemplate()
... def plus_one(number: int) -> int:
...     return number + 1
>>> @LinearFlowTemplate(plus_one, plus_one, plus_one)
... def plus_three(number: int) -> int:
...     ...
>>> plus_three.run(10)
```

## Create a runnable job via `.apply()`

```pycon exec="1" source="console"
>>> from omnipy import TaskTemplate, LinearFlowTemplate
>>> @TaskTemplate()
... def plus_one(number: int) -> int:
...     return number + 1
>>> @LinearFlowTemplate(plus_one, plus_one, plus_one)
... def plus_three(number: int) -> int:
...     ...
>>> flow_job = plus_three.apply()
>>> flow_job(10)
```

## Async note

!!! note
    Some task/flow contexts support async usage.

### Try it in a notebook

For async exploration, run in Jupyter where `await` is convenient.
