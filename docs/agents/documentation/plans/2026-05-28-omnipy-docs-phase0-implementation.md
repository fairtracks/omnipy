# Omnipy Docs Phase 0 (Landing + Start + Tutorials 1–3) — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement Phase 0 of the approved docs redesign spec: a compelling landing page, Start pages (Install + 10-minute Quickstart), Tutorials 1–3, updated navigation, and thin redirect stubs.

**Architecture:** Keep MkDocs Material setup intact, add new pages under `docs/start/` and `docs/tutorials/`, update `mkdocs.yml` `nav:` to provide the Phase 0 “Start here” and “Tutorials” on-ramps, and preserve old top-level pages as thin stubs pointing to the new locations. Prefer runnable docs examples using `markdown-exec` (`pycon exec="1"`) and ensure every tutorial demonstrates Omnipy’s display output (`_docs()`, plus optional `peek/full/json/browse` where appropriate).

**Tech Stack:** MkDocs Material; `markdown-exec`; `pymdownx` extensions already configured; `uv` for running `mkdocs build`.

---

## File structure (create/modify map)

**Create:**
- `docs/start/install.md` — installation guide extracted from existing `docs/readme.md`
- `docs/start/quickstart.md` — 10-minute end-to-end quickstart
- `docs/tutorials/01-interactive-safety.md` — tutorial 1
- `docs/tutorials/02-json-to-tables.md` — tutorial 2
- `docs/tutorials/03-dataset-batch.md` — tutorial 3
- `docs/story_mode.md` — neutral v2 placeholder page linked from landing

**Modify:**
- `docs/index.md` — replace readme-include wrapper with purpose-built landing page
- `mkdocs.yml` — nav reorganized to Phase 0 IA
- `docs/data_models.md` — thin redirect stub to new tutorial(s)/start
- `docs/python_typing.md` — thin redirect stub to “Learn” (Phase 1+) while linking to Start/Tutorials now

**Preserve (no content rewrite in Phase 0, but ensure reachable):**
- `docs/parse_dont_validate.md` — must remain and be linked from Tutorial 2

**Note on literate-nav:** current `mkdocs.yml` uses `literate-nav` for API reference under `reference/`. Phase 0 changes should not alter `docs/gen_ref_pages.py` or the generated `reference/SUMMARY.md`.

---

## Global verification commands (use throughout)

- Build docs site:
  - Run: `uv run --all-groups mkdocs build`
  - Expected: exit code 0

---

## Task 0: Preflight + keep the workspace clean

**Files:** none

- [ ] **Step 0.1: Verify working tree is clean enough**

Run: `git status --porcelain=v1`

Expected: no unexpected modified tracked files. (Untracked files are OK, but should be avoided.)

- [ ] **Step 0.2: (Optional) If you’ve generated `outputs/` and `logs/` during local experiments, disable persistence in doc examples**

When writing runnable examples later, include these 4 lines near the top of each tutorial’s session (so `markdown-exec` runs don’t create `outputs/`/`logs/`):

```pycon exec="1" session="..."
>>> from omnipy import runtime
>>> runtime.config.root_log.log_to_stdout = False
>>> runtime.config.root_log.log_to_stderr = False
>>> runtime.config.root_log.log_to_file = False
>>> runtime.config.job.output_storage.persist_outputs = 'disabled'
```

No commit for this task.

---

## Task 1: Create Phase 0 doc directories

**Files:**
- Create: `docs/start/.gitkeep`
- Create: `docs/tutorials/.gitkeep`

- [ ] **Step 1.1: Add `docs/start/` directory marker**

Create `docs/start/.gitkeep` with:

```text

```

- [ ] **Step 1.2: Add `docs/tutorials/` directory marker**

Create `docs/tutorials/.gitkeep` with:

```text

```

- [ ] **Step 1.3: Verify MkDocs build still passes**

Run: `uv run --all-groups mkdocs build`

Expected: exit code 0

- [ ] **Step 1.4: Commit**

```bash
git add docs/start/.gitkeep docs/tutorials/.gitkeep
git commit -m "docs: add Phase 0 start/tutorial directories"
```

---

## Task 2: Update MkDocs nav to Phase 0 IA

**Files:**
- Modify: `mkdocs.yml`

Replace the current `nav:` block with the following (keep the rest of the file unchanged):

