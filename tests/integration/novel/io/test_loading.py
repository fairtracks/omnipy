"""Load remote content through the shared Model and Dataset entry points."""

import asyncio

from aiohttp import web
from aiohttp.test_utils import TestServer
import pytest
import pytest_cases as pc

from omnipy.components.json.datasets import JsonDataset
from omnipy.components.remote import helpers
from omnipy.components.remote.datasets import HttpUrlDataset
from omnipy.components.remote.helpers import RateLimitingClientSession
from omnipy.components.remote.models import HttpUrlModel
from omnipy.components.remote.tasks import (
    async_load_urls_into_new_dataset,
    load_urls_into_new_dataset,
)
from omnipy.data.dataset import Dataset
from omnipy.data.model import Model
from omnipy.shared.exceptions import FailedDataError
from omnipy.util.helpers import resolve
from omnipy.util.pydantic import ValidationError

from .helpers.functions import expected_for


@pytest.mark.parametrize(
    'kind, model_cls, expected',
    [
        ('json', Model[list[int]], [1, 2]),
        ('text', Model[str], 'sample'),
        ('bytes', Model[bytes], b'sample'),
    ],
)
@pytest.mark.parametrize('mode', ['instance', 'class', 'sync_instance', 'sync_class'])
async def test_model_load_single_response(
    load_content_server: TestServer, kind: str, model_cls: type[Model], expected, mode: str
) -> None:
    url = HttpUrlModel(str(load_content_server.make_url(f'/{kind}')))
    if mode == 'instance':
        model = model_cls()
        original = model.to_data()
        loading = model.load_into(url)
        assert isinstance(loading, asyncio.Task)
        assert model.to_data() == original
        assert await loading is model
    elif mode == 'class':
        model = await resolve(model_cls.load(url))
    elif mode == 'sync_instance':
        model = model_cls()
        assert await asyncio.to_thread(model.load_into, url) is model
    else:
        model = await asyncio.to_thread(model_cls.load, url)

    assert isinstance(model, model_cls)
    assert model.to_data() == expected


@pytest.mark.parametrize('wrapper_cls', [HttpUrlDataset, Model[Model[HttpUrlDataset]], dict])
@pytest.mark.parametrize('count', [0, 1, 2])
async def test_model_load_keyed_collection(
    load_content_server: TestServer, wrapper_cls: type, count: int
) -> None:
    url = str(load_content_server.make_url('/json'))
    urls = wrapper_cls({key: url for key in ('first', 'second')[:count]})
    model = Model[dict[str, list[int]]]({'existing': [9]})

    loading = model.load_into(urls)
    assert isinstance(loading, asyncio.Task)
    assert model.content == {'existing': [9]}
    assert await loading is model
    assert model.content == {key: [1, 2] for key in ('first', 'second')[:count]}


async def test_model_load_url_string_and_mime_override(load_content_server: TestServer) -> None:
    url = str(load_content_server.make_url('/json_as_text'))
    model = await resolve(Model[list[int]].load(url, as_mime_type='application/json'))
    assert model.content == [1, 2]


async def test_model_load_keyword_and_iterable_sources(load_content_server: TestServer) -> None:
    url = str(load_content_server.make_url('/json'))
    model_cls = Model[dict[str, list[int]]]

    named = await resolve(model_cls.load(page=HttpUrlModel(url)))
    assert named.content == {'page': [1, 2]}

    iterable = await resolve(model_cls.load([url]))
    assert iterable.content == {url: [1, 2]}


@pytest.mark.parametrize('collection', [False, True])
@pytest.mark.parametrize('failure', ['http', 'validation'])
async def test_model_loading_failure_preserves_contents(
    load_content_server: TestServer, collection: bool, failure: str
) -> None:
    url = HttpUrlModel(
        str(load_content_server.make_url('/missing' if failure == 'http' else '/json'))
    )
    model = Model[dict[str, int]]({'existing': 7}) if collection else Model[int](7)
    original = model.to_data()
    urls = HttpUrlDataset(page=url) if collection else url

    with pytest.raises(FailedDataError if failure == 'http' else ValidationError):
        await resolve(model.load_into(urls))
    assert model.to_data() == original


