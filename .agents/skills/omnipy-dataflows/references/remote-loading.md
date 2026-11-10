# Paging URLs and Dataset loading

Use `HttpUrlModel` for URL construction and typed Models for generating finite
page ranges and merging response records. The runnable declarations are in
[remote_loading_example.py](remote_loading_example.py); the reusable implementations
live in the general, nested, and remote components.

## Generate a known range of page URLs

`PagesInfo` describes pagination. `PagesInfoRangeModel` expands it into individual
page descriptions, and `GeneratePagedUrlsModel` applies a URL converter and gives
the resulting Dataset explicit positional keys.

```python
from typing import Literal

import omnipy as om
import omnipy.util.pydantic as pyd


class ObservationPagesInfo(om.PagesInfo):
    base_url: pyd.HttpUrl
    endpoint: str = 'observations'


class ObservationPageUrl(om.ConverterModel[ObservationPagesInfo, om.HttpUrlModel]):
    @classmethod
    def _convert(cls, data: ObservationPagesInfo) -> om.HttpUrlModel:
        url = om.HttpUrlModel(data.base_url)
        url.path // 'api' // data.endpoint
        url.query['page'] = data.page
        if data.items_per_page is not None:
            url.query['limit'] = data.items_per_page
        return url


@om.mimics(om.HttpUrlDataset)
class ObservationUrls(om.GeneratePagedUrlsModel[ObservationPageUrl, ObservationPagesInfo]): ...


urls = ObservationUrls(
    base_url='https://example.com',
    num_items=80,
    items_per_page=25,
)
```

This creates four requests, numbered zero through three, with `limit=25` on every
request. The final page has `items_on_page=5`: that is its expected response size,
not a smaller request limit. Keeping request capacity constant matters for APIs
that calculate offsets as `page * limit`. URL construction preserves unrelated
query parameters, fragments, and the base path.

Use `start_from_one=True` for one-based page numbers, `page` for a later start,
and `step` to select every nth page. Supply `num_pages` when the page count is
known directly. Conflicting counts and invalid bounds fail validation.
`num_items=0` or `num_pages=0` produces an empty URL Dataset. Subclass fields and
extra pagination metadata survive expansion.

The API defines its numbering and page-count semantics. Cursor and next-link APIs
need response-dependent traversal; this finite-range helper does not invent a
page count for them. `mimics` supplies static typing for the concrete wrapper;
its runtime behavior comes from the Model itself.

## Merge response pages into a typed Dataset

Declare the record schema and the desired Dataset identity:

```python
class Observation(pyd.BaseModel):
    project: str
    identity: str
    value: int


@om.mimics(om.Dataset[om.Model[Observation]])
class ObservationsByPrimaryKey(
    om.MergePagesOfRecordsIntoDatasetByPrimaryKeyModel[
        om.PrimaryKey[Literal['project'], Literal['identity']], Observation
    ]
): ...


@om.mimics(om.Dataset[om.Model[Observation]])
class ObservationsByPosition(om.MergePagesOfRecordsIntoDatasetByIndexModel[Observation]): ...
```

Both Models accept a sequence of record-list pages or a Dataset containing those
pages. They preserve page and record order and flatten only the page level.
Empty pages contribute no records. The positional variant preserves every
occurrence under keys `'0'`, `'1'`, and so on. The primary-key variant rejects
serialized key collisions, including duplicates from different pages.

A known Pydantic v1 limitation affects record schemas with no required fields:
empty page lists can be interpreted as empty dictionaries and then default-valued
records. The affected cases are marked as a skipped known-issue test, with a TODO
to recheck them when Omnipy migrates to native Pydantic v2.

The reusable pieces are `AddAllValuesModel`, which adds iterable elements or
mapping values without in-place addition; `EnumeratedDatasetModel`, which makes
list positions explicit; and `PrimaryKeyDatasetModel`, which keys validated
Pydantic records. `AddAllValuesModel` returns the added value as its content.
Aggregation requires at least one value, while input already accepted as its
output type passes through under `ConverterModel` semantics. The page-merging
Models accept an empty collection.

