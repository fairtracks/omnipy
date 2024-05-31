from abc import ABCMeta
from collections import defaultdict, UserDict
from collections.abc import Hashable, Iterable
from copy import copy, deepcopy
from dataclasses import dataclass
import functools
import gc
import inspect
from inspect import getmodule, isclass
import locale as pkg_locale
import operator
import sys
import traceback
from types import GenericAlias, ModuleType, NoneType, UnionType
from typing import _AnnotatedAlias  # type: ignore[attr-defined]
from typing import _LiteralGenericAlias  # type: ignore[attr-defined]
from typing import _LiteralSpecialForm  # type: ignore[attr-defined]
from typing import _UnionGenericAlias  # type: ignore[attr-defined]
from typing import (_SpecialForm,
                    Annotated,
                    Any,
                    Callable,
                    cast,
                    ClassVar,
                    Dict,
                    ForwardRef,
                    Generic,
                    get_args,
                    get_origin,
                    Mapping,
                    NamedTuple,
                    overload,
                    Protocol,
                    Sequence,
                    Type,
                    TypeVar,
                    Union)
from weakref import WeakKeyDictionary, WeakValueDictionary

from bidict import bidict
from isort import place_module
from isort.sections import STDLIB
from pydantic import BaseModel, ValidationError
from pydantic.fields import Undefined
from pydantic.generics import GenericModel
from pydantic.typing import display_as_type
from typing_inspect import get_generic_bases, is_generic_type

from omnipy.api.protocols.private.util import HasContents, IsSnapshot
from omnipy.api.typedefs import LocaleType, TypeForm

_KeyT = TypeVar('_KeyT', bound=Hashable)
_ObjT = TypeVar('_ObjT', bound=object)
_HasContentsT = TypeVar('_HasContentsT', bound=HasContents)
_AnyKeyT = TypeVar('_AnyKeyT', bound=object)
_ValT = TypeVar('_ValT', bound=object)
_ContentsT = TypeVar('_ContentsT', bound=object)

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
            return cast(type | GenericAlias, in_type._evaluate(globalns, localns, frozenset()))
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


def all_type_variants(
    in_type: type | GenericAlias | UnionType | _UnionGenericAlias
) -> tuple[type | GenericAlias, ...]:
    if is_union(in_type):
        return get_args(in_type)
    else:
        return (cast(type | GenericAlias, in_type),)


def is_iterable(obj: object) -> bool:
    try:
        iter(obj)  # type: ignore[call-overload]
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


def remove_annotated_plus_optional_if_present(type_or_class: TypeForm) -> TypeForm:
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


# _deepcopy_dispatch: dict[type, Callable]
# d: dict[type, Callable]
#
# # Copied from stdlib (python3.10/copy.py:180), update for new CPython versions
# _deepcopy_dispatch = d = {}
#
#
# def _deepcopy_atomic(x, memo):
#     return x
#
#
# d[type(None)] = _deepcopy_atomic
# d[type(Ellipsis)] = _deepcopy_atomic
# d[type(NotImplemented)] = _deepcopy_atomic
# d[int] = _deepcopy_atomic
# d[float] = _deepcopy_atomic
# d[bool] = _deepcopy_atomic
# d[complex] = _deepcopy_atomic
# d[bytes] = _deepcopy_atomic
# d[str] = _deepcopy_atomic
# d[types.CodeType] = _deepcopy_atomic
# d[type] = _deepcopy_atomic
# d[range] = _deepcopy_atomic
# d[types.BuiltinFunctionType] = _deepcopy_atomic
# d[types.FunctionType] = _deepcopy_atomic
# d[weakref.ref] = _deepcopy_atomic
# d[property] = _deepcopy_atomic


