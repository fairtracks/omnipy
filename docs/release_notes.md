## Omnipy v0.17.1

_Release date: Nov 9, 2024_

### Bug fixes in v0.17.1

- Fixed incorrect (lack of) closing of client sessions in asynchronous download tasks

## Omnipy v0.17.0

_Release date: Nov 7, 2024_

v0.17.0 of Omnipy was also a **huge** release, with a focus on features for building dynamic URLs
and loading datasets asynchronously from APIs. As a whole, the release was a major step towards
dependable communication with APIs, and the ability to handle large datasets in a concurrent and
efficient manner.

### New features in v0.17.0

- **Dynamic building of URLs**

  A new model, `HttpUrlModel`, has been added to support dynamic building of URLs from parts. It is
  more flexible than other similar solutions in the standard Python library, `Pydantic`, or other
  libraries, supporting the following features:
    - All parts can be easily edited at any time, using built-in types such as `dict` and `Path`
    - Automatic data type conversion _(generic Omnipy feature)_
    - Continuous validation after each change _(generic Omnipy feature)_
    - Error recovery: revert to last valid snapshot after invalid change _(generic Omnipy feature)_
    - Whenever the `HttpUrlModel` object is converted to a string, i.e. by insertion into a
      `StrModel` / `StrDataset` or being used to fetch data, the URL string is automatically
      constructed from the parts.
    - Builds on top of [`Url`](https://docs.pydantic.dev/2.0/usage/types/urls/) from
      `pydantic_core`, which provides basic validation, URL encoding as well as
      [punycode](https://en.wikipedia.org/wiki/Punycode) encoding of international domain names for
      [increased security](https://www.xudongz.com/blog/2017/idn-phishing/)

  With the `HttpUrlDataset`, dynamic URLs are scaled up to operate in batch mode, e.g. for building
  URLs for repeated API calls to be fetched concurrently and asynchronously.


- **`Dataset` upgraded to support state info for per-item tasks**

  To support per-item asynchronous tasks, the `Dataset` class has been upgraded to support state
  information for **pendinG** and **failed** tasks - _on a per-item basis._ This includes storing
  exceptions and other relevant info for each item that has failed or is pending. Dataset
  visualisation has been updated to relay this info to the user in a clear and concise way.


- **Job modifier `iterate_over_data_files` now supports asynchronous iteration**

  The `iterate_over_data_files` job modifier has been upgraded to support asynchronous iteration
  over data files. This allows for more efficient handling of large datasets, and is especially  
  useful when combined with the new `Dataset` state information for pending and failed tasks
  (see item above).


- **Automatic handling of asynchronous tasks based on runtime environment**

  Through the new `auto_async` job modifier, Omnipy now automatically detects whether the code is
  being run in an asynchronous runtime environment, such as a Jupyter notebook, and adjusts the
  execution of asynchronous tasks accordingly:
    - Technically, if `auto_async` is set to `True` (the default), the existing event loop is
      detected and used to run an asynchronous Omnipy `Task` as an `asyncio.Task`, allowing tasks to
      be run in the background if run from, _e.g._, a Jupyter notebook.
    - If no event loop is detected, Omnipy will create a new event loop and close it after the task
      is finished, allowing the task to be run synchronously in a regular Python script, or from the
      console.
    - The `auto_async` feature alleviates the complexity of running asynchronous tasks in different
      environments, and simplifies the combined use of asynchronous and synchronous tasks.

  _**Note 1:** Omnipy is yet to support asynchronous flows, so asynchronous tasks currently need to
  be run independently._

  _**Note 2:** `auto_async` does not support the opposite functionality, that is, running blocking
  synchronous tasks in the background in an asyncronous environment. This would require running the
  blocking tasks in threads, however Omnipy runtime objects (such as configs) are not (yet)
  thread-safe. Hence, synchronous tasks will block the event loop and any asynchronous tasks that
  are running there._


- **`Dataset` now supports asynchronous loading of data from URLs**

  The `Dataset` class has been upgraded to support asynchronous loading of data from URLs. This
  makes use of the new `HttpUrlDataset` class for building URLs, the new state information for
  failed and pending _per-item_ tasks, and the asynchronous iteration over data files. The fetching
  is implemented in the new `get_*_from_api_endpoint` tasks (where `*` is `json`,
  `bytes`, or `str`), built on top of the asynchronous `aiohttp` library, and supports the following
  features:
    - Automatic retry of HTTP requests, building on the `aiohttp_retry` library. Retries are
      configurable to retry for particular HTTP response codes, to retry a specified number of times
      and to use a specified algorithm to calculate the delay between retries.
    - Rate limiting of HTTP requests, building on the `aiolimiter` library. Rate limiting is
      configurable to limit the number of requests per time period, and to specify the time period
      used for calculation, indirectly also controlling the burst size. Adding to what is provided
      by the `aiolimiter` library, Omnipy ensures that the maximum rate limit is not exceeded also
      for the initial burst of requests.
    - Automatic reset of rate limiter counting and delays for subsequent batches of requests
    - Retries and rate limiting are configured individually for each domain. Omnipy ensures that
      HTTP requests in the same batch (e.g. provided in the same `HttpUrlDataset`) are coordinated
      according to their domain.
    - The default values for retries and rate limiting are set to reasonable values, so that this
      functionality is provided seamlessly for the users. However, these default values can be
      easily be changed if needed.
    - `Dataset.load()` now supports lists and dicts of paths or URLs (strings or `HttpUrlModel`
      objects) as input, as well as `HttpUrlDataset` objects.
    - Due to the asynchronous nature of the `get_*_from_api_endpoint` tasks, users in an
      asynchronous environment such as Jupyter Notebook can inspect the status of the download tasks
      while the download is in progress by inspecting the `Dataset` object.


- **Other new features / bug fixes / refactorings**
    - Refactored Model and Dataset __repr__ to make use of IPython pretty printer. Drops support for
      plain Python console for automatic pretty prints
    - Implemented NestedSplitToItemsModel and NestedJoinItemsModel for parsing nested structures of
      any level to/from strings (e.g. `"param1=true&param2=42"`)
    - Implemented MatchItemsModel, which allows for filtering of items in a list based on a
      user-defined functions
    - Implemented task `create_row_index_from_column()` and basic table datasets
    - Added support for optional fields in `PydanticRecordModel`
    - Fixed lack of `to_data()` conversion when importing mappings and iterators of models to a
      dataset
    - Refactored models and datasets for split and join, to reduce duplication and allow adjustments
      of params for all.

## Omnipy v0.16.1

_Release date: Sep 20, 2024_

v0.16 of Omnipy is a **huge** release, with a focus on performance and improvements on internals. It
is also the first version where we will start providing detailed release notes.

_Note, the v0.16.1 release notes includes features from the v0.16.0 release, which was yanked due to
issues with Python 3.12._

### New features in v0.16

- **General speedup**  
  Performance has been a major focus of the new release. Many of the major new features have been
  implemented to allow improved efficiency. Execution time of all examples in
  the [omnipy_examples](https://github.com/fairtracks/omnipy_examples) repo have been improved; in
  some cases the run times has been reduced to less than one tenth of the previous time. There is
  now very little overhead added by Omnipy on top of pydantic, so we should expect a major speed
  boost once support for pydantic v2 is added.


- **Reimplemented model snapshots for efficiency**  
  Model snapshots now make use of a memoization dictionary through the Pythons builtin `deepcopy`
  functionality, greatly speeding up snapshots of hierarchical models. The snapshots and the
  contents of the memoization dictionary are automatically deleted following garbage collection,
  thoroughly tested to provide no memory leaks.


- **Lazy snapshots**  
  Models now take snapshots only when they might change the first time, greatly improving efficiency
  of models with contents that do not change.


- **Remove unneeded nested Models**  
  Some models, such as `SplitLinesToColumnsModel` have been are reimplemented to remove second-level
  Omnipy models, and instead use doubly nested builtin collections, e.g. `Model[list[list[str]]`
  instead of `Model[list[Model[list[str]]]]`. JSON Model containers now use simple types at the
  terminal level (e.g. 42 instead of JsonScalarM(42)). For cases where the nested Omnipy models are
  required, this is now supported by a new non-default option (see next feature).


- **Dynamically convert elements to models**  
  Support for dynamically generating Model objects from the elements of parent collection Models,
  e.g. to generate Model[int] objects when iterating through the elements of a Model[list[int]].
  Turned off by default through `dynamically_convert_elements_to_models` config for efficiency.


- **Redesigned parametrised models and datasets to keep state**  
  Previous implementation of parametrised models and datasets required users to specify the
  parameter every time it was used, making in difficult to specify composite models that include
  parametrised submodels. Also, the implementation was complex and made it difficult to improve
  Omnipy with with improved functionality for conversion and serialization. New implementation is
  based on parametrizing models and datasets as new types in a highly decoupled fashion. It is
  unfortunately slightly more complex to define parametrized models and datasets in the new solution
  due to innate complexities in how Python implements type annotations. Having tested a number of
  alternatives, most of whom did not work out, it is clear that the new solution strikes a good
  balance between simplicity and flexibility.


- **Chained models**  
  A new solution for creating `mini-workflows` by chaining two or more models to form a single
  chained model. This reduces the need to specify linear flows for parsing, as exemplified in the
  new [BED file parser](https://github.com/fairtracks/omnipy_examples/blob/master/src/omnipy_examples/bed.py)
  example in [omnipy_examples](https://github.com/fairtracks/omnipy_examples).


- **Support for streaming to models by overloading `+` operator**  
  All models supporting the `+` operator can now be streamed to from builtin types or other models,
  triggering parsing as specified in the model. Example:
  `my_table_model = TableOfPydanticRecordsModel[MyColumns](); my_table_model += [['text', 12, True]]`.
  This in principle allows for large flows to continue where they left off in case of network
  issues, or faulty data in the middle of a longer stream. Proper failure management is yet to be
  implemented, but is made much easier through the support of streaming to Models. Basic interactive
  operations are also much simplified with this feature, e.g. for concatenation of data.


- **Improved automatic conversion**
    - Mimicked operations now autoconvert the outputs, e.g. `Model[int](5) + 5 == Model[int](10)`.
    - Iterators and other sequence-like types such as range generators are now automatically
      recognized and converted sequence types such as `list` and `tuple`.
    - `PandasModel` and `PandasDataset` now support other models and datasets as input during
      initialisation.


- **Improvements of model validation**
    - Internals of validation functionality in the Model class has been harmonised and simplified.
    - Mimicked methods/attributes are validated also when interactive_mode=False
    - Pydantic models are validated before accessing attributes


- **Better handling of `None` values**  
  Pydantic v1 made some poor choices in how to handle `None` values, which has been very difficult
  to rectify within Omnipy. A previous hack to fix this issue has now been replaced with an improved
  hack which also fixed a number of previously "known issues" in the Omnipy tests. This refactoring
  is paving the way to a simplified move to pydantic v2, which is on the horizon, but postponed for
  now to focus on feature completion.


- **Other new features**
    - Support for Python 3.12 and Prefect 2.20
    - Better support for forward references
    - Caching of type-related function calls such as Model.outer_type(), further improving
      efficiency
    - Dataset.load() now supports lists of paths or URLs as input
    - Implementation of a SetDeque util class for speedup of various features, including model
      snapshots
    - Support default values for `TypeVar`, through `typing_extensions` (otherwise a Python 3.13
      feature)
    - Refactoring of root log, fixing issues with a stuck timestamp when running flows
    - Reimplemented and fixed `__name__`, `__qualname__`, and `__repr__` for Model and Dataset
    - Implemented support for `__call__()`, and `__bool__()` for Models
    - Implemented `copy()` for Model and Dataset
    - Implemented flexible `__setitem__` and `__delitem__` for Dataset, supporting indexing by ints,
      slices and tuples.
    - A ton of smaller bug fixes, new tests and code cleanup. Some refactoring, especially of new
      snapshot functionality, is postponed to later versions.