from omnipy.compute.flow import LinearFlowTemplate

from ..general.tasks import convert_dataset
from ..json.datasets import JsonDictOfDictsDataset
from ..json.flows import flatten_nested_json
from ..json.tasks import transpose_dict_of_dicts_2_list_of_dicts
from .datasets import FlattenedIsaJsonDataset, IsaJsonDataset


@LinearFlowTemplate(
    convert_dataset.refine(fixed_params=dict(dataset_cls=JsonDictOfDictsDataset)),
    transpose_dict_of_dicts_2_list_of_dicts,
    flatten_nested_json,
    convert_dataset.refine(fixed_params=dict(dataset_cls=FlattenedIsaJsonDataset)))
def flatten_isa_json(dataset: IsaJsonDataset) -> FlattenedIsaJsonDataset:
    ...
