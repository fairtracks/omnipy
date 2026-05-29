# Omnipy Documentation Redesign (Online Docs) — Design Spec

Date: 2026-05-28

## 0. Scope and goals

### In-scope

- Redesign Omnipy’s **online documentation content** (MkDocs Material site) to be:
  - practical/tutorial-driven,
  - convincing in <3 seconds,
  - useful for both **developers** and **convenience-oriented users** (e.g. researchers), and
  - aligned with what Omnipy can do **today**, while clearly signposting **Preview** and
    **Planned** items.
- Propose a new **information architecture (IA)** (site navigation and page ordering).
- Specify a **front page** (landing page) structure that sells the “missing middle” value quickly.
- Define a **tutorial program** (what tutorials exist, what each demonstrates, prerequisites, and
  what to show as current vs aspirational).
- Define a **feature overview** format that highlights Omnipy’s output formatting/visualization.
- Define a **superhero-theme integration plan** for a later version (v2+), without introducing it
  into v1 content.
- Identify **documentation coverage gaps** in the codebase that should become documentation pages.

### Out-of-scope (explicitly not addressed here)

- API reference / docstrings (already handled separately via mkdocstrings).
- Implementing new library features.
- Rewriting MkDocs theme/templates beyond what’s needed for content organization (v1).

### Success criteria

- A new user can answer these quickly:
  1) “What is Omnipy?” 2) “Why not just use Pydantic + pandas + requests?” 3) “What can I do in
  10 minutes?”
- Site navigation makes it obvious where to start for:
  - a developer integrating Omnipy into a project, and
  - a researcher doing interactive data wrangling.
- Tutorials show Omnipy’s **unique value** (continuous validation + conversions + datasets +
  visualization + resilience), not generic Python basics.


## 1. Target audience analysis

Omnipy’s docs must convert and serve two primary personas with different “ROI” definitions.

### Persona A — “Systems-minded Developer” (tech-savvy)

- **Context:** builds pipelines/services; already knows Pydantic, pandas, Prefect/Dagster, and
  workflow engines (Snakemake/Nextflow).
- **Pain points:**
  - brittle ad-hoc scripts for metadata wrangling;
  - schema drift in external APIs;
  - hard-to-test transformations of deeply nested JSON;
  - typed guarantees disappear once data becomes a `dict`/`list`/DataFrame;
  - operational failures: timeouts, rate limits, partial runs.
- **ROI means:**
  - fewer production incidents, faster iteration, lower maintenance,
  - stronger contracts between pipeline stages, better IDE/type-checker experience,
  - ability to scale from notebook → batch → orchestration without rewriting everything.
- **Likely skepticism (Devil’s Advocate):**
  - “I can do this with `requests + tenacity + pandas.json_normalize + pydantic`.”
- **Docs must prove:**
  - where those tools break (deep hierarchies + schema drift + batch + reproducibility), and
  - the cost curve difference when pipelines grow (the “missing middle”).

### Persona B — “Researcher / Analyst” (convenience-oriented)

- **Context:** notebooks first; needs quick wins; may not care about architecture.
- **Pain points:**
  - messy inputs from collaborators/APIs;
  - interactive exploration produces accidental corruption;
  - hard to see nested structures (cryptic reprs, truncated output);
  - repeated re-runs and manual cleanup steps.
- **ROI means:**
  - faster data understanding (“see what I have”),
  - fewer notebook footguns (safe experimentation),
  - converting to “analysis-ready tables” quickly.
- **Docs must prove:**
  - “I can safely manipulate typed data and recover from mistakes,” and
  - “I can turn nested metadata into tabular form quickly.”

### Secondary audiences (supporting)

- **Data engineers / platform users:** care about orchestration and batch runs; likely to arrive via
  Prefect integration.
- **ELIXIR/community contributors:** need a clear mental model + contribution entry points.


## 2. Narrative framing (what to emphasize)

### The core message: “The Missing Middle”

Omnipy sits between:

- file-centric workflow engines (Snakemake/Nextflow) that don’t care about structure inside files,
  and
