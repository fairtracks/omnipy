# Omnipy Docs Phase 0 (Landing + Start + Tutorials 1–3) — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement Phase 0 of the approved docs redesign spec: a compelling landing page, Start pages (Install + 10-minute Quickstart), Tutorials 1–3, updated navigation, and thin redirect stubs.

**Architecture:** Keep MkDocs Material setup intact, add new pages under `docs/start/` and `docs/tutorials/`, update `mkdocs.yml` `nav:` to provide the Phase 0 “Start here” and “Tutorials” on-ramps, and preserve old top-level pages as thin stubs pointing to the new locations. Prefer runnable docs examples using `markdown-exec` (`pycon exec="1"`) and ensure every tutorial demonstrates Omnipy’s display output (`_docs()`, plus optional `peek/full/json/browse` where appropriate).

**Tech Stack:** MkDocs Material; `markdown-exec`; `pymdownx` extensions already configured; `uv` for running `mkdocs build`.

**Maturity labels (required):**

- **Now**: stable, supported, runnable examples — APIs are settled.
- **Preview**: implemented and usable today, but still under active refinement — docs must state scope/limits, APIs may shift.
- **Planned**: not yet implemented or publicly usable — describe user value only, no speculative signatures.

Docs content must use **Now / Preview / Planned** consistently (no ad-hoc labels).

---

## File structure (create/modify map)

**Create:**
- `docs/start/install.md` — installation guide extracted from existing `docs/readme.md`
- `docs/start/quickstart.md` — 10-minute end-to-end quickstart
- `docs/start/concepts.md` — Start-here concepts page (stub)
- `docs/tutorials/01-interactive-safety.md` — tutorial 1
- `docs/tutorials/02-json-to-tables.md` — tutorial 2
- `docs/tutorials/03-dataset-batch.md` — tutorial 3
- `docs/tutorials/04-build-a-dataflow.md` — tutorial 4 (stub; Phase 1)
- `docs/tutorials/05-domain-tabular-formats.md` — tutorial 5 (stub; Phase 1)
- `docs/tutorials/06-resilient-api-fetching.md` — tutorial 6 (stub; Phase 1)
- `docs/tutorials/07-ai-safe-boundaries.md` — tutorial 7 (stub; Phase 2)
- `docs/tutorials/08-prefect-orchestration.md` — tutorial 8 (stub; Phase 2)
- `docs/howto/models/define-models.md` — How-to Models: Define Models (stub)
- `docs/howto/models/pydantic-compatibility.md` — How-to Models: Pydantic compatibility (stub)
- `docs/howto/models/parse-strategies.md` — How-to Models: Parse strategies (stub)
- `docs/howto/models/conversions-to.md` — How-to Models: Conversions with `.to()` (stub)
- `docs/howto/models/chainx-recipes.md` — How-to Models: ChainX recipes (stub)
- `docs/howto/models/parametrized-models.md` — How-to Models: Parametrized models (stub)
- `docs/howto/models/display-visualization.md` — How-to Models: Display/visualization (stub)
- `docs/howto/datasets/working-with-datasets.md` — How-to Datasets: Working with Datasets (stub)
- `docs/howto/datasets/hierarchies-blueprints.md` — How-to Datasets: Hierarchies & blueprints (stub)
- `docs/howto/compute/tasks.md` — How-to Compute: Tasks (stub)
- `docs/howto/compute/flows.md` — How-to Compute: Flows (stub)
- `docs/howto/compute/modifiers.md` — How-to Compute: Modifiers (stub)
- `docs/howto/compute/engines.md` — How-to Compute: Engines (stub)
- `docs/howto/compute/mapping-over-datasets.md` — How-to Compute: Mapping over Datasets (stub)
- `docs/howto/formats/domain-tabular-formats.md` — How-to Formats: Domain tabular formats (stub)
- `docs/howto/formats/column-based-tabular.md` — How-to Formats: Column-based parsing/validation (stub)
- `docs/howto/formats/planned-format-support.md` — How-to Formats: Planned format support (stub)
- `docs/howto/serialization-persistence.md` — How-to: Serialization & persistence (stub)
- `docs/features/continuous-validation.md` — Feature overview: continuous validation (stub)
- `docs/features/snapshots-rollbacks.md` — Feature overview: snapshots & rollbacks (stub)
- `docs/features/conversions.md` — Feature overview: conversions (stub)
- `docs/features/datasets.md` — Feature overview: datasets (stub)
- `docs/features/compute-dataflows.md` — Feature overview: dataflows/compute (stub)
- `docs/features/display.md` — Feature overview: display/visualization (stub)
- `docs/features/components-catalog.md` — Feature overview: components catalog (stub)
- `docs/features/engines.md` — Feature overview: engines (stub)
- `docs/features/tabular-schemas-vs-pandera.md` — Feature overview: tabular schemas vs Pandera (stub)
- `docs/learn/omnipy-mental-model.md` — Learn: mental model (stub)
- `docs/learn/python-typing.md` — Learn: Python typing (stub)
- `docs/learn/positioning-comparisons.md` — Learn: positioning & comparisons (stub)
- `docs/story_mode.md` — Learn: visual metaphors & story mode (stub)
- `docs/reference_nonapi/configuration.md` — Reference: configuration (stub)
- `docs/reference_nonapi/glossary.md` — Reference: glossary (stub)
- `docs/reference_nonapi/faq-troubleshooting.md` — Reference: FAQ/troubleshooting (stub)
- `docs/contributing/documentation.md` — Contributing: documentation contribution (stub)
- `docs/_includes/maturity_labels.md` — shared maturity label definitions
- `docs/_includes/stub_now.md` — stub include (Now)
- `docs/_includes/stub_preview.md` — stub include (Preview)
- `docs/_includes/stub_planned.md` — stub include (Planned)

