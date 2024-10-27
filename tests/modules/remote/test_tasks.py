from typing import Annotated

from aiohttp import web
import pytest

from helpers.protocols import AssertModelOrValFunc
from omnipy.modules.remote.datasets import HttpUrlDataset
from omnipy.modules.remote.models import HttpUrlModel
from omnipy.modules.remote.tasks import get_json_from_api_endpoint


async def text_endpoint(request: web.Request) -> web.Response:
    url = HttpUrlModel(str(request.url))
    match url.query.get('song'):
        case 'Her kommer vinteren':
            data = dict(
                author='Joachim Nielsen',
                lyrics=[
                    "Her kommer vinter'n",
                    'Her kommer den kalde fine tida',
                    "Her kommer vinter'n",
                    'Endelig fred å få'
                ])
        case '1984':
            data = dict(
                author='deLillos',
                lyrics=[
                    'Og en fyr lå i senga mi',
                    'Og det var kaldt',
                    'Den kaldeste dagen',
                    'Overalt',
                    'Den kaldeste dagen i Nittenåttifire'
                ])

    return web.json_response(data)


def create_app() -> web.Application:
    app = web.Application()
    app.router.add_route('GET', '/lyrics', text_endpoint)
    return app


async def test_get_endpoint_json_data(
    aiohttp_server,
    assert_model_if_dyn_conv_else_val: Annotated[AssertModelOrValFunc, pytest.fixture],
) -> None:
    server = await aiohttp_server(create_app())
    server_url = server.make_url('/lyrics')

    urls = HttpUrlDataset()
    for key, song in dict(jokke='Her kommer vinteren', delillos='1984').items():
        urls[key] = HttpUrlModel(str(server_url))
        urls[key].query['song'] = song

    data = await get_json_from_api_endpoint.run(urls)

    assert_model_if_dyn_conv_else_val(data['jokke']['author'], str, 'Joachim Nielsen')
    assert_model_if_dyn_conv_else_val(data['jokke']['lyrics'][0], str, "Her kommer vinter'n")
    assert_model_if_dyn_conv_else_val(data['delillos']['author'], str, 'deLillos')
    assert_model_if_dyn_conv_else_val(data['delillos']['lyrics'][0], str, 'Og en fyr lå i senga mi')
