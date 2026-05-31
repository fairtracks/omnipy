# Engines overview

--8<-- "_includes/maturity_labels.md"

!!! note
    **Status: Preview**

    Local engine is **Now**. Prefect orchestration is usable but evolving.

## Inspect current engine

```pycon exec="1" source="console"
>>> from omnipy import runtime
>>> runtime.config.engine.choice
```

## Set engine choice

```python
from omnipy import runtime

runtime.config.engine.choice = 'local'
runtime.config.engine.choice = 'prefect'
```

Use `local` examples in docs to keep builds self-contained.
