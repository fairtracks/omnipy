# Tutorial 1: Interactive safety

You are collecting arcade sensor readings that must stay valid integers while you experiment.

Omnipy models continuously validate data and type-mimic the wrapped Python type.

> A Pydantic model is a use-once-then-discard validator; an Omnipy model is a continuous
> static-type repairman in a dynamic environment.

## Setup

```pycon exec="1" session="tutorial1" source="console"
>>> import omnipy as om
>>> om.runtime.config.root_log.log_to_stdout = False
>>> om.runtime.config.root_log.log_to_stderr = False
>>> om.runtime.config.root_log.log_to_file = False
>>> om.runtime.config.job.output_storage.persist_outputs = 'disabled'
>>> om.runtime.config.data.model.interactive = True
```

## Parse and inspect

```pycon exec="1" session="tutorial1" source="console"
>>> readings = om.Model[list[int]]((120, '135', 142.0))
>>> readings
```

```pycon exec="1" session="tutorial1" result="console" html="true"
>>> print(readings._docs())
```

## Error + rollback demonstration

```pycon exec="1" session="tutorial1" source="console"
>>> before_error = readings.content.copy()
>>> try:
...     readings.append('bonus-ticket')
... except Exception as err:
...     print(type(err).__name__)
>>> after_error = readings.content
>>> print(before_error == after_error)
>>> readings
```

```pycon exec="1" session="tutorial1" result="console" html="true"
>>> print(readings._docs())
```

## Interactive mode framing

Choose based on trade-offs, not environment:

- `runtime.config.data.model.interactive = True`: snapshot + rollback robustness.
- `runtime.config.data.model.interactive = False`: lower memory overhead and raw write speed, but
  no rollback after validation errors.

```pycon exec="1" session="tutorial1" source="console"
>>> om.runtime.config.data.model.interactive = False
>>> fast_mode = om.Model[list[int]]([10, 20, 30])
>>> try:
...     fast_mode.append('VIP')
... except Exception as err:
...     print(type(err).__name__)
>>> fast_mode
```

With `interactive=False`, Omnipy still raises a validation exception immediately, but the invalid
value remains in the model state (`[10, 20, 30, 'VIP']`).

```pycon exec="1" session="tutorial1" result="console" html="true"
>>> print(fast_mode._docs())
```

## What you learned

- Continuous validation + type mimicking keep model edits safe.
- Rollback behavior is controlled via `runtime.config.data.model.interactive`.

## Common pitfalls

- Assuming non-interactive mode is "strictly safer" because it still raises errors. It raises, but
  it does not roll back invalid mutations.

## Next steps

- Continue with [Tutorial 2: Nested JSON to tables](02-json-to-tables.md).
