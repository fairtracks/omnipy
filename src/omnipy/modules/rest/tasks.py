import aiohttp

from ... import TaskTemplate
from ..json.models import JsonModel
from .models import HttpUrlModel


@TaskTemplate(iterate_over_data_files=True)
async def get_json_from_api_endpoint(url: HttpUrlModel) -> JsonModel:
    async with aiohttp.ClientSession() as session:
        async with session.get(str(url)) as response:
            if response.status != 200:
                raise ConnectionError(f'Failed to get data from {url}')
            return JsonModel(await response.json())
