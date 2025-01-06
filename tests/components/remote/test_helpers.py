import asyncio
from datetime import datetime
from typing import Annotated, AsyncGenerator

from aiohttp import ClientSession, web
import pytest
import pytest_cases as pc

from omnipy.components.remote.helpers import RateLimitingClientSession


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
    client_session: RateLimitingClientSession,
    my_endpoint_url: str,
    num_requests: int,
) -> float:
    start_time = datetime.now()

    tasks = [client_session.get(my_endpoint_url) for _ in range(num_requests)]
    responses = await asyncio.gather(*tasks)
    for response in responses:
        assert response.status == 200
        assert await response.text() == '"My response"'

    return (datetime.now() - start_time).total_seconds()


@pytest.mark.parametrize(
    'num_requests, requests_per_time_period, time_period_in_secs, run_time_min, run_time_max',
    [
        (21, 1, 0.05, 0.95, 1.07),
        (21, 10, 0.5, 0.95, 1.05),
    ],
    ids=['no_burst_1_requests_per_0.05s', 'burst_10_requests_per_0.5s'],
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
    client_session = RateLimitingClientSession(requests_per_time_period, time_period_in_secs)

    async with client_session:
        assert client_session.requests_per_second == requests_per_time_period / time_period_in_secs
        assert isinstance(client_session, ClientSession)

        for i in range(2):
            run_time = await _assert_requests_and_get_run_time_in_secs(
                client_session,
                my_endpoint_url,
                num_requests,
            )

            assert run_time_min < run_time < run_time_max

            await asyncio.sleep(0.1)
