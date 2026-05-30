# Omnipy Docs Phase 1 (Core story: Features + How-tos + Compute + Tutorial 5 + Compare) — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Complete Phase 1 of the Omnipy online docs overhaul by replacing stub pages with content that tells the “core story”: why Omnipy exists, how to use Models/Datasets/`.to()`/Display/Compute, and how to parse domain tabular formats.

**Architecture:** Keep the existing MkDocs Material site + IA intact; replace Phase 0 “coming soon” stubs with concise, example-first pages. Prefer runnable docs examples via `markdown-exec` (`pycon exec="1"`) but avoid executing UI-heavy methods (`browse()`) during `mkdocs build`.

**Tech Stack:** MkDocs Material; `markdown-exec`; `pymdownx.snippets` (already enabled) for shared includes; `uv` for running `mkdocs build`.

**Constraints (from spec + user):**

- Maturity labels: **Now**, **Preview**, **Planned** (use consistently).
- Correct config path: `runtime.config.data.model.interactive` (NOT `interactive_mode`).
- Use `markdown-exec` (`pycon exec="1"`) for runnable examples.
- No superhero theme.
- Feature overview pages must follow template: (1) What it solves, (2) The idea, (3) Example, (4) Output/display, (5) When to use/when not, (6) Gotchas, (7) Links.
- Preserve these legacy docs pages as-is (do not edit):
  - `docs/data_models.md`
  - `docs/python_typing.md`
  - `docs/parse_dont_validate.md`

---

## File structure (create/modify map)

**Create:**
- `docs/_includes/.gitkeep`
- `docs/_includes/maturity_labels.md` — shared definitions for Now/Preview/Planned
- `docs/_includes/pycon_setup.md` — shared `markdown-exec` setup (silence logs + disable output persistence)

**Modify (Phase 1 pages):**

Feature overview pages:
- `docs/features/continuous-validation.md`
- `docs/features/snapshots-rollbacks.md`
- `docs/features/conversions.md`
- `docs/features/datasets.md`
- `docs/features/display.md`
- `docs/features/components-catalog.md`
- `docs/features/compute-dataflows.md`
- `docs/features/engines.md`

How-to guides (Models):
- `docs/howto/models/define-models.md`
- `docs/howto/models/parse-strategies.md`
- `docs/howto/models/conversions.md`
- `docs/howto/models/display-inspection.md`
- `docs/howto/models/chainx.md`
- `docs/howto/models/parametrized-models.md`
- `docs/howto/models/complex-models.md` (use this page for the “Pydantic compatibility trust-builder” content)

How-to guides (Datasets):
- `docs/howto/datasets/basics.md`
- `docs/howto/datasets/hierarchies-blueprints.md`

How-to guides (Dataflows / Compute):
- `docs/howto/dataflows/tasks.md`
- `docs/howto/dataflows/flows.md`
- `docs/howto/dataflows/running-flows.md`
- `docs/howto/dataflows/modifiers.md`
- `docs/howto/dataflows/mapping-over-datasets.md`
- `docs/howto/dataflows/engines-overview.md`

Tutorials:
- `docs/tutorials/05-domain-formats.md` (Tutorial 5)

Learn:
- `docs/learn/comparisons.md` (Compare / “When Omnipy vs alternatives”)

Formats/components guide:
- `docs/howto/components/domain-formats.md` (Domain format parsing guide)

---

## Global verification commands (use throughout)

- Build docs site (executes `markdown-exec` blocks):
  - Run: `uv run --all-groups mkdocs build`
  - Expected: exit code 0

- Search for wrong config name in the *new/edited* Phase 1 pages:
  - Run:
    - `rg -n "interactive_mode" docs/features docs/howto docs/tutorials/05-domain-formats.md docs/learn/comparisons.md docs/_includes`
  - Expected: no matches
  - Note: legacy pages are allowed to contain `interactive_mode` (they are preserved as-is).

---

## Task 0: Preflight (baseline build)

**Files:** none

- [ ] **Step 0.1: Confirm working tree is clean enough**

Run: `git status --porcelain=v1`

Expected: no unexpected modified tracked files. (Avoid committing local-only files like `.envrc`, `_cache/`, `outputs/`.)

- [ ] **Step 0.2: Baseline docs build**

Run: `uv run --all-groups mkdocs build`

Expected: exit code 0.

No commit for this task.

---

## Task 1: Add shared includes for maturity labels + runnable example setup

**Files:**
- Create: `docs/_includes/.gitkeep`
- Create: `docs/_includes/maturity_labels.md`
- Create: `docs/_includes/pycon_setup.md`

- [ ] **Step 1.1: Create `docs/_includes/.gitkeep`**

Create `docs/_includes/.gitkeep` with:

```text

```

- [ ] **Step 1.2: Create `docs/_includes/maturity_labels.md`**

Create `docs/_includes/maturity_labels.md` with:

```markdown
> [!NOTE]
> **Maturity labels**
> - **Now**: stable, supported, runnable examples — APIs are settled.
> - **Preview**: implemented and usable today, but still evolving — scope/limits are documented; APIs may shift.
> - **Planned**: not yet implemented or publicly usable — describe user value only (no speculative signatures).
```

- [ ] **Step 1.3: Create `docs/_includes/pycon_setup.md`**

Create `docs/_includes/pycon_setup.md` with:

```text
>>> from omnipy import runtime
>>> runtime.config.root_log.log_to_stdout = False
>>> runtime.config.root_log.log_to_stderr = False
>>> runtime.config.root_log.log_to_file = False
>>> runtime.config.job.output_storage.persist_outputs = 'disabled'
```

- [ ] **Step 1.4: Verify MkDocs build**

Run: `uv run --all-groups mkdocs build`

Expected: exit code 0.

- [ ] **Step 1.5: Commit**

```bash
git add docs/_includes/.gitkeep docs/_includes/maturity_labels.md docs/_includes/pycon_setup.md
git commit -m "docs: add shared includes for maturity labels and pycon setup"
```

---

## Task 2: Feature overview — Continuous validation & type mimicking

**Files:**
- Modify: `docs/features/continuous-validation.md`

- [ ] **Step 2.1: Replace `docs/features/continuous-validation.md` with:**

```markdown
# Continuous validation & type mimicking

--8<-- "_includes/maturity_labels.md"

> [!NOTE]
> **Status: Now**

## What it solves

When you parse messy input into a model, you want **two things at once**:

1. a stable, typed shape after parsing, and
2. safety while you keep editing that data.

Omnipy models continuously validate *after* parsing, so a model doesn’t silently drift into an
invalid state.

## The idea

- An Omnipy `Model[T]` parses input into a typed value.
- After parsing, the model **type-mimics** the underlying Python type (e.g. list-like methods for
  `Model[list[int]]`).
- Mutations keep the model validated continuously.

## Example

```pycon exec="1" session="feature_cont_validation" source="console"
>>> from omnipy import Model
--8<-- "_includes/pycon_setup.md"
>>> readings = Model[list[int]]((120, '135', 142.0))
>>> readings
```

## Output / display

```pycon exec="1" session="feature_cont_validation" result="console" html="true"
>>> print(readings._docs())
```

## When to use it / when not

Use it when:

- you mutate parsed data interactively (notebooks, REPL),
- you want type guarantees to survive beyond the parse boundary.

You may not need it when:

- you only validate once and immediately serialize out (a pure “validate then freeze” workflow).

## Gotchas

- **Continuous validation is not the same as rollback.** Rollback behavior is controlled by
  `runtime.config.data.model.interactive` (see the Snapshots & rollbacks feature page).
- Older docs may mention `interactive_mode`; the correct runtime path is
  `runtime.config.data.model.interactive`.

## Links

- Feature: [Snapshots & rollbacks](snapshots-rollbacks.md)
- Tutorial: [Interactive safety](../tutorials/01-interactive-safety.md)
- How-to: [Define Models](../howto/models/define-models.md)
```

