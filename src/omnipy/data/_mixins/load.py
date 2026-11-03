"""Share loading entry points between Models and Datasets."""

import asyncio
from collections.abc import Iterable
from os import fspath, PathLike
from typing import cast, Self

from omnipy.shared.protocols.data import (
    IsPathOrUrl,
    IsPathsOrUrlsOneOrMore,
    IsPathsOrUrlsOneOrMoreOrNone,
)
from omnipy.util.helpers import has_items_method
from omnipy.util.pydantic import ValidationError


class LoadMixin:
    """Reuse Dataset loading and validate complete responses through a Model."""

    @classmethod
    def load(
        cls,
        paths_or_urls: IsPathsOrUrlsOneOrMoreOrNone = None,
        by_file_suffix: bool = False,
        as_mime_type: str | None = None,
        ignore_dirs: bool = False,
        **kwargs: IsPathOrUrl,
    ) -> Self | asyncio.Task[Self]:
        """Create an instance and load serialized contents into it.

        Accepts the same arguments as ``load_into()``. Inside a running event
        loop, returns a task that resolves to the newly created instance.
        """
        instance = cls()
        return instance.load_into(
            paths_or_urls,
            by_file_suffix=by_file_suffix,
            as_mime_type=as_mime_type,
            ignore_dirs=ignore_dirs,
            **kwargs,
        )

    def load_into(
        self,
        paths_or_urls: IsPathsOrUrlsOneOrMoreOrNone = None,
        by_file_suffix: bool = False,
        as_mime_type: str | None = None,
        ignore_dirs: bool = False,
        **kwargs: IsPathOrUrl,
    ) -> Self | asyncio.Task[Self]:
        """Load serialized contents into this Model or Dataset.

        Datasets load responses into their named entries. Models collect decoded
        responses in a temporary Dataset, then pass the loaded data to their
        ``from_data()`` method after loading completes. A single HTTP URL supplies
        its response contents; a URL Dataset, mapping, iterable, or keyword
        arguments supply a keyed collection, even when empty or containing one
        URL. Local files use suffix-based serializer selection for Models. One
        loaded file supplies its contents; multiple files supply their named
        entries, including when they come from the same archive.

        Args:
            paths_or_urls: Path, HTTP URL, or collection of paths or URLs.
            by_file_suffix: Prefer file suffixes when selecting local serializers.
            as_mime_type: Optional MIME type override for HTTP responses.
            ignore_dirs: Skip directory entries inside archives/directories.
            **kwargs: Named sources when ``paths_or_urls`` is omitted.

        Returns:
            This instance after loading, or a task resolving to it inside a
            running event loop.
        """
        from omnipy.data.dataset import Dataset, is_dataset_instance
        from omnipy.data.model import Model

        if paths_or_urls is None:
            assert len(kwargs) > 0, 'No paths or urls specified'
            paths_or_urls = kwargs
        else:
            assert len(kwargs) == 0, 'No keyword arguments allowed when paths_or_urls is specified'

        dataset = self if is_dataset_instance(self) else Dataset[Model[object]]()
        loaded, single_response = dataset._load_paths_or_urls(
            paths_or_urls,
            by_file_suffix=by_file_suffix or not is_dataset_instance(self),
            as_mime_type=as_mime_type,
            ignore_dirs=ignore_dirs,
        )

        if is_dataset_instance(self):
            return cast(Self | asyncio.Task[Self], loaded)

        def update_model(model: Self) -> Self:
            data = dataset.to_data()
            cast(Model, model).from_data(next(iter(data.values())) if single_response else data)
            return model

        if isinstance(loaded, asyncio.Task):

            async def update_after_loading() -> Self:
                await loaded
                return update_model(self)

            return asyncio.get_running_loop().create_task(update_after_loading())

        return update_model(self)

    def _load_paths_or_urls(
        self,
        paths_or_urls: IsPathsOrUrlsOneOrMore,
        by_file_suffix: bool,
        as_mime_type: str | None,
        ignore_dirs: bool,
    ) -> tuple[Self | asyncio.Task[Self], bool]:
        """Dispatch into a Dataset and report whether to unwrap its sole item."""
        from omnipy.components.remote.datasets import HttpUrlDataset
        from omnipy.components.remote.models import HttpUrlModel
        from omnipy.data.dataset import Dataset

        dataset = cast(Dataset, self)
        single_response = False

        if isinstance(paths_or_urls, PathLike):
            paths_or_urls = fspath(paths_or_urls)

        match paths_or_urls:
            case HttpUrlDataset():
                loaded = dataset._load_http_urls(paths_or_urls, as_mime_type=as_mime_type)

            case HttpUrlModel():
                single_response = True
                loaded = dataset._load_http_urls(
                    HttpUrlDataset({str(paths_or_urls): paths_or_urls}),
                    as_mime_type=as_mime_type,
                )

            case str():
                try:
                    http_url_dataset = HttpUrlDataset({paths_or_urls: paths_or_urls})
                except ValidationError:
                    loaded = dataset._load_paths(
                        [paths_or_urls],
                        by_file_suffix,
                        ignore_dirs=ignore_dirs,
                    )
                    return cast(Self, loaded), len(loaded) == 1
                single_response = True
                loaded = dataset._load_http_urls(http_url_dataset, as_mime_type=as_mime_type)

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
                path_or_url_iterable = tuple(
                    fspath(path) if isinstance(path, PathLike) else path for path in paths_or_urls
                )
                try:
                    http_url_dataset = HttpUrlDataset(
                        zip(path_or_url_iterable, path_or_url_iterable)
                    )
                except ValidationError:
                    loaded = dataset._load_paths(
                        path_or_url_iterable,
                        by_file_suffix,
                        ignore_dirs=ignore_dirs,
                    )
                    return cast(Self, loaded), len(loaded) == 1
                loaded = dataset._load_http_urls(http_url_dataset, as_mime_type=as_mime_type)
            case _:
                raise TypeError(
                    f'"paths_or_urls" argument is of incorrect type. Type '
                    f'{type(paths_or_urls)} is not supported.'
                )

        return cast(Self | asyncio.Task[Self], loaded), single_response
