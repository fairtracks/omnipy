from collections.abc import Hashable, Iterable
import inspect
import locale as pkg_locale
from types import UnionType
from typing import (Annotated,
                    Any,
                    cast,
                    ClassVar,
                    get_args,
                    get_origin,
                    Mapping,
                    Protocol,
                    Type,
                    TypeVar,
                    Union)

from typing_inspect import get_generic_bases, is_generic_type

from omnipy.api.typedefs import LocaleType

KeyT = TypeVar('KeyT', bound=Hashable)

Dictable = Mapping[KeyT, Any] | Iterable[tuple[KeyT, Any]]


def as_dictable(obj: object) -> Dictable | None:
    def _is_iterable_of_tuple_pairs(obj_inner: object) -> bool:
        return isinstance(obj_inner, Iterable) and \
            all(isinstance(el, tuple) and len(el) == 2 for el in obj_inner)

    if isinstance(obj, Mapping) or _is_iterable_of_tuple_pairs(obj):
        return cast(Dictable, obj)
    else:
        return None


def create_merged_dict(dictable_1: Dictable[KeyT], dictable_2: Dictable[KeyT]) -> dict[KeyT, Any]:
    merged_dict = dictable_1 if isinstance(dictable_1, dict) else dict(dictable_1)
    dict_2 = dictable_2 if isinstance(dictable_2, dict) else dict(dictable_2)
    merged_dict |= dict_2
    return merged_dict


def remove_none_vals(**kwargs: object) -> dict[object, object]:
    return {key: val for key, val in kwargs.items() if val is not None}


def get_datetime_format(locale: LocaleType | None = None) -> str:
    pkg_locale.setlocale(pkg_locale.LC_ALL, locale)

    if hasattr(pkg_locale, 'nl_langinfo'):  # noqa
        datetime_format = pkg_locale.nl_langinfo(pkg_locale.D_T_FMT)
    else:
        datetime_format = '%a %b %e %X %Y'
    return datetime_format


async def resolve(val):
    return await val if inspect.isawaitable(val) else val


def repr_max_len(data: object, max_len: int = 200):
    repr_str = repr(data)
    return f'{repr_str[:max_len]}...' if len(repr_str) > max_len else repr_str


def get_bases(cls):
    return get_generic_bases(cls) if is_generic_type(cls) else cls.__bases__


def generic_aware_issubclass_ignore_args(cls, cls_or_tuple):
    try:
        return issubclass(cls, cls_or_tuple)
    except TypeError:
        return issubclass(get_origin(cls), cls_or_tuple)


def transfer_generic_args_to_cls(to_cls, from_generic_type):
    try:
        return to_cls[get_args(from_generic_type)]
    except (TypeError, AttributeError):
        return to_cls


def is_iterable(obj: object) -> bool:
    try:
        iter(obj)
        return True
    except TypeError:
        return False


def is_union(cls_or_type: type | UnionType | None | object) -> bool:
    return get_origin(cls_or_type) in [Union, UnionType]


def is_optional(cls_or_type: type | UnionType | None | object) -> bool:
    return is_union(cls_or_type) and type(None) in get_args(cls_or_type)


def is_strict_subclass(
        __cls: type,
        __class_or_tuple: type | UnionType | tuple[type | UnionType | tuple[Any, ...], ...]
) -> bool:
    if issubclass(__cls, __class_or_tuple):
        if isinstance(__class_or_tuple, Iterable):
            return __cls not in __class_or_tuple
        else:
            return __cls != __class_or_tuple
    return False


class IsDataclass(Protocol):
    __dataclass_fields__: ClassVar[dict]


def remove_annotated_plus_optional_if_present(
        type_or_class: Type | UnionType | object) -> Type | UnionType | object:
    if get_origin(type_or_class) == Annotated:
        type_or_class = get_args(type_or_class)[0]
        if is_optional(type_or_class):
            args = get_args(type_or_class)
            if len(args) == 2:
                type_or_class = args[0]
            else:
                type_or_class = Union[args[:-1]]
    return type_or_class
