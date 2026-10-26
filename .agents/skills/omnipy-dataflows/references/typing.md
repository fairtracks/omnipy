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
Do not assume an explicit annotation such as a function parameter `Model[int]`
exposes every mimicked operation just because `Model[int](1)` is inferred with
those operations. Check the actual usage; a concrete `mimics`-decorated Model or
a capability protocol can supply the missing interface.

`assert_type` checks the inferred type when run through the type checker; running
the Python file alone does not check that assertion. Use the repository's
`uv run basedpyright` configuration. Mypy does not support the `mimics` technique;
its separate plugin coverage does not establish that these examples type-check.

## Expose the interface of a particular Model

Use `@om.mimics(SomeClass)` on a concrete Model when the checker needs the wrapped
class's interface. Keep the validation type in `Model[...]`. For example:

```python
import omnipy.util.pydantic as pyd


class StationSchema(pyd.BaseModel):
    station_id: str
    capacity: int


@om.mimics(StationSchema)
class StationModel(om.Model[StationSchema]):
    ...


class StationDataset(om.Dataset[StationModel]):
    ...


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

The current `mimics` implementation does not preserve generic arguments passed
directly to it. Do not rely on `@om.mimics(list[StationModel])` for typed list
elements. When a concrete wrapper needs an explicit parameterized interface,
give that interface a non-parameterized name:

```python
from typing import Protocol

from omnipy.shared.protocols.content import IsListContent


class IsStationList(IsListContent[StationModel], Protocol):
    ...


@om.mimics(IsStationList)
class StationListModel(om.Model[list[StationModel]]):
    ...


station_list = StationListModel([station])
assert_type(station_list[0].capacity, int)
```

Use the existing content protocols when they describe the required behavior:
they account for Model operations that preserve wrappers, such as list slicing.
For an ordinary `Model[list[int]]`, the built-in support already suffices; the
extra protocol is useful when specializing an interface the checker cannot infer.
This list illustrates an item's structured content, not a replacement for a
Dataset batch.

## Describe the capabilities a reusable consumer needs

Use a protocol when an operation should accept several implementations sharing
an interface. This can generalize both Model consumers and Dataset consumers:

```python
from collections.abc import Iterable


class HasCapacity(Protocol):
    @property
    def capacity(self) -> int:
        ...


class HasCapacityValues(Protocol):
    def values(self) -> Iterable[HasCapacity]:
        ...


def total_capacity(stations: HasCapacityValues) -> int:
    return sum(station.capacity for station in stations.values())


assert total_capacity(stations) == 4
assert total_capacity({'a': StationSchema(station_id='a', capacity=4)}) == 4
```

The read-only property expresses what the consumer needs without requiring
mutable fields of an identical type. The protocol supplies no validation or
implementation. Keep workflow boundaries typed as the appropriate Model/Dataset
when they must enforce a data contract; use capabilities for reusable operations
inside or across those boundaries.

Protocols and `mimics` have complementary roles: a protocol describes an
interface; `mimics` exposes an existing wrapped interface on a concrete Model to
the checker. Neither should claim methods that the runtime object does not have.
Avoid casts to dictionaries or `Any` just to silence an unresolved interface.

For framework/component maintenance that needs richer typing, existing code also
uses `TYPE_CHECKING`-only facades and constructor/item-access overloads. Inspect
`src/omnipy/data/_typing/mimic_models.py`, `Model.__new__`, `Dataset.__getitem__`,
and `HttpUrlModel` before extending that machinery. Verify runtime behavior and
inferred types separately; ordinary dataflows rarely need to reproduce it.
