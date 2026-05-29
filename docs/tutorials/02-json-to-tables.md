# Tutorial 2: Nested JSON to tables

This tutorial parses nested JSON, flattens it into related table-like datasets, and converts output
to pandas-backed types.

## Setup

```pycon exec="1" session="tutorial2" source="console"
>>> from omnipy import runtime
>>> runtime.config.root_log.log_to_stdout = False
>>> runtime.config.root_log.log_to_stderr = False
>>> runtime.config.root_log.log_to_file = False
>>> runtime.config.job.output_storage.persist_outputs = 'disabled'
```

## Parse nested JSON

```pycon exec="1" session="tutorial2" source="console"
>>> from omnipy import JsonListOfDictsDataset
>>> nested = JsonListOfDictsDataset({'items': [
...     {'id': 'a', 'meta': {'x': 1, 'y': 2}, 'tags': [{'k': 't', 'v': 1}, {'k': 'u', 'v': 2}]},
...     {'id': 'b', 'meta': {'x': 3, 'y': 4}, 'tags': []},
... ]})
>>> nested
```

```pycon exec="1" session="tutorial2" result="console" html="true"
>>> print(nested._docs())
```

## Flatten to related tables

```pycon exec="1" session="tutorial2" source="console"
>>> from omnipy.components.json.flows import flatten_nested_json
>>> flat = flatten_nested_json.run(nested)
>>> sorted(flat.to_data().keys())
```

```pycon exec="1" session="tutorial2" result="console" html="true"
>>> print(flat._docs())
```

Dataset naming preserves relational structure (`items`, `items.meta`, `items.tags`) so table
relationships stay explicit.

## Convert with `.to(PandasModel)` and `.to(PandasDataset)`

```pycon exec="1" session="tutorial2" source="console"
>>> from omnipy import JsonListOfDictsModel, PandasDataset, PandasModel
>>> flat_pd = flat.to(PandasDataset)
>>> one_table = JsonListOfDictsModel([{'id': 'a', 'x': 1}, {'id': 'b', 'x': 3}])
>>> one_table_pd = one_table.to(PandasModel)
>>> flat_pd
>>> one_table_pd
```

```pycon exec="1" session="tutorial2" result="console" html="true"
>>> print(flat_pd._docs())
```

## Current boundaries

Supported shapes include:

- list of dicts
- dict of dicts
- dict of lists

Not supported in this conversion path:

- mixed containers/scalars at level 2
- single-level lists, dicts, or scalars

Flattening supports deeply nested structures where `pandas.json_normalize` often struggles, but it
still has boundaries.

See also: [Parse, don't validate](../learn/parse-dont-validate.md)
