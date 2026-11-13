# Engines overview

--8<-- "_includes/maturity_labels.md"

!!! note
    **Status: Preview**

    Local engine is **Now**. Prefect orchestration is usable but evolving.

## Inspect current engine

```pycon exec="1" source="console"
>>> import omnipy as om
>>> om.runtime.config.engine.choice
```

## Set engine choice

```python
import omnipy as om

om.runtime.config.engine.choice = 'local'
om.runtime.config.engine.choice = 'prefect'
```

Use `local` examples in docs to keep builds self-contained.

## Plugin engines

Other packages can add engines. A plugin declares its engine in the `omnipy.engines` entry point
group of its `pyproject.toml`, with the engine name as the entry point name:

```toml
[project.entry-points."omnipy.engines"]
tes = "omnipy_ga4gh_sdk.engine:TesEngine"
```

Once the package is installed, the engine name is accepted as an engine choice. The plugin is
only imported when the engine is first used, so installed plugins do not slow down
`import omnipy`:

```python
import omnipy as om

om.runtime.config.engine.choice = 'tes'  # imports the plugin and loads the engine
om.runtime.config.engine.tes.base_url = 'http://localhost:8000'
```

Reading `om.runtime.config.engine.tes` or `om.runtime.objects.tes` also loads the engine.
Choosing a name that no installed engine has raises an error listing the registered engines.

Type checkers only know the built-in engines, so they flag attributes such as
`om.runtime.config.engine.tes`. A plugin can offer typed helpers for its config and engine.
