"""Flows for transforming ISA-JSON datasets into flattened tabular-like structures."""

from omnipy.compute.flow import LinearFlowTemplate

from ..general.tasks import create_dataset_args
from ..json.datasets import JsonDictOfDictsDataset
from ..json.flows import flatten_nested_json, transpose_dict_of_dicts_2_list_of_dicts
from .datasets import FlattenedIsaJsonDataset, IsaJsonDataset


@LinearFlowTemplate(
    create_dataset_args.refine(fixed_params=dict(dataset_cls=JsonDictOfDictsDataset)),
    transpose_dict_of_dicts_2_list_of_dicts,
    flatten_nested_json,
    create_dataset_args.refine(fixed_params=dict(dataset_cls=FlattenedIsaJsonDataset)))
def flatten_isa_json(dataset: IsaJsonDataset) -> FlattenedIsaJsonDataset:
    """Flatten ISA-JSON documents into tabular-like records.

    The flow converts each ISA document to an intermediate dictionary-of-dictionaries
    representation, transposes that structure into record lists, and then flattens
    nested keys into scalar columns.

    Args:
        dataset: Dataset with ISA-JSON documents to flatten.

    Returns:
        A dataset containing flattened ISA records suitable for tabular workflows.
    """
    ...
