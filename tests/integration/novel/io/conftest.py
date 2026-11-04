"""Local services and runtime configurations for public I/O integration tests."""

from collections.abc import AsyncGenerator
from typing import Annotated

from aiohttp import web
from aiohttp.test_utils import TestServer
import pytest
from pytest_aiohttp import AiohttpServer
import pytest_cases as pc

from omnipy.shared.protocols.hub.runtime import IsRuntime


@pytest.fixture(autouse=True)
def configure_runtime(runtime: Annotated[IsRuntime, pytest.fixture]) -> None:
    """Exercise the shared I/O entry points under each Model configuration."""


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