**Modify:**
- `docs/index.md` — replace readme-include wrapper with purpose-built landing page
- `mkdocs.yml` — wire FULL IA nav (with stub pages) per updated spec
- `docs/data_models.md` — thin redirect stub to new tutorial(s)/start
- `docs/python_typing.md` — thin redirect stub to “Learn” (Phase 1+) while linking to Start/Tutorials now
- `docs/parse_dont_validate.md` — (optional) manual moved notice to Learn section (Phase 1+ target is `docs/learn/parse-dont-validate.md`)

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

Replace the current `nav:` block with the following (keep the rest of the file unchanged).

This wires the **full IA** from the updated spec and uses stub pages for deferred sections.

```yaml
nav:
  - Start here:
      - Home: index.md
      - Install: start/install.md
      - 10-minute Quickstart: start/quickstart.md
      - Concepts (stub): start/concepts.md
  - Tutorials:
      - '01. Interactive safety': tutorials/01-interactive-safety.md
      - '02. Nested JSON to tables': tutorials/02-json-to-tables.md
      - '03. Batch processing with Dataset': tutorials/03-dataset-batch.md
      - '04. Build a dataflow (Task → Flow → Engine) (stub)': tutorials/04-build-a-dataflow.md
      - '05. Domain tabular formats (BED/GFF) (stub)': tutorials/05-domain-tabular-formats.md
      - '06. Resilient API fetching (stub)': tutorials/06-resilient-api-fetching.md
      - '07. AI-safe boundaries (stub)': tutorials/07-ai-safe-boundaries.md
      - '08. Orchestrate with Prefect (stub)': tutorials/08-prefect-orchestration.md
  - How-to guides:
      - Models:
          - Define Models (stub): howto/models/define-models.md
          - Pydantic compatibility (stub): howto/models/pydantic-compatibility.md
          - Parse strategies (stub): howto/models/parse-strategies.md
          - Conversions with .to() (stub): howto/models/conversions-to.md
          - ChainX recipes (stub): howto/models/chainx-recipes.md
          - Parametrized models (stub): howto/models/parametrized-models.md
          - Display/visualization (stub): howto/models/display-visualization.md
      - Datasets:
          - Working with Datasets (stub): howto/datasets/working-with-datasets.md
          - Hierarchies & blueprints (stub): howto/datasets/hierarchies-blueprints.md
      - Dataflows (Compute):
          - Tasks (stub): howto/compute/tasks.md
          - Flows (stub): howto/compute/flows.md
          - Modifiers (stub): howto/compute/modifiers.md
          - Engines (Local vs Prefect) (stub): howto/compute/engines.md
          - Mapping over Datasets (stub): howto/compute/mapping-over-datasets.md
      - File & format parsing:
          - Domain tabular formats (Now) (stub): howto/formats/domain-tabular-formats.md
          - Column-based parsing/validation (Preview) (stub): howto/formats/column-based-tabular.md
          - Planned format support (stub): howto/formats/planned-format-support.md
      - Serialization & persistence (stub): howto/serialization-persistence.md
  - Feature overview:
      - Continuous validation (stub): features/continuous-validation.md
      - Snapshots & rollbacks (stub): features/snapshots-rollbacks.md
      - Conversions (.to) (stub): features/conversions.md
      - Dataset batch + hierarchies (stub): features/datasets.md
      - Dataflows (Compute) (stub): features/compute-dataflows.md
      - Display/visualization (stub): features/display.md
      - Components catalog (stub): features/components-catalog.md
      - Engines (stub): features/engines.md
      - Tabular schemas vs Pandera (Preview) (stub): features/tabular-schemas-vs-pandera.md
  - Learn:
      - Omnipy mental model (stub): learn/omnipy-mental-model.md
      - Parse, don't validate: parse_dont_validate.md
      - Python typing (stub): learn/python-typing.md
      - Positioning & comparisons (stub): learn/positioning-comparisons.md
      - Visual metaphors and story mode (Planned): story_mode.md
  - Reference (non-API):
      - Configuration (stub): reference_nonapi/configuration.md
      - Glossary (stub): reference_nonapi/glossary.md
      - FAQ / Troubleshooting (stub): reference_nonapi/faq-troubleshooting.md
  - Contributing:
      - Contributing: contributing.md
      - Documentation contribution (stub): contributing/documentation.md
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

## Task 2.2: Add shared maturity labels + stub includes (for FULL IA placeholders)

**Files:**
- Create: `docs/_includes/maturity_labels.md`
- Create: `docs/_includes/stub_now.md`
- Create: `docs/_includes/stub_preview.md`
- Create: `docs/_includes/stub_planned.md`

Create these files with the exact content below.

### `docs/_includes/maturity_labels.md`

```markdown
> [!NOTE]
> **Maturity labels**
> - **Now**: stable, supported, runnable examples — APIs are settled.
> - **Preview**: implemented and usable today, but still under active refinement — docs must state scope/limits, APIs may shift.
> - **Planned**: not yet implemented or publicly usable — describe user value only, no speculative signatures.
```

### `docs/_includes/stub_now.md`

```markdown
> [!NOTE]
> **Status: Now**
>
> This page exists to wire the documentation navigation.
> It will be expanded in a later phase.
```

### `docs/_includes/stub_preview.md`

```markdown
> [!NOTE]
> **Status: Preview**
>
> This page exists to wire the documentation navigation.
> It will be expanded in a later phase.
```

### `docs/_includes/stub_planned.md`

```markdown
> [!NOTE]
> **Status: Planned**
>
> This page exists to wire the documentation navigation.
> It will be expanded in a later phase.
```

- [ ] **Step 2.2.1: Create shared includes**

Create the four files exactly as above.

- [ ] **Step 2.2.2: Verify MkDocs build**

Run: `uv run --all-groups mkdocs build`

Expected: exit code 0.

- [ ] **Step 2.2.3: Commit**

```bash
git add docs/_includes/maturity_labels.md \
  docs/_includes/stub_now.md \
  docs/_includes/stub_preview.md \
  docs/_includes/stub_planned.md
