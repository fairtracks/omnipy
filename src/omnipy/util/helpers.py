import asyncio
from collections.abc import Hashable, Iterable
import functools
from importlib.abc import Loader
from importlib.machinery import FileFinder, ModuleSpec
import inspect
from inspect import getmodule, isclass
from keyword import iskeyword, issoftkeyword
import locale as pkg_locale
import operator
import sys
from types import GenericAlias, ModuleType, NoneType, UnionType
from typing import _AnnotatedAlias  # type: ignore[attr-defined]
from typing import _LiteralGenericAlias  # type: ignore[attr-defined]
from typing import _LiteralSpecialForm  # type: ignore[attr-defined]
from typing import _UnionGenericAlias  # type: ignore[attr-defined]
from typing import (_SpecialForm,
                    Any,
                    cast,
                    ClassVar,
                    ForwardRef,
                    get_args,
                    get_origin,
                    Mapping,
                    overload,
                    Protocol,
                    TypeGuard,
                    Union)

from typing_extensions import TypeVar

from omnipy.shared.typedefs import LocaleType, TypeForm
import omnipy.util._pydantic as pyd

_KeyT = TypeVar('_KeyT', bound=Hashable)
_ObjT = TypeVar('_ObjT', bound=object)

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
    return {key: obj for key, obj in kwargs.items() if obj is not None}


def get_datetime_format(locale: LocaleType | None = None) -> str:
    pkg_locale.setlocale(pkg_locale.LC_ALL, locale)

    if hasattr(pkg_locale, 'nl_langinfo'):  # noqa
        datetime_format = pkg_locale.nl_langinfo(pkg_locale.D_T_FMT)
    else:
        datetime_format = '%a %b %e %X %Y'
    return datetime_format


async def resolve(obj):
    return await obj if inspect.isawaitable(obj) else obj


def repr_max_len(data: object, max_len: int = 200):
    repr_str = repr(data)
    return f'{repr_str[:max_len]}...' if len(repr_str) > max_len else repr_str


def get_parametrized_type(obj: object):
    return getattr(obj, '__orig_class__', type(obj))


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


@overload
def ensure_plain_type(in_type: ForwardRef) -> ForwardRef:
    ...


@overload
def ensure_plain_type(in_type: TypeVar) -> TypeVar:
    ...


@overload
def ensure_plain_type(in_type: type | GenericAlias | UnionType) -> type:
    ...


@overload
def ensure_plain_type(in_type: _SpecialForm) -> _SpecialForm:
    ...


@overload
def ensure_plain_type(
    in_type: _LiteralGenericAlias | _UnionGenericAlias | _AnnotatedAlias
) -> _LiteralSpecialForm | type:
    ...


def ensure_plain_type(
        in_type: TypeForm) -> ForwardRef | TypeVar | type | _SpecialForm | _LiteralSpecialForm:

    if in_type == NoneType:
        return None

    origin = get_origin(in_type)
    if origin == Union:
        return UnionType
    else:
        return cast(type | ForwardRef | TypeVar, origin if get_args(in_type) else in_type)


def evaluate_any_forward_refs_if_possible(in_type: TypeForm,
                                          calling_module: str | None = None,
                                          **localns) -> TypeForm:
    if not calling_module:
        calling_module = get_calling_module_name() if 'ForwardRef' in str(in_type) else None

    if isinstance(in_type, ForwardRef):
        if calling_module and calling_module in sys.modules:
            globalns = sys.modules[calling_module].__dict__.copy()
        else:
            globalns = {}
        try:
            return cast(
                type | GenericAlias,
                in_type._evaluate(
                    globalns, localns if localns else locals(), recursive_guard=set()))
        except NameError:
            pass
    else:
        origin = get_origin(in_type)
        args = get_args(in_type)
        if origin and args:
            new_args = tuple(
                evaluate_any_forward_refs_if_possible(arg, calling_module, **localns)
                for arg in args)
            if origin == UnionType:
                return functools.reduce(operator.or_, new_args)
            else:
                return origin[new_args]
    return in_type


def get_default_if_typevar(typ_: type[_ObjT] | TypeForm | TypeVar) -> type[_ObjT] | TypeForm:
    if isinstance(typ_, TypeVar):
        if hasattr(typ_, '__default__'):
            return typ_.__default__
        else:
            raise TypeError(f'The TypeVar "{typ_.__name__}" needs to specify a default value. '
                            f'This requires Python 3.13, but is supported in earlier versions '
                            f'of Python by importing TypeVar from the library '
                            f'"typing-extensions".')
    return typ_