- [ ] **Step 2.2: Verify MkDocs build**

Run: `uv run --all-groups mkdocs build`

Expected: exit code 0.

- [ ] **Step 2.3: Commit**

```bash
git add docs/features/continuous-validation.md
git commit -m "docs: write feature overview for continuous validation"
```

---

## Task 3: Feature overview — Snapshots & rollbacks

**Files:**
- Modify: `docs/features/snapshots-rollbacks.md`

- [ ] **Step 3.1: Replace `docs/features/snapshots-rollbacks.md` with:**

```markdown
# Snapshots & rollbacks

--8<-- "_includes/maturity_labels.md"

> [!NOTE]
> **Status: Now**

## What it solves

When you mutate a model and hit a validation error, you want the failure to be loud **and** the
state to remain usable.

Rollback gives you “safe experimentation”: invalid mutations raise immediately and the model can
return to the last valid state.

## The idea

Omnipy can take snapshots of validated model content. When interactive mode is enabled,
invalid mutations can roll back automatically.

The switch is:

- `runtime.config.data.model.interactive = True` (snapshots + rollback)
- `runtime.config.data.model.interactive = False` (no snapshot overhead; no rollback)

## Example

```pycon exec="1" session="feature_rollbacks" source="console"
>>> from omnipy import Model
--8<-- "_includes/pycon_setup.md"
>>> from omnipy import runtime
>>> runtime.config.data.model.interactive = True
>>> xs = Model[list[int]]([1, 2, 3])
>>> before = xs.to_data().copy()
>>> try:
...     xs.append('oops')
... except Exception as err:
...     print(type(err).__name__)
>>> after = xs.to_data()
>>> before == after
True
>>> xs
```

## Output / display

```pycon exec="1" session="feature_rollbacks" result="console" html="true"
>>> print(xs._docs())
```

## When to use it / when not

Use it when:

- you do exploratory edits and want recoverability,
- you prefer “dead programs tell no lies” *and* “keep my last good state.”

Turn it off when:

- you’re running performance-sensitive batch transforms and you can tolerate rebuilding state from
  upstream inputs.

## Gotchas

- Turning interactive mode off does **not** mean “no validation.” Validation still happens; you
  just lose automatic rollback.
- Correct config path: `runtime.config.data.model.interactive`.

## Links

- Feature: [Continuous validation & type mimicking](continuous-validation.md)
- Tutorial: [Interactive safety](../tutorials/01-interactive-safety.md)
```

- [ ] **Step 3.2: Verify MkDocs build**

Run: `uv run --all-groups mkdocs build`

Expected: exit code 0.

- [ ] **Step 3.3: Commit**

```bash
git add docs/features/snapshots-rollbacks.md
git commit -m "docs: write feature overview for snapshots and rollbacks"
```

---

## Task 4: Feature overview — Declarative conversions (`.to()`)

**Files:**
- Modify: `docs/features/conversions.md`

- [ ] **Step 4.1: Replace `docs/features/conversions.md` with:**

```markdown
# Declarative conversions (.to())

--8<-- "_includes/maturity_labels.md"

> [!NOTE]
> **Status: Now**

## What it solves

You often want to move between compatible representations:

- nested JSON → related table-like datasets,
- table-like JSON → pandas,
- model ↔ dataset wrappers.

Omnipy’s `.to()` is the “one obvious way” to ask for a new typed representation.

## The idea

`.to(Target)` is intentionally simple:

- for `Model`: `m.to(TargetModel)` returns `TargetModel(m)`
- for `Dataset`: `d.to(TargetDataset)` returns `TargetDataset(d)`

Conversions work when the target type knows how to parse the source.

## Example

```pycon exec="1" session="feature_to" source="console"
>>> from omnipy import JsonListOfDictsDataset, PandasDataset
--8<-- "_includes/pycon_setup.md"
>>> records = JsonListOfDictsDataset({'rows': [{'id': 'a', 'value': '1'}, {'id': 'b', 'value': 2}]})
>>> records_pd = records.to(PandasDataset)
>>> records_pd
```

## Output / display

```pycon exec="1" session="feature_to" result="console" html="true"
>>> print(records_pd._docs())
```

## When to use it / when not

Use it when:

- you want a repeatable “conversion boundary” instead of ad-hoc conversion glue,
- you want conversions to stay typed and discoverable in code.

Avoid it when:

- you need a conversion that doesn’t exist yet; in that case, treat it as parsing/transform work
  and build the target shape explicitly.

## Gotchas

- Not every pair of types is convertible.
- Avoid writing docs that promise a future “conversion registry” API unless it exists.

## Links

- How-to: [Conversions with .to()](../howto/models/conversions.md)
- Tutorial: [Nested JSON to tables](../tutorials/02-json-to-tables.md)
```

- [ ] **Step 4.2: Verify MkDocs build**

Run: `uv run --all-groups mkdocs build`

Expected: exit code 0.

- [ ] **Step 4.3: Commit**

```bash
git add docs/features/conversions.md
git commit -m "docs: write feature overview for declarative conversions"
```

---

## Task 5: Feature overview — Dataset batch + hierarchies

**Files:**
- Modify: `docs/features/datasets.md`

- [ ] **Step 5.1: Replace `docs/features/datasets.md` with:**

```markdown
# Dataset batch + hierarchies

--8<-- "_includes/maturity_labels.md"

> [!NOTE]
> **Status: Now**

## What it solves

You don’t want your “batch semantics” to be a pile of `for` loops that throw away typing.

Datasets let you treat many items as one typed collection and map operations without losing
structure.

## The idea

- `Dataset[Model[T]]` is a typed mapping from keys (data item names) to values.
- `Dataset` can be hierarchical (datasets of datasets).
- Mapping helpers (like `.do(...)`) let you apply transformations across items.

## Example

```pycon exec="1" session="feature_datasets" source="console"
>>> from omnipy import Dataset, Model
--8<-- "_includes/pycon_setup.md"
>>> xs = Dataset[Model[int]]({'a': '1', 'b': 2.0, 'c': 10})
>>> xs
```

```pycon exec="1" session="feature_datasets" source="console"
>>> ys = xs.do(lambda x: int(x) + 1)
>>> ys.to_data()
```

## Output / display

```pycon exec="1" session="feature_datasets" result="console" html="true"
>>> print(xs._docs())
```

## When to use it / when not

Use it when:

- you have many records/files/IDs and want one typed container,
- you want to keep a stable structure while transforming.

You may not need it when:

- you truly only have one item and no reason to keep a batch container.

## Gotchas

- Decide what the keys mean (file paths, IDs, sample names) and keep them stable.
- If you find yourself nesting three levels deep, consider whether you should restructure the
  hierarchy.

## Links

- Tutorial: [Dataset batch](../tutorials/03-dataset-batch.md)
- How-to: [Working with Datasets](../howto/datasets/basics.md)
- How-to: [Hierarchies & blueprints](../howto/datasets/hierarchies-blueprints.md)
```

- [ ] **Step 5.2: Verify MkDocs build**

Run: `uv run --all-groups mkdocs build`

Expected: exit code 0.

- [ ] **Step 5.3: Commit**

