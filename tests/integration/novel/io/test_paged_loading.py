"""Exercise URL generation, remote loading, and page merging against a local API."""

import asyncio

import pytest

from omnipy.components.general.models import MergeListsOfRecordsIntoDatasetByIndexModel
from omnipy.components.remote.tasks import async_load_urls, load_urls
from omnipy.shared.exceptions import FailedDataError
from omnipy.util.helpers import resolve
from omnipy.util.pydantic import ValidationError

from .helpers.classes import PagedObservationService
from .helpers.models import (
    MergeObservations,
    Observation,
    ObservationUrls,
)


@pytest.mark.parametrize(
    'mode', ['instance', 'class', 'async_task', 'sync_task', 'sync_task_in_loop']
)
async def test_load_directly_into_merge_model(
    paged_observation_service: PagedObservationService, mode: str
) -> None:
    service = paged_observation_service
    urls = ObservationUrls(
        base_url=service.base_url, num_items=len(service.records), items_per_page=2
    )
    if mode == 'instance':
        dataset = MergeObservations()
        assert await resolve(dataset.load_into(urls)) is dataset
    elif mode == 'class':
        dataset = await resolve(MergeObservations.load(urls))
    elif mode == 'async_task':
        dataset = await async_load_urls.run(urls, data_cls=MergeObservations)
    elif mode == 'sync_task':
        dataset = await asyncio.to_thread(load_urls.run, urls, data_cls=MergeObservations)
    else:
        dataset = await resolve(load_urls.run(urls, data_cls=MergeObservations))

    assert isinstance(dataset, MergeObservations)
    assert list(dataset.to_data()) == [
        'north|a%7Cb',
        'north|c%25',
        'south|a%7Cb',
        'south|d',
        'south|e',
    ]
    assert list(dataset.to_data().values()) == service.records
    assert sorted(service.requests) == [(0, 2), (1, 2), (2, 2)]


async def test_load_directly_into_index_merge_model(
    paged_observation_service: PagedObservationService,
) -> None:
    service = paged_observation_service
    urls = ObservationUrls(
        base_url=service.base_url, num_items=len(service.records), items_per_page=2
    )
    model_cls = MergeListsOfRecordsIntoDatasetByIndexModel[Observation]
    dataset = await async_load_urls.run(urls, data_cls=model_cls)
    assert list(dataset.to_data()) == ['0', '1', '2', '3', '4']
    assert list(dataset.to_data().values()) == service.records


async def test_empty_pagination_makes_no_requests(
    paged_observation_service: PagedObservationService,
) -> None:
    service = paged_observation_service
    urls = ObservationUrls(base_url=service.base_url, num_items=0, items_per_page=2)
    dataset = await async_load_urls.run(urls, data_cls=MergeObservations)
    assert dataset.to_data() == {}
    assert service.requests == []


@pytest.mark.parametrize('failure', ['duplicate', 'invalid_record', 'http_error'])
async def test_failed_page_merge_preserves_existing_target(
    paged_observation_service: PagedObservationService, failure: str
) -> None:
    service = paged_observation_service
    urls = ObservationUrls(
        base_url=service.base_url, num_items=len(service.records), items_per_page=2
    )
    original = [[{'project': 'original', 'identity': 'kept', 'value': 7}]]
    dataset = MergeObservations(original)
    if failure == 'duplicate':
        service.responses[1] = [service.records[0]]
        expected_error = ValidationError
    elif failure == 'invalid_record':
        service.responses[1] = [{'value': 'bad'}]
        expected_error = ValidationError
    else:
        service.responses[1] = 503
        dataset.config.http.defaults.retry_attempts = 1
        expected_error = FailedDataError

    with pytest.raises(expected_error):
        await resolve(dataset.load_into(urls))
    assert dataset.to_data() == {'original|kept': original[0][0]}
