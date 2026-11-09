"""Local services and runtime configurations for public I/O integration tests."""

import asyncio
from collections.abc import AsyncGenerator
from typing import Annotated

from aiohttp import web
from aiohttp.test_utils import TestServer
import pytest
from pytest_aiohttp import AiohttpServer
import pytest_cases as pc

from omnipy.shared.protocols.hub.runtime import IsRuntime

from .helpers.classes import PagedObservationService


@pytest.fixture(autouse=True)
def configure_runtime(
    runtime: Annotated[IsRuntime, pytest.fixture],
    skip_test_if_dynamically_convert_elements_to_models: Annotated[None, pytest.fixture],
) -> None:
    """Exercise the shared I/O entry points in interactive and non-interactive mode.

    Loading and saving do not depend on dynamic conversion of elements to models, as the
    serializers and model parsing turn it off.
    """


@pc.fixture(scope='function')
async def load_content_server(aiohttp_server: AiohttpServer) -> AsyncGenerator[TestServer, None]:
    """Serve the response formats supported by the shared Model/Dataset loader."""

    async def content(request: web.Request) -> web.Response:
        match request.match_info['kind']:
            case 'json':
                return web.json_response([1, 2])
            case 'text':
                return web.Response(text='sample')
            case 'bytes':
                return web.Response(body=b'sample')
            case 'json_as_text':
                return web.Response(text='[1, 2]')
            case _:
                return web.Response(status=404)

    app = web.Application()
    app.router.add_get('/{kind}', content)
    yield await aiohttp_server(app)


@pc.fixture(scope='function')
async def paged_observation_service(
    aiohttp_server,
) -> AsyncGenerator[PagedObservationService, None]:
    """Serve finite record pages and allow response failures to be injected."""
    service = PagedObservationService(
        records=[
            {'project': 'north', 'identity': 'a|b', 'value': 1},
            {'project': 'north', 'identity': 'c%', 'value': 2},
            {'project': 'south', 'identity': 'a|b', 'value': 3},
            {'project': 'south', 'identity': 'd', 'value': 4},
            {'project': 'south', 'identity': 'e', 'value': 5},
        ]
    )

    async def observations(request: web.Request) -> web.Response:
        page = int(request.query['page'])
        limit = int(request.query['limit'])
        service.requests.append((page, limit))
        if page == 0:
            await asyncio.sleep(0.02)
        if page in service.responses:
            response = service.responses[page]
            if isinstance(response, int):
                return web.Response(status=response)
            return web.json_response(response)
        return web.json_response(service.records[page * limit : (page + 1) * limit])

    app = web.Application()
    app.router.add_get('/api/observations', observations)
    server = await aiohttp_server(app)
    service.base_url = str(server.make_url('/'))
    yield service