- validation/ETL tools (Pydantic, pandas, ad-hoc scripts) that don’t provide continuous safety,
  hierarchical batch semantics, and coherent typed conversions across a whole dataflow.

Docs should **not** pitch Omnipy as “nicer loops”; they should pitch Omnipy as a:

- **heavy-duty hierarchical harmonizer** for complex standards and nested metadata, and
- **interactive safety net** that keeps data valid throughout manipulation.

### Trust-builder: “Pydantic model language + Omnipy extensions”

Omnipy should explicitly acknowledge that it inherits much of its modelling ergonomics from
**Pydantic** (including many familiar patterns and “bells and whistles”), and then describe what it
adds on top:

- continuous validation via type mimicking and safe interactive rollback,
- dataflow abstractions (Tasks/Flows/Modifiers) and batch semantics (Datasets),
- convenience patterns like **ChainX** for chained model transformations.

Docs should *not* attempt to re-document Pydantic itself (DRY risk). The goal is to lower adoption
fear by saying “if you know Pydantic, you can be productive quickly,” while keeping Omnipy’s unique
story in the foreground.

### Application framing: AI-safe boundaries (without pretending to be an AI framework)

Omnipy can be positioned as a typed **data boundary layer** around AI calls:

- validate/parse LLM outputs into strict Models,
- batch-clean and transform results into analysis-ready structures,
- protect downstream pipelines from schema drift / hallucinated keys.

Guardrail: Omnipy orchestrates **data**, not “agent reasoning.” Docs should not imply it replaces
Instructor/Marvin/PydanticAI; instead, it complements them.

### What to de-emphasize (or qualify)

- Avoid overselling aspirational features (e.g. future converter registration APIs) as present.
- Avoid deep typing theory on the critical path; keep it as “Learn” material.


## 3. Information architecture (proposed doc site structure)

### Design principles

1. **Two on-ramps:** “I want to try it now” vs “I want to understand it.”
2. **Tutorial-first:** task-oriented pages before conceptual deep dives.
3. **Feature pages are “how it helps + example + output + gotchas”**, not encyclopedic.
4. **Roadmap-awareness:** use **Now / Preview / Planned** labels consistently where useful.

### Proposed top-level navigation

> Note: exact filenames are suggestions; the IA is the key deliverable.

1. **Start here**
   - Home (Landing)
   - Install
   - 10-minute Quickstart
   - Concepts (lightweight)
2. **Tutorials**
   - Tutorial 1: Continuous validation & rollback (interactive safety)
   - Tutorial 2: JSON → tables (nested → analysis-ready)
   - Tutorial 3: Batch processing with Dataset (no for-loops)
   - Tutorial 4: Build a dataflow (Task → Flow → Engine)
   - Tutorial 5: Domain tabular formats (e.g. BED/GFF) via model specs
   - Tutorial 6: Resilient API fetching (retries/backoff, HTTP status handling, rate-limiting
     session wiring; pagination **Planned**/user-land loop)
   - Tutorial 7: AI-safe boundaries (clean LLM outputs into typed Models + tables)
   - Tutorial 8: Orchestrate with Prefect (scale-up path)
3. **How-to guides** (goal-oriented, reference-lite)
   - **Models**
     - Define Models
     - Pydantic compatibility (what carries over; where Omnipy differs)
     - Parse strategies (“parse, don’t validate” in practice)
     - Conversions with `.to()`
     - ChainX recipes (chained model transformations)
     - Parametrized models (patterns + limitations)
     - Display/visualization (peek/full/json/browse/_docs() output)
   - **Datasets**
     - Working with Datasets (mapping, indexing)
     - Hierarchies & blueprints
   - **Dataflows (Compute)**
     - Tasks
     - Flows (Linear vs DAG vs Func)
     - Modifiers (task/flow/job modifiers)
     - Engines (Local vs Prefect) and running flows
     - Mapping Tasks/Flows over Datasets (bridge patterns)
    - **File & format parsing**
      - Domain tabular formats (row-based parsing): **Now**
      - Column-based tabular parsing/validation: **Preview**
      - Notes on **Planned** format support (Excel/Parquet/Polars/etc.)
   - Serialization & persistence (what exists today)
