import asyncio
from collections import defaultdict
from json import dumps
import random
from typing import Annotated, AsyncGenerator

from aiohttp import web
from aiohttp.test_utils import TestServer
from attr import dataclass
import pytest_cases as pc

from omnipy import HttpUrlDataset, HttpUrlModel, JsonModel, Model, StrictBytesModel, StrictStrModel


async def _get_lyrics(url: str):
    url = HttpUrlModel(url)
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
    return data


async def lyrics_bytes_endpoint(request: web.Request) -> web.Response:
    data = await _get_lyrics(str(request.url))
    return web.Response(body=dumps(data).encode('utf-8'))


async def lyrics_text_endpoint(request: web.Request) -> web.Response:
    data = await _get_lyrics(str(request.url))
    return web.Response(text=dumps(data))


async def lyrics_json_endpoint(request: web.Request) -> web.Response:
    data = await _get_lyrics(str(request.url))
    return web.json_response(data)


_request_counts_per_url: defaultdict[str, int] = defaultdict(int)


async def timeout_lyrics_endpoint(request: web.Request) -> web.Response:
    global _request_counts_per_url
    url = str(request.url)
    _request_counts_per_url[url] += 1
    if _request_counts_per_url[url] % 3 == 0:
        data = await _get_lyrics(url)
        return web.json_response(data)
    else:
        await asyncio.sleep(0.01)
        return web.Response(
            text='Error',
            status=random.choice((408, 425, 429, 500, 502, 503, 504)),
        )


def create_app() -> web.Application:
    app = web.Application()
    app.router.add_route('GET', '/lyrics_bytes', lyrics_bytes_endpoint)
    app.router.add_route('GET', '/lyrics_text', lyrics_text_endpoint)
    app.router.add_route('GET', '/lyrics_json', lyrics_json_endpoint)
    app.router.add_route('GET', '/timeout_lyrics', timeout_lyrics_endpoint)
    return app


@pc.fixture(scope='function')
async def lyrics_server(aiohttp_server) -> AsyncGenerator[TestServer, None]:
    yield await aiohttp_server(create_app())


@pc.fixture(scope='function')
async def lyrics_bytes_server_url(
        lyrics_server: Annotated[TestServer, pc.fixture]) -> AsyncGenerator[str, None]:
    yield str(lyrics_server.make_url('/lyrics_bytes'))


@pc.fixture(scope='function')
async def lyrics_text_server_url(
        lyrics_server: Annotated[TestServer, pc.fixture]) -> AsyncGenerator[str, None]:
    yield str(lyrics_server.make_url('/lyrics_text'))


@pc.fixture(scope='function')
async def lyrics_json_server_url(
        lyrics_server: Annotated[TestServer, pc.fixture]) -> AsyncGenerator[str, None]:
    yield str(lyrics_server.make_url('/lyrics_json'))


@pc.fixture(scope='function')
async def timeout_lyrics_server_url(
        lyrics_server: Annotated[TestServer, pc.fixture]) -> AsyncGenerator[str, None]:
    yield str(lyrics_server.make_url('/timeout_lyrics'))


@dataclass
class EndpointCase:
    query_urls: HttpUrlDataset
    auto_model_type: type[Model]


@pc.fixture(scope='function')
@pc.parametrize(
    'server_url, auto_model_type',
    [
        (lyrics_bytes_server_url, StrictBytesModel),
        (lyrics_text_server_url, StrictStrModel),
        (lyrics_json_server_url, JsonModel),
        (timeout_lyrics_server_url, JsonModel),
    ],
    ids=['bytes_content', 'text_content', 'json_content', 'timeout_issues'])
def endpoint(server_url: str, auto_model_type: type[Model]) -> EndpointCase:
    urls = HttpUrlDataset()
    for key, song in dict(jokke='Her kommer vinteren', odd='Blues fra Oslo Ø',
                          delillos='1984', delillos_2='Arne').items():
        urls[key] = HttpUrlModel(str(server_url))
        urls[key].query['song'] = song
    return EndpointCase(query_urls=urls, auto_model_type=auto_model_type)
