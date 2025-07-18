from typing import Annotated

import pytest
import pytest_cases as pc

from omnipy import (BytesDataset,
                    Dataset,
                    JsonDataset,
                    JsonModel,
                    Model,
                    StrDataset,
                    StrictBytesModel,
                    StrictStrModel)
from omnipy.components.remote.datasets import AutoResponseContentDataset
from omnipy.components.remote.tasks import (async_load_urls_into_new_dataset,
                                            get_auto_from_api_endpoint,
                                            get_bytes_from_api_endpoint,
                                            get_json_from_api_endpoint,
                                            get_str_from_api_endpoint,
                                            load_urls_into_new_dataset)

from ..helpers.classes import EndpointCase, RequestTypeCase


@pc.case(tags='supports_external_session')
def case_get_json_from_api_endpoint() -> RequestTypeCase:
    return RequestTypeCase(True, get_json_from_api_endpoint, dict(), JsonDataset)


@pc.case(tags='supports_external_session')
def case_get_str_from_api_endpoint() -> RequestTypeCase:
    return RequestTypeCase(True, get_str_from_api_endpoint, dict(), StrDataset)


@pc.case(tags='supports_external_session')
def case_get_bytes_from_api_endpoint() -> RequestTypeCase:
    return RequestTypeCase(True, get_bytes_from_api_endpoint, dict(), BytesDataset)


@pc.case(tags='supports_external_session')
def case_get_auto_from_api_endpoint() -> RequestTypeCase:
    return RequestTypeCase(True, get_auto_from_api_endpoint, dict(), AutoResponseContentDataset)


@pc.case
def case_sync_load_urls_into_new_dataset(
        endpoint: Annotated[EndpointCase, pytest.fixture]) -> RequestTypeCase:
    return RequestTypeCase(False,
                           load_urls_into_new_dataset,
                           dict(dataset_cls=Dataset[endpoint.auto_model_type]),
                           Dataset[endpoint.auto_model_type])


@pc.case
def case_async_load_urls_into_new_dataset(
        endpoint: Annotated[EndpointCase, pytest.fixture]) -> RequestTypeCase:
    return RequestTypeCase(True,
                           async_load_urls_into_new_dataset,
                           dict(dataset_cls=Dataset[endpoint.auto_model_type]),
                           Dataset[endpoint.auto_model_type])


@pc.case
@pc.parametrize(
    'model_cls, mime_type',
    [
        (StrictBytesModel, 'application/octet-stream'),
        (StrictStrModel, 'text/plain'),
        (JsonModel, 'application/json'),
    ],
    ids=['bytes', 'text', 'json'])
def case_async_load_urls_into_new_dataset_auto_as_mime_type(
    endpoint: Annotated[EndpointCase, pytest.fixture],
    model_cls: type[Model],
    mime_type: str,
) -> RequestTypeCase:
    return RequestTypeCase(True,
                           async_load_urls_into_new_dataset,
                           dict(
                               dataset_cls=Dataset[model_cls],
                               as_mime_type=mime_type,
                           ),
                           Dataset[model_cls])


@pc.case
@pc.parametrize(
    'model_cls, mime_type',
    [
        (StrictBytesModel, 'text/plain'),
        (StrictStrModel, 'application/json'),
        (JsonModel, 'application/octet-stream'),
    ],
    ids=['bytes', 'text', 'json'])
def case_fail_async_load_urls_into_new_dataset_auto_as_incorrect_mime_type(
    endpoint: Annotated[EndpointCase, pytest.fixture],
    model_cls: type[Model],
    mime_type: str,
) -> RequestTypeCase:
    return RequestTypeCase(True,
                           async_load_urls_into_new_dataset,
                           dict(
                               dataset_cls=Dataset[model_cls],
                               as_mime_type=mime_type,
                           ),
                           Dataset[model_cls], (ValueError, TypeError))
