import inspect
import locale as pkg_locale
from typing import Dict, get_args, get_origin, Iterable, Mapping, Optional, Tuple, Union

from typing_inspect import get_generic_bases, is_generic_type

from omnipy.api.types import LocaleType

DictT = Union[Mapping[object, object], Iterable[Tuple[object, object]]]


def create_merged_dict(dict_1: DictT, dict_2: DictT) -> Dict[object, object]:
    merged_dict = dict(dict_1)
    dict_2_cast = dict(dict_2)
    merged_dict |= dict_2_cast
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
