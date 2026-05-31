# RootModel Migration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Migrate `omnipy.data.model.Model` from the current `GenericModel`/`BaseModel` compat layer to pydantic v2 `RootModel` while preserving Omnipy parsing semantics, eager `to_data()` conversion behavior, and downstream Dataset/component behavior.

**Architecture:** Rebase `Model` onto native `pyd.RootModel` and keep Omnipy behavior by normalizing inputs at the `Model` boundary instead of relying on `__root__`-dict emulation. Preserve the public Omnipy API by treating `.content` as the stable API, `.root` as the pydantic-facing implementation detail, and by keeping cross-model / dataset / pydantic-model conversion explicit in a RootModel schema hook plus before-validators.

**Tech Stack:** Python, `uv`, pytest, pydantic v2 `RootModel`, `pydantic_core.core_schema`, Omnipy `DataClassBase`/metaclass helpers, repo mypy-plugin pytest flags.

---

## Non-negotiable migration constraints

- Preserve current eager `to_data()` conversion behavior. Do **not** change conversion policy during this migration.
- Preserve Omnipy call ergonomics:
  - `Model[T](value)`
  - `Model[dict](a=1, b=2)`
- `Model[T](__root__=12)`-style migration compatibility input only
- Preserve `.content` as the public API.
- Accept legacy root-wrapper payloads (`{'__root__': x}` and `{'root': x}`) only as compatibility inputs, not as the internal representation.
- Keep `cleanup_name_qualname_and_module()`, `orig_model` tracking, special-method mimic injection, and `update_forward_refs()` behavior.
- Do not change Dataset to `RootModel`; only stabilize Dataset against the new `Model` internals.

## File map and responsibilities

- `src/omnipy/util/pydantic.py`
  - Export `RootModel` / RootModel metaclass helpers.
  - Update `validate_model()` and root-model compatibility helpers so RootModel callers receive native-root values.
- `src/omnipy/data/model.py`
  - Rebase `Model` inheritance, metaclass, `__class_getitem__()`, constructor, validators, schema hook, serialization, copy helpers, and forward-ref rebuild flow.
- `src/omnipy/data/dataset.py`
  - Replace remaining v1 field access assumptions and ensure Dataset copies / validation / nested `Model` interactions still work.
- `src/omnipy/data/param.py`
  - Verify Params continues to use `pyd.validate_model()` correctly after RootModel compatibility changes.
- `src/omnipy/components/json/models.py`
  - Keep JSON parse hooks functioning with raw RootModel input.
- `src/omnipy/components/json/constants.py`
  - Preserve external default-key behavior unless tests prove a change is safe and explicitly desired.
- `src/omnipy/components/tables/models.py`
  - Replace `__fields__` access with v2-safe field inspection (`model_fields`, `is_required()`, `get_default()`).
- `tests/data/test_model.py`
  - Primary tracer-bullet and regression suite for Model semantics.
- `tests/data/test_dataset.py`
  - Dataset compatibility regressions.
- `tests/components/raw/test_models.py`
  - Raw parsing hooks / recursive list parsing regressions.
- `tests/components/json/test_json_models.py`
  - JSON model consistency and root-shape regressions.
- `tests/components/tables/test_models.py`
  - Table / pydantic-record integration regressions.

## Baseline capture (run once before Task 1)

- [ ] Install deps and record the pre-migration baseline

Run:

```bash
uv sync --all-groups
```

Expected: environment sync completes without dependency errors.

- [ ] Record a focused behavioral baseline

Run:

```bash
uv run pytest tests/data/test_model.py::test_init_and_data tests/data/test_model.py::test_init_model_as_input tests/data/test_dataset.py::test_validation_union_and_nested_type -v --mypy-only-local-stub --mypy-pyproject-toml-file=pyproject.toml --mypy-same-process
```

Expected: PASS on the pre-implementation branch state.

- [ ] Record a simple performance baseline for later comparison

Run:

```bash
uv run python -c "from timeit import timeit; from omnipy.data.model import Model; from omnipy.data.dataset import Dataset; print('cross-model', timeit(lambda: Model[int](Model[float](4.5)), number=5000)); print('iterable', timeit(lambda: Model[list[tuple[int, str]]](enumerate(('a', 'b', 'c'))), number=2000)); print('dataset-union', timeit(lambda: Dataset[Model[int] | Model[str] | Dataset[Model[int]]](data_file_1=123, data_file_2='abc', data_file_3={'data_file_inner': '456'}), number=500))"
```

Expected: three timing lines; save the numbers in the working notes for the final gate.