```yaml
nav:
  - Start here:
      - Home: index.md
      - Install: start/install.md
      - 10-minute Quickstart: start/quickstart.md
  - Tutorials:
      - '01. Interactive safety': tutorials/01-interactive-safety.md
      - '02. Nested JSON to tables': tutorials/02-json-to-tables.md
      - '03. Batch processing with Dataset': tutorials/03-dataset-batch.md
  - Learn:
      - Parse, don't validate: parse_dont_validate.md
      - Visual metaphors and story mode (planned): story_mode.md
      - Python typing (stub): python_typing.md
  - Reference:
      - Data models (stub): data_models.md
      - Contributing: contributing.md
      - Release notes: release_notes.md
      - Code Reference: reference/
```

- [ ] **Step 2.1: Edit `mkdocs.yml` nav**

Apply the change above.

- [ ] **Step 2.2: Verify MkDocs build**

Run: `uv run --all-groups mkdocs build`

Expected: exit code 0 (warnings OK).

- [ ] **Step 2.3: Commit**

```bash
git add mkdocs.yml
git commit -m "docs: reorganize nav for Phase 0 start and tutorials"
```

---

## Task 2.5: Add the Phase 0 “story mode” stub page

**Files:**
- Create: `docs/story_mode.md`

Create `docs/story_mode.md` with this complete content:

```markdown
# Visual metaphors and story mode (planned)

Later versions of the documentation may add an optional “story mode” layer and visual metaphors to
support learning.

- This is **not** part of v1 documentation.
- v1 content stays technical and neutral.
```

- [ ] **Step 2.5.1: Create `docs/story_mode.md`**

Add the file exactly as above.

- [ ] **Step 2.5.2: Verify MkDocs build**

Run: `uv run --all-groups mkdocs build`

Expected: exit code 0.

- [ ] **Step 2.5.3: Commit**

```bash
git add docs/story_mode.md
git commit -m "docs: add planned story mode stub"
```

---

## Task 3: Replace landing page (`docs/index.md`) with purpose-built copy

**Files:**
- Modify: `docs/index.md`

Replace the entire file with this complete content:

```markdown
---
hide:
  - toc
---

# Omnipy

Typed dataflows for messy real‑world data — continuous validation, safe interactive manipulation,
and one‑line conversions from nested JSON to tables.

!!! note "JSON → tables caveat"
    Deep JSON flattening works well for many common shapes, but it has limits (deeply irregular
    hierarchies, ambiguous keys, and mixed record types). See
    [Tutorial 2: Nested JSON to tables](tutorials/02-json-to-tables.md) for what works today.

## Why you care (in 3 seconds)

- **Keep data valid while you edit it** (automatic rollback after invalid operations)
- **Convert complex formats declaratively** with `.to(...)`
- **Batch-process hierarchical collections** with `Dataset` mapping

## One small example (with visible output)

```pycon exec="1" session="landing" source="console"
>>> from omnipy import Model, runtime
>>> runtime.config.root_log.log_to_stdout = False
>>> runtime.config.root_log.log_to_stderr = False
>>> runtime.config.root_log.log_to_file = False
>>> runtime.config.job.output_storage.persist_outputs = 'disabled'
>>> runtime.config.data.model.interactive = True
>>> ints = Model[list[int]]((123, '234', 345.0))
>>> try:
...     ints.append('oops')
... except Exception as err:
...     print(type(err).__name__)
>>> ints
```

```pycon exec="1" session="landing" result="console" html="true"
>>> print(ints._docs())
```

## Start now

<p>
  <a href="start/quickstart/" class="md-button md-button--primary">10-minute Quickstart</a>
  <a href="tutorials/01-interactive-safety/" class="md-button">Tutorials</a>
</p>

## Compare (when Omnipy pays off)

If `requests + pydantic + pandas` is enough for your situation, keep using it.
Omnipy pays off when you need **continuous safety** while transforming data, **repeatable conversions**
between structured formats, and **batch semantics** over collections without rewriting notebook code
into loops.

## Visual metaphors and story mode (planned)

Later versions may add optional visual metaphors and a “story mode” layer for learning. Not in v1.
See: [Visual metaphors and story mode (planned)](story_mode.md)
```

- [ ] **Step 3.1: Replace `docs/index.md` content**

Paste the full content above.

- [ ] **Step 3.2: Verify MkDocs build**

Run: `uv run --all-groups mkdocs build`

Expected: exit code 0.

- [ ] **Step 3.3: Commit**

```bash
git add docs/index.md
git commit -m "docs: replace landing page with Phase 0 value prop and CTAs"
```

---

## Task 4: Write Installation guide (`docs/start/install.md`)

