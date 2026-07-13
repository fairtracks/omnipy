"""Tests for remote request tasks."""

import asyncio
from functools import partial
from typing import Annotated, Any, cast

import aiohttp
from aiohttp import web
import pytest
import pytest_cases as pc

import omnipy
from omnipy import (AutoResponseContentDataset,
                    Dataset,
                    JsonDictOfListsDataset,
                    Model,
                    StrictBytesDataset,
                    StrictStrDataset)
from omnipy.components.remote.tasks import (get_auto_from_api_endpoint,
                                            get_bytes_from_api_endpoint,
                                            get_json_from_api_endpoint,
                                            get_retry_client,
                                            get_str_from_api_endpoint)
from omnipy.shared.exceptions import FailedDataError
from omnipy.util.helpers import get_event_loop_and_check_if_loop_is_running

from ...helpers.functions import assert_model_or_val, assert_val
from ...helpers.protocols import AssertModelOrValFunc
from .helpers.classes import EndpointCase, RequestTypeCase


@pytest.fixture(scope='function')
async def always_failing_server_url(aiohttp_server):
    async def _always_failing_endpoint(request: web.Request) -> web.Response:
        return web.Response(text='Error', status=503)

    app = web.Application()
    app.router.add_route('GET', '/always_fails', _always_failing_endpoint)
    server = await aiohttp_server(app)
    yield str(server.make_url('/always_fails'))


@pytest.fixture(scope='function')
async def fails_once_then_succeeds_server_url(aiohttp_server):
    request_count = 0

    async def _flaky_endpoint(request: web.Request) -> web.Response:
        nonlocal request_count
        request_count += 1

        if request_count == 1:
            return web.Response(text='Error', status=503)

        return web.json_response(dict(author='Recovered Artist', lyrics=['Recovered line']))

    app = web.Application()
    app.router.add_route('GET', '/fails_once', _flaky_endpoint)
    server = await aiohttp_server(app)
    yield str(server.make_url('/fails_once'))


async def _run_get_json_with_retry_attempts(url: str, retry_attempts: int):
    query_urls = omnipy.HttpUrlDataset({'flaky': omnipy.HttpUrlModel(url)})

    async with aiohttp.ClientSession() as client_session:
        async with get_retry_client(
                client_session=client_session,
                retry_http_statuses=(503,),
                retry_attempts=retry_attempts,
        ) as retry_client:
            return cast(
                Any,
                await
                get_json_from_api_endpoint.run(cast(Any, query_urls), retry_client=retry_client))


async def test_get_retry_client_with_single_attempt_fails_after_initial_503(
        fails_once_then_succeeds_server_url: str) -> None:
    output = await _run_get_json_with_retry_attempts(
        fails_once_then_succeeds_server_url, retry_attempts=1)
    output_any = cast(Any, output)

    with pytest.raises(FailedDataError, match='HTTP status: 503'):
        _ = output_any['flaky']['author']


async def test_get_retry_client_with_second_attempt_recovers_after_initial_503(
        fails_once_then_succeeds_server_url: str) -> None:
    output = await _run_get_json_with_retry_attempts(
        fails_once_then_succeeds_server_url, retry_attempts=2)
    output_any = cast(Any, output)
    assert_model_or_val(output_any['flaky']['author'], str, 'Recovered Artist')


@pytest.mark.parametrize(
    'task',
    [
        get_json_from_api_endpoint,
        get_str_from_api_endpoint,
        get_bytes_from_api_endpoint,
        get_auto_from_api_endpoint,
    ],
    ids=['json', 'str', 'bytes', 'auto'],
)
async def test_get_from_api_endpoint_run_raises_for_non_200_response(
    always_failing_server_url: str,
    task: Any,
) -> None:
    query_urls = omnipy.HttpUrlDataset({'failing': omnipy.HttpUrlModel(always_failing_server_url)})

    async with aiohttp.ClientSession() as client_session:
        async with get_retry_client(
                client_session=client_session,
                retry_http_statuses=(),
                retry_attempts=1,
        ) as retry_client:
            output = await task.run(query_urls, retry_client=retry_client)

    with pytest.raises(FailedDataError, match='HTTP status: 503') as exc_info:
        _ = output['failing']

    assert 'always_fails' in str(exc_info.value)