@pytest.mark.usefixtures('skip_test_if_not_default_data_config_values')
async def test_dataset_load_rate_limits_with_the_host_config(
    aiohttp_server,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def endpoint(request: web.Request) -> web.Response:
        return web.json_response(dict(value=request.match_info['i']))

    app = web.Application()
    app.router.add_route('GET', '/data/{i}', endpoint)
    server = await aiohttp_server(app)

    sessions: list[RateLimitingClientSession] = []

    class RecordingSession(RateLimitingClientSession):
        def __init__(self, *args, **kwargs) -> None:
            super().__init__(*args, **kwargs)
            sessions.append(self)

    monkeypatch.setattr(helpers, 'RateLimitingClientSession', RecordingSession)

    dataset = JsonDataset()
    host_config = dataset.config.http.for_host[server.host]
    monkeypatch.setattr(host_config, 'requests_per_time_period', 7)
    monkeypatch.setattr(host_config, 'time_period_in_secs', 0.5)
    monkeypatch.setattr(host_config, 'burst_ratio', 0.3)

    urls = HttpUrlDataset({str(i): str(server.make_url(f'/data/{i}')) for i in range(3)})
    load_task = dataset.load(urls)
    assert isinstance(load_task, asyncio.Task)
    loaded = await load_task

    assert loaded.to_data() == {str(i): dict(value=str(i)) for i in range(3)}
    assert len(sessions) == 1
    assert sessions[0].requests_per_time_period == 7
    assert sessions[0].time_period_in_secs == 0.5
    assert sessions[0].burst_size == 2


@pytest.mark.parametrize(
    'wrapper_cls',
    [dict, Model[dict[str, str]], Model[Model[HttpUrlDataset]]],
)
@pytest.mark.parametrize('empty', [False, True])
async def test_dataset_load_into_preserves_keys_from_wrapped_urls(
    aiohttp_server, wrapper_cls: type, empty: bool
) -> None:
    async def endpoint(request: web.Request) -> web.Response:
        return web.json_response(dict(value=request.match_info['name']))

    app = web.Application()
    app.router.add_get('/data/{name}', endpoint)
    server = await aiohttp_server(app)

    url_data = (
        {}
        if empty
        else {
            'first_page': str(server.make_url('/data/one')),
            'second_page': str(server.make_url('/data/two')),
        }
    )
    urls = wrapper_cls(url_data)
    dataset = JsonDataset(existing={'value': 'original'})

    load_task = dataset.load_into(urls)
    assert isinstance(load_task, asyncio.Task)
    loaded = await load_task

    expected = {'existing': {'value': 'original'}}
    if not empty:
        expected |= {'first_page': {'value': 'one'}, 'second_page': {'value': 'two'}}
    assert loaded is dataset
    assert dataset.to_data() == expected
    assert list(dataset) == list(expected)


@pc.parametrize_with_cases('load_kwargs, expected_model, expected_dataset', cases='.cases.urls')
@pytest.mark.parametrize('target_cls', [Model[object], Dataset[Model[object]], Model[JsonDataset]])
@pytest.mark.parametrize('entry_point', ['load', 'load_into'])
async def test_model_and_dataset_http_inputs(
    load_kwargs, expected_model, expected_dataset, target_cls, entry_point
) -> None:
    if entry_point == 'load':
        result = await resolve(target_cls.load(**load_kwargs))
    else:
        result = target_cls()
        assert await resolve(result.load_into(**load_kwargs)) is result
    assert result.to_data() == expected_for(result, expected_model, expected_dataset)


@pytest.mark.parametrize('target_cls', [JsonDataset, Model[dict[str, list[int]]]])
async def test_load_urls_into_new_dataset_tasks(
    load_content_server: TestServer, target_cls: type
) -> None:
    urls = HttpUrlDataset(first=str(load_content_server.make_url('/json')))

    loaded = await resolve(load_urls_into_new_dataset.run(urls, dataset_cls=target_cls))
    assert isinstance(loaded, target_cls)
    assert loaded.to_data() == {'first': [1, 2]}

    loaded = await async_load_urls_into_new_dataset.run(urls, dataset_cls=target_cls)
    assert isinstance(loaded, target_cls)
    assert loaded.to_data() == {'first': [1, 2]}
