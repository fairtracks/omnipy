from collections.abc import Iterable

from pydantic import constr, PositiveInt

from omnipy.compute.task import TaskTemplate
from omnipy.compute.typing import mypy_fix_task_template
from omnipy.modules.json.datasets import JsonDataset

from .functions import encode_api


@mypy_fix_task_template
@TaskTemplate()
def import_dataset_from_encode(endpoints: Iterable[constr(min_length=1)],
                               max_data_item_count: PositiveInt) -> JsonDataset:
    dataset = JsonDataset()
    for endpoint in endpoints:
        dataset[endpoint] = encode_api(
            endpoint,
            limit=str(max_data_item_count),
            format='json',
        )
    return dataset
