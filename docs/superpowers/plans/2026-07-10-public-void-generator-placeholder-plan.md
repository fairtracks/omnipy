# Public Void Generator Placeholder Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a public `Void` helper for signature-only generator flow bodies, re-export it from `omnipy`, document it primarily in the `Void` docstring, and update the existing generator flow tests to use it.

**Architecture:** Implement `Void` in `src/omnipy/compute/helpers.py` as a tiny sync/async empty iterable. Keep the public convention as small as possible: `yield from Void()` for sync generators and `async for _ in Void(): yield _` for async generators. Make the docstring the primary documentation surface, and add only a short supporting example section in `docs/howto/dataflows/flows.md`.

**Tech Stack:** Python 3.10, Omnipy public API, pytest, mypy, basedpyright, MkDocs docs

---

## File map

- Create: `src/omnipy/compute/helpers.py`
- Modify: `src/omnipy/__init__.py`
- Modify if needed by export maintenance: `src/omnipy/_dynamic_all.py`
- Modify: `tests/engine/cases/flows.py`
- Modify: `docs/howto/dataflows/flows.md`

## Settled public convention

Sync generator body:

```python
yield from Void()  # For generator signature only; never run.
```

Async generator body:

```python
async for _ in Void():  # For generator signature only; never run.
    yield _
```

## Task 1: Add the public helper

**Files:**
- Create: `src/omnipy/compute/helpers.py`

- [ ] Add `Void` with this implementation and docstring:

```python
class Void:
    """
    Empty sync/async iterable for signature-only generator flow bodies.

    Use this when a flow template body exists only to define a generator or
    async-generator callable signature, while the child jobs perform the
    actual work.

    Examples:
        @LinearFlowTemplate(task_one, generator_task_two)
        def my_sync_generator_flow(number: int) -> Generator[int, None, None]:
            yield from Void()  # For generator signature only; never run.

        @DagFlowTemplate(task_one, async_generator_task_two)
        async def my_async_generator_flow(number: int) -> AsyncGenerator[int, None]:
            async for _ in Void():  # For generator signature only; never run.
                yield _
    """

    def __iter__(self):
        return iter(())

    def __aiter__(self):
        return self

    async def __anext__(self):
        raise StopAsyncIteration
```

- [ ] Keep the examples intentionally non-runnable but understandable: the body is signature-only, and the named child jobs indicate what actually executes.

## Task 2: Re-export `Void` publicly

**Files:**
- Modify: `src/omnipy/__init__.py`
- Modify if needed: `src/omnipy/_dynamic_all.py`

- [ ] Add the public import:

```python
from omnipy.compute.helpers import Void
```

- [ ] Update any related dynamic export maintenance file if Omnipy requires it for top-level API completeness.

## Task 3: Update generator flow tests to use the public API

**Files:**
- Modify: `tests/engine/cases/flows.py`

- [ ] Import `Void` from the public API path:

```python
from omnipy import Void
```

- [ ] Replace sync signature-only generator bodies with:

```python
yield from Void()  # For generator signature only; never run.
```

- [ ] Replace async signature-only generator bodies with:

```python
async for _ in Void():  # For generator signature only; never run.
    yield _
```

- [ ] Remove the current `if False: yield ...` placeholders from the updated cases.

## Task 4: Add short supporting docs examples

**Files:**
- Modify: `docs/howto/dataflows/flows.md`

- [ ] Add a short note explaining that some generator flow bodies exist only to define the callable signature while the child jobs perform the actual work.

- [ ] Add a brief sync example:

```python
@LinearFlowTemplate(task_one, generator_task_two)
def my_sync_generator_flow(number: int) -> Generator[int, None, None]:
    yield from Void()  # For generator signature only; never run.
```

- [ ] Add a brief async example:

```python
@DagFlowTemplate(task_one, async_generator_task_two)
async def my_async_generator_flow(number: int) -> AsyncGenerator[int, None]:
    async for _ in Void():  # For generator signature only; never run.
        yield _
```

- [ ] Keep the full explanation in the `Void` docstring; the docs page should only supplement it.

## Task 5: Verify

**Files:**
- Verify: `src/omnipy/compute/helpers.py`
- Verify: `src/omnipy/__init__.py`
- Verify: `tests/engine/cases/flows.py`
- Verify: `docs/howto/dataflows/flows.md`

- [ ] Run:

```bash
uv run pytest tests/engine/cases/flows.py -v --mypy-pyproject-toml-file=pyproject.toml
```

- [ ] Run:

```bash
uv run mypy --hide-error-context --no-error-summary tests/engine/cases/flows.py src/omnipy/compute/helpers.py src/omnipy/__init__.py
```

- [ ] Run:

```bash
uv run basedpyright tests/engine/cases/flows.py src/omnipy/compute/helpers.py src/omnipy/__init__.py
```

- [ ] Run:

```bash
uv run pre-commit run --hook-stage manual --all-files
```

## Task 6: Final review

- [ ] Confirm public usage is `Void()`.
- [ ] Confirm the `Void` docstring is the primary documentation surface.
- [ ] Confirm `docs/howto/dataflows/flows.md` only adds short supporting examples.
- [ ] Confirm the updated flow tests no longer use `if False: yield ...` in the converted cases.
