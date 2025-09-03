import asyncio
from dataclasses import dataclass
from pathlib import Path
from typing import AsyncGenerator, cast, TYPE_CHECKING

from typing_extensions import TypeVar

from omnipy.compute.task import TaskTemplate
from omnipy.data.dataset import Dataset
from omnipy.data.model import Model
from omnipy.shared.enums.data import BackoffStrategy

from ..json.datasets import JsonDataset, JsonListOfDictsDataset
from ..json.models import JsonModel
from ..raw.datasets import BytesDataset, StrDataset
from ..raw.models import BytesModel, StrModel
from .constants import DEFAULT_BACKOFF_STRATEGY, DEFAULT_RETRIES, DEFAULT_RETRY_STATUSES
from .datasets import AutoResponseContentDataset, HttpUrlDataset
from .models import AutoResponseContentModel, HttpUrlModel, ResponseContentPydModel

if TYPE_CHECKING:
    from .lazy_import import ClientResponse, ClientSession, RetryClient

_JsonDatasetT = TypeVar('_JsonDatasetT', bound=Dataset)


async def _call_get(url: HttpUrlModel,
                    session: 'ClientSession') -> 'AsyncGenerator[ClientResponse, None]':
    async with session.get(str(url)) as response:
        if response.status != 200:
            raise ConnectionError(f'Failed to get data from {url}')
        yield response


def _get_retry_client(
    client_session: 'ClientSession | None',
    retry_http_statuses: tuple[int, ...],
    retry_attempts: int,
    retry_backoff_strategy: BackoffStrategy.Literals,
) -> 'RetryClient':
    from .helpers import BACKOFF_STRATEGY_2_RETRY_CLS
    from .lazy_import import RetryClient

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
    client_session: 'ClientSession | None',
    retry_http_statuses: tuple[int, ...],
    retry_attempts: int,
    retry_backoff_strategy: BackoffStrategy.Literals,
) -> 'AsyncGenerator[RetryClient, None]':
    from .lazy_import import ClientSession

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
    client_session: 'ClientSession | None' = None,
    retry_http_statuses: tuple[int, ...] = DEFAULT_RETRY_STATUSES,
    retry_attempts: int = DEFAULT_RETRIES,
    retry_backoff_strategy: BackoffStrategy.Literals = DEFAULT_BACKOFF_STRATEGY,
) -> JsonModel:
    from .lazy_import import ClientSession

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
    client_session: 'ClientSession | None' = None,
    retry_http_statuses: tuple[int, ...] = DEFAULT_RETRY_STATUSES,
    retry_attempts: int = DEFAULT_RETRIES,
    retry_backoff_strategy: BackoffStrategy.Literals = DEFAULT_BACKOFF_STRATEGY,
) -> StrModel:
    from .lazy_import import ClientSession

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
    client_session: 'ClientSession | None' = None,
    retry_http_statuses: tuple[int, ...] = DEFAULT_RETRY_STATUSES,
    retry_attempts: int = DEFAULT_RETRIES,
    retry_backoff_strategy: BackoffStrategy.Literals = DEFAULT_BACKOFF_STRATEGY,
) -> BytesModel:
    from .lazy_import import ClientSession

    async for retry_session in _ensure_retry_session(
            client_session,
            retry_http_statuses,
            retry_attempts,
            retry_backoff_strategy,
    ):
        async for response in _call_get(url, cast(ClientSession, retry_session)):
            output_data = BytesModel(await response.read())
    return output_data


@TaskTemplate(iterate_over_data_files=True, output_dataset_cls=AutoResponseContentDataset)
async def get_auto_from_api_endpoint(
    url: HttpUrlModel,
    client_session: 'ClientSession | None' = None,
    retry_http_statuses: tuple[int, ...] = DEFAULT_RETRY_STATUSES,
    retry_attempts: int = DEFAULT_RETRIES,
    retry_backoff_strategy: BackoffStrategy.Literals = DEFAULT_BACKOFF_STRATEGY,
    as_mime_type: str | None = None,
) -> AutoResponseContentModel:
    from .lazy_import import ClientSession, CONTENT_TYPE

    async for retry_session in _ensure_retry_session(
            client_session,
            retry_http_statuses,
            retry_attempts,
            retry_backoff_strategy,
    ):
        async for response in _call_get(url, cast(ClientSession, retry_session)):
            if as_mime_type:
                content_type = content_type_header = as_mime_type
            else:
                assert CONTENT_TYPE in response.headers
                content_type_header = response.headers[CONTENT_TYPE]
                content_type = response.content_type
            match content_type:
                case 'application/json':
                    content = await response.json(content_type=None)
                case 'text/plain':
                    content = await response.text()
                case 'application/octet-stream' | _:
                    content = await response.read()

    model = AutoResponseContentModel(
        ResponseContentPydModel(content_type=content_type_header, response=content))
    return model