def all_type_variants(
    in_type: type | GenericAlias | UnionType | _UnionGenericAlias
) -> tuple[type | GenericAlias, ...]:
    if is_union(in_type):
        return get_args(in_type)
    else:
        return (cast(type | GenericAlias, in_type),)


def is_iterable(obj: Iterable[_ObjT] | _ObjT) -> TypeGuard[Iterable[_ObjT]]:
    try:
        iter(obj)  # type: ignore[arg-type]
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


@functools.cache
def is_union(cls_or_type: type | UnionType | None | object) -> bool:
    union_types = [Union, UnionType]
    return cls_or_type in union_types or get_origin(cls_or_type) in union_types


@functools.cache
def is_optional(cls_or_type: type | UnionType | None | object) -> bool:
    return is_union(cls_or_type) and any(pyd.is_none_type(arg) for arg in get_args(cls_or_type))


def all_equals(first, second) -> bool:
    equals = first == second
    if is_iterable(equals):
        if hasattr(equals, 'all') and callable(getattr(equals, 'all')):
            return equals.all(None)  # works for both pandas and numpy
        else:
            return all(equals)
    else:
        return equals


@functools.cache
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
    return type(obj).__bases__ == (pyd.BaseModel,)


def is_non_omnipy_pydantic_model(obj: object):
    from omnipy.data.dataset import Dataset
    from omnipy.data.model import Model

    mro = type(obj).__mro__
    return mro[0] != pyd.BaseModel \
        and (pyd.BaseModel in mro or pyd.GenericModel in mro) \
        and Model not in mro \
        and Dataset not in mro


class IsDataclass(Protocol):
    __dataclass_fields__: ClassVar[dict]


def is_unreserved_identifier(identifier: str) -> bool:
    return identifier.isidentifier() and not iskeyword(identifier) and not issoftkeyword(identifier)


def remove_forward_ref_notation(type_str: str):
    return type_str.replace("ForwardRef('", '').replace("')", '')


def format_classname_with_params(cls_name: str, params_str: str) -> str:
    return f'{cls_name}[{params_str}]'


def _is_internal_module(module: ModuleType, imported_modules: list[ModuleType]):
    return module not in imported_modules and module.__name__.startswith('omnipy')


def recursive_module_import_new(root_path: list[str],
                                imported_modules: dict[str, ModuleType],
                                excluded_set: set[str]):

    import pkgutil

    module_finder: FileFinder
    module_name: str
    is_pkg: bool

    cur_excluded_prefix = ''

    for module_finder, module_name, is_pkg in pkgutil.walk_packages(root_path):  # type: ignore
        # print(f'{module_name}: {is_pkg}')
        if cur_excluded_prefix and module_name.startswith(cur_excluded_prefix):
            continue
        else:
            cur_excluded_prefix = ''

        if module_name in excluded_set:
            cur_excluded_prefix = f'{module_name}.'
            continue

        module_spec: ModuleSpec | None = module_finder.find_spec(module_name)
        if module_spec:
            loader: Loader | None = module_spec.loader
            if loader:
                imported_modules[module_name] = loader.load_module(module_name)


def recursive_module_import(module: ModuleType,
                            imported_modules: list[ModuleType] = []) -> dict[str, object]:
    module_vars = vars(module)
    imported_modules.append(module)

    for obj in module_vars.values():
        if isclass(obj):
            for base_cls in obj.__bases__:
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


def get_event_loop_and_check_if_loop_is_running() -> tuple[asyncio.AbstractEventLoop | None, bool]:
    loop_is_running: bool
    loop: asyncio.AbstractEventLoop | None = None

    try:
        loop = asyncio.get_event_loop()
        loop_is_running = loop.is_running()
    except RuntimeError:
        loop_is_running = False

    return loop, loop_is_running


def running_in_ipython() -> bool:
    try:
        return get_ipython().__class__.__name__ == 'TerminalInteractiveShell'
    except NameError:
        return False


def running_in_jupyter() -> bool:
    try:
        return get_ipython().__class__.__name__ == 'ZMQInteractiveShell'
    except NameError:
        return False
