## Getting started

The design of Omnipy centers around two types of object, those related to data, and those related to
compute. The following two sections will introduce the basic concepts of each.

# Data

They Data objects centers around the Dataset class, which to a large degree operates as the Python
builtin `dict`, with the limitation that only strings are supported as keys. Contrary to the builtin
dicts, however, the values of a `Dataset` object is guaranteed to follow a particular type. This is
defined through using the `Model` class as a type argument to `Dataset`, while the actual type
guarantees are declared as a type argument to the `Model` class, e.g. `Dataset[Model[str]]`. This
Dataset variant is then operates as `dict[str, str]` with one important difference: the type
annotations of a builtin `dict` are not enforced at runtime. A `Datase[Model[str]]` object on the
other hand is guaranteed to only contain strings. This has important consequences for the fail
safety of code:

```python
# types are not enforced
my_dict: dict[str, str] = {'a': 'foo', 1: 'bar', 'c': 42}

# failures can occurr at any time
for key, val in my_dict.items():
    my_dict[key] = key + '_' + my_dict[key]
```

Here, the code in the for-loop can fail at any time due to bad data. In this example an exception is
raised in the second iteration due to the calculation: `1 + 'bar'`, which illegal in Python. Using
an omnipy Dataset, on the other hand, data is checked upfront. One the Dataset object is created,
the contents are guaranteed to follow the data model. Sudden failures due to unexpected types of
data will not occurr:

```python
from omnipy import Dataset, Model

# failures can happen here
my_dataset = Dataset[Model[str]]({'a': 'foo', 1: 'bar', 'c': 42})

# for loop is guaranteed to finish once started
for key, val in my_dataset.items():
    my_dict[key] = key + '_' + my_dict[key]
```

The above code illustrates another important feature of Omnipy datasets: data is "parsed, not
validated". This means that instead of failing hard and fast when there is a mismatch between the
data type and the guaranteed data model (following the concept of "validation*), standard Python
conversions (for example allowing `int("5") == 5`) are instead honored if relevant. In the code
example above, `my_dataset` would thus be *parsed* to `{'a': 'foo', '1': 'bar', 'c': '42'})` instead
of failing. Note that the parsing of the keys is done by the Dataset object, while the Model
objects (one per dataset value) are responsible for parsing of the values.

Data models can be defined on all levels of complexity, ranging from very generic to highly
specialised, e.g.:

```python
from omnipy import Model
from typing import Union
Model[object](set(1, 2, 3)).contents == set(1, 2, 3)
Model[list[Union[str, int]]]([1, 'abc', 2.3]).contents == [1, 'abc', 2]
```

One particular useful set of data models that comes predefined with Omnipy is the JSON models,
implemented as Model subclasses and respective Dataset subclasses. The most general variant of this
is the `JsonModel` and the `JsonDataset` which are defined recursively and as such able to
represent any JSON content.
