# End Report: Omnipy Online Documentation Redesign (Phase 0)

> Date: 2026-05-28
> Scope: Docs redesign spec → plan → Phase 0 implementation
> Committed: `f81c32ed` (final Phase 0 fix), cumulative from `d7f11065`

## Overview

This report documents the important choices made during the Omnipy documentation
redesign process, covering the design spec, implementation plan, and Phase 0
implementation. It is written to allow the human partner to review and backtrace
decisions.

---

## Design phase decisions

### 1. Information architecture: "Tutorial-first" over "conceptual-first"

**Choice:** The docs site is organized around task-oriented tutorials and
how-to guides, with conceptual/background material (Learn section) pushed deeper
in the nav hierarchy.

**Rationale:** Two personas with different ROI definitions — developers need
to see working code fast, researchers need quick wins. A tutorial-first
structure serves both better than leading with theory.

**Consequence:** The "Parse, don't validate" philosophical background and
Python typing primer are moved to a secondary Learn section, linked from
tutorials rather than being on the critical onboarding path.

**Backtrace:** Spec Section 3 (IA), confirmed in review discussion.

### 2. Narrative framing: "The Missing Middle"

**Choice:** Omnipy is positioned as occupying the space between:
- file-centric workflow engines (Snakemake/Nextflow) that don't care about
  structure inside files, and
- validation/ETL tools (Pydantic, pandas, ad-hoc scripts) that lack continuous
  safety, hierarchical batch semantics, and coherent typed conversions.

**Rationale:** Derived from the landscaping docs and devil's advocate analysis.
The alternative — pitching Omnipy as "nicer loops" or "better API retries" —
loses to the status quo. The "Missing Middle" positions Omnipy as a heavy-duty
hierarchical harmonizer for complex standards.

**Consequence:** The landing page and tutorials emphasize cases where
`requests+pandas+pydantic` breaks down (deep hierarchies, schema drift, batch,
reproducibility). Simpler use cases are acknowledged but de-emphasized.

**Backtrace:** Spec Section 2, landscape docs, devil's advocate document.

### 3. Dataflows/Compute promoted to top-level IA peer

**Choice:** Tasks, flows (Linear/DAG/Func), and modifiers are surfaced as a
top-level "Dataflows (Compute)" section under How-to Guides, alongside Models
and Datasets.

**Rationale:** The user (human) identified that the compute layer was
undersold in the initial spec. Tasks/flows/modifiers are core user-facing
parts of the library, not just engine internals.

**Consequence:** Increased onboarding complexity is mitigated by keeping
compute depth to "second tutorial" rather than quickstart.

**Backtrace:** User discussion (A2 choice), Spec Section 3 (IA revision).

### 4. Maturity labels: Now / Preview / Planned

**Choice:** A three-tier labeling system for documentation:
- **Now** = stable, supported, runnable examples — APIs are settled
- **Preview** = implemented and usable today, but still under active refinement
- **Planned** = not yet implemented or publicly usable

**Rationale:** Prevents overpromising while acknowledging real capabilities.
"Preview" was chosen over alternatives (Experimental, Beta, Maturing) as the
best balance of honesty and approachability.

**Consequence:** Column-based tabular parsing/validation is labeled Preview
(usable but evolving). Domain file format parsing (BED/GFF) is Now (solid
row-by-row, Preview for columnar).

**Backtrace:** Review discussion rounds, user vote.

### 5. Superhero theme deferred to v2 (with preparation)

**Choice:** The poster superhero narrative (The Omnificents vs. The UnFAIR
Alliance) is explicitly kept out of v1 documentation. A small placeholder on
the landing page and a future-facing section in the spec reserve the option
for v2.

**Rationale:** Risk of tone mismatch with serious documentation. The user
confirmed v1 should stay neutral.

**Consequence:** The mapping of heroes to features (Optimus Parse → parsing,
Endless Schema → validation, etc.) is maintained in the spec but not exposed
in v1 docs. V2 can add an optional "Story mode" layer.

**Backtrace:** Spec Section 7, user discussion (F choice).

---

## Implementation phase decisions

### 6. Phase 0 scope: skeleton over enrichment

**Choice:** Phase 0 delivers structural/nav work, landing page, install guide,
quickstart, and tutorials 1–3 with technically correct but not yet "rich"
content. A separate enrichment pass (test mining → story building → rewrite)
is deferred.

**Rationale:** The user approved this approach (Option A) to get a readable
documentation skeleton to iterate on quickly, rather than stalling for
content perfection.