git commit -m "docs: add maturity labels and stub includes"
```

---

## Task 2.3: Create FULL IA stub pages required by nav (deferred content, split by directory)

**Files:**
- Create: `docs/start/concepts.md`
- Create: `docs/tutorials/04-build-a-dataflow.md`
- Create: `docs/tutorials/05-domain-tabular-formats.md`
- Create: `docs/tutorials/06-resilient-api-fetching.md`
- Create: `docs/tutorials/07-ai-safe-boundaries.md`
- Create: `docs/tutorials/08-prefect-orchestration.md`
- Create: `docs/howto/models/define-models.md`
- Create: `docs/howto/models/pydantic-compatibility.md`
- Create: `docs/howto/models/parse-strategies.md`
- Create: `docs/howto/models/conversions-to.md`
- Create: `docs/howto/models/chainx-recipes.md`
- Create: `docs/howto/models/parametrized-models.md`
- Create: `docs/howto/models/display-visualization.md`
- Create: `docs/howto/datasets/working-with-datasets.md`
- Create: `docs/howto/datasets/hierarchies-blueprints.md`
- Create: `docs/howto/compute/tasks.md`
- Create: `docs/howto/compute/flows.md`
- Create: `docs/howto/compute/modifiers.md`
- Create: `docs/howto/compute/engines.md`
- Create: `docs/howto/compute/mapping-over-datasets.md`
- Create: `docs/howto/formats/domain-tabular-formats.md`
- Create: `docs/howto/formats/column-based-tabular.md`
- Create: `docs/howto/formats/planned-format-support.md`
- Create: `docs/howto/serialization-persistence.md`
- Create: `docs/features/continuous-validation.md`
- Create: `docs/features/snapshots-rollbacks.md`
- Create: `docs/features/conversions.md`
- Create: `docs/features/datasets.md`
- Create: `docs/features/compute-dataflows.md`
- Create: `docs/features/display.md`
- Create: `docs/features/components-catalog.md`
- Create: `docs/features/engines.md`
- Create: `docs/features/tabular-schemas-vs-pandera.md`
- Create: `docs/learn/omnipy-mental-model.md`
- Create: `docs/learn/python-typing.md`
- Create: `docs/learn/positioning-comparisons.md`
- Create: `docs/reference_nonapi/configuration.md`
- Create: `docs/reference_nonapi/glossary.md`
- Create: `docs/reference_nonapi/faq-troubleshooting.md`
- Create: `docs/contributing/documentation.md`

For **every** stub file in this task:

1) Use the exact H1 title listed below (no template placeholders).
2) Include shared maturity labels: `--8<-- "_includes/maturity_labels.md"`.
3) Include exactly one status include: `_includes/stub_now.md`, `_includes/stub_preview.md`, or `_includes/stub_planned.md`.

- [ ] **Step 2.3.1: Create `start/` stubs**

| File | H1 title | Status include |
|---|---|---|
| `docs/start/concepts.md` | `Concepts (stub)` | `stub_planned.md` |

- [ ] **Step 2.3.2: Create `tutorials/` stubs (Tutorials 4–8, deferred)**

| File | H1 title | Status include | Extra line |
|---|---|---|---|
| `docs/tutorials/04-build-a-dataflow.md` | `Tutorial 4: Build a dataflow (Task → Flow → Engine) (stub)` | `stub_planned.md` | `This tutorial is **Planned** for Phase 1.` |
| `docs/tutorials/05-domain-tabular-formats.md` | `Tutorial 5: Domain tabular formats via model specs (BED/GFF) (stub)` | `stub_planned.md` | `This tutorial is **Planned** for Phase 1.` |
| `docs/tutorials/06-resilient-api-fetching.md` | `Tutorial 6: Resilient API fetching (stub)` | `stub_planned.md` | `This tutorial is **Planned** for Phase 1.` |
| `docs/tutorials/07-ai-safe-boundaries.md` | `Tutorial 7: AI-safe boundaries (stub)` | `stub_planned.md` | `This tutorial is **Planned** for Phase 2.` |
| `docs/tutorials/08-prefect-orchestration.md` | `Tutorial 8: Orchestrate with Prefect (stub)` | `stub_planned.md` | `This tutorial is **Planned** for Phase 2.` |

- [ ] **Step 2.3.3: Create `howto/models/` stubs**

| File | H1 title | Status include |
|---|---|---|
| `docs/howto/models/define-models.md` | `Define Models (stub)` | `stub_planned.md` |
| `docs/howto/models/pydantic-compatibility.md` | `Pydantic compatibility (stub)` | `stub_planned.md` |
| `docs/howto/models/parse-strategies.md` | `Parse strategies (stub)` | `stub_planned.md` |
| `docs/howto/models/conversions-to.md` | `Conversions with .to() (stub)` | `stub_planned.md` |
| `docs/howto/models/chainx-recipes.md` | `ChainX recipes (stub)` | `stub_planned.md` |
| `docs/howto/models/parametrized-models.md` | `Parametrized models (stub)` | `stub_planned.md` |
| `docs/howto/models/display-visualization.md` | `Display/visualization (stub)` | `stub_planned.md` |

- [ ] **Step 2.3.4: Create `howto/datasets/` stubs**

| File | H1 title | Status include |
|---|---|---|
| `docs/howto/datasets/working-with-datasets.md` | `Working with Datasets (stub)` | `stub_planned.md` |
| `docs/howto/datasets/hierarchies-blueprints.md` | `Hierarchies & blueprints (stub)` | `stub_planned.md` |

- [ ] **Step 2.3.5: Create `howto/dataflows` stubs (implemented under `docs/howto/compute/`)**

| File | H1 title | Status include |
|---|---|---|
| `docs/howto/compute/tasks.md` | `Tasks (stub)` | `stub_planned.md` |
| `docs/howto/compute/flows.md` | `Flows (stub)` | `stub_planned.md` |
| `docs/howto/compute/modifiers.md` | `Modifiers (stub)` | `stub_planned.md` |
| `docs/howto/compute/engines.md` | `Engines (Local vs Prefect) (stub)` | `stub_planned.md` |
| `docs/howto/compute/mapping-over-datasets.md` | `Mapping Tasks/Flows over Datasets (stub)` | `stub_planned.md` |

- [ ] **Step 2.3.6: Create `howto/components`-oriented stubs (formats + serialization + feature overview)**

| File | H1 title | Status include |
|---|---|---|
| `docs/howto/formats/domain-tabular-formats.md` | `Domain tabular formats (row-based parsing) (stub)` | `stub_now.md` |
| `docs/howto/formats/column-based-tabular.md` | `Column-based tabular parsing/validation (stub)` | `stub_preview.md` |
| `docs/howto/formats/planned-format-support.md` | `Planned format support (stub)` | `stub_planned.md` |
| `docs/howto/serialization-persistence.md` | `Serialization & persistence (stub)` | `stub_planned.md` |
| `docs/features/continuous-validation.md` | `Continuous validation & type mimicking (stub)` | `stub_planned.md` |
| `docs/features/snapshots-rollbacks.md` | `Snapshots & rollbacks (stub)` | `stub_planned.md` |
| `docs/features/conversions.md` | `Declarative conversions (.to()) (stub)` | `stub_planned.md` |
| `docs/features/datasets.md` | `Dataset batch + hierarchies (stub)` | `stub_planned.md` |
| `docs/features/compute-dataflows.md` | `Dataflows (Compute): Tasks/Flows/Modifiers (stub)` | `stub_planned.md` |
| `docs/features/display.md` | `Display & visualization (stub)` | `stub_planned.md` |
| `docs/features/components-catalog.md` | `Components catalog (stub)` | `stub_planned.md` |
| `docs/features/engines.md` | `Engines & orchestration (stub)` | `stub_planned.md` |
| `docs/features/tabular-schemas-vs-pandera.md` | `Tabular schemas: Omnipy vs Pandera (stub)` | `stub_preview.md` |

- [ ] **Step 2.3.7: Create `learn/` stubs**

| File | H1 title | Status include |
|---|---|---|
| `docs/learn/omnipy-mental-model.md` | `Omnipy mental model (stub)` | `stub_planned.md` |
| `docs/learn/python-typing.md` | `Python typing (stub)` | `stub_planned.md` |
| `docs/learn/positioning-comparisons.md` | `Positioning & comparisons (stub)` | `stub_planned.md` |

- [ ] **Step 2.3.8: Create `reference/` stubs (implemented under `docs/reference_nonapi/`)**

| File | H1 title | Status include |
|---|---|---|
| `docs/reference_nonapi/configuration.md` | `Configuration (stub)` | `stub_planned.md` |
| `docs/reference_nonapi/glossary.md` | `Glossary (stub)` | `stub_planned.md` |
| `docs/reference_nonapi/faq-troubleshooting.md` | `FAQ / Troubleshooting (stub)` | `stub_planned.md` |

- [ ] **Step 2.3.9: Create `contributing/` stubs**

| File | H1 title | Status include |
|---|---|---|
| `docs/contributing/documentation.md` | `Documentation contribution (stub)` | `stub_planned.md` |

- [ ] **Step 2.3.10: Verify MkDocs build (nav paths resolve)**

Run: `uv run --all-groups mkdocs build`

Expected: exit code 0.

- [ ] **Step 2.3.11: Commit**

```bash
git add docs/start/concepts.md \
  docs/tutorials/04-build-a-dataflow.md \
  docs/tutorials/05-domain-tabular-formats.md \
  docs/tutorials/06-resilient-api-fetching.md \
  docs/tutorials/07-ai-safe-boundaries.md \
  docs/tutorials/08-prefect-orchestration.md \
  docs/howto docs/features docs/learn docs/reference_nonapi docs/contributing
