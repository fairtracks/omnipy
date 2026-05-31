# Pydantic V2 Migration Guide — Key Points for Omnipy Migration

Source: https://docs.pydantic.dev/latest/migration/ (fetched 2026-05-31)

## 1. API Method Renames (BaseModel)

| V1 | V2 |
|---|---|
| `__fields__` | `model_fields` |
| `__private_attributes__` | `__pydantic_private__` |
| `construct()` | `model_construct()` |
| `copy()` | `model_copy()` |
| `dict()` | `model_dump()` |
| `json()` | `model_dump_json()` |
| `parse_obj()` | `model_validate()` |
| `update_forward_refs()` | `model_rebuild()` |
| `schema_json()` / `json_schema()` | `model_json_schema()` |

- `dict()` / `json()` still work with deprecation warnings.
- `.json()` with `indent` etc. may cause confusing errors — use `model_dump_json()` instead.
- `model_dump_json()` produces **compact** JSON (no spaces). V1 produced pretty-printed.
  - To match V1: use `json.dumps(model.model_dump(), indent=2)` or `model_dump_json()` with `separators` workaround.

## 2. RootModel (replaces `__root__`)

- `__root__` field is **gone** in V2. Use `RootModel[T]` instead.
- RootModel subclasses have a `.root` attribute instead of a `__root__` field.
- `arbitrary_types_allowed` is NOT supported on RootModel.

## 3. Generic Models

- `pydantic.generics.GenericModel` removed. Use `class MyModel(BaseModel, Generic[T]): ...`.
- Mixing V1 and V2 models as type params is not supported.
- Avoid `isinstance()` checks with parametrized generics.

## 4. Config Changes

- Use `model_config = ConfigDict(...)` instead of inner `class Config`.
- Config settings renamed:
  - `allow_population_by_field_name` → `populate_by_name`
  - `anystr_lower` → `str_to_lower`
  - `anystr_strip_whitespace` → `str_strip_whitespace`
  - `orm_mode` → `from_attributes`
  - `validate_all` → `validate_default`
  - `schema_extra` → `json_schema_extra`
  - `anystr_upper` → `str_to_upper`
  - `max_anystr_length` / `min_anystr_length` → `str_max_length` / `str_min_length`
  - `keep_untouched` → `ignored_types`
- Removed config settings: `allow_mutation`, `error_msg_templates`, `fields`, `smart_union` (now default), `underscore_attrs_are_private` (always True now), `json_loads`, `json_dumps`, `copy_on_model_validation`, `post_init_call`.
- `smart_union` removed — default union_mode in V2 is `'smart'`.

## 5. Validator Changes

- `@validator` → **deprecated**, replace with `@field_validator`.
- `@root_validator` → **deprecated**, replace with `@model_validator`.
- `@validate_arguments` → renamed to `@validate_call`.
- `@field_validator` does NOT have `each_item` — use `Annotated` on type args instead.
- `@field_validator` signature: `config` and `field` arguments removed. Use `info.config` and `cls.model_fields[info.field_name]`.
- `TypeError` in validators is NO LONGER converted to `ValidationError`.
- `@model_validator(mode='before')` receives dict; `(mode='after')` receives model instance.
- `always=True` → use `validate_default` in Field instead.
- `allow_reuse` keyword argument is no longer necessary.

## 6. Coercion Changes (CRITICAL for Omnipy)

- **`int`/`float`/`Decimal` → `str` is disabled by default**. Use `coerce_numbers_to_str=True` in model_config to restore V1 behavior.
- **`float` → `int`** only allowed if decimal part is zero (e.g., `10.0` → `10`, but `10.2` raises error).
- **Iterables of pairs** are NO LONGER coerced to dicts.
- `Optional[T]` means: field is **required** but allows `None`. Does NOT mean optional with default None.
- `Any` no longer defaults to `None`.
- Input types are NOT preserved for generic collections (e.g., `Mapping[str, int]` becomes `dict`).
- Input types ARE preserved for BaseModel/dataclass subclasses.

## 7. Union Handling

- Default union_mode is `'smart'` (tries to preserve input type when it matches one of the union cases).
- To restore V1 left-to-right behavior: `Field(union_mode='left_to_right')`.
- Example: `x: Union[int, str]` with input `'1'` → V2 keeps it as string `'1'` (since input is already a string), V1 would coerce to int `1`.

## 8. TypeAdapter (replaces parse_obj_as)

- `TypeAdapter[T].validate_python(value)` replaces `parse_obj_as(T, value)`.
- `TypeAdapter` also handles validation, serialization, and JSON schema generation for arbitrary types.
- `parse_obj_as` is deprecated but available through `pydantic.v1`.

## 9. Custom Types

- `__get_validators__` ➜ replace with `__get_pydantic_core_schema__`.
- `__modify_schema__` ➜ replace with `__get_pydantic_json_schema__`.
- Use `typing.Annotated` to add custom validation without modifying the type itself.

## 10. Field Changes

- No arbitrary kwargs on Field → use `json_schema_extra` dict instead.
- `alias` property returns `None` (not field name) when no alias is set.
- Removed: `const`, `min_items`/`max_items` (use min/max_length), `unique_items`, `allow_mutation` (use `frozen`), `regex` (use `pattern`), `final`.
- Field constraints NOT propagated to generic type params automatically.

## 11. JSON Schema

- Default JSON Schema target: draft 2020-12 (with OpenAPI extensions).
- `Optional` fields now explicitly mark `null` as allowed.
- `Decimal` types serialized as strings in JSON schema.
- Customization via subclassing `GenerateJsonSchema` (much easier than V1).

## 12. `ModelField` removed

- `ModelField` class no longer exists in V2.
- Use `FieldInfo` (from `pydantic.fields`) instead.
- `FieldInfo` does NOT have `class_` attribute; use `annotation` instead.

## 13. Private Attributes

- All underscore attributes are treated as private by default (equivalent to `underscore_attrs_are_private=True` in V1).
- Can still use `PrivateAttr` for typed private attributes.
- Private attributes copied/deep-copied during model init/copy.

## 14. Dataclasses

- Vanilla dataclasses no longer accept tuples as validation input (use dicts).
- `__post_init__` called AFTER validation (was before).
- `__post_init_post_parse__` removed.
- No `__pydantic_model__` attribute on pydantic dataclasses.

## 15. Copy/Deepcopy

- `copy()` → `model_copy()`.
- `model_copy(deep=True)` for deep copy.
- Private attributes are deep-copied by default during model init.
- Models are copied/validated rather than modified in place in many cases.

## 16. Equality Changes

- Models only equal to other BaseModel instances (not dicts).
- Models must have same type (or generic origin) to be equal.
- Private attribute values affect equality.

## 17. Settings

- `BaseSettings` has moved to `pydantic-settings` package (separate install).

## 18. Error Handling

- `ValidationError` construction has changed — not all V1 patterns work.
- `TypeError` no longer auto-converted to `ValidationError`.
- `ErrorWrapper` is a V1 internal — not generally needed in V2.
- `validate_model` utility function (V1 internal) — use `TypeAdapter` or `model_validate` instead.
