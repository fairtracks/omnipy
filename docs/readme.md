![Omnipy logo](images/omnipy-logo-320.png)

Omnipy is a type-driven Python library for:

- data parsing, wrangling, visualization, and conversion
- tool and web service interoperability, and
- scalable dataflow orchestration

![Conceptual overview of Omnipy](images/omnipy-overview-comics-style.png)


## Why use Omnipy?

**Dataflows, Not Workflows**

Traditional workflows rely on command-line tools and intermediate files, adding complexity to data
pipelines. Omnipy replaces this with dataflows that operate directly in memory or on standard
formats like JSON or CSV. Built on [Pydantic](https://docs.pydantic.dev/) models, Omnipy enhances
data parsing, conversion, and serialization for structured data processing.

**"It's Static Typing!"… "It's Dynamic!"… "It's Omnipy!"**

Omnipy blends Python’s dynamic typing with runtime type safety. Models behave like native Python
structures while ensuring type guarantees without the rigidity of static typing. Defined in Python,
Omnipy models can be as general or specific as needed.

**Parse, Don’t Validate**

Strict validation often breaks pipelines when data is messy. Inspired by
["Parse, don't validate"](https://lexi-lambda.github.io/blog/2019/11/05/parse-don-t-validate/),
Omnipy eagerly parses input into structured models that retain integrity throughout the pipeline.
This approach aligns with the [Robustness Principle](https://devopedia.org/postel-s-law): _"be
liberal in what you accept, and conservative in what you send!"_

**Self-Constraining Data Models**

Omnipy models aren’t just one-time validators. A `Model[list[int]]()` behaves like a list but
ensures its elements are always integers. Every modification parses data to enforce integrity,
rolling back invalid operations automatically.

**Omnify Your Data Pipelines**

Omnipy invites you to ["omnify"](https://www.websters1913.com/words/Omnify) pipelines — break them
into reusable, universal components. By defining dataflows and tasks with structured input and
output models, Omnipy simplifies reuse and promotes good coding practices, improving maintainability
as projects grow.

**Catalog of Components for Interoperability**

Omnipy includes components for tasks like asynchronous API requests with rate limiting, parsing JSON
or tabular data, and flattening nested data into relational tables. Integration with REST APIs and
data wrangling/analysis tools like [Pandas](https://pandas.pydata.org/) simplifies interoperability
across diverse systems. Expect the catalog to grow as the community expands!

**Built to Scale**

Omnipy’s hierarchical `Dataset` structure simplifies batch processing of directory-based data,
including parsing, serialization, and metadata handling. With
built-in [Prefect](https://www.prefect.io/) support, Omnipy scales seamlessly from local experiments
to distributed deployment, meeting the demands of projects large and small.


## Installing Omnipy

1. Make sure that your Python version is between `3.11.4` and `3.15`, e.g.:

    ```bash
    $ python --version
    Python 3.15
    ```

2. Create and activate a virtual environment for your project, e.g.:

    ```bash
    $ python -m venv myproject
    $ source myproject/bin/activate
    ```

    > TIP:
    > - If you need help with setting up a virtual environment, check out the relevant section in
    >   the [FastAPI documentation](https://fastapi.tiangolo.com/virtual-environments/).
    >   _(Please note that Omnipy does not depend on FastAPI, it is just that their documentation is
    >   excellent!)_
    > - If you are using Omnipy in a [Jupyter notebook](https://jupyter.org/), you can most likely
    >   skip this step.

2. Install Omnipy using:
    ```bash
    $ pip install omnipy
    ```

## Getting started

To define an Omnipy data model, simply concretize the generic `Model` class by specifying a
data type in brackets, e.g. `Model[list[int]]`.

The following creates a data model of a list of integers, and parses some data into that model:

```pycon exec="1" session="greet" source="console"
>>> import omnipy as om
>>> data = (123, '234', 345.0)  # Note that the input data is a tuple of mixed types
>>> data_as_list_of_ints = om.Model[list[int]](data)
>>> data_as_list_of_ints  # The data is now parsed into a list of integers
```

```pycon exec="1" session="greet" result="console" html="true"
>>> print(data_as_list_of_ints._docs())
```

### Load some water-sample data

Let's work with river samples from the
[water-sample harmonization example](https://github.com/fairtracks/omnipy/tree/main/tests/integration/novel/full/water_sample_harmonization).
The URLs below are illustrative: the documentation serves its example JSON from a
local mock HTTP service. Substitute your own endpoint when trying this in a
Python console.

A Model can load the response from a single URL. The API returns the samples
in pages. Each response is a JSON list of sample records, so we load the first
page with `JsonListOfDictsModel`:

```pycon exec="1" session="water-samples" source="console"
>>> import omnipy as om
--8<-- "_includes/pycon_hidden_runtime_setup.md"
>>> ui_config = om.runtime.config.data.ui.browser
>>> ui_config.color.style = om.DarkHighContrastColorStyles.MEASURED_DARK_T16
>>> ui_config.color.solid_background = True
>>> from runpy import run_path  # markdown-exec: hide
>>> _fixture_path = 'docs/examples/water_sample_service.py'  # markdown-exec: hide
>>> _service = run_path(_fixture_path)['water_sample_service']()  # markdown-exec: hide

>>> water_api = 'https://water.example'
>>> water_api = _service.__enter__()  # markdown-exec: hide
>>> river_url_0 = f'{water_api}/samples?page=0'

>>> page = om.JsonListOfDictsModel.load(river_url_0)
>>> page
```

```pycon exec="1" session="water-samples" result="console" html="true"
>>> print(page._docs())
```

For a batch of responses, use a Dataset instead. Its keys name the responses;
each item is still a Model containing a list of samples. Let's load both pages
of river samples:

```pycon exec="1" session="water-samples" source="console"
>>> river_url_1 = f'{water_api}/samples?page=1'

>>> pages = om.JsonListOfDictsDataset.load(river_page_0=river_url_0, river_page_1=river_url_1)
>>> pages
```

```pycon exec="1" session="water-samples" result="console" html="true"
>>> print(pages._docs())
```

A dataset's `peek()` shows the contents of its items side by side:

```pycon
>>> pages.peek()
```

```pycon exec="1" session="water-samples" result="console" html="true"
>>> print(pages._docs(method='peek'))
```

These are synchronous console calls. In a notebook or other running event loop,
use `await` with `.load()`.

### Give a measurement a type

Models mimic their wrapped values, so we can index the loaded JSON directly.
The second measurement in the first sample is phosphorus, reported in µg/L:

```pycon exec="1" session="water-samples" source="console"
>>> raw_measurement = pages['river_page_0'][0]['measurements'][1]
>>> raw_measurement
```

```pycon exec="1" session="water-samples" result="console" html="true"
>>> print(raw_measurement._docs())
```

JSON types alone do not describe what a measurement means. A Pydantic record
gives its fields a contract, and an Omnipy Model keeps that contract active while
we work. `mimics` also makes the wrapped record's interface visible to supported editors
and type checkers; runtime field access works through the Model itself.

```python exec="1" session="water-samples" result="console" html="true"
import omnipy as om
from textwrap import dedent

code = dedent("""\
    import omnipy as om
    import omnipy.util.pydantic as pyd

    class RiverUgConcMeasurementRecord(pyd.BaseModel):
        name: str
        value_ug_l: float

    @om.mimics(RiverUgConcMeasurementRecord)
    class RiverUgConcMeasurementModel(om.Model[RiverUgConcMeasurementRecord]): ...""")

exec(code, globals(), locals())
print(
    om.StrModel(code)._docs(
        max_title_height=0,
        method='full',
        width=None,
        syntax='python',
        style=om.DarkHighContrastColorStyles.CHINOISERIE_MORANDI_T16,
    )
)
```
_Models #1: structured typing of the data as a Pydantic record, wrapped by
an Omnipy Model._

```pycon exec="1" session="water-samples" source="console"
>>> phosphorus = RiverUgConcMeasurementModel(raw_measurement)
>>> phosphorus
```

```pycon exec="1" session="water-samples" result="console" html="true"
>>> print(phosphorus._docs())
```

### Edit safely, without unpacking

Omnipy Models are self-constraining: assigning through the mimicked interface
parses the new value against its field type. An invalid concentration raises a
validation error:

```pycon
>>> phosphorus.value_ug_l = 'not a number'
```

```pycon exec="1" session="water-samples" result="console"
>>> try:
...     phosphorus.value_ug_l = 'not a number'
... except pyd.ValidationError as err:
...     print(err)
```

In interactive mode, the failed edit is rolled back to the last valid snapshot.
The measurement is still `120.0 µg/L`; we do not need to reload the response:

```pycon exec="1" session="water-samples" source="console"
>>> phosphorus
```

```pycon exec="1" session="water-samples" result="console" html="true"
>>> print(phosphorus._docs())
```

A numeric string, on the other hand, can be parsed as a float. Let's correct the
reading to `150.0 µg/L`:

```pycon exec="1" session="water-samples" source="console"
>>> phosphorus.value_ug_l = '150.0'

>>> phosphorus
```

```pycon exec="1" session="water-samples" result="console" html="true"
>>> print(phosphorus._docs())
```

### Convert to a common representation

Other sources use different field names and units. A `ConverterModel` makes a
conversion reusable and validates its output. For this concentration measurement,
let's normalize the name and convert µg/L to mg/L:

```python exec="1" session="water-samples" result="console" html="true"
import omnipy as om
from textwrap import dedent

code = dedent("""\
    import omnipy as om
    from typing import Literal

    class NormalizedConcentrationRecord(pyd.BaseModel):
        type: Literal['ammonium', 'nitrate', 'phosphorus']
        value: float
        unit: Literal['mg/L']

    @om.mimics(NormalizedConcentrationRecord)
    class MicrogramsToMilligramsMapper(
        om.ConverterModel[RiverUgConcMeasurementRecord, NormalizedConcentrationRecord]
    ):
        @classmethod
        def _convert(cls, data: RiverUgConcMeasurementRecord) -> NormalizedConcentrationRecord:
            return NormalizedConcentrationRecord(
                type=data.name.lower(),
                value=data.value_ug_l / 1000,
                unit='mg/L',
            )""")

exec(code, globals(), locals())
print(
    om.StrModel(code)._docs(
        max_title_height=0,
        method='full',
        width=None,
        syntax='python',
        style=om.DarkHighContrastColorStyles.CHINOISERIE_MORANDI_T16,
    )
)
```
_Models #2: mormalized measurement record, with a mimicking ConverterModel
to convert from the original measurement record._

```pycon exec="1" session="water-samples" source="console"
>>> normalized = MicrogramsToMilligramsMapper(phosphorus)
>>> normalized
```

```pycon exec="1" session="water-samples" result="console" html="true"
>>> print(normalized._docs())
```

The corrected reading is now `0.15 mg/L`. The same mapper can be the item type
of a Dataset, so conversion applies to each named measurement without a manual
processing loop:

```pycon exec="1" session="water-samples" source="console"
>>> concentrations = om.Dataset[MicrogramsToMilligramsMapper]({'river-r1': phosphorus})
>>> concentrations
```

```pycon exec="1" session="water-samples" result="console" html="true"
>>> print(concentrations._docs())
```

```pycon exec="1" session="water-samples" result="console"
>>> _service.__exit__(None, None, None)
```

This is a small slice of the full example. The
[integration scenario](https://github.com/fairtracks/omnipy/blob/main/tests/integration/novel/full/water_sample_harmonization/test_water_sample_harmonization.py)
extends it to paginated river and wastewater data, reusable child flows, and
Pandas tables of samples and measurements. Its
[models](https://github.com/fairtracks/omnipy/blob/main/tests/integration/novel/full/water_sample_harmonization/models.py)
also handle temperature readings and source-specific measurement names.

## Running example scripts
- Install `omnipy-examples`:
  - `pip install omnipy-examples`
- Example script:
  - `omnipy-examples isajson`
- For help on the command line interface:
  - `omnipy-examples --help`
- For help on a particular example:
  - `omnipy-examples isajson --help`

### Output of flow runs

The output will by default appear in the `data` directory, with a timestamp.

- It is recommended to install a file viewer that are capable of browsing tar.gz files.
  For instance, the "File Expander" plugin in PyCharm is excellent for this.
- To unpack the compressed files of a run on the command line
  (just make sure to replace the datetime string from this example):
  ```
  for f in $(ls data/2023_02_03-12_51_51/*.tar.gz); do mkdir ${f%.tar.gz}; tar xfzv $f -C ${f%.tar.gz}; done
  ```

### Run with the Prefect engine

Omnipy is integrated with the powerful [Prefect](https://prefect.io) dataflow orchestration library.

- To run an example using the `prefect` engine, e.g.:
  - `omnipy-examples --engine prefect isajson`
- After completion of some runs, you can check the flow logs and orchestration options in the Prefect UI:
  - `prefect server start`

More info on Prefect configuration will come soon.
