"""Tasks for fetching remote resources and building URL datasets."""

import asyncio
from dataclasses import dataclass
from pathlib import Path
from typing import AsyncGenerator, cast

from typing_extensions import TypeVar

from omnipy.compute.task import TaskTemplate
from omnipy.data.dataset import Dataset
from omnipy.data.model import Model
from omnipy.shared.enums.data import BackoffStrategy
from omnipy.shared.exceptions import ShouldNotOccurException
from omnipy.shared.typing import TYPE_CHECKING

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
    """Perform a GET request and yield the validated successful response.

    Args:
        url: URL to request.
        session: Active aiohttp-compatible session used to execute the request.

    Returns:
        AsyncGenerator[ClientResponse, None]: Async generator yielding one successful response.

    Raises:
        ConnectionError: If the response status code is not ``200``.

    Example:
        >>> # async for response in _call_get(HttpUrlModel('https://example.com'), session):
        >>> #     data = await response.read()
        >>> pass
    """
    async with session.get(str(url)) as response:
        yield response


def _check_response_status(response: 'ClientResponse') -> None:
    if response.status != 200:
        raise ConnectionError(f'Failed to get data. '
                              f'HTTP status: {response.status}. '
                              f'URL: {response.url}')


def get_retry_client(
    client_session: 'ClientSession | None' = None,
    retry_http_statuses: tuple[int, ...] = DEFAULT_RETRY_STATUSES,
    retry_attempts: int = DEFAULT_RETRIES,
    retry_backoff_strategy: BackoffStrategy.Literals = DEFAULT_BACKOFF_STRATEGY,
) -> 'RetryClient':
    """Build a retry-enabled HTTP client wrapper.

    Args:
        client_session: Existing client session to wrap.
        retry_http_statuses: Status codes that should trigger retries.
        retry_attempts: Maximum number of retry attempts.
        retry_backoff_strategy: Backoff strategy identifier.

    Returns:
        RetryClient: Configured retry client instance.

    Raises:
        KeyError: If ``retry_backoff_strategy`` is not registered.

    Example:
        >>> # retry_client = _get_retry_client(session, (429, 503), 5, 'exponential')
        >>> # type(retry_client).__name__
        >>> 'RetryClient'
    """
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
        retry_client: 'RetryClient | None') -> 'AsyncGenerator[RetryClient, None]':
    from .lazy_import import ClientSession

    if retry_client:
        yield retry_client
    else:
        async with ClientSession() as tmp_session:
            yield get_retry_client(tmp_session,)


@TaskTemplate(iterate_over_data_files=True, output_dataset_cls=JsonDataset)
async def get_json_from_api_endpoint(
    url: HttpUrlModel,
    retry_client: 'RetryClient | None' = None,
) -> JsonModel:
    """Fetch a JSON API endpoint and decode the response body as JSON.

    Args:
        url: HTTP URL to request.
        client_session: Optional shared aiohttp client session.
        retry_http_statuses: HTTP status codes that trigger retries.
        retry_attempts: Maximum number of retry attempts.
        retry_backoff_strategy: Backoff policy used between retries.

    Returns:
        The decoded JSON response for the requested URL.

    Raises:
        ConnectionError: If the endpoint response status is not ``200``.
        ValueError: If the response body cannot be decoded as JSON.

    Example:
        >>> # result = await get_json_from_api_endpoint(HttpUrlModel('https://api.example.com'))
        >>> # isinstance(result, JsonModel)
        >>> True
    """
    from .lazy_import import ClientSession

    async for retry_session in _ensure_retry_session(retry_client,):
        async for response in _call_get(url, cast(ClientSession, retry_session)):
            _check_response_status(response)
            return JsonModel(await response.json(content_type=None))

    raise ShouldNotOccurException('Other exception should have been raised before this point.')