class RefCountMemoDict(UserDict[int, _ObjT], Generic[_ObjT]):
    def __init__(self, dict=None, /, **kwargs) -> None:
        super().__init__(dict, **kwargs)
        self._key_2_obj_id = bidict[int, int]()

    # def __init__(self, dict=None, /, **kwargs) -> None:
    #     self._std_dict: dict[int, _ObjT] = {}
    #     self._weak_value_dict = WeakValueDictionary[int, _ObjT]()
    #     if dict is not None:
    #         self.update(dict)
    #     if kwargs:
    #         self.update(kwargs)
    #
    # def __setattr__(self, key, value):
    #     if key == 'data':
    #         self._std_dict.clear()
    #         self._weak_value_dict.clear()
    #         for k, v in value.items():
    #             self[k] = v
    #     super().__setattr__(key, value)
    #
    # def __getattr__(self, item):
    #     if item == 'data':
    #         return self._std_dict | dict(self._weak_value_dict.items())
    #     return super().__getattr__(item)

    def __setitem__(self, key, obj):
        try:
            print(f'{key},{id(obj)}: {obj} [{type(obj)}]')
        except AttributeError:
            print(f'{key},{id(obj)}: [{type(obj)}]')
        # if isinstance(obj, list):
        #     print([id(x) for x in obj])
        #     obj = [self.data[id(x)] if id(x) in self.data else x for x in obj]
        if isinstance(obj, dict):
            print({k: id(v) for k, v in obj.items()})
        #     obj = {k: self.data[id(v)] if id(v) in self.data else v for k, v in obj.items()}
        # try:
        #     obj = weakref.ref(obj)
        # except TypeError:
        #     pass
        # print(f'{key}: {obj}')
        if key != id(self):
            self.data[key] = obj
            self._key_2_obj_id[key] = id(obj)
        # print(f'{orig_id_obj}: {obj}')
        # self.data[orig_id_obj] = obj
        # try:
        #     weakref.ref(obj)
        #     self._weak_value_dict[key] = obj
        # except TypeError:
        #     self._std_dict[key] = obj

    def clear(self):
        super().clear()
        self._key_2_obj_id.clear()

    # def __getitem__(self, item):
    #     print(f'Getting {item}')
    #     ret = super().__getitem__(item)
    #     # if isinstance(ret, weakref.ref):
    #     #     return ret()
    #     # elif isinstance(ret, list):
    #     #     return [x() if isinstance(x, weakref.ref) else x for x in ret]
    #     # elif isinstance(ret, dict):
    #     #     return {k: v() if isinstance(v, weakref.ref) else v for k, v in ret.items()}
    #     return ret

    # def __delitem__(self, key):
    #     if key in self._weak_value_dict:
    #         del self._weak_value_dict[key]
    #     else:
    #         del self._std_dict[key]

    # def __copy__(self):
    #     inst = self.__class__.__new__(self.__class__)
    #     inst.__dict__.update(self.__dict__)
    #     # Create a copy and avoid triggering descriptors
    #     inst.__dict__["data"] = self.__dict__["data"].copy()
    #     return inst

    # def get(self, key, default=None):
    #     try:
    #         return self.__getitem__(key)
    #     except KeyError:
    #         return default

    def recursively_remove_deleted_objs(
        self,
        *keys: int,
        known_references_callback: Callable[[int], int] | None = None,
    ):
        print(f'Recursively removing deleted objects for {keys}...')

        try:
            known_refcount_for_all_contained_objs_in_memo = defaultdict[int, int](lambda: 0)
            self.get_known_refcount_for_all_contained_objs_in_memo(
                *keys,
                known_refcount_for_all_contained_objs_in_memo=
                known_refcount_for_all_contained_objs_in_memo,
                known_refcount_callback=known_references_callback)
            print(known_refcount_for_all_contained_objs_in_memo)
            self._remove_deleted_objs(list(known_refcount_for_all_contained_objs_in_memo.keys()))
        except Exception as e:
            print(f'Error in recursively_remove_deleted_objs: {repr(e)}')
            traceback.print_exc()
            raise

    def _remove_deleted_objs(self, keys_to_delete: list[int]):
        print(f'_remove_deleted_objs({keys_to_delete})')
        self_keys = tuple(self.keys())

        while True:
            any_keys_deleted = False
            retry_keys = []
            while len(keys_to_delete) > 0:
                print(f'len(keys_to_delete): {len(keys_to_delete)}')
                print(f'keys_to_delete: {keys_to_delete}')
                gc.collect()  # Try to uncomment if memo dict is not cleared
                key = keys_to_delete.pop(0)
                obj = self.data[key]
                print(f'obj: {obj}')
                # gc.collect()  # Try to uncomment if memo dict is not cleared
                ref_count = sys.getrefcount(obj)
                print(f'{obj} has {ref_count} references')
                for k, v in self.data.items():
                    print(f'{k}: {v}')
                k = 0
                v = 0
                # ref_count_target = 4 if isinstance(obj, tuple) else 3
                ref_count_target = 3
                # ref_count_target += known_ref_count
                print(f'ref_count_target: {ref_count_target}')
                for ref in gc.get_referrers(obj):
                    try:
                        print(f'{type(ref)}: {ref}')
                        print(*gc.get_referrers(ref))

                        # print(
                        #     f"ref['obj_copy'][1].__dict__: {ref['obj_copy'][1].__dict__}, id={id(ref['obj_copy'][1].__dict__)}"
                        # )
                        # print(
                        #     f"ref['obj_copy'][1].data: {ref['obj_copy'][1].data}, id={id(ref['obj_copy'][1].data)}"
                        # )
                    except:
                        pass
                # 3 references: the one in the memo dict, one in the gc, and obj
                # +1 reference for tuples, as they are immutable
                if ref_count <= ref_count_target:
                    key_idx = self_keys.index(key)
                    keys_to_delete = self._remove_obj(key, key_idx, self_keys, keys_to_delete)
                    any_keys_deleted = True
                else:
                    retry_keys.append(key)

            if any_keys_deleted:
                keys_to_delete = retry_keys
            else:
                break

    def _remove_obj(self,
                    key: int,
                    key_idx: int,
                    self_keys: tuple[int, ...],
                    keys_to_delete: list[int],
                    equal_obj: object = None) -> list[int]:
        print(f'key: {key}')
        print(f'key_idx: {key_idx}')
        print(f'self_keys: {self_keys}')
        print(f'keys_to_delete: {keys_to_delete}')
        print(f'equal_obj: {equal_obj}')
        print(f'memo_dict: {self}')

        obj = self[key]
        print(f'Removing {obj}')
        print(f'id(obj): {id(obj)}')

        obj_dict = getattr(obj, '__dict__', Undefined)
        if obj_dict is not Undefined and key_idx + 1 < len(self_keys):
            cur_key = self_keys[key_idx + 1]
            if cur_key in self:
                next_memo_obj = self[cur_key]
                print(f'obj.__class__: {obj.__class__}')
                print(f"id(obj_dict): {id(obj_dict)}")
                print(f"cur_key: {cur_key}")
                print(f"next_memo_obj: {next_memo_obj}")
                print(f'self._key_2_obj_id: {self._key_2_obj_id}')

                if isinstance(obj, BaseModel) and isinstance(
                        next_memo_obj, dict) and '__fields_set__' in next_memo_obj:

                    for i, (k, v) in enumerate(reversed(next_memo_obj.items())):
                        print(f'{k}: {v} (key={self._key_2_obj_id.inverse[id(v)]})')
                        keys_to_delete.insert(0, self._key_2_obj_id.inverse[id(v)])

                    keys_to_delete.insert(0, cur_key)

                elif next_memo_obj == obj_dict:
                    keys_to_delete.insert(0, cur_key)

        elif obj.__class__ is set and key_idx > 0:
            cur_key = self_keys[key_idx - 1]
            if cur_key in self:
                prev_memo_obj = self[cur_key]
                if isinstance(prev_memo_obj, list) and set(prev_memo_obj) == obj:
                    keys_to_delete.insert(0, cur_key)

        print(f'Now deleting {obj}')
        del self[key]
        del self._key_2_obj_id[key]
        print(f'memo_dict: {self}')

        return keys_to_delete

    # def _get_objects_in_memo_dict(self, *keys: int) -> dict[int, _ObjT]:
    #
    #     elements_in_memo = {key: self.data[key] for key in keys if key in self.data}
    #     return {
    #         key: cast(_ObjT, obj()) if isinstance(obj, weakref.ref) else obj for key,
    #         obj in elements_in_memo.items()
    #     }

    def get_known_refcount_for_all_contained_objs_in_memo(
        self,
        *keys_of_objs_to_check: int,
        known_refcount_for_all_contained_objs_in_memo: defaultdict[int, int],
        known_refcount_callback: Callable[[int], int] | None = None,
    ) -> None:
        print(f'keys_of_objs_to_check: {keys_of_objs_to_check}')
        dict_of_objs_to_check_in_memo = {
            key: self.data[key] for key in keys_of_objs_to_check if key in self.data
        }
        print(f'dict_of_objs_to_check_in_memo: {dict_of_objs_to_check_in_memo}')
        keys_of_contained_objs_also_in_memo: tuple[int, ...] = ()
        for key_to_check, obj_to_check in dict_of_objs_to_check_in_memo.items():
            if hasattr(obj_to_check, '__dict__'):
                print(f'{obj_to_check} is an object')
                obj_to_check = getattr(obj_to_check, '__dict__')
            contained_objs = {id(obj): obj for obj in gc.get_referents(obj_to_check)}
            print(f'contained_objs: {contained_objs}')
            ids_of_contained_objs = tuple(
                id(contained_obj) for contained_obj in gc.get_referents(obj_to_check))
            print(f'ids_of_contained_objs: {ids_of_contained_objs}')
            keys_of_contained_objs_also_in_memo += tuple(
                self._key_2_obj_id.inverse[contained_obj_id]
                for contained_obj_id in ids_of_contained_objs
                if contained_obj_id in self._key_2_obj_id.inverse)
            known_refcount = 0
            if known_refcount_callback:
                known_refcount = known_refcount_callback(id(obj_to_check))
            for key in (key_to_check,) + keys_of_contained_objs_also_in_memo:
                known_refcount_for_all_contained_objs_in_memo[key] += known_refcount
        print('known_refcount_for_all_contained_objs_in_memo:',
              known_refcount_for_all_contained_objs_in_memo)

        if len(keys_of_contained_objs_also_in_memo) > 0:
            return self.get_known_refcount_for_all_contained_objs_in_memo(
                *keys_of_contained_objs_also_in_memo,
                known_refcount_for_all_contained_objs_in_memo=
                known_refcount_for_all_contained_objs_in_memo,
                known_refcount_callback=known_refcount_callback)

    def start_deepcopy(self, obj):
        pass

    def end_deepcopy(self, obj):
        pass


