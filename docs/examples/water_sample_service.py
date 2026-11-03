"""Serve the README's example river responses without contacting an external API."""

import asyncio
from collections.abc import Iterator
from contextlib import contextmanager
import threading

from aiohttp import web
from aiohttp.test_utils import TestServer

# The river pages from the water_sample_harmonization integration scenario.
RIVER_SAMPLE_PAGES = {
    0: [
        {
            'river_sample_id': 'river-sample-1',
            'catchment': 'glomma-upper',
            'sampled_at': '2026-05-03',
            'station': 'River Mouth',
            'sample_alias': 'River-R1',
            'measurements': [
                {'name': 'Nitrate', 'value_mg_l': 1.2},
                {'name': 'Phosphorus', 'value_ug_l': 120.0},
            ],
        },
        {
            'river_sample_id': 'river-sample-2',
            'catchment': 'glomma-upper',
            'sampled_at': '2026-05-10',
            'station': 'River Mouth',
            'sample_alias': 'River-R2',
            'measurements': [
                {'name': 'nitrate', 'value_mg_l': 1.4},
            ],
        },
    ],
    1: [
        {
            'river_sample_id': 'river-sample-3',
            'catchment': 'glomma-upper',
            'sampled_at': '2026-05-17',
            'station': 'Upstream Bend',
            'sample_alias': 'River-R3',
            'measurements': [
                {'name': 'Temperature', 'value_celsius': 9.8},
            ],
        },
    ],
}


def _create_river_service_app() -> web.Application:
    async def _samples_endpoint(request: web.Request) -> web.Response:
        page = int(request.query.get('page', '-1'))
        if page not in RIVER_SAMPLE_PAGES:
            raise web.HTTPNotFound()
        return web.json_response(RIVER_SAMPLE_PAGES[page])

    app = web.Application()
    app.router.add_route('GET', '/samples', _samples_endpoint)
    return app


@contextmanager
def water_sample_service() -> Iterator[str]:
    """Yield a local base URL serving `/samples?page=N`; keep Omnipy's loading code real."""
    loop = asyncio.new_event_loop()
    server = TestServer(_create_river_service_app(), loop=loop)
    server_started = threading.Event()

    def _run_loop() -> None:
        asyncio.set_event_loop(loop)
        loop.run_until_complete(server.start_server(loop=loop))
        server_started.set()
        loop.run_forever()

    thread = threading.Thread(target=_run_loop, daemon=True)
    thread.start()
    server_started.wait()

    try:
        yield f'http://127.0.0.1:{server.port}'
    finally:
        asyncio.run_coroutine_threadsafe(server.close(), loop).result()
        loop.call_soon_threadsafe(loop.stop)
        thread.join()
