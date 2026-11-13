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

### Per-job options from plugins

A plugin can add keyword arguments to job templates, for settings that vary per job:

```python
@om.TaskTemplate(tes_image='ghcr.io/me/omnipy-bio:1.2')
def align(...): ...
```

The plugin provides them through a job mixin, listed in its engine class as `job_mixins`. The
mixin is added to every job applied while that engine is selected, and to any job that gives one
of its keyword arguments.

Plugins are loaded lazily, so a template may be created before the plugin is loaded. Omnipy then
keeps the unknown keyword arguments on the template and tries them again when the template is
applied. If no loaded mixin uses a keyword argument at that point, for example when running a job
with TES options on the local engine, or after a typo, Omnipy logs a warning. Setting the
environment variable `OMNIPY_SILENCE_UNUSED_JOB_KEYWORDS=1` silences it.