class KeyRef(list):
    def __init__(self, obj: object) -> None:
        super().__init__([id(obj)])

    def __hash__(self) -> int:  # type: ignore[override]
        return self[0]


class WeakKeyRefContainer(Generic[_AnyKeyT, _ValT]):
    def __init__(self) -> None:
        self._key_dict: WeakValueDictionary[KeyRef, _AnyKeyT] = WeakValueDictionary()
        self._value_dict: WeakKeyDictionary[KeyRef, _ValT] = WeakKeyDictionary()

    def __contains__(self, key: _AnyKeyT) -> bool:
        return KeyRef(key) in self._value_dict

    def get(self, key: _AnyKeyT) -> _ValT | None:
        key_ref = KeyRef(key)
        if key_ref in self._value_dict:
            return self._value_dict[key_ref]
        else:
            return None

    def __getitem__(self, key: _AnyKeyT) -> _ValT:
        key_ref = KeyRef(key)
        if key_ref in self._value_dict:
            return self._value_dict[key_ref]
        else:
            raise KeyError(f'{key} is not in {self.__class__.__name__}')

    def __setitem__(self, key: _AnyKeyT, value: _ValT) -> None:
        key_ref = KeyRef(key)
        self._key_dict[key_ref] = key
        self._value_dict[key_ref] = value

    def __len__(self) -> int:
        return len(self._value_dict)

    def clear(self) -> None:
        self._key_dict.clear()
        self._value_dict.clear()