**Files:**
- Create: `docs/start/install.md`

Create `docs/start/install.md` with this complete content:

```markdown
# Install

## Requirements

- Python **3.10–3.13** (Python 3.14 is not supported yet)

## Install Omnipy

If you already manage environments in your preferred way (venv, conda, Poetry, uv), keep doing that.

### Option A: `pip` (works everywhere)

```bash
python -m pip install omnipy
```

### Option B: `uv` (fast)

```bash
uv pip install omnipy
```

## Verify the install

```bash
python -c "import omnipy; print(omnipy.__version__)"
```

## Next

- Continue to the [10-minute Quickstart](quickstart.md)
```

- [ ] **Step 4.1: Create `docs/start/install.md`**

Add the file exactly as above.

- [ ] **Step 4.2: Verify MkDocs build**

Run: `uv run --all-groups mkdocs build`

Expected: exit code 0.

- [ ] **Step 4.3: Commit**

```bash
git add docs/start/install.md
git commit -m "docs: add installation guide"
```

---

## Task 5: Write 10-minute Quickstart (`docs/start/quickstart.md`)

**Files:**
- Create: `docs/start/quickstart.md`

Create `docs/start/quickstart.md` with this complete content (runnable):

```markdown
# 10-minute Quickstart

This page is a fast, runnable path to a visible result.

## 1) Install

Follow: [Install](install.md)

## 2) Parse messy input into a typed `Model`

```pycon exec="1" session="quickstart" source="console"
>>> from omnipy import Model, runtime
>>> runtime.config.root_log.log_to_stdout = False
>>> runtime.config.root_log.log_to_stderr = False
>>> runtime.config.root_log.log_to_file = False
>>> runtime.config.job.output_storage.persist_outputs = 'disabled'
>>> runtime.config.data.model.interactive = True
>>> raw = (123, '234', 345.0)
>>> ints = Model[list[int]](raw)
>>> ints
```

```pycon exec="1" session="quickstart" result="console" html="true"
>>> print(ints._docs())
```

## 3) Safe interactive edits (rollback on error)

```pycon exec="1" session="quickstart" source="console"
>>> try:
...     ints.append('oops')
... except Exception as err:
...     print(type(err).__name__)
```

```pycon exec="1" session="quickstart" source="console"
>>> ints
```

```pycon exec="1" session="quickstart" result="console" html="true"
>>> print(ints._docs())
```

## 4) Convert nested JSON to tables (preview)

This is a preview; the full story is in Tutorial 2.

```pycon exec="1" session="quickstart" source="console"
>>> from omnipy import JsonListOfDictsDataset, PandasDataset
>>> nested = JsonListOfDictsDataset({'items': [
...   {'id': 'a', 'meta': {'x': 1, 'y': 2}},
...   {'id': 'b', 'meta': {'x': 3, 'y': 4}},
... ]})
>>> nested
```

```pycon exec="1" session="quickstart" result="console" html="true"
>>> print(nested._docs())
```

```pycon exec="1" session="quickstart" source="console"
>>> pandas = nested.to(PandasDataset)
>>> pandas
```

```pycon exec="1" session="quickstart" result="console" html="true"
>>> print(pandas._docs())
```

## 5) Batch processing with `Dataset` (no loops)

```pycon exec="1" session="quickstart" source="console"
>>> from omnipy import Dataset, TaskTemplate
>>> @TaskTemplate(iterate_over_data_files=True)
... def inc(x: int) -> int:
...     return x + 1
>>> numbers = Dataset[Model[int]]({'a': 1, 'b': 2, 'c': 10})
>>> out = inc.run(numbers)
>>> out.to_data()
```

## Next steps

- [Tutorial 1: Interactive safety](../tutorials/01-interactive-safety.md)
- [Tutorial 2: Nested JSON to tables](../tutorials/02-json-to-tables.md)
- [Tutorial 3: Batch processing with Dataset](../tutorials/03-dataset-batch.md)
```

- [ ] **Step 5.1: Create `docs/start/quickstart.md`**

Add the file exactly as above.

- [ ] **Step 5.2: Verify MkDocs build (exec examples)**

Run: `uv run --all-groups mkdocs build`

Expected: exit code 0.

- [ ] **Step 5.3: Commit**

```bash
git add docs/start/quickstart.md
git commit -m "docs: add 10-minute quickstart"
```

---

## Task 6: Tutorial 1 — Interactive safety (`docs/tutorials/01-interactive-safety.md`)

