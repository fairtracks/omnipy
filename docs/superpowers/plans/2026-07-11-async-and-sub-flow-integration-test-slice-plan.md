# Async And Sub-Flow Integration Test Slice Replacement Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the old mixed async/subflow showcase with three readable integration tests that cover the new spec's scenario A, scenario B+C, and separate callable-type / `refine()` / `revise()` validation slice.

**Architecture:** Keep `tests/engine/` as the primary authority for async and nested-flow semantics, and use `tests/integration/novel/full/` only for selective, narrative, user-facing confirmations. The integration slice should stay small, readable, and helper-driven: Scenario A proves real GET + `Dataset.load()` + flattening, Scenario B+C proves typed Dataset brokering with async adapters, and the third test isolates composition-validation behavior without re-running the engine matrix.

**Tech Stack:** Python, pytest, aiohttp test server fixtures, Omnipy `Dataset` / `Model` / flow templates, Pydantic-backed typed models, `PandasDataset`

---

## Relationship to the parent plan

- This document fully replaces Task 9 in `docs/superpowers/plans/2026-07-10-async-and-sub-flow-testing-plan.md`.
- The binding requirements source remains `docs/superpowers/specs/2026-07-09-async-and-sub-flow-testing-schema-design.md`.
- This slice must not recreate the engine-harness matrix; it confirms representative user-facing behavior only.
- If the third test reveals missing construction-time or `refine()` / `revise()` validation behavior, route that gap back to the parent plan's Task 8 instead of inventing a new integration-only production seam.

## File map

- Create: `tests/integration/novel/full/test_environmental_monitoring_harmonization.py`
  - Scenario A narrative integration test.
- Create: `tests/integration/novel/full/test_sequence_submission_brokering.py`
  - Scenario B+C narrative integration test.
- Create: `tests/integration/novel/full/test_flow_callable_type_validation.py`
  - Separate readable validation-oriented integration test.
- Create: `tests/integration/novel/full/helpers/monitoring_services.py`
  - Extracted aiohttp app factory, payload builders, and URL/fixture helpers for Scenario A.
- Create: `tests/integration/novel/full/helpers/submission_models.py`
  - Tiny typed `Model` / `Dataset` definitions and normalization-visible schemas for Scenario B+C.
- Create: `tests/integration/novel/full/helpers/submission_cases.py`
  - Scenario B+C sample data, manifest/storage fixtures, and adapter-facing expected payload helpers.
- Modify or remove: `tests/integration/novel/full/test_async_subflow_scenarios.py`
  - Remove the old mixed showcase once the three new files cover its intended value more readably.

## Shared constraints

- Keep the tests readable enough to seed future docs/tutorial examples.
- Prefer small local helper extraction over large generic harness layers.
- Use explicit support-gap classification (`xfail(strict=True)` or a narrow retained red) when a real claimed-supported gap remains.
- Keep assertions user-facing: outputs, contracts, and observable composition behavior before low-level internals.
- Pause for user confirmation if the async-lifting rule is still ambiguous between terminal-child semantics and any-async-child semantics.

## Shared acceptance criteria

- `tests/integration/novel/full/` contains exactly three new canonical async/subflow slice tests: Scenario A, Scenario B+C, and the separate callable-type validation test.
- Scenario A exercises real GET-backed `Dataset.load()` / `load_into()` behavior and Omnipy flattening in one integrated path.
- Scenario B+C uses typed Dataset members `submission_samples`, `submission_files`, and `submission_metadata`, with visible normalization and linkage validation.
- The third test stays readable and non-scenario-oriented, and only asserts validation behavior that already exists or that the parent plan explicitly adds.
- The old `test_async_subflow_scenarios.py` showcase is removed or reduced so it is no longer the canonical coverage entry point for this slice.

### Task 1: Scenario A — environmental monitoring harmonization

**Test level:** Integration/contract test with real mock-HTTP GET traffic and real dataset loading behavior.

**Files:**
- Create: `tests/integration/novel/full/test_environmental_monitoring_harmonization.py`
- Create: `tests/integration/novel/full/helpers/monitoring_services.py`

**What this slice must prove:**
- One async parent flow coordinates two async source-specific collection tasks.
- Each source task can fetch multiple pages asynchronously from its mocked GET service.
- A harmonization subflow normalizes field names and units, then uses Omnipy flattening in the integrated path.
- The final result is a Dataset containing `samples` and `measurements` as `PandasDataset` members.

