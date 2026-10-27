# Paging URLs and Dataset loading

Use `HttpUrlModel` for URL construction and `HttpUrlDataset` for named request
sources. Edit structured components (`path`, `query`, `port`) through their
mimicked interfaces. This preserves unrelated URL parts and delegates URL
validation and encoding to the existing Models.

## Construct a known set of page URLs

```python
import omnipy as om


@om.mimics(int)
class PageNumberModel(om.Model[int]):
    ...


@om.TaskTemplate(iterate_over_data_files=True, output_dataset_cls=om.HttpUrlDataset)
def page_url(page: PageNumberModel, *, endpoint: om.HttpUrlModel) -> om.HttpUrlModel:
    url = endpoint.copy(deep=True)
    url.query['page'] = str(int(page))
    return url


endpoint = om.HttpUrlModel('https://example.com/api?limit=100')
endpoint.path /= 'observations'
page_numbers = om.Dataset[PageNumberModel]({f'page-{page}': page for page in range(1, 4)})
urls = page_url.run(page_numbers, endpoint=endpoint)
```

`PageNumberModel` exposes integer operations statically on the task parameter
as well as at runtime; see [typing examples](typing.md). `str(int(page))` produces
the query value; `str(page)` alone produces the general Model representation.
The copy isolates each page's edits from the shared endpoint. The comprehension
constructs known inputs; the iterated task performs the batch transformation.
The service defines whether page numbers begin at zero or one and how page count
is obtained. A cursor or next-link API needs response-dependent traversal; do not
invent page numbers or request all pages speculatively for that API.

The URL Dataset's keys identify request/response slots such as `page-2`. Loading
retains those keys. They do not become the primary keys of every record inside
the response. If a later stage schedules work per domain record, construct that
stage's Dataset using the records' primary keys and reject collisions. A page
containing a list of observations remains one response item at the loading stage.

## Load into the intended response type

For an ordinary synchronous entry point without a running event loop:

```python
pages = om.JsonListOfDictsDataset.load(urls)
```

For HTTP URLs inside a running event loop, `load` returns an `asyncio.Task` that
must be awaited. Its annotation covers both sync and async outcomes; the existing
`resolve` helper is useful when a boundary accepts either form:

```python
from omnipy.util.helpers import resolve


async def load_urls(urls: om.HttpUrlDataset) -> om.JsonListOfDictsDataset:
    return await resolve(om.JsonListOfDictsDataset.load(urls))
```

This is the documented dual-mode loader contract, not a reason to inspect whether
every job result is awaitable. `load(...)` creates a new Dataset; `load_into(...)`
loads into an existing instance. Select the target Dataset for the response
shape, such as a JSON list of objects per URL. A custom response Dataset can
validate more specific schemas. Loading does not automatically flatten pages or
map an external response schema into the dataflow's domain schema.

HTTP loading uses the remote component's sessions, host configuration, retry
configuration, and rate limiting. Reuse that behavior before writing a second
HTTP client or manual gathering loop. Plain `iterate_over_data_files=True` alone
does not imply those HTTP policies. `as_mime_type` is an available decoding hint
when the service's content type needs an explicit override. More advanced client
and recovery requirements require inspecting the current component API.

## Compose the existing loading tasks

When loading is a flow stage, first consider the reusable
`load_urls_into_new_dataset` and `async_load_urls_into_new_dataset` templates. Bind
the response Dataset class with a modifier:

```python
fetch_pages = om.async_load_urls_into_new_dataset.refine(
    fixed_params={'dataset_cls': om.JsonListOfDictsDataset},
)


@om.LinearFlowTemplate(page_url, fetch_pages)
async def load_pages(
    page_numbers: om.Dataset[PageNumberModel], *, endpoint: om.HttpUrlModel,
) -> om.JsonListOfDictsDataset:
    ...
```

Use the async template in async composition and the sync template at a synchronous
boundary. The first stage creates the URL batch, and the second loads it using
the existing component. Add a wrapper task when it contributes a meaningful
contract or operation beyond renaming the loader.

Check failed/pending results before assuming every page loaded; see
[current failure inspection](patterns.md#inspect-current-failure-and-pending-results).
Partial pagination must not silently become a supposedly complete source.

## Test the real loader against a mocked service

For an integration test or tutorial test, mock the external service and exercise
Omnipy itself. Use pytest and the repository's existing runtime, engine, and HTTP
server fixtures. Do not replace `Dataset.load()` or the remote loading templates
with a custom fixture loader, and do not replace Omnipy's scheduling or validation
to manufacture the expected result.

Use this arrangement:

1. A service fixture exposes the API's actual routes, query parameters, response
   payloads, content types, and relevant error responses through a local HTTP
   test server. Keep fixture data and service state in `conftest.py` or fixture
   and `pytest_cases` case modules suited to the scenarios.
2. Construct `HttpUrlModel` endpoints using that server's host/port and pass them
   into the actual flow. Its normal URL construction and Dataset loading run
   against those endpoints.
3. Assert observed service requests and the resulting typed data. Select failure
   cases that support the scenario's contract; a success case alone does not
   verify every retry, rate-limiting, or recovery policy.

The water-sample example's
[service fixtures](../../../../tests/integration/novel/full/water_sample_harmonization/conftest.py)
use an `aiohttp.web.Application` and the `aiohttp_server` pytest fixture to serve
JSON pages. Follow that arrangement to exercise real request handling, response
decoding, and Dataset population without depending on a live external service.
For a service represented by a typed callable, replace that external callable
with a faithful stand-in while retaining the real Omnipy task and flow.

The existing tutorial example is
[water-sample harmonization](../../../../tests/integration/novel/full/water_sample_harmonization/test_water_sample_harmonization.py),
with a loader in its [tasks module](../../../../tests/integration/novel/full/water_sample_harmonization/tasks.py).
API sources are `src/omnipy/components/remote/models.py`,
`src/omnipy/components/remote/tasks.py`, and `Dataset.load` / `Dataset.load_into`
in `src/omnipy/data/dataset.py`. Component-specific skills beyond these common
patterns remain future work.
