import functools

from typing_extensions import TypeIs

import omnipy.data.model
from omnipy.shared.typedefs import TypeForm
from omnipy.util._pydantic import is_none_type, lenient_isinstance, lenient_issubclass

__all__ = [
    'is_model_instance',
    'is_model_subclass',
    'obj_or_model_contents_isinstance',
]


def is_model_instance(__obj: object) -> 'TypeIs[omnipy.data.model.Model]':
    from omnipy.data.model import Model
    return lenient_isinstance(__obj, Model) \
        and not is_none_type(__obj)  # Consequence of _ModelMetaclass hack


@functools.cache
def is_model_subclass(__cls: TypeForm) -> 'TypeIs[type[omnipy.data.model.Model]]':
    from omnipy.data.model import Model
    return lenient_issubclass(__cls, Model) \
        and not is_none_type(__cls)  # Consequence of _ModelMetaclass hack


def obj_or_model_contents_isinstance(__obj: object, __class_or_tuple: type) -> bool:
    return isinstance(__obj.contents if is_model_instance(__obj) else __obj, __class_or_tuple)
