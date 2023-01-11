import inspect
import locale as pkg_locale
from typing import Dict, Iterable, Mapping, Tuple, Union

DictT = Union[Mapping[object, object], Iterable[Tuple[object, object]]]


def create_merged_dict(dict_1: DictT, dict_2: DictT) -> Dict[object, object]:
    merged_dict = dict(dict_1)
    dict_2_cast = dict(dict_2)
    merged_dict.update(dict_2_cast)
    return merged_dict


def remove_none_vals(**kwargs: object) -> Dict[object, object]:
    return {key: val for key, val in kwargs.items() if val is not None}


def get_datetime_format(locale: Union[str, Tuple[str, str]] = '') -> str:
    pkg_locale.setlocale(pkg_locale.LC_ALL, locale)

    if hasattr(pkg_locale, 'nl_langinfo'):  # noqa
        datetime_format = pkg_locale.nl_langinfo(pkg_locale.D_T_FMT)
    else:
        datetime_format = '%a %b %e %X %Y'
    return datetime_format


async def resolve(val):
    if inspect.isawaitable(val):
        return await val
    else:
        return val
