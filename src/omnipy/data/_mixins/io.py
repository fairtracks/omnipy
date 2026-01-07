import asyncio
from collections import defaultdict
import inspect
import os
import tarfile
from typing import cast, Iterable, Mapping, TYPE_CHECKING

from omnipy.shared.constants import ASYNC_LOAD_SLEEP_TIME
from omnipy.shared.protocols.data import (IsDataset,
                                          IsHttpUrlDataset,
                                          IsPathOrUrl,
                                          IsPathsOrUrlsOneOrMoreOrNone)
from omnipy.util._pydantic import ValidationError
from omnipy.util.helpers import get_event_loop_and_check_if_loop_is_running

if TYPE_CHECKING:
    from omnipy.data.dataset import _ModelT, Dataset
    from omnipy.data.model import Model


class DatasetIOMixin:
    def save(self, path: str):
        # self = cast('Dataset | Model', self)

        serializer_registry = self._get_serializer_registry()

        self_as_dataset = cast(IsDataset, self)
        parsed_dataset, serializer = \
            serializer_registry.auto_detect_tar_file_serializer(self_as_dataset)

        if serializer is None:
            print(f'Unable to find a serializer for dataset with data type "{type(self)}". '
                  f'Will abort saving...')
        else:
            assert parsed_dataset is not None

            out_tar_gz_path = f'{path}' if path.endswith('.tar.gz') else f'{path}.tar.gz'
            print(f'Writing dataset as a gzipped tarpack to "{os.path.abspath(out_tar_gz_path)}"')

            with open(out_tar_gz_path, 'wb') as out_tar_gz_file:
                out_tar_gz_file.write(serializer.serialize(parsed_dataset))

            directory = os.path.abspath(out_tar_gz_path[:-7])
            if not os.path.exists(directory):
                os.makedirs(directory)

            tar = tarfile.open(out_tar_gz_path)
            print(f'Extracting content to directory "{os.path.abspath(out_tar_gz_path[:-7])}"')
            tar.extractall(path=directory)
            tar.close()

    @classmethod
    def load(
        cls,
        paths_or_urls: IsPathsOrUrlsOneOrMoreOrNone = None,
        by_file_suffix: bool = False,
        as_mime_type: None | str = None,
        **kwargs: IsPathOrUrl,
    ) -> 'DatasetIOMixin | asyncio.Task[DatasetIOMixin]':
        dataset = cls()
        return dataset.load_into(
            paths_or_urls, by_file_suffix=by_file_suffix, as_mime_type=as_mime_type, **kwargs)

    def load_into(
        self,
        paths_or_urls: IsPathsOrUrlsOneOrMoreOrNone = None,
        by_file_suffix: bool = False,
        as_mime_type: None | str = None,
        **kwargs: IsPathOrUrl,
    ) -> 'DatasetIOMixin | asyncio.Task[DatasetIOMixin]':
        from omnipy.components.remote.datasets import HttpUrlDataset
        from omnipy.components.remote.models import HttpUrlModel

        if paths_or_urls is None:
            assert len(kwargs) > 0, 'No paths or urls specified'
            paths_or_urls = kwargs
        else:
            assert len(kwargs) == 0, 'No keyword arguments allowed when paths_or_urls is specified'

        match paths_or_urls:
            case HttpUrlDataset():
                return self._load_http_urls(paths_or_urls, as_mime_type=as_mime_type)

            case HttpUrlModel():
                return self._load_http_urls(
                    HttpUrlDataset({str(paths_or_urls): paths_or_urls}),
                    as_mime_type=as_mime_type,
                )

            case str():
                try:
                    http_url_dataset = HttpUrlDataset({paths_or_urls: paths_or_urls})
                except ValidationError:
                    return self._load_paths([paths_or_urls], by_file_suffix)
                return self._load_http_urls(http_url_dataset, as_mime_type=as_mime_type)

            case Mapping():
                try:
                    http_url_dataset = HttpUrlDataset(paths_or_urls)
                except ValidationError as exp:
                    raise NotImplementedError(
                        'Loading files with specified keys is not yet '
                        'implemented, as only tar.gz file import is '
                        'supported until serializers have been refactored.') from exp
                return self._load_http_urls(http_url_dataset, as_mime_type=as_mime_type)

            case Iterable():
                path_or_url_iterable = cast(Iterable[str], paths_or_urls)
                try:
                    http_url_dataset = HttpUrlDataset(
                        zip(path_or_url_iterable, path_or_url_iterable))
                except ValidationError:
                    return self._load_paths(path_or_url_iterable, by_file_suffix)
                return self._load_http_urls(http_url_dataset, as_mime_type=as_mime_type)
            case _:
                raise TypeError(f'"paths_or_urls" argument is of incorrect type. Type '
                                f'{type(paths_or_urls)} is not supported.')

    def _load_http_urls(
        self,
        http_url_dataset: IsHttpUrlDataset,
        as_mime_type: None | str = None,
    ) -> 'DatasetIOMixin | asyncio.Task[DatasetIOMixin]':
        from omnipy.components.remote.helpers import RateLimitingClientSession
        from omnipy.components.remote.tasks import get_auto_from_api_endpoint

        self_as_data_class = cast('Dataset | Model', self)

        hosts: defaultdict[str, list[int]] = defaultdict(list)
        for i, url in enumerate(http_url_dataset.values()):
            hosts[url.host].append(i)

        async def load_all(as_mime_type: None | str = None) -> 'Dataset[_ModelT]':
            tasks = []

            for host in hosts:
                async with RateLimitingClientSession(
                        self_as_data_class.config.http.for_host[host].requests_per_time_period,
                        self_as_data_class.config.http.for_host[host].time_period_in_secs
                ) as client_session:
                    indices = hosts[host]
                    # fetch_task = get_auto_from_api_endpoint
                    # if as_mime_type:
                    #     match as_mime_type:
                    #         case 'application/json':
                    #             fetch_task = get_json_from_api_endpoint
                    #         case 'text/plain':
                    #             fetch_task = get_str_from_api_endpoint
                    #         case 'application/octet-stream' | _:
                    #             fetch_task = get_bytes_from_api_endpoint

                    ret = get_auto_from_api_endpoint.refine(
                        output_dataset_param='output_dataset').run(
                            http_url_dataset[indices],
                            client_session=client_session,
                            output_dataset=self_as_data_class,
                            as_mime_type=as_mime_type)

                    if not isinstance(ret, asyncio.Task):
                        assert inspect.iscoroutine(ret)
                        task = asyncio.create_task(ret)
                    else:
                        task = ret

                    tasks.append(task)

                    while not task.done():
                        await asyncio.sleep(ASYNC_LOAD_SLEEP_TIME)

            await asyncio.gather(*tasks)
            return self_as_data_class

        loop, loop_is_running = get_event_loop_and_check_if_loop_is_running()

        if loop and loop_is_running:
            return loop.create_task(load_all(as_mime_type=as_mime_type))
        else:
            return asyncio.run(load_all(as_mime_type=as_mime_type))

    def _load_paths(self, path_or_urls: Iterable[str], by_file_suffix: bool) -> 'DatasetIOMixin':
        self_as_data_class = cast('Dataset | Model', self)

        for path_or_url in path_or_urls:
            serializer_registry = self._get_serializer_registry()
            tar_gz_file_path = self._ensure_tar_gz_file(path_or_url)

            self_as_dataset = cast(IsDataset, self)
            if by_file_suffix:
                loaded_dataset = \
                    serializer_registry.load_from_tar_file_path_based_on_file_suffix(
                        self_as_data_class, tar_gz_file_path, self_as_dataset)
            else:
                loaded_dataset = \
                    serializer_registry.load_from_tar_file_path_based_on_dataset_cls(
                        self_as_data_class, tar_gz_file_path, self_as_dataset, any_file_suffix=True)
            if loaded_dataset is not None:
                self_as_data_class.absorb(loaded_dataset)
                continue
            else:
                raise RuntimeError('Unable to load from serializer')
        return self

    @staticmethod
    def _ensure_tar_gz_file(path: str):
        assert os.path.exists(path), f'No file or directory at {path}'

        if not path.endswith('.tar.gz'):
            tar_gz_file_path = path + '.tar.gz'
            if not os.path.isfile(tar_gz_file_path):
                print(f'Creating compressed file {os.path.abspath(tar_gz_file_path)} from '
                      f'the content of "{os.path.abspath(path)}"')

                with tarfile.open(tar_gz_file_path, 'w:gz') as tar:
                    if os.path.isdir(path):
                        for fn in sorted(os.listdir(path)):
                            p = os.path.join(path, fn)
                            tar.add(p, arcname=fn)
                    elif os.path.isfile(path):
                        tar.add(path, arcname=os.path.basename(path))
            return tar_gz_file_path

        return path

    @staticmethod
    def _get_serializer_registry():
        from omnipy.components import get_serializer_registry
        return get_serializer_registry()
