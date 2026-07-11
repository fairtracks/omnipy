# Async And Sub-Flow Integration Test Slice Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the current async/subflow integration implementation attempt with three readable integration tests that match the approved spec's scenario A, scenario B+C, and separate callable-type / `refine()` / `revise()` validation slice.

**Architecture:** Keep `tests/engine/` as the primary authority for async and nested-flow semantics, and use `tests/integration/novel/full/` only for selective, narrative, user-facing confirmations. Scenario A should exercise real GET-backed `Dataset.load()` / `load_into()` behavior plus a harmonization subflow that normalizes data and uses Omnipy flattening in the integrated path. Scenario B+C should use small Pydantic-backed Omnipy `Model` / `Dataset` types and async adapter tasks for POST-like downstream steps, while keeping those adapters easy to swap later for mock HTTP POST services. The third test should stay separate from the narrative scenarios and cover outer callable-type plus construction / `refine()` / `revise()` validation behavior readably.

**Tech Stack:** Python, pytest, aiohttp test server fixtures, Omnipy `Dataset` / `Model` / flow templates, Pydantic-backed typed models, `PandasDataset`

---

## Relationship to the parent plan

- This document is a rewrite of the prior file at the same path.
- This document merges and supersedes both:
  - the old Task 9 integration-slice authority in `docs/superpowers/plans/2026-07-10-async-and-sub-flow-testing-plan.md`
  - the earlier replacement-plan draft previously saved at this path
- This document is now the sole implementation authority for the integration-test slice.
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
  - Extracted aiohttp app factory, paginated payload builders, and URL/fixture helpers for Scenario A, following the established `tests/components/remote/` aiohttp-server fixture pattern.
- Create: `tests/integration/novel/full/helpers/submission_models.py`
  - Tiny typed `Model` / `Dataset` definitions and normalization-visible Pydantic schemas for Scenario B+C.
- Create: `tests/integration/novel/full/helpers/submission_cases.py`
  - Scenario B+C sample data, manifest/storage fixtures, storage-backed FASTQ references, and adapter-facing expected JSON payload helpers.
- Delete as part of cleanup: `tests/integration/novel/full/test_async_subflow_scenarios.py`
  - Retire the old mixed showcase completely; it must not remain as a fourth overlapping async/subflow narrative test.
- Modify shared files to remove only the superseded async/subflow-specific entries while preserving other still-used coverage:
  - `tests/integration/novel/full/cases/flows.py`
  - `tests/integration/novel/full/cases/raw/flows.py`
  - `tests/integration/novel/full/cases/raw/tasks.py`
- Delete dead files after the shared-file cleanup proves they are no longer referenced:
  - `tests/integration/novel/full/cases/raw/asserts.py`
  - `tests/integration/novel/full/cases/raw/validators.py`
- Retain shared support files that are still used by unrelated integration tests:
  - `tests/integration/novel/full/helpers/models.py`
  - package `__init__.py` files needed by surviving tests
- Leave unrelated existing integration tests in place:
  - `tests/integration/novel/full/test_three_task_flow.py`
  - `tests/integration/novel/full/test_multi_model_dataset.py`

## Shared constraints

- Keep the tests readable enough to seed future docs/tutorial examples.
- Prefer small local helper extraction over large generic harness layers.
- Use explicit support-gap classification (`xfail(strict=True)` or a narrow retained red) when a real claimed-supported gap remains.
- Keep assertions user-facing: outputs, contracts, and observable composition behavior before low-level internals.
- Keep exact spec naming and linkage rules visible in test data and helper names; do not rename the authoritative dataset members or linkage fields.
- Pause for user confirmation if the async-lifting rule is still ambiguous between terminal-child semantics and any-async-child semantics.

## Required slice details carried over from the spec

### Scenario A details that must remain explicit

