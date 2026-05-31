# Snapshots & rollbacks

--8<-- "_includes/maturity_labels.md"

!!! note
    **Status: Now**

## 1) What it solves

Interactive edits are error-prone. If one mutation fails validation, you want to keep the last good
state and continue.

## 2) The idea

With interactive mode enabled, Omnipy snapshots validated model state and rolls back on failed
mutations.

## 3) Example

```pycon exec="1" source="console"
>>> import omnipy as om
>>> om.runtime.config.data.model.interactive = True
>>> xs = om.Model[list[int]]([1, 2, 3])
>>> try:
...     xs.append('oops')
... except Exception as err:
...     print(type(err).__name__)
>>> xs.content
```

## 4) Output / display

```pycon exec="1" result="console" html="true"
>>> import omnipy as om
>>> om.runtime.config.data.model.interactive = True
>>> xs = om.Model[list[int]]([1, 2, 3])
>>> print(xs._docs())
```

## 5) When to use / when not

Use it in notebook-first and exploration-heavy workflows.

Disable it for tight batch loops if you need to reduce snapshot overhead.

## 6) Gotchas

- Validation still happens when interactive mode is off.
- Only rollback behavior changes.

## 7) Links

- Feature: [Continuous validation](continuous-validation.md)
- How-to: [Display & inspection](../howto/models/display-inspection.md)
