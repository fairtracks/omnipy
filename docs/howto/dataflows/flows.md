# Flows

--8<-- "_includes/maturity_labels.md"

!!! note
    **Status: Now**

## Linear flows

```pycon exec="1" source="console"
>>> import omnipy as om
>>> @om.TaskTemplate()
... def plus_one(number: int) -> int:
...     return number + 1
>>> @om.LinearFlowTemplate(plus_one, plus_one)
... def plus_two(number: int) -> int:
...     ...
>>> plus_two.run(10)
```

## DAG flows

```pycon exec="1" source="console"
>>> import omnipy as om
>>> @om.TaskTemplate()
... def make_inputs() -> dict[str, int]:
...     return {'number': 21}
>>> @om.TaskTemplate()
... def double(number: int) -> int:
...     return number * 2
>>> @om.DagFlowTemplate(make_inputs, double)
... def my_dag() -> int:
...     ...
>>> my_dag.run()
```

## FuncFlow

```pycon exec="1" source="console"
>>> import omnipy as om
>>> @om.TaskTemplate()
... def plus_one(number: int) -> int:
...     return number + 1
>>> @om.FuncFlowTemplate()
... def repeat_plus_one(number: int, n: int) -> int:
...     for _ in range(n):
...         number = plus_one(number=number)
...     return number
>>> repeat_plus_one.run(0, 3)
```
