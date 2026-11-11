# Validation of nested Models and the validators of their parents

Date: 2026-11-11. Summary of an investigation and the decisions made with the user, while
reworking the sequence data brokering integration test
(`tests/integration/novel/full/sequence_data_brokering/`).

## Background

The brokering test moved its service URLs from flow keywords into the submission, in a new
`logistics` member holding the broker's settings (`services`, one schema per service) and state
(`status`), apart from the content sent to the Sequence Depot. Secrets handling, e.g. for
authentication with the services, is a missing Omnipy feature and was left as a TODO.

After the move, the final task lost an update made through a local reference:

```python
status = submission.logistics.status
...  # reads other fields of the submission
status.sequence_depot_submission_status = 'completed'  # not kept in the submission
```

## Findings

### Models of Pydantic models revalidated their whole content on every attribute read

`Model.__getattr__` revalidated the content before returning any attribute when the content was a
non-Omnipy Pydantic model:

```python
if self._is_non_omnipy_pydantic_model() and self._content_obj_hasattr(attr):
    self._validate_and_set_value(self.content)
```

Validation converts the content to raw data and parses it again (`_validate_content_from_value`),
and `_generic_validate_content` copies the result if validation returned the same object. Every
read therefore replaced the content and all nested objects:

- References to nested Models taken earlier were disconnected from the parent after any later read.
  Changes through them were lost without an error.
- Each read cost time proportional to the content. With a Dataset inside the schema, reading a scalar
  field cost about 1.3 ms with 10 items, 11 ms with 100 and 110 ms with 1000.
- Neither `interactive` nor `dynamically_convert_elements_to_models` changed this, nor did Pydantic's
  `copy_on_model_validation`. The copies are made by Omnipy.

