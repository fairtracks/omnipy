## Omnipy v0.16.1 
_Release date: Sep 20, 2024_

v0.16 of Omnipy is a **huge** release, with a focus on performance and improvements on internals. It is also the first version where we will start providing detailed release notes.

_Note, the v0.16.1 release notes includes features from the v0.16.0 release, which was yanked due to issues with Python 3.12._

### New features in v0.16

- **General speedup**  
  Performance has been a major focus of the new release. Many of the major new features have been implemented to allow improved efficiency. Execution time of all examples in the [omnipy_examples](https://github.com/fairtracks/omnipy_examples) repo have been improved; in some cases the run times has been reduced to less than one tenth of the previous time. There is now very little overhead added by Omnipy on top of pydantic, so we should expect a major speed boost once support for pydantic v2 is added.
- **Reimplemented model snapshots for efficiency**  
  Model snapshots now make use of a memoization dictionary through the Pythons builtin `deepcopy` functionality, greatly speeding up snapshots of hierarchical models. The snapshots and the contents of the memoization dictionary are automatically deleted following garbage collection, thoroughly tested to provide no memory leaks.
- **Lazy snapshots**  
  Models now take snapshots only when they might change the first time, greatly improving efficiency of models with contents that do not change.
- **Remove unneeded nested Models**  
  Some models, such as `SplitLinesToColumnsModel` have been are reimplemented to remove second-level Omnipy models, and instead use doubly nested builtin collections, e.g. `Model[list[list[str]]` instead of `Model[list[Model[list[str]]]]`. JSON Model containers now use simple types at the terminal level (e.g. 42 instead of JsonScalarM(42)). For cases where the nested Omnipy models are required, this is now supported by a new non-default option (see next feature).
- **Dynamically convert elements to models**  
  Support for dynamically generating Model objects from the elements of parent collection Models, e.g. to generate Model[int] objects when iterating through the elements of a Model[list[int]]. Turned off by default through `dynamically_convert_elements_to_models` config for efficiency. 
- **Redesigned parametrised models and datasets to keep state**  
  Previous implementation of parametrised models and datasets required users to specify the parameter every time it was used, making in difficult to specify composite models that include parametrised submodels. Also, the implementation was complex and made it difficult to improve Omnipy with with improved functionality for conversion and serialization. New implementation is based on parametrizing models and datasets as new types in a highly decoupled fashion. It is unfortunately slightly more complex to define parametrized models and datasets in the new solution due to innate complexities in how Python implements type annotations. Having tested a number of alternatives, most of whom did not work out, it is clear that the new solution strikes a good balance between simplicity and flexibility.
- **Chained models**  
  A new solution for creating `mini-workflows` by chaining two or more models to form a single chained model. This reduces the need to specify linear flows for parsing, as exemplified in the new [BED file parser](https://github.com/fairtracks/omnipy_examples/blob/master/src/omnipy_examples/bed.py) example in [omnipy_examples](https://github.com/fairtracks/omnipy_examples).
- **Support for streaming to models by overloading `+` operator**  
  All models supporting the `+` operator can now be streamed to from builtin types or other models, triggering parsing as specified in the model. Example: `my_table_model = TableOfPydanticRecordsModel[MyColumns](); my_table_model += [['text', 12, True]]`. This in principle allows for large flows to continue where they left off in case of network issues, or faulty data in the middle of a longer stream. Proper failure management is yet to be implemented, but is made much easier through the support of streaming to Models. Basic interactive operations are also much simplified with this feature, e.g. for concatenation of data.
- **Improved automatic conversion**  
  - Mimicked operations now autoconvert the outputs, e.g. `Model[int](5) + 5 == Model[int](10)`.
  - Iterators and other sequence-like types such as range generators are now automatically recognized and converted sequence types such as `list` and `tuple`.
  - `PandasModel` and `PandasDataset` now support other models and datasets as input during initialisation. 
- **Improvements of model validation**  
  - Internals of validation functionality in the Model class has been harmonised and simplified.
  - Mimicked methods/attributes are validated also when interactive_mode=False
  - Pydantic models are validated before accessing attributes
- **Better handling of `None` values**  
  Pydantic v1 made some poor choices in how to handle `None` values, which has been very difficult to rectify within Omnipy. A previous hack to fix this issue has now been replaced with an improved hack which also fixed a number of previously "known issues" in the Omnipy tests. This refactoring is paving the way to a simplified move to pydantic v2, which is on the horizon, but postponed for now to focus on feature completion.
- **Other new features**  
  - Support for Python 3.12 and Prefect 2.20
  - Better support for forward references
  - Caching of type-related function calls such as Model.outer_type(), further improving efficiency
  - Dataset.load() now supports lists of paths or URLs as input
  - Implementation of a SetDeque util class for speedup of various features, including model snapshots
  - Support default values for `TypeVar`, through `typing_extensions` (otherwise a Python 3.13 feature)
  - Refactoring of root log, fixing issues with a stuck timestamp when running flows
  - Reimplemented and fixed `__name__`, `__qualname__`, and `__repr__` for Model and Dataset
  - Implemented support for `__call__()`, and `__bool__()` for Models
  - Implemented `copy()` for Model and Dataset
  - Implemented flexible `__setitem__` and `__delitem__` for Dataset, supporting indexing by ints, slices and tuples.
  - A ton of smaller bug fixes, new tests and code cleanup. Some refactoring, especially of new snapshot functionality, is postponed to later versions.