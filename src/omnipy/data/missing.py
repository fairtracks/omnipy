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
# together with hacks setting allow_none=True (_ModelMetaclass and _recursively_set_allow_none).
# See series of relevant tests in test_model.py starting with  test_list_of_none_variants().
def parse_none_according_to_model(value: _RootT, root_model) -> _RootT:  # IsModel
    outer_type = root_model.outer_type(with_args=True)
    plain_outer_type = root_model.outer_type(with_args=False)
    outer_args = get_args(outer_type)

    if is_model_subclass(outer_type):
        return _parse_none_in_model(outer_type, value)

    if root_model.is_nested_type():
        inner_val_type = root_model.inner_type(with_args=True)

        # Mutable sequences or variable tuples
        if _outer_type_and_value_are_of_types(plain_outer_type, value, (MutableSequence, tuple)):
            return _parse_none_in_mutable_sequence_or_tuple(plain_outer_type, inner_val_type, value)

        # Mappings
        if _outer_type_and_value_are_of_types(plain_outer_type, value, Mapping) and outer_args:
            return _parse_none_in_mapping(plain_outer_type, outer_args, inner_val_type, value)

        if lenient_isinstance(outer_type, TypeVar):
            return _parse_none_in_typevar(inner_val_type)

        if value is None:
            raise OmnipyNoneIsNotAllowedError()

    else:
        union_variants = _split_outer_type_to_union_variants(outer_args)
        flattened_union_variants = _flatten_two_level_tuple(union_variants)

        if any(is_model_subclass(tp_) or _supports_none(tp_) for tp_ in flattened_union_variants):

            # Fixed tuples
            if _outer_type_and_value_are_of_types(plain_outer_type, value, tuple) and outer_args:
                return _parse_none_in_fixed_tuple(plain_outer_type, union_variants, value)

            # Unions
            if is_union(plain_outer_type):
                return _parse_none_in_union(flattened_union_variants, value)

    return value


def _parse_none_in_model(outer_type, value):
    return outer_type(value)


def _split_to_union_variants(type_: TypeForm) -> tuple[TypeForm]:
    return get_args(type_) if is_union(type_) else (type_,)


def _split_outer_type_to_union_variants(outer_type_args):
    return tuple(_split_to_union_variants(_) for _ in outer_type_args)


def _flatten_two_level_tuple(two_level_tuple):
    return tuple(el for first_level_tuple in two_level_tuple for el in first_level_tuple)


def _supports_none(type_: TypeForm) -> bool:
    return is_none_type(type_) or is_optional(type_) or type_ in (object, Any)


def _outer_type_and_value_are_of_types(plain_outer_type, value, *types):
    return any(
        lenient_issubclass(plain_outer_type, type_) and lenient_isinstance(value, type_)
        for type_ in types)


def _parse_none_in_mutable_sequence_or_tuple(plain_outer_type, inner_val_type, value):
    inner_val_union_types = _split_to_union_variants(inner_val_type)

    if any(is_model_subclass(_) or _supports_none(_) for _ in inner_val_union_types):
        return plain_outer_type(
            _parse_none_in_types(inner_val_union_types) if val is None else val for val in value)
    return value


def _parse_none_in_mapping(plain_outer_type, outer_type_args, inner_val_type, value):
    inner_val_union_types = _split_to_union_variants(inner_val_type)

    inner_key_type = outer_type_args[0] if lenient_issubclass(
        plain_outer_type, Mapping) and outer_type_args else Undefined
    inner_key_union_types = _split_to_union_variants(inner_key_type)

    if any(
            is_model_subclass(_) or _supports_none(_)
            for _ in chain(inner_key_union_types, inner_val_union_types)):
        return plain_outer_type({
            _parse_none_in_types(inner_key_union_types) if key is None else key:
                _parse_none_in_types(inner_val_union_types) if val is None else val for key,
            val in value.items()
        })
    return value


def _parse_none_in_typevar(inner_val_type):
    inner_val_union_types = _split_to_union_variants(inner_val_type)

    return _parse_none_in_types(inner_val_union_types)


def _parse_none_in_fixed_tuple(plain_outer_type, tuple_of_union_variant_types, value):
    return plain_outer_type(
        _parse_none_in_types(tuple_of_union_variant_types[i]) if val is None else val for i,
        val in enumerate(value))


def _parse_none_in_union(flattened_union_variant_types, value):
    if value is None:
        return _parse_none_in_types(flattened_union_variant_types)
    else:
        return value


def _parse_none_in_types(inner_union_types: tuple[TypeForm]) -> object:
    for type_ in inner_union_types:
        if is_model_subclass(type_):
            return type_(parse_none_according_to_model(None, type_))
        elif _supports_none(type_):
            return None
    raise OmnipyNoneIsNotAllowedError()