4. **Feature overview** (short pages, each with “why + example + output”)
   - Continuous validation & type mimicking
   - Snapshots & rollbacks
   - Declarative conversions (`.to()`)
   - Dataset batch + hierarchies
   - Dataflows: Tasks/Flows/Modifiers (architectural overview)
   - Components catalog (General/JSON/Remote/Tables/etc.)
   - Engines (local + Prefect integration)
   - Tabular schemas: Omnipy vs Pandera (capabilities + limits; **Preview**)
5. **Learn (Background)**
   - Omnipy mental model (Model/Dataset/Task/Flow)
   - Parse, don’t validate (philosophy)
   - Python typing (shortened; link out)
   - Positioning & comparisons (optional, careful tone)
   - Visual metaphors and story mode (**Planned**)
6. **Reference (non-API)**
   - Configuration (runtime config variants, interactive flag)
   - Glossary
   - FAQ / Troubleshooting
7. **Contributing**
   - Contributing guide (existing)
   - Documentation contribution (new: style, examples, testing docs)
8. **Release notes**

### Placement of existing pages

- `docs/readme.md`: becomes source material; split into:
  - Home (landing) copy,
  - Quickstart tutorial,
  - Feature overview snippets.
- `docs/index.md`: replaced by a purpose-built landing page (still can include parts of readme but
  should not be “readme pasted into index”).
- `docs/data_models.md`: becomes “How-to: Define models” + “Feature: continuous validation”.
- `docs/python_typing.md`: moved under Learn; shortened and more skimmable.
- `docs/parse_dont_validate.md`: moved under Learn; linked from tutorials.
- `docs/use_cases.md`: archived/moved to historical notes or rewritten into modern “Use cases” that
  match current positioning.


## 4. Front page redesign (hook in 3 seconds)

### Front-page objectives

In the first screenful, answer:

1) What it is, 2) what it replaces, 3) how to try it immediately.

### Proposed layout (above the fold)

1. **One-sentence value proposition** (missing middle):
   - “Typed dataflows for messy real-world data — continuous validation, safe interactive
      manipulation, and one-line conversions from nested JSON to tables.”
   - Guardrail note (required): caveat that deep JSON flattening works for many common patterns,
     but has known limits; link to Tutorial 2 for current boundaries.
2. **3-bullet “why you care”** (fast):
   - Keep data valid while you edit it (automatic rollback)
   - Convert complex formats declaratively (`.to(...)`)
   - Batch-process hierarchical collections (Dataset mapping)
3. **A single, compelling code snippet** that demonstrates uniqueness (not “hello world”).
   - Example theme: parse messy input → safe edit → convert/display.
4. **Two CTA buttons**:
   - “10-minute Quickstart”
   - “Tutorials”
5. **A small “Compare” strip** (one paragraph) addressing the devil’s advocate:
   - When `requests+pandas+pydantic` is enough vs when Omnipy pays off.
   - Tone rule: factual and example-first; no dunking on alternatives.

### Output-formatting showcase (mandatory)

The landing page should include at least one rendered example of Omnipy’s display advantage.
Options already present in docs/examples:

- `print(model._docs())` output (currently used in `docs/readme.md`).

Design rule: every “wow” claim must have a visible output, not just prose.

### “Superhero style later” placeholder (v1)

On the landing page, reserve a **small, non-themed** placeholder section:

- “Visual metaphors and story mode (coming later)”
- Link to a future page (or stub) explaining that the doc theme may adopt narrative characters and
  comic-style callouts in v2.
- Strictness rule: keep this placeholder to 1–2 sentences, use strictly neutral language (no hero
  names, no comic voice), and link to the future page stub.

This satisfies the request to “suggest how the front page can be edited later” without actually
introducing the superhero voice into v1.


## 5. Tutorial approach