## Slice 1: Minimal native `RootModel` tracer bullet

**Slice goal:** Make `Model[int]` a real pydantic RootModel while keeping `.content`, `to_data()/from_data()`, and the default-value path intact.

**User Check-in:** Stop after this slice and confirm that minimal `Model[int]` construction, `.content`, `.root`, and `to_data()/from_data()` behavior still look right before touching cross-model coercion.

### Task 1: Rebase `Model` onto native `RootModel`

**Files:**
- Modify: `tests/data/test_model.py`
- Modify: `src/omnipy/util/pydantic.py`
- Modify: `src/omnipy/data/model.py`

- [ ] **Step 1: Write the failing tracer-bullet tests**

```python
def test_rootmodel_tracer_bullet_native_root_storage() -> None:
    model = Model[int](12)

    assert model.__class__.__pydantic_root_model__ is True
    assert model.content == 12
    assert model.root == 12
    assert model.to_data() == 12


def test_model_copy_tracks_rootmodel_fields_set() -> None:
    model_copy = copy(Model[list[int]]([1, 2, 3]))

    assert model_copy.model_fields_set == {'root'}
```

- [ ] **Step 2: Run the new tests to verify they fail**

Run:

```bash
uv run pytest tests/data/test_model.py::test_rootmodel_tracer_bullet_native_root_storage tests/data/test_model.py::test_model_copy_tracks_rootmodel_fields_set -v --mypy-only-local-stub --mypy-pyproject-toml-file=pyproject.toml --mypy-same-process
```

Expected: FAIL because `Model` is still a GenericModel compat wrapper rather than a native RootModel, and the field-set assertion still reflects the old root representation.

- [ ] **Step 3: Write the minimal implementation to make the tracer bullet pass**

```python
# src/omnipy/util/pydantic.py
RootModel = pyd.RootModel
RootModelMetaclass = type(RootModel)


def _as_root_model_values(validated_obj: BaseModel) -> dict[str, Any]:
    dumped = validated_obj.model_dump(by_alias=True)
    return {'root': dumped}


__all__ = [
    'GenericModel',
    'ModelMetaclass',
    'RootModel',
    'RootModelMetaclass',
    'validate_model',
]
```

```python
# src/omnipy/data/model.py
class ModelMetaclass(DataClassBaseMeta, pyd.RootModelMetaclass):
    def __instancecheck__(self, instance: Any) -> bool:
        if instance is None:
            return True
        return super().__instancecheck__(instance)


class Model(  # type: ignore[misc]
        ModelDisplayMixin,
        DataClassBase[_RootT],
        pyd.RootModel[_RootT],
        metaclass=ModelMetaclass,
):
    root: _RootT = pyd.Field(default_factory=undefined_default_factory)

    @property
    def content(self) -> _RootT:
        return cast(_RootT, self.root)

    @content.setter
    def content(self, value: _RootT) -> None:
        super().__setattr__('root', value)

    def __init__(
        self,
        value: _RootT | object | UndefinedType = Undefined,
        *,
        __root__: _RootT | object | UndefinedType = Undefined,
        **kwargs: _RootT | object,
    ) -> None:
        if value is not Undefined:
            root_value = value
        elif __root__ is not Undefined:
            root_value = __root__
        elif kwargs:
            root_value = kwargs
        else:
            root_value = self._get_default_value()

        super().__init__(root=cast(_RootT, root_value))

    def to_data(self) -> object:
        return super().model_dump(by_alias=True)

    def dict(self, *args, **kwargs) -> dict[str, object]:
        return {ROOT_KEY: self.to_data()}
```

Implementation notes:

- Export the new RootModel helpers without removing existing `GenericModel` / `ModelMetaclass` exports yet; Dataset and Params still depend on them.
- Keep `ROOT_KEY == 'root'` as the internal key.
- Do not touch cross-model conversion logic in this task; keep it for Slice 2.

- [ ] **Step 4: Run the focused tracer-bullet tests again**

Run:

```bash
uv run pytest tests/data/test_model.py::test_rootmodel_tracer_bullet_native_root_storage tests/data/test_model.py::test_model_copy_tracks_rootmodel_fields_set -v --mypy-only-local-stub --mypy-pyproject-toml-file=pyproject.toml --mypy-same-process
```

Expected: PASS (`2 passed`).

- [ ] **Step 5: Run adjacent minimal regressions**

Run:

```bash
uv run pytest tests/data/test_model.py::test_init_and_data tests/data/test_model.py::test_data_import_variants -v --mypy-only-local-stub --mypy-pyproject-toml-file=pyproject.toml --mypy-same-process
```