def _assert_query_results(assert_model_if_dyn_conv_else_val,
                          case: RequestTypeCase,
                          data: Dataset,
                          auto_model_type: type[Model]):
    """Assert remote query results for the requested dataset type."""
    assert isinstance(data, case.dataset_cls)
    _type = case.dataset_cls.get_type(
    ) if case.dataset_cls != AutoResponseContentDataset else auto_model_type
    match _type:
        case omnipy.BytesModel | omnipy.StrictBytesModel:
            _assert_bytes_query_results(cast(StrictBytesDataset, data))
        case omnipy.StrModel | omnipy.StrictStrModel:
            _assert_str_query_results(cast(StrictStrDataset, data))
        case omnipy.JsonModel | omnipy.JsonDictModel:
            _assert_json_query_results(cast(JsonDictOfListsDataset, data))
        case _:
            raise RuntimeError(f'Unknown model: "{_type.__name__}"')


def _assert_bytes_query_results(data: StrictBytesDataset):
    """Assert the trailing bytes content for each lyrics response."""
    assert_val(data['jokke'].content[-10:], bytes | str, b'f\\u00e5"]}')
    assert_val(data['odd'].content[-10:], bytes | str, b'5 drite"]}')
    assert_val(data['delillos'].content[-10:], bytes | str, b'ttifire"]}')
    assert_val(data['delillos_2'].content[-10:], bytes | str, b'n\\u00f8"]}')


def _assert_str_query_results(data: StrictStrDataset):
    """Assert the trailing text content for each lyrics response."""
    assert_val(data['jokke'].content[-10:], str | bytes, 'f\\u00e5"]}')
    assert_val(data['odd'].content[-10:], str | bytes, '5 drite"]}')
    assert_val(data['delillos'].content[-10:], str | bytes, 'ttifire"]}')
    assert_val(data['delillos_2'].content[-10:], str | bytes, 'n\\u00f8"]}')


def _assert_json_query_results(data: JsonDictOfListsDataset):
    """Assert the parsed JSON content for each lyrics response."""
    assert_model_or_val(data['jokke']['author'], str, 'Joachim Nielsen')
    assert_model_or_val(data['jokke']['lyrics'][0], str, "Her kommer vinter'n")
    assert_model_or_val(data['odd']['author'], str, 'Odd Børretzen')
    assert_model_or_val(data['odd']['lyrics'][0], str, 'Jeg så min første blues')
    assert_model_or_val(data['delillos']['author'], str, 'deLillos')
    assert_model_or_val(data['delillos']['lyrics'][0], str, 'Og en fyr lå i senga mi')
    assert_model_or_val(data['delillos_2']['author'], str, 'deLillos')
    assert_model_or_val(data['delillos_2']['lyrics'][0], str, 'Joda sier Arne')


@pc.parametrize_with_cases('case', cases='.cases.request_types')
async def test_get_from_api_endpoint_without_retry_client(
    endpoint: Annotated[EndpointCase, pytest.fixture],
    assert_model_if_dyn_conv_else_val: Annotated[AssertModelOrValFunc, pytest.fixture],
    case: RequestTypeCase,
) -> None:
    if case.is_async:
        data = await case.job.run(endpoint.query_urls, **case.kwargs)
    else:
        # Need to run synchronous job in thread to simulate a synchronous
        # environment, while the async endpoints continue to serve requests
        # in the event loop.
        loop, loop_is_running = get_event_loop_and_check_if_loop_is_running()
        assert loop_is_running
        assert loop

        run_func = partial(case.job.run, endpoint.query_urls, **case.kwargs)
        data = await loop.run_in_executor(None, run_func)
    if case.expected_exceptions:
        with pytest.raises(case.expected_exceptions):
            _assert_query_results(
                assert_model_if_dyn_conv_else_val,
                case,
                data,
                endpoint.auto_model_type,
            )
    else:
        _assert_query_results(
            assert_model_if_dyn_conv_else_val,
            case,
            data,
            endpoint.auto_model_type,
        )


@pc.parametrize_with_cases(
    'case',
    cases='.cases.request_types',
    has_tag='supports_external_retry_client',
)
async def test_get_from_api_endpoint_with_retry_client(
    endpoint: Annotated[EndpointCase, pytest.fixture],
    assert_model_if_dyn_conv_else_val: Annotated[AssertModelOrValFunc, pytest.fixture],
    case: RequestTypeCase,
) -> None:
    """Test fetching remote endpoint data with a shared client session."""

    async with aiohttp.ClientSession() as client_session:
        async with get_retry_client(client_session=client_session) as retry_client:
            task1 = case.job.run(endpoint.query_urls[:2], retry_client=retry_client)
            task2 = case.job.run(endpoint.query_urls[2:], retry_client=retry_client)
            results = await asyncio.gather(task1, task2)
            data = results[0] | results[1]

    _assert_query_results(assert_model_if_dyn_conv_else_val, case, data, endpoint.auto_model_type)