### Tutorial design principles

- Each tutorial should be runnable and end with a tangible artifact:
  - Runnable definition: execute through `markdown-exec` during `mkdocs build` in CI to prevent
    docs-to-code drift.
  - Fallback rule: when `markdown-exec` cannot handle the example (e.g. async code), provide a
    copy/paste-runnable example plus a clear “Try it in a notebook” callout.
  - a validated model instance,
  - a dataset mapping result,
  - a table, or
  - a reproducible flow run.
- Start with **interactive notebook/console** flows first; add orchestration later.
- Use “messy input” examples that reflect real pain: mixed types, missing keys, nested JSON.
- Each tutorial ends with:
  - “What you learned,”
  - “Common pitfalls,” and
  - “Next steps.”

### Proposed tutorial set (v1)

1. **Tutorial: Interactive safety (continuous validation + rollback)**
   - Story: you’re exploring data in a notebook; you make a mistake; Omnipy saves state.
   - Demonstrates: type mimicking, continuous validation, snapshots/rollbacks, `interactive`.
   - Must show: error + rollback + continuing work without re-parsing.

2. **Tutorial: Nested JSON → analysis-ready tables**
   - Story: API returns deeply nested metadata; you need tables.
   - Demonstrates: JSON component basics, flattening approach, `.to(PandasModel)` where possible,
     and the limits (when it’s hard and why Omnipy matters).
   - Must show: readable display before/after conversion.

3. **Tutorial: Batch processing with Dataset (no for-loops)**
   - Story: you have many records/files; apply one transformation across all.
   - Demonstrates: Dataset creation, mapping a task, hierarchical datasets concept.
   - Must show: “one line replaces loop” while keeping type guarantees.

4. **Tutorial: Build a dataflow (Task → Flow → Engine)**
   - Story: you have a transformation pipeline; you want it to be modular and runnable.
   - Demonstrates: Tasks, at least one Flow type (Linear as default), modifiers as a modular
     extension mechanism, and running on the local engine.
   - Must show: composing multiple tasks into a flow, then running it.
   - Bridge requirement: include a short “batch it” section mapping a Task or Flow over a Dataset.

5. **Tutorial: Domain tabular formats via model specs (BED/GFF)**
   - Story: life science formats are custom and plentiful; you want a robust parsing language.
   - Demonstrates: domain-specific tabular parsing using Model specs + row-based parsing.
   - Must show: a minimal BED- or GFF-like example and a typed output that can be transformed.
   - Performance note: acknowledge row-based parsing is **Now** but can be slightly slow.

6. **Tutorial: Resilient API retrieval**
   - Story: intermittent failures + retry/backoff + status handling under realistic API usage.
   - Demonstrates: Remote component retry semantics as implemented today (`retry_attempts`,
     `retry_http_statuses`, `retry_backoff_strategy`), and how to pass a rate-limiting session
     (`RateLimitingClientSession`) while producing typed Models/Datasets.
   - Must show: configuration knobs and reproducible behavior.
   - Pagination: explicitly out of current built-ins; document as either **Planned** or a
     user-land loop pattern.

7. **Tutorial: AI-safe boundaries (clean LLM outputs into typed Models + tables)**
   - Story: LLM outputs are useful but untrusted; enforce schema at the boundary.
   - Demonstrates: parsing/validating LLM-like JSON into Models, then batch-cleaning and
     converting into analysis-ready formats.
   - Guardrail: state explicitly that Omnipy is the data layer around AI calls, not an agent
     framework.
   - Must show: one example of rejecting/repairing a hallucinated key/type mismatch.

8. **Tutorial: Scale-up path with Prefect (optional v1, can be v1.1)**
   - Story: you have a working interactive pipeline; now run at scale.
   - Demonstrates: what Omnipy means by engines, and the minimal steps to run with Prefect.
   - Must be honest about current maturity and prerequisites.

### Aspirational features (“aim for” but not claim)

Use a consistent callout style (e.g. “Planned”) for roadmap items:

- simpler converter registration API (roadmap blocker),
- serializer rewrite (roadmap blocker),
- improved table visualization (roadmap item),
- built-in pagination ergonomics for Remote workflows (currently user-land).

Rule: aspirational notes must include the label **Planned** and should not include API signatures
unless they exist.


## 6. Feature overview design (page template)

Each feature page should follow a consistent template to stay skimmable and avoid “wall of text.”

### Template

1. **What it solves (1–3 sentences)**
2. **The idea (short)** — conceptual model
3. **Example (minimal)** — 10–25 lines
4. **Output / display** — show the advantage (docs rendering)
5. **When to use it / when not to** — devil’s advocate inclusion
6. **Gotchas** — footguns and current limitations
7. **Links** — tutorials + how-to + related features

### Required feature pages (v1)

- Continuous validation via type mimicking
- Snapshots & rollback (interactive)
- Declarative conversions (`.to()`)
- Dataset batch processing + hierarchies
- Dataflows (Compute): Tasks/Flows/Modifiers
- Visualization/display primitives (peek/full/json/browse/_docs())
- Components catalog (high-level)
- Engines & orchestration (high-level, honest)

Recommended (v1) feature pages (not all required for Phase 0):

- Pydantic compatibility and Omnipy extensions (trust-builder)
- ChainX: chained model transformations (recipe-driven)
- Domain tabular parsing (row-based): **Now**
- Column-based tabular parsing/validation: **Preview**
- Tabular schemas: Omnipy vs Pandera: **Preview**

Components catalog scope rule:

- v1 catalog page lists only currently bundled components: **General, JSON, Nested, Raw, Remote,
  Tables**.
- Planned plugins/extensions (e.g. ISA, SeqCol, Pandas extraction path) must appear in a separate
  section labeled **Planned**.


## 7. Superhero integration plan (v2+; not in v1)

The poster materials offer powerful metaphors for features. The risk is tone mismatch for
documentation. The plan is to keep v1 neutral and optionally layer narrative elements later.

### v2 integration strategy

1. **Optional “Story mode” toggles**, not default voice.
   - Use MkDocs Material features (tabs/callouts) to provide a collapsible narrative sidebar.
2. **Map metaphors to features (stable mapping)**
   - Optimus Parse → parse & conversions
   - Endless Schema → strict enforcement contracts
   - Merciless Mimic Mantis → continuous validation + rollback
   - Master Zen-Batch → dataset mapping
   - Sir Fetch-a-Lot → remote fetching resilience
   - Visor → display/visualization
3. **Use metaphors as mnemonics** only where they reduce cognitive load.
4. **Tone control:** the primary explanation stays technical; the narrative is a layer.

Future narrative emphasis note:

- The poster narrative strongly emphasizes **AI-related risk** (hallucinated keys/schemas) and
  Omnipy as a boundary/firewall. The v2 story layer should preserve that emphasis even if v1 docs
  only introduce AI-safe boundaries in a neutral, practical way.

### How to prepare v1 to enable v2 later

- Keep landing-page sections modular (distinct include blocks / partials) so a future commit can
  swap in “hero cards” without rewriting the entire page.
- Create a single future-facing page stub in Learn:
   - “Visual metaphors and story mode (**Planned**)” linking to the roster documents.


## 8. Priorities and phasing

### Phase 0 (immediate, highest ROI)

- Replace the “readme-as-index” approach with a designed landing page.
- Create “Start here” + “10-minute Quickstart.”
- Deliver Tutorials 1–3 (interactive safety, JSON→tables, Dataset batch).

#### Phase 0 explicit deliverables (required)

1. `docs/index.md` — New landing page
   - Content: value proposition, 3-bullet why-care, one compelling code snippet, two CTAs,
     compare strip.
   - Minimum acceptance: includes an output-rendering example, includes the JSON-flattening
     caveat with link to Tutorial 2, and includes a minimal non-themed v2 placeholder.
2. `docs/start/install.md` — Installation guide
   - Content: install instructions extracted/updated from existing readme material.
   - Minimum acceptance: clean install path for a new user and link forward to Quickstart.
