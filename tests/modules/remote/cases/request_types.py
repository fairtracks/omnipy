from dataclasses import dataclass

import pytest_cases as pc

from omnipy import BytesDataset, Dataset, JsonDataset, StrDataset, TaskTemplate
from omnipy.modules.remote.tasks import (get_bytes_from_api_endpoint,
                                         get_json_from_api_endpoint,
                                         get_str_from_api_endpoint)


@dataclass
class RequestTypeCase:
    job: TaskTemplate
    kwargs: dict[str, str]
    dataset_cls: type[Dataset]


@pc.case
def case_get_json_from_api_endpoint() -> RequestTypeCase:
    return RequestTypeCase(get_json_from_api_endpoint, dict(), JsonDataset)


@pc.case
def case_get_str_from_api_endpoint() -> RequestTypeCase:
    return RequestTypeCase(get_str_from_api_endpoint, dict(), StrDataset)


@pc.case
def case_get_bytes_from_api_endpoint() -> RequestTypeCase:
    return RequestTypeCase(get_bytes_from_api_endpoint, dict(), BytesDataset)