Expected: PASS. `Model[int]()`, `Model[str]()`, dict kwargs, and `__root__=` compatibility input still work.

- [ ] **Step 6: Commit Slice 1 tracer-bullet base**

```bash
git add src/omnipy/util/pydantic.py src/omnipy/data/model.py tests/data/test_model.py
git commit -m "refactor: move Model tracer bullet to RootModel"
```

### Task 2: Restore generic specialization metadata and naming on the RootModel path

**Files:**
- Modify: `tests/data/test_model.py`
- Modify: `src/omnipy/data/model.py`

- [ ] **Step 1: Add a focused failing regression for RootModel specialization metadata**

```python
def test_rootmodel_class_getitem_preserves_nested_specialization_metadata() -> None:
    model_cls = Model[dict[str, Model[None]]]

    assert model_cls.__pydantic_root_model__ is True
    assert model_cls.get_orig_model() == dict[str, Model[None]]
    assert model_cls.outer_type(with_args=True) == dict[str, Model[None]]
    assert model_cls.__name__ == 'Model[dict[str, Model[None]]]'
```

- [ ] **Step 2: Run the focused regression plus existing naming/type regressions**

Run:

```bash
uv run pytest tests/data/test_model.py::test_rootmodel_class_getitem_preserves_nested_specialization_metadata tests/data/test_model.py::test_name_qualname_and_module tests/data/test_model.py::test_get_inner_outer_type -v --mypy-only-local-stub --mypy-pyproject-toml-file=pyproject.toml --mypy-same-process
```

Expected: FAIL because the GenericModel-specific `__class_getitem__()` path no longer populates RootModel metadata correctly.

- [ ] **Step 3: Rewrite `Model.__class_getitem__()` for the RootModel path**

```python
@override
def __class_getitem__(
    cls,
    params: type[_RootT] | tuple[type[_RootT]] | TypeVar | tuple[TypeVar],
) -> 'type[Model[_RootT]]':
    model = cls._prepare_params(params)
    orig_model: type[_RootT] | TypeVar = model

    created_model = cast(
        type[Model],
        pyd.RootModel.__class_getitem__.__func__(  # type: ignore[attr-defined]
            cls,
            model if cls is Model else params,
        ),
    )

    root_field = deepcopy(created_model.model_fields['root'])
    created_model.model_fields['root'] = root_field

    if cls is Model and orig_model is not _RootT:  # type: ignore[misc]
        root_field.json_schema_extra = {'orig_model': orig_model}

    created_model._inherit_first_orig_model_in_bases_if_missing()

    if created_model is not cls:
        cleanup_name_qualname_and_module(cls, created_model, orig_model)

    cls._prepare_cls_members_to_mimic_model(created_model)
    cls._clean_type_caches()
    return created_model
```

Also keep these existing behaviors intact:

- `_inherit_first_orig_model_in_bases_if_missing()`
- `get_orig_model()` / `set_orig_model()`
- `_prepare_cls_members_to_mimic_model()`
- `_clean_type_caches()`

- [ ] **Step 4: Run the focused RootModel specialization regressions again**

Run:

```bash
uv run pytest tests/data/test_model.py::test_rootmodel_class_getitem_preserves_nested_specialization_metadata tests/data/test_model.py::test_name_qualname_and_module tests/data/test_model.py::test_get_inner_outer_type -v --mypy-only-local-stub --mypy-pyproject-toml-file=pyproject.toml --mypy-same-process
```

Expected: PASS.

- [ ] **Step 5: Commit the specialization fix**

```bash
git add src/omnipy/data/model.py tests/data/test_model.py
git commit -m "refactor: restore Model generic metadata on RootModel"
```

## Slice 2: Cross-model equivalence and union matching

**Slice goal:** Preserve current Omnipy parse-oriented conversion policy when `Model`, `Dataset`, or plain pydantic models are used as inputs to another `Model`, including union matching.

**User Check-in:** Stop after this slice and confirm that cross-model conversion still behaves as before (`Model[int](Model[float](4.5)) -> 4`) before moving to recursive/raw/json-heavy cases.

### Task 3: Port constructor and before-validator entrypoints to raw RootModel input

**Files:**
- Modify: `tests/data/test_model.py`
- Modify: `src/omnipy/data/model.py`
- Modify: `src/omnipy/util/pydantic.py`

- [ ] **Step 1: Write a failing regression for raw RootModel input ergonomics**