git commit -m "docs: add IA stub pages for deferred sections"
```

---

## Task 2.4: Add the Phase 0 “story mode” stub page

**Files:**
- Create: `docs/story_mode.md`

Create `docs/story_mode.md` with this complete content:

```markdown
# Visual metaphors and story mode (Planned)

Later versions of the documentation may add an optional “story mode” layer and visual metaphors to
support learning.

- This is **Planned** (not part of v1 documentation).
- v1 content stays technical and neutral.
```

- [ ] **Step 2.4.1: Create `docs/story_mode.md`**

Add the file exactly as above.

- [ ] **Step 2.4.2: Verify MkDocs build**

Run: `uv run --all-groups mkdocs build`

Expected: exit code 0.

- [ ] **Step 2.4.3: Commit**

```bash
git add docs/story_mode.md
git commit -m "docs: add Planned story mode stub"
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

## Visual metaphors and story mode (Planned)

Later versions may add optional visual metaphors and a “story mode” layer for learning. Not in v1.
See: [Visual metaphors and story mode (Planned)](story_mode.md)
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

## 4) Convert nested JSON to tables (Preview)

This is **Preview**; the full story is in Tutorial 2.

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

This tutorial demonstrates Omnipy’s “interactive safety net”: models continuously validate and,
with interactive mode enabled, automatically roll back after invalid edits.

