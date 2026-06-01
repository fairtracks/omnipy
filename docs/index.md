# Omnipy

Typed dataflows for messy real-world data — continuous validation, safe interactive manipulation,
and one-line conversions from nested JSON to tables.

Deep JSON flattening works for many common structures, but there are current boundaries and
shape-dependent edge cases — see [Tutorial 2: Nested JSON to tables](tutorials/02-json-to-tables.md)
for the current limits.

## Why you care

- **Continuous validation** while editing keeps model state valid after failed operations.
- **Declarative conversions** with `.to(...)` reduce custom conversion glue code.
- **Dataset batch semantics** apply typed parsing and transformations across many records.

## Parse messy input → safe edit → pretty-printed output

```pycon exec="1" session="landing" source="console"
>>> import omnipy as om
--8<-- "_includes/pycon_hidden_runtime_setup.md"
```

```pycon exec="1" session="landing" source="console"
>>> my_integers = om.Model[list[int]]((101, '102', 103.0))
>>> my_integers
```

```pycon exec="1" session="landing" result="console" html="true"
>>> print(my_integers._docs())
```

```pycon
>>> my_integers.append('invalid')
```


```pycon exec="1" session="landing" result="console"
>>> import omnipy.util.pydantic as pyd
>>> try:
>>>     my_integers.append('invalid')
>>> except pyd.ValidationError as e:
>>>     print(e)
```

```pycon
>>> my_integers
```

```pycon exec="1" session="landing" result="console" html="true"
>>> print(my_integers._docs())
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

## Visual metaphors and story mode (coming later)

Visual metaphors and story mode (coming later).
See the planned stub page: [Visual metaphors and story mode](learn/visual-metaphors-story-mode.md).