3. `docs/start/quickstart.md` — 10-minute Quickstart tutorial
   - Content: first end-to-end success path.
   - Minimum acceptance: copy/paste-runnable path to a visible result and “what next” links.
4. `docs/tutorials/01-interactive-safety.md` — Tutorial 1
   - Content: continuous validation + rollback with `interactive` behavior.
   - Minimum acceptance: shows an error, rollback, and continued work.
5. `docs/tutorials/02-json-to-tables.md` — Tutorial 2
   - Content: nested JSON to analysis-ready structures plus current limits.
   - Minimum acceptance: before/after display output and explicit boundary notes.
6. `docs/tutorials/03-dataset-batch.md` — Tutorial 3
   - Content: Dataset mapping/batch semantics replacing explicit loops.
   - Minimum acceptance: one transformation applied across a collection with typed guarantees.
7. `mkdocs.yml` (update) — Phase 0 nav alignment
   - Content: wire the full IA with stub/placeholder pages for deferred sections (not just Phase 0
     pages).
   - Minimum acceptance: local build succeeds, nav paths resolve, and deferred sections have
     placeholder targets.
8. Tutorial execution enforcement in CI (Phase 0 requirement)
   - Content: all tutorials must execute through `markdown-exec` during `mkdocs build` in CI.
   - Fallback rule: async examples that cannot run through `markdown-exec` must be
     copy/paste-runnable and include a clear notebook callout.
   - Minimum acceptance: tutorial code execution is CI-verified via `mkdocs build`.
9. Deferred explicitly in Phase 0:
   - Tutorials 4–8,
   - Feature overview pages,
   - How-to guides,
   - Learn pages.

### Phase 1 (complete the core story)

- Add Feature overview pages using the template.
- Add How-to guides for Models, `.to()`, Datasets, display.
- Add Dataflows (Compute) docs: Tasks/Flows/Modifiers + local engine runnable path.
- Add Tutorial 5 (domain formats, BED/GFF) and file/format parsing guide.
- Add Pydantic compatibility trust-builder page and ChainX/parametrized model recipes.
- Add “Compare / When Omnipy vs alternatives” page (careful, factual tone).

### Phase 2 (scale and ecosystem)

- Prefect tutorial and orchestration overview.
- Components catalog expansion.
- Troubleshooting/FAQ.
- Add Tutorial 7 (AI-safe boundaries) and a template-style guide.
- Column-based tabular parsing/validation docs (**Preview**) and a factual Omnipy vs Pandera page.

### Phase 3 (v2 doc experience)

- Superhero narrative layer (“Story mode”) and hero cards.
- More polished visuals, additional tutorial tracks, and deeper examples.


## 9. Coverage gaps (areas needing documentation)

Based on current docs and roadmap framing, these areas appear under-documented for online docs:

1. **Dataset basics and advanced usage**
   - hierarchical datasets, blueprints, indexing semantics, mapping tasks.
2. **Conversions (`.to()`)**
   - what conversions exist, how to discover them, typical JSON→Pandas workflows.
3. **Display/visualization**
   - `peek/full/json/browse` and `_docs()` output formatting; how to use effectively in notebooks.
4. **Remote/API component**
   - rate limiting, retries/backoff, status handling, and typed outputs.
   - pagination must be documented as **Planned** or user-land loop guidance (not built-in).
5. **Engines & orchestration**
   - local vs Prefect; what “engine” means for the user.
6. **Serialization/persistence**
   - current state (honest), what formats are supported, and roadmap notes (serializer rewrite).
7. **Configuration model**
   - `interactive` flag, runtime config, and how config affects safety/behavior.
   - Correct access paths to document explicitly:
     - `Model.config.model.interactive = False`
     - `runtime.config.data.model.interactive = False`
   - Existing docs using `interactive_mode` are incorrect and should be cleaned up.
8. **Components catalog discoverability**
    - a user-facing index: what components exist and what problem each solves.