- Domain story: harmonize river-water and wastewater monitoring batches for the same catchment and monitoring dates.
- Service boundary: use mock HTTP GET services built with extracted helper modules + fixtures, following the existing `tests/components/remote/` aiohttp-server pattern rather than ad-hoc monkeypatching.
- Fetching surface: use real `Dataset.load()` / `load_into()` behavior for the GET side.
- Async shape: one async parent flow with two async source-specific collection tasks; each task may fetch multiple pages asynchronously from one source type.
- Subflow shape: a harmonization subflow normalizes field names and units, then uses Omnipy flattening functionality in the integrated path.
- Output shape: return a Dataset with two `PandasDataset` members named `samples` and `measurements`.

### Scenario B+C details that must remain explicit

- Domain story: broker a sequencing submission package from local metadata + file manifests + storage-backed FASTQ files into fictional downstream services `BioSampleVault` and `Sequence Depot`.
- Required Dataset members:
  - `submission_samples`
  - `submission_files`
  - `submission_metadata`
- Required linkage names:
  - `local_submission_alias` is the internal submission identifier
  - `local_sample_alias` is the internal sample identifier
  - paired-end FASTQ manifest rows link to samples through `local_sample_alias`
  - `submission_metadata` is a single record that also carries included `local_sample_aliases`
- Validation/cleanup must be visible through typed models, including lowercasing local aliases and checking sample/file/metadata linkage consistency.
- Adapter/request boundaries should stay JSON-shaped and isolated so the v1 async task adapters can later be swapped for mock HTTP POST services without rewriting the scenario assertions.
- Final output must be the enriched typed Dataset package plus final receipt/status stored in `submission_metadata`.

### Third validation test details that must remain explicit

- This test is intentionally not scenario-oriented.
- It must cover readable construction-time, `refine()`, and `revise()` variations where child composition changes may require revalidation.
- It must explicitly include the async-lifting rule intended by production code, but only after implementation verifies whether the real rule is “terminal child decides” or “any async child lifts the outer callable type to async.”
- It must not invent a second validation path; any new production validation requirement routes back to the parent plan's Task 8.

## Shared acceptance criteria

- `tests/integration/novel/full/` ends with exactly three canonical async/subflow slice tests: Scenario A, Scenario B+C, and the separate callable-type validation test.
- Scenario A exercises real GET-backed `Dataset.load()` / `load_into()` behavior and Omnipy flattening in one integrated path.
- Scenario A returns a Dataset with `samples` and `measurements` as `PandasDataset` members and asserts representative harmonized rows/values.
- Scenario B+C uses typed Dataset members `submission_samples`, `submission_files`, and `submission_metadata`, with visible normalization and linkage validation around `local_submission_alias`, `local_sample_alias`, and `local_sample_aliases`.
- Scenario B+C stores the final downstream receipt/status back into `submission_metadata` and preserves the orchestration order required by the spec.
- The third test stays readable and non-scenario-oriented, and only asserts validation behavior that already exists or that the parent plan explicitly adds.
- `tests/integration/novel/full/test_async_subflow_scenarios.py` is deleted, not rewritten.
- The old async/subflow implementation attempt under `tests/integration/novel/full/` is retired by deleting the old showcase test, removing its async-subflow-only case/helper entries from shared files, and deleting only those leftover files that become unreferenced afterward.

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
- The extracted mock-service fixtures follow the existing aiohttp-server style already used under `tests/components/remote/`, so the narrative test still uses realistic request/response wiring.

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
- Normalization and validation are visible through the typed models, including lowercase alias cleanup and linkage checks across `local_submission_alias`, `local_sample_alias`, paired-end files, and metadata membership via `local_sample_aliases`.
- Async task adapters enforce the brokering order: metadata cleanup and manifest/storage verification happen before submission-ID creation, transfer completion, BioSampleVault registration, and final Sequence Depot submission.
- The final receipt/status is stored back into `submission_metadata`.
- The helper layout keeps POST-like request/response payloads isolated behind adapter-friendly JSON builders so a later swap to aiohttp mock POST services is local rather than architectural.

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

