from dataclasses import dataclass

import pytest_cases as pc

from omnipy import BytesDataset, Dataset, JsonDataset, JsonDictDataset, StrDataset, TaskTemplate
from omnipy.modules.remote.tasks import (async_load_urls_into_new_dataset,
                                         get_bytes_from_api_endpoint,
                                         get_json_from_api_endpoint,
                                         get_str_from_api_endpoint)


@dataclass
class RequestTypeCase:
    job: TaskTemplate
    kwargs: dict[str, object]
    dataset_cls: type[Dataset]


@pc.case(tags='supports_external_session')
def case_get_json_from_api_endpoint() -> RequestTypeCase:
    return RequestTypeCase(get_json_from_api_endpoint, dict(), JsonDataset)


@pc.case(tags='supports_external_session')
def case_get_str_from_api_endpoint() -> RequestTypeCase:
    return RequestTypeCase(get_str_from_api_endpoint, dict(), StrDataset)


@pc.case(tags='supports_external_session')
def case_get_bytes_from_api_endpoint() -> RequestTypeCase:
    return RequestTypeCase(get_bytes_from_api_endpoint, dict(), BytesDataset)


@pc.case
def case_load_urls_into_new_dataset_default_json() -> RequestTypeCase:
    return RequestTypeCase(async_load_urls_into_new_dataset, dict(), JsonDataset)


@pc.case
def case_load_urls_into_new_dataset_other_dataset_cls() -> RequestTypeCase:
    return RequestTypeCase(
        async_load_urls_into_new_dataset,
        dict(dataset_cls=JsonDictDataset),
        JsonDictDataset,
    )


# TODO: Add test for synchronous task `load_urls_into_new_dataset`