Useful mental model:

> A Pydantic model is a use-once-then-discard validator; an Omnipy model is a continuous
> static-type repairman in a dynamic environment.

After parsing, the Omnipy model also **type-mimics** the underlying Python type. In this tutorial,
`Model[list[int]]` behaves like a list while continuously enforcing integer semantics.

## What you’ll build

- A typed model that behaves like a Python list
- An intentional mistake that triggers an immediate error
- A comparison of interactive mode ON vs OFF

## Setup (silence logs + avoid output persistence)

```pycon exec="1" session="t1" source="console"
>>> from omnipy import Model, runtime
>>> runtime.config.root_log.log_to_stdout = False
>>> runtime.config.root_log.log_to_stderr = False
>>> runtime.config.root_log.log_to_file = False
>>> runtime.config.job.output_storage.persist_outputs = 'disabled'
>>> runtime.config.data.model.interactive = True  # default
```

!!! note "Execution"
    This tutorial is **Now** and must execute during `mkdocs build` via `markdown-exec`.

## 1) Parse messy input (fun scenario: arcade ticket counts)

```pycon exec="1" session="t1" source="console"
>>> ticket_counts = Model[list[int]]((120, '135', 142.0))
>>> ticket_counts
```

```pycon exec="1" session="t1" result="console" html="true"
>>> print(ticket_counts._docs())
```