@dataclass
class Snapshot(Generic[_ObjT, _ContentsT]):
    id: int
    obj_copy: _ContentsT

    def taken_of_same_obj(self, obj: _ObjT) -> bool:
        return self.id == id(obj)

    def differs_from(self, obj: _ObjT) -> bool:
        return not all_equals(self.obj_copy, obj)


obj_getattr = object.__getattribute__
obj_setattr = object.__setattr__


class SnapshotHolder(WeakKeyRefContainer[_HasContentsT, IsSnapshot[_HasContentsT, _ContentsT]],
                     Generic[_HasContentsT, _ContentsT]):
    def __init__(self) -> None:
        super().__init__()
        self._deepcopy_memo = RefCountMemoDict[_ContentsT]()
        # self._key_2_obj_copy_id = dict[int, int]()
        # self._obj_copy_id_keys = defaultdict[int, list[int]](list[int])
        self.keys_for_deleted_objs: list[int] = []

    def __setitem__(self, obj: _HasContentsT, value: IsSnapshot[_HasContentsT, _ContentsT]) -> None:
        raise TypeError(f"'{self.__class__.__name__}' object does not support item assignment")

    def __getattribute__(self, name: str) -> Any:
        _delete_scheduled = obj_getattr(self, '_delete_scheduled')
        _delete_scheduled()
        return obj_getattr(self, name)

    def _delete_scheduled(self) -> None:
        print(f"Deleting scheduled {len(obj_getattr(self, 'keys_for_deleted_objs'))} objects...")
        keys_for_deleted_objs = obj_getattr(self, 'keys_for_deleted_objs')
        if len(keys_for_deleted_objs) > 0:
            obj_setattr(self, 'keys_for_deleted_objs', [])
            deepcopy_memo = obj_getattr(self, '_deepcopy_memo')
            deepcopy_memo.recursively_remove_deleted_objs(*keys_for_deleted_objs)

    def clear(self):
        self.keys_for_deleted_objs = []
        self._deepcopy_memo.clear()
        super().clear()

    def take_snapshot(self, obj: _HasContentsT) -> None:
        gc.collect()
        self._delete_scheduled()
        # from time import sleep
        # sleep(1)
        gc.disable()
        try:
            # self.clear()
            obj_copy: _ContentsT = deepcopy(obj.contents,
                                            self._deepcopy_memo)  # type: ignore[arg-type]
        except (TypeError, ValueError, ValidationError) as exp:
            print(exp)
            obj_copy = copy(obj.contents)
        gc.enable()

        key = id(obj)
        obj_copy_id = id(obj_copy)

        super().__setitem__(obj, Snapshot(key, obj_copy))

        # if key in self._key_2_obj_copy_id:
        #     prev_obj_copy_id = self._key_2_obj_copy_id[key]
        #     self._obj_copy_id_keys[prev_obj_copy_id].remove(key)
        # self._key_2_obj_copy_id[key] = obj_copy_id
        # self._obj_copy_id_keys[obj_copy_id].append(key)

    # def recursively_remove_deleted_obj_from_deepcopy_memo(self, key: int) -> None:
    #     def _known_snapshot_references(obj_copy_id: int) -> int:
    #         # if obj_copy_id in self._obj_copy_id_keys:
    #         #     return len(self._obj_copy_id_keys[obj_copy_id])
    #         return 0
    #
    #     self._deepcopy_memo.recursively_remove_deleted_objs(
    #         key,
    #         known_references_callback=_known_snapshot_references,
    #     )


