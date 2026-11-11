# Component structure and naming

Use existing `src/omnipy/components/` packages as the template when organizing
reusable dataflow code. A package should represent a coherent capability or domain.
This file structure will be the basis of Omnipy's future plugin architecture.
The same responsibilities can organize an application or narrative integration
package; adopting this layout does not require moving it into Omnipy's library.

## Module responsibilities

| Module | Responsibility |
| --- | --- |
| `models.py` | Data contracts, validation, normalization, and model-based conversions/mappers |
| `datasets.py` | Named Dataset classes and Dataset-specific behavior |
| `tasks.py` | Reusable operations exposed as task templates |
| `flows.py` | Composition of operations into dataflows |
| `serializers.py` | Serialization formats and Dataset integration when needed |
| `helpers.py`, `protocols.py`, `typedefs.py`, `constants.py`, `enums.py` | Supporting functionality separated by responsibility when its size and use warrant it |

The JSON component demonstrates most of this structure. Smaller components need
only the relevant modules. Keep a small helper beside its caller; move shared
support into an appropriately scoped module. Additional files should improve
navigation and ownership. An application or integration example can additionally
use `services.py` for typed service clients or coroutine stand-ins, following the
existing [external-contract guidance](patterns.md#external-api-contracts). Mocked
HTTP services belong with the fixtures in `conftest.py`; see
[mock services](patterns.md#mock-services-and-failure-scenarios).

When a module becomes difficult to navigate, turn it into a same-named package
and split it by meaningful responsibility. The ISA component demonstrates this
for models:

```text
component/
    models/
        __init__.py
        sample_schema.py
        study_schema.py
        validators.py
    datasets.py
    tasks.py
    flows.py
```

Preserve useful import paths through the package's `__init__.py`. Apply the same
approach to other growing modules. Keep public exports deliberate, including any
addition to `src/omnipy/__init__.py`; that surface also affects import-time behavior.

## Names expose contracts and operations

Use meaningful domain or structural names with established role suffixes:

| Role | Naming guidance and examples |
| --- | --- |
| Pydantic schema | Prefer `Schema`, such as `SampleSchema`. `Record` is used primarily for table-row schemas, such as `SampleRecord` in `TableOfPydanticRecordsDataset[SampleRecord]`. |
| Omnipy Model | Use `Model`, such as `HttpUrlModel` or `SampleModel`. |
| Dataset | Use `Dataset`, such as `HttpUrlDataset` or `SampleDataset`. |
| Conversion Model | Use `Mapper`, such as `SampleToServiceRequestMapper`; make source/target meaning clear where helpful. |
| External contract | Preserve meaningful API terminology, such as `RegistrationRequest` or `RegistrationResponse`. |

Preserve semantic stems across related classes. The `Dataset` suffix already
communicates the collection role; follow established names such as
`SubmissionSamplesDataset` when working with existing code. Names in
an example do not by themselves establish a naming rule for new components.

Tasks and flows use descriptive verbs in `snake_case`, such as
`get_json_from_api_endpoint`, `collect_and_normalize_samples`, and
`flatten_nested_json`. Their names explain the work; decorators and signatures
expose job and callable types. Function names need not universally end in `_task`,
`_flow`, or `_async`.

When distinguishing a template from its applied instance, name the concrete kind:
`publish_task = publish_template.apply()` or
`publish_flow = publish_template.apply()`, as appropriate. Prefer `_task` and
`_flow` over `_job`; the general "job" vocabulary is mainly useful in framework
internals handling tasks and flows uniformly. The
[lifecycle example](patterns.md#templates-and-executable-jobs) shows this distinction.
Private helpers use a leading underscore; constants use uppercase names.

## Dependencies and imports

Flows compose tasks and data classes. Tasks use contracts and external-service
operations. Data validation and conversion remain usable independently of the
dataflow and its tests. Place reusable functionality with the capability it
belongs to; reuse alone does not make a helper belong in `components/general`
or the global `util` package. Scenario fixtures and expectations belong in tests.

**Within Omnipy component code**, use relative imports within a component and
between components. This supports potential extraction of a component into a
separate repository. For example, imports in `components/remote/tasks.py` include:

```python
from omnipy.compute.task import TaskTemplate

from ..json.datasets import JsonDataset
from .models import HttpUrlModel
```

The relative-import guideline applies to in-Omnipy component code, not as a general
rule for applications, integration examples, or documentation. Imports from core
Omnipy modules can use their defining module paths. Documentation follows the
root `AGENTS.md` convention of `import omnipy as om`.

Preserve existing lazy-import arrangements for dependencies where relevant, such
as `remote/lazy_import.py` and `pandas/lazy_import.py`. Check existing test locations
before adding mirrored tests; keep narrative fixture organization aligned with
the [test guidance](patterns.md#validation-and-narrative-tests).

## Repository examples

- Module responsibilities: `src/omnipy/components/json/` and
  `src/omnipy/components/pandas/`.
- A module grown into a package: `src/omnipy/components/isa/models/`.
- Schema/Model pairing: `src/omnipy/components/isa/models/sample_schema.py`.
- Table-row schema specialization: `src/omnipy/components/tables/datasets.py`.
- Relative imports within and between components:
  `src/omnipy/components/remote/tasks.py`.
- Implementation modules with the test fixtures and mock services apart:
  `tests/integration/novel/full/sequence_data_brokering/`.
