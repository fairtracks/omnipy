# FAQ

--8<-- "_includes/maturity_labels.md"

> [!NOTE]
> **Status: Now**

## Why use Omnipy when Pydantic already exists?

Pydantic is excellent for object-level validation. Omnipy builds on that style and adds pipeline
oriented primitives: typed datasets, conversions (`.to()`), task/flow templates, runtime engine
switching, and interactive rollback behavior that helps catch bad state during transformations.

In short: Pydantic gives strong schema validation; Omnipy adds structured dataflow ergonomics around
that foundation.

## Does Omnipy work in notebooks?

Yes. Notebook usage is a common workflow for exploratory parsing, model design, and inspecting data
with `_docs()` / `.to_data()`. For async-heavy or UI-specific exploration, notebooks are often more
convenient than plain terminal sessions.

## How do I disable interactive mode?

Set interactive behavior on runtime config:

```python
from omnipy import runtime

runtime.config.data.model.interactive = False
```

Set it back to `True` when you want interactive rollback checks during development.

## How do I convert JSON to tables?

Use typed JSON models and convert into table-oriented models for analysis workflows:

```pycon exec="1" source="console"
>>> from omnipy import JsonListOfDictsModel, RowWiseTableWithColNamesModel, PandasModel
>>> json_rows = JsonListOfDictsModel([
...     {'sample': 's1', 'count': 10},
...     {'sample': 's2', 'count': 12},
... ])
>>> json_rows.to(RowWiseTableWithColNamesModel).to_data()
[{"sample": "s1", "count": 10}, {"sample": "s2", "count": 12}]
>>> json_rows.to(RowWiseTableWithColNamesModel).to(PandasModel).to_data()
[{"sample": "s1", "count": 10}, {"sample": "s2", "count": 12}]
```

For deeper nesting patterns, start with the JSON tutorial path and flatten in stages.

## How do I run flows with Prefect?

1. Install dependencies with `pip install omnipy` (Prefect is included).
2. Set `runtime.config.engine.choice = 'prefect'`.
3. Run your flow with `.run(...)` as usual.
4. Optionally run CLI examples with `--engine prefect`.
5. Start Prefect UI via `prefect server start` to inspect runs.

See: [Tutorial 8: Prefect orchestration](../tutorials/08-prefect-orchestration.md)
