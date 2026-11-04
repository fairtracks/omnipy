"""Loading entry points for Datasets."""

import asyncio
from collections.abc import Iterable
from os import fspath, PathLike
from typing import cast, Self

from omnipy.shared.enums.data import SelectSerializerBy
from omnipy.shared.protocols.data import (
    IsPathOrUrl,
    IsPathsOrUrlsOneOrMore,
    IsPathsOrUrlsOneOrMoreOrNone,
)
from omnipy.util.helpers import has_items_method
from omnipy.util.pydantic import ValidationError


class LoadMixin:
    """Load serialized contents from local paths or HTTP URLs."""

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

        return self._load_paths_or_urls(
            paths_or_urls,
            select_serializer_by=select_serializer_by,
            as_mime_type=as_mime_type,
            ignore_dirs=ignore_dirs,
        )

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
