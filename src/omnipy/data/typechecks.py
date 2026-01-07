import functools
from types import GenericAlias, UnionType
from typing import TYPE_CHECKING

from typing_extensions import TypeIs

from omnipy.shared.protocols.data import IsDataset
from omnipy.shared.typedefs import TypeForm
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


def obj_or_model_content_isinstance(
    __obj: object,
    __class_or_tuple: type | tuple[type, ...] | UnionType,
) -> bool:
    return isinstance(__obj.content if is_model_instance(__obj) else __obj, __class_or_tuple)


def all_dataset_type_variants(dataset: IsDataset) -> tuple[type | GenericAlias, ...]:
    _type = dataset.get_type()
    if is_model_subclass(_type):
        _type = _type.full_type()
    return all_type_variants(_type)
