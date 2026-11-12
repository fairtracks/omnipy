# Runtime mimicking and static typing

`Model[T]` mimics the wrapped class at runtime: its supported attributes, methods,
indexing, iteration, and operators are available through the Model. This applies
to classes generally, including domain schemas and third-party objects, subject to
the Model's supported operations. It is not limited to standard collections or
classes decorated with `mimics`. Validation belongs to the Model; the decorator
adds no runtime behavior.

Static typing is a separate problem: Python's type system cannot generally express
"a Model with the interface of its type argument." Omnipy supplies typing support
for common scalar and standard collection shapes, including list, dict, set, and
supported tuple shapes. Dataset item access also supplies specialized typing for
these Models. Start with the existing support:

```python
from typing_extensions import assert_type

import omnipy as om

numbers = om.Model[list[int]]([1, 2])
numbers.append(3)
assert_type(numbers[0], int)

counts = om.Dataset[om.Model[list[int]]]({'station-a': [1, 2]})
assert_type(counts['station-a'][0], int)
```

The typing machinery specializes constructor results and Dataset item access.
Assume a Model correctly mimics its wrapped type, including when explicitly
annotated as a function parameter such as `Model[int]`. If runtime behavior does
not match, report the discrepancy and/or suggest a fix rather than designing
around it. A checker failing to expose that interface is a separate static-typing
limitation; a concrete `mimics`-decorated Model or a capability protocol can make
the interface visible.

`assert_type` checks the inferred type when run through the type checker; running
the Python file alone does not check that assertion. Use the repository's
`uv run basedpyright` configuration. Mypy does not support the `mimics` technique;
an Omnipy mypy plugin is future work. The repository's `pytest-mypy-plugins` test
coverage does not establish that the `mimics` examples type-check with mypy.
Explicit protocol inheritance is an alternative for interfaces that need mypy
support, as shown below.

Prefer mypy support for additions to Omnipy library code, including components;
use mypy-compatible typing facades where the built-in support is insufficient.
For examples, tutorials, and tests, the shorter `mimics` variant may be preferred
for readability, unless mypy compatibility is part of their purpose.

## Methods hidden by Model

`om.is_model_of_dataset_instance(value)` detects Models currently containing a Dataset
through mimicking; `value.dataset` then returns that existing Dataset without validation
or conversion. `om.is_model_of_dataset_subclass(type_form)` probes default construction
of Model subclasses; only construction failure falls back to the original direct
`Model[Dataset]` type check. Successful construction with non-Dataset content returns
`False`. For Datasets themselves, use `om.is_dataset_instance()` or
`om.is_dataset_subclass()`. These helpers do not authorize changes to caller behavior.

Mimicking forwards attributes that `Model` does not define itself. Methods that
`Model` defines, such as `load()`, `load_into()`, `save()`, `to_data()` and the
display methods (`peek()`, `full()`, ...), take precedence over methods with the
same name on the wrapped object. To call such a method of the wrapped object, call
it on `.content`, and then revalidate if the method changed the content:

```python
report.content.save()
report.validate_content()
```

This is a general limitation of overloaded names, not specific to any Model type.

## Expose the interface of a particular Model

Use `@om.mimics(SomeClass)` on a concrete Model when the checker needs the wrapped
class's interface. Keep the validation type in `Model[...]`. For example:

```python
import omnipy.util.pydantic as pyd


class StationSchema(pyd.BaseModel):
    station_id: str
    capacity: int


@om.mimics(StationSchema)
class StationModel(om.Model[StationSchema]): ...


class StationDataset(om.Dataset[StationModel]): ...


station = StationModel({'station_id': 'a', 'capacity': 4})
assert_type(station.capacity, int)
stations = StationDataset({'a': station})
assert_type(stations['a'].capacity, int)
```

Specializing the Dataset with the typed item Model carries its interface into
item access. A Dataset already exposes its own mapping interface; do not decorate
the Dataset with `mimics(StationSchema)` or pretend it is one station. Check the
actual access paths used, including indexing and iteration, before adding custom
typing machinery. A subclass alone does not automatically expose every arbitrary
wrapped class to every checker.

The same approach applies to a `ConverterModel` whose public interface is its
target schema: decorate the concrete mapper with `mimics(TargetSchema)`.

## Bind a parameterized interface with a protocol

Use the existing content protocols when they describe the required behavior:
they account for Model operations that preserve wrappers, such as list slicing.
For an ordinary `Model[list[int]]`, the built-in support already suffices. When
a concrete wrapper needs an explicit parameterized interface, there are two
approaches.

### Inherit the protocol in a type-checking facade

For mypy-compatible list typing, follow `SplitToItemsModelBase` in
`src/omnipy/components/raw/models.py`: inherit from `PlainModel` and
`IsListContent[StationModel]` under `TYPE_CHECKING`, retaining the ordinary
Model subclass at runtime.