Primary-key fields stay visible in each record. Single-field keys are stringified
without escaping. Composite keys escape `%` as `%25` and `|` as `%7C`, then join
the components with `|`. A component's `to_data()` is used when available.
`None`, list values, and dictionary values are supported; dictionary insertion
order affects its string representation. Values with default address-based object
representations and all serialized collisions are rejected. These rules follow
the approved [table architecture spec](../../../../docs/agents/technical/specs/2026-10-16-table-model-architecture-and-conversions.md#primary-keys).

## Load directly into the merge Model

```python
async def load_observations(urls: ObservationUrls) -> ObservationsByPrimaryKey:
    return await om.async_load_urls_into_new_dataset.run(urls, dataset_cls=ObservationsByPrimaryKey)
```

The helper creates an empty instance, calls the shared Model/Dataset
`load_into()`, and returns that same instance. `ObservationsByPrimaryKey.load(urls)`
also creates and loads a new Model. The equivalent instance API is:

```python
async def populate_observations(urls: ObservationUrls) -> ObservationsByPrimaryKey:
    observations = ObservationsByPrimaryKey()
    await observations.load_into(urls)
    return observations
```

The shared loader collects decoded responses in a temporary Dataset, then calls
`from_data()` on the outer Model after loading completes. A single `HttpUrlModel`
(or URL string) supplies the response contents. An `HttpUrlDataset`, including a
mimicking Model, supplies the keyed response collection even when it has zero or
one URL. Mappings, iterables, and keyword URL arguments also supply a collection.
For the merge Models, that collection is parsed through the declared conversion
chain; no page-specific loading implementation is needed.

HTTP failures raise `FailedDataError`; invalid records or duplicate keys raise
validation errors. Existing target contents are retained on these failures.
There is no separate `require_all_items` task in this pipeline. Model/Dataset
wrappers for explicit completion checks and available-data selection remain a
separate extension.

At a synchronous entry point without a running event loop, use
`load_urls_into_new_dataset.run(urls, dataset_cls=ObservationsByPrimaryKey)` or
`observations.load_into(urls)`. Inside an event loop, await the returned task.
Loading uses the existing remote sessions, host configuration, retries, and rate
limits. `as_mime_type` can override response decoding.

An ordinary response Dataset still supports `Dataset.load(urls)` and
`dataset.load_into(urls)`. Its keys identify requests; a list-valued response
remains one Dataset item. The merge Models provide the explicit conversion from
that response shape into per-record Dataset items.

## Post requests to a service

`Model.post()` and `Dataset.post()` send JSON requests through the same remote
sessions, host configuration, and rate limits as loading. A Model posts its complete
contents as one request; a Dataset, or a Model wrapping one, posts each item as a
separate request to the same URL. Name the service's response contract with
`response_cls`:

```python
class RegistrationRequest(pyd.BaseModel):
    sample_alias: str


class RegistrationResponse(pyd.BaseModel):
    sample_alias: str
    sample_id: str


async def register_samples(
    requests: om.Dataset[om.Model[RegistrationRequest]],
    url: om.HttpUrlModel,
) -> om.Dataset[om.Model[RegistrationResponse]]:
    return await requests.post(url, response_cls=om.Dataset[om.Model[RegistrationResponse]])
```

The responses keep the request keys. Without `response_cls`, a Dataset returns a
`JsonDataset` and a Model returns a `JsonModel`. A response Dataset holds each failed
request, or response that does not parse, as a failed item; a response Model raises
the error instead. The URL can be a string or an `HttpUrlModel`. Any 2xx status is a
success. JSON is currently the only supported request and response format.

Like `load()`, `post()` returns the result at a synchronous entry point and an
`asyncio.Task` inside a running event loop, so async code, including task bodies, can
await it directly. `resolve()` from `omnipy.util.helpers` awaits a value only when
needed, for code that may run in either context. The `post_to_url` and
`async_post_to_url` tasks wrap the same entry point.

POST requests are not idempotent: retrying one that the server has already processed
can repeat the operation, e.g. registering a sample twice. They are therefore retried
on the separate `retry_http_statuses_for_post` of the host configuration, which by
default lists only statuses where the server has normally not processed the request
(408, 425, 429 and 503).

Posting each item to the URL with the same key in an `HttpUrlDataset` is planned,
but its design is not settled. Until then, all items of one `post()` call go to the
same URL.

## Save and load local files

`Model` and `Dataset` share `load()`, `load_into()`, and `save()` entry points.
`load()` creates a new instance; `load_into()` updates an existing instance.
Local loading supports files, directories, `.tar.gz` archives, and `.zip`
archives. Pass a string or `Path`, or an iterable of paths for several sources.
Model file loading chooses serializers by file suffix automatically.

A Model receives the contents directly when local loading produces one file.
When it produces several files, including several members of one archive, the
Model receives their keyed collection. An empty archive supplies an empty
collection. Datasets always retain file names as keys and merge loaded entries.
Keyed local paths remain unsupported; keyword arguments and mappings are for URLs.

`Dataset.save()` writes a file for each entry. `Model.save()` writes its complete
contents as one member named `data`, with the serializer's suffix. This preserves
the Model's own dictionary keys and allows a direct round trip:

```python
record = om.Model[dict[str, int]]({'first': 1, 'second': 2})
record.save('record')
restored = om.Model[dict[str, int]].load('record.tar.gz')
```

Saving accepts paths with or without `.tar.gz` and also extracts a directory
copy beside the archive, following the existing Dataset API.

## Test against a local service

Exercise the real URL Models, loading tasks, Dataset loader, and merge conversion
against an `aiohttp` test service. Keep endpoint fixtures and response data in the
test fixture/helper modules. Do not substitute a custom loader for Omnipy's own
loading path.

The [paged-loading tests](../../../../tests/integration/novel/io/test_paged_loading.py)
cover direct instance loading, both loading tasks, out-of-order responses, empty
ranges, malformed records, HTTP failures, composite keys, and collisions. Their
[declarations](../../../../tests/components/remote/helpers/models.py) and
[service fixture](../../../../tests/components/remote/conftest.py) provide a complete
example without contacting a live API. The
[posting tests](../../../../tests/integration/novel/io/test_posting.py) cover the
`post()` entry point the same way, including failed requests and POST retries.
