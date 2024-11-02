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


async def test_rate_limiting_client_session(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture],
        my_endpoint_url: Annotated[str, pytest.fixture]):
    async with RateLimitingClientSession(requests_per_second=10) as client_session:
        assert client_session.requests_per_second == 10
        assert isinstance(client_session, ClientSession)

        start_time = datetime.now()
        async with client_session:
            tasks = [client_session.get(my_endpoint_url) for _ in range(21)]
            responses = await asyncio.gather(*tasks)
            for response in responses:
                assert response.status == 200
                assert await response.text() == '"My response"'
        end_time = datetime.now()
        assert (end_time - start_time).total_seconds() > 2