```python
def test_rootmodel_accepts_legacy_root_payloads_and_dict_kwargs() -> None:
    assert Model[int]({'__root__': '12'}).to_data() == 12
    assert Model[int]({'root': '13'}).to_data() == 13
    assert Model[dict[str, int]](a='1', b=2).to_data() == {'a': 1, 'b': 2}
    assert Model[list[int]](range(3)).to_data() == [0, 1, 2]
```

- [ ] **Step 2: Run the ergonomics regression to verify it fails**

Run:

```bash
uv run pytest tests/data/test_model.py::test_rootmodel_accepts_legacy_root_payloads_and_dict_kwargs -v --mypy-only-local-stub --mypy-pyproject-toml-file=pyproject.toml --mypy-same-process
```

Expected: FAIL because RootModel now receives raw inputs and the old dict-wrapper logic no longer normalizes them.

- [ ] **Step 3: Rewrite raw-input normalization in `Model` and `pyd.validate_model()`**

```python
@classmethod
def _unwrap_root_input(cls, value: Any) -> Any:
    if isinstance(value, Mapping):
        if '__root__' in value:
            return value['__root__']
        if 'root' in value and len(value) == 1:
            return value['root']
    return value


@pyd.model_validator(mode='before')
def _generous_iterable_support(cls, value: Any) -> Any:
    value = cls._unwrap_root_input(value)
    outer_type = cls.outer_type()
    if (lenient_issubclass(outer_type, Iterable)
            and not lenient_isinstance(value, outer_type)
            and is_non_str_byte_iterable(value)
            and not pyd.sequence_like(value)
            and not isinstance(value, Mapping)):
        return (_ for _ in value)
    return value


@pyd.model_validator(mode='before')
def _parse_root_object(cls, value: Any) -> Any:
    value = cls._unwrap_root_input(value)
    value = parse_none_according_to_model(value, root_model=cls)

    config = cls.data_class_creator.config  # type: ignore[attr-defined]
    with hold_and_reset_prev_attrib_value(config.model, 'dynamically_convert_elements_to_models'):
        config.model.dynamically_convert_elements_to_models = False
        return cls._parse_data(value)
```

```python
# src/omnipy/util/pydantic.py
def _as_v1_style_values(model: type[BaseModel], validated_obj: BaseModel) -> dict[str, Any]:
    if _is_root_model_cls(model):
        return {'root': validated_obj.model_dump(by_alias=True)}
    return validated_obj.model_dump()


def _as_v1_style_fields_set(model: type[BaseModel], validated_obj: BaseModel) -> set[str]:
    fields_set = set(getattr(validated_obj, '__pydantic_fields_set__', set()))
    if _is_root_model_cls(model):
        return {'root'} if 'root' in fields_set else set()
    return fields_set
```

Implementation notes:

- Keep `_secondary_validation_from_data()` only if tests still prove it is needed after RootModel input normalization.
- Do not add a recursive global prewalk; normalize only the current boundary value.

- [ ] **Step 4: Run the focused ergonomics regressions again**

Run:

```bash
uv run pytest tests/data/test_model.py::test_rootmodel_accepts_legacy_root_payloads_and_dict_kwargs tests/data/test_model.py::test_parse_convertible_iterables tests/data/test_model.py::test_data_import_variants -v --mypy-only-local-stub --mypy-pyproject-toml-file=pyproject.toml --mypy-same-process
```

Expected: PASS.

- [ ] **Step 5: Commit the raw RootModel input port**

```bash
git add src/omnipy/data/model.py src/omnipy/util/pydantic.py tests/data/test_model.py
git commit -m "refactor: port Model validators to raw RootModel input"
```

### Task 4: Reintroduce cross-model equivalence with a RootModel core-schema hook

**Files:**
- Modify: `tests/data/test_model.py`
- Modify: `src/omnipy/data/model.py`

- [ ] **Step 1: Add failing cross-model and union-matching regressions**

```python
def test_union_matching_accepts_nested_model_root_input() -> None:
    model = Model[str | Model[list[int]]]([1.2, 2.9])

    assert isinstance(model.content, Model[list[int]])
    assert model.to_data() == [1, 2]
```

Use the existing regression too:

```python
def test_init_model_as_input() -> None:
    assert Model[int](Model[float](4.5)).to_data() == 4
    assert Model[tuple[int, ...]](Model[list[float]]([4.5, 2.3])).to_data() == (4, 2)

    assert Model[Model[int]](Model[float](4.5)).content == Model[int](4)
    assert Model[Model[int]](Model[float](4.5)).to_data() == 4
```

- [ ] **Step 2: Run the focused regressions to verify they fail**

