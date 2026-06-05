from types import GenericAlias

from omnipy.data.dataset import is_dataset_subclass
from omnipy.data.model import is_model_subclass
from omnipy.shared.protocols.data import IsDataset, IsModel
from omnipy.util.helpers import all_type_variants


def all_model_type_variants(model: type[IsModel] | IsModel,) -> tuple[type | GenericAlias, ...]:
    return tuple(all_type_variants(model.full_type()))


def all_dataset_type_variants(
        dataset: type[IsDataset] | IsDataset) -> tuple[type | GenericAlias, ...]:
    _type = dataset.get_type()

    type_variants: list[type | GenericAlias] = []

    for variant in all_type_variants(_type):
        if is_model_subclass(variant):
            type_variants += all_model_type_variants(variant)
        elif is_dataset_subclass(variant):
            type_variants.append(variant)

    return tuple(type_variants)
