from typing import AsyncGenerator, cast

from aiohttp import ClientResponse, ClientSession
from aiohttp_retry import ExponentialRetry, FibonacciRetry, JitterRetry, RandomRetry, RetryClient
from typing_extensions import TypeVar

from omnipy.compute.task import TaskTemplate
from omnipy.data.dataset import Dataset
from omnipy.shared.enums import BackoffStrategy

from ..json.datasets import JsonDataset
from ..json.models import JsonModel
from ..raw.datasets import BytesDataset, StrDataset
from ..raw.models import BytesModel, StrModel
from .constants import DEFAULT_BACKOFF_STRATEGY, DEFAULT_RETRIES, DEFAULT_RETRY_STATUSES
from .datasets import HttpUrlDataset
from .models import HttpUrlModel

_JsonDatasetT = TypeVar('_JsonDatasetT', bound=Dataset)

_BACKOFF_STRATEGY_2_RETRY_CLS = {
    BackoffStrategy.EXPONENTIAL: ExponentialRetry,
    BackoffStrategy.JITTER: JitterRetry,
    BackoffStrategy.FIBONACCI: FibonacciRetry,
    BackoffStrategy.RANDOM: RandomRetry,
}


async def _call_get(url: HttpUrlModel,
                    session: ClientSession) -> AsyncGenerator[ClientResponse, None]:
    async with session.get(str(url)) as response:
        if response.status != 200:
            raise ConnectionError(f'Failed to get data from {url}')
        yield response


def _get_retry_client(
    client_session: ClientSession | None,
    retry_http_statuses: tuple[int, ...],
    retry_attempts: int,
    retry_backoff_strategy: BackoffStrategy,
) -> RetryClient:

    retry_cls = _BACKOFF_STRATEGY_2_RETRY_CLS[retry_backoff_strategy]
    retry_options = retry_cls(
        attempts=retry_attempts,
        statuses=retry_http_statuses,
        retry_all_server_errors=False,
    )
    return RetryClient(
        client_session=client_session,
        retry_options=retry_options,
    )


async def _ensure_retry_session(
    client_session: ClientSession | None,
    retry_http_statuses: tuple[int, ...],
    retry_attempts: int,
    retry_backoff_strategy: BackoffStrategy,
) -> AsyncGenerator[RetryClient, None]:
    if client_session:
        yield _get_retry_client(
            client_session,
            retry_http_statuses,
            retry_attempts,
            retry_backoff_strategy,
        )
    else:
        async with ClientSession() as tmp_session:
            yield _get_retry_client(
                tmp_session,
                retry_http_statuses,
                retry_attempts,
                retry_backoff_strategy,
            )


@TaskTemplate(iterate_over_data_files=True, output_dataset_cls=JsonDataset)
async def get_json_from_api_endpoint(
    url: HttpUrlModel,
    client_session: ClientSession | None = None,
    retry_http_statuses: tuple[int, ...] = DEFAULT_RETRY_STATUSES,
    retry_attempts: int = DEFAULT_RETRIES,
    retry_backoff_strategy: BackoffStrategy = DEFAULT_BACKOFF_STRATEGY,
) -> JsonModel:
    async for retry_session in _ensure_retry_session(
            client_session,
            retry_http_statuses,
            retry_attempts,
            retry_backoff_strategy,
    ):
        async for response in _call_get(url, cast(ClientSession, retry_session)):
            output_data = JsonModel(await response.json(content_type=None))
    return output_data


@TaskTemplate(iterate_over_data_files=True, output_dataset_cls=StrDataset)
async def get_str_from_api_endpoint(
    url: HttpUrlModel,
    client_session: ClientSession | None = None,
    retry_http_statuses: tuple[int, ...] = DEFAULT_RETRY_STATUSES,
    retry_attempts: int = DEFAULT_RETRIES,
    retry_backoff_strategy: BackoffStrategy = DEFAULT_BACKOFF_STRATEGY,
) -> StrModel:
    async for retry_session in _ensure_retry_session(
            client_session,
            retry_http_statuses,
            retry_attempts,
            retry_backoff_strategy,
    ):
        async for response in _call_get(url, cast(ClientSession, retry_session)):
            output_data = StrModel(await response.text())
    return output_data


@TaskTemplate(iterate_over_data_files=True, output_dataset_cls=BytesDataset)
async def get_bytes_from_api_endpoint(
    url: HttpUrlModel,
    client_session: ClientSession | None = None,
    retry_http_statuses: tuple[int, ...] = DEFAULT_RETRY_STATUSES,
    retry_attempts: int = DEFAULT_RETRIES,
    retry_backoff_strategy: BackoffStrategy = DEFAULT_BACKOFF_STRATEGY,
) -> BytesModel:
    async for retry_session in _ensure_retry_session(
            client_session,
            retry_http_statuses,
            retry_attempts,
            retry_backoff_strategy,
    ):
        async for response in _call_get(url, cast(ClientSession, retry_session)):
            output_data = BytesModel(await response.read())
    return output_data


@TaskTemplate()
async def async_load_urls_into_new_dataset(
    urls: HttpUrlDataset,
    dataset_cls: type[_JsonDatasetT] = JsonDataset,
) -> _JsonDatasetT:
    dataset = dataset_cls()
    await dataset.load(urls)
    return dataset


@TaskTemplate()
def load_urls_into_new_dataset(
    urls: HttpUrlDataset,
    dataset_cls: type[_JsonDatasetT] = JsonDataset,
) -> _JsonDatasetT:
    dataset = dataset_cls()
    dataset.load(urls)
    return dataset