## 2) Make a mistake (and recover automatically)

```pycon exec="1" session="t1" source="console"
>>> try:
...     ticket_counts.append('bonus')
... except Exception as err:
...     print(type(err).__name__)
```

The model is still valid after the error:

```pycon exec="1" session="t1" source="console"
>>> ticket_counts
```

```pycon exec="1" session="t1" result="console" html="true"
>>> print(ticket_counts._docs())
```

## 3) Continue working without re-parsing

```pycon exec="1" session="t1" source="console"
>>> ticket_counts.append('150')
>>> ticket_counts
```

```pycon exec="1" session="t1" result="console" html="true"
>>> print(ticket_counts._docs())
```

## 4) Turning interactive rollback off

Interactive mode controls snapshot + rollback behavior:

- **Interactive = True (default)**: automatic snapshots and rollbacks on validation errors.
- **Interactive = False**: skip snapshot overhead (lower memory footprint, often faster writes),
  but lose automatic recoverability.

Both modes still raise validation errors immediately (**fail fast**).

```pycon exec="1" session="t1" source="console"
>>> runtime.config.data.model.interactive = False
>>> ticket_counts_fast = Model[list[int]]([10, 20, 30])
>>> try:
...     ticket_counts_fast.append('VIP')
... except Exception as err:
...     print(type(err).__name__)
>>> ticket_counts_fast
```

