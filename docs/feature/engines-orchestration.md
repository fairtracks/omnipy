# Engines & orchestration

--8<-- "_includes/maturity_labels.md"

> [!NOTE]
> **Status: Preview**
>
> Local engine behavior is **Now**. Prefect orchestration is usable and evolving.

## 1) What it solves

You want one task/flow definition that can run locally today and move to orchestration later.

## 2) The idea

Runtime engine choice controls execution backend (`local` or `prefect`) without rewriting model or
flow definitions.

## 3) Example

```pycon exec="1" source="console"
>>> from omnipy import TaskTemplate, runtime
>>> runtime.config.engine.choice
'local'
>>> runtime.config.engine.choice = 'prefect'
>>> @TaskTemplate()
... def double(x: int) -> int:
...     return x * 2
>>> double.run(21)
42
>>> runtime.config.engine.choice = 'local'
```

## 4) Output / display

Inspect values with `_docs()` / `.to_data()` the same way regardless of engine.

## 5) When to use / when not

Use local for inner-loop development and deterministic docs examples.

Use orchestration when scheduling/retry/caching/operational controls matter.

## 6) Gotchas

- Keep docs runnable without external services by default.
- Engine-specific operational semantics can differ.
- For CLI-driven runs, use `omnipy-examples --engine prefect ...`.

## 7) Links

- How-to: [Engines overview](../howto/dataflows/engines-overview.md)
- How-to: [Running flows](../howto/dataflows/running-flows.md)
- Tutorial: [Prefect orchestration](../tutorials/08-prefect-orchestration.md)