@TaskTemplate(iterate_over_data_files=True, output_dataset_cls=StrDataset)
async def get_str_from_api_endpoint(
    url: HttpUrlModel,
    retry_client: 'RetryClient | None' = None,
) -> StrModel:
    """Fetch an API endpoint and decode the response body as text.

    Args:
        url: HTTP URL to request.
        client_session: Optional shared aiohttp client session.
        retry_http_statuses: HTTP status codes that trigger retries.
        retry_attempts: Maximum number of retry attempts.
        retry_backoff_strategy: Backoff policy used between retries.

    Returns:
        The response body as plain text.

    Raises:
        ConnectionError: If the endpoint response status is not ``200``.

    Example:
        >>> # text = await get_str_from_api_endpoint(HttpUrlModel('https://example.com'))
        >>> # isinstance(text, StrModel)
        >>> True
    """
    from .lazy_import import ClientSession

    async for retry_session in _ensure_retry_session(retry_client,):
        async for response in _call_get(url, cast(ClientSession, retry_session)):
            _check_response_status(response)
            return StrModel(await response.text())

    raise ShouldNotOccurException('Other exception should have been raised before this point.')


@TaskTemplate(iterate_over_data_files=True, output_dataset_cls=BytesDataset)
async def get_bytes_from_api_endpoint(
    url: HttpUrlModel,
    retry_client: 'RetryClient | None' = None,
) -> BytesModel:
    """Fetch an API endpoint and decode the response body as raw bytes.

    Args:
        url: HTTP URL to request.
        client_session: Optional shared aiohttp client session.
        retry_http_statuses: HTTP status codes that trigger retries.
        retry_attempts: Maximum number of retry attempts.
        retry_backoff_strategy: Backoff policy used between retries.

    Returns:
        The response body as bytes.

    Raises:
        ConnectionError: If the endpoint response status is not ``200``.

    Example:
        >>> # blob = await get_bytes_from_api_endpoint(HttpUrlModel('https://example.com/file'))
        >>> # isinstance(blob, BytesModel)
        >>> True
    """
    from .lazy_import import ClientSession

    async for retry_session in _ensure_retry_session(retry_client,):
        async for response in _call_get(url, cast(ClientSession, retry_session)):
            _check_response_status(response)
            return BytesModel(await response.read())

    raise ShouldNotOccurException('Other exception should have been raised before this point.')


@TaskTemplate(iterate_over_data_files=True, output_dataset_cls=AutoResponseContentDataset)
async def get_auto_from_api_endpoint(
    url: HttpUrlModel,
    retry_client: 'RetryClient | None' = None,
    as_mime_type: str | None = None,
) -> AutoResponseContentModel:
    """Fetch an API endpoint and decode the response from its MIME type.

    Args:
        url: HTTP URL to request.
        client_session: Optional shared aiohttp client session.
        retry_http_statuses: HTTP status codes that trigger retries.
        retry_attempts: Maximum number of retry attempts.
        retry_backoff_strategy: Backoff policy used between retries.
        as_mime_type: Optional MIME type override for response decoding.

    Returns:
        The response content wrapped together with its effective content type.

    Raises:
        AssertionError: If the response has no ``Content-Type`` header and no override is given.
        ConnectionError: If the endpoint response status is not ``200``.

    Example:
        >>> # data = await get_auto_from_api_endpoint(HttpUrlModel('https://example.com/data'))
        >>> # isinstance(data, AutoResponseContentModel)
        >>> True
    """
    from .lazy_import import ClientSession, CONTENT_TYPE

    async for retry_session in _ensure_retry_session(retry_client):
        async for response in _call_get(url, cast(ClientSession, retry_session)):
            _check_response_status(response)
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

    raise ShouldNotOccurException('Other exception should have been raised before this point.')


@TaskTemplate()
def load_urls_into_new_dataset(
    urls: HttpUrlDataset,
    dataset_cls: type[_JsonDatasetT] = JsonDataset,
    as_mime_type: str | None = None,
) -> _JsonDatasetT:
    """Load remote URLs into a newly created dataset instance.

    Args:
        urls: Dataset containing the URLs to load.
        dataset_cls: Dataset type to populate from the fetched content.
        as_mime_type: Optional MIME type override for response decoding.

    Returns:
        A newly loaded dataset of type ``dataset_cls``.

    Raises:
        TypeError: If fetched data cannot be parsed by ``dataset_cls``.

    Example:
        >>> # loaded = load_urls_into_new_dataset(HttpUrlDataset({'a': 'https://example.com'}))
        >>> # isinstance(loaded, JsonDataset)
        >>> True
    """
    return dataset_cls.load(urls, as_mime_type=as_mime_type)


