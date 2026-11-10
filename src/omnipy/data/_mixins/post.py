"""Posting entry point shared by Models and Datasets."""

import asyncio
from typing import cast, overload, TypeVar

from omnipy.shared.protocols.config import IsHttpConfig
from omnipy.shared.protocols.data import IsDataset, IsHttpUrlModel, IsModel
from omnipy.shared.typing import TYPE_CHECKING
from omnipy.util.helpers import get_event_loop_and_check_if_loop_is_running

if TYPE_CHECKING:
    from omnipy.components.remote.models import HttpUrlModel

_ResponseT = TypeVar('_ResponseT', bound=IsDataset | IsModel)


class PostMixin:
    """Post the contents of Models and Datasets as JSON to an HTTP URL."""

    @overload
    def post(
        self,
        url: str | IsHttpUrlModel,
        response_cls: type[_ResponseT],
    ) -> _ResponseT | asyncio.Task[_ResponseT]: ...

    @overload
    def post(
        self,
        url: str | IsHttpUrlModel,
        response_cls: None = None,
    ) -> IsDataset | IsModel | asyncio.Task[IsDataset] | asyncio.Task[IsModel]: ...

    def post(
        self,
        url: str | IsHttpUrlModel,
        response_cls: type[IsDataset | IsModel] | None = None,
    ) -> object:
        """Post the contents as JSON to an HTTP URL, and return the decoded JSON responses.

        Datasets post each data item as a separate request to the same URL. The responses are
        kept under the keys of the data items, by default in a ``JsonDataset``. Models wrapping a
        Dataset (e.g. ``Model[JsonDataset]``) post the items of the wrapped Dataset in the same
        way. Other Models post their complete contents as a single request, and the response is
        by default a ``JsonModel``.

        A ``response_cls`` parses the responses according to the response contract of the
        service, e.g. ``Dataset[Model[ResponseSchema]]`` for the responses to the items of a
        Dataset or ``Model[ResponseSchema]`` for a single response. A response Dataset holds a
        failed request, or a response it cannot parse, as a failed data item. A response Model
        instead raises the error.

        Requests are rate limited and retried according to ``config.http.for_host[host]``. As
        POST requests are not idempotent, they are only retried on the status codes in
        ``retry_http_statuses_for_post``. On Models, ``post()`` hides a method of the same name on
        the content; call ``model.content.post()`` to use that instead.

        Args:
            url: HTTP URL to post to, as a string or an ``HttpUrlModel``.
            response_cls: Dataset or Model class to parse the decoded JSON responses into.

        Returns:
            A new instance of ``response_cls`` with the responses, or an ``asyncio.Task``
            when called inside a running event loop.

        Raises:
            TypeError: If ``response_cls`` is neither a Dataset nor a Model class.
        """
        # TODO: Support posting each data item to the URL with the same key in an HttpUrlDataset
        from omnipy.components.json.datasets import JsonDataset
        from omnipy.components.json.models import JsonModel
        from omnipy.components.remote.models import HttpUrlModel
        from omnipy.data.dataset import Dataset, is_dataset_instance, is_dataset_subclass
        from omnipy.data.helpers import get_single_value_key
        from omnipy.data.model import Model

        http_url = HttpUrlModel(url)

        posts_items: bool
        if is_dataset_instance(self):
            posts_items = True
            requests = JsonDataset(self.to_data())
        else:
            model = cast(Model, self)
            # Whether a Model wraps a Dataset is decided by its type, not by its current content
            posts_items = is_dataset_subclass(model.outer_type())
            if posts_items:
                requests = JsonDataset(model.to_data())
            else:
                requests = JsonDataset({get_single_value_key(type(model)): model.to_data()})

        if response_cls is None:
            response_cls = JsonDataset if posts_items else JsonModel

        if not (isinstance(response_cls, type) and issubclass(response_cls, Dataset | Model)):
            raise TypeError(
                f'"response_cls" must be a Dataset or Model class, not {response_cls!r}'
            )
        resolved_response_cls: type[Dataset | Model] = response_cls

        http_config = cast(Dataset | Model, self).config.http

        async def post_all() -> Dataset | Model:
            if posts_items and issubclass(resolved_response_cls, Dataset):
                # Posting directly into the response Dataset keeps failed requests as failed items
                responses = resolved_response_cls()
                await _post_json_items(requests, http_url, http_config, responses)
                return responses

            posted = Dataset[Model[object]]()
            await _post_json_items(requests, http_url, http_config, posted)
            response_data = posted.to_data()
            return resolved_response_cls(
                response_data if posts_items else next(iter(response_data.values()))
            )

        loop, loop_is_running = get_event_loop_and_check_if_loop_is_running()
        if loop and loop_is_running:
            return loop.create_task(post_all())
        return asyncio.run(post_all())


async def _post_json_items(
    requests: IsDataset,
    url: 'HttpUrlModel',
    http_config: IsHttpConfig,
    output_dataset: IsDataset,
) -> None:
    """Post each JSON request item to the URL, keeping the responses in ``output_dataset``."""
    from omnipy.components.remote.tasks import open_host_retry_client, post_json_to_api_endpoint

    host_config = http_config.for_host[url.host]
    async with open_host_retry_client(host_config, for_post=True) as retry_client:
        post_task = post_json_to_api_endpoint.refine(
            output_dataset_param='output_dataset',
        ).apply()
        await post_task(  # pyright: ignore[reportGeneralTypeIssues]
            requests,  # pyright: ignore[reportArgumentType]
            url=url,
            retry_client=retry_client,
            output_dataset=output_dataset,  # pyright: ignore[reportCallIssue]
        )
