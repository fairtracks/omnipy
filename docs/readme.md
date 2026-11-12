![Omnipy logo](images/omnipy-logo-320.png)

Omnipy is a type-driven Python library for:

- data parsing, wrangling, visualization, and conversion
- tool and web service interoperability, and
- scalable dataflow orchestration

![Conceptual overview of Omnipy](images/omnipy-overview-comics-style.png)


## Why use Omnipy?

**A Readable Contract Between You and Your AI Agent**

AI agents are good at the time-consuming parts of working with research data: reformatting,
cleaning, and integrating. Omnipy gives that work a structure a human can inspect. The agent turns
exploratory code into data models, conversions, and dataflows declared in Python; the data is
validated at every step; and you review the declarations and the data at each junction rather than
the agent's code paths. The declarations are the contract between you and your agent.

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
as projects grow. Small, typed, reviewable components are also what an agent should produce.

**Catalog of Components for Interoperability**

Omnipy includes components for tasks like asynchronous API requests with rate limiting and retries,
posting JSON to web services, building paged URLs, keying Datasets by the primary keys of their
records, parsing JSON or tabular data, and flattening nested data into relational tables.
Integration with REST APIs and data wrangling/analysis tools like
[Pandas](https://pandas.pydata.org/) simplifies interoperability across diverse systems. Expect the
catalog to grow as the community expands!

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

3. Install Omnipy using:
    ```bash
    $ pip install omnipy
    ```

4. If you work with a coding agent, install the Omnipy skills into your project, running in the
   project directory:
    ```bash
    $ python -m omnipy.skills install
    ```

    This links the skills shipped with Omnipy into `.agents/skills/`, where most agents read them,
    so that they follow Omnipy through upgrades. Add `--claude` for Claude Code, which reads
    `.claude/skills/`, and see `python -m omnipy.skills --help` for listing the skills and other
    options.

Omnipy works with both Pydantic 1 and 2. With Pydantic 2 installed, it runs through Pydantic's v1
compatibility layer; Pydantic 2 models are not supported yet.

## Getting started

### Parse data into a model

To define an Omnipy data model, concretize the generic
[`Model`](reference/omnipy/data/model.md#omnipy.data.model.Model) class by specifying a
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

### Style the displays

Omnipy's [display settings](reference/omnipy/config/data.md#omnipy.config.data.UserInterfaceConfig)
configure the terminal, notebook, and browser separately. The displays below use the browser's
dark [`MEASURED_DARK_T16`](reference/omnipy/shared/enums/colorstyles.md#omnipy.shared.enums.colorstyles.DarkHighContrastColorStyles)
theme with a solid background. Use `ui.terminal` or `ui.jupyter` in place
of `ui.browser` to style your own console or notebook:

```pycon exec="1" session="water-samples" source="console"
>>> import omnipy as om
--8<-- "_includes/pycon_hidden_runtime_setup.md"
>>> ui_config = om.runtime.config.data.ui.browser
>>> ui_config.color.style = om.DarkHighContrastColorStyles.MEASURED_DARK_T16
>>> ui_config.color.solid_background = True
```

### Build the URLs of a web API

Let's work with river samples from the
[water-sample harmonization example](https://github.com/fairtracks/omnipy/tree/main/tests/integration/novel/full/water_sample_harmonization).
A water quality API would return such samples in pages. Here the two pages are JSON files in the
Omnipy repository, so the walkthrough runs as it stands from any Python console.

An [`HttpUrlModel`](reference/omnipy/components/remote/models.md#omnipy.components.remote.models.HttpUrlModel)
holds a URL as structured fields, so the path is edited in place instead of by
string formatting:

```pycon exec="1" session="water-samples" source="console"
>>> river_data = om.HttpUrlModel('https://raw.githubusercontent.com/fairtracks/omnipy/main')
>>> river_data.path // 'docs' // 'examples' // 'river_samples'

>>> river_page_0 = om.HttpUrlModel(river_data)
>>> river_page_0.path // 'page_0.json'
>>> river_page_0
```

```pycon exec="1" session="water-samples" result="console" html="true"
>>> print(river_page_0._docs())
```

A second page differs only in its file name. An
[`HttpUrlDataset`](reference/omnipy/components/remote/datasets.md#omnipy.components.remote.datasets.HttpUrlDataset)
collects the URLs under names that will also name the responses:

```pycon exec="1" session="water-samples" source="console"
>>> river_page_1 = om.HttpUrlModel(river_data)
>>> river_page_1.path // 'page_1.json'

>>> page_urls = om.HttpUrlDataset(river_page_0=river_page_0, river_page_1=river_page_1)
>>> page_urls
```

```pycon exec="1" session="water-samples" result="console" html="true"
>>> print(page_urls._docs())
```

Such Datasets are also built by the catalog:
[`GeneratePagedUrlsModel`](reference/omnipy/components/remote/models.md#omnipy.components.remote.models.GeneratePagedUrlsModel)
from a page or item count for APIs with many pages, and the
[`get_github_repo_urls`](reference/omnipy/components/remote/tasks.md#omnipy.components.remote.tasks.get_github_repo_urls)
task from a directory listing on GitHub.

### Load the pages

A Dataset's [`load()`](reference/omnipy/data/dataset.md#omnipy.data.dataset.Dataset.load) fetches
all its URLs, keeping the responses under the URL names. A
[`JsonDataset`](reference/omnipy/components/json/datasets.md#omnipy.components.json.datasets.JsonDataset) parses
the responses as JSON, including when the server sends them as plain text, as GitHub does here:

```pycon exec="1" session="water-samples" source="console"
>>> pages = om.JsonDataset.load(page_urls)
>>> pages
```

```pycon exec="1" session="water-samples" result="console" html="true"
>>> print(pages._docs())
```

A Dataset's [`peek()`](reference/omnipy/data/dataset.md#omnipy.data.dataset.Dataset.peek)
shows the contents of its items side by side:

```pycon
>>> pages.peek()
```

```pycon exec="1" session="water-samples" result="console" html="true"
>>> print(pages._docs(method='peek'))
```

These are synchronous console calls. In a notebook or other running event loop,
use `await` with `.load()`.

### Give one measurement a type

Models mimic their wrapped values, so we can index the loaded JSON directly.
The second measurement in the first sample is phosphorus, reported in µg/L:

```pycon exec="1" session="water-samples" source="console"
>>> raw_measurement = pages['river_page_0'][0]['measurements'][1]
>>> raw_measurement
```

```pycon exec="1" session="water-samples" result="console" html="true"
>>> print(raw_measurement._docs())
```

JSON types alone do not describe what a measurement means. Start with one
[Pydantic record](howto/models/pydantic-compatibility.md) for
a concentration in µg/L, wrapped in an Omnipy Model to keep its field types active during edits.
[`mimics`](reference/omnipy/data/typing/helpers.md#omnipy.data.typing.helpers.mimics) exposes the
record's fields to editors and type checkers; the Model supplies field access at runtime.

```python exec="1" session="water-samples" result="console" html="true"
import omnipy as om
from textwrap import dedent

code = dedent("""\
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

Constructing the Model parses the JSON measurement into the record:

```pycon exec="1" session="water-samples" source="console"
>>> measurement = RiverUgConcMeasurementModel(raw_measurement)
>>> measurement
```

```pycon exec="1" session="water-samples" result="console" html="true"
>>> print(measurement._docs())
```

### Give the samples a type

The full sample includes temperature in °C and concentrations in mg/L or µg/L. A union of records
tells these shapes apart by their fields. The sample record combines them with a station and a
[`DateModel`](reference/omnipy/components/raw/models.md#omnipy.components.raw.models.DateModel).
The catalog's
[`MergeListsOfRecordsIntoDatasetByPrimaryKeyModel`](reference/omnipy/components/general/models.md#omnipy.components.general.models.MergeListsOfRecordsIntoDatasetByPrimaryKeyModel)
merges the pages and keys the samples by their
[`PrimaryKey`](reference/omnipy/data/primary_key.md#omnipy.data.primary_key.PrimaryKey), rejecting
duplicates. Its contents are a Dataset, so we name the specialization `RiverSamplesDataset`.

```python exec="1" session="water-samples" result="console" html="true"
import omnipy as om
from textwrap import dedent

code = dedent("""\
    from typing import Literal

    class RiverTempMeasurementRecord(pyd.BaseModel):
        name: str
        value_celsius: float

    class RiverMgConcMeasurementRecord(pyd.BaseModel):
        name: str
        value_mg_l: float

    RiverMeasurementRecordType = (
        RiverTempMeasurementRecord | RiverMgConcMeasurementRecord | RiverUgConcMeasurementRecord
    )

    class RiverSampleRecord(pyd.BaseModel):
        river_sample_id: str
        catchment: str
        sampled_at: om.DateModel
        station: str
        sample_alias: str
        measurements: list[RiverMeasurementRecordType]

    @om.mimics(om.Dataset[om.Model[RiverSampleRecord]])
    class RiverSamplesDataset(
        om.MergeListsOfRecordsIntoDatasetByPrimaryKeyModel[
            om.PrimaryKey[Literal['river_sample_id']], RiverSampleRecord
        ]
    ): ...""")

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

Constructing the Dataset from the loaded pages parses them into typed samples:

```pycon exec="1" session="water-samples" source="console"
>>> samples = RiverSamplesDataset(pages)
>>> samples
```

```pycon exec="1" session="water-samples" result="console" html="true"
>>> print(samples._docs())
```

For larger records, [`json()`](reference/omnipy/data/model.md#omnipy.data.model.Model.json)
displays the data with JSON syntax highlighting:

```pycon
>>> samples['river-sample-1'].json()
```

```pycon exec="1" session="water-samples" result="console" html="true"
>>> print(samples['river-sample-1']._docs(method='json'))
```

### Work with the Dataset

A [`Dataset`](reference/omnipy/data/dataset.md#omnipy.data.dataset.Dataset) supports names and
integer positions. The third sample can be accessed by its name, and its station read through
the Model:

```pycon
>>> samples['river-sample-3'].station
```

```pycon exec="1" session="water-samples" result="console"
>>> print(repr(samples['river-sample-3'].station))
```

Integer indexing starts at zero, so `samples[2]` selects the same sample:

```pycon
>>> samples[2].station
```

```pycon exec="1" session="water-samples" result="console"
>>> print(repr(samples[2].station))
```

A list of keys selects several items and returns a Dataset:

```pycon
>>> samples[['river-sample-1', 'river-sample-2']].peek()
```

```pycon exec="1" session="water-samples" result="console" html="true"
>>> print(samples[['river-sample-1', 'river-sample-2']]._docs(method='peek'))
```

A slice selects by position. Here it returns the same two items:

```pycon exec="1" session="water-samples" source="console"
>>> samples[:2]
```

```pycon exec="1" session="water-samples" result="console" html="true"
>>> print(samples[:2]._docs())
```

### Edit safely, without unpacking

Omnipy Models are self-constraining: assigning through the mimicked interface
parses the new value against its field type. An invalid concentration raises a
validation error:

```pycon exec="1" session="water-samples" source="console"
>>> phosphorus = samples['river-sample-1'].measurements[1]
>>> phosphorus
```

```pycon exec="1" session="water-samples" result="console" html="true"
>>> print(phosphorus._docs())
```

```pycon
>>> phosphorus.value_ug_l = 'not a number'
```

```pycon exec="1" session="water-samples"
>>> with catch_and_format_error():
...     phosphorus.value_ug_l = 'not a number'
```

In [interactive mode](feature/continuous-validation.md), the failed edit is rolled back to the
last valid snapshot. Displaying the measurement again shows the original `120.0 µg/L`:

```pycon exec="1" session="water-samples" source="console"
>>> phosphorus
```

```pycon exec="1" session="water-samples" result="console" html="true"
>>> print(phosphorus._docs())
```

A numeric string can be parsed as a float. Let's correct the
reading to `150.0 µg/L`. The measurement is part of the sample, so the correction
is visible there too:

```pycon exec="1" session="water-samples" source="console"
>>> phosphorus.value_ug_l = '150.0'

>>> samples['river-sample-1'].measurements[1]
```

```pycon exec="1" session="water-samples" result="console" html="true"
>>> print(samples['river-sample-1'].measurements[1]._docs())
```

### Convert to a common representation

Other sources use different field names and units. A
[`ConverterModel`](reference/omnipy/components/general/models.md#omnipy.components.general.models.ConverterModel)
makes a conversion reusable and validates its output. First, a measurement mapper uses the record
type to choose the conversion, including µg/L to mg/L:

```python exec="1" session="water-samples" result="console" html="true"
import omnipy as om
from textwrap import dedent

code = dedent("""\
    class NormalizedMeasurementRecord(pyd.BaseModel):
        type: Literal['nitrate', 'phosphorus', 'temperature']
        value: float
        unit: Literal['mg/L', 'deg_C']

    @om.mimics(NormalizedMeasurementRecord)
    class NormalizedRiverMeasurementMapper(
        om.ConverterModel[RiverMeasurementRecordType, NormalizedMeasurementRecord]
    ):
        @classmethod
        def _convert(cls, data: RiverMeasurementRecordType) -> NormalizedMeasurementRecord:
            match data:
                case RiverTempMeasurementRecord():
                    return NormalizedMeasurementRecord(
                        type=data.name.lower(), value=data.value_celsius, unit='deg_C'
                    )
                case RiverMgConcMeasurementRecord():
                    return NormalizedMeasurementRecord(
                        type=data.name.lower(), value=data.value_mg_l, unit='mg/L'
                    )
                case RiverUgConcMeasurementRecord():
                    return NormalizedMeasurementRecord(
                        type=data.name.lower(), value=data.value_ug_l / 1000, unit='mg/L'
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

Constructing the mapper converts the corrected measurement to `0.15 mg/L`:

```pycon exec="1" session="water-samples" source="console"
>>> normalized = NormalizedRiverMeasurementMapper(phosphorus)
>>> normalized
```

```pycon exec="1" session="water-samples" result="console" html="true"
>>> print(normalized._docs())
```

Next, a sample mapper renames the sample fields and reuses the measurement mapper's
[`convert_all()`](reference/omnipy/components/general/models.md#omnipy.components.general.models.ConverterModel.convert_all)
for its measurements. A Dataset of that mapper converts all the samples:

```python exec="1" session="water-samples" result="console" html="true"
import omnipy as om
from textwrap import dedent

code = dedent("""\
    class NormalizedSampleRecord(pyd.BaseModel):
        sample_key: str
        monitoring_date: om.DateModel
        location_name: str
        measurements: list[NormalizedMeasurementRecord]

    @om.mimics(NormalizedSampleRecord)
    class NormalizedRiverSampleMapper(
        om.ConverterModel[RiverSampleRecord, NormalizedSampleRecord]
    ):
        @classmethod
        def _convert(cls, data: RiverSampleRecord) -> NormalizedSampleRecord:
            return NormalizedSampleRecord(
                sample_key=data.sample_alias.lower(),
                monitoring_date=data.sampled_at,
                location_name=data.station,
                measurements=list(
                    NormalizedRiverMeasurementMapper.convert_all(data.measurements)
                ),
            )

    class NormalizedRiverSamplesDataset(om.Dataset[NormalizedRiverSampleMapper]): ...""")

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

The Dataset constructor applies the mapper to every sample, keeping the sample ids as keys.
`peek()` displays the converted samples side by side:

```pycon exec="1" session="water-samples" source="console"
>>> normalized_samples = NormalizedRiverSamplesDataset(samples)
```

```pycon
>>> normalized_samples.peek()
```

```pycon exec="1" session="water-samples" result="console" html="true"
>>> print(normalized_samples._docs(method='peek'))
```

For a one-line conversion and display,
[`to()`](reference/omnipy/data/model.md#omnipy.data.model.Model.to) is convenient too:

```pycon
>>> samples[0].to(NormalizedRiverSampleMapper).json()
```

```pycon exec="1" session="water-samples" result="console" html="true"
>>> print(samples[0].to(NormalizedRiverSampleMapper)._docs(method='json'))
```

### Explore the hierarchy as nested Datasets

[`NestedDataset`](reference/omnipy/components/nested/datasets.md#omnipy.components.nested.datasets.NestedDataset)
represents mappings recursively as Datasets, with a chosen Model type for the leaves. Here
[`JsonModel`](reference/omnipy/components/json/models.md#omnipy.components.json.models.JsonModel)
holds scalar fields and measurement lists. The conversion preserves the sample ids and field
names, while making the sample's fields selectable as Dataset items:

```pycon exec="1" session="water-samples" source="console"
>>> nested_samples = om.NestedDataset[om.JsonModel](normalized_samples)
>>> nested_samples[0]
```

```pycon exec="1" session="water-samples" result="console" html="true"
>>> print(nested_samples[0]._docs())
```

```pycon
>>> nested_samples[0]['measurements'].json()
```

```pycon exec="1" session="water-samples" result="console" html="true"
>>> print(nested_samples[0]['measurements']._docs(method='json'))
```

### Turn the measurements into tables

Each measurement has the same `type`, `value`, and `unit` fields, so those records make natural
table rows. [`do()`](reference/omnipy/data/dataset.md#omnipy.data.dataset.Dataset.do) selects the
measurements from each sample, keeping the sample ids as keys. A
[`PandasDataset`](reference/omnipy/components/pandas/datasets.md#omnipy.components.pandas.datasets.PandasDataset)
then converts each measurement list to a table:

```pycon exec="1" session="water-samples" source="console"
>>> measurements = nested_samples.do(lambda sample: sample['measurements'])
>>> tables = om.PandasDataset(measurements)
```

```pycon
>>> tables.peek(width=132)
```

```pycon exec="1" session="water-samples" result="console" html="true"
>>> print(tables._docs(method='peek', width=132))
```

### Compose tasks and flows

The steps so far form a dataflow: fetch the pages, key the samples, normalize them, expose the
hierarchy, select measurements, and tabulate. A
[`TaskTemplate`](reference/omnipy/compute/task.md#omnipy.compute.task.TaskTemplate) wraps a function;
a [`LinearFlowTemplate`](reference/omnipy/compute/flow.md#omnipy.compute.flow.LinearFlowTemplate)
declares its stages in order. Model and Dataset constructors can be stages directly.
[`resolve()`](reference/omnipy/util/helpers.md#omnipy.util.helpers.resolve) handles the loader's
result whether it is already available or still awaiting completion:

```python exec="1" session="water-samples" result="console" html="true"
import omnipy as om
from textwrap import dedent

code = dedent("""\
    @om.TaskTemplate()
    async def fetch_sample_pages(page_urls: om.HttpUrlDataset) -> om.JsonDataset:
        return await om.resolve(om.JsonDataset.load(page_urls))

    @om.TaskTemplate()
    def select_measurements(
        samples: om.NestedDataset[om.JsonModel],
    ) -> om.NestedDataset[om.JsonModel]:
        return samples.do(lambda sample: sample['measurements'])

    @om.LinearFlowTemplate(
        fetch_sample_pages,
        RiverSamplesDataset,
        NormalizedRiverSamplesDataset,
        om.NestedDataset[om.JsonModel],
        select_measurements,
        om.PandasDataset,
    )
    async def harmonize_river_samples(page_urls: om.HttpUrlDataset) -> om.PandasDataset: ...""")

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

The flow reloads the original pages, so its phosphorus reading starts at `0.12 mg/L`.
The manual correction above belongs to the earlier in-memory Dataset:

```pycon exec="1" session="water-samples" source="console"
>>> tables = harmonize_river_samples.run(page_urls)
```

```pycon
>>> tables.peek(width=132)
```

```pycon exec="1" session="water-samples" result="console" html="true"
>>> print(tables._docs(method='peek', width=132))
```

The flow declaration is what a reviewer reads, and what an AI agent working on the pipeline
produces and is held to: the stages, their order, and the types passing between them, with every
Model and Dataset validating its data at its stage. The same flow runs on
[Prefect](https://www.prefect.io/) by setting `om.runtime.config.engine.choice = 'prefect'`;
see [Tutorial 8: Prefect orchestration](tutorials/08-prefect-orchestration.md).

## Where next

- Meet the [comics roster](comics/index.md): the Omnificients and the Un-FAIR Alliance turn
  parsing, validation, batch processing, API retrieval, and visualization into stories.
- The full
  [water-sample harmonization scenario](https://github.com/fairtracks/omnipy/blob/main/tests/integration/novel/full/water_sample_harmonization/test_water_sample_harmonization.py)
  extends this walkthrough to river and wastewater sources, reusable child flows, and Pandas tables
  of samples and measurements.
- The
  [sequence data brokering scenario](https://github.com/fairtracks/omnipy/tree/main/tests/integration/novel/full/sequence_data_brokering)
  shows a larger dataflow: a typed submission with Datasets of samples and files, mapped requests
  posted to mock web services, derived status, and DAG child flows. A tutorial based on it is in
  preparation.
- Jupyter notebooks with real-world Omnipy code:
  [ihec_encode](https://github.com/fairtracks/omnipy/blob/main/docs/notebooks/ihec_encode.ipynb),
  [isa_json_data_wrangling_example](https://github.com/fairtracks/omnipy/blob/main/docs/notebooks/isa_json_data_wrangling_example.ipynb),
  and [nobel_idw2025](https://github.com/fairtracks/omnipy/blob/main/docs/notebooks/nobel_idw2025.ipynb).
- [Tutorial 8: Prefect orchestration](tutorials/08-prefect-orchestration.md) runs a flow on the
  Prefect engine.
- The [Omnipy skills](https://github.com/fairtracks/omnipy/tree/main/.agents/skills) are what a
  coding agent reads to work with Omnipy. The first,
  [omnipy-dataflows](https://github.com/fairtracks/omnipy/blob/main/.agents/skills/omnipy-dataflows/SKILL.md),
  covers designing dataflows: typed contracts first, reusable tasks and flows, and narrative tests
  that double as tutorials. The skills ship with Omnipy, see step 4 of
  [Installing Omnipy](#installing-omnipy) above.
- The workshop
  [Structure your AI-powered research data pipelines with Omnipy](https://www.ub.uio.no/english/courses-events/courses/dsdays/2027/structure-your-ai-powered-research-data-pipelines-wi.html)
  at Digital Scholarship Days 2027, University of Oslo, is where this direction is taken further.
- The [omnipy-examples](https://pypi.org/project/omnipy-examples/) package has stand-alone
  example scripts (`pip install omnipy-examples`, then `omnipy-examples --help`). It is updated
  separately and may lag behind the Omnipy release.