The revalidation was added in August 2024 (`59e83798`, "Pydantic models are validated before
accessing attributes"), when nested Pydantic objects were plain `BaseModel`s, so changes inside them
could only be validated through the parent. Since October 2026 (`2f9e0a1a`),
`create_pydantic_model_subclass_with_wrappers` wraps fields that are or contain Pydantic models in
Omnipy Models, which validate their own changes. The revalidation was then only needed for one
effect: rerunning the validators of the parent after an in-place change to nested data.

### Comparison with JsonModel and other container Models

| | JsonModel / `Model[dict[...]]` | `Model[PydanticSchema]` (before the change) |
|---|---|---|
| A read goes through | `__getitem__`, a read-only special method | `__getattr__`, revalidating everything first |
| References to nested Models | stay connected | disconnected after any read |
| Invalid nested change | the nested Model raises | the nested Model raises (wrappers) |
| Validators of the parent after a nested change | not rerun | rerun on the next read |
| Cost of a read | none | proportional to the content |

### No Model or Dataset reruns the validators of its parent after an in-place nested change

Verified with the current code:

- A JsonModel subclass deriving `total` from `numbers` in `_parse_data`, and allowing at most three
  numbers: `m['numbers'].append(...)` leaves `total` outdated and can break the rule without an error.
  Assigning at the top level or calling `validate_content()` reruns `_parse_data`.
- `Model[list[Model[list[int]]]]` with a rule on the inner lists: `m[0].append(3)` is accepted even
  when breaking the rule; `m[0] = [...]` and `validate_content()` raise. With immutable elements, as
  in `Model[list[Model[int]]]`, every change goes through the parent, so the issue cannot occur.
- A Dataset with a uniqueness validator (`@pyd.validator('data')`): changing an item in place to
  duplicate an id is accepted; assigning the item raises. Datasets have no `validate_content()`.

Until then, Pydantic content was the only exception, because of the revalidation on read.

### Pydantic v2

Verified with Pydantic 2.13 (installed; Omnipy uses its v1 API):

- In-place changes to nested lists or models do not rerun the parent's `model_validator`s. A rule of
  the parent can be broken without an error.
- `validate_assignment=True` reruns the parent's after-validators on assignment at the top level.
- `@computed_field` values are computed on access, so they are always current, and are included by
  `model_dump()`.
- With the default `revalidate_instances='never'`, validating a parent reuses existing nested model
  instances, where v1 copied them. Lists are still new after validation.

Pydantic v2 thus solves derived fields (computed fields), but not rules of parents over nested data.
It does not remove the copies made by Omnipy's own validation either.

## Alternatives considered

- **A. Remove the revalidation on read.** Models of Pydantic models then behave like other Models:
  references stay connected and reads cost nothing. The validators of the parent rerun only on
  changes through the parent or explicit validation. All tests passed except the one checking the
  snapshot taken on reading a field.
- **B. Propagate validation to parents when a nested Model changes.** Reads are free and rules and
  derived fields are always current. Requires links from nested Models to possibly several parents,
  revalidates all ancestors on every change (quadratic in loops over large Datasets) and interacts
  with the snapshot machinery. Pydantic v2 deliberately does not do this.
- **C. Keep the revalidation on read, but merge changed values into the existing objects.** A
  prototype (about 25 lines) passed all 5157 data and integration tests and kept references
  connected. It kept the cost (95 ms per read at 1000 items), and the snapshot machinery printed
  deepcopy-memo warnings, as snapshots track objects by id and expect validation to produce new ones.
- **D. Revalidate only when something changed since the last validation.** Detecting changes needs an
  O(N) comparison with the snapshot (interactive mode only) or change flags from nested Models, which
  need the parent links of B. References taken before a real change still go stale.
- **Grouped update (`with model.updating(): ...`).** The parent validates once when the block ends
  and rolls back on failure. Gives errors close to the change and atomic changes passing through
  invalid intermediate states (e.g. renaming a sample changes both its local id and the references
  from its files), at the cost of one validation of the parent. Explicit, so code not using it gets no earlier checking.

## Decisions

- **A was chosen and implemented** (`aa6dafd4`). The snapshot test was deleted and replaced by a test
  that references to nested Models stay connected.
- **Validation at job boundaries** is planned as a job modifier, rerunning the validators of the
  parents of job inputs and outputs. It must rerun the parents' own validators rather than only
  accept already validated nested Models, and validate inputs as well as outputs, to also catch
  changes made outside of jobs. TODO in `src/omnipy/compute/_func_job.py`; skipped known-issue test
  `test_job_boundaries_validate_parents_of_changed_nested_models_known_issue` in
  `tests/compute/test_task.py` (`fe6367cd`).
- **Derived fields** are planned as `@computed_field`s with Pydantic v2 (already a TODO in the
  brokering models).
- **B was set aside.** With validation at job boundaries and computed fields, its remaining benefit is
  errors at the line of the change rather than at the job boundary, mainly in interactive use. The
  grouped update covers that need explicitly, without parent links.
- **The grouped update** was implemented as `Model.updating()` (`7581493e`), for Models only.
  - **Rollback:** it follows the existing snapshots, rolling back only in interactive mode, like
    other Model operations.
  - **Start of the block:** an explicit validation there was rejected as counter to the lazy
    snapshots. The rollback point is instead prepared as for other state-changing operations. In
    interactive mode, the model is validated only if it changed since its last snapshot.
  - **Exceptions:** any exception raised in the block also triggers the rollback.
- **Until then, the rule for all Models and Datasets:** after changing nested data in place that a
  rule or derived field of a parent depends on, assign the changed member back through the parent,
  make the changes inside `with parent.updating():`, or call `validate_content()` on a parent
  Model. The brokering allocation task now assigns the
  metadata back for this reason (`e89bae47`).

Tests pinning the current behaviour (`3672ce4b`):
`test_parent_validators_rerun_only_on_validation_of_or_changes_through_the_parent` and
`test_derived_fields_of_pydantic_model_update_only_on_changes_through_the_parent` in
`tests/data/test_model.py`, and `test_dataset_validators_rerun_only_on_changes_through_the_dataset`
in `tests/data/test_dataset.py`. The omnipy-dataflows skill documents the rule (`1f5ec0d1`).

## Possible future improvements

- The job modifier validating at job boundaries (see Decisions).
- `@computed_field`s for derived fields with Pydantic v2, including how computed keys in saved job
  outputs are treated when loaded again (ignored or rejected, depending on `extra`).
- `validate_content()` and `updating()` for Datasets, so that Dataset-level validators can be rerun
  explicitly. Datasets have no snapshots, so rollback needs its own design, possibly shared with the
  planned atomic rollback of jobs.
- A "dirty" flag for snapshots (TODO in `Model._prepare_reset_solution_take_snapshot_if_needed`).
  Checking whether a model changed since its snapshot compares the content with the snapshot, which
  costs time proportional to the content, also when `updating()` prepares its rollback point.
- The cost of validation in general: `validate_content()` and assignments through a parent convert
  the whole content to raw data and parse it again. Validating without the round trip through raw
  data would make parent-level validation cheaper and keep nested objects.
- Static typing of subclasses of list Models: the constructor of a subclass of
  `Model[list[Model[list[int]]]]` is typed as returning the base `Model_list`, and a nested
  `Model[list[int]]` annotation is not seen as a list. The new tests use line-level pyright ignores.
- Secrets handling, e.g. for authentication with services (TODO in the brokering models).
- The related known issue `test_mimic_dynamically_bound_instance_method_known_issue`: validation in
  interactive mode copies the Model, so methods grafted onto an instance stay bound to the old one.