_memo: dict[int, object] = {}


class RestorableContents:
    def __init__(self) -> None:
        self._last_snapshot: Snapshot | None = None

    def has_snapshot(self) -> bool:
        return self._last_snapshot is not None

    def take_snapshot(self, obj: object):
        try:
            snapshot_obj = deepcopy(obj, _memo)
        except (TypeError, ValueError, ValidationError) as exp:
            snapshot_obj = copy(obj)
        self._last_snapshot = Snapshot(id(obj), snapshot_obj)

    def _get_not_empty_snapshot(self) -> Snapshot:
        assert self.has_snapshot(), 'No snapshot has been taken yet'
        return cast(Snapshot, self._last_snapshot)

    def get_last_snapshot(self) -> object:
        return self._get_not_empty_snapshot().obj_copy

    def last_snapshot_taken_of_same_obj(self, obj: object) -> bool:
        return self._get_not_empty_snapshot().id == id(obj)

    def differs_from_last_snapshot(self, obj: object) -> bool:
        return not all_equals(self._get_not_empty_snapshot().obj_copy, obj)


def _is_internal_module(module: ModuleType, imported_modules: list[ModuleType]):
    return module not in imported_modules and module.__name__.startswith('omnipy')


def recursive_module_import(module: ModuleType, imported_modules: list[ModuleType] = []):
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