**Files:**
- Create: `docs/tutorials/01-interactive-safety.md`

Create `docs/tutorials/01-interactive-safety.md` with this complete content:

```markdown
# Tutorial 1: Interactive safety (continuous validation + rollback)

This tutorial demonstrates Omnipy’s “interactive safety net”: models continuously validate and
automatically roll back after invalid edits when interactive mode is enabled.

## What you’ll build

- A typed model that behaves like a Python container
- An intentional mistake that triggers an error
- Automatic rollback to the last valid snapshot

## Setup (silence logs + avoid output persistence)

```pycon exec="1" session="t1" source="console"
>>> from omnipy import Model, runtime
>>> runtime.config.root_log.log_to_stdout = False
>>> runtime.config.root_log.log_to_stderr = False
>>> runtime.config.root_log.log_to_file = False
>>> runtime.config.job.output_storage.persist_outputs = 'disabled'
>>> runtime.config.data.model.interactive = True
```

## 1) Parse messy input

```pycon exec="1" session="t1" source="console"
>>> data = (123, '234', 345.0)
>>> ints = Model[list[int]](data)
>>> ints
```

```pycon exec="1" session="t1" result="console" html="true"
>>> print(ints._docs())
```

## 2) Make a mistake (and recover automatically)

```pycon exec="1" session="t1" source="console"
>>> try:
...     ints.append('not-an-int')
... except Exception as err:
...     print(type(err).__name__)
```

The model is still valid after the error:

```pycon exec="1" session="t1" source="console"
>>> ints
```

```pycon exec="1" session="t1" result="console" html="true"
>>> print(ints._docs())
```

## 3) Continue working without re-parsing

```pycon exec="1" session="t1" source="console"
>>> ints.append('456')
>>> ints
```

```pycon exec="1" session="t1" result="console" html="true"
>>> print(ints._docs())
```

## 4) Turning interactive rollback off

Interactive rollback is a feature (great for notebooks), but you can turn it off.

```pycon exec="1" session="t1" source="console"
>>> runtime.config.data.model.interactive = False
>>> ints2 = Model[list[int]]([1, 2, 3])
>>> try:
...     ints2.append('x')
... except Exception as err:
...     print(type(err).__name__)
>>> ints2
```

Notice: with interactive mode disabled, invalid operations can leave the model in an invalid state.
That’s often what you want in non-interactive contexts where you prefer failing fast.

## What you learned

- Omnipy models parse data into a typed shape and keep enforcing it
- With `runtime.config.data.model.interactive = True`, invalid edits roll back automatically

## Common pitfalls

- Confusing the config name: the correct setting is `model.interactive` (not `interactive_mode`).

## Next steps

- [Tutorial 2: Nested JSON to tables](02-json-to-tables.md)
```

- [ ] **Step 6.1: Create `docs/tutorials/01-interactive-safety.md`**

Add the file exactly as above.

- [ ] **Step 6.2: Verify MkDocs build**

Run: `uv run --all-groups mkdocs build`

Expected: exit code 0.

- [ ] **Step 6.3: Commit**

```bash
git add docs/tutorials/01-interactive-safety.md
git commit -m "docs: add tutorial 1 on interactive safety"
```

---

## Task 7: Tutorial 2 — Nested JSON to tables (`docs/tutorials/02-json-to-tables.md`)

**Files:**
- Create: `docs/tutorials/02-json-to-tables.md`

Create `docs/tutorials/02-json-to-tables.md` with this complete content:

