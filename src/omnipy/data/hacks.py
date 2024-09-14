from itertools import chain
from typing import Any, get_args, Mapping, MutableSequence

from pydantic.fields import Undefined
from pydantic.typing import is_none_type
from pydantic.utils import lenient_isinstance, lenient_issubclass
from typing_extensions import TypeVar

from omnipy.api.exceptions import OmnipyNoneIsNotAllowedError
from omnipy.api.typedefs import TypeForm
from omnipy.data.helpers import is_model_subclass
from omnipy.util.helpers import is_optional, is_union

_RootT = TypeVar('_RootT')


# Partial workaround of https://github.com/pydantic/pydantic/issues/3836 and similar bugs,
# together withhacks setting allow_none=True (_ModelMetaclass and _recursively_set_allow_none).
# See series of relevant tests in test_model.py starting with  test_list_of_none_variants().
def parse_none_value_according_to_model(
        value: _RootT,
        root_model,  # IsModel
) -> _RootT:
    outer_type = root_model.outer_type(with_args=True)
    plain_outer_type = root_model.outer_type(with_args=False)
    outer_type_args = get_args(outer_type)

    inner_key_type = outer_type_args[0] if lenient_issubclass(
        plain_outer_type, Mapping) and outer_type_args else Undefined
    inner_val_type = root_model.inner_type(with_args=True)

    if is_model_subclass(outer_type):
        return outer_type(value)

    def _split_to_union_variants(type_: TypeForm) -> tuple[TypeForm]:
        return get_args(type_) if is_union(type_) else (type_,)

    def _supports_none(type_: TypeForm) -> bool:
        return is_none_type(type_) or is_optional(type_) or type_ in (object, Any)

    def _parse_none_value(inner_union_types: tuple[TypeForm]) -> object:
        for type_ in inner_union_types:
            if is_model_subclass(type_):
                return type_(parse_none_value_according_to_model(None, type_))
            elif _supports_none(type_):
                return None
        raise OmnipyNoneIsNotAllowedError()

    if root_model.is_nested_type():
        inner_val_union_types = _split_to_union_variants(inner_val_type)

        # Mutable sequences or variable tuples
        if lenient_issubclass(plain_outer_type, (MutableSequence, tuple)) and lenient_isinstance(
                value, plain_outer_type):
            if any(is_model_subclass(_) or _supports_none(_) for _ in inner_val_union_types):
                return plain_outer_type(
                    _parse_none_value(inner_val_union_types) if val is None else val
                    for val in value)

        # Mappings
        if lenient_issubclass(plain_outer_type, Mapping) and lenient_isinstance(
                value, Mapping) and outer_type_args:

            inner_key_union_types = _split_to_union_variants(inner_key_type)

            if any(
                    is_model_subclass(_) or _supports_none(_)
                    for _ in chain(inner_key_union_types, inner_val_union_types)):
                return plain_outer_type({
                    _parse_none_value(inner_key_union_types) if key is None else key:
                        _parse_none_value(inner_val_union_types) if val is None else val for key,
                    val in value.items()
                })

        if lenient_isinstance(outer_type, TypeVar):
            return _parse_none_value(inner_val_union_types)

        if value is None:
            raise OmnipyNoneIsNotAllowedError()

    else:
        tuple_of_union_variant_types = [_split_to_union_variants(_) for _ in outer_type_args]
        flattened_union_variant_types = [
            type_ for union_variant_types in tuple_of_union_variant_types
            for type_ in union_variant_types
        ]
        if any(is_model_subclass(type_) or _supports_none(type_) \
               for type_ in flattened_union_variant_types):

            # Fixed tuples
            if lenient_issubclass(plain_outer_type, tuple) and lenient_isinstance(
                    value, tuple) and outer_type_args:
                assert len(value) == len(outer_type_args) and outer_type_args[-1] is not Ellipsis
                return plain_outer_type(
                    _parse_none_value(tuple_of_union_variant_types[i]) if val is None else val
                    for i,
                    val in enumerate(value))

            # Unions
            elif is_union(plain_outer_type):
                if value is None:
                    return _parse_none_value(flattened_union_variant_types)
                else:
                    return value
    return value