Run:

```bash
uv run pytest tests/data/test_model.py::test_init_model_as_input tests/data/test_model.py::test_union_matching_accepts_nested_model_root_input -v --mypy-only-local-stub --mypy-pyproject-toml-file=pyproject.toml --mypy-same-process
```

Expected: FAIL because raw RootModel validation no longer eagerly normalizes `Model` / `Dataset` / pydantic-model inputs before union selection.

- [ ] **Step 3: Add the RootModel core-schema pre-validator**

```python
from pydantic import GetCoreSchemaHandler
from pydantic_core import CoreSchema, core_schema


@classmethod
def _normalize_rootmodel_input(cls, value: Any) -> Any:
    value = cls._unwrap_root_input(value)

    if is_model_instance(value) or is_dataset_instance(value):
        return value.to_data()
    if is_non_omnipy_pydantic_model(value):
        return cast(pyd.BaseModel, value).model_dump(by_alias=True)
    return value


@classmethod
def __get_pydantic_core_schema__(
    cls,
    source: type[Any],
    handler: GetCoreSchemaHandler,
) -> CoreSchema:
    schema = handler(source)
    return core_schema.no_info_before_validator_function(cls._normalize_rootmodel_input, schema)
```

Implementation notes:

- Normalize only the top-level accepted input.
- Keep the conversion deterministic and local to the receiving `Model`.
- This hook is the replacement for the old “prepare dataset/model as input + fallback secondary validation” behavior.

- [ ] **Step 4: Re-run the focused cross-model regressions**

Run:

```bash
uv run pytest tests/data/test_model.py::test_init_model_as_input tests/data/test_model.py::test_union_matching_accepts_nested_model_root_input tests/data/test_model.py::test_init_converting_model_as_input tests/data/test_model.py::test_init_converting_dataset_as_input -v --mypy-only-local-stub --mypy-pyproject-toml-file=pyproject.toml --mypy-same-process
```

Expected: PASS.

- [ ] **Step 5: Commit the schema-hook preservation of parse semantics**

```bash
git add src/omnipy/data/model.py tests/data/test_model.py
git commit -m "feat: normalize cross-model inputs before RootModel validation"
```

## Slice 3: Recursive / union-heavy raw and JSON cases

**Slice goal:** Keep `_parse_data()`-driven parse hooks, recursive unions, raw-model chains, JSON model behavior, and forward references working on top of RootModel.

**User Check-in:** Stop after this slice and confirm that recursive/list-heavy/json-heavy parsing still matches expectations before stabilizing Dataset and table integrations.

### Task 5: Restore recursive union parsing and raw-model parse hooks

**Files:**
- Modify: `tests/data/test_model.py`
- Modify: `tests/components/raw/test_models.py`
- Modify: `src/omnipy/data/model.py`

- [ ] **Step 1: Add the failing recursive RootModel regression**

```python
def test_recursive_rootmodel_union_accepts_nested_lists() -> None:
    class RecursiveModel(Model[str | list['RecursiveModel']]):
        pass

    RecursiveModel.update_forward_refs(RecursiveModel=RecursiveModel)

    assert RecursiveModel([]).to_data() == []
    assert RecursiveModel(['a']).to_data() == ['a']
    assert RecursiveModel(['a', ['b']]).to_data() == ['a', ['b']]
```

Also keep the existing raw parse-hook regression in the run set:

```python
def test_split_lines_to_columns_and_join_columns_to_lines_model(
    use_str_model: bool,
    assert_model_if_dyn_conv_else_val: Annotated[AssertModelOrValFunc, pytest.fixture],
) -> None:
    cols_stripped_tab = SplitLinesToColumnsModel(data_tab)
    assert cols_stripped_tab[1:].to_data() == [['mno', 'pqr', 'stu', 'vwx'], ['yz']]
```

- [ ] **Step 2: Run the recursive/raw regressions to verify they fail**

Run:

```bash
uv run pytest tests/data/test_model.py::test_recursive_rootmodel_union_accepts_nested_lists tests/components/raw/test_models.py::test_split_lines_to_columns_and_join_columns_to_lines_model -v --mypy-only-local-stub --mypy-pyproject-toml-file=pyproject.toml --mypy-same-process
```

Expected: FAIL because RootModel input now bypasses the old dict-root assumptions that `_parse_data()` and recursive unions relied on.

- [ ] **Step 3: Fix parse-hook ordering without changing eager conversion policy**