```markdown
# Tutorial 2: Nested JSON to tables (nested → analysis-ready)

This tutorial shows a practical path from nested JSON to table-shaped data you can work with.

We’ll use two techniques:

1. **Flatten nested JSON into multiple related “tables”** (JSON datasets)
2. **Convert table-like JSON to pandas** via `.to(PandasDataset)` / `.to(PandasModel)`

It also documents the current boundaries of automatic flattening.

## Setup (silence logs + avoid output persistence)

```pycon exec="1" session="t2" source="console"
>>> from omnipy import runtime
>>> runtime.config.root_log.log_to_stdout = False
>>> runtime.config.root_log.log_to_stderr = False
>>> runtime.config.root_log.log_to_file = False
>>> runtime.config.job.output_storage.persist_outputs = 'disabled'
```

## 1) Start with nested JSON

```pycon exec="1" session="t2" source="console"
>>> from omnipy import JsonListOfDictsDataset
>>> nested = JsonListOfDictsDataset({
...   'items': [
...     {'id': 'a', 'meta': {'x': 1, 'y': 2}, 'tags': [{'k': 't', 'v': 1}, {'k': 'u', 'v': 2}]},
...     {'id': 'b', 'meta': {'x': 3, 'y': 4}, 'tags': []},
...   ]
... })
>>> nested
```

```pycon exec="1" session="t2" result="console" html="true"
>>> print(nested._docs())
```

## 2) Flatten into related datasets

```pycon exec="1" session="t2" source="console"
>>> from omnipy.components.json.flows import flatten_nested_json
>>> flat = flatten_nested_json.run(nested)
>>> sorted(flat.to_data().keys())
```

The result is a JSON dataset with multiple “tables”:

- `items` (scalar columns)
- `items.meta` (nested object expanded)
- `items.tags` (nested list expanded)

```pycon exec="1" session="t2" source="console"
>>> flat
```

```pycon exec="1" session="t2" result="console" html="true"
>>> print(flat._docs())
```

## 3) Convert to pandas where it fits

If a dataset is already table-shaped, convert it directly:

```pycon exec="1" session="t2" source="console"
>>> from omnipy import PandasDataset
>>> pandas = flat.to(PandasDataset)
>>> pandas
```

```pycon exec="1" session="t2" result="console" html="true"
>>> print(pandas._docs())
```

## Current boundaries (what can be hard)

- Deeply irregular structures (records with different nesting at different levels)
- Keys that collide when flattened
- Mixed lists (sometimes dicts, sometimes scalars)

When flattening doesn’t produce what you want, treat it as a **parsing problem**: define a clearer
target shape and parse/transform toward it.

For background, see: [Parse, don't validate](../parse_dont_validate.md)

## What you learned

- How to flatten nested JSON into related datasets with `flatten_nested_json.run(...)`
- How to convert table-like JSON datasets to pandas with `.to(PandasDataset)`

## Common pitfalls

- Assuming flattening always yields a single table. Real nested JSON often yields *multiple* related
  tables.

## Next steps

- [Tutorial 3: Batch processing with Dataset](03-dataset-batch.md)
```

- [ ] **Step 7.1: Create `docs/tutorials/02-json-to-tables.md`**

Add the file exactly as above.

- [ ] **Step 7.2: Verify MkDocs build**

Run: `uv run --all-groups mkdocs build`

Expected: exit code 0.

- [ ] **Step 7.3: Commit**

```bash
git add docs/tutorials/02-json-to-tables.md
git commit -m "docs: add tutorial 2 on nested JSON to tables"
```

---

## Task 8: Tutorial 3 — Batch processing with Dataset (`docs/tutorials/03-dataset-batch.md`)

**Files:**
- Create: `docs/tutorials/03-dataset-batch.md`

Create `docs/tutorials/03-dataset-batch.md` with this complete content:

```markdown
# Tutorial 3: Batch processing with Dataset (no for-loops)

This tutorial shows how `Dataset` lets you apply a transformation across many items without writing
loops, while keeping typed guarantees.

## Setup (silence logs + avoid output persistence)

```pycon exec="1" session="t3" source="console"
>>> from omnipy import runtime
>>> runtime.config.root_log.log_to_stdout = False
>>> runtime.config.root_log.log_to_stderr = False
>>> runtime.config.root_log.log_to_file = False
>>> runtime.config.job.output_storage.persist_outputs = 'disabled'
```

## 1) A dataset is a mapping from names → typed models

```pycon exec="1" session="t3" source="console"
>>> from omnipy import Dataset, Model
>>> numbers = Dataset[Model[int]]({'a': 1, 'b': 2, 'c': 10})
>>> numbers
```

```pycon exec="1" session="t3" result="console" html="true"
>>> print(numbers._docs())
```

## 2) Map a task over all items (one line)

`TaskTemplate(iterate_over_data_files=True)` turns a per-item function into a dataset-mapping task.

```pycon exec="1" session="t3" source="console"
>>> from omnipy import TaskTemplate
>>> @TaskTemplate(iterate_over_data_files=True)
... def inc(x: int) -> int:
...     return x + 1
>>> out = inc.run(numbers)
>>> out.to_data()
```

## 3) Hierarchical datasets (batch over groups)

Datasets can contain datasets. Here we apply the same task to each group without writing loops,
using `Dataset.do(...)` as a convenient mapping helper.

```pycon exec="1" session="t3" source="console"
>>> Inner = Dataset[Model[int]]
>>> Outer = Dataset[Inner]
>>> grouped = Outer({'group1': {'a': 1, 'b': 2}, 'group2': {'a': 10}})
>>> grouped
```

```pycon exec="1" session="t3" result="console" html="true"
>>> print(grouped._docs())
```

```pycon exec="1" session="t3" source="console"
>>> grouped_out = grouped.do(inc.run)
>>> grouped_out.to_data()
```

## What you learned

- A `Dataset` is a typed mapping of many items
- `TaskTemplate(iterate_over_data_files=True)` maps a task across all items without loops
- `Dataset` can be hierarchical, and you can map across groups with `.do(...)`

## Common pitfalls

- Trying to map a task directly over a dataset-of-datasets with `iterate_over_data_files=True`.
  Instead, map at the right level (e.g. `grouped.do(inc.run)`).

## Next steps

- Revisit [Tutorial 2: Nested JSON to tables](02-json-to-tables.md) and combine it with batch
  semantics (many JSON payloads → many tables).
```

