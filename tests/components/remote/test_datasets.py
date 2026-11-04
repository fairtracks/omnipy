"""Tests for remote datasets."""

import asyncio
from typing import Annotated

from aiohttp import web
import pytest

from omnipy.components.json.datasets import JsonDataset
from omnipy.components.remote import helpers
from omnipy.components.remote.datasets import HttpUrlDataset
from omnipy.components.remote.helpers import RateLimitingClientSession
from omnipy.data.model import Model

from ...helpers.protocols import AssertModelOrValFunc


def test_http_url_dataset(
    assert_model_if_dyn_conv_else_val: Annotated[AssertModelOrValFunc, pytest.fixture],
) -> None:
    urls = HttpUrlDataset()
    urls['url1'] = 'http://abc.net'
    urls['url2'] = 'https://user:pass@cba.com/def?ghi=jkl#mno'

    # TODO: Support dynamically_convert_elements_to_models also for accessing members of
    #       omnipy-wrapped pydantic models

    assert urls['url1'].host == 'abc.net'
    assert_model_if_dyn_conv_else_val(urls['url2'].query['ghi'], str, 'jkl')


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
