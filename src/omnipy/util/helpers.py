from collections.abc import Hashable, Iterable
from copy import copy, deepcopy
import inspect
from inspect import getmodule, isclass
import locale as pkg_locale
from types import GenericAlias, ModuleType, UnionType
from typing import (Annotated,
                    Any,
                    cast,
                    ClassVar,
                    get_args,
                    get_origin,
                    Mapping,
                    NamedTuple,
                    Protocol,
                    Type,
                    TypeVar,
                    Union)

from isort import place_module
from isort.sections import STDLIB
from pydantic import BaseModel, ValidationError
from pydantic.generics import GenericModel
from pydantic.typing import display_as_type
from typing_inspect import get_generic_bases, is_generic_type

from omnipy.api.typedefs import LocaleType

_KeyT = TypeVar('_KeyT', bound=Hashable)

Dictable = Mapping[_KeyT, Any] | Iterable[tuple[_KeyT, Any]]


def as_dictable(obj: object) -> Dictable | None:
    def _is_iterable_of_tuple_pairs(obj_inner: object) -> bool:
        return isinstance(obj_inner, Iterable) and \
            all(isinstance(el, tuple) and len(el) == 2 for el in obj_inner)

    if isinstance(obj, Mapping) or _is_iterable_of_tuple_pairs(obj):
        return cast(Dictable, obj)
    else:
        return None


def create_merged_dict(dictable_1: Dictable[_KeyT],
                       dictable_2: Dictable[_KeyT]) -> dict[_KeyT, Any]:
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


def ensure_plain_type(in_type: type | GenericAlias) -> type | GenericAlias | None | Any:
    return get_origin(in_type) if get_args(in_type) else in_type


def is_iterable(obj: object) -> bool:
    try:
        iter(obj)
        return True
    except TypeError:
        return False


def is_non_str_byte_iterable(obj: object) -> bool:
    return is_iterable(obj) and not type(obj) in (str, bytes)


def ensure_non_str_byte_iterable(value):
    return value if is_non_str_byte_iterable(value) else (value,)


def has_items(obj: object) -> bool:
    return hasattr(obj, '__len__') and obj.__len__() > 0


def get_first_item(iterable: Iterable[object]) -> object:
    assert has_items(iterable)
    for item in iterable:
        return item


def is_union(cls_or_type: type | UnionType | None | object) -> bool:
    union_types = [Union, UnionType]
    return cls_or_type in union_types or get_origin(cls_or_type) in union_types


def is_optional(cls_or_type: type | UnionType | None | object) -> bool:
    return is_union(cls_or_type) and type(None) in get_args(cls_or_type)


def all_equals(first, second) -> bool:
    equals = first == second
    if is_iterable(equals):
        if hasattr(equals, 'all') and callable(getattr(equals, 'all')):
            return equals.all(None)  # works for both pandas and numpy
        else:
            return all(equals)
    else:
        return equals


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


def is_pure_pydantic_model(obj: object):
    return type(obj).__bases__ == (BaseModel,)


def is_non_omnipy_pydantic_model(obj: object):
    from omnipy.data.dataset import Dataset
    from omnipy.data.model import Model

    mro = type(obj).__mro__
    return mro[0] != BaseModel \
        and (BaseModel in mro or GenericModel in mro) \
        and Model not in mro \
        and Dataset not in mro


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


def remove_forward_ref_notation(type_str: str):
    return type_str.replace("ForwardRef('", '').replace("')", '')


def generate_qualname(cls_name: str, model: Any) -> str:
    m_module = model.__module__ if hasattr(model, '__module__') else ''
    m_module_prefix = f'{m_module}.' if m_module and place_module(m_module) != STDLIB else ''
    fully_qual_model_name = f'{m_module_prefix}{display_as_type(model)}'
    return f'{cls_name}[{fully_qual_model_name}]'


class Snapshot(NamedTuple):
    id: int
    obj_copy: object


class RestorableContents:
    def __init__(self):
        self._last_snapshot: Snapshot | None = None

    def has_snapshot(self) -> bool:
        return self._last_snapshot is not None

    def take_snapshot(self, obj: object):
        try:
            snapshot_obj = deepcopy(obj)
        except (TypeError, ValueError, ValidationError):
            snapshot_obj = copy(obj)
        self._last_snapshot = Snapshot(id(obj), snapshot_obj)

    def _assert_not_empty(self):
        assert self.has_snapshot(), 'No snapshot has been taken yet'

    def get_last_snapshot(self) -> object:
        self._assert_not_empty()
        return self._last_snapshot.obj_copy

    def last_snapshot_taken_of_same_obj(self, obj: object) -> bool:
        self._assert_not_empty()
        return self._last_snapshot.id == id(obj)

    def differs_from_last_snapshot(self, obj: object) -> bool:
        self._assert_not_empty()
        return not all_equals(self._last_snapshot.obj_copy, obj)


def _is_internal_module(module: ModuleType, imported_modules: list[ModuleType]):
    return module not in imported_modules and module.__name__.startswith('omnipy')


def recursive_module_import(module: ModuleType, imported_modules: list[ModuleType] = []):
    module_vars = vars(module)
    imported_modules.append(module)

    for val in module_vars.values():
        if isclass(val):
            for base_cls in val.__bases__:
                base_cls_module = getmodule(base_cls)
                if base_cls_module and _is_internal_module(base_cls_module, imported_modules):
                    module_vars = create_merged_dict(
                        recursive_module_import(base_cls_module, imported_modules),
                        module_vars,
                    )

    return module_vars


def get_calling_module_name() -> str | None:
    stack = inspect.stack()
    start_frame_index = 2
    while len(stack) > start_frame_index:
        grandparent_frame = stack[start_frame_index][0]
        module = inspect.getmodule(grandparent_frame)
        if module is not None:
            return module.__name__
        start_frame_index += 1


def called_from_omnipy_tests() -> bool:
    stack = inspect.stack()
    for index in range(len(stack)):
        frame = stack[index][0]
        module = inspect.getmodule(frame)
        if module is not None \
                and module.__name__.startswith('tests') \
                and module.__file__ is not None \
                and 'omnipy/tests' in module.__file__:
            return True
    return False