```bash
git add docs/features/datasets.md
git commit -m "docs: write feature overview for datasets"
```

---

## Task 6: Feature overview — Display & visualization

**Files:**
- Modify: `docs/features/display.md`

- [ ] **Step 6.1: Replace `docs/features/display.md` with:**

```markdown
# Display & visualization

--8<-- "_includes/maturity_labels.md"

> [!NOTE]
> **Status: Now**

## What it solves

Nested data is hard to inspect quickly. Omnipy provides display helpers designed for:

- “What do I have?” (fast peek)
- “Show me everything” (full)
- “Open in a browser for scrolling” (browse)
- “Give me a readable docs-style rendering” (`_docs()`)

## The idea

Models and Datasets implement a consistent display surface:

- `peek()` — preview
- `full()` — complete view
- `browse()` — open full view in a browser (best for large outputs)
- `json()` — JSON-focused display when relevant
- `_docs()` — rendered documentation-friendly representation

## Example

```pycon exec="1" session="feature_display" source="console"
>>> from omnipy import Model
--8<-- "_includes/pycon_setup.md"
>>> m = Model[list[int]]((1, '2', 3.0))
>>> m
```

## Output / display

```pycon exec="1" session="feature_display" result="console" html="true"
>>> print(m._docs())
```

## When to use it / when not

Use it when:

- you’re exploring data interactively and want fast visual feedback,
- you want docs examples to show real output.

You may avoid `browse()` in headless contexts (CI, remote servers without a browser).

## Gotchas

- Don’t execute `browse()` in documentation builds; show it as a non-executed snippet.
- Display output depends on detected UI environment (terminal vs Jupyter).

## Links

- How-to: [Display & inspection](../howto/models/display-inspection.md)
- Tutorial: [Nested JSON to tables](../tutorials/02-json-to-tables.md)
```

- [ ] **Step 6.2: Verify MkDocs build**

Run: `uv run --all-groups mkdocs build`

Expected: exit code 0.

- [ ] **Step 6.3: Commit**

```bash
git add docs/features/display.md
git commit -m "docs: write feature overview for display and visualization"
```

---

## Task 7: Feature overview — Components catalog (high-level)

**Files:**
- Modify: `docs/features/components-catalog.md`

- [ ] **Step 7.1: Replace `docs/features/components-catalog.md` with:**

```markdown
# Components catalog (high-level)

--8<-- "_includes/maturity_labels.md"

> [!NOTE]
> **Status: Now**

## What it solves

Omnipy is a collection of interoperating building blocks (“components”) for:

- data models and datasets,
- conversions,
- parsing common content types,
- remote fetching,
- tabular formats.

This page helps you choose a starting point.

## The idea

You usually start from a *source shape* (what you have) and convert into a *target shape*
(what you want):

- **General**: basic models/tasks used across components
- **JSON**: JSON models/datasets + utilities like flattening
- **Nested**: nested-list / nested-dict model utilities for hierarchical content
- **Raw**: bytes/strings and splitting/joining primitives
- **Tables**: row/column table models + TSV/CSV parsers
- **Remote**: typed URL/query models + remote tasks

## Example

```pycon exec="1" session="feature_components" source="console"
>>> from omnipy import JsonListOfDictsDataset
--8<-- "_includes/pycon_setup.md"
>>> data = JsonListOfDictsDataset({'rows': [{'id': 'a', 'x': 1}, {'id': 'b', 'x': 2}]})
>>> data
```

## Output / display

```pycon exec="1" session="feature_components" result="console" html="true"
>>> print(data._docs())
```

## When to use it / when not

Use components when:

- you want conversions that preserve typing across boundaries,
- you want reusable parsing building blocks.

Don’t overfit to components when:

- a plain `Model[T]` is enough — start simple and add structure only when it pays off.

## Gotchas

- Some component areas are deeper than others; when in doubt, start from Tutorials and How-tos.

## Links

- How-to: Components catalog (separate catalog how-to page)
- Feature: [Declarative conversions](conversions.md)
- Tutorial: [Nested JSON to tables](../tutorials/02-json-to-tables.md)
```

- [ ] **Step 7.2: Verify MkDocs build**

Run: `uv run --all-groups mkdocs build`

Expected: exit code 0.

- [ ] **Step 7.3: Commit**

```bash
git add docs/features/components-catalog.md
git commit -m "docs: write feature overview for components catalog"
```

---

## Task 8: Feature overview — Dataflows (Compute): Tasks/Flows/Modifiers

**Files:**
- Modify: `docs/features/compute-dataflows.md`

- [ ] **Step 8.1: Replace `docs/features/compute-dataflows.md` with:**

```markdown
# Dataflows (Compute): Tasks/Flows/Modifiers

--8<-- "_includes/maturity_labels.md"

> [!NOTE]
> **Status: Now**

## What it solves

You want pipeline-like composition without giving up:

- typed inputs/outputs,
- small reusable transformation units,
- a clear scale-up path (local → orchestration).

## The idea

- **Tasks** are typed functions packaged as reusable jobs.
- **Flows** compose tasks into runnable pipelines (Linear, DAG, Func).
- “Modifiers” are job configuration knobs exposed as decorator parameters and via `.refine(...)`
  (name, fixed params, parameter key mapping, iteration over datasets, etc.).

## Example

```pycon exec="1" session="feature_compute" source="console"
>>> from omnipy import TaskTemplate, LinearFlowTemplate
--8<-- "_includes/pycon_setup.md"
>>> @TaskTemplate()
... def plus_one(number: int) -> int:
...     return number + 1
>>> @LinearFlowTemplate(plus_one, plus_one, plus_one)
... def plus_three(number: int) -> int:
...     ...
>>> plus_three.run(10)
13
```

## Output / display

For larger flows, prefer inspecting intermediate model/dataset outputs with `_docs()`.

## When to use it / when not

Use compute when:

- you want reusable transformation units,
- you want to turn notebook code into a repeatable pipeline.

You may skip compute when:

- you only need one transform and no composition.

## Gotchas

- If you call a template like a function outside a flow context, you’ll get a helpful error.
  Use `.run(...)` for templates.
- Keep examples simple and runnable with the local engine.

## Links

- How-to: [Tasks](../howto/dataflows/tasks.md)
- How-to: [Flows](../howto/dataflows/flows.md)
- How-to: [Running flows (local engine)](../howto/dataflows/running-flows.md)
- How-to: [Modifiers](../howto/dataflows/modifiers.md)
```

- [ ] **Step 8.2: Verify MkDocs build**

Run: `uv run --all-groups mkdocs build`

Expected: exit code 0.

- [ ] **Step 8.3: Commit**

```bash
git add docs/features/compute-dataflows.md
git commit -m "docs: write feature overview for compute dataflows"
```

---

## Task 9: Feature overview — Engines & orchestration (honest)

**Files:**
- Modify: `docs/features/engines.md`

- [ ] **Step 9.1: Replace `docs/features/engines.md` with:**