@TaskTemplate()
async def async_load_urls_into_new_dataset(
    urls: HttpUrlDataset,
    dataset_cls: type[_JsonDatasetT] = JsonDataset,
    as_mime_type: str | None = None,
) -> _JsonDatasetT:
    """Asynchronously load remote URLs into a newly created dataset instance.

    Args:
        urls: Dataset containing the URLs to load.
        dataset_cls: Dataset type to populate from the fetched content.
        as_mime_type: Optional MIME type override for response decoding.

    Returns:
        A newly loaded dataset of type ``dataset_cls``.

    Raises:
        TypeError: If fetched data cannot be parsed by ``dataset_cls``.

    Example:
        >>> # loaded = await async_load_urls_into_new_dataset(
        >>> #     HttpUrlDataset({'a': 'https://example.com'}),
        >>> # )
        >>> # isinstance(loaded, JsonDataset)
        >>> True
    """
    return await dataset_cls.load(urls, as_mime_type=as_mime_type)


@dataclass
class GithubRepoContext:
    """Describe a GitHub repository location used for URL generation.

    Args:
        owner: GitHub repository owner or organization.
        repo: Repository name.
        branch: Branch or reference to read from.
        path: File or directory path inside the repository.

    Returns:
        GithubRepoContext: Repository context container.

    Raises:
        TypeError: If field values do not match declared types.

    Example:
        >>> ctx = GithubRepoContext('octocat', 'hello-world', 'main', 'docs')
        >>> ctx.repo
        'hello-world'
    """

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
    """Create raw GitHub content URLs for one file or matching files in a repository path.

    Args:
        owner: GitHub repository owner or organization.
        repo: Repository name.
        branch: Branch or ref to read from.
        path: File or directory path inside the repository.
        file_suffix: Optional suffix filter when ``path`` points to a directory.

    Returns:
        A dataset of raw-content URLs keyed by file name.

    Raises:
        TypeError: If any input cannot be converted to expected model types.

    Example:
        >>> # urls = get_github_repo_urls('octocat', 'hello-world', 'main', 'README.md')
        >>> # isinstance(urls, HttpUrlDataset)
        >>> True
    """

    repo_context = GithubRepoContext(owner=owner, repo=repo, branch=branch, path=path)

    if file_suffix:
        return _get_urls_for_files_in_dir_with_suffix(repo_context, file_suffix)
    else:
        return _get_url_for_single_file(repo_context)


def _get_urls_for_files_in_dir_with_suffix(ctx: GithubRepoContext, file_suffix: str):
    """Build raw-content URLs for files in a repository directory filtered by suffix.

    Args:
        ctx: Repository context describing owner, repo, branch, and path.
        file_suffix: Filename suffix used to filter listed files.

    Returns:
        HttpUrlDataset: URL dataset containing matching files.

    Raises:
        TypeError: If fetched GitHub API listing cannot be parsed as JSON list data.

    Example:
        >>> # dataset = _get_urls_for_files_in_dir_with_suffix(ctx, '.py')
        >>> # isinstance(dataset, HttpUrlDataset)
        >>> True
    """
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
    """Asynchronously create raw GitHub content URLs for repository files.

    Args:
        owner: GitHub repository owner or organization.
        repo: Repository name.
        branch: Branch or ref to read from.
        path: File or directory path inside the repository.
        file_suffix: Optional suffix filter when ``path`` points to a directory.

    Returns:
        A dataset of raw-content URLs keyed by file name.

    Raises:
        TypeError: If any input cannot be converted to expected model types.

    Example:
        >>> # urls = await async_get_github_repo_urls('octocat', 'hello-world', 'main', 'README.md')
        >>> # isinstance(urls, HttpUrlDataset)
        >>> True
    """

    repo_context = GithubRepoContext(owner=owner, repo=repo, branch=branch, path=path)

    if file_suffix:
        return await _async_get_urls_for_files_in_dir_with_suffix(repo_context, file_suffix)
    else:
        return _get_url_for_single_file(repo_context)


