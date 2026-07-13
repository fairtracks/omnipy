# Flow Task Dedup Refactor Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reduce duplication in `tests/engine/cases/flows.py` by extracting reusable `TaskTemplate` definitions into a shared raw-task module and by consolidating repeated result-assertion patterns.

**Architecture:** Keep `tests/engine/cases/flows.py` as the authority for flow topology and case-specific routing, but move reusable sync/async task templates into `tests/engine/cases/raw/tasks.py`. Preserve callable type exactly for every reused task and keep structurally specific DAG-routing or revise-only tasks local to the cases that need them.

**Tech Stack:** Python, pytest, pytest-cases, asyncio, Omnipy `TaskTemplate` / flow templates

---

## File map

- Create: `tests/engine/cases/raw/tasks.py`
  - Shared sync-function, async-coroutine, sync-generator, and async-generator task templates reused across flow cases.
- Modify: `tests/engine/cases/flows.py`
  - Import the shared task templates, replace duplicate local task definitions where callable type and behavior match, and extract common result/assertion helpers.

## Acceptance criteria

- `tests/engine/cases/raw/tasks.py` contains the shared task templates used by the refactored flow cases.
- `tests/engine/cases/flows.py` has materially fewer inline `@TaskTemplate()` definitions and reuses the shared tasks without changing callable type.
- Repeated `run_and_assert_results` boilerplate is reduced through shared helper functions in `tests/engine/cases/flows.py`.
- These verification commands pass:
  - `uv run pytest tests/engine/test_all_engines.py -v --mypy-pyproject-toml-file=pyproject.toml`
  - `uv run pytest tests/engine/test_job_runner.py -v --mypy-pyproject-toml-file=pyproject.toml`
  - `uv run pytest tests/integration/reused/engine/test_all_engines_with_real_jobs_and_registry.py -v --mypy-pyproject-toml-file=pyproject.toml`

## Tasks

### Task 1: Add the shared raw-task catalog

**Files:**
- Create: `tests/engine/cases/raw/tasks.py`

- [ ] Add shared `TaskTemplate` definitions for the repeated arithmetic helpers, repeated sync/async sequence emitters, and repeated reducers/passthrough helpers used by `flows.py`.
- [ ] Keep callable types exact: sync function stays sync function, async coroutine stays async coroutine, sync generator stays sync generator, async generator stays async generator.
- [ ] Do not move case-specific DAG-routing or revise-only tasks into the shared module.

### Task 2: Refactor `flows.py` to reuse shared tasks

**Files:**
- Modify: `tests/engine/cases/flows.py`

- [ ] Import the shared tasks from `tests/engine/cases/raw/tasks.py`.
- [ ] Replace duplicate local tasks with shared tasks where behavior and callable type match.
- [ ] Use `refine(param_key_map=...)` and `refine(result_key=...)` when a shared task's generic parameter names need to bind to case-specific DAG keys.
- [ ] Leave structurally specific tasks local when sharing would hide meaningful topology or require a callable-type change.

### Task 3: Extract common assertion helpers and verify

**Files:**
- Modify: `tests/engine/cases/flows.py`

- [ ] Add shared helpers for repeated scalar, awaited-scalar, sync-generator, async-generator, and nested-async-generator assertion patterns.
- [ ] Update the affected `run_and_assert_results` closures to use those helpers while preserving case-specific expectations.
- [ ] Run the requested verification commands and confirm they pass.