```markdown
# Engines & orchestration

--8<-- "_includes/maturity_labels.md"

> [!NOTE]
> **Status: Preview**
>
> The local engine is **Now**. Prefect orchestration is usable but evolving.

## What it solves

The same Task/Flow code should run:

- locally (fast iteration), and
- under orchestration (scale, scheduling) without rewriting the pipeline.

## The idea

The runtime chooses an engine:

- `local` — runs jobs in-process
- `prefect` — runs jobs via Prefect wrappers

The default engine choice is local.

## Example

```pycon exec="1" session="feature_engines" source="console"
>>> from omnipy import TaskTemplate, runtime
--8<-- "_includes/pycon_setup.md"
>>> runtime.config.engine.choice
'local'
>>> @TaskTemplate()
... def double(x: int) -> int:
...     return x * 2
>>> double.run(21)
42
```

## Output / display

For orchestration engines, prefer using the same `_docs()`-based inspection as you use locally.

## When to use it / when not

Use local when:

- you are developing and iterating.

Consider orchestration when:

- you need scheduling, retries, caching, or scale-out execution.

## Gotchas

- Keep docs examples runnable without external services.
- Orchestration semantics (e.g. caching) are engine-specific.

## Links

- How-to: [Engines overview](../howto/dataflows/engines-overview.md)
- How-to: [Running flows (local engine)](../howto/dataflows/running-flows.md)
- Tutorial: Build a dataflow (Tutorial 4)
```

- [ ] **Step 9.2: Verify MkDocs build**

Run: `uv run --all-groups mkdocs build`

Expected: exit code 0.

- [ ] **Step 9.3: Commit**

```bash
git add docs/features/engines.md
git commit -m "docs: write feature overview for engines and orchestration"
```

---

## Task 10: How-to (Models) — Define models (quick patterns)

**Files:**
- Modify: `docs/howto/models/define-models.md`

- [ ] **Step 10.1: Replace `docs/howto/models/define-models.md` with:**

```markdown
# Define Models

--8<-- "_includes/maturity_labels.md"

> [!NOTE]
> **Status: Now**

This page shows quick, practical patterns for defining Omnipy models.

## Pattern 1: One-off models with `Model[T]`

```pycon exec="1" session="howto_define_models" source="console"
>>> from omnipy import Model
--8<-- "_includes/pycon_setup.md"
>>> ints = Model[list[int]]((1, '2', 3.0))
>>> ints
```

```pycon exec="1" session="howto_define_models" result="console" html="true"
>>> print(ints._docs())
```

## Pattern 2: Named model classes (for reuse)

When you want a reusable type, create a subclass:

```pycon exec="1" session="howto_define_models" source="console"
>>> from omnipy import Model
>>> class Ints(Model[list[int]]):
...     ...
>>> Ints(['1', 2, 3.0]).to_data()
[1, 2, 3]
```

## Pattern 3: Custom parsing ("parse, don’t validate")

Override `_parse_data` to accept messy input and produce a clean typed output.

```pycon exec="1" session="howto_define_models" source="console"
>>> class PosInts(Model[list[int]]):
...     @classmethod
...     def _parse_data(cls, data: list[int]) -> list[int]:
...         return [x for x in data if x > 0]
>>> PosInts([-1, 0, 1, 2]).to_data()
[1, 2]
```

## Common pitfalls

- Confusing the interactive config path: use `runtime.config.data.model.interactive`.

## Links

- Learn: [Parse, don't validate](../../parse_dont_validate.md)
- How-to: [Parse strategies](parse-strategies.md)
- Feature: [Continuous validation & type mimicking](../../features/continuous-validation.md)
```

- [ ] **Step 10.2: Verify MkDocs build**

Run: `uv run --all-groups mkdocs build`

Expected: exit code 0.

- [ ] **Step 10.3: Commit**

```bash
git add docs/howto/models/define-models.md
git commit -m "docs: write how-to for defining models"
```

---

## Task 11: How-to (Models) — Parse strategies (“parse, don’t validate” in practice)

**Files:**
- Modify: `docs/howto/models/parse-strategies.md`

- [ ] **Step 11.1: Replace `docs/howto/models/parse-strategies.md` with:**

```markdown
# Parse strategies

--8<-- "_includes/maturity_labels.md"

> [!NOTE]
> **Status: Now**

This page shows practical strategies for turning messy inputs into stable, typed outputs.

## Strategy A: Let `Model[T]` do the basic coercions

```pycon exec="1" session="howto_parse_strategies" source="console"
>>> from omnipy import Model
--8<-- "_includes/pycon_setup.md"
>>> Model[list[int]]((1, '2', 3.0)).to_data()
[1, 2, 3]
```

## Strategy B: Normalize before typing (when inputs are *really* messy)

Use `_parse_data` to normalize inputs into a cleaner intermediate shape, then let the type handle
the rest.

```pycon exec="1" session="howto_parse_strategies" source="console"
>>> class IntListFromAnything(Model[list[int]]):
...     @classmethod
...     def _parse_data(cls, data):
...         if isinstance(data, str):
...             data = data.replace(',', ' ').split()
...         return data
>>> IntListFromAnything('1, 2  3').to_data()
[1, 2, 3]
```

## Strategy C: “Fail fast” vs “repair”

Omnipy models are parsers. That doesn’t mean you should silently accept everything.

- If repair is safe and obvious (e.g. trimming whitespace), do it.
- If repair is ambiguous (e.g. guessing units), fail fast and require explicit user intent.

## Links

- Learn: [Parse, don't validate](../../parse_dont_validate.md)
- How-to: [Define Models](define-models.md)
```

- [ ] **Step 11.2: Verify MkDocs build**

Run: `uv run --all-groups mkdocs build`

Expected: exit code 0.

- [ ] **Step 11.3: Commit**

```bash
git add docs/howto/models/parse-strategies.md
git commit -m "docs: write how-to for parse strategies"
```

---

## Task 12: How-to (Models) — Conversions with `.to()`

**Files:**
- Modify: `docs/howto/models/conversions.md`

- [ ] **Step 12.1: Replace `docs/howto/models/conversions.md` with:**

```markdown
# Conversions with .to()

--8<-- "_includes/maturity_labels.md"

> [!NOTE]
> **Status: Now**

This page shows the practical `.to(Target)` conversion workflow.

## Convert a dataset to another dataset type

```pycon exec="1" session="howto_to" source="console"
>>> from omnipy import JsonListOfDictsDataset, PandasDataset
--8<-- "_includes/pycon_setup.md"
>>> records = JsonListOfDictsDataset({'rows': [{'id': 'a', 'value': '1'}, {'id': 'b', 'value': 2}]})
>>> records_pd = records.to(PandasDataset)
>>> records_pd.to_data()
[{'id': 'a', 'value': 1}, {'id': 'b', 'value': 2}]
```

## Convert a single model to another model type

```pycon exec="1" session="howto_to" source="console"
>>> from omnipy import JsonListOfDictsModel, PandasModel
>>> one_table = JsonListOfDictsModel([{'id': 'a', 'x': 1}, {'id': 'b', 'x': 3}])
>>> one_table_pd = one_table.to(PandasModel)
>>> one_table_pd
```

## Troubleshooting conversions

- If `.to(Target)` fails: the target likely can’t parse the source shape.
- Use `.to_data()` to inspect the current shape and decide what transform you need.

## Links

- Feature: [Declarative conversions](../../features/conversions.md)
- Tutorial: [Nested JSON to tables](../../tutorials/02-json-to-tables.md)
```

- [ ] **Step 12.2: Verify MkDocs build**

Run: `uv run --all-groups mkdocs build`

Expected: exit code 0.

- [ ] **Step 12.3: Commit**

```bash
git add docs/howto/models/conversions.md
git commit -m "docs: write how-to for conversions with to()"
```

---

## Task 13: How-to (Models) — Display & inspection

**Files:**
- Modify: `docs/howto/models/display-inspection.md`

- [ ] **Step 13.1: Replace `docs/howto/models/display-inspection.md` with:**