```python
@pyd.model_validator(mode='before')
def _parse_root_object(cls, value: Any) -> Any:
    value = cls._normalize_rootmodel_input(value)
    value = parse_none_according_to_model(value, root_model=cls)

    config = cls.data_class_creator.config  # type: ignore[attr-defined]
    with hold_and_reset_prev_attrib_value(config.model, 'dynamically_convert_elements_to_models'):
        config.model.dynamically_convert_elements_to_models = False
        parsed = cls._parse_data(value)

    return parsed
```

Implementation notes:

- `parse_none_according_to_model()` stays in place for this migration; do not redesign it here.
- `_parse_data()` must still run before strict final typing is locked in.
- Preserve the current eager `to_data()` behavior; this task is only about getting the same parsed content back under RootModel.

- [ ] **Step 4: Re-run the recursive/raw regressions**

Run:

```bash
uv run pytest tests/data/test_model.py::test_recursive_rootmodel_union_accepts_nested_lists tests/components/raw/test_models.py::test_split_lines_to_columns_and_join_columns_to_lines_model tests/data/test_model.py::test_parse_convertible_iterables -v --mypy-only-local-stub --mypy-pyproject-toml-file=pyproject.toml --mypy-same-process
```

Expected: PASS.

- [ ] **Step 5: Commit the recursive/raw parse-hook fix**

```bash
git add src/omnipy/data/model.py tests/data/test_model.py tests/components/raw/test_models.py
git commit -m "fix: restore recursive and raw parsing on RootModel"
```

### Task 6: Update JSON consistency, serialization, and forward-ref assertions for RootModel internals

**Files:**
- Modify: `tests/components/json/test_json_models.py`
- Modify: `tests/data/test_model.py`
- Modify: `src/omnipy/data/model.py`
- Modify: `src/omnipy/util/pydantic.py`

- [ ] **Step 1: Replace implementation-detail assertions with RootModel-native behavioral assertions**

```python
def test_json_model_consistency_basic() -> None:
    example_dict_data = {'abc': 2312}
    assert JsonModel(example_dict_data).content == _JsonAnyDictM({'abc': 2312})
    assert JsonDictModel(example_dict_data).content == _JsonAnyDictM({'abc': 2312})

    example_list_data = ['abc', 2312]
    assert JsonModel(example_list_data).content == _JsonAnyListM(['abc', 2312])
    assert JsonListModel(example_list_data).content == _JsonAnyListM(['abc', 2312])
```

```python
assert not model_copy.has_snapshot()
assert model_copy.model_fields_set == {'root'}
```

- [ ] **Step 2: Run the JSON / serialization / forward-ref regressions to verify they fail**

Run:

```bash
uv run pytest tests/components/json/test_json_models.py::test_json_model_consistency_basic tests/components/json/test_json_models.py::test_json_model_consistency_with_none tests/data/test_model.py::test_copy tests/data/test_model.py::test_class_init_generic_with_forwardref -v --mypy-only-local-stub --mypy-pyproject-toml-file=pyproject.toml --mypy-same-process
```

Expected: FAIL until RootModel serialization and forward-ref bookkeeping are aligned with the new root representation.

- [ ] **Step 3: Reconcile RootModel serialization and rebuild flow**

```python
def to_data(self) -> object:
    return super().model_dump(by_alias=True)


def to_json(self, pretty: bool = True) -> str:
    json_content = self.model_dump_json()
    return self._pretty_print_json(json.loads(json_content)) if pretty else json_content


super().model_rebuild(_types_namespace=globalns)
root_field = cls._get_root_field()
root_field.annotation = evaluate_any_forward_refs_if_possible(prev_annotation, **globalns)
cls.set_orig_model(evaluate_any_forward_refs_if_possible(prev_orig_model, **globalns))
cls._clean_type_caches()
```

```python
# src/omnipy/util/pydantic.py
def _to_v2_validation_input(model: type[BaseModel], input_data: dict[str, Any]) -> Any:
    if _is_root_model_cls(model):
        if '__root__' in input_data:
            return input_data['__root__']
        if 'root' in input_data:
            return input_data['root']
    return input_data
```

Implementation notes:

- Keep accepting `__root__` / `root` as inputs.
- Do not preserve `__root__` as an internal assertion target.
- `to_json_schema()` should continue stripping `orig_model` metadata from the output schema.

- [ ] **Step 4: Re-run the JSON / serialization / forward-ref regressions**

Run:

```bash
uv run pytest tests/components/json/test_json_models.py::test_json_model_consistency_basic tests/components/json/test_json_models.py::test_json_model_consistency_with_none tests/data/test_model.py::test_copy tests/data/test_model.py::test_class_init_generic_with_forwardref tests/data/test_model.py::test_class_init_forwardref -v --mypy-only-local-stub --mypy-pyproject-toml-file=pyproject.toml --mypy-same-process
```

