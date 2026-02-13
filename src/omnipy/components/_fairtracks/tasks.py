from collections.abc import Iterable

from omnipy.compute.task import TaskTemplate
import omnipy.util._pydantic as pyd

from ..json.datasets import JsonDataset
from .functions import encode_api


@TaskTemplate()
def import_dataset_from_encode(endpoints: Iterable[pyd.constr(min_length=1)],
                               max_data_item_count: pyd.PositiveInt) -> JsonDataset:
    dataset = JsonDataset()
    for endpoint in endpoints:
        dataset[endpoint] = encode_api(
            endpoint,
            limit=str(max_data_item_count),
            format='json',
        )
    return dataset