```markdown
# Display & inspection

--8<-- "_includes/maturity_labels.md"

> [!NOTE]
> **Status: Now**

This page explains how to inspect Models and Datasets effectively.

## `_docs()` — docs-friendly rendering

```pycon exec="1" session="howto_display" source="console"
>>> from omnipy import Model
--8<-- "_includes/pycon_setup.md"
>>> m = Model[dict[str, list[int]]]({'a': [1, 2], 'b': [3, 4]})
>>> m
```

```pycon exec="1" session="howto_display" result="console" html="true"
>>> print(m._docs())
```

## `peek()` / `full()` / `browse()` (interactive helpers)

These are designed for interactive exploration:

```python
from omnipy import Model

m = Model[list[int]]([1, 2, 3])
m.peek()
m.full()
m.browse()
```

Tip: avoid executing `browse()` in headless contexts.

## Links

- Feature: [Display & visualization](../../features/display.md)
- Tutorial: [Interactive safety](../../tutorials/01-interactive-safety.md)
```

- [ ] **Step 13.2: Verify MkDocs build**

Run: `uv run --all-groups mkdocs build`

Expected: exit code 0.

- [ ] **Step 13.3: Commit**

```bash
git add docs/howto/models/display-inspection.md
git commit -m "docs: write how-to for display and inspection"
```

---

## Task 14: How-to (Models) — ChainX recipes (chained model transformations)

**Files:**
- Modify: `docs/howto/models/chainx.md`

- [ ] **Step 14.1: Replace `docs/howto/models/chainx.md` with:**

```markdown
# ChainX recipes

--8<-- "_includes/maturity_labels.md"

> [!NOTE]
> **Status: Now**

Chain models let you build small, repeatable transformation pipelines.

## Recipe: parse lines → split columns → interpret header row

Omnipy includes ready-made chain-friendly building blocks for table parsing.

```pycon exec="1" session="howto_chainx" source="console"
>>> from omnipy import TsvTableModel
--8<-- "_includes/pycon_setup.md"
>>> tsv = "a\tb\n1\t2\n3\t4\n"
>>> table = TsvTableModel(tsv)
>>> table.to_data()
[{'a': '1', 'b': '2'}, {'a': '3', 'b': '4'}]
```

## Recipe: chain a conversion step explicitly

When a step doesn’t exist as a built-in chain model, use a normal model parse step:

```pycon exec="1" session="howto_chainx" source="console"
>>> from omnipy import Model
>>> ints = Model[list[int]](['1', '2', 3.0])
>>> ints.to_data()
[1, 2, 3]
```

## Limitations

- Chains are best for clear, linear transformations.
- If you need branching, consider compute flows.

## Links

- Feature: [Declarative conversions](../../features/conversions.md)
- How-to: [Tasks](../dataflows/tasks.md)
- Tutorial: [Domain formats via model specs](../../tutorials/05-domain-formats.md)
```

- [ ] **Step 14.2: Verify MkDocs build**

Run: `uv run --all-groups mkdocs build`

Expected: exit code 0.

- [ ] **Step 14.3: Commit**

```bash
git add docs/howto/models/chainx.md
git commit -m "docs: write how-to for ChainX recipes"
```

---

## Task 15: How-to (Models) — Parametrized models (patterns + limitations)

**Files:**
- Modify: `docs/howto/models/parametrized-models.md`

- [ ] **Step 15.1: Replace `docs/howto/models/parametrized-models.md` with:**

```markdown
# Parametrized models

--8<-- "_includes/maturity_labels.md"

> [!NOTE]
> **Status: Now**

Parametrized (generic) models are useful when you want one pattern that works across many inner
types.

## Pattern: a dataset of typed items

The most common “generic” pattern in Omnipy is: `Dataset[Model[T]]`.

```pycon exec="1" session="howto_param_models" source="console"
>>> from omnipy import Dataset, Model
--8<-- "_includes/pycon_setup.md"
>>> ints = Dataset[Model[int]]({'a': '1', 'b': 2, 'c': 3.0})
>>> ints.to_data()
{'a': 1, 'b': 2, 'c': 3}
```

## Pattern: reuse a shape with a different inner type

```pycon exec="1" session="howto_param_models" source="console"
>>> from omnipy import Model
>>> Model[list[str]]([1, '2', 3]).to_data()
['1', '2', '3']
```

## Limitations

- Deeply nested generic types can become hard to debug. Prefer a few named, reusable model classes
  at key boundaries.

## Links

- How-to: [Define Models](define-models.md)
- Feature: [Dataset batch + hierarchies](../../features/datasets.md)
```

- [ ] **Step 15.2: Verify MkDocs build**

Run: `uv run --all-groups mkdocs build`

Expected: exit code 0.

- [ ] **Step 15.3: Commit**

```bash
git add docs/howto/models/parametrized-models.md
git commit -m "docs: write how-to for parametrized models"
```

---

## Task 16: How-to (Models) — Pydantic compatibility (trust-builder)

**Files:**
- Modify: `docs/howto/models/complex-models.md`

- [ ] **Step 16.1: Replace `docs/howto/models/complex-models.md` with:**

```markdown
# Pydantic compatibility

--8<-- "_includes/maturity_labels.md"

> [!NOTE]
> **Status: Now**

Omnipy builds on Pydantic’s model language and adds continuous validation, type-mimicking, datasets,
and compute.

This page explains what carries over and what differs.

## What carries over

If you know Pydantic models, the mental model is familiar:

- fields + types describe a target shape
- parsing/coercion happens at the boundary

## What differs

Omnipy models:

- keep enforcing their type continuously after parsing,
- can type-mimic non-record containers (e.g. list-like models),
- integrate with datasets + flows.

## Example: Pydantic model inside an Omnipy model

```pycon exec="1" session="howto_pyd_compat" source="console"
>>> from omnipy import Model
--8<-- "_includes/pycon_setup.md"
>>> from omnipy.util import pydantic as pyd
>>> class BedRow(pyd.BaseModel):
...     chrom: str
...     start: int
...     end: int
...     name: str | None = None
>>> row = Model[BedRow]({'chrom': 'chr1', 'start': '10', 'end': 20, 'name': None})
>>> row.to_data()
{'chrom': 'chr1', 'start': 10, 'end': 20, 'name': None}
```

## Common pitfalls

- Don’t assume a one-off “validate then mutate freely” model lifecycle. Omnipy is built for
  continuous safety.
- Older Omnipy docs may refer to `interactive_mode`; use
  `runtime.config.data.model.interactive`.

## Links

- Feature: [Continuous validation & type mimicking](../../features/continuous-validation.md)
- Feature: [Snapshots & rollbacks](../../features/snapshots-rollbacks.md)
- Tutorial: [Domain formats via model specs](../../tutorials/05-domain-formats.md)
```

- [ ] **Step 16.2: Verify MkDocs build**

Run: `uv run --all-groups mkdocs build`

Expected: exit code 0.

- [ ] **Step 16.3: Commit**

```bash
git add docs/howto/models/complex-models.md
git commit -m "docs: write pydantic compatibility trust-builder page"
```

---

## Task 17: How-to (Datasets) — Working with Datasets

**Files:**
- Modify: `docs/howto/datasets/basics.md`

- [ ] **Step 17.1: Replace `docs/howto/datasets/basics.md` with:**