**What this slice must prove:**
- Linear and DAG flow construction behavior stays readable when callable type depends on child composition.
- `refine()` and `revise()` cases cover the meaningful composition-change variations without turning into another scenario story.
- The intended async-lifting rule is verified against the actual production rule before the expectation is hardened.
- If Task 8 in the parent plan introduced a narrow validation seam, this test is the readable integration-level confirmation of that seam; if not, it must only assert already-supported behavior.
- The test includes the third validation requirement from the spec: construction-time behavior plus child-composition revalidation during both `refine()` and `revise()`.

**User-facing acceptance criteria:**
- The test is clearly separated from domain-story scenarios and can be read as a callable-type behavior guide.
- Construction-time, `refine()`, and `revise()` expectations are explicit and low-noise.
- No second validation path is invented in integration code; any new production validation requirement pauses and routes back to the parent plan.

**Verification target:**
- `uv run pytest tests/integration/novel/full/test_flow_callable_type_validation.py -v --mypy-pyproject-toml-file=pyproject.toml`

### Task 4: Remove the superseded integration implementation attempt and verify the new slice is the only canonical narrative coverage

**Files:**
- Delete: `tests/integration/novel/full/test_async_subflow_scenarios.py`
- Modify to remove only async/subflow-scenario entries that supported the deleted showcase test:
  - `tests/integration/novel/full/cases/flows.py`
  - `tests/integration/novel/full/cases/raw/flows.py`
  - `tests/integration/novel/full/cases/raw/tasks.py`
- Delete if left unreferenced after that cleanup:
  - `tests/integration/novel/full/cases/raw/asserts.py`
  - `tests/integration/novel/full/cases/raw/validators.py`
- Retain because other tests still use them:
  - `tests/integration/novel/full/helpers/models.py`
  - package `__init__.py` files required by surviving tests

**What this slice must prove:**
- The current implementation attempt is actually retired rather than left beside the new tests as confusing duplicate coverage.
- The end state is unambiguous: the old showcase test is deleted, not rewritten or reduced.
- Shared support modules are trimmed only where they carried async-subflow-scenario-specific entries for the deleted test; shared support still needed by `test_three_task_flow.py` and `test_multi_model_dataset.py` remains in place.
- Imports, helper references, and package layout remain coherent after the cleanup.

**Verification target:**
- `uv run pytest tests/integration/novel/full/test_environmental_monitoring_harmonization.py tests/integration/novel/full/test_sequence_submission_brokering.py tests/integration/novel/full/test_flow_callable_type_validation.py -v --mypy-pyproject-toml-file=pyproject.toml`

## Sequencing and coordination notes

- Implement Task 1 first if the repo still needs a clean `Dataset.load()` + async subflow exemplar.
- Implement Task 2 second; it is the most helper-heavy slice but independent from callable-type validation semantics.
- Implement Task 3 last so its expectations can align with the final Task 8 outcome from the parent plan, if that seam was needed.
- Implement Task 4 before final handoff so the superseded files are gone by the time this slice is reported complete.

## User Check-in markers

- **User Check-in A:** Pause if Task 3 cannot determine the intended async-lifting rule from existing code plus the approved spec.
- **User Check-in B:** Pause if any of the three integration tests needs a production change broader than the small validation/testability seams already allowed by the spec.

## Spec-to-plan self-check

- Scenario A matches the spec's mock GET + `Dataset.load()` + flattening requirement.
- Scenario B+C matches the typed Dataset brokering requirement, preserves the exact dataset member and linkage names, and keeps async service boundaries adapter-based for v1 with a future mock-POST swap seam.
- The third test is separated from the narrative scenarios and is explicitly tied to construction / `refine()` / `revise()` validation behavior, including the async-lifting ambiguity check.
- The plan now explicitly includes cleanup/removal of the current `tests/integration/novel/full/` async/subflow implementation attempt.
- The plan keeps integration coverage selective and readable rather than duplicating the engine harness.