Interactive mode is not only for notebooks — it is useful in any context where recoverability and
inspection of the pre-error state are valuable.

## What you learned

- Omnipy models parse data into a typed shape, then keep enforcing it continuously
- Omnipy models type-mimic the underlying Python type while adding continuous validation
- `runtime.config.data.model.interactive` chooses between recoverability and lower overhead

## Common pitfalls

- Confusing the config path: use `runtime.config.data.model.interactive` (not `interactive_mode`).

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

!!! note "Execution"
    This tutorial is **Now** and must execute during `mkdocs build` via `markdown-exec`.

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

The result is a JSON dataset with multiple related “tables”:

- `items` (scalar columns)
- `items.meta` (nested object expanded)
- `items.tags` (nested list expanded)

Think of this output as a small **relational table set**. The relationships are encoded by dataset
naming (`items`, `items.meta`, `items.tags`, etc.), which makes parent/child structure explicit.

```pycon exec="1" session="t2" source="console"
>>> flat
```

```pycon exec="1" session="t2" result="console" html="true"
>>> print(flat._docs())
```

## 3) Convert to pandas where it fits

If a dataset is already table-shaped, convert it directly to `PandasDataset`:

```pycon exec="1" session="t2" source="console"
>>> from omnipy import PandasDataset
>>> pandas = flat.to(PandasDataset)
>>> pandas
```

```pycon exec="1" session="t2" result="console" html="true"
>>> print(pandas._docs())
```

You can also convert a single table-shaped model to `PandasModel`:

```pycon exec="1" session="t2" source="console"
>>> from omnipy import JsonListOfDictsModel, PandasModel
>>> one_table = JsonListOfDictsModel([{'id': 'a', 'x': 1}, {'id': 'b', 'x': 3}])
>>> one_table_pd = one_table.to(PandasModel)
>>> one_table_pd
```

## Current boundaries

Supported top-level structures for JSON-to-table conversion include:

- A clean **list of dicts**
- A **dict of dicts** (via `transpose_dict_of_dicts_2_list_of_dicts`)
- A **dict of lists** (via table transformations)

Not supported:

- Mixed containers or scalars at level 2
- Single-level lists
- Single-level dicts
- Single scalars

Strengths:

- Flattening handles many deeply nested structures where regular flattening approaches (for
  example `pandas.json_normalize`) often fail.
- The output is a set of related relational tables, not necessarily one flat table.

When flattening doesn’t produce what you want, treat it as a **parsing problem**: define a clearer
target shape and parse/transform toward it.