**Consequence:** Tutorials use functional examples (sensor readings, JSON data,
numeric datasets) rather than the whimsical multi-domain stories planned for
the enrichment pass.

**Backtrace:** User discussion after first plan review.

### 7. markdown-exec required in CI from Phase 0

**Choice:** Tutorials must execute during `mkdocs build` via markdown-exec,
and this is enforced in CI via an added workflow step.

**Rationale:** Prevents docs-to-code drift. If examples stop working, the
build fails.

**Consequence:** Async-heavy examples cannot use markdown-exec directly and
fall back to "Try it in a notebook" callouts. The build now takes slightly
longer due to executing Python blocks.

**Backtrace:** Spec Section 5 ("runnable" definition), review clarification.

### 8. Full IA wired with stubs in Phase 0

**Choice:** The mkdocs.yml nav is wired to the complete IA structure from the
spec, with stub pages for all deferred sections (tutorials 4–8, how-to guides,
feature overview, etc.).

**Rationale:** Provides a complete navigation experience and prevents broken
links. Stubs use "coming soon" wording without maturity labels.

**Consequence:** More mkdocs.yml maintenance but better user experience than
a nav that grows organically.

**Backtrace:** Review clarification (user chose "wire full IA with stubs").

### 9. Existing legacy pages preserved

**Choice:** `docs/data_models.md`, `docs/python_typing.md`, and
`docs/parse_dont_validate.md` are left in place and unchanged. New pages link
to them where appropriate.

**Rationale:** The user explicitly chose this over creating redirect stubs.
These pages contain content that is partially outdated but still valuable.

**Consequence:** Some URL duplication exists. These pages remain in the nav
under the Learn section alongside new pages.

**Backtrace:** User decision during fix round.

### 10. docs/agents/ excluded from site build

**Choice:** The entire `docs/agents/` tree is excluded from MkDocs build
output via `exclude_docs` configuration.

**Rationale:** This directory contains agent-facing working documents
(including superhero-themed content). Without exclusion, MkDocs would build
and potentially publish them.

**Consequence:** The `docs/` directory contains agent docs and user docs
side-by-side; only user-facing docs are published.

**Backtrace:** Review finding (critical issue 5).

---

## Key metrics

| Artifact | Path | Status |
|----------|------|--------|
| Design spec | `docs/agents/documentation/specs/2026-05-28-omnipy-docs-redesign-spec.md` | Final (3 review rounds) |
| Implementation plan | `docs/agents/documentation/plans/2026-05-28-omnipy-docs-phase0-implementation.md` | Final (2 revision rounds) |
| Landing page | `docs/index.md` | Phase 0 complete |
| Installation guide | `docs/start/install.md` | Phase 0 complete |
| Quickstart | `docs/start/quickstart.md` | Phase 0 complete |
| Tutorial 1 (safety) | `docs/tutorials/01-interactive-safety.md` | Phase 0 complete |
| Tutorial 2 (JSON→tables) | `docs/tutorials/02-json-to-tables.md` | Phase 0 complete |
| Tutorial 3 (Dataset batch) | `docs/tutorials/03-dataset-batch.md` | Phase 0 complete |
| Stub pages (34 files) | `docs/tutorials/04-08`, `docs/howto/`, `docs/learn/`, etc. | Phase 0 complete |
| CI enforcement | `.github/workflows/run_tests.yaml` | Phase 0 complete |
| Site build | `uv run mkdocs build` exit 0 | Verified |

## Known gaps (deferred to Phase 1+)

- Test-informed feature mining for richer tutorial examples
- Story-driven tutorial scenarios
- Compute layer how-to content (Tasks, Flows, Modifiers)
- Domain format parsing (BED/GFF) tutorial
- AI-safe boundaries tutorial
- Detailed ChainX and parametrized model documentation
- Prefect integration tutorial
- Column-based tabular validation (Pandera comparison)
- Components catalog expansion
- Superhero narrative layer (v2)

---

## Commit reference

| Commit | Description |
|--------|-------------|
| `d7f11065` | Initial docs redesign spec |
| `055d7006` | Spec fixes per review |
| `86fa9d1d` | Spec revision (compute, formats, AI) |
| `29162c36` | Final spec polish (Preview labels, full IA stubs) |
| `5d155eea` | Initial implementation plan |
| `84bbb114` | Plan fixes per user corrections |
| `c83c98cf` | Phase 0 scaffold (nav + stubs) |
| `124cb38e` | Phase 0 content (landing, start, tutorials) |
| `176ce33a` | CI enforcement + moved notices |
| `f81c32ed` | Phase 0 critical fix round |
