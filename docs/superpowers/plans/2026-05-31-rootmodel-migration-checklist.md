# RootModel Migration Checklist (Omnipy `Model`)

## Goal

Migrate `omnipy.data.model.Model` from the current `GenericModel`/`BaseModel` compat layer to a true
Pydantic v2 `RootModel`-based implementation **without** losing Omnipy’s parse-oriented behavior
(including cross-model conversion semantics), and with concrete acceptance criteria for each step.

## Pre-analysis findings from current codebase

### A. Current `Model` architecture (what exists today)

- `Model` inherits `pyd.GenericModel` (`src/omnipy/data/model.py`) and uses a custom metaclass:
  `ModelMetaclass(DataClassBaseMeta, pyd.ModelMetaclass)`.
- Root behavior is emulated via `__root__` + a compat alias to `root` in
  `src/omnipy/util/pydantic.py::_GenericModelCompatMeta`.
- `Model.__class_getitem__()` manually invokes `BaseModel.__class_getitem__` and then mutates
  `model_fields['root']`, sets `orig_model` metadata, cleans class names, and injects special-method
  mimics (`_prepare_cls_members_to_mimic_model`).
- Parsing pipeline relies on before-validators that currently expect dict payloads with `ROOT_KEY='root'`:
  `_generous_iterable_support()` and `_parse_root_object()`.
- Omnipy conversion policy is currently implemented in constructor/helpers, not only in pydantic schema:
  `_prepare_value_for_validation_if_dataset_or_model()`, fallback `_secondary_validation_from_data()`,
  `from_data()`, `_validate_content_from_value()`.

### B. Current cross-model assumptions explicitly present in tests

- `Model[int](Model[float](4.5)).to_data() == 4` (`tests/data/test_model.py`).
- `Model[Model[int]](Model[float](4.5)).to_data() == 4`.
- Many tests depend on parse/coercion behavior and dynamic conversion toggles.

### C. RootModel feasibility findings (validated by direct probes)

- `RootModel` supports:
  - generic specialization (`RootModel[T]` subclasses),
  - recursive models (`RootModel[str | list[Self]]`),
  - `@model_validator(mode='before')`,
  - `__get_pydantic_core_schema__` customization.
- Cross-model equivalence can be reintroduced on top of `RootModel` by a base-class core-schema
  pre-validator that normalizes inputs (e.g. other Omnipy models via `to_data()`, legacy
  `{'__root__': ...}`/`{'root': ...}` payloads) before core validation.

---

## Checklist

> Format: each item includes concrete change scope + acceptance criteria.

### 1) Introduce RootModel in pydantic compat layer

- [ ] Export `RootModel` (and any related typing helpers needed) from `src/omnipy/util/pydantic.py`.
- [ ] Keep existing public imports stable where possible (`pyd.RootModel` access path).

**Acceptance criteria**

- `omnipy.util.pydantic` exposes a RootModel symbol used by `Model`.
- No import-cycle regressions in `src/omnipy/data/model.py` and dependent modules.

### 2) Rebase `Model` inheritance onto RootModel

- [ ] Change `Model` to inherit from RootModel-based base (instead of `pyd.GenericModel`).
- [ ] Preserve `DataClassBase` and `ModelDisplayMixin` integration.
- [ ] Decide whether custom metaclass remains needed; if needed, adapt it to RootModel’s metaclass type.

**Acceptance criteria**

- `Model[int]`, subclassed models (`class X(Model[int])`), and generic subclasses (`class X(Model[T], ...)`) still construct.
- `cleanup_name_qualname_and_module` behavior remains consistent with existing naming tests.

### 3) Replace `__root__` emulation with native root semantics

- [ ] Remove dependency on `__root__` alias trick in model internals.
- [ ] Keep compatibility handling only where required for migration inputs (not as core representation).
- [ ] Update `_get_pydantic_root_key()` and call sites to align with RootModel-native behavior.

**Acceptance criteria**

- Internal storage is native RootModel (`root`), while Omnipy API continues to expose `.content`.
- Model creation works from plain root values without dict wrappers.

### 4) Rewrite `Model.__class_getitem__()` for RootModel path

- [ ] Remove GenericModel-specific assumptions (manual `BaseModel.__class_getitem__` call pattern).
- [ ] Preserve:
  - storing/retrieving `orig_model` metadata,
  - class-name cleanup,
  - special-method mimic injection,
  - cache invalidation (`_clean_type_caches`).

**Acceptance criteria**

- `Model[dict[str, Model[None]]]`, nested/union/generic combinations still create concrete classes.
- `get_orig_model()/set_orig_model()` still track original type form across inheritance chains.

### 5) Rework constructor and validation entrypoints for RootModel

- [ ] Simplify `__init__` to RootModel input contract while preserving Omnipy positional/keyword ergonomics.
- [ ] Remove v1/v2 compat hacks that exist only due to GenericModel dict-input semantics.
- [ ] Keep/replace `_secondary_validation_from_data()` only if still needed after root-native path.

**Acceptance criteria**

- Existing call forms still work (except explicitly removed legacy hacks):
  - `Model[T](value)`
  - `Model[dict](a=1, b=2)`
  - model/dataset inputs where supported.
- Default-value initialization behavior remains equivalent for empty construction.

### 6) Port before-validators from dict-root input to RootModel input

- [ ] Rewrite `_generous_iterable_support()` and `_parse_root_object()` signatures/logic to accept raw root input.
- [ ] Ensure `parse_none_according_to_model()` is invoked at the right stage for RootModel input.
- [ ] Ensure parser hooks (`_parse_data`) still run before strict model typing is finalized.

