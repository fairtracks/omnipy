from omnipy.compute.flow import LinearFlowTemplate
from omnipy.compute.typing import mypy_fix_linear_flow_template

from ..general.tasks import convert_dataset
from ..json.datasets import JsonDictOfDictsDataset
from ..json.flows import flatten_nested_json, transpose_dict_of_dicts_2_list_of_dicts
from .datasets import FlattenedIsaJsonDataset, IsaJsonDataset


@mypy_fix_linear_flow_template
@LinearFlowTemplate(
    convert_dataset.refine(fixed_params=dict(dataset_cls=JsonDictOfDictsDataset)),
    transpose_dict_of_dicts_2_list_of_dicts,
    flatten_nested_json,
    convert_dataset.refine(fixed_params=dict(dataset_cls=FlattenedIsaJsonDataset)))
def flatten_isa_json(dataset: IsaJsonDataset) -> FlattenedIsaJsonDataset:
    ...
