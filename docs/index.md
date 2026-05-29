# Omnipy

Typed dataflows for messy real-world data — continuous validation, safe interactive manipulation,
and one-line conversions from nested JSON to tables.

!!! note "JSON → tables caveat"
    Deep JSON flattening works well for many common shapes, but it still has limits (for example,
    deeply irregular hierarchies and mixed structures). See
    [Tutorial 2: Nested JSON to tables](tutorials/02-json-to-tables.md) for current boundaries.

## Why you care

- **Continuous validation** while editing keeps model state valid after failed operations.
- **Declarative conversions** with `.to(...)` reduce custom conversion glue code.
- **Dataset batch semantics** apply typed parsing and transformations across many records.

## Parse messy input → safe edit → visible output

```pycon exec="1" session="landing" source="console"
>>> from omnipy import Model, runtime
>>> runtime.config.root_log.log_to_stdout = False
>>> runtime.config.root_log.log_to_stderr = False
>>> runtime.config.root_log.log_to_file = False
>>> runtime.config.job.output_storage.persist_outputs = 'disabled'
>>> runtime.config.data.model.interactive = True
>>> readings = Model[list[int]]((101, '102', 103.0))
>>> try:
...     readings.append('invalid')
... except Exception as err:
...     print(type(err).__name__)
>>> readings
```

```pycon exec="1" session="landing" result="console" html="true"
>>> print(readings._docs())
```

<p>
  <a href="start/quickstart/" class="md-button md-button--primary">10-minute Quickstart</a>
  <a href="tutorials/01-interactive-safety/" class="md-button">Tutorials</a>
</p>

## Compare

- **When `requests + pandas + pydantic` is enough:** straightforward one-off parsing and tabular
  analysis pipelines.
- **When Omnipy pays off:** continuous typed safety during editing, nested-to-tabular conversion
  paths, and dataset-level batch semantics.

## Visual metaphors and story mode (Planned)

Later versions may add optional visual metaphors and a story-mode learning layer.