**Acceptance criteria**

- Iterable coercion tests still pass for non-string iterables.
- Parse hooks for component models (e.g. raw/json/table models) continue to run with expected input types.

### 7) Implement cross-model equivalence via core-schema hook (parse policy)

- [ ] Add `Model.__get_pydantic_core_schema__` pre-validator that normalizes accepted inputs before root validation:
  - Omnipy `Model` instances -> `to_data()`
  - Omnipy `Dataset` instances -> `to_data()` (where relevant)
  - non-Omnipy pydantic models -> `model_dump(by_alias=True)`
  - compatibility payloads `{'__root__': x}` / optionally `{'root': x}` -> `x`
- [ ] Keep behavior deterministic and branch-local (no global recursive prewalk).

**Acceptance criteria**

- `Model[int](Model[float](4.5))` coercion behavior remains (subject to target type rules).
- `Union[str, SomeModel]` style parsing accepts root-shaped list/scalar inputs when `SomeModel` should match.
- Recursive union cases (e.g. nested list/string models) accept `[]`, `['a']`, `['a', ['b']]` where type permits.

### 8) Preserve Omnipy API surface (`content`, `to_data`, `from_data`, special methods)

- [ ] Map `.content` property cleanly onto RootModel `.root` while preserving current semantics.
- [ ] Verify `_get_real_content()` behavior for model-of-model cases.
- [ ] Revalidate special-method mimic logic (`_special_method`, conversion-on-ops) under RootModel internals.

**Acceptance criteria**

- Existing API consumers still use `.content`; `.root` remains implementation detail/pydantic-facing.
- Special-method behavior in `tests/data/test_model.py` remains equivalent.

### 9) Update serialization and schema behaviors

- [ ] Reconcile `to_data()`, `dict()`, `to_json()`, `to_json_schema()` with RootModel-native `model_dump` behavior.
- [ ] Remove schema hacks that only existed for `__root__` compatibility.

**Acceptance criteria**

- `to_data()/from_data()` round-trips remain stable.
- JSON component behavior remains correct (including flattening/default-key flows where applicable).

### 10) Forward refs and rebuild flow

- [ ] Ensure `update_forward_refs()` wrapper continues to work (internally using `model_rebuild`).
- [ ] Verify parent-class propagation logic remains valid with RootModel.

**Acceptance criteria**

- Forward-ref tests in `tests/data/test_model.py` continue to pass.
- Recursive model definitions requiring deferred rebuild still work.

### 11) Update tests and compatibility assertions explicitly tied to `__root__`

- [ ] Replace/adjust tests that assert `__fields_set__ == {'__root__'}` and other legacy `__root__` internals.
- [ ] Keep behavioral assertions; remove implementation-detail assertions no longer valid by design.
- [ ] Update JSON tests that instantiate private pydantic models via `__root__=...` if needed.

**Acceptance criteria**

- No remaining test depends on `__root__` internal representation unless intentionally retained as migration-compat behavior.
- Behavioral expectations (parse/coerce/roundtrip) remain covered.

### 12) Dataset and dependent subsystem compatibility audit

- [ ] Audit and update call sites that assume GenericModel/BaseModel root-wrapper details:
  - `src/omnipy/data/dataset.py`
  - `src/omnipy/components/tables/models.py` (metaclass + pydantic field access)
  - `src/omnipy/components/json/*` (default key and shape assumptions)
  - any code using `__fields__` or root-wrapper specific dumps.

**Acceptance criteria**

- Dataset<Model[...]> parsing/serialization still works for nested datasets and multi-model datasets.
- Table/json component tests pass under RootModel migration branch.

### 13) Validation utility cleanup in `omnipy.util.pydantic`

- [ ] Remove or simplify GenericModel compat metaclass features no longer needed.
- [ ] Update `validate_model()` root handling to RootModel-native input/output conventions.
- [ ] Ensure error wrapping still yields useful locations/messages.

**Acceptance criteria**

- `pyd.validate_model(...)` callers in Model/Params paths continue to function.
- Error messages remain at least as actionable as current output.

### 14) Tracer-bullet sequence (recommended implementation order)

- [ ] Slice 1: minimal RootModel `Model[int]` + `.content` + `to_data/from_data` + passing core `test_init_and_data`.
- [ ] Slice 2: cross-model equivalence hook + `test_init_model_as_input`.
- [ ] Slice 3: recursive/union heavy raw/json cases (including failing `SplitLinesToColumns`/nested list paths).
- [ ] Slice 4: broad dataset/component stabilization.

**Acceptance criteria**

- Each slice introduces failing tests first and turns them green before next slice.
- No slice proceeds with unresolved regressions in prior slice.

### 15) Performance and regression gates

- [ ] Benchmark representative parse paths before/after (especially union-heavy and nested-model inputs).
- [ ] Confirm that schema-hook solution does not introduce unacceptable overhead versus current v2 baseline.
- [ ] Run full repo verification command once migration slice set is complete.

**Acceptance criteria**

- Performance is not worse than current branch in key parse workloads without documented justification.
- Full test suite passes at migration completion gate.

---

## “Done” definition for RootModel migration

- `Model` is RootModel-based in core architecture.
- Omnipy parse-oriented semantics (including cross-model conversion policy) are preserved by explicit,
  tested mechanisms.
- `__root__` as internal implementation detail is removed or retained only as intentional compatibility shim.
- Model/Dataset/component test suites pass with updated, behavior-focused assertions.