async def _async_get_urls_for_files_in_dir_with_suffix(ctx: GithubRepoContext, file_suffix: str):
    """Asynchronously build filtered raw-content URLs for a repository directory.

    Args:
        ctx: Repository context describing owner, repo, branch, and path.
        file_suffix: Filename suffix used to filter listed files.

    Returns:
        HttpUrlDataset: URL dataset containing matching files.

    Raises:
        TypeError: If fetched GitHub API listing cannot be parsed as JSON list data.

    Example:
        >>> # dataset = await _async_get_urls_for_files_in_dir_with_suffix(ctx, '.py')
        >>> # isinstance(dataset, HttpUrlDataset)
        >>> True
    """
    api_url = _create_api_url_for_file_list(ctx)
    file_list = await cast(asyncio.Task[JsonListOfDictsDataset],
                           JsonListOfDictsDataset.load(api_url))
    return _create_url_dataset_for_files_with_suffix(file_list, file_suffix, ctx)


def _create_api_url_for_file_list(ctx: GithubRepoContext) -> HttpUrlModel:
    """Create GitHub Contents API URL for listing files under ``ctx.path``.

    Args:
        ctx: Repository context with path and branch details.

    Returns:
        HttpUrlModel: URL pointing to the GitHub Contents API endpoint.

    Raises:
        TypeError: If context fields cannot be embedded in URL path/query values.

    Example:
        >>> # api_url = _create_api_url_for_file_list(ctx)
        >>> # 'api.github.com' in str(api_url)
        >>> True
    """
    api_url = HttpUrlModel('https://api.github.com')
    api_url.path // 'repos' // ctx.owner // ctx.repo // 'contents' // ctx.path
    api_url.query['ref'] = ctx.branch
    return api_url


def _create_url_dataset_for_files_with_suffix(
    file_list: JsonListOfDictsDataset,
    file_suffix: str,
    ctx: GithubRepoContext,
):
    """Convert GitHub file metadata to raw-content URLs filtered by suffix.

    Args:
        file_list: JSON dataset from GitHub Contents API response.
        file_suffix: Filename suffix used to filter entries.
        ctx: Repository context used to build the raw-content URL prefix.

    Returns:
        HttpUrlDataset: Dataset mapping matching file names to raw-content URLs.

    Raises:
        KeyError: If expected ``name`` keys are missing in API response items.

    Example:
        >>> # urls = _create_url_dataset_for_files_with_suffix(file_list, '.py', ctx)
        >>> # isinstance(urls, HttpUrlDataset)
        >>> True
    """
    url_prefix = _get_url_prefix_for_download(ctx)
    names = Model[list[str]]([f['name'] for f in file_list[0] if f['name'].endswith(file_suffix)])
    return HttpUrlDataset({name: f'{url_prefix}/{name}' for name in names})


def _get_url_prefix_for_download(ctx: GithubRepoContext):
    """Create raw-content base URL prefix for downloading files from GitHub.

    Args:
        ctx: Repository context containing owner, repository, branch, and path.

    Returns:
        HttpUrlModel: Raw-content URL prefix ending at the configured path.

    Raises:
        TypeError: If context values cannot be composed into a URL path.

    Example:
        >>> # prefix = _get_url_prefix_for_download(ctx)
        >>> # 'raw.githubusercontent.com' in str(prefix)
        >>> True
    """
    url_pre = HttpUrlModel('https://raw.githubusercontent.com')
    url_pre.path // ctx.owner // ctx.repo // ctx.branch // ctx.path
    return url_pre


def _get_url_for_single_file(repo_context):
    """Create a one-item URL dataset for a single repository file path.

    Args:
        repo_context: Repository context whose path points to a single file.

    Returns:
        HttpUrlDataset: Dataset mapping the filename to its raw-content URL.

    Raises:
        ValueError: If ``repo_context.path`` does not resolve to a filename.

    Example:
        >>> # urls = _get_url_for_single_file(ctx)
        >>> # isinstance(urls, HttpUrlDataset)
        >>> True
    """
    url_pre = _get_url_prefix_for_download(repo_context)
    name = url_pre.path.name
    return HttpUrlDataset({name: url_pre})
