import asyncio
from functools import partial
from typing import Annotated, cast

import aiohttp
import aiohttp.web_response
import pytest
import pytest_cases as pc

import omnipy
from omnipy import AutoResponseContentDataset, BytesDataset, Dataset, JsonDataset, Model, StrDataset
from omnipy.util.helpers import get_event_loop_and_check_if_loop_is_running

from ...helpers.functions import assert_model, assert_model_or_val
from ...helpers.protocols import AssertModelOrValFunc
from .helpers.classes import EndpointCase, RequestTypeCase


def _assert_query_results(assert_model_if_dyn_conv_else_val,
                          case: RequestTypeCase,
                          data: Dataset,
                          auto_model_type: type[Model]):
    assert isinstance(data, case.dataset_cls)
    model_cls = case.dataset_cls.get_model_class(
    ) if case.dataset_cls != AutoResponseContentDataset else auto_model_type
    match model_cls:
        case omnipy.BytesModel | omnipy.StrictBytesModel:
            _assert_bytes_query_results(assert_model, cast(BytesDataset, data))
        case omnipy.StrModel | omnipy.StrictStrModel:
            _assert_str_query_results(assert_model, cast(StrDataset, data))
        case omnipy.JsonModel | omnipy.JsonDictModel:
            _assert_json_query_results(assert_model_if_dyn_conv_else_val, cast(JsonDataset, data))
        case _:
            raise RuntimeError(f'Unknown model: "{model_cls.__name__}"')


def _assert_bytes_query_results(assert_model, data: BytesDataset):
    assert_model_or_val(data['jokke'][-10:], bytes | str, b'f\\u00e5"]}')
    assert_model_or_val(data['odd'][-10:], bytes | str, b'5 drite"]}')
    assert_model_or_val(data['delillos'][-10:], bytes | str, b'ttifire"]}')
    assert_model_or_val(data['delillos_2'][-10:], bytes | str, b'n\\u00f8"]}')


def _assert_str_query_results(assert_model, data: StrDataset):
    assert_model_or_val(data['jokke'][-10:], str | bytes, 'f\\u00e5"]}')
    assert_model_or_val(data['odd'][-10:], str | bytes, '5 drite"]}')
    assert_model_or_val(data['delillos'][-10:], str | bytes, 'ttifire"]}')
    assert_model_or_val(data['delillos_2'][-10:], str | bytes, 'n\\u00f8"]}')


def _assert_json_query_results(assert_model_if_dyn_conv_else_val, data: JsonDataset):
    assert_model_or_val(data['jokke']['author'], str, 'Joachim Nielsen')
    assert_model_or_val(data['jokke']['lyrics'][0], str, "Her kommer vinter'n")
    assert_model_or_val(data['odd']['author'], str, 'Odd Børretzen')
    assert_model_or_val(data['odd']['lyrics'][0], str, 'Jeg så min første blues')
    assert_model_or_val(data['delillos']['author'], str, 'deLillos')
    assert_model_or_val(data['delillos']['lyrics'][0], str, 'Og en fyr lå i senga mi')
    assert_model_or_val(data['delillos_2']['author'], str, 'deLillos')
    assert_model_or_val(data['delillos_2']['lyrics'][0], str, 'Joda sier Arne')


@pc.parametrize_with_cases('case', cases='.cases.request_types')
async def test_get_from_api_endpoint_without_session(
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
    has_tag='supports_external_session',
)
async def test_get_from_api_endpoint_with_session(
    endpoint: Annotated[EndpointCase, pytest.fixture],
    assert_model_if_dyn_conv_else_val: Annotated[AssertModelOrValFunc, pytest.fixture],
    case: RequestTypeCase,
) -> None:

    async with aiohttp.ClientSession() as client_session:
        task1 = case.job.run(endpoint.query_urls[:2], client_session=client_session)
        task2 = case.job.run(endpoint.query_urls[2:], client_session=client_session)
        results = await asyncio.gather(task1, task2)
        data = results[0] | results[1]

    _assert_query_results(assert_model_if_dyn_conv_else_val, case, data, endpoint.auto_model_type)