Expected: PASS.

- [ ] **Step 5: Commit the RootModel serialization / forward-ref cleanup**

```bash
git add src/omnipy/data/model.py src/omnipy/util/pydantic.py tests/data/test_model.py tests/components/json/test_json_models.py
git commit -m "test: update RootModel serialization and forward ref assertions"
```

## Slice 4: Dataset and component stabilization

**Slice goal:** Audit dependent subsystems that assumed GenericModel / `__root__` / `__fields__` details and make them stable against the new Model internals.

**User Check-in:** Stop after this slice and manually test one Dataset + one JSON/table flow before running the full repo gate.

### Task 7: Stabilize Dataset and Params against RootModel-backed `Model`

**Files:**
- Modify: `tests/data/test_dataset.py`
- Modify: `src/omnipy/data/dataset.py`
- Modify: `src/omnipy/data/param.py`
- Modify: `src/omnipy/util/pydantic.py`

- [ ] **Step 1: Use the existing failing Dataset regressions as the red phase**

Run:

```bash
uv run pytest tests/data/test_dataset.py::test_copy tests/data/test_dataset.py::test_deepcopy tests/data/test_dataset.py::test_validation_union_and_nested_type -v --mypy-only-local-stub --mypy-pyproject-toml-file=pyproject.toml --mypy-same-process
```

Expected: FAIL if Dataset still depends on v1 field APIs or if nested `Model` validation no longer returns the expected data shape.

- [ ] **Step 2: Replace remaining v1 field assumptions in Dataset / Params paths**

```python
# src/omnipy/data/dataset.py
def copy(self, *, deep: bool = False, **kwargs) -> Self:
    pydantic_copy = self.model_copy(deep=deep, **kwargs)
    if not deep:
        object.__setattr__(pydantic_copy, DATA_KEY, pydantic_copy.__dict__[DATA_KEY].copy())
    return pydantic_copy  # pyright: ignore[reportReturnType]


@classmethod
def _get_data_field(cls) -> pyd.ModelField:
    return cast(pyd.ModelField, cls.model_fields.get(DATA_KEY))


def _set_standard_field_description(self) -> None:
    self.model_fields[DATA_KEY].description = self._get_standard_field_description()
```

```python
# src/omnipy/data/param.py
values, fields_set, validation_error = pyd.validate_model(
    model_cls,
    input_data={k: v for k, v in default_vals.items()},
)
```

Implementation notes:

- Keep Dataset as the existing BaseModel/GenericModel-based type for this migration.
- This task is only about consuming the new `Model` behavior safely.

- [ ] **Step 3: Re-run the Dataset / Params regressions**

Run:

```bash
uv run pytest tests/data/test_dataset.py::test_copy tests/data/test_dataset.py::test_deepcopy tests/data/test_dataset.py::test_validation_union_and_nested_type -v --mypy-only-local-stub --mypy-pyproject-toml-file=pyproject.toml --mypy-same-process
```

Expected: PASS.

- [ ] **Step 4: Commit the Dataset stabilization**

```bash
git add src/omnipy/data/dataset.py src/omnipy/data/param.py tests/data/test_dataset.py
git commit -m "fix: stabilize Dataset around RootModel-backed Model"
```

### Task 8: Stabilize JSON/table component integrations and audit remaining root-wrapper assumptions

**Files:**
- Modify: `tests/components/tables/test_models.py`
- Modify: `tests/components/json/test_json_models.py`
- Modify: `src/omnipy/components/tables/models.py`
- Review: `src/omnipy/components/json/constants.py`

- [ ] **Step 1: Use the component regressions as the red phase**

Run:

```bash
uv run pytest tests/components/tables/test_models.py::test_columnwise_table_iter tests/components/json/test_json_models.py::test_json_model_consistency_basic tests/components/raw/test_models.py::test_split_lines_to_columns_and_join_columns_to_lines_model -v --mypy-only-local-stub --mypy-pyproject-toml-file=pyproject.toml --mypy-same-process
```

Expected: FAIL anywhere component code still assumes `__fields__`, `required`, or `__root__`-wrapper internals.

- [ ] **Step 2: Replace table-model v1 field inspection and keep JSON compatibility explicit**