```markdown
# Working with Datasets

--8<-- "_includes/maturity_labels.md"

> [!NOTE]
> **Status: Now**

Datasets are typed collections: `Dataset[Model[T]]`.

## Create a dataset

```pycon exec="1" session="howto_datasets" source="console"
>>> from omnipy import Dataset, Model
--8<-- "_includes/pycon_setup.md"
>>> ds = Dataset[Model[int]]({'a': '1', 'b': 2.0})
>>> ds.to_data()
{'a': 1, 'b': 2}
```

## Index and iterate

```pycon exec="1" session="howto_datasets" source="console"
>>> sorted(ds.keys())
['a', 'b']
>>> ds['a']
```

## Map over items

```pycon exec="1" session="howto_datasets" source="console"
>>> ds2 = ds.do(lambda x: int(x) + 10)
>>> ds2.to_data()
{'a': 11, 'b': 12}
```

## Links

- Feature: [Dataset batch + hierarchies](../../features/datasets.md)
- Tutorial: [Dataset batch](../../tutorials/03-dataset-batch.md)
```

- [ ] **Step 17.2: Verify MkDocs build**

Run: `uv run --all-groups mkdocs build`

Expected: exit code 0.

- [ ] **Step 17.3: Commit**

```bash
git add docs/howto/datasets/basics.md
git commit -m "docs: write how-to for working with datasets"
```

---

## Task 18: How-to (Datasets) — Hierarchies & blueprints

**Files:**
- Modify: `docs/howto/datasets/hierarchies-blueprints.md`

- [ ] **Step 18.1: Replace `docs/howto/datasets/hierarchies-blueprints.md` with:**

```markdown
# Hierarchies & blueprints

--8<-- "_includes/maturity_labels.md"

> [!NOTE]
> **Status: Now**

Datasets can contain datasets. This is useful when your data is grouped (e.g. samples → runs →
files).

## Hierarchical dataset example

```pycon exec="1" session="howto_ds_hier" source="console"
>>> from omnipy import Dataset, Model
--8<-- "_includes/pycon_setup.md"
>>> Inner = Dataset[Model[int]]
>>> Outer = Dataset[Inner]
>>> grouped = Outer({'group1': {'a': 1, 'b': 2}, 'group2': {'a': 10}})
>>> grouped.to_data()
{'group1': {'a': 1, 'b': 2}, 'group2': {'a': 10}}
```

## Map across groups

```pycon exec="1" session="howto_ds_hier" source="console"
>>> out = grouped.do(lambda ds: ds.do(lambda x: int(x) + 1))
>>> out.to_data()
{'group1': {'a': 2, 'b': 3}, 'group2': {'a': 11}}
```

## Notes on “blueprints”

If you find yourself repeatedly building the same nested structure, treat the *structure* as a
reusable blueprint: define the dataset types (`Inner`, `Outer`) once and reuse them.

## Links

- How-to: [Working with Datasets](basics.md)
- How-to: [Mapping Tasks/Flows over Datasets](../dataflows/mapping-over-datasets.md)
```

- [ ] **Step 18.2: Verify MkDocs build**

Run: `uv run --all-groups mkdocs build`

Expected: exit code 0.

- [ ] **Step 18.3: Commit**

```bash
git add docs/howto/datasets/hierarchies-blueprints.md
git commit -m "docs: write how-to for dataset hierarchies"
```

---

## Task 19: How-to (Compute) — Tasks

**Files:**
- Modify: `docs/howto/dataflows/tasks.md`

- [ ] **Step 19.1: Replace `docs/howto/dataflows/tasks.md` with:**

```markdown
# Tasks

--8<-- "_includes/maturity_labels.md"

> [!NOTE]
> **Status: Now**

Tasks are typed transformation units built from Python functions.

## Define a task

```pycon exec="1" session="howto_tasks" source="console"
>>> from omnipy import TaskTemplate
--8<-- "_includes/pycon_setup.md"
>>> @TaskTemplate()
... def plus_one(number: int) -> int:
...     return number + 1
>>> plus_one.run(10)
11
```

## Refine a task (a common “modifier”)

Use `.refine(...)` to adapt a template without rewriting the function:

```pycon exec="1" session="howto_tasks" source="console"
>>> @TaskTemplate()
... def plus_other(number: int, other: int) -> int:
...     return number + other
>>> plus_one_again = plus_other.refine(name='plus_one', fixed_params={'other': 1})
>>> plus_one_again.run(10)
11
```

## Links

- How-to: [Modifiers](modifiers.md)
- How-to: [Mapping Tasks/Flows over Datasets](mapping-over-datasets.md)
- Feature: [Dataflows (Compute)](../../features/compute-dataflows.md)
```

- [ ] **Step 19.2: Verify MkDocs build**

Run: `uv run --all-groups mkdocs build`

Expected: exit code 0.

- [ ] **Step 19.3: Commit**

```bash
git add docs/howto/dataflows/tasks.md
git commit -m "docs: write how-to for compute tasks"
```

---

## Task 20: How-to (Compute) — Flows (Linear vs DAG vs Func)

**Files:**
- Modify: `docs/howto/dataflows/flows.md`

- [ ] **Step 20.1: Replace `docs/howto/dataflows/flows.md` with:**

```markdown
# Flows

--8<-- "_includes/maturity_labels.md"

> [!NOTE]
> **Status: Now**

Flows compose tasks into runnable pipelines.

## Linear flows

Linear flows run tasks in a fixed sequence.

```pycon exec="1" session="howto_flows" source="console"
>>> from omnipy import TaskTemplate, LinearFlowTemplate
--8<-- "_includes/pycon_setup.md"
>>> @TaskTemplate()
... def plus_one(number: int) -> int:
...     return number + 1
>>> @LinearFlowTemplate(plus_one, plus_one)
... def plus_two(number: int) -> int:
...     ...
>>> plus_two.run(10)
12
```

## DAG flows

DAG flows connect tasks by matching keys in dictionaries.

```pycon exec="1" session="howto_flows" source="console"
>>> from omnipy import DagFlowTemplate
>>> @TaskTemplate()
... def make_inputs() -> dict[str, int]:
...     return {'number': 21}
>>> @TaskTemplate()
... def double(number: int) -> int:
...     return number * 2
>>> @DagFlowTemplate(make_inputs, double)
... def my_dag() -> int:
...     ...
>>> my_dag.run()
42
```

## Func flows

Func flows are useful when you want to write control flow explicitly.

```pycon exec="1" session="howto_flows" source="console"
>>> from omnipy import FuncFlowTemplate
>>> @FuncFlowTemplate()
... def repeat_plus_one(number: int, n: int) -> int:
...     for _ in range(n):
...         number = plus_one(number=number)
...     return number
>>> repeat_plus_one.run(0, 3)
3
```

## Links

- How-to: [Running flows](running-flows.md)
- How-to: [Modifiers](modifiers.md)
```

- [ ] **Step 20.2: Verify MkDocs build**

Run: `uv run --all-groups mkdocs build`

Expected: exit code 0.

- [ ] **Step 20.3: Commit**

```bash
git add docs/howto/dataflows/flows.md
git commit -m "docs: write how-to for compute flows"
```

---

## Task 21: How-to (Compute) — Running flows (local engine)

**Files:**
- Modify: `docs/howto/dataflows/running-flows.md`

- [ ] **Step 21.1: Replace `docs/howto/dataflows/running-flows.md` with:**

