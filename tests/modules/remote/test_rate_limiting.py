import asyncio
from datetime import datetime
from typing import Annotated, AsyncGenerator

from aiohttp import ClientSession, web
import pytest
import pytest_cases as pc

from omnipy.modules.remote.helpers import RateLimitingClientSession


async def my_endpoint(request: web.Request) -> web.Response:
    return web.json_response('My response')


def create_app() -> web.Application:
    app = web.Application()
    app.router.add_route('GET', '/my_endpoint', my_endpoint)
    return app


@pc.fixture(scope='function')
async def my_endpoint_url(aiohttp_server) -> AsyncGenerator[str, None]:
    server = await aiohttp_server(create_app())
    yield str(server.make_url('/my_endpoint'))


async def _assert_requests_and_get_run_time_in_secs(
    my_endpoint_url: str,
    num_requests: int,
    requests_per_time_period: float,
    time_period_in_secs: float,
) -> float:
    client_session = RateLimitingClientSession(requests_per_time_period, time_period_in_secs)
    async with client_session:
        assert client_session.requests_per_second == requests_per_time_period / time_period_in_secs
        assert isinstance(client_session, ClientSession)

        start_time = datetime.now()
        async with client_session:
            tasks = [client_session.get(my_endpoint_url) for _ in range(num_requests)]
            responses = await asyncio.gather(*tasks)
            for response in responses:
                assert response.status == 200
                assert await response.text() == '"My response"'
        end_time = datetime.now()
    return (end_time - start_time).total_seconds()


@pytest.mark.parametrize(
    'num_requests, requests_per_time_period, time_period_in_secs, run_time_min, run_time_max',
    [
        (21, 10, 0.5, 1, 1.1),
        (21, 1, 0.05, 1, 1.1),
    ],
    ids=['10_requests_per_0.5s', '1_requests_per_0.05s'],
)
async def test_rate_limiting_client_session(
    skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture],
    my_endpoint_url: Annotated[str, pytest.fixture],
    num_requests: int,
    requests_per_time_period: float,
    time_period_in_secs: float,
    run_time_min: float,
    run_time_max: float,
) -> None:
    run_time = await _assert_requests_and_get_run_time_in_secs(
        my_endpoint_url,
        num_requests,
        requests_per_time_period,
        time_period_in_secs,
    )
    assert run_time_min < run_time < run_time_max
