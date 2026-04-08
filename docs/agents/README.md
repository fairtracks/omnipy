# docs/agents

Home for durable AI-generated working documents.

## Canonical top-level directories

- `technical/`
- `process/`
- `strategy/`
- `documentation/`
- `materials/`
- `concepts/`
- `other/`

Do not add new top-level directories unless explicitly instructed.

## Canonical subdirectories

### `technical/`

- `explorations/`
- `specs/`
- `plans/`
- `implementation/`
- `reviews/`
- `other/`

Use `technical/` for documents about building, changing, or evaluating Omnipy itself.

### `process/`

- `explorations/`
- `specs/`
- `plans/`
- `reviews/`
- `other/`

Use `process/` for documents about how work is organized or executed.

### `documentation/`

- `explorations/`
- `specs/`
- `plans/`
- `reviews/`
- `other/`

Use `documentation/` for working docs that support user or developer documentation, not for the canonical published docs.

### Shared lifecycle subdirectories

These meanings apply wherever these subdirectories are used:

- `explorations/`: investigate options, tradeoffs, or open questions before committing.
- `specs/`: define intended behavior, structure, scope, or rules.
- `plans/`: describe how work should be carried out.
- `implementation/`: implementation-related notes tied to concrete engineering work. Currently canonical only under `technical/`.
- `reviews/`: review, critique, audit, or evaluate designs, plans, docs, processes, or outcomes.
- `other/`: fallback for docs in that topic area that do not fit the categories above.

### `concepts/`

`concepts/` is topic-structured. Use it for reusable ideas that are not tied mainly to one concrete material output. Agents may add self-explanatory topic subdirectories here when clearly needed.

### `strategy/`

`strategy/` is topic-structured. Current canonical subdirectories:

- `roadmap/`
- `landscape/`
- `other/`

Agents may add self-explanatory topic subdirectories here when clearly needed.

Use `strategy/` for direction-setting and framing docs.

- `roadmap/`: plans or direction docs about where Omnipy is going.
- `landscape/`: competitor, ecosystem, audience, or positioning analysis.

### `materials/`

Use `materials/` for concrete outputs or working docs tied mainly to one deliverable, event, meeting, poster, talk, paper, or submission.

All `materials/` subdirectories should be date-first. Use `YYYY-MM`, typically based on the most relevant event date, delivery date, or creation date. If no event or delivery date is clearly relevant, use the creation date.

Examples:

- `2025-06-eah-poster/`
- `2026-09-project-meeting/`

Inside each material directory, prefer descriptive filenames even when the path already provides context, for example `eah-2026-poster-abstract.md`.

Do not invent additional shared subdirectories under `materials/` unless instructed.

### `other/`

Use `other/` sparingly for anything that clearly does not fit elsewhere.

## Filing rule

File documents by primary purpose or reuse context:

- building or changing Omnipy itself -> `technical/`
- improving how work gets done -> `process/`
- landscapes, roadmaps, and strategic framing -> `strategy/`
- working docs for user or developer documentation -> `documentation/`
- concrete deliverables or deliverable-bound work -> `materials/`
- reusable cross-material ideas -> `concepts/`

## Date prefix policy

To make document age easier to judge, document filenames or their parent directories should start with a date prefix.

Use one of these formats:

- `YYYY-MM`
- `YYYY-MM-DD`

Examples:

- `2026-05-limit-peek-elements-design.md`
- `2026-05-19-limit-peek-elements-design.md`
- `materials/2026-05-eah-poster/eah-2026-poster-abstract.md`

For material bundles, put the date on the parent directory.

For standalone docs, put the date on the filename unless the parent directory already provides it.

Date prefixes can also be useful on non-material directories when the date meaningfully describes the whole document collection.

## Drafts sidecar convention

When earlier versions should be kept, store them in a sidecar `drafts/` directory next to the current doc.

Examples:

- `some-doc.md`
- `drafts/some-doc_v1.md`
- `drafts/some-doc_v2.md`

Use `drafts/` only when needed, across any directory type.

## Directory creation policy

- Only create directories that are already canonical or explicitly requested.
- Do not add new directories just because a document could fit multiple ways.
- Except for `strategy/` and `concepts/`, do not create new category subdirectories unless instructed.

