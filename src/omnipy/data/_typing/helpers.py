from types import GenericAlias
from typing import cast

from omnipy.data.dataset import is_dataset_subclass
from omnipy.data.model import is_model_subclass
from omnipy.shared.protocols.data import IsDataset, IsModel
from omnipy.util.helpers import all_type_variants


def all_model_type_variants(
    model: type[IsModel] | IsModel,
    double_model_unions_as_variants: bool,
) -> tuple[type | GenericAlias, ...]:
    # For double Models, e.g. Model[Model[int]],
    # _get_real_content() have already skipped the outer Model
    # to get the real content value, provided here as `ret`.
    # In order to check if `ret` can be expressed as a Model
    # variant, we need to flatten double models to get to the
    # relevant type variants for the check. For example, for
    # `Model[Model[int]]`, we need to check if `ret` can be
    # expressed as `Model[int]`.
    #
    # If `double_model_unions_as_variants` is `True`, we also
    # consider variants defined by Unions inside doubled
    # Models. In this case, e.g. `Model[int | str]`,
    # `Model[Model[int | str]]` and `Model[Model[int] |
    # Model[str]]` should all return `{int, str}` as the types
    # to check against.
    model_type_variants = []
    for type_to_check in all_type_variants(model.full_type()):
        if is_model_subclass(type_to_check):
            model_full_type = cast(IsModel, type_to_check).full_type()
            if double_model_unions_as_variants:
                for type_variant in all_type_variants(model_full_type):
                    if type_variant not in model_type_variants:
                        model_type_variants.append(type_variant)
            else:
                model_type_variants.append(model_full_type)
        else:
            model_type_variants.append(type_to_check)
    return tuple(model_type_variants)


def all_dataset_type_variants(
        dataset: type[IsDataset] | IsDataset) -> tuple[type | GenericAlias, ...]:
    _type = dataset.get_type()

    type_variants: list[type | GenericAlias] = []

    for variant in all_type_variants(_type):
        if is_model_subclass(variant):
            type_variants += all_model_type_variants(variant, double_model_unions_as_variants=True)
        elif is_dataset_subclass(variant):
            type_variants.append(variant)

    return tuple(type_variants)
