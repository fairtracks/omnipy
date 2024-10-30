import asyncio
from typing import Annotated, AsyncGenerator

import aiohttp
from aiohttp import web
import pytest
import pytest_cases as pc

from helpers.protocols import AssertModelOrValFunc
from modules.remote.cases.request_types import RequestTypeCase
import omnipy
from omnipy import Dataset, JsonDataset
from omnipy.api.exceptions import ShouldNotOccurException
from omnipy.modules.remote.datasets import HttpUrlDataset
from omnipy.modules.remote.models import HttpUrlModel


async def lyrics_endpoint(request: web.Request) -> web.Response:
    url = HttpUrlModel(str(request.url))
    match url.query.get('song'):
        case 'Her kommer vinteren':
            data = dict(
                author='Joachim Nielsen',
                lyrics=[
                    "Her kommer vinter'n",
                    'Her kommer den kalde fine tida',
                    "Her kommer vinter'n",
                    'Endelig fred å få',
                ])
        case 'Blues fra Oslo Ø':
            data = dict(
                author='Odd Børretzen',
                lyrics=[
                    'Jeg så min første blues',
                    'på veggen på do',
                    'herrer',
                    'ned trappa',
                    'under perrong fem',
                    'Der sto det:',
                    "Arbe' og slite",
                    'tjene lite',
                    'og 25 øre for å drite',
                ])
        case '1984':
            data = dict(
                author='deLillos',
                lyrics=[
                    'Og en fyr lå i senga mi',
                    'Og det var kaldt',
                    'Den kaldeste dagen',
                    'Overalt',
                    'Den kaldeste dagen i Nittenåttifire',
                ])
        case 'Arne':
            data = dict(
                author='deLillos',
                lyrics=[
                    'Joda sier Arne',
                    'Det er vel og bra det',
                    'Men jeg lever til jeg dør',
                    'Faen som det regner ute',
                    'Jeg lurer på om det er i natt det begynner å snø',
                ])

    return web.json_response(data)


def create_app() -> web.Application:
    app = web.Application()
    app.router.add_route('GET', '/lyrics', lyrics_endpoint)
    return app


@pytest.fixture(scope='function')
async def lyrics_server_url(aiohttp_server) -> AsyncGenerator[str, None]:
    server = await aiohttp_server(create_app())
    server_url = server.make_url('/lyrics')
    yield str(server_url)


@pytest.fixture(scope='function')
def query_urls(lyrics_server_url: Annotated[str, pytest.fixture]) -> HttpUrlDataset:
    urls = HttpUrlDataset()
    for key, song in dict(jokke='Her kommer vinteren', odd='Blues fra Oslo Ø',
                          delillos='1984', delillos_2='Arne').items():
        urls[key] = HttpUrlModel(str(lyrics_server_url))
        urls[key].query['song'] = song
    return urls


def _assert_query_results(assert_model_if_dyn_conv_else_val, case: RequestTypeCase, data: Dataset):
    assert isinstance(data, case.dataset_cls)
    match case.dataset_cls:
        case omnipy.StrDataset | omnipy.BytesDataset:
            json_data = JsonDataset()
            json_data.from_json(data.to_data())
        case omnipy.JsonDataset:
            json_data = data
        case _:
            raise ShouldNotOccurException()

    _assert_json_query_results(assert_model_if_dyn_conv_else_val, json_data)


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
    query_urls: Annotated[HttpUrlDataset, pytest.fixture],
    assert_model_if_dyn_conv_else_val: Annotated[AssertModelOrValFunc, pytest.fixture],
    case: RequestTypeCase,
) -> None:
    data = await case.job.run(query_urls, **case.kwargs)
    _assert_query_results(assert_model_if_dyn_conv_else_val, case, data)


@pc.parametrize_with_cases('case', cases='.cases.request_types')
async def test_get_from_api_endpoint_with_session(
    query_urls: Annotated[HttpUrlDataset, pytest.fixture],
    assert_model_if_dyn_conv_else_val: Annotated[AssertModelOrValFunc, pytest.fixture],
    case: RequestTypeCase,
) -> None:

    async with aiohttp.ClientSession() as session:
        task1 = case.job.run(query_urls[:2], session=session)
        task2 = case.job.run(query_urls[2:], session=session)
        results = await asyncio.gather(task1, task2)
        data = results[0] | results[1]

    _assert_query_results(assert_model_if_dyn_conv_else_val, case, data)
