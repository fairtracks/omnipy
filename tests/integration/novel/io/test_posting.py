"""Post contents as JSON through the shared Model and Dataset entry point."""

import asyncio

import pytest

from omnipy.components.json.datasets import JsonDataset
from omnipy.components.json.models import JsonModel
from omnipy.components.remote.models import HttpUrlModel
from omnipy.components.remote.tasks import async_post_to_url, post_to_url
from omnipy.data.dataset import Dataset
from omnipy.data.model import Model
from omnipy.shared.exceptions import FailedDataError
from omnipy.util.helpers import resolve
import omnipy.util.pydantic as pyd

from .helpers.classes import PostService


class DoubledSchema(pyd.BaseModel):
    doubled: int


class DoubledModel(Model[DoubledSchema]): ...


class DoubledDataset(Dataset[DoubledModel]): ...


class ErrorSchema(pyd.BaseModel):
    error: str


def _sorted_requests(post_service: PostService) -> list[object]:
    return sorted(post_service.requests, key=str)


@pytest.mark.parametrize('mode', ['async', 'sync'])
async def test_model_post_single_request(post_service: PostService, mode: str) -> None:
    model = Model[dict[str, int]]({'value': 21})
    url = post_service.url('/double')

    if mode == 'async':
        posting = model.post(url)
        assert isinstance(posting, asyncio.Task)
        response = await posting
    else:
        response = await asyncio.to_thread(model.post, url)

    assert isinstance(response, JsonModel)
    assert response.to_data() == {'doubled': 42}
    assert post_service.requests == [{'value': 21}]


@pytest.mark.parametrize(
    'data_cls',
    [Dataset[Model[dict[str, int]]], Model[JsonDataset]],
    ids=['dataset', 'model_wrapping_dataset'],
)
@pytest.mark.parametrize('url_cls', [str, HttpUrlModel], ids=['str', 'http_url_model'])
async def test_post_each_data_item_to_the_url(
    post_service: PostService,
    data_cls: type[Dataset] | type[Model],
    url_cls: type[str] | type[HttpUrlModel],
) -> None:
    data = data_cls({'first': {'value': 1}, 'second': {'value': 2}})

    responses = await resolve(data.post(url_cls(post_service.url('/double'))))

    assert isinstance(responses, JsonDataset)
    assert responses.to_data() == {'first': {'doubled': 2}, 'second': {'doubled': 4}}
    assert _sorted_requests(post_service) == [{'value': 1}, {'value': 2}]


async def test_post_parses_responses_with_response_cls(post_service: PostService) -> None:
    url = post_service.url('/double')

    responses = await resolve(
        JsonDataset({'first': {'value': 1}}).post(url, response_cls=DoubledDataset)
    )
    assert isinstance(responses, DoubledDataset)
    assert responses.to_data() == {'first': {'doubled': 2}}

    response = await resolve(
        Model[dict[str, int]]({'value': 3}).post(url, response_cls=DoubledModel)
    )
    assert isinstance(response, DoubledModel)
    assert response.to_data() == {'doubled': 6}


async def test_dataset_post_keeps_failed_requests_as_failed_items(
    post_service: PostService,
) -> None:
    rejected = await resolve(JsonDataset({'first': {'value': 1}}).post(post_service.url('/reject')))
    with pytest.raises(FailedDataError, match='HTTP status: 400'):
        _ = rejected['first']

    unparsable = await resolve(
        JsonDataset({'first': {'value': 1}}).post(
            post_service.url('/double'),
            response_cls=Dataset[Model[ErrorSchema]],
        )
    )
    with pytest.raises(FailedDataError):
        _ = unparsable['first']


async def test_model_post_raises_for_failed_request(post_service: PostService) -> None:
    with pytest.raises(FailedDataError, match='HTTP status: 400'):
        await resolve(Model[dict[str, int]]({'value': 1}).post(post_service.url('/reject')))


async def test_post_accepts_only_json_responses(post_service: PostService) -> None:
    response = await resolve(
        Model[dict[str, int]]({'value': 1}).post(post_service.url('/json-only'))
    )

    assert response.to_data() == {'accepted': True}


@pytest.mark.usefixtures('skip_test_if_not_default_data_config_values')
@pytest.mark.parametrize(
    'first_status, retry_http_statuses_for_post, retried',
    [
        (503, None, True),
        (500, None, False),
        (500, (500,), True),
        (503, (), False),
    ],
    ids=['default_retries_503', 'default_does_not_retry_500', 'config_retries_500', 'no_retries'],
)
async def test_post_retries_on_the_host_config_statuses_for_post(
    post_service: PostService,
    monkeypatch: pytest.MonkeyPatch,
    first_status: int,
    retry_http_statuses_for_post: tuple[int, ...] | None,
    retried: bool,
) -> None:
    post_service.first_status = first_status
    data = JsonDataset({'submission': {'value': 1}})
    if retry_http_statuses_for_post is not None:
        host_config = data.config.http.for_host[HttpUrlModel(post_service.base_url).host]
        monkeypatch.setattr(
            host_config, 'retry_http_statuses_for_post', retry_http_statuses_for_post
        )

    responses = await resolve(data.post(post_service.url('/fails-once')))

    if retried:
        assert responses.to_data() == {'submission': {'accepted': True}}
        assert post_service.requests == [{'value': 1}, {'value': 1}]
    else:
        with pytest.raises(FailedDataError, match=f'HTTP status: {first_status}'):
            _ = responses['submission']
        assert post_service.requests == [{'value': 1}]


@pytest.mark.parametrize('task_is_async', [False, True], ids=['post_to_url', 'async_post_to_url'])
async def test_post_to_url_tasks(post_service: PostService, task_is_async: bool) -> None:
    data = JsonDataset({'first': {'value': 1}})
    url = post_service.url('/double')

    if task_is_async:
        responses = await async_post_to_url.run(data, url, response_cls=DoubledDataset)
    else:
        responses = await resolve(post_to_url.run(data, url, response_cls=DoubledDataset))

    assert isinstance(responses, DoubledDataset)
    assert responses.to_data() == {'first': {'doubled': 2}}


def test_post_rejects_response_cls_that_is_neither_dataset_nor_model() -> None:
    with pytest.raises(TypeError, match='"response_cls" must be a Dataset or Model class'):
        JsonDataset().post('http://localhost/data', response_cls=dict)  # pyright: ignore[reportArgumentType, reportCallIssue]