For background, see: [Parse, don't validate](../parse_dont_validate.md)

## What you learned

- How to flatten nested JSON into related datasets with `flatten_nested_json.run(...)`
- How to convert table-like JSON datasets to pandas with `.to(PandasDataset)` and `.to(PandasModel)`

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

This tutorial starts with the primary batch operation in Omnipy: **batch parsing with
`Dataset[Model[...]]`**. It then extends to task-based batch transformations.

## Setup (silence logs + avoid output persistence)

```pycon exec="1" session="t3" source="console"
>>> from omnipy import runtime
>>> runtime.config.root_log.log_to_stdout = False
>>> runtime.config.root_log.log_to_stderr = False
>>> runtime.config.root_log.log_to_file = False
>>> runtime.config.job.output_storage.persist_outputs = 'disabled'
```

!!! note "Execution"
    This tutorial is **Now** and must execute during `mkdocs build` via `markdown-exec`.

## 1) Batch-parse many values at once (primary pattern)

```pycon exec="1" session="t3" source="console"
>>> from omnipy import Dataset, Model
>>> numbers = Dataset[Model[int]]({'a': '1', 'b': 2.0, 'c': 10})
>>> numbers
```

```pycon exec="1" session="t3" result="console" html="true"
>>> print(numbers._docs())
```

`Dataset[Model[int]](...)` parses each value and gives you a typed batch container in one step.

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

- `Dataset[Model[T]]` is the default way to batch-parse many items into a typed shape
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

### Optional moved notice: `docs/parse_dont_validate.md`

The updated spec places this page under **Learn**. Phase 0 does not require moving it, but if you
choose to align URLs early, preserve the old page as a manual moved notice.

If doing this in Phase 0, add:

- Create: `docs/learn/parse-dont-validate.md` (new home)
- Modify: `docs/parse_dont_validate.md` (moved notice)
- Update `mkdocs.yml` Learn entry to point to `learn/parse-dont-validate.md`

`docs/learn/parse-dont-validate.md` content:

```markdown
# Parse, don't validate

--8<-- "parse_dont_validate.md"
```

`docs/parse_dont_validate.md` moved notice content:

```markdown
# Parse, don't validate (moved)

This page has moved to: [Parse, don't validate](learn/parse-dont-validate.md)
```

### Redirect stub: `docs/data_models.md`

Replace the entire file with:

```markdown
# Data models (moved)

This page has moved to: [How-to: Define Models](howto/models/define-models.md)

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

This page has moved to: [Learn: Python typing](learn/python-typing.md)

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

## Task 10: Enforce docs build in CI

**Files:**
- Modify: `.github/workflows/run_tests.yaml` (existing test workflow)

- [ ] **Step 10.1: Confirm CI workflow location**

Check `.github/workflows/` for a test workflow. In this repo, use
`.github/workflows/run_tests.yaml`.

- [ ] **Step 10.2: Add MkDocs build step to test workflow**

In `.github/workflows/run_tests.yaml`, add a step in the existing `run-tests` job:

```yaml
      - name: Build docs with MkDocs
        run: |
          uv sync --all-groups
          uv run mkdocs build
```

Place it after dependency installation and before/after pytest as preferred; keep existing tests.

- [ ] **Step 10.3: Verify workflow YAML is valid + run docs build locally**

Run:

```bash
uv sync --all-groups
uv run mkdocs build
```

Expected: exit code 0.

- [ ] **Step 10.4: Commit**

```bash
git add .github/workflows/run_tests.yaml
git commit -m "ci: enforce mkdocs build in test workflow"
```

---

## Task 11: Plan self-review (against spec)

Run this self-review before handing off for execution.

- [ ] **Step 11.1: Spec coverage check (Phase 0)**

Confirm the plan includes:

- Landing page: value prop, 3 bullets, code snippet with visible output, CTAs, compare strip, JSON→tables caveat link, and a neutral v2 placeholder.
- Install page extracted/updated from readme (Python version constraint, install command, next link).
- Quickstart: install → model parse → interactive safety → conversion Preview → dataset mapping.
- Tutorials 1–3: runnable, each shows `_docs()` output; Tutorial 2 links to `parse_dont_validate.md`; Tutorials are neutral tone.
- Nav updated in `mkdocs.yml` to the FULL IA (with stub/placeholder pages) and **Dataflows (Compute)** as a top-level peer within How-to.
- Maturity labels are defined and used consistently as **Now / Preview / Planned**.
- Tutorial execution is enforced by `markdown-exec` (tutorial code runs during `mkdocs build`).
- Redirect stubs follow the manual notice format: “This page has moved to <new page>” + link.
- CI enforces docs build by running `uv sync --all-groups` and `uv run mkdocs build` in workflow.

- [ ] **Step 11.2: Placeholder scan**

Search the plan-created docs for placeholders:

Run: `rg -n "\b(TBD|TODO|coming soon)\b" docs/start docs/tutorials docs/index.md docs/data_models.md docs/python_typing.md`

Expected: no unlabelled roadmap claims.

- [ ] **Step 11.3: Final verification build**

Run: `uv run --all-groups mkdocs build`

Expected: exit code 0.

No commit for this task.

---

## Execution notes

- Prefer `markdown-exec` runnable blocks (`pycon exec="1"`) and keep each tutorial’s examples in a single named `session` so outputs accumulate.
- Keep tone neutral (no superhero voice).
- Use the correct config naming: `runtime.config.data.model.interactive` and call it “interactive mode” or “interactive rollback.” Avoid the outdated `interactive_mode` name.