```python
from typing import TYPE_CHECKING, Protocol

from omnipy.shared.protocols.content import IsListContent

if TYPE_CHECKING:
    from omnipy.data.typing.model import PlainModel

    class StationListModel(  # type: ignore[misc]
        PlainModel[list[StationModel]], IsListContent[StationModel]
    ): ...
else:

    class StationListModel(om.Model[list[StationModel]]): ...


station_list = StationListModel([station])
assert_type(station_list[0], StationModel)
assert_type(station_list[:], StationListModel)
```

The protocol is inherited by the Model's static facade, not merely defined as a
separate interface. Keep it out of the runtime bases: content protocols contain
placeholder methods, while the actual behavior and validation come from Model.
`PlainModel` is an internal, type-checking-only facade that avoids the specialized
constructor inference of `Model.__new__`.
In the current checkout, mypy reports conflicting inherited `json` signatures
from `BaseDisplayMixin` and Pydantic's `BaseModel` on this facade. This is a known
Pydantic v1 issue, expected to be resolved in v2. The targeted
`type: ignore[misc]` suppresses that conflict, not the list operations; remove it
once the issue is resolved.

This gives mypy and basedpyright the list interface and its element type without
`mimics`. It does not make the earlier `mimics`-decorated `StationModel`'s schema
attributes visible to mypy; typing `station_list[0].capacity` there also requires
a mypy-visible interface for the item Model.

### Expose a named protocol with `mimics`

When mypy support is not required, `mimics` keeps a single Model declaration.
The current implementation does not preserve generic arguments passed directly
to it: do not rely on `@om.mimics(list[StationModel])` for typed elements.
Instead, give the parameterized interface a non-parameterized name. This is an
alternative definition of `StationListModel`, not an additional wrapper:

```python
class IsStationList(IsListContent[StationModel], Protocol): ...


@om.mimics(IsStationList)
class StationListModel(om.Model[list[StationModel]]): ...


station_list = StationListModel([station])
assert_type(station_list[0], StationModel)
assert_type(station_list[0].capacity, int)
```

| Approach | Advantages | Trade-offs |
| --- | --- | --- |
| Protocol inheritance under `TYPE_CHECKING` | Explicit generic arguments; supports mypy and basedpyright; leaves runtime inheritance unchanged. | Separate static/runtime declarations must stay aligned; uses the internal `PlainModel` facade; currently needs a targeted mypy suppression for the known Pydantic v1 `json` issue. |
| `mimics` with a named protocol | One Model declaration; concise; no runtime behavior or inheritance changes. | Not supported by mypy; parameterized interfaces need a named protocol because decorator arguments lose generic parameters. |

For additions to Omnipy library code, prefer the mypy-compatible protocol
inheritance approach when an explicit interface is needed. In examples,
tutorials, and tests, `mimics` may be preferable for its shorter declaration;
retain mypy support where it is part of the example or test's purpose. Both
describe existing runtime mimicking, not new behavior. This list illustrates an
item's structured content, not a replacement for a Dataset batch.

## Describe the capabilities a reusable consumer needs

Use a protocol when an operation should accept several implementations sharing
an interface. This can generalize both Model consumers and Dataset consumers:

```python
from collections.abc import Iterable


class HasCapacity(Protocol):
    @property
    def capacity(self) -> int: ...


class HasCapacityValues(Protocol):
    def values(self) -> Iterable[HasCapacity]: ...


def total_capacity(stations: HasCapacityValues) -> int:
    return sum(station.capacity for station in stations.values())


assert total_capacity(stations) == 4
assert total_capacity({'a': StationSchema(station_id='a', capacity=4)}) == 4
```

The read-only property expresses what the consumer needs without requiring
mutable fields of an identical type. The protocol supplies no validation or
implementation. Keep dataflow boundaries typed as the appropriate Model/Dataset
when they must enforce a data contract; use capabilities for reusable operations
inside or across those boundaries.

Protocols describe interfaces. Inheriting one in a type-checking facade or using
`mimics` can expose an existing wrapped interface on a concrete Model to the
checker. Neither should claim methods that the runtime object does not have.
Avoid casts to dictionaries or `Any` just to silence an unresolved interface.
When a checker cannot express a valid runtime operation, prefer a targeted
`# type: ignore[code]` or `# pyright: ignore[rule]` on the reported line rather
than casting the problem away with catch-all types.

For framework/component maintenance that needs richer typing, existing code also
uses `TYPE_CHECKING`-only facades and constructor/item-access overloads. Inspect
`src/omnipy/data/_typing/mimic_models.py`, `Model.__new__`, `Dataset.__getitem__`,
and `HttpUrlModel` before extending that machinery. Verify runtime behavior and
inferred types separately; ordinary dataflows rarely need to reproduce it.
