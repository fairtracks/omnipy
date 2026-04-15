import functools
from types import GenericAlias
from typing import cast

from typing_extensions import TypeIs, TypeVar

from omnipy.shared.protocols.data import IsDataset, IsModel
from omnipy.shared.typedefs import TypeForm
from omnipy.shared.typing import TYPE_CHECKING
from omnipy.util._pydantic import is_none_type, lenient_isinstance, lenient_issubclass
from omnipy.util.helpers import all_type_variants

if TYPE_CHECKING:
    from omnipy.data.dataset import Dataset
    from omnipy.data.model import Model

__all__ = [
    'is_model_instance',
    'is_model_subclass',
    'is_dataset_subclass',
    'obj_or_model_content_isinstance',
]


def is_model_instance(__obj: object) -> 'TypeIs[Model]':
    from omnipy.data.model import Model
    return lenient_isinstance(__obj, Model) \
        and not is_none_type(__obj)  # Consequence of _ModelMetaclass hack


@functools.cache
def is_model_subclass(__cls: TypeForm) -> 'TypeIs[type[Model]]':
    from omnipy.data.model import Model
    return lenient_issubclass(__cls, Model) \
        and not is_none_type(__cls)  # Consequence of _ModelMetaclass hack


def is_dataset_instance(__obj: object) -> 'TypeIs[Dataset]':
    from omnipy.data.dataset import Dataset
    return lenient_isinstance(__obj, Dataset)


@functools.cache
def is_dataset_subclass(__cls: TypeForm) -> 'TypeIs[type[Dataset]]':
    from omnipy.data.dataset import Dataset
    return lenient_issubclass(__cls, Dataset)


ClassOrTupleT = TypeVar('ClassOrTupleT')


def obj_or_model_content_isinstance(
    __obj: object,
    __class_or_tuple: type[ClassOrTupleT] | tuple[type[ClassOrTupleT], ...],
) -> TypeIs[ClassOrTupleT]:
    return isinstance(__obj.content if is_model_instance(__obj) else __obj, __class_or_tuple)


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
