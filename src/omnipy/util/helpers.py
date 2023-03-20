from __future__ import annotations

import inspect
import locale as pkg_locale
from typing import cast, Dict, get_args, get_origin, Iterable, Mapping, Optional, Tuple, Union

from typing_inspect import get_generic_bases, is_generic_type

from omnipy.api.types import LocaleType

Dictable = Union[Mapping[object, object], Iterable[Tuple[object, object]]]


def as_dictable(obj: object) -> Optional[Dictable]:
    def _is_iterable_of_tuple_pairs(obj_inner: object) -> bool:
        return isinstance(obj_inner, Iterable) and \
            all(isinstance(el, tuple) and len(el) == 2 for el in obj_inner)

    if isinstance(obj, Mapping) or _is_iterable_of_tuple_pairs(obj):
        return cast(Dictable, obj)
    else:
        return None


def create_merged_dict(dictable_1: Dictable, dictable_2: Dictable) -> Dict[object, object]:
    merged_dict = dictable_1 if isinstance(dictable_1, dict) else dict(dictable_1)
    dict_2 = dictable_2 if isinstance(dictable_2, dict) else dict(dictable_2)
    merged_dict |= dict_2
    return merged_dict


def remove_none_vals(**kwargs: object) -> Dict[object, object]:
    return {key: val for key, val in kwargs.items() if val is not None}


def get_datetime_format(locale: Optional[LocaleType] = None) -> str:
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