```markdown
# Running flows

--8<-- "_includes/maturity_labels.md"

> [!NOTE]
> **Status: Now**

This page shows the “runnable path” for flows using the local engine.

## Run a flow template

Flow templates run via `.run(...)`.

```pycon exec="1" session="howto_run_flows" source="console"
>>> from omnipy import TaskTemplate, LinearFlowTemplate
--8<-- "_includes/pycon_setup.md"
>>> @TaskTemplate()
... def plus_one(number: int) -> int:
...     return number + 1
>>> @LinearFlowTemplate(plus_one, plus_one, plus_one)
... def plus_three(number: int) -> int:
...     ...
>>> plus_three.run(10)
13
```

## Apply a flow and call it

`.apply()` returns a runnable job object.

```pycon exec="1" session="howto_run_flows" source="console"
>>> flow = plus_three.apply()
>>> flow(10)
13
```

## Links

- How-to: [Engines overview](engines-overview.md)
- Feature: [Engines & orchestration](../../features/engines.md)
```

- [ ] **Step 21.2: Verify MkDocs build**

Run: `uv run --all-groups mkdocs build`

Expected: exit code 0.

- [ ] **Step 21.3: Commit**

```bash
git add docs/howto/dataflows/running-flows.md
git commit -m "docs: write how-to for running flows"
```

---

## Task 22: How-to (Compute) — Modifiers

**Files:**
- Modify: `docs/howto/dataflows/modifiers.md`

- [ ] **Step 22.1: Replace `docs/howto/dataflows/modifiers.md` with:**

```markdown
# Modifiers

--8<-- "_includes/maturity_labels.md"

> [!NOTE]
> **Status: Now**

Modifiers are configuration knobs for tasks and flows.

Common modifier patterns:

- naming: `name='...'`
- fixed parameters: `fixed_params={...}`
- parameter key mapping: `param_key_map={...}`
- result key wrapping (DAG-friendly): `result_key='...'`
- iteration over datasets: `iterate_over_data_files=True`

## Example: rename parameters with `param_key_map`

```pycon exec="1" session="howto_modifiers" source="console"
>>> from omnipy import TaskTemplate
--8<-- "_includes/pycon_setup.md"
>>> @TaskTemplate()
... def plus_other(number: int, other: int) -> int:
...     return number + other
>>> plus_x = plus_other.refine(name='plus_x', param_key_map={'other': 'x'})
>>> plus_x.run(number=1, x=2)
3
```

## Example: make a task return a dict (DAG-friendly)

```pycon exec="1" session="howto_modifiers" source="console"
>>> plus_one_dict = (plus_other.refine(name='plus_one', fixed_params={'other': 1})
...                           .refine(result_key='number'))
>>> plus_one_dict.run(number=10)
{'number': 11}
```

## Links

- How-to: [Tasks](tasks.md)
- How-to: [Flows](flows.md)
```

- [ ] **Step 22.2: Verify MkDocs build**

Run: `uv run --all-groups mkdocs build`

Expected: exit code 0.

- [ ] **Step 22.3: Commit**

```bash
git add docs/howto/dataflows/modifiers.md
git commit -m "docs: write how-to for compute modifiers"
```

---

## Task 23: How-to (Compute) — Mapping Tasks/Flows over Datasets

**Files:**
- Modify: `docs/howto/dataflows/mapping-over-datasets.md`

- [ ] **Step 23.1: Replace `docs/howto/dataflows/mapping-over-datasets.md` with:**

```markdown
# Mapping Tasks/Flows over Datasets

--8<-- "_includes/maturity_labels.md"

> [!NOTE]
> **Status: Now**

This page shows two mapping styles:

1) dataset-native mapping with `Dataset.do(...)`, and
2) compute mapping with `TaskTemplate(iterate_over_data_files=True)`.

## Map with `Dataset.do(...)`

```pycon exec="1" session="howto_map" source="console"
>>> from omnipy import Dataset, Model
--8<-- "_includes/pycon_setup.md"
>>> xs = Dataset[Model[int]]({'a': '1', 'b': 2.0})
>>> xs.do(lambda x: int(x) + 1).to_data()
{'a': 2, 'b': 3}
```

## Map with `iterate_over_data_files=True`

```pycon exec="1" session="howto_map" source="console"
>>> from omnipy import TaskTemplate
>>> @TaskTemplate(iterate_over_data_files=True)
... def inc(x: int) -> int:
...     return x + 1
>>> inc.run(xs).to_data()
{'a': 2, 'b': 3}
```

## Links

- How-to: [Tasks](tasks.md)
- How-to: [Working with Datasets](../datasets/basics.md)
```

- [ ] **Step 23.2: Verify MkDocs build**

Run: `uv run --all-groups mkdocs build`

Expected: exit code 0.

- [ ] **Step 23.3: Commit**

```bash
git add docs/howto/dataflows/mapping-over-datasets.md
git commit -m "docs: write how-to for mapping over datasets"
```

---

## Task 24: How-to (Compute) — Engines overview

**Files:**
- Modify: `docs/howto/dataflows/engines-overview.md`

- [ ] **Step 24.1: Replace `docs/howto/dataflows/engines-overview.md` with:**

```markdown
# Engines overview

--8<-- "_includes/maturity_labels.md"

> [!NOTE]
> **Status: Preview**
>
> Local engine is **Now**. Prefect orchestration is usable but evolving.

## What an engine is

An engine is how tasks/flows are executed.

The runtime has two engine objects wired in:

- local runner
- prefect engine

and an engine choice:

```pycon exec="1" session="howto_engines" source="console"
>>> from omnipy import runtime
--8<-- "_includes/pycon_setup.md"
>>> runtime.config.engine.choice
'local'
```

## Choosing an engine

```python
from omnipy import runtime

runtime.config.engine.choice = 'local'
runtime.config.engine.choice = 'prefect'
```

Keep docs examples runnable without external services; prefer local in examples.

## Links

- Feature: [Engines & orchestration](../../features/engines.md)
- How-to: [Running flows](running-flows.md)
```

- [ ] **Step 24.2: Verify MkDocs build**

Run: `uv run --all-groups mkdocs build`

Expected: exit code 0.

- [ ] **Step 24.3: Commit**

```bash
git add docs/howto/dataflows/engines-overview.md
git commit -m "docs: write how-to for engines overview"
```

---

## Task 25: Tutorial 5 — Domain tabular formats (BED/GFF) via model specs

**Files:**
- Modify: `docs/tutorials/05-domain-formats.md`

- [ ] **Step 25.1: Replace `docs/tutorials/05-domain-formats.md` with:**

```markdown
# Tutorial 5: Domain tabular formats (BED/GFF) via model specs

--8<-- "_includes/maturity_labels.md"

> [!NOTE]
> **Status: Now**
>
> This tutorial focuses on row-based parsing using model specs. Column-based validation is **Preview**.

Life science formats (BED, GFF, …) are often “just TSV with conventions” — until they aren’t.
The goal is to build a robust parsing boundary that turns rows into typed records.

## What you’ll build

- parse a BED-like TSV string into rows,
- convert rows into typed records using a model spec,
- convert to a table-friendly representation.

## Setup

```pycon exec="1" session="tutorial5" source="console"
--8<-- "_includes/pycon_setup.md"
```

## 1) Start with a BED-like file

```pycon exec="1" session="tutorial5" source="console"
>>> bed = "chrom\tstart\tend\tname\nchr1\t10\t20\tgeneA\nchr2\t5\t9\tgeneB\n"
>>> bed
```

## 2) Parse to a table model

```pycon exec="1" session="tutorial5" source="console"
>>> from omnipy import TsvTableModel
>>> table = TsvTableModel(bed)
>>> table.to_data()
```

## 3) Define a model spec for one row

Use a Pydantic-style record model as the row spec.

```pycon exec="1" session="tutorial5" source="console"
>>> from omnipy.util import pydantic as pyd
>>> class BedRow(pyd.BaseModel):
...     chrom: str
...     start: int
...     end: int
...     name: str | None = None
```

## 4) Parse rows into typed records

```pycon exec="1" session="tutorial5" source="console"
>>> from omnipy import Model
>>> rows = Model[list[BedRow]](table.to_data())
>>> rows.to_data()
```

## 5) Convert to a pandas-friendly table (optional)

```pycon exec="1" session="tutorial5" source="console"
>>> from omnipy import RowWiseTableWithColNamesModel, PandasModel
>>> as_table = RowWiseTableWithColNamesModel(rows.to_data())
>>> df = as_table.to(PandasModel)
>>> df.to_data()
```

## What you learned

- How to parse domain tabular text into a row-wise table model.
- How to define a typed row spec and parse rows into typed records.

## Common pitfalls

- Row-wise parsing can be slightly slower than vectorized approaches. Use it at the boundary for
  correctness, then convert to faster representations.

## Next steps

- How-to: [Domain format parsing guide](../howto/components/domain-formats.md)
- Feature: [Declarative conversions](../features/conversions.md)
```