**User-facing acceptance criteria:**
- Representative harmonized rows show river-water and wastewater records aligned by catchment/date semantics.
- The test demonstrates that the REST boundary, `Dataset.load()` / `load_into()`, flattening, and subflow composition all work together.
- Assertions stay focused on the returned two-table dataset and representative normalized values rather than engine-internal mechanics.

**Verification target:**
- `uv run pytest tests/integration/novel/full/test_environmental_monitoring_harmonization.py -v --mypy-pyproject-toml-file=pyproject.toml`

### Task 2: Scenario B+C — sequence submission brokering

**Test level:** Integration/contract test with typed in-memory datasets and async task adapters standing in for POST-like downstream services.

**Files:**
- Create: `tests/integration/novel/full/test_sequence_submission_brokering.py`
- Create: `tests/integration/novel/full/helpers/submission_models.py`
- Create: `tests/integration/novel/full/helpers/submission_cases.py`

**What this slice must prove:**
- The workflow starts from typed local metadata, file manifests, and storage-backed FASTQ references.
- The Dataset package contains `submission_samples`, `submission_files`, and `submission_metadata`.
- Normalization and validation are visible through the typed models, including lowercase alias cleanup and linkage checks across `local_submission_alias`, `local_sample_alias`, paired-end files, and metadata membership.
- Async task adapters enforce the brokering order: metadata cleanup and manifest/storage verification happen before submission-ID creation, transfer completion, BioSampleVault registration, and final Sequence Depot submission.
- The final receipt/status is stored back into `submission_metadata`.

**User-facing acceptance criteria:**
- The test reads like a small end-user workflow, not a transport harness demo.
- The final dataset package is enriched with downstream identifiers/receipt data while preserving typed validation guarantees.
- Assertions show both data cleanup and orchestration ordering, without pretending that real third-party HTTP integrations already exist.

**Verification target:**
- `uv run pytest tests/integration/novel/full/test_sequence_submission_brokering.py -v --mypy-pyproject-toml-file=pyproject.toml`

### Task 3: Separate integration test — callable-type and `refine()` / `revise()` validation

**Test level:** Readable integration/contract test focused on outer flow behavior when child composition changes.

**Files:**
- Create: `tests/integration/novel/full/test_flow_callable_type_validation.py`
- Modify or remove: `tests/integration/novel/full/test_async_subflow_scenarios.py`

**What this slice must prove:**
- Linear and DAG flow construction behavior stays readable when callable type depends on child composition.
- `refine()` and `revise()` cases cover the meaningful composition-change variations without turning into another scenario story.
- The intended async-lifting rule is verified against the actual production rule before the expectation is hardened.
- If Task 8 in the parent plan introduced a narrow validation seam, this test is the readable integration-level confirmation of that seam; if not, it must only assert already-supported behavior.

**User-facing acceptance criteria:**
- The test is clearly separated from domain-story scenarios and can be read as a callable-type behavior guide.
- Construction-time, `refine()`, and `revise()` expectations are explicit and low-noise.
- No second validation path is invented in integration code; any new production validation requirement pauses and routes back to the parent plan.

**Verification target:**
- `uv run pytest tests/integration/novel/full/test_flow_callable_type_validation.py -v --mypy-pyproject-toml-file=pyproject.toml`

## Sequencing and coordination notes

- Implement Task 1 first if the repo still needs a clean `Dataset.load()` + async subflow exemplar.
- Implement Task 2 second; it is the most helper-heavy slice but independent from callable-type validation semantics.
- Implement Task 3 last so its expectations can align with the final Task 8 outcome from the parent plan, if that seam was needed.

## User Check-in markers

- **User Check-in A:** Pause if Task 3 cannot determine the intended async-lifting rule from existing code plus the approved spec.
- **User Check-in B:** Pause if any of the three integration tests needs a production change broader than the small validation/testability seams already allowed by the spec.

## Spec-to-plan self-check

- Scenario A matches the spec's mock GET + `Dataset.load()` + flattening requirement.
- Scenario B+C matches the typed Dataset brokering requirement and keeps async service boundaries adapter-based for v1.
- The third test is separated from the narrative scenarios and is explicitly tied to construction / `refine()` / `revise()` validation behavior.
- The plan keeps integration coverage selective and readable rather than duplicating the engine harness.
