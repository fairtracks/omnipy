# Tutorial 3: Dataset batch

Start with Dataset + Model batch parsing, then apply transformations without explicit loops.

## Setup

```pycon exec="1" session="tutorial3" source="console"
>>> import omnipy as om
>>> om.runtime.config.root_log.log_to_stdout = False  # markdown-exec: hide
>>> om.runtime.config.root_log.log_to_stderr = False  # markdown-exec: hide
>>> om.runtime.config.root_log.log_to_file = False  # markdown-exec: hide
>>> om.runtime.config.job.output_storage.persist_outputs = 'disabled'  # markdown-exec: hide
```

## Batch parsing with Dataset

```pycon exec="1" session="tutorial3" source="console"
>>> readings = om.Dataset[om.Model[int]]({'sensor_a': '1', 'sensor_b': 2.0, 'sensor_c': 3})
>>> readings
```

```pycon exec="1" session="tutorial3" result="console" html="true"
>>> print(readings._docs())
```

## No-for-loop batch transform pattern

```pycon exec="1" session="tutorial3" source="console"
>>> incremented = readings.do(lambda value: int(value) + 1)
```

```pycon exec="1" session="tutorial3" result="console"
>>> incremented.json()
```

## Hierarchical datasets

```pycon exec="1" session="tutorial3" source="console"
>>> from omnipy import Dataset, Model
>>> Inner = Dataset[Model[int]]
>>> Outer = Dataset[Inner]
>>> grouped = Outer({'group1': {'a': 1, 'b': 2}, 'group2': {'a': 10}})
>>> grouped
```

```pycon exec="1" session="tutorial3" result="console" html="true"
>>> print(grouped._docs())
```

```pycon exec="1" session="tutorial3" source="console"
>>> grouped_incremented = grouped.do(lambda dataset: dataset.do(lambda value: int(value) + 1))
```

```pycon exec="1" session="tutorial3" result="console"
>>> grouped_incremented.json()
```

You get batch behavior and hierarchy handling without writing explicit `for` loops.

## What you learned

- `Dataset[Model[int]](...)` parses and batches many values in one typed container.
- `Dataset.do(...)` lets you apply per-item transforms without explicit loops.
- Nested datasets can be transformed hierarchically while preserving structure.

## Common pitfalls

- Forgetting to convert values inside lambdas when needed. Use `int(value)` in mixed parsed inputs.

## Next steps

- Revisit [Tutorial 2: Nested JSON to tables](02-json-to-tables.md) and combine it with batch
  transformations.