- [ ] **Step 25.2: Verify MkDocs build (exec tutorial)**

Run: `uv run --all-groups mkdocs build`

Expected: exit code 0.

- [ ] **Step 25.3: Commit**

```bash
git add docs/tutorials/05-domain-formats.md
git commit -m "docs: write tutorial 5 on domain tabular formats"
```

---

## Task 26: Compare page — “When Omnipy vs alternatives” (examples-first)

**Files:**
- Modify: `docs/learn/comparisons.md`

- [ ] **Step 26.1: Replace `docs/learn/comparisons.md` with:**

```markdown
# When Omnipy vs alternatives

--8<-- "_includes/maturity_labels.md"

> [!NOTE]
> **Status: Now**

This page is factual and examples-first. It doesn’t “win arguments”; it helps you choose.

## When `pydantic + pandas + requests` is enough

Use the usual stack when:

- you have a stable schema,
- you validate once at the boundary,
- you don’t need batch/hierarchy semantics beyond simple loops.

## When Omnipy pays off

Omnipy is most useful when you need **all** of the following in one place:

- continuous safety while you mutate parsed data,
- repeatable typed conversions (`.to(...)`) across representations,
- batch semantics over hierarchical collections,
- a scale-up path from local to orchestration.

## Example 1: continuous safety while editing

```pycon exec="1" session="compare" source="console"
>>> from omnipy import Model
--8<-- "_includes/pycon_setup.md"
>>> xs = Model[list[int]]([1, 2, 3])
>>> try:
...     xs.append('oops')
... except Exception as err:
...     print(type(err).__name__)
>>> xs.to_data()
[1, 2, 3]
```

## Example 2: nested JSON → related tables

```pycon exec="1" session="compare" source="console"
>>> from omnipy import JsonListOfDictsDataset
>>> from omnipy.components.json.flows import flatten_nested_json
>>> nested = JsonListOfDictsDataset({'items': [{'id': 'a', 'meta': {'x': 1}}, {'id': 'b', 'meta': {'x': 2}}]})
>>> flat = flatten_nested_json.run(nested)
>>> sorted(flat.to_data().keys())
['items', 'items.meta']
```

## Example 3: batch semantics without writing loops

```pycon exec="1" session="compare" source="console"
>>> from omnipy import Dataset, Model
>>> ds = Dataset[Model[int]]({'a': '1', 'b': 2.0})
>>> ds.do(lambda x: int(x) + 100).to_data()
{'a': 101, 'b': 102}
```

## Comparisons (quick map)

- **Pydantic:** shared model language; Omnipy adds continuous safety and dataset/compute.
- **pandas:** great for tables; Omnipy helps you *get to* tables from messy nested inputs and keep
  typed boundaries.
- **Prefect/Dagster:** orchestration; Omnipy focuses on typed data boundaries and conversions.
- **Snakemake/Nextflow:** file-centric pipelines; Omnipy focuses on structure *inside* files.

## Links

- Start: [10-minute Quickstart](../start/quickstart.md)
- Tutorials: [Interactive safety](../tutorials/01-interactive-safety.md),
  [Nested JSON to tables](../tutorials/02-json-to-tables.md),
  [Dataset batch](../tutorials/03-dataset-batch.md)
- Feature: [Dataflows (Compute)](../features/compute-dataflows.md)
```

- [ ] **Step 26.2: Verify MkDocs build**

Run: `uv run --all-groups mkdocs build`

Expected: exit code 0.

- [ ] **Step 26.3: Commit**

```bash
git add docs/learn/comparisons.md
git commit -m "docs: write comparisons page for when omnipy vs alternatives"
```

---

## Task 27: Domain format parsing guide (custom formats mental model)

**Files:**
- Modify: `docs/howto/components/domain-formats.md`

- [ ] **Step 27.1: Replace `docs/howto/components/domain-formats.md` with:**

```markdown
# Domain format parsing guide

--8<-- "_includes/maturity_labels.md"

> [!NOTE]
> **Status: Now**

This guide explains how model-based tabular parsing works for custom, domain-specific formats.

## The core pattern

1) parse raw text into rows/columns,
2) map rows into typed records,
3) convert to the representation you want (tables/pandas/datasets).

## Start from a TSV-like parser

```pycon exec="1" session="domain_formats" source="console"
--8<-- "_includes/pycon_setup.md"
>>> from omnipy import TsvTableModel
>>> text = "a\tb\n1\t2\n"
>>> TsvTableModel(text).to_data()
[{'a': '1', 'b': '2'}]
```

## Add a typed row spec

```pycon exec="1" session="domain_formats" source="console"
>>> from omnipy.util import pydantic as pyd
>>> class Row(pyd.BaseModel):
...     a: int
...     b: int
>>> from omnipy import Model
>>> typed = Model[list[Row]](TsvTableModel(text).to_data())
>>> typed.to_data()
[{'a': 1, 'b': 2}]
```

## Notes on extending to real formats

- Add comment skipping and header detection as explicit parse steps.
- Keep “repair” logic local and well-documented.
- Prefer small composable steps over one monolithic parser.

## Links

- Tutorial: [Domain formats via model specs](../../tutorials/05-domain-formats.md)
- How-to: [ChainX recipes](../models/chainx.md)
```

- [ ] **Step 27.2: Verify MkDocs build**

Run: `uv run --all-groups mkdocs build`

Expected: exit code 0.

- [ ] **Step 27.3: Commit**

```bash
git add docs/howto/components/domain-formats.md
git commit -m "docs: write domain format parsing guide"
```

---

## Task 28: Final Phase 1 verification sweep

**Files:** none

- [ ] **Step 28.1: Verify docs build (full)**

Run: `uv run --all-groups mkdocs build`

Expected: exit code 0.

- [ ] **Step 28.2: Verify config-path correctness in Phase 1 pages**

Run:

```bash
rg -n "interactive_mode" docs/features docs/howto docs/tutorials/05-domain-formats.md docs/learn/comparisons.md docs/_includes
```

Expected: no matches.

- [ ] **Step 28.3: Placeholder scan (Phase 1 pages)**

Run:

```bash
rg -n "\b(coming soon|TBD|TODO)\b" docs/features docs/howto docs/tutorials/05-domain-formats.md docs/learn/comparisons.md
```

Expected: no matches.

- [ ] **Step 28.4: Link validation sweep (strict build)**

Run:

```bash
uv run --all-groups mkdocs build --strict
```

Expected: exit code 0 (no unresolved-link warnings).

No commit for this task.
