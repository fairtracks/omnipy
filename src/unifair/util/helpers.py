import inspect
import locale as pkg_locale
from typing import Any, Dict, Mapping, Tuple, Union


def create_merged_dict(dict_1: Union[Mapping[Any, Any]],
                       dict_2: Union[Mapping[Any, Any]]) -> Dict[Any, Any]:
    merged_dict = dict(dict_1)
    merged_dict.update(dict_2)
    return merged_dict


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
