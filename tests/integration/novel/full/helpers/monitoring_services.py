from collections.abc import AsyncGenerator
from typing import cast, Literal

from aiohttp import web
from aiohttp.test_utils import TestServer
import pytest

from omnipy import HttpUrlDataset, HttpUrlModel

MonitoringSource = Literal['river', 'wastewater']

_MONITORING_PAGES: dict[MonitoringSource, dict[int, list[dict[str, object]]]] = {
    'river': {
        1: [
            {
                'river_batch_id':
                    'river-batch-1',
                'catchment':
                    'glomma-upper',
                'sampled_at':
                    '2026-05-03',
                'station':
                    'River Mouth',
                'sample_alias':
                    'River-R1',
                'measurements': [
                    {
                        'name': 'nitrate', 'value_mg_l': 1.2
                    },
                    {
                        'name': 'phosphorus', 'value_ug_l': 120.0
                    },
                ],
            },
            {
                'river_batch_id': 'river-batch-2',
                'catchment': 'glomma-upper',
                'sampled_at': '2026-05-10',
                'station': 'River Mouth',
                'sample_alias': 'River-R2',
                'measurements': [{
                    'name': 'nitrate', 'value_mg_l': 1.4
                },],
            },
        ],
        2: [{
            'river_batch_id': 'river-batch-3',
            'catchment': 'glomma-upper',
            'sampled_at': '2026-05-17',
            'station': 'Upstream Bend',
            'sample_alias': 'River-R3',
            'measurements': [{
                'name': 'temperature', 'value_celsius': 9.8
            },],
        },],
    },
    'wastewater': {
        1: [{
            'wastewater_batch_id':
                'wastewater-batch-1',
            'catchment_code':
                'glomma-upper',
            'monitoring_date':
                '2026-05-03',
            'treatment_plant':
                'North Works',
            'sample_alias':
                'WW-9A',
            'measurements': [
                {
                    'metric': 'ammonium', 'value': '0.8', 'unit': 'mg/L'
                },
                {
                    'metric': 'phosphorus', 'value': '0.15', 'unit': 'mg/L'
                },
            ],
        },],
        2: [{
            'wastewater_batch_id': 'wastewater-batch-2',
            'catchment_code': 'glomma-upper',
            'monitoring_date': '2026-05-10',
            'treatment_plant': 'North Works',
            'sample_alias': 'WW-9B',
            'measurements': [{
                'metric': 'ammonium', 'value': '0.75', 'unit': 'mg/L'
            },],
        },],
    },
}


def create_monitoring_service_app() -> web.Application:
    async def _monitoring_endpoint(request: web.Request) -> web.Response:
        source = cast(MonitoringSource, request.match_info['source'])
        page = int(request.query.get('page', '1'))
        return web.json_response(_MONITORING_PAGES[source][page])

    app = web.Application()
    app.router.add_route('GET', '/{source}', _monitoring_endpoint)
    return app


@pytest.fixture(scope='function')
async def monitoring_service(aiohttp_server) -> AsyncGenerator[TestServer, None]:
    yield await aiohttp_server(create_monitoring_service_app())


def build_paginated_source_urls(server: TestServer, source: MonitoringSource) -> HttpUrlDataset:
    base_url = str(server.make_url(f'/{source}'))
    urls = HttpUrlDataset()

    for page in sorted(_MONITORING_PAGES[source]):
        url = HttpUrlModel(base_url)
        url.query['page'] = str(page)
        urls[f'{source}_page_{page}'] = url

    return urls
