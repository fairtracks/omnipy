<!-- Generated from docs/readme.md by docs/gen_readme.py. Edit the source and regenerate. -->
![Omnipy logo](docs/images/omnipy-logo-320.png)

Omnipy is a type-driven Python library for:

- data parsing, wrangling, visualization, and conversion
- tool and web service interoperability, and
- scalable dataflow orchestration

![Conceptual overview of Omnipy](docs/images/omnipy-overview-comics-style.png)

## Why use Omnipy?

**A Readable Contract Between You and Your AI Agent**

AI agents are good at the time-consuming parts of working with data:
reformatting, cleaning, and integrating. Omnipy gives that work a
structure a human can inspect. The agent turns exploratory code into data
models, conversions, and dataflows declared in Python; the data is
validated at every step; and you review the declarations and the data at
each junction. The declarations are the contract between you and your
agent.

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

The examples below run when the documentation is built, and their output is shown here as images. The code blocks remain selectable and copyable. The [documentation site](https://omnipy.readthedocs.io/) shows the same page with selectable output too.

### Parse data into a model

To define an Omnipy data model, concretize the generic
[`Model`](https://omnipy.readthedocs.io/en/latest/reference/omnipy/data/model/#omnipy.data.model.Model) class by specifying a
data type in brackets, e.g. `Model[list[int]]`.

The following creates a data model of a list of integers, and parses some data into that model:

```pycon
>>> import omnipy as om
>>> data = (123, '234', 345.0)  # Note that the input data is a tuple of mixed types
>>> data_as_list_of_ints = om.Model[list[int]](data)
>>> data_as_list_of_ints  # The data is now parsed into a list of integers
```

![Display of data_as_list_of_ints](docs/images/readme/01-data_as_list_of_ints.svg)

### Style the displays

Omnipy's [display settings](https://omnipy.readthedocs.io/en/latest/reference/omnipy/config/data/#omnipy.config.data.UserInterfaceConfig)
configure the terminal, notebook, and browser separately. The displays below use the
dark [`MEASURED_DARK_T16`](https://omnipy.readthedocs.io/en/latest/reference/omnipy/shared/enums/colorstyles/#omnipy.shared.enums.colorstyles.DarkHighContrastColorStyles)
theme with a solid background. Use `ui.terminal` or `ui.jupyter` in place
of `ui.browser` to style your own console or notebook:

```pycon
>>> ui_config = om.runtime.config.data.ui.browser
>>> ui_config.color.style = om.DarkHighContrastColorStyles.MEASURED_DARK_T16
>>> ui_config.color.solid_background = True
```

The list of integers from above now displays in the new theme:

```pycon
>>> data_as_list_of_ints
```

![Display of data_as_list_of_ints](docs/images/readme/02-data_as_list_of_ints.svg)

### Build the URLs of a web API

Let's work with river samples from the [water-sample harmonization
example](https://github.com/fairtracks/omnipy/tree/main/tests/integration/novel/full/water_sample_harmonization).
A water quality API would return such samples in pages. Here the two pages
for this tutorial are provided JSON files in the Omnipy repository, so the
walkthrough runs as it stands from any Python console.

An [`HttpUrlModel`](https://omnipy.readthedocs.io/en/latest/reference/omnipy/components/remote/models/#omnipy.components.remote.models.HttpUrlModel)
holds a URL as structured fields, so the path is edited in place instead of by
string formatting:

```pycon
>>> data_base_url = om.HttpUrlModel('https://raw.githubusercontent.com/fairtracks/omnipy/main')
>>> data_base_url.path // 'docs' // 'examples' // 'river_samples'
>>> page_0_url = om.HttpUrlModel(data_base_url)
>>> page_0_url.path // 'page_0.json'
>>> page_0_url
```

![Display of page_0_url](docs/images/readme/03-page_0_url.svg)

A second page differs only in its file name. An
[`HttpUrlDataset`](https://omnipy.readthedocs.io/en/latest/reference/omnipy/components/remote/datasets/#omnipy.components.remote.datasets.HttpUrlDataset)
collects the URLs under names that will also name the responses:

```pycon
>>> page_1_url = om.HttpUrlModel(data_base_url)
>>> page_1_url.path // 'page_1.json'
>>> page_urls = om.HttpUrlDataset(page_0=page_0_url, page_1=page_1_url)
>>> page_urls
```

![Display of page_urls](docs/images/readme/04-page_urls.svg)

Such Datasets are also built by the catalog:
[`GeneratePagedUrlsModel`](https://omnipy.readthedocs.io/en/latest/reference/omnipy/components/remote/models/#omnipy.components.remote.models.GeneratePagedUrlsModel)
from a page or item count for APIs with many pages, and the
[`get_github_repo_urls`](https://omnipy.readthedocs.io/en/latest/reference/omnipy/components/remote/tasks/#omnipy.components.remote.tasks.get_github_repo_urls)
task from a directory listing on GitHub.

### Load the pages

A Dataset's [`load()`](https://omnipy.readthedocs.io/en/latest/reference/omnipy/data/dataset/#omnipy.data.dataset.Dataset.load) fetches
all its URLs, keeping the responses under the URL names. A
[`JsonDataset`](https://omnipy.readthedocs.io/en/latest/reference/omnipy/components/json/datasets/#omnipy.components.json.datasets.JsonDataset) parses
the responses as JSON, including when the server sends them as plain text, as GitHub does here:

```pycon
>>> pages = om.JsonDataset.load(page_urls)
>>> pages
```

![Display of pages](docs/images/readme/05-pages.svg)

A Dataset's [`peek()`](https://omnipy.readthedocs.io/en/latest/reference/omnipy/data/dataset/#omnipy.data.dataset.Dataset.peek)
shows the contents of its items side by side:

```pycon
>>> pages.peek()
```

![Display of pages](docs/images/readme/06-pages.svg)

These are synchronous console calls. In a notebook or other running event loop,
use `await` with `.load()`.

### Give one measurement a type

Models mimic their wrapped values, so we can index the loaded JSON directly.
The second measurement in the first sample is phosphorus, reported in µg/L:

```pycon
>>> raw_measurement = pages['page_0'][0]['measurements'][1]
>>> raw_measurement
```

![Display of raw_measurement](docs/images/readme/07-raw_measurement.svg)

JSON types alone do not describe what a measurement means. Start with one
[Pydantic record](https://omnipy.readthedocs.io/en/latest/howto/models/pydantic-compatibility/) for
a concentration in µg/L, wrapped in an Omnipy Model to keep its field types active during edits.
[`mimics`](https://omnipy.readthedocs.io/en/latest/reference/omnipy/data/typing/helpers/#omnipy.data.typing.helpers.mimics) exposes the
record's fields to editors and type checkers; the Model supplies field access at runtime.

```python
import omnipy.util.pydantic as pyd

class RiverUgConcMeasurementRecord(pyd.BaseModel):
    name: str
    value_ug_l: float

@om.mimics(RiverUgConcMeasurementRecord)
class RiverUgConcMeasurementModel(om.Model[RiverUgConcMeasurementRecord]): ...
```

Constructing the Model parses the JSON measurement into the record:

```pycon
>>> measurement = RiverUgConcMeasurementModel(raw_measurement)
>>> measurement
```

![Display of measurement](docs/images/readme/08-measurement.svg)

### Give the samples a type

The full sample includes temperature in °C and concentrations in mg/L or µg/L. A union of records
tells these shapes apart by their fields. The sample record combines them with a station and a
[`DateModel`](https://omnipy.readthedocs.io/en/latest/reference/omnipy/components/raw/models/#omnipy.components.raw.models.DateModel).
The catalog's
[`MergeListsOfRecordsIntoDatasetByPrimaryKeyModel`](https://omnipy.readthedocs.io/en/latest/reference/omnipy/components/general/models/#omnipy.components.general.models.MergeListsOfRecordsIntoDatasetByPrimaryKeyModel)
merges the pages and keys the samples by their
[`PrimaryKey`](https://omnipy.readthedocs.io/en/latest/reference/omnipy/data/primary_key/#omnipy.data.primary_key.PrimaryKey), rejecting
duplicates. Its contents are a Dataset, so we name the specialization `RiverSamplesDataset`.

```python
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
): ...
```

Constructing the Dataset from the loaded pages parses them into typed samples:

```pycon
>>> samples = RiverSamplesDataset(pages)
```

```pycon
>>> samples.peek()
```

![Display of samples](docs/images/readme/09-samples.svg)

[`json()`](https://omnipy.readthedocs.io/en/latest/reference/omnipy/data/dataset/#omnipy.data.dataset.Dataset.json) displays the data
with JSON syntax highlighting. The display methods also take a color style of their own:

```pycon
>>> samples.json(style='gotham-t16')
```

![Display of samples](docs/images/readme/10-samples.svg)

### Work with the Dataset

A [`Dataset`](https://omnipy.readthedocs.io/en/latest/reference/omnipy/data/dataset/#omnipy.data.dataset.Dataset) supports names and
integer positions. The third sample can be accessed by its name, and its station read through
the Model:

```pycon
>>> samples['river-sample-3'].station
'Upstream Bend'
```

Integer indexing starts at zero, so `samples[2]` selects the same sample:

```pycon
>>> samples[2].station
'Upstream Bend'
```

A list of keys selects several items and returns a Dataset:

```pycon
>>> samples[['river-sample-1', 'river-sample-2']].peek()
```

![Display of samples[['river-sample-1', 'river-sample-2']]](docs/images/readme/11-samples-river-sample-1-river-sample-2.svg)

A slice selects by position. Here it returns the same two items:

```pycon
>>> samples[:2]
```

![Display of samples[:2]](docs/images/readme/12-samples-2.svg)

### Edit safely, without unpacking

Omnipy Models are self-constraining: assigning through the mimicked interface
parses the new value against its field type. An invalid concentration raises a
validation error:

```pycon
>>> phosphorus = samples['river-sample-1'].measurements[1]
>>> phosphorus
```

![Display of phosphorus](docs/images/readme/13-phosphorus.svg)

```pycon
>>> phosphorus.value_ug_l = 'not a number'
ValidationError: 2 validation errors for Model[RiverUgConcMeasurementRecord]
__root__ -> value_ug_l
  value is not a valid float (type=type_error.float)
__root__
   (type=assertion_error)
```

In [interactive mode](https://omnipy.readthedocs.io/en/latest/feature/continuous-validation/), the failed edit is rolled back to the
last valid snapshot. Displaying the measurement again shows the original `120.0 µg/L`:

```pycon
>>> phosphorus
```

![Display of phosphorus](docs/images/readme/14-phosphorus.svg)

A numeric string can be parsed as a float. Let's correct the
reading to `150.0 µg/L`. The measurement is part of the sample, so the correction
is visible there too:

```pycon
>>> phosphorus.value_ug_l = '150.0'
>>> samples['river-sample-1'].measurements[1]
```

![Display of samples['river-sample-1'].measurements[1]](docs/images/readme/15-samples-river-sample-1-measurements-1.svg)

### Convert to a common representation

Other sources use different field names and units. A
[`ConverterModel`](https://omnipy.readthedocs.io/en/latest/reference/omnipy/components/general/models/#omnipy.components.general.models.ConverterModel)
makes a conversion reusable and validates its output. First, a measurement mapper uses the record
type to choose the conversion, including µg/L to mg/L:

```python
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
                )
```

Constructing the mapper converts the corrected measurement to `0.15 mg/L`:

```pycon
>>> normalized = NormalizedRiverMeasurementMapper(phosphorus)
>>> normalized
```

![Display of normalized](docs/images/readme/16-normalized.svg)

Next, a sample mapper renames the sample fields and reuses the measurement mapper's
[`convert_all()`](https://omnipy.readthedocs.io/en/latest/reference/omnipy/components/general/models/#omnipy.components.general.models.ConverterModel.convert_all)
for its measurements. A Dataset of that mapper converts all the samples:

```python
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

class NormalizedRiverSamplesDataset(om.Dataset[NormalizedRiverSampleMapper]): ...
```

The Dataset constructor applies the mapper to every sample, keeping the sample ids as keys.
`peek()` displays the converted samples side by side:

```pycon
>>> normalized_samples = NormalizedRiverSamplesDataset(samples)
```

```pycon
>>> normalized_samples.json()
```

![Display of normalized_samples](docs/images/readme/17-normalized_samples.svg)

For a one-line conversion and display,
[`to()`](https://omnipy.readthedocs.io/en/latest/reference/omnipy/data/model/#omnipy.data.model.Model.to) is convenient too:

```pycon
>>> samples[0].to(NormalizedRiverSampleMapper).json()
```

![Display of samples[0].to(NormalizedRiverSampleMapper)](docs/images/readme/18-samples-0-to-NormalizedRiverSampleMapper.svg)

### Explore the hierarchy as nested Datasets

[`StructuredNestedDataset`](https://omnipy.readthedocs.io/en/latest/reference/omnipy/components/nested/datasets/#omnipy.components.nested.datasets.StructuredNestedDataset)
represents mappings recursively as Datasets and recognizes the structure of the leaves: scalar
fields become
[`JsonScalarModel`](https://omnipy.readthedocs.io/en/latest/reference/omnipy/components/json/models/#omnipy.components.json.models.JsonScalarModel)
items, and each measurement list, a list of records with the same fields, becomes a column-wise
table Model. The conversion preserves the sample ids and field names, while making the samples
nested Datasets with their fields as items:

```pycon
>>> nested_samples = om.StructuredNestedDataset(normalized_samples)
>>> nested_samples
```

![Display of nested_samples](docs/images/readme/19-nested_samples.svg)

Calling `peek()` on a StructuredNestedDataset shows a hierarchical view of the structure, with
tables nested within tables:

```pycon
>>> nested_samples[0].peek()
```

![Display of nested_samples[0]](docs/images/readme/20-nested_samples-0.svg)

### Turn the measurements into tables

The measurement tables have `type`, `value`, and `unit` columns.
[`do()`](https://omnipy.readthedocs.io/en/latest/reference/omnipy/data/dataset/#omnipy.data.dataset.Dataset.do) applies a
placeholder expression to each item, here selecting the measurements from each sample, keeping
the sample ids as keys. A
[`PandasDataset`](https://omnipy.readthedocs.io/en/latest/reference/omnipy/components/pandas/datasets/#omnipy.components.pandas.datasets.PandasDataset)
then converts each measurement table to a pandas DataFrame:

```pycon
>>> measurements = nested_samples.do(om.x['measurements'])
>>> tables = om.PandasDataset(measurements)
```

```pycon
>>> tables.peek(width=132)
```

![Display of tables](docs/images/readme/21-tables.svg)

### Compose tasks and flows

The steps so far form a dataflow: fetch the pages, key the samples, normalize them, expose the
hierarchy, select measurements, and tabulate. A
[`TaskTemplate`](https://omnipy.readthedocs.io/en/latest/reference/omnipy/compute/task/#omnipy.compute.task.TaskTemplate) wraps a function;
a [`LinearFlowTemplate`](https://omnipy.readthedocs.io/en/latest/reference/omnipy/compute/flow/#omnipy.compute.flow.LinearFlowTemplate)
declares its stages in order. Model and Dataset constructors can be stages directly.
[`resolve()`](https://omnipy.readthedocs.io/en/latest/reference/omnipy/util/helpers/#omnipy.util.helpers.resolve) handles the loader's
result whether it is already available or still awaiting completion:

```python
@om.TaskTemplate()
async def fetch_sample_pages(page_urls: om.HttpUrlDataset) -> om.JsonDataset:
    return await om.resolve(om.JsonDataset.load(page_urls))

@om.TaskTemplate()
def select_measurements(samples: om.StructuredNestedDataset) -> om.StructuredNestedDataset:
    return samples.do(om.x['measurements'])

@om.LinearFlowTemplate(
    fetch_sample_pages,
    RiverSamplesDataset,
    NormalizedRiverSamplesDataset,
    om.StructuredNestedDataset,
    select_measurements,
    om.PandasDataset,
)
async def harmonize_river_samples(page_urls: om.HttpUrlDataset) -> om.PandasDataset: ...
```

The flow reloads the original pages, so its phosphorus reading starts at `0.12 mg/L`.
The manual correction above belongs to the earlier in-memory Dataset:

```pycon
>>> tables = harmonize_river_samples.run(page_urls)
```

```pycon
>>> tables.peek(width=132)
```

![Display of tables](docs/images/readme/22-tables.svg)

The flow declaration is what a reviewer reads, and what an AI agent working on the pipeline
produces and is held to: the stages, their order, and the types passing between them, with every
Model and Dataset validating its data at its stage. The same flow runs on
[Prefect](https://www.prefect.io/) by setting `om.runtime.config.engine.choice = 'prefect'`;
see [Tutorial 8: Prefect orchestration](https://omnipy.readthedocs.io/en/latest/tutorials/08-prefect-orchestration/).

## Where next

- Meet the [comics roster](https://omnipy.readthedocs.io/en/latest/comics/): the Omnificients and the Un-FAIR Alliance turn
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
- [Tutorial 8: Prefect orchestration](https://omnipy.readthedocs.io/en/latest/tutorials/08-prefect-orchestration/) runs a flow on the
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
