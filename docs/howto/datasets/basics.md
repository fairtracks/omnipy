# Working with Datasets

Create, access, and transform typed collections with Dataset primitives.

This section is coming soon — check back as Omnipy evolves.

## Detect Dataset content through Models

`om.is_model_of_dataset_instance(value)` checks whether a Model currently contains a
Dataset, including through nested Models and unions. Empty Datasets are recognized.
After this check, `value.dataset` returns the existing Dataset through mimicking,
without conversion or validation. A Dataset's public `.dataset` property returns itself.
Use `om.is_dataset_instance(value)` to detect a Dataset itself.

`om.is_model_of_dataset_subclass(type_form)` checks for a Model subclass, then attempts
default construction and checks the resulting instance. Only if construction raises an
exception does it fall back to the existing direct `Model[Dataset]`
type check. This fallback does not recursively inspect types or create a container.
A successfully constructed Model with non-Dataset content gives `False`.
Use `om.is_dataset_subclass(type_form)` to detect a Dataset subclass itself.

Default construction runs validators and examines only the default union branch.
Use the instance helper when a value is available. These helpers perform detection;
they do not select serializers or define loading, conversion, merging, or saving policies.
