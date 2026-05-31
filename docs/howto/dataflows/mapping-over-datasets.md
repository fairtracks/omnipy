# Mapping over datasets

--8<-- "_includes/maturity_labels.md"

!!! note
    **Status: Now**

## Dataset-native mapping with `.do(...)`

```pycon exec="1" source="console"
>>> from omnipy import Dataset, Model
>>> xs = Dataset[Model[int]]({'a': '1', 'b': 2.0})
>>> xs.do(lambda x: int(x) + 1).to_data()
```

## Task mapping with `iterate_over_data_files=True`

```pycon exec="1" source="console"
>>> from omnipy import Dataset, Model, TaskTemplate
>>> xs = Dataset[Model[int]]({'a': '1', 'b': 2.0})
>>> @TaskTemplate(iterate_over_data_files=True)
... def inc(x: int) -> int:
...     return x + 1
>>> inc.run(xs).to_data()
```
