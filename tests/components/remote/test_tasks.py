import asyncio
from typing import Annotated, cast

import aiohttp
import aiohttp.web_response
import pytest
import pytest_cases as pc

import omnipy
from omnipy import (AutoResponseContentsDataset,
                    BytesDataset,
                    Dataset,
                    JsonDataset,
                    Model,
                    StrDataset)

from ...helpers.functions import assert_model
from ...helpers.protocols import AssertModelOrValFunc
from .cases.request_types import RequestTypeCase
from .conftest import EndpointCase


def _assert_query_results(assert_model_if_dyn_conv_else_val,
                          case: RequestTypeCase,
                          data: Dataset,
                          auto_model_type: type[Model]):
    assert isinstance(data, case.dataset_cls)
    match case.dataset_cls if case.dataset_cls != AutoResponseContentsDataset else auto_model_type:
        case omnipy.BytesDataset:
            _assert_bytes_query_results(assert_model, cast(BytesDataset, data))
        case omnipy.StrDataset:
            _assert_str_query_results(assert_model, cast(StrDataset, data))
        case omnipy.JsonDataset | omnipy.JsonDictDataset:
            _assert_json_query_results(assert_model_if_dyn_conv_else_val, cast(JsonDataset, data))


def _assert_bytes_query_results(assert_model, data: BytesDataset):
    assert_model(data['jokke'][-10:], bytes | str, b'f\\u00e5"]}')
    assert_model(data['odd'][-10:], bytes | str, b'5 drite"]}')
    assert_model(data['delillos'][-10:], bytes | str, b'ttifire"]}')
    assert_model(data['delillos_2'][-10:], bytes | str, b'n\\u00f8"]}')


def _assert_str_query_results(assert_model, data: StrDataset):
    assert_model(data['jokke'][-10:], str | bytes, 'f\\u00e5"]}')
    assert_model(data['odd'][-10:], str | bytes, '5 drite"]}')
    assert_model(data['delillos'][-10:], str | bytes, 'ttifire"]}')
    assert_model(data['delillos_2'][-10:], str | bytes, 'n\\u00f8"]}')


def _assert_json_query_results(assert_model_if_dyn_conv_else_val, data: JsonDataset):
    assert_model_if_dyn_conv_else_val(data['jokke']['author'], str, 'Joachim Nielsen')
    assert_model_if_dyn_conv_else_val(data['jokke']['lyrics'][0], str, "Her kommer vinter'n")
    assert_model_if_dyn_conv_else_val(data['odd']['author'], str, 'Odd Børretzen')
    assert_model_if_dyn_conv_else_val(data['odd']['lyrics'][0], str, 'Jeg så min første blues')
    assert_model_if_dyn_conv_else_val(data['delillos']['author'], str, 'deLillos')
    assert_model_if_dyn_conv_else_val(data['delillos']['lyrics'][0], str, 'Og en fyr lå i senga mi')
    assert_model_if_dyn_conv_else_val(data['delillos_2']['author'], str, 'deLillos')
    assert_model_if_dyn_conv_else_val(data['delillos_2']['lyrics'][0], str, 'Joda sier Arne')


@pc.parametrize_with_cases('case', cases='.cases.request_types')
async def test_get_from_api_endpoint_without_session(
    endpoint: Annotated[EndpointCase, pytest.fixture],
    assert_model_if_dyn_conv_else_val: Annotated[AssertModelOrValFunc, pytest.fixture],
    case: RequestTypeCase,
) -> None:
    if case.is_async:
        data = await case.job.run(endpoint.query_urls, **case.kwargs)
    else:
        data = case.job.run(endpoint.query_urls, **case.kwargs)
    _assert_query_results(assert_model_if_dyn_conv_else_val, case, data, endpoint.auto_model_type)


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
