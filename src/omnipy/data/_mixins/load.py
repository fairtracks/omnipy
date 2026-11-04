"""Loading entry points shared by Models and Datasets."""

import asyncio
from collections.abc import Callable, Iterable
import os
from os import fspath, PathLike
import tarfile
from typing import cast, Literal, Self, TypeVar

from omnipy.shared.enums.data import SelectSerializerBy
from omnipy.shared.protocols.data import (
    IsPathOrUrl,
    IsPathsOrUrlsOneOrMore,
    IsPathsOrUrlsOneOrMoreOrNone,
)
from omnipy.util.helpers import has_items_method
from omnipy.util.pydantic import ValidationError

_T = TypeVar('_T')


class LoadMixin:
    """Load serialized contents from local paths or HTTP URLs into Models and Datasets."""

    @classmethod
    def load(
        cls,
        paths_or_urls: IsPathsOrUrlsOneOrMoreOrNone = None,
        select_serializer_by: SelectSerializerBy.Literals = SelectSerializerBy.TYPE,
        as_mime_type: str | None = None,
        ignore_dirs: bool = False,
        **kwargs: IsPathOrUrl,
    ) -> Self | asyncio.Task[Self]:
        """Create an instance and load serialized contents into it.

        Args:
            paths_or_urls: Path, URL, iterable of paths or URLs, or dataset/model of HTTP URLs to
                load from.
            select_serializer_by: For local files, select serializers by the target type
                (``'type'``, falling back to file suffixes) or by file suffix (``'suffix'``).
                Files are read as raw bytes if no serializer supports their file
                suffix. Files with different suffixes raise an error, unless
                selected by type.
            as_mime_type: Optional MIME type hint for HTTP loading.
            ignore_dirs:  Whether to skip directory entries inside archives/directories.
            **kwargs: Alternate keyed path or URL arguments when ``paths_or_urls`` is omitted.

        Returns:
            A loaded instance, or an ``asyncio.Task`` when called inside a running event loop.
        """
        instance = cls()
        return instance.load_into(
            paths_or_urls,
            select_serializer_by=select_serializer_by,
            as_mime_type=as_mime_type,
            ignore_dirs=ignore_dirs,
            **kwargs,
        )

    def load_into(
        self,
        paths_or_urls: IsPathsOrUrlsOneOrMoreOrNone = None,
        select_serializer_by: SelectSerializerBy.Literals = SelectSerializerBy.TYPE,
        as_mime_type: str | None = None,
        ignore_dirs: bool = False,
        **kwargs: IsPathOrUrl,
    ) -> Self | asyncio.Task[Self]:
        """Load serialized contents into this instance.

        Datasets load the sources into their named entries, keeping existing entries. Models
        wrapping a Dataset (e.g. ``Model[JsonDataset]``) load in the same way into the wrapped
        Dataset. Other Models load either a single value or a mapping of named values, as
        determined by the sources:

        - A single URL, or a path to a single file, gives a single value
        - An archive or directory saved from a single Model value by ``save()`` gives that value
        - Other archives or directories, mappings, Datasets of URLs, iterables and keyword
          arguments give a mapping of named values, also with one entry or none

        Such Models are left unchanged if loading fails. On Models, ``load_into()`` hides a
        method of the same name on the content; call ``model.content.load_into()`` followed by
        ``model.validate_content()`` to use that instead.

        Args:
            paths_or_urls: Path, URL, iterable of paths or URLs, or dataset/model of HTTP URLs to
                load from.
            select_serializer_by: For local files, select serializers by the target type
                (``'type'``, falling back to file suffixes) or by file suffix (``'suffix'``).
                Files are read as raw bytes if no serializer supports their file
                suffix. Files with different suffixes raise an error, unless
                selected by type.
            as_mime_type: Optional MIME type hint for HTTP loading.
            ignore_dirs:  Whether to skip directory entries inside archives/directories.
            **kwargs: Alternate keyed path or URL arguments when ``paths_or_urls`` is omitted.

        Returns:
            This instance after loading, or an ``asyncio.Task`` when called inside a running event
            loop.

        Raises:
            AssertionError: If the input forms are combined incorrectly.
            TypeError: If ``paths_or_urls`` has an unsupported type.
            NotImplementedError: If keyed local-path loading is requested.
        """
        if paths_or_urls is None:
            assert len(kwargs) > 0, 'No paths or urls specified'
            paths_or_urls = kwargs
        else:
            assert len(kwargs) == 0, 'No keyword arguments allowed when paths_or_urls is specified'

        from omnipy.data.dataset import is_dataset_instance

        if is_dataset_instance(self):
            return self._load_paths_or_urls(
                paths_or_urls,
                select_serializer_by=select_serializer_by,
                as_mime_type=as_mime_type,
                ignore_dirs=ignore_dirs,
            )
        return self._load_into_model(
            paths_or_urls,
            select_serializer_by=select_serializer_by,
            as_mime_type=as_mime_type,
            ignore_dirs=ignore_dirs,
        )

    def _load_into_model(
        self,
        paths_or_urls: IsPathsOrUrlsOneOrMore,
        select_serializer_by: SelectSerializerBy.Literals,
        as_mime_type: str | None,
        ignore_dirs: bool,
    ) -> Self | asyncio.Task[Self]:
        """Load into a Model through a Dataset, as described in ``load_into()``."""
        from omnipy.data.dataset import Dataset, is_dataset_subclass
        from omnipy.data.model import Model

        model = cast(Model, self)

        # Whether a Model wraps a Dataset is decided by its type, not by its current content
        if is_dataset_subclass(model.outer_type()):
            wrapped_dataset = cast(Dataset, model.content)
            # TODO: Make Models wrapping a Dataset hold failed and pending entries like the Dataset
            #       A Dataset can hold failed and pending data entries, e.g. from failed HTTP
            #       requests, but validating a Model wrapping it raises FailedDataError or
            #       PendingDataError instead. To be resolved as part of updated failure handling.
            loaded = wrapped_dataset._load_paths_or_urls(
                paths_or_urls,
                select_serializer_by=select_serializer_by,
                as_mime_type=as_mime_type,
                ignore_dirs=ignore_dirs,
            )

            return _after_loading(loaded, model.validate_content, self)

        source_kind = _classify_source_for_model(paths_or_urls)
        # For local files, a Dataset of the Model type selects serializers by that type
        model_cls = type(model)
        dataset = Dataset[model_cls]() if source_kind == 'path' else Dataset[Model[object]]()  # type: ignore[valid-type]
        loaded = dataset._load_paths_or_urls(
            paths_or_urls,
            select_serializer_by=select_serializer_by,
            as_mime_type=as_mime_type,
            ignore_dirs=ignore_dirs,
        )

        def set_model_content() -> None:
            data = dataset.to_data()
            if source_kind == 'keyed':
                model.from_data(data)
            else:
                if len(data) != 1:
                    raise ValueError(f'Expected a single value to load, but got {len(data)}')
                model.from_data(next(iter(data.values())))

        return _after_loading(loaded, set_model_content, self)

    def _load_paths_or_urls(
        self,
        paths_or_urls: IsPathsOrUrlsOneOrMore,
        select_serializer_by: SelectSerializerBy.Literals,
        as_mime_type: str | None,
        ignore_dirs: bool,
    ) -> Self | asyncio.Task[Self]:
        """Dispatch loading on the form of ``paths_or_urls``."""
        from omnipy.components.remote.datasets import HttpUrlDataset
        from omnipy.components.remote.models import HttpUrlModel
        from omnipy.data.dataset import Dataset

        dataset = cast(Dataset, self)

        if isinstance(paths_or_urls, PathLike):
            paths_or_urls = fspath(paths_or_urls)

        loaded: object
        match paths_or_urls:
            case HttpUrlDataset():
                loaded = dataset._load_http_urls(paths_or_urls, as_mime_type=as_mime_type)

            case HttpUrlModel():
                loaded = dataset._load_http_urls(
                    HttpUrlDataset({str(paths_or_urls): paths_or_urls}),
                    as_mime_type=as_mime_type,
                )

            case str():
                loaded = self._load_http_urls_or_paths(
                    {paths_or_urls: paths_or_urls},
                    [paths_or_urls],
                    select_serializer_by=select_serializer_by,
                    as_mime_type=as_mime_type,
                    ignore_dirs=ignore_dirs,
                )

            case _ if has_items_method(paths_or_urls):
                try:
                    http_url_dataset = HttpUrlDataset(paths_or_urls)
                except ValidationError as exp:
                    raise NotImplementedError(
                        'Loading files with specified keys is not yet '
                        'implemented, as only tar.gz file import is '
                        'supported until serializers have been refactored.'
                    ) from exp
                loaded = dataset._load_http_urls(http_url_dataset, as_mime_type=as_mime_type)

            case Iterable():
                # Materialize first, as an iterator would be consumed by the URL attempt
                path_or_url_tuple = tuple(
                    fspath(path) if isinstance(path, PathLike) else path for path in paths_or_urls
                )
                loaded = self._load_http_urls_or_paths(
                    zip(path_or_url_tuple, path_or_url_tuple),
                    path_or_url_tuple,
                    select_serializer_by=select_serializer_by,
                    as_mime_type=as_mime_type,
                    ignore_dirs=ignore_dirs,
                )

            case _:
                raise TypeError(
                    f'"paths_or_urls" argument is of incorrect type. Type '
                    f'{type(paths_or_urls)} is not supported.'
                )

        return cast(Self | asyncio.Task[Self], loaded)

    def _load_http_urls_or_paths(
        self,
        keys_and_urls: Iterable[tuple[str, str]] | dict[str, str],
        paths: Iterable[str],
        select_serializer_by: SelectSerializerBy.Literals,
        as_mime_type: str | None,
        ignore_dirs: bool,
    ) -> Self | asyncio.Task[Self]:
        """Load the sources as HTTP URLs if they all are, otherwise as local paths."""
        from omnipy.components.remote.datasets import HttpUrlDataset
        from omnipy.data.dataset import Dataset

        dataset = cast(Dataset, self)
        loaded: object
        try:
            http_url_dataset = HttpUrlDataset(keys_and_urls)
        except ValidationError:
            loaded = dataset._load_paths(paths, select_serializer_by, ignore_dirs=ignore_dirs)
        else:
            loaded = dataset._load_http_urls(http_url_dataset, as_mime_type=as_mime_type)
        return cast(Self | asyncio.Task[Self], loaded)


