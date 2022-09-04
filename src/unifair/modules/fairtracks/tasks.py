from typing import Iterable

from pydantic import constr, PositiveInt

from unifair.compute.task import TaskTemplate
from unifair.old.steps.imports.encode import ImportEncodeMetadataFromApi

from ..json.models import JsonDataset


@TaskTemplate
def import_dataset_from_encode(endpoints: Iterable[constr(min_length=1)],
                               max_data_item_count: PositiveInt) -> JsonDataset:
    dataset = JsonDataset()
    for endpoint in endpoints:
        dataset[endpoint] = ImportEncodeMetadataFromApi.encode_api(
            endpoint,
            limit=str(max_data_item_count),
            format='json',
        )
    return dataset
