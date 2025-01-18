![Omnipy logo](images/omnipy-logo-320.png)

Omnipy is a type-driven Python library for:

- data conversion, parsing and wrangling
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

## Generic functionality

_(NOTE: Read the
section [Transformation on the FAIRtracks.net website](https://fairtracks.net/fair/#fair-07-transformation)
for a more detailed and better formatted version of the following description!)_

Omnipy is designed primarily to simplify development and deployment of (meta)data transformation
processes in the context of FAIRification and data brokering efforts. However, the functionality is
very generic and can also be used to support research data (and metadata) transformations in a range
of fields and contexts beyond life science, including day-to-day research scenarios:

## Data wrangling in day-to-day research

Researchers in life science and other data-centric fields often need to extract, manipulate and
integrate data and/or metadata from different sources, such as repositories, databases or flat
files. Much research time is spent on trivial and not-so-trivial details of
such ["data wrangling"](https://en.wikipedia.org/wiki/Data_wrangling):

- reformat data structures
- clean up errors
- remove duplicate data
- map and integrate dataset fields
- etc.

General software for data wrangling and analysis, such as [Pandas](https://pandas.pydata.org/),
[R](https://www.r-project.org/) or [Frictionless](https://frictionlessdata.io/), are useful, but
researchers still regularly end up with hard-to-reuse scripts, often with manual steps.

## Step-wise data model transformations

With the Omnipy Python package, researchers can import (meta)data in almost any shape or form:
_nested JSON; tabular
(relational) data; binary streams; or other data structures_. Through a step-by-step process, data
is continuously parsed and reshaped according to a series of data model transformations.

## "Parse, don't validate"

Omnipy follows the principles of "Type-driven design" (read
_Technical note #2: "Parse, don't validate"_ on the
[FAIRtracks.net website](https://fairtracks.net/fair/#fair-07-transformation) for more info). It
makes use of cutting-edge [Python type hints](https://peps.python.org/pep-0484/) and the popular
[pydantic](https://pydantic-docs.helpmanual.io/) package to "pour" data into precisely defined data
models that can range from very general (e.g. _"any kind of JSON data", "any kind of tabular data"_,
etc.) to very specific (e.g. _"follow the FAIRtracks JSON Schema for track files with the extra
restriction of only allowing BigBED files"_).

## Data types as contracts

Omnipy _tasks_ (single steps) or _flows_ (dataflows) are defined as transformations from specific
_input_ data models to specific _output_ data models.
[pydantic](https://pydantic-docs.helpmanual.io/)-based parsing guarantees that the input and output
data always follows the data models (i.e. data types). Thus, the data models defines "contracts"
that simplifies reuse of tasks and flows in a _mix-and-match_ fashion.

## Catalog of common processing steps

Omnipy is built from the ground up to be modular. We aim to provide a catalog of commonly useful
functionality ranging from:

- data import from REST API endpoints, common flat file formats, database dumps, etc.
- flattening of complex, nested JSON structures
- standardization of relational tabular data (i.e. removing redundancy)
- mapping of tabular data between schemas
- lookup and mapping of ontology terms
- semi-automatic data cleaning (through e.g. [Open Refine](https://openrefine.org/))
- support for common data manipulation software and libraries, such as
  [Pandas](https://pandas.pydata.org/), [R](https://www.r-project.org/),
  [Frictionless](https://frictionlessdata.io/), etc.

In particular, we will provide a _FAIRtracks_ module that contains data models and processing steps
to transform metadata to follow the [FAIRtracks standard](/standards/#standards-01-fairtracks).

![Catalog of commonly useful processing steps, data modules and tool integrations](https://fairtracks.net/_nuxt/img/7101c5f-1280.png)

## Refine and apply templates

An Omnipy module typically consists of a set of generic _task_ and
_flow templates_ with related data models, (de)serializers, and utility functions. The user can then
pick task and flow templates from this extensible, modular catalog, further refine them in the
context of a custom, use case-specific flow, and apply them to the desired compute engine to carry
out the transformations needed to wrangle data into the required shape.

## Rerun only when needed

When piecing together a custom flow in Omnipy, the user has persistent access to the state of the
data at every step of the process. Persistent intermediate data allows for caching of tasks based on
the input data and parameters. Hence, if the input data and parameters of a task does not change
between runs, the task is not rerun. This is particularly useful for importing from REST API
endpoints, as a flow can be continuously rerun without taxing the remote server; data import will
only carried out in the initial iteration or when the REST API signals that the data has changed.

## Scale up with external compute resources

In the case of large datasets, the researcher can set up a flow based on a representative sample of
the full dataset, in a size that is suited for running locally on, say, a laptop. Once the flow has
produced the correct output on the sample data, the operation can be seamlessly scaled up to the
full dataset and sent off in
[software containers](https://www.docker.com/resources/what-container/) to run on external compute
resources, using e.g. [Kubernetes](https://kubernetes.io/). Such offloaded flows can be easily
monitored using a web GUI.

![Working with Omnipy directly from an Integrated Development Environment (IDE)](https://fairtracks.net/_nuxt/img/f9be071-1440.png)

## Industry-standard ETL backbone

Offloading of flows to external compute resources is provided by the integration of Omnipy with a
dataflow engine based on the [Prefect](https://www.prefect.io/)
Python package. Prefect is an industry-leading platform for dataflow automation and orchestration
that brings a [series of powerful features](https://www.prefect.io/opensource/) to Omnipy:

- Predefined integrations with a range of compute infrastructure solutions
- Predefined integration with various services to support extraction, transformation, and loading
  (ETL) of data and metadata
- Code as workflow ("If Python can write it, Prefect can run it")
- Dynamic workflows: no predefined Direct Acyclic Graphs (DAGs) needed!
- Command line and web GUI-based visibility and control of jobs
- Trigger jobs from external events such as GitHub commits, file uploads, etc.
- Define continuously running workflows that still respond to external events
- Run tasks concurrently through support for asynchronous tasks

![Overview of the compute and storage infrastructure integrations that comes built-in with Prefect](https://fairtracks.net/_nuxt/img/ccc322a-1440.png)

## Pluggable workflow engines

It is also possible to integrate Omnipy with other workflow backends by implementing new workflow
engine plugins. This is relatively easy to do, as the core architecture of Omnipy allows the user to
easily switch the workflow engine at runtime. Omnipy supports both traditional DAG-based and the
more _avant garde_ code-based definition of flows. Two workflow engines are currently supported:
_local_ and _prefect_.
