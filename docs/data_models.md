## Models parse and operate on structured data

The Model class is the most basic building block of the Omnipy library. It is a generic class that
has several important features:


### Omnipy makes use of Python type hinting to  define structured data models

To define a data model, simply provide a type hint as a type parameter to the Model class.
For example, to define a data model that represents a list of integers, you would write:

```python
from omnipy import Model

int_list_model = Model[list[int]]([1,2,3])
```

As `Model` are standard python classes, you can easily subclass them to reuse common data models
and/or define other model-specific functionality, e.g.:

```python
from omnipy import Model

class IntListModel(Model[list[int]]): ...

int_list_data = IntListModel([-1, 0, 1, 2, 3])
print(int_list_data)  # prints: IntListModel([-1, 0, 1, 2, 3])
```

As in `Pydantic`, the `Model` class can de defined to contain other `Model` classes, e.g.:

```python
class NestedModel(Model[dict[str, IntListModel]]): ...

nested_data = NestedModel({'a': [-1, 2, 4], 'b': [-4, 5, 6]})
print(nested_data)  # prints: NestedModel({'a': IntListModel([-1, 2, 4]), 'b': IntListModel([-4, 5, 6])})

```



### "Parse, don't validate" with Omnipy Model objects

While `pydantic` is focusing mostly on data validation, Omnipy `Model` objects are designed to 
be parsers, rather than just validators. (Please read _Technical note #2: "Parse, don't validate"_ 
on the [FAIRtracks.net website](https://fairtracks.net/fair/#fair-07-transformation) for more info
about this concept).

As in the non-strict mode of `pydantic`, the `Model` class will automatically parse input data to 
comply to the data model, e.g.:

```python
int_list_data = IntListModel(['-1', 0, '1', 2, '3'])
print(int_list_data)  # prints: IntListModel([-1, 0, 1, 2, 3])
```

Note that some of the data elements in the list above were strings. The `Model` class will
automatically parse these strings to integers as long as the string can be converted to
an integer through builtin Python casting (e.g. `int('-1') == -1`). Instead of failing hard and 
fast when there is a mismatch between the data type and the guaranteed data model (following the 
concept of "validation"), standard Python conversions are instead honored if relevant. A parser
follow the general programming guideline to allow as varied input data as possible, while producing
a guaranteed consistent output.

More complex parsing can be achieved by overriding the `_parse_data` class method in a subclass of 
`Model`, e.g.:

```python
from omnipy import Model

class OnlyPosIntListModel(Model[list[int]]):
    @classmethod
    def _parse_data(cls, data: list[int]) -> list[int]:
        return [i for i in data if i > 0]

pos_int_list_data = OnlyPosIntListModel([-1,0,1,2,3])
print(pos_int_list_data)  # prints: OnlyPositiveIntListModel([1, 2, 3])
```

Note that the implementation of parse methods will be simplified in a future version of Omnipy,
e.g. by using a `@parse` decorator:

```python
from omnipy import Model, parse

class OnlyPosIntListModel(Model[list[int]]):
    @parse
    def filter_positive_integers(data: list[int]) -> list[int]:
        return [i for i in data if i > 0]
```

### Model objects provide snapshots and automatic rollbacks

If an Omnipy `Model` model contains invalid data, a `ValidationError` will be raised. However, since
the model object is now in an invalid state, Omnipy will automatically roll back the contents to the
last validated snapshot. As a consequence, a model object will always contain valid data, even after
an invalid operation, e.g.:

```python
from omnipy import Model

class IntListModel(Model[list[int]]): ...

int_list_data = IntListModel([1, 2, 3])
try:
    int_list_data[1] = 'abc'  # raises a ValidationError
except ValidationError:
    print(int_list_data)  # prints: IntListModel([1, 2, 3])
```

This functionality is especially useful when users are working with Omnipy in an interactive session
such as a [Jupyter notebook](https://jupyter.org/) or in the Python console, where it is easy to 
make mistakes and cumbersome to rerun code. Hence, the snapshot and rollback feature of Omnipy 
`Model` objects can be disabled through the `interactive_mode` configuration, e.g.:

```python
from omnipy import Model

Model.config.interactive_mode = False
```

Or equivalently:

```python
from omnipy import runtime

runtime.config.data.interactive_mode = False
```

### Model objects can be operated as the modelled class

One potentially groundbreaking feature of Omnipy is the capability of model objects to automatically
mimic behaviour of the modelled class. A `Model` object  So e.g.
`Model[list[int]]()` is not just a run-time typesafe parser that continuously makes sure that the
elements in the list are, in fact, integers; the object can also be operated as a list using e.g.
`.append()`, `.insert()` and concatenation with the `+` operator; and furthermore: if you append an
unparseable element, say `"abc"` instead of `"123"`, it will roll back the contents to the previously
validated snapshot.