from typing import AsyncGenerator, cast

from aiohttp import ClientResponse, ClientSession
from aiohttp_retry import ExponentialRetry, FibonacciRetry, JitterRetry, RandomRetry, RetryClient

from omnipy.api.enums import BackoffStrategy
from omnipy.compute.task import TaskTemplate

from ..json.datasets import JsonDataset
from ..json.models import JsonModel
from ..raw.datasets import BytesDataset, StrDataset
from ..raw.models import BytesModel, StrModel
from .models import HttpUrlModel

DEFAULT_RETRIES = 5
DEFAULT_BACKOFF_STRATEGY = BackoffStrategy.EXPONENTIAL
DEFAULT_RETRY_STATUSES = (408, 425, 429, 500, 502, 503, 504)

BACKOFF_STRATEGY_2_RETRY_CLS = {
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

    retry_cls = BACKOFF_STRATEGY_2_RETRY_CLS[retry_backoff_strategy]
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
            return JsonModel(await response.json(content_type=None))


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
            return StrModel(await response.text())


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
            return BytesModel(await response.read())
