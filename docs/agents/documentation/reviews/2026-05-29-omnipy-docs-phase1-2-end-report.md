# End Report: Omnipy Documentation Redesign (Phases 1 & 2)

> Date: 2026-05-29
> Scope: Feature overviews, how-to guides, compute docs, domain formats, AI boundaries, Prefect, FAQ
> Cumulative commits: from `263c70fb` through `a94230b9`

## Overview

This report covers Phase 1 ("complete the core story") and Phase 2 ("scale and
ecosystem") of the Omnipy online documentation redesign. Phase 0 (landing,
start pages, tutorials 1-3) was completed earlier and has its own end report at
`docs/agents/documentation/reviews/2026-05-28-omnipy-docs-redesign-end-report.md`.

---

## Phase 1 deliverables

### 1. Feature overview pages (7 pages)

All follow the approved template (What it solves -> The idea -> Example -> Output
-> When to use -> Gotchas -> Links):

- `docs/feature/continuous-validation.md` -- type mimicking, self-constraining
- `docs/feature/snapshots-rollbacks.md` -- interactive safety, lazy snapshots
- `docs/feature/declarative-conversions.md` -- `.to()` conversions, JSON->Pandas
- `docs/feature/dataset-batch-hierarchies.md` -- Dataset mapping, nesting
- `docs/feature/display-visualization.md` -- peek/full/browse/_docs
- `docs/feature/components-catalog.md` -- General, JSON, Nested, Raw, Remote, Tables
- `docs/feature/engines-orchestration.md` -- local vs Prefect engine

### 2. How-to guides for Models (7 pages)

- `docs/howto/models/define-models.md` -- quick patterns, subclassing
- `docs/howto/models/parse-strategies.md` -- parse don't validate in practice
- `docs/howto/models/conversions-to.md` -- `.to()` patterns
- `docs/howto/models/display-inspection.md` -- peek/full/browse/_docs
- `docs/howto/models/chainx-recipes.md` -- chained model transformations
- `docs/howto/models/parametrized-models.md` -- patterns + limitations
- `docs/howto/models/pydantic-compatibility.md` -- trust-builder page

### 3. Dataflows (Compute) how-to guides (6 pages)

- `docs/howto/dataflows/tasks.md` -- Task definition
- `docs/howto/dataflows/flows.md` -- Linear vs DAG vs FuncFlow
- `docs/howto/dataflows/running-flows.md` -- local engine execution
- `docs/howto/dataflows/modifiers.md` -- task/flow/job modifiers
- `docs/howto/dataflows/mapping-over-datasets.md` -- mapping tasks over datasets
- `docs/howto/dataflows/engines-overview.md` -- local + Prefect

### 4. Tutorial 5: Domain tabular formats (BED/GFF)

- `docs/tutorials/05-domain-tabular-formats.md`
- Row-based parsing labeled **Now**, column-based validation labeled **Preview**

### 5. Compare page

- `docs/learn/comparisons.md` -- Omnipy vs Pandas+requests+Pydantic,
  Snakemake/Nextflow, Prefect, Dagster, dlt, Pandera

### 6. Domain format parsing guide

- `docs/howto/components/domain-formats.md`
- Model-based tabular parsing for custom file formats

---

## Phase 2 deliverables

### 1. Prefect tutorial

- `docs/tutorials/08-prefect-orchestration.md` (**Preview**)
- Engine configuration, `--engine prefect`, Prefect UI
- Updated `docs/feature/engines-orchestration.md` to reference Prefect

### 2. Components catalog expansion

- `docs/howto/components/catalog.md` (**Now**)
- All 6 bundled components with problem statements

### 3. FAQ

- `docs/reference/faq.md` (**Now**)
- Common questions about Omnipy vs Pydantic, notebooks, interactive mode,
  JSON-to-tables, Prefect

### 4. Tutorial 7: AI-safe boundaries

- `docs/tutorials/07-ai-safe-boundaries.md` (**Preview**)
- Schema firewall, hallucinated key rejection, batch cleaning, repair-flow
  task pattern, template-style guide
- Ecosystem note: works with Instructor/Marvin/PydanticAI

### 5. Column-based tabular validation

- `docs/howto/components/column-based-tabular.md` (**Preview**)
- Column/record workflows, honest Pandera comparison

---

## Important decisions made during implementation

### 1. Shared includes for consistency

Created `docs/_includes/maturity_labels.md` and `docs/_includes/pycon_setup.md`
to reduce repetition across feature pages. Keeps maturity label definitions in
one place.

### 2. Plan documents not part of nav

The `docs/agents/` directory is excluded from MkDocs build output via
`exclude_docs`. Plan documents (which contain large code blocks) don't need
to be part of the published site.

### 3. markdown-exec blocks made self-contained

Each `pycon exec="1"` block is self-contained to avoid cross-block state
dependencies. This makes tutorials more robust for copy/paste use and avoids
build failures from out-of-order execution.

### 4. Prefect as base dependency

`prefect` is a base (not optional) dependency of Omnipy. Install docs were
corrected from `pip install "omnipy[prefect]"` to `pip install omnipy`.

### 5. AI tutorial framed as patterns, not native integration

The AI-safe boundaries tutorial explicitly positions Omnipy as a data-layer
complement to AI frameworks like Instructor/Marvin/PydanticAI - not a
replacement. This avoids overclaiming while still addressing the use case.

---

## Build verification

| Check | Result |
|-------|--------|
| `uv run mkdocs build` exit code | 0 |
| markdown-exec examples executed | Pass |
| `interactive_mode` in new pages | None found |
| "coming soon" / "stub" in content | None found |

## Commit reference (Phase 1)

| Commit | Description |
|--------|-------------|
| `263c70fb` | Fix Phase 1 plan links and checks |
| `e1b29155` | Add Phase 1 feature overview pages |
| `bdae0659` | Add Phase 1 model how-to guides |
| `a4e95c30` | Add Phase 1 dataflows + tutorial 5 + comparisons |
| `48f15966` | Make tutorial 5 snippets self-contained |
| `ec30510b` | Restore spec artifact, fix plan executable blocks |

## Commit reference (Phase 2)

| Commit | Description |
|--------|-------------|
| `e582f16e` | Add Prefect orchestration tutorial |
| `961f5641` | Expand bundled components catalog |
| `35ce3ec3` | Add FAQ reference page |
| `2f4dbd5f` | Add AI-safe boundaries tutorial |
| `f8525860` | Add column-based tabular validation guide |
| `a94230b9` | Fix Phase 2 review issues |

## Known gaps (deferred)

- Superhero narrative layer (v2, Phase 3)
- Test-informed enrichment of tutorial stories and examples
- More polished interactive table visualization
- Excel/Numpy/Polars/Parquet format support docs