def _after_loading(
    loaded: object, finish: Callable[[], object], result: _T
) -> _T | asyncio.Task[_T]:
    """Call ``finish`` and return ``result`` after loading, in a task if loading runs in one."""
    if isinstance(loaded, asyncio.Task):
        loading_task = loaded

        async def finish_after_loading() -> _T:
            await loading_task
            finish()
            return result

        return asyncio.get_running_loop().create_task(finish_after_loading())
    finish()
    return result


def _classify_source_for_model(
    paths_or_urls: IsPathsOrUrlsOneOrMore,
) -> Literal['url', 'path', 'keyed']:
    """Return whether the sources give a single value from a URL or a path, or named values."""
    from omnipy.components.remote.datasets import HttpUrlDataset
    from omnipy.components.remote.models import HttpUrlModel

    if isinstance(paths_or_urls, PathLike):
        paths_or_urls = fspath(paths_or_urls)

    if isinstance(paths_or_urls, HttpUrlModel):
        return 'url'

    if isinstance(paths_or_urls, str):
        try:
            HttpUrlDataset({paths_or_urls: paths_or_urls})
        except ValidationError:
            if _is_single_value_path(paths_or_urls):
                return 'path'
        else:
            return 'url'

    return 'keyed'


def _is_single_value_path(path: str) -> bool:
    """Return whether a path is a single file, or an archive or directory saved from a value."""
    from omnipy.data.dataset import Dataset
    from omnipy.data.helpers import is_single_value_key

    if os.path.isfile(path) and not path.endswith(('.tar.gz', '.zip')):
        return True

    tar_gz_file_path = Dataset._ensure_tar_gz_file(path)
    with tarfile.open(tar_gz_file_path, 'r:gz') as archive:
        file_names = [member.name for member in archive.getmembers() if not member.isdir()]

    if len(file_names) != 1:
        return False
    data_file_name = os.path.basename('.'.join(file_names[0].split('.')[:-1]))
    return is_single_value_key(data_file_name)
