from typing import AsyncGenerator

from aiohttp import ClientResponse, ClientSession

from ... import BytesDataset, BytesModel, JsonDataset, StrDataset, StrModel, TaskTemplate
from ..json.models import JsonModel
from .models import HttpUrlModel


async def _call_get(url: HttpUrlModel,
                    session: ClientSession) -> AsyncGenerator[ClientResponse, None]:
    async with session.get(str(url)) as response:
        if response.status != 200:
            raise ConnectionError(f'Failed to get data from {url}')
        yield response


async def _ensure_session(session: ClientSession | None) -> AsyncGenerator[ClientSession, None]:
    if session:
        yield session
    else:
        async with ClientSession() as tmp_session:
            yield tmp_session


@TaskTemplate(iterate_over_data_files=True, output_dataset_cls=JsonDataset)
async def get_json_from_api_endpoint(
    url: HttpUrlModel,
    session: ClientSession | None = None,
) -> JsonModel:
    async for session in _ensure_session(session):
        async for response in _call_get(url, session):
            return JsonModel(await response.json(content_type=None))


@TaskTemplate(iterate_over_data_files=True, output_dataset_cls=StrDataset)
async def get_str_from_api_endpoint(
    url: HttpUrlModel,
    session: ClientSession | None = None,
) -> StrModel:
    async for session in _ensure_session(session):
        async for response in _call_get(url, session):
            return StrModel(await response.text())


@TaskTemplate(iterate_over_data_files=True, output_dataset_cls=BytesDataset)
async def get_bytes_from_api_endpoint(
    url: HttpUrlModel,
    session: ClientSession | None = None,
) -> BytesModel:
    async for session in _ensure_session(session):
        async for response in _call_get(url, session):
            return BytesModel(await response.read())
