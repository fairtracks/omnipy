from typing import Annotated

from aiohttp.test_utils import TestServer
import pytest

from omnipy.components.remote.datasets import HttpUrlDataset
from omnipy.components.remote.models import HttpUrlModel

from .flows import env_monitoring_harmonization_flow, flatten_and_wrangle_as_dataframe
from .models import NormalizedBatchesDataset


def _build_paginated_source_urls(source_name: str, port: int | None, endpoint: str,
                                 page_count: int) -> HttpUrlDataset:
    urls = HttpUrlDataset()

    for page in range(page_count):
        url = HttpUrlModel('http://localhost')
        url.port = port
        url.path /= endpoint
        url.query['page'] = page
        urls[f'{source_name}_page_{page}'] = url

    return urls


@pytest.fixture
async def harmonized_batches(
    runtime_all_engines: Annotated[None, pytest.fixture],  # noqa
    river_service: Annotated[TestServer, pytest.fixture],
    wastewater_service: Annotated[TestServer, pytest.fixture],
) -> NormalizedBatchesDataset:
    river_urls = _build_paginated_source_urls(
        'river',
        river_service.port,
        'samples',
        page_count=2,
    )
    wastewater_urls = _build_paginated_source_urls(
        'wastewater',
        wastewater_service.port,
        'retrieve_samples',
        page_count=2,
    )

    return await env_monitoring_harmonization_flow.run(
        river_urls=river_urls, wastewater_urls=wastewater_urls)


async def test_harmonize_environmental_monitoring_data(
    runtime_all_engines: Annotated[None, pytest.fixture],  # noqa
    harmonized_batches: Annotated[NormalizedBatchesDataset, pytest.fixture],
) -> None:
    print()
    # harmonized_batches.full(syntax='json5')
    harmonized_batches.full()

    assert harmonized_batches['all_river_batches'].to_data()[0] == {
        'sample_key':
            'river-r1',
        'catchment_id':
            'glomma-upper',
        'monitoring_date':
            '2026-05-03',
        'location_name':
            'River Mouth',
        'measurements': [
            {
                'type': 'nitrate',
                'value': 1.2,
                'unit': 'mg/L',
            },
            {
                'type': 'phosphorus',
                'value': 0.12,
                'unit': 'mg/L',
            },
        ],
    }

    assert harmonized_batches['all_wastewater_batches'].to_data()[0] == {
        'sample_key':
            'ww-9a',
        'catchment_id':
            'glomma-upper',
        'monitoring_date':
            '2026-05-03',
        'location_name':
            'North Works',
        'measurements': [
            {
                'type': 'ammonium',
                'value': 0.8,
                'unit': 'mg/L',
            },
            {
                'type': 'phosphorus',
                'value': 0.15,
                'unit': 'mg/L',
            },
        ]
    }


async def test_flatten_and_wrangle_environmental_monitoring_data_as_dataframe(
    runtime_all_engines: Annotated[None, pytest.fixture],  # noqa
    harmonized_batches: Annotated['NormalizedBatchesDataset', pytest.fixture],
) -> None:
    flattened_df_dataset = flatten_and_wrangle_as_dataframe.run(harmonized_batches)
    print()
    flattened_df_dataset['samples'].full()
    flattened_df_dataset['measurements'].full()

    assert flattened_df_dataset['samples'].to_data()['sample_key'] == [
        'river-r1',
        'river-r2',
        'river-r3',
        'ww-9a',
        'ww-9b',
    ]

    assert flattened_df_dataset['measurements'].to_data()['monitoring_date'] == [
        '2026-05-03',
        '2026-05-03',
        '2026-05-03',
        '2026-05-03',
        '2026-05-10',
        '2026-05-10',
        '2026-05-17',
    ]

    assert flattened_df_dataset['measurements'].to_data()['value'] == [
        0.8,
        0.15,
        1.2,
        0.12,
        0.75,
        1.4,
        9.8,
    ]