@TaskTemplate()
def load_urls_into_new_dataset(
    urls: HttpUrlDataset,
    dataset_cls: type[_JsonDatasetT] = JsonDataset,
    as_mime_type: str | None = None,
) -> _JsonDatasetT:
    return dataset_cls.load(urls, as_mime_type=as_mime_type)


@TaskTemplate()
async def async_load_urls_into_new_dataset(
    urls: HttpUrlDataset,
    dataset_cls: type[_JsonDatasetT] = JsonDataset,
    as_mime_type: str | None = None,
) -> _JsonDatasetT:
    return await dataset_cls.load(urls, as_mime_type=as_mime_type)


@dataclass
class GithubRepoContext:
    owner: str
    repo: str
    branch: str
    path: str | Path


@TaskTemplate()
def get_github_repo_urls(
    owner: str,
    repo: str,
    branch: str,
    path: str | Path,
    file_suffix: str | None = None,
) -> HttpUrlDataset:

    repo_context = GithubRepoContext(owner=owner, repo=repo, branch=branch, path=path)

    if file_suffix:
        return _get_urls_for_files_in_dir_with_suffix(repo_context, file_suffix)
    else:
        return _get_url_for_single_file(repo_context)


def _get_urls_for_files_in_dir_with_suffix(ctx: GithubRepoContext, file_suffix: str):
    api_url = _create_api_url_for_file_list(ctx)
    file_list = cast(JsonListOfDictsDataset, JsonListOfDictsDataset.load(api_url))
    return _create_url_dataset_for_files_with_suffix(file_list, file_suffix, ctx)


@TaskTemplate()
async def async_get_github_repo_urls(
    owner: str,
    repo: str,
    branch: str,
    path: str | Path,
    file_suffix: str | None = None,
) -> HttpUrlDataset:

    repo_context = GithubRepoContext(owner=owner, repo=repo, branch=branch, path=path)

    if file_suffix:
        return await _async_get_urls_for_files_in_dir_with_suffix(repo_context, file_suffix)
    else:
        return _get_url_for_single_file(repo_context)


async def _async_get_urls_for_files_in_dir_with_suffix(ctx: GithubRepoContext, file_suffix: str):
    api_url = _create_api_url_for_file_list(ctx)
    file_list = await cast(asyncio.Task[JsonListOfDictsDataset],
                           JsonListOfDictsDataset.load(api_url))
    return _create_url_dataset_for_files_with_suffix(file_list, file_suffix, ctx)


def _create_api_url_for_file_list(ctx: GithubRepoContext) -> HttpUrlModel:
    api_url = HttpUrlModel('https://api.github.com')
    api_url.path // 'repos' // ctx.owner // ctx.repo // 'contents' // ctx.path
    api_url.query['ref'] = ctx.branch
    return api_url


def _create_url_dataset_for_files_with_suffix(
    file_list: JsonListOfDictsDataset,
    file_suffix: str,
    ctx: GithubRepoContext,
):
    url_prefix = _get_url_prefix_for_download(ctx)
    names = Model[list[str]]([f['name'] for f in file_list[0] if f['name'].endswith(file_suffix)])
    return HttpUrlDataset({name: f'{url_prefix}/{name}' for name in names})


def _get_url_prefix_for_download(ctx: GithubRepoContext):
    url_pre = HttpUrlModel('https://raw.githubusercontent.com')
    url_pre.path // ctx.owner // ctx.repo // ctx.branch // ctx.path
    return url_pre


def _get_url_for_single_file(repo_context):
    url_pre = _get_url_prefix_for_download(repo_context)
    name = url_pre.path.name
    return HttpUrlDataset({name: url_pre})