```python
# src/omnipy/components/tables/models.py
headers = pydantic_model.model_fields

num_required_fields = -1
for i, header_field in enumerate(headers.values()):
    if not header_field.is_required():
        if num_required_fields == -1:
            num_required_fields = i
        continue
    elif num_required_fields != -1 and i > num_required_fields:
        raise ValueError('Required fields must not come after optional fields')


content[key] = [pyd_model.model_fields[key].get_default(call_default_factory=True)] * col_len

for key, field in pyd_model.model_fields.items():
    if field.is_required() and key not in content:
        _init_col(content, pyd_model, key)
```

JSON audit rule for this task:

- Keep `src/omnipy/components/json/constants.py:DEFAULT_KEY = '__root__'` unless a failing user-facing behavior proves that external default-key behavior should change.
- Accept `__root__` / `root` payloads through `Model` normalization rather than changing JSON user-facing contracts during this migration.

- [ ] **Step 3: Re-run the component regressions plus a wider smoke set**

Run:

```bash
uv run pytest tests/components/tables/test_models.py tests/components/json/test_json_models.py tests/components/raw/test_models.py -v --mypy-only-local-stub --mypy-pyproject-toml-file=pyproject.toml --mypy-same-process
```

Expected: PASS.

- [ ] **Step 4: Commit the component stabilization**

```bash
git add src/omnipy/components/tables/models.py tests/components/tables/test_models.py tests/components/json/test_json_models.py
git commit -m "fix: stabilize component models for RootModel migration"
```

## Final verification gate

- [ ] **Step 1: Run the full focused migration suite**

Run:

```bash
uv run pytest tests/data/test_model.py tests/data/test_dataset.py tests/components/json/test_json_models.py tests/components/tables/test_models.py tests/components/raw/test_models.py -v --mypy-only-local-stub --mypy-pyproject-toml-file=pyproject.toml --mypy-same-process
```

Expected: PASS.

- [ ] **Step 2: Re-run the performance sample and compare to baseline**

Run:

```bash
uv run python -c "from timeit import timeit; from omnipy.data.model import Model; from omnipy.data.dataset import Dataset; print('cross-model', timeit(lambda: Model[int](Model[float](4.5)), number=5000)); print('iterable', timeit(lambda: Model[list[tuple[int, str]]](enumerate(('a', 'b', 'c'))), number=2000)); print('dataset-union', timeit(lambda: Dataset[Model[int] | Model[str] | Dataset[Model[int]]](data_file_1=123, data_file_2='abc', data_file_3={'data_file_inner': '456'}), number=500))"
```

Expected: three timing lines that are not materially worse than the baseline without a written justification.

- [ ] **Step 3: Run repo-wide verification**

Run:

```bash
uv run pytest -v --mypy-only-local-stub --mypy-pyproject-toml-file=pyproject.toml --mypy-same-process
```

Expected: full test suite PASS.

- [ ] **Step 4: Run formatting / import-order / lint hooks**

Run:

```bash
uv run pre-commit run --hook-stage manual --all-files
```

Expected: PASS, or auto-fixes followed by a clean re-run.

## Checklist coverage self-review

- Checklist 1 (`RootModel` export in compat layer) -> Task 1
- Checklist 2 (rebase `Model` inheritance) -> Task 1
- Checklist 3 (replace `__root__` emulation with native root semantics) -> Tasks 1, 3, 6
- Checklist 4 (`__class_getitem__` rewrite) -> Task 2
- Checklist 5 (constructor / validation entrypoints) -> Task 3
- Checklist 6 (before-validators on raw RootModel input) -> Tasks 3, 5
- Checklist 7 (cross-model equivalence core-schema hook) -> Task 4
- Checklist 8 (`content`, `to_data`, `from_data`, special methods) -> Tasks 1, 4, 6
- Checklist 9 (serialization / schema behavior) -> Task 6
- Checklist 10 (forward refs and rebuild flow) -> Task 6
- Checklist 11 (tests tied to `__root__`) -> Task 6
- Checklist 12 (Dataset / dependent subsystem audit) -> Tasks 7, 8
- Checklist 13 (`omnipy.util.pydantic` validation cleanup) -> Tasks 1, 3, 6, 7
- Checklist 14 (four tracer-bullet slices) -> Slices 1-4 above
- Checklist 15 (performance and regression gates) -> Final verification gate

## Notes for the implementing agent

- Prefer minimal, surgical changes. Do not redesign Omnipy conversion policy in this migration.
- When a new failing test reveals an architectural gap, stop and update this plan instead of improvising a larger rewrite.
- If a later slice tempts a broader cleanup (e.g. Dataset also becoming RootModel), defer it; that is outside this migration scope.
