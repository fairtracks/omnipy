from dataclasses import dataclass
from typing import Annotated

import pytest
import pytest_cases as pc

from components.remote.conftest import EndpointCase
from omnipy import BytesDataset, Dataset, JsonDataset, StrDataset, TaskTemplate
from omnipy.components.remote.datasets import AutoResponseContentsDataset
from omnipy.components.remote.tasks import (async_load_urls_into_new_dataset,
                                            get_auto_from_api_endpoint,
                                            get_bytes_from_api_endpoint,
                                            get_json_from_api_endpoint,
                                            get_str_from_api_endpoint,
                                            load_urls_into_new_dataset)


@dataclass
class RequestTypeCase:
    is_async: bool
    job: TaskTemplate
    kwargs: dict[str, object]
    dataset_cls: type[Dataset]


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
    return RequestTypeCase(True, get_auto_from_api_endpoint, dict(), AutoResponseContentsDataset)


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


# TODO: Add test for synchronous task `load_urls_into_new_dataset`
