## Omnipy v0.22.2

_Release date: Feb 3, 2026_

### New features and bugfixes in v0.22.2

- Implemented `pre-commit` script `expand_docstr_macros` to automatically
  expand docstring macros before commit.
- Harmonize docstrings for all Model and Dataset display methods with
  macros. Support both static and runtime docstring generation (e.g. both
  `pyright` and `help()`). Fix typing errors
- Fixed bug to allow nested Datasets to set values using parameters of the
  Dataset.__init__() method as keys (e.g. 'self', 'value', 'data')
- Changed dependency management from `poetry` to `uv`.
- Switched `pyright` dependency with `basedpyright`.


## Omnipy v0.22.1

_Release date: Jan 8, 2026_

### New features and bugfixes in v0.22.1

- Initial implementation of to() and do() methods for Models and Datasets, 
  including `placeholder` variables `x`, `m`, and `F`.
- Fixed Dockerfile to install correct versions of Pyright, ipyvue, and 
  ipyvuetify.


## Omnipy v0.22.0

_Release date: Jan 8, 2026_

Omnipy v0.22.0 brings major improvements to data model flexibility and
type system robustness. This release focuses on enhanced support for
nested datasets, improved table model architecture, and comprehensive
typing improvements across the codebase. The JSON parsing system has been
significantly enhanced, and new display capabilities make working with
complex nested data structures more intuitive.

### New features and changes in v0.22.0

- **Nested Dataset support**

  Major architectural enhancement enabling nested datasets:
  
  - `Dataset` objects can now contain other datasets as items, allowing for
    arbitrarily nested dataset structures, implemented through the new 
    `NestedDataset` class. `Union` types are also now allowed in `Dataset` 
    type specialization.
  - Implemented configurable limits for controlling display of deeply nested
    structures. Deep nested content automatically falls back to JSON display
    for improved readability
  - Enhanced Dataset validation to properly handle iterables as input and
    prevent invalid iterators. Pydantic v1 workaround to prevent unwanted
    coercion of nested structures.
  - `Model[Dataset]` objects now display as datasets for intuitive 
    interaction


- **Enhanced JSON parsing and display**

  Comprehensive improvements to JSON handling:
  
  - `JsonModel` now parses all JSON types except JSON strings (e.g., `"hi"`)
  - Helper methods for parsing and serializing JSON outside of models
  - New `json()` display method in `ModelDisplayMixin`
  - Fixed compact JSON reflowing algorithm, preventing line overflow
  - `ConfigBase` now has `as_model()` method returning `JsonDictModel`
  - Improved type hints for JSON models throughout


- **Table model architecture overhaul**

  Complete redesign of table models for better performance and flexibility:
  
  - Split table models into `RowWise` and `ColumnWise` types with conversion
    support, such as `RowWiseTableWithColNamesModel` and 
    `ColumnWiseTableWithColNamesModel`.
  - Implemented `IteratingPydanticRecordModel` for optimized validation of
    column-wise and row-wise data (with a focus on the former). Will allow
    fast validation of e.g. Pandas DataFrames or Numpy/Bionumpy structured
    arrays in future releases. This feature was implemented on top
    of feather-light row-wise iteration to 
    `ColumnWiseTableWithColNamesModel` through `IterRow`
  - Support for simplified concatenation through addition operator for 
    column-wise tables (row-wise tables can already be concatenated this
    way).
  - Added `RowWiseTableModel` implementation
  - Refactored `SplitLinesToColumnsByCommaModel` and 
    `JoinColumnsByCommaToLinesModel`, and added `SplitToItemsByTabModel`
    with associated parameters
  - First implementation of table displays!


- **Comprehensive typing improvements**

  Major enhancements to type system and static analysis support:
  
  - Introduced `IsList`, `IsDict`, and other protocols for builtin types
  - Replaced direct subclassing with protocols for mimic typing in `Model`
    and `Dataset`
  - Enhanced type hints in `Dataset` and `Model` classes with additional
    overloads
  - Improved typing of `ChainX` models with support for `Dataset` and 
    `Union` types
  - Simplified typing of `ColumnWiseTableWithColNamesModel` and other table
    models
  - Support for `Model` of types with no default values
  - Pydantic v1 hack for supporting models with generic types
  - Introduced `TypeVarTuple` for better tuple handling
  - Added detection of which type checker is running through `TYPE_CHECKER`
    variable
  - Fixed numerous typing issues across multiple modules