9. **Tasks/Flows/Modifiers (Compute layer)**
   - Tasks, the three Flow types (Linear/DAG/Func), and modifier patterns as modular extension.

10. **Domain-specific formats & tabular parsing**
   - BED/GFF style parsers as first-audience, ELIXIR-relevant examples.

11. **Column-based tabular parsing/validation (Pandera-like)** — **Preview**
   - Clarify what exists, what is experimental, and what it enables (including transformation
     patterns that are awkward in pure “validation-only” libraries).

12. **Model ergonomics beyond basics**
   - ChainX and parametrized models: when to use, patterns, and limitations.

13. **AI-safe boundaries**
   - A short, honest guide showing how Models can guard LLM outputs, without claiming a dedicated AI
     framework.


## 10. Roadmap alignment rules

### Documenting what exists vs what’s planned

- **Now:** Document current public APIs and behaviors with runnable examples.
- **Preview:** For features that are implemented and usable today but still under active
  refinement, label them **Preview** and include explicit scope and limits.
- **Planned:** Mention roadmap items only as “Planned” callouts and describe user value, not
  speculative signatures.

### Roadmap-aware caution flags (from v1 roadmap)

- Converter registration API is not yet final/user-friendly → avoid “how to extend conversions” as
  a polished guide; keep it either advanced or **Planned**.
- Serializer mapping is slated for rewrite → document current behavior conservatively and provide a
  “Known limitations” section.
- Better table visualization is a roadmap must-have, but if not yet shipped it must be labeled
  **Planned** in docs while emphasizing current display capabilities.

Pydantic v2 transition note:

- Assume Pydantic v2 support is a target and in active progress. Docs should avoid locking into
  version-specific details that are likely to change during the transition.

### Maturity label definitions

> **Now** = stable, supported, runnable examples — APIs are settled  \
> **Preview** = implemented and usable today, but still under active refinement — docs must state
> scope/limits, APIs may shift  \
> **Planned** = not yet implemented or publicly usable — describe user value only, no speculative
> signatures


## 11. Implementation notes for the doc overhaul (non-binding)

This spec does not prescribe implementation steps, but a few constraints matter for design:

- MkDocs `nav` should be reorganized to match the IA.
- IA/redirect constraint:
  - MkDocs currently uses both hardcoded `nav:` and `literate-nav` (via `SUMMARY.md`), and no
    redirects plugin is in use.
  - No HTTP redirects mechanism/plugin will be added as part of this redesign.
  - Old moved pages should be preserved as manual notice stubs with text in the form:
    “This page has moved to <new page>”, plus a direct link to the new page.
  - Old URL compatibility is best-effort.
- Prefer short pages with cross-links over long monoliths.


## 12. Spec self-review (consistency / ambiguity)

- No superhero tone is introduced in v1; only a preparation plan exists.
- “Planned” callouts are explicitly marked to avoid misrepresenting roadmap items as shipped.
- IA provides two clear on-ramps and prioritizes tutorials.


## Appendix A — Source documents referenced

- Poster abstract: `docs/agents/materials/2026-06-elixir-all-hands-poster/eah-2026-poster-abstract.md`
- Hero roster: `docs/agents/materials/2026-06-elixir-all-hands-poster/roster/eah-2026-poster-heroes-roster.md`
- Villain roster: `docs/agents/materials/2026-06-elixir-all-hands-poster/roster/eah-2026-poster-villains-roster.md`
- Roadmap: `docs/agents/strategy/roadmap/2026-04-02-omnipy-core-features-v1-roadmap.md`
- Landscapes:
  - `docs/agents/strategy/landscape/2026-04-02-ai-pydantic-landscape.md`
  - `docs/agents/strategy/landscape/2026-04-02-omnipy-devils-advocate.md`
  - `docs/agents/strategy/landscape/2026-04-02-omnipy-competitors.md`
- Existing docs:
  - `docs/readme.md`, `docs/index.md`, `docs/data_models.md`, `docs/python_typing.md`,
    `docs/parse_dont_validate.md`
