# Omnipy — Pydantic v2 native migration (design/spec)

Date: 2026-05-29
Worktree/branch: `work/pydantic-v2-migration` / `pydantic-v2-migration`

## Goal

Migrate Omnipy to **native Pydantic v2 APIs** while preserving Omnipy’s **public behavior** as a hard requirement.

Key constraint decisions (approved):

- **Drop Pydantic v1 entirely** (no `pydantic.v1` usage).
- Keep `omnipy.util.pydantic` as a **single internal import facade**, but make it **v2-only**.
- Keep **Prefect `<3`**, but **bump Prefect to the latest 2.x** version compatible with Pydantic v2.

## Non-goals

- No separate “TODO sweep” for Pydantic-v2-related TODOs; only address TODOs encountered in code we must change.
- No redesign of Omnipy’s data model concepts (`Model`, `Dataset`, snapshots, etc.) beyond what is required to preserve behavior under Pydantic v2.
- No Prefect 3 migration.

## Scope (what must change)

Omnipy currently embeds significant Pydantic v1 patterns and even v1 internal APIs, including:

- Decorators: `@validator`, `@root_validator`.
- Configuration: nested `class Config`, `validate_all`, `smart_union`, etc.
- Serialization: `.dict()`, `.json()`.
- Model internals: `__fields__`, `ModelField`, `validate_model`, `ErrorWrapper`, and manual `ValidationError(...)` construction.

Under Pydantic v2, the migration will standardize on:

- Validation: `model_validate`, `TypeAdapter.validate_python`, `model_validate_json` (where appropriate).
- Serialization: `model_dump`, `model_dump_json`, `model_copy`.
- Validators: `@field_validator`, `@model_validator`.
- Config: `model_config = ConfigDict(...)` / `ConfigDict` values.
- Field metadata: `model_fields` (v2) rather than `__fields__`.
- Error semantics: v2-native error types and/or adapter helpers (see “Facade responsibilities”).

Primary high-churn areas (expected):

- `src/omnipy/util/pydantic.py` (must become v2-only; remove `pydantic.v1` conditional path).
- Core models/datasets:
  - `src/omnipy/data/model.py`
  - `src/omnipy/data/dataset.py`
  - `src/omnipy/data/param.py`
- Config + publish/subscribe:
  - `src/omnipy/util/publisher.py` (uses `__fields__`)
  - `src/omnipy/config/**`
- Components that heavily use validators/forward refs:
  - `src/omnipy/components/json/**`
  - `src/omnipy/components/isa/**`
- Display panels/dataclasses using Pydantic dataclasses + validators:
  - `src/omnipy/data/_display/**`

## Facade responsibilities (`omnipy.util.pydantic`)

The facade remains the single “approved import location” for the rest of Omnipy.

It will:

1. Re-export the Pydantic v2 APIs used throughout Omnipy (e.g. `BaseModel`, `Field`, `ConfigDict`, `PrivateAttr`, `ValidationError`, decorators, etc.).
2. Provide small **Omnipy-specific compatibility helpers** that replace v1-only internals currently depended upon, specifically:
   - A v2-native equivalent for places where Omnipy currently calls `validate_model`.
   - A v2-native way to build/raise validation errors that preserves Omnipy error messages/structure where tests assert them.
   - Any “type inspection helpers” currently imported from v1 internals (`lenient_isinstance`, `lenient_issubclass`, etc.) must be replaced with v2-supported alternatives or local implementations.

The facade must not:

- Import or reference `pydantic.v1`.

## Behavior compatibility contract

“Public behavior compatibility” means:

- Same accept/reject behavior for inputs to `Model[...]` and `Dataset[...]` specializations, including coercions that Omnipy historically relied on.
- Same snapshot/rollback behavior and “none is not allowed” semantics (Omnipy currently raises `OmnipyNoneIsNotAllowedError` derived from a v1 error type).
- Same serialization output shape for the public surfaces that tests cover (notably `.dict(by_alias=True)` equivalents, JSON formatting behavior where asserted, and schema generation where used).

If Pydantic v2 makes an exact equivalence impractical, we must **pause and raise the specific delta** (with minimal reproduction + proposed mitigation options) for user decision.

## Dependency constraints

- Update `pydantic` dependency to a v2 constraint (exact floor TBD during implementation, but must be v2).
- Update Prefect to the **latest release that is still `<3`** and compatible with Pydantic v2.
- Reconcile any transitive constraints (including anything pulling in v1-only behavior).

## Risks / known hard points

1. **Manual error construction:** code currently uses v1 `ErrorWrapper` and `ValidationError` constructors directly (e.g. dataset-level aggregated validation failures). v2 error representation differs.
2. **Model/Dataset metaclass hacks:** there are v1-specific hacks (e.g. `ModelMetaclass.__instancecheck__` notes, dataset “union hack”, `pydantic_v1_hack()`). These must be re-evaluated for v2 and either removed or replaced.
3. **Field and model metadata:** `__fields__` → `model_fields` differences affect publisher/subscriptions and Params metaclass behavior.
4. **Validator ordering/semantics:** v2 validator phases differ; root/field validators must be carefully mapped to preserve behavior.
5. **JSON/recursive models:** Omnipy’s JSON model hierarchy currently contains v1-era workarounds and forward-ref update patterns; v2 may simplify some of these but we will avoid “nice-to-have” refactors unless required for correctness.

## Acceptance criteria (definition of done for the transition)

- No `pydantic.v1` imports or runtime usage anywhere in `src/`.
- `omnipy.util.pydantic` is v2-only and is the primary Pydantic import surface.
- Prefect is bumped to latest `<3`.
- Full verification passes:
  - `uv run pytest -v --mypy-only-local-stub --mypy-pyproject-toml-file=pyproject.toml --mypy-same-process`
- Any unavoidable behavior changes are documented and explicitly approved before landing.

## Out-of-scope cleanup policy

There are multiple TODOs about Pydantic v2 across the repo. During this migration:

- Only fix/remove a TODO if it is in code we must change to make v2 work.
- Do not perform a separate TODO sweep.

## Open questions (to resolve during implementation)

- What is the minimal v2-compatible replacement for:
  - `validate_model`
  - v1 `ErrorWrapper`-based aggregated errors
  - `NoneIsNotAllowedError` inheritance used by `OmnipyNoneIsNotAllowedError`
- Which v1 workarounds become unnecessary under v2 and can be removed without changing public behavior?