- [ ] **Step 8.1: Create `docs/tutorials/03-dataset-batch.md`**

Add the file exactly as above.

- [ ] **Step 8.2: Verify MkDocs build**

Run: `uv run --all-groups mkdocs build`

Expected: exit code 0.

- [ ] **Step 8.3: Commit**

```bash
git add docs/tutorials/03-dataset-batch.md
git commit -m "docs: add tutorial 3 on dataset batch processing"
```

---

## Task 9: Thin redirect stubs for moved/legacy pages

**Files:**
- Modify: `docs/data_models.md`
- Modify: `docs/python_typing.md`

### Redirect stub: `docs/data_models.md`

Replace the entire file with:

```markdown
# Data models (moved)

This page has been reorganized as part of the Phase 0 docs overhaul.

Start here:

- [10-minute Quickstart](start/quickstart.md)
- [Tutorial 1: Interactive safety](tutorials/01-interactive-safety.md)

If you were looking for background on parsing strategy, see:

- [Parse, don't validate](parse_dont_validate.md)
```

### Redirect stub: `docs/python_typing.md`

Replace the entire file with:

```markdown
# Python typing (moved)

This page will be reintroduced under **Learn** in a later phase.

For now, start here:

- [Install](start/install.md)
- [10-minute Quickstart](start/quickstart.md)
- [Tutorials](tutorials/01-interactive-safety.md)
```

- [ ] **Step 9.1: Replace `docs/data_models.md` with stub**

Paste the stub content above.

- [ ] **Step 9.2: Replace `docs/python_typing.md` with stub**

Paste the stub content above.

- [ ] **Step 9.3: Verify MkDocs build**

Run: `uv run --all-groups mkdocs build`

Expected: exit code 0.

- [ ] **Step 9.4: Commit**

```bash
git add docs/data_models.md docs/python_typing.md
git commit -m "docs: add redirect stubs for moved pages"
```

---

## Task 10: Plan self-review (against spec)

Run this self-review before handing off for execution.

- [ ] **Step 10.1: Spec coverage check (Phase 0)**

Confirm the plan includes:

- Landing page: value prop, 3 bullets, code snippet with visible output, CTAs, compare strip, JSON→tables caveat link, and a neutral v2 placeholder.
- Install page extracted/updated from readme (Python version constraint, install command, next link).
- Quickstart: install → model parse → interactive safety → conversion preview → dataset mapping.
- Tutorials 1–3: runnable, each shows `_docs()` output; Tutorial 2 links to `parse_dont_validate.md`; Tutorials are neutral tone.
- Nav updated in `mkdocs.yml` to “Start here” + “Tutorials”; `parse_dont_validate.md` preserved and linked.
- Redirect stubs for moved `data_models.md` and `python_typing.md`.

- [ ] **Step 10.2: Placeholder scan**

Search the plan-created docs for placeholders:

Run: `rg -n "\b(TBD|TODO|coming soon)\b" docs/start docs/tutorials docs/index.md docs/data_models.md docs/python_typing.md`

Expected: no unlabelled roadmap claims.

- [ ] **Step 10.3: Final verification build**

Run: `uv run --all-groups mkdocs build`

Expected: exit code 0.

No commit for this task.

---

## Execution notes

- Prefer `markdown-exec` runnable blocks (`pycon exec="1"`) and keep each tutorial’s examples in a single named `session` so outputs accumulate.
- Keep tone neutral (no superhero voice).
- Use the correct config naming: `runtime.config.data.model.interactive` and call it “interactive mode” or “interactive rollback.” Avoid the outdated `interactive_mode` name.