- **Model and Dataset enhancements**

  Various improvements to core data structures:
  
  - `JsonScalarModel` is now a proper model subclass
  - Support for enums as values in Omnipy models
  - Expanded general sequence support in `Model` to handle any iterable
  - Name changes: `NestedStrWithListModels` → `NestedListsAndStrsWithModels` (and similar)
  - Fixed edge case issue for `_NestedSplitToItemsModel`


- **Display and UI improvements**

  - Renamed horizontal overflow mode: `WORD_WRAP` → `WRAP`
  - Removed unneeded extra resize rendering for `browse()`
  - Fixed bug with syntax coloring of text content
  - Partly fixed edge case issues with very long lines for compact JSON
  - `Dataset.full()` now based on `peek()` instead of `list()`
  - Renamed random color styles: `random-t16-dark` → `random-dark-t16` (and
    similar)


- **Performance improvements**

  - Improved import performance greatly by removing solara import for non-
    Jupyter UI types, and other improvements
  - Miscellaneous speedups across various operations
  - Added `open_func` parameter to `import_directory` for BioNumpy support
  - Implemented `class_or_instance_method` decorator, which allows method to
    be called as class method or instance method. Will be used to unify
    `load()` and `load_into()` methods.


- **Development and testing**

  - LiteralEnum checks now only run when in develop mode (editable install)
  - Workaround documented for `Chain2` with `Union` types
  - Updated mypy version
  - Clean up of inheritance for `Config` classes and protocols with 
    `IsConfigBase` intermediate
  - Updated IHEC and nobel notebooks
  - Various cleanups and removed unneeded tests. Skipped some tests that are
    known to fail


## Omnipy v0.21.2

_Release date: Nov 3, 2025_

### Bugfixes in v0.21.2

- Updates to Dockerfile and related README to fix issues with JupyterHub
- Fixed bug with `browse()` method for `Model` and `Dataset` when local
  cache folder is missing
- Fixed issue showing style when random style is selected as keyword 
  argument


## Omnipy v0.21.1

_Release date: Nov 1, 2025_

### Bugfixes in v0.21.1

- Fixed major import issue for straight install, without pytest
- Updated Dockerfile to import main branch of Omnipy


## Omnipy v0.21

_Release date: Nov 1, 2025_

v0.21 represents a major milestone for Omnipy with the introduction of a
comprehensive output styling and pretty-printing system built from the
ground up. This release also brings significant performance improvements
through lazy loading of dependencies and intelligent caching, as well as
Docker integration for seamless Jupyter deployment.

### New features and changes in v0.21

- **Complete output styling and pretty-printing system (brand new!)**
  
  A comprehensive pretty-printing and layout system has been implemented
  from scratch, wrapping the [Rich](https://github.com/Textualize/rich)
  library while solving complex boundary and dimension challenges:

  - **Direct access to data** at your fingertips. Model and Dataset contents
    expand to full size, intelligently utilizing available display space
    with syntax-highlighted layout in full color:
    - New method `peek()` for Datasets and Models gives quick access to
      content previews.
    - `Dataset.list()` gives a detailed listing of entries in the dataset.
    - As before, hitting `Enter` on a Model or Dataset in Jupyter shows a
      concise summary, a `peek` for a Model, or a `list` for a Dataset.
    - New method `full()` for Models and Datasets shows the complete output
      without any truncation (of a `peek` or `list` respectively).
    - New method `browse()` for Models and  Datasets shows the full output
      in new browser tabs for easy scrolling and exploration of large
      contents. Particularly useful for large Datasets.
  
  - **Advanced panel system**: A complete panel system has been implemented
    supporting dynamic pretty-printing of Python objects, compact JSON,
    hexdumps, syntax-highlighted text, and nested layouts, making the most
    of available display space.
  
  - **Intelligent layout and flow engine**: Built sophisticated layout
    optimization with automatic width distribution, proportional sizing,
    cropping (horizontal and vertical) with title and content ellipses.
    Implemented comprehensive reflow algorithms automatic frame
    adjustments to fit content while respecting constraints, while also
    handling edge cases like empty layouts, single panels, and complex
    nested structures.
  
  - **Rich color and syntax highlighting**: Added over 300 color styles,
    with automatic loading of Base16 themes from the 
    [Tinted Theming project](https://github.com/tinted-theming), in 
    addition to the styles from the 
    [Pygments library](https://pygments.org/styles/). Color styles support
    transparent/solid background handling for both terminal and HTML 
    outputs, and configurable fonts/CSS. Syntax highlighting based on 
    [hundreds of Pygments lexers](https://pygments.org/languages/).
    Output as ANSI terminal codes or HTML, with plain text, stylized text
    and colorized output variants.
  
  - **Comprehensive User Interfaces support**: Added support for various UI
    contexts, including terminal ANSI output for the basic Python terminal
    interpreter, the IPython interpreter, the PyCharm console, Jupyter
    notebook and JupyterHub, and HTML export as web pages or embedded tags
    (e.g. for documentation). Autodetection of UI contexts.
  
  - **Configuration system**: Comprehensive configuration of all aspects of
    output presentation, including color styles, fonts, panel and title
    styles, syntax language, background transparency, height and width
    limits, indentation, cropping behavior, and more. Configurable
    globally or per display call.
  
  - **Other features**: 
    - Support for variable character widths.


- **Jupyter and UI integration**
  
  Seamless integration with Jupyter environments through dynamic resizing
  and reactive components:
  
  - Outputs in Jupyter are reactive, with automatically resizing and
    restyling based on e.g. window size, global config changes and
    selection of dark/light theme.
  - Reactive compunents implemented using the Solara library, which
    simplifies development of reactive components and Jupyter widgets
    using plain Python or VueJS.
  - JupyterLab settings and scrolling workarounds, and other CSS fixes.


- **Performance and caching improvements**
  
  Major performance enhancements through intelligent caching strategies:
  
  - Import of omnipy is now significantly faster due to lazy loading of
    submodules
  - Bounded `lru_cache` for draft panel formatting to prevent unbounded
    cache growth while maintaining fast lookups
  - Caching for downloaded base16 themes and other remote resources
  - Rendering efficiency improvements to reduce unnecessary reflows


- **Dockerfile and container support**
  
  Complete Docker setup for running Omnipy in JupyterLab.


- **Documentation overhaul**
  
  Extensive improvements to documentation:
  
  - Added Omnipy logos and overview illustration
  - Complete README rewrite and reorganization into new 'Data models'
    section
  - Migration of all Markdown files into `docs` directory
  - Detailed inline documentation for output styling: color styles, HTML
    export variants, pretty-printing, base16 themes
  - Added examples and notebooks demonstrating new features
  - Color and style updates


- **Dataset and data loading enhancements**
  
  - API change: `Dataset.load()` → `load_into()`; `Dataset.load()` is now a
    class method
  - Added `as_mime_type` parameter to loading functions
  - Fixed synchronous testing of asynchronous endpoints


- **Tests and quality improvements**
  
  - Extensive test coverage for panels, layout flow, cropping, HTML output,
    and color styles
  - Fixed previously non-running tests due to bugs


- **Miscellaneous improvements**
  
  - Python 3.13 compatibility
  - Cleanup: removed debug prints, fixed typos, improved docstrings, import
    sorting fixes, and typing fixes across multiple modules
  - Improved macOS web browser support for open() (used in `browse()`)
  - Added overridable `_get_default_factory()` in `Model`
  - Added`.editorconfig` for consistent formatting
  - Added example notebooks
  - Updated dependencies and CI adjustments


## Omnipy v0.20.1

_Release date: Jan 7, 2025_

### New features in v0.20.1

- Improved speed of JSON-heavy operations by removing unneeded model
  creation
- Refactor Prefect engine to remove redundant code
- Fix to run `dataset.load()` from sync tasks (e.g. bed in omnipy_examples)
- Added `StrictStrModel`, `StrictBytesModel` and related `-Dataset` classes
- Implemented `AutoResponseContentsModel` (and `-Dataset`) for automatic
  decoding of response contents based on content type
- Implemented
  `get_auto_from_api_endpoint()` and deployed in `Dataset.load()`


## Omnipy v0.20.0

_Release date: Jan 6, 2025_

Omnipy v0.20.0 has focused on improving the documentation and code
structure of the project, as well as fixing a few bugs from the v0.90
release.

A previous attempt to configure a reference documentation auto-build
solution based on the (seemingly unmaintained)
[portray](https://github.com/timothycrosley/portray) library has now been
abandoned in favor of [mkdocstrings](https://mkdocstrings.github.io/). In
v0.20.0, the documentation setup has been completely overhauled to support
a clean and readable structure. While the new system might be slightly
less flexible, it is more standardised and seems to require less custom
code to support the basic features needed byOmnipy.

### New features in v0.20.0

- **Finalized transition of documentation to `mkdocstrings`, including
  massive code reorganization**

  - Fixed bug causing the documentation build to fail
  - Consistent styling, including an updated color scheme and improved
    readability
  - Specified a large number of code elements as private (i.e. of interest
    mostly to core `Omnipy` developers), and thus excluded from the
    documentation. This moves the reference documentation from the previous
    confused and unintelligible mess to a clear and understandable
    structure.
  - As part of the reorganization, the previous `omnipy.modules` submodule 
    has been renamed to `omnipy.components`, and the `omnipy.api` submodule
    has been renamed to `omnipy.shared`.
  - Auto-generated documentation now supports including inherited members on
    a per-module basis. The default settings have been adjusted to what
    makes most sense for each submodule.
  - Removed outdated code from the previous `portray`-based solution.
  - Misc smaller reorganizations and cleanups.
  - Docstrings and general documentation are still mostly missing, but will
    be a priority for the next few releases.


- **Updated dependency management**
  - Updated to use [Poetry](https://python-poetry.org/) v2.0.0 (released Jan 5!), including
    restructure of `pyproject.toml` file in accordance
    with [PEP 508](https://peps.python.org/pep-0508/).
  - Replaced embedded [tabulate](https://pypi.org/project/tabulate/) package
    with the [tabulated](https://pypi.org/project/tabulated/) fork. The
    `tabulate` package was previously included with the Omnipy source code
    in order to provide for non-released bug fixes that are included in
    the `tabulated` fork). The current plan is to move completely away
    from `tabulate`.


- **Smaller bug fixes and improvements**
  - Fixed `test_dataset::test_import_and_export` issue introduced in v0.19.0
  - PandasModel.__init__() now converts from all four types of tables
    supported by Omnipy
  - Refactored away `_Model` and similar private classes added in the
    v0.19.0 auto-complete hack


## Omnipy v0.19.0

_Release date: Dec 17, 2024_

The v0.19.0 release of Omnipy follows the focus from v0.18.0 on supporting
code completion and/or validation by static type analysers like `pyright`
and `mypy`. In particular, this release improves type analysis of `Omnipy`
configs, as well as Model objects, specifically basic support for typing
that Model objects can mimic the functionality of its type arguments.

### New features in v0.19.0

- **Omnipy configs have transitioned from basic dataclasses to pydantic
  BaseModel. Refactoring of related functionality**

  - Cleaned up pydantic imports
  - Refactored functionality for otherwise decoupled objects to subscribe to
    changes in runtime objects and configs. Refactored tests for specific
    subscriptions.
  - Switched type of config classes from Python dataclasses to Pydantic
    BaseModels
  - `JobCreator` now always has a `JobConfig` instance, even if runtime is
    not created yet. If so, runtime later adopts the existing JobConfig
    instance


- **Improved typing of core classes to improve validation and/or
  auto-completion using static type analysers**

  - Improved and fixed typing for `Dataset` and `Model`
  - Improved typing of `Dataset.clone_dataset_cls()`. Cleanup
  - Hack to let pyright (and possibly other type checkers) allow
    autocomplete for mimicking ops believing that Models also inherit from
    their type arguments
  - Adding root type as type hint for `Model.__init__()`, in addition to
    object
  - Added type hint overload hack also to `Dataset.__getitem__()`. Fixed and
    reorganised the type hint hacks for `Model` and `Dataset`
  - Added note on Python type checkers


- **Other new features / bug fixes / refactorings**
  - Better support for keeping Pandas DataFrames (and other types) inside a
    Model after operations
  - Added convenience functions to detect IPython and Jupyter Notebooks
  - Bugfix in `QueryParamsModel` for URL-encoded parameters that encode `&`
    or `=`


## Omnipy v0.18.0

_Release date: Dec 6, 2024_

v0.18.0 of Omnipy another **huge** release in terms of code line
modifications, but not so much in terms of new features. The main new
feature is, however, a very important one - the ability to make use of
static type analysers like `pyright` to provide code-completion and/or
validation of `Omnipy` tasks and flows. Also, Omnipy documentation is
starting to receive some love!

### New features in v0.18.0

- **Extensive update to type hints for tasks and flows, supporting code
  auto-completion**

  - The type hints for tasks and flows have been updated to provide better
    support for code auto-completion. This includes typing the class
    decorator factory `callable_decorator_cls` in a way that is currently
    supported by major static analysis tools, including `mypy`, `pyright`
    and `Pycharm`.
  - Type hints now include generics for the parameters and return type of
    decorated functions. This allows for better type checking and code
    completion of tasks and flows.
  - Job modifiers are now properly supported with type hints for the
    `__call__` method of task and flow templates.
  - Code completion has been tested in `PyCharm` and `Jupyter notebook`
    using `Pyright` language server, which is now the recommended
    auto-completion setup. `Pycharm` basic auto-completion does not
    correctly support the new `Python` type hint features needed for
    auto-completion.
  - A large number of type hint issues have been fixed.
  - Type hint updates are massive, and spans the entire code base, but with
    a focus on the `compute` module and it's tests.


- **Moved document generation to `mkdocs` and `mkdocstrings`**

  - The documentation has been moved from `portray` to `mkdocs` and
    `mkdocstrings`. This change was made due to the lack of updates from
    `portray`. The new setup allows for more flexibility and control over
    the documentation, and provides a more stable and future-proof
    solution.
  - Reference documentation is yet to be cleaned up and updated to the new
    format.


- **Started writing general documentation**

  - The documentation has been updated with a new section on Python typing,
    describing a historical and conceptual background for Omnipy's new
    take on typing in Python. The description starts with the traditional
    `duck typing` of Python, moved through `type annotations` for static
    analysis and `pydantic` take on making use of type annotation for
    runtime validation. The section ends with a description of how
    `Omnipy` extends the functionality of `pydantic` to provide the safety
    and predictability of static typing functionality within the context
    of the flexible type dynamics possible in Python.
  - Added general section describing the `Model` class, and how it is used
    to define data models as parsers in Omnipy, as well as snapshots,
    automatic rollback, functional mimicking, and other features of the
    `Model` class.


- **Other new features / bug fixes / refactorings**
  - Allow Dataset.load() of urls with specified keys
  - Added TsvTableModel, TsvTableDataset, CsvTableModel, and CsvTableDataset
  - Fixed inheritance of Params classes for a few join/split Models in the
    `raw` module
  - Fixed a number of issues with the CI workflows:
    - Fixed test code that caused crashes in Python particular Python
      versions.
    - Fix for strange time formatting issue in the Python 3.11 VM
    - Decreased `run_time_min` for `test_rate_limiting_client_session` due
      to new and more efficient version of `aiolimiter`
    - Updated pre-commit tools.
    - Removed parallel run of yapf checks to fix strange issue with `yapf`
      and `pickle`


## Omnipy v0.17.2

_Release date: Nov 9, 2024_

### Bug fixes in v0.17.2

- Fixed an inconsistency between `Dataset.__init__()` and
  `Dataset.__setitem__()` methods. Directly setting dataset items now
  converts Models using `to_data()` +`from_data()`.


## Omnipy v0.17.1

_Release date: Nov 9, 2024_

### Bug fixes in v0.17.1

- Fixed incorrect (lack of) closing of client sessions in asynchronous
  download tasks


## Omnipy v0.17.0

_Release date: Nov 7, 2024_

v0.17.0 of Omnipy was also a **huge** release, with a focus on features
for building dynamic URLs and loading datasets asynchronously from APIs.
As a whole, the release was a major step towards dependable communication
with APIs, and the ability to handle large datasets in a concurrent and
efficient manner.

### New features in v0.17.0

- **Dynamic building of URLs**

  A new model, `HttpUrlModel`, has been added to support dynamic building of
  URLs from parts. It is more flexible than other similar solutions in the
  standard Python library, `Pydantic`, or other libraries, supporting the
  following features:
  - All parts can be easily edited at any time, using built-in types such as
    `dict` and `Path`
  - Automatic data type conversion _(generic Omnipy feature)_
  - Continuous validation after each change _(generic Omnipy feature)_
  - Error recovery: revert to last valid snapshot after invalid change
    _(generic Omnipy feature)_
  - Whenever the `HttpUrlModel` object is converted to a string, i.e. by
    insertion into a `StrModel` / `StrDataset` or being used to fetch
    data, the URL string is automatically constructed from the parts.
  - BUilds on top of
    [`Url`](https://docs.pydantic.dev/2.0/usage/types/urls/) from
    `pydantic_core`, which provides basic validation, URL encoding as well
    as [punycode](https://en.wikipedia.org/wiki/Punycode) encoding of
    international domain names for
    [increased security](https://www.xudongz.com/blog/2017/idn-phishing/)

  With the `HttpUrlDataset`, dynamic URLs are scaled up to operate in batch
  mode, e.g. for building URLs for repeated API calls to be fetched
  concurrently and asynchronously.


- **`Dataset` upgraded to support state info for per-item tasks**

  To support per-item asynchronous tasks, the `Dataset` class has been
  upgraded to support state information for **pendinG** and **failed** tasks
  - _on a per-item basis._ This includes storing exceptions and other
  relevant info for each item that has failed or is pending. Dataset
  visualisation has been updated to relay this info to the user in a clear
  and concise way.


- **Job modifier `iterate_over_data_files` now supports asynchronous
  iteration**

  The `iterate_over_data_files` job modifier has been upgraded to support
  asynchronous iteration over data files. This allows for more efficient
  handling of large datasets, and is especially useful when combined with
  the new `Dataset` state information for pending and failed tasks (see item
  above).


- **Automatic handling of asynchronous tasks based on runtime environment**

  Through the new `auto_async` job modifier, Omnipy now automatically
  detects whether the code is being run in an asynchronous runtime
  environment, such as a Jupyter notebook, and adjusts the execution of
  asynchronous tasks accordingly:
  - Technically, if `auto_async` is set to `True` (the default), the
    existing event loop is detected and used to run an asynchronous Omnipy
    `Task` as an `asyncio.Task`, allowing tasks to be run in the
    background if run from, _e.g._, a Jupyter notebook.
  - If no event loop is detected, Omnipy will create a new event loop and
    close it after the task is finished, allowing the task to be run
    synchronously in a regular Python script, or from the console.
  - The `auto_async` feature alleviates the complexity of running
    asynchronous tasks in different environments, and simplifies the
    combined use of asynchronous and synchronous tasks.

  _**Note 1:** Omnipy is yet to support asynchronous flows, so asynchronous
  tasks currently need to be run independently._

  _**Note 2:** `auto_async` does not support the opposite functionality,
  that is, running blocking synchronous tasks in the background in an
  asyncronous environment. This would require running the blocking tasks in
  threads, however Omnipy runtime objects (such as configs) are not (yet)
  thread-safe. Hence, synchronous tasks will block the event loop and any
  asynchronous tasks that are running there._


- **`Dataset` now supports asynchronous loading of data from URLs**

  The `Dataset` class has been upgraded to support asynchronous loading of
  data from URLs. This makes use of the new `HttpUrlDataset` class for
  building URLs, the new state information for failed and pending _per-item_
  tasks, and the asynchronous iteration over data files. The fetching is
  implemented in the new `get_*_from_api_endpoint` tasks (where `*` is
  `json`, `bytes`, or `str`), built on top of the asynchronous `aiohttp`
  library, and supports the following features:

  - Automatic retry of HTTP requests, building on the `aiohttp_retry`
    library. Retries are configurable to retry for particular HTTP
    response codes, to retry a specified number of times and to use a
    specified algorithm to calculate the delay between retries.
  - Rate limiting of HTTP requests, building on the `aiolimiter` library.
    Rate limiting is configurable to limit the number of requests per time
    period, and to specify the time period used for calculation,
    indirectly also controlling the burst size. Adding to what is provided
    by the `aiolimiter` library, Omnipy ensures that the maximum rate
    limit is not exceeded also for the initial burst of requests.
  - Automatic reset of rate limiter counting and delays for subsequent
    batches of requests
  - Retries and rate limiting are configured individually for each domain.
    Omnipy ensures that HTTP requests in the same batch (e.g. provided in
    the same `HttpUrlDataset`) are coordinated according to their domain.
  - The default values for retries and rate limiting are set to reasonable
    values, so that this functionality is provided seamlessly for the
    users. However, these default values can be easily be changed if
    needed.
  - `Dataset.load()` now supports lists and dicts of paths or URLs (strings
    or `HttpUrlModel` objects) as input, as well as `HttpUrlDataset`
    objects.
  - Due to the asynchronous nature of the `get_*_from_api_endpoint` tasks,
    users in an asynchronous environment such as Jupyter Notebook can
    inspect the status of the download tasks while the download is in
    progress by inspecting the `Dataset` object.


- **Other new features / bug fixes / refactorings**
  - Refactored Model and Dataset __repr__ to make use of IPython pretty
    printer. Drops support for plain Python console for automatic pretty
    prints
  - Implemented NestedSplitToItemsModel and NestedJoinItemsModel for parsing
    nested structures of any level to/from strings (e.g.
    `"param1=true&param2=42"`)
  - Implemented MatchItemsModel, which allows for filtering of items in a
    list based on a user-defined functions
  - Implemented task `create_row_index_from_column()` and basic table
    datasets
  - Added support for optional fields in `PydanticRecordModel`
  - Fixed lack of `to_data()` conversion when importing mappings and
    iterators of models to a dataset
  - Refactored models and datasets for split and join, to reduce duplication
    and allow adjustments of params for all.


## Omnipy v0.16.1

_Release date: Sep 20, 2024_

v0.16 of Omnipy is a **huge** release, with a focus on performance and
improvements on internals. It is also the first version where we will
start providing detailed release notes.

_Note, the v0.16.1 release notes includes features from the v0.16.0
release, which was yanked due to issues with Python 3.12._

### New features in v0.16

- **General speedup**  
  Performance has been a major focus of the new release. Many of the major
  new features have been implemented to allow improved efficiency. Execution
  time of all examples in the
  [omnipy_examples](https://github.com/fairtracks/omnipy_examples) repo have
  been improved; in some cases the run times has been reduced to less than
  one tenth of the previous time. There is now very little overhead added by
  Omnipy on top of pydantic, so we should expect a major speed boost once
  support for pydantic v2 is added.


- **Reimplemented model snapshots for efficiency**  
  Model snapshots now make use of a memoization dictionary through the
  Pythons builtin `deepcopy` functionality, greatly speeding up snapshots of
  hierarchical models. The snapshots and the contents of the memoization
  dictionary are automatically deleted following garbage collection,
  thoroughly tested to provide no memory leaks.


- **Lazy snapshots**  
  Models now take snapshots only when they might change the first time,
  greatly improving efficiency of models with contents that do not change.


- **Remove unneeded nested Models**  
  Some models, such as `SplitLinesToColumnsModel` have been are
  reimplemented to remove second-level Omnipy models, and instead use doubly
  nested builtin collections, e.g. `Model[list[list[str]]` instead of
  `Model[list[Model[list[str]]]]`. JSON Model containers now use simple
  types at the terminal level (e.g. 42 instead of JsonScalarM(42)). For
  cases where the nested Omnipy models are required, this is now supported
  by a new non-default option (see next feature).


- **Dynamically convert elements to models**  
  Support for dynamically generating Model objects from the elements of
  parent collection Models, e.g. to generate Model[int] objects when
  iterating through the elements of a Model[list[int]]. Turned off by
  default through `dynamically_convert_elements_to_models` config for
  efficiency.


- **Redesigned parametrised models and datasets to keep state**  
  Previous implementation of parametrised models and datasets required users
  to specify the parameter every time it was used, making in difficult to
  specify composite models that include parametrised submodels. Also, the
  implementation was complex and made it difficult to improve Omnipy with
  improved functionality for conversion and serialization. New
  implementation is based on parametrizing models and datasets as new types
  in a highly decoupled fashion. It is unfortunately slightly more complex
  to define parametrized models and datasets in the new solution due to
  innate complexities in how Python implements type annotations. Having
  tested a number of alternatives, most of whom did not work out, it is
  clear that the new solution strikes a good balance between simplicity and
  flexibility.


- **Chained models**  
  A new solution for creating `mini-workflows` by chaining two or more
  models to form a single chained model. This reduces the need to specify
  linear flows for parsing, as exemplified in the new
  [BED file parser](https://github.com/fairtracks/omnipy_examples/blob/master/src/omnipy_examples/bed.py)
  example in
  [omnipy_examples](https://github.com/fairtracks/omnipy_examples).


- **Support for streaming to models by overloading `+` operator**  
  All models supporting the `+` operator can now be streamed to from builtin
  types or other models, triggering parsing as specified in the model.
  Example: `my_table_model = TableOfPydanticRecordsModel[MyColumns](); my_table_model += [['text', 12, True]]`.
  This in principle allows for large flows to continue where they left off
  in case of network issues, or faulty data in the middle of a longer
  stream. Proper failure management is yet to be implemented, but is made
  much easier through the support of streaming to Models. Basic interactive
  operations are also much simplified with this feature, e.g. for
  concatenation of data.


- **Improved automatic conversion**
  - Mimicked operations now autoconvert the outputs, e.g.
    `Model[int](5) + 5 == Model[int](10)`.
  - Iterators and other sequence-like types such as range generators are now
    automatically recognized and converted sequence types such as `list`
    and `tuple`.
  - `PandasModel` and `PandasDataset` now support other models and datasets
    as input during initialisation.


- **Improvements of model validation**
  - Internals of validation functionality in the Model class has been
    harmonised and simplified.
  - Mimicked methods/attributes are validated also when
    interactive_mode=False
  - Pydantic models are validated before accessing attributes


- **Better handling of `None` values**  
  Pydantic v1 made some poor choices in how to handle `None` values, which
  has been very difficult to rectify within Omnipy. A previous hack to fix
  this issue has now been replaced with an improved hack which also fixed a
  number of previously "known issues" in the Omnipy tests. This refactoring
  is paving the way to a simplified move to pydantic v2, which is on the
  horizon, but postponed for now to focus on feature completion.


- **Other new features**
  - Support for Python 3.12 and Prefect 2.20
  - Better support for forward references
  - Caching of type-related function calls such as Model.outer_type(),
    further improving efficiency
  - Dataset.load() now supports lists of paths or URLs as input
  - Implementation of a SetDeque util class for speedup of various features,
    including model snapshots
  - Support default values for `TypeVar`, through `typing_extensions`
    (otherwise a Python 3.13 feature)
  - Refactoring of root log, fixing issues with a stuck timestamp when
    running flows
  - Reimplemented and fixed `__name__`, `__qualname__`, and `__repr__` for
    Model and Dataset
  - Implemented support for `__call__()`, and `__bool__()` for Models
  - Implemented `copy()` for Model and Dataset
  - Implemented flexible `__setitem__` and `__delitem__` for Dataset,
    supporting indexing by ints, slices and tuples.
  - A ton of smaller bug fixes, new tests and code cleanup. Some
    refactoring, especially of new snapshot functionality, is postponed to
    later versions.