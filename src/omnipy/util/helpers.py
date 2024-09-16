from collections import defaultdict, UserDict
from collections.abc import Hashable, Iterable
from copy import copy, deepcopy
from dataclasses import dataclass
from importlib.abc import Loader
from importlib.machinery import FileFinder, ModuleSpec
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
                    Any,
                    cast,
                    ClassVar,
                    ForwardRef,
                    Generic,
                    get_args,
                    get_origin,
                    Mapping,
                    overload,
                    Protocol,
                    TypeGuard,
                    TypeVar,
                    Union)
from weakref import WeakKeyDictionary, WeakValueDictionary

from pydantic import BaseModel, ValidationError
from pydantic.generics import GenericModel
from pydantic.typing import is_none_type
from typing_inspect import get_generic_bases, is_generic_type

from omnipy.api.protocols.private.util import HasContents, IsSnapshotWrapper
from omnipy.api.typedefs import LocaleType, TypeForm
from omnipy.util.contexts import setup_and_teardown_callback_context
from omnipy.util.setdeque import SetDeque

_KeyT = TypeVar('_KeyT', bound=Hashable)
_ObjT = TypeVar('_ObjT', bound=object)
_HasContentsT = TypeVar('_HasContentsT', bound=HasContents)
_AnyKeyT = TypeVar('_AnyKeyT', bound=object)
_ValT = TypeVar('_ValT', bound=object)
_ContentsT = TypeVar('_ContentsT', bound=object)

T = TypeVar('T')

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


def is_iterable(obj: Iterable[T] | T) -> TypeGuard[Iterable[T]]:
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
    return is_union(cls_or_type) and any(is_none_type(arg) for arg in get_args(cls_or_type))


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


def remove_forward_ref_notation(type_str: str):
    return type_str.replace("ForwardRef('", '').replace("')", '')


def format_classname_with_params(cls_name: str, params_str: str) -> str:
    return f'{cls_name}[{params_str}]'


class RefCountMemoDict(UserDict[int, _ObjT], Generic[_ObjT]):
    def __init__(self) -> None:
        super().__init__()
        self._cur_deepcopy_obj_id: int | None = None
        self._cur_keep_alive_list: list[_ObjT] = []
        self._keep_alive_dict: dict[int, _ObjT] = {}
        self._sub_obj_ids: defaultdict[int, SetDeque[int]] = defaultdict(SetDeque)

    def all_are_empty(self, debug: bool = False) -> bool:
        _all_are_empty = (
            len(self) == 0 and len(self._keep_alive_dict) == 0 and len(self._sub_obj_ids) == 0
            and self._cur_deepcopy_obj_id is None and len(self._cur_keep_alive_list) == 0)

        if debug:
            print()
            print(f'RefCountMemoDict.all_are_empty(): {_all_are_empty}')
            print('--------------------------------------------------')
            print(f'len(self): {len(self)}')
            print(f'len(self._keep_alive_dict): {len(self._keep_alive_dict)}')
            print(f'len(self._sub_obj_ids): {len(self._sub_obj_ids)}')
            print(f'self._cur_deepcopy_obj_id: {self._cur_deepcopy_obj_id}')
            print(f'len(self._cur_keep_alive_list): {len(self._cur_keep_alive_list)}')

            if len(self) > 0:
                print('==================================================')
                for key in self:
                    print(f'Content id: {key} '
                          f'[{sys.getrefcount(self[key]) - 1} refs, id={id(self[key])}]: '
                          f'{repr(self[key])}')

                for key in self:
                    print('--------------------------------------------------')
                    print(f'References for {key}: {repr(self[key])}')
                    print('--------------------------------------------------')
                    for i, ref in enumerate(gc.get_referrers(self[key])):
                        try:
                            print(f'[Reference {i}]')
                            print(f'    Type: {type(ref)}')
                            print(f'    ID: {id(ref)}')
                            print(f'    Value: {repr(ref)}')
                            print()

                        except Exception as e:
                            print(f'Error: {repr(e)}')
                            pass
                    del ref

        return _all_are_empty

    def clear(self):
        super().clear()
        self._keep_alive_dict.clear()
        self._sub_obj_ids.clear()

    def get_deepcopy_object_ids(self) -> SetDeque[int]:
        return SetDeque(self._sub_obj_ids.keys())

    def setup_deepcopy(self, obj):
        assert self._cur_deepcopy_obj_id is None, \
            f'self._cur_deepcopy_obj_id is not None, but {self._cur_deepcopy_obj_id}'
        assert len(self._cur_keep_alive_list) == 0, \
            f'len(self._cur_keep_alive_list) == {len(self._cur_keep_alive_list)} instead of 0'

        # Solution to test_ref_count_memo_dict_repeated_deepcopy_same_obj(), but not
        # necessary for the current implementation (see comments on the test). Fix unnecessarily
        # deletes shared fragments between the old and new deepcopies, and is thus disabled.
        # Instead, there is a check to ensure that the current object has not already been
        # deepcopied, which is the assumption behind disabling the fix

        assert id(obj) not in self._sub_obj_ids, \
            (f'Object with id: {id(obj)} already in deepcopy_memo. It has either already been '
             f'deepcopied, or it is reusing the id of a deleted object which has not been deleted '
             'from the deepcopy memo.')

        self._cur_deepcopy_obj_id = id(obj)

    def keep_alive_after_deepcopy(self):
        # old_sub_obj_ids = self._sub_obj_ids[self._cur_deepcopy_obj_id]
        # assert len(old_sub_obj_ids) == len(self._cur_keep_alive_list)
        #
        # self._sub_obj_ids[self._cur_deepcopy_obj_id] = SetDeque()

        while len(self._cur_keep_alive_list) > 0:
            keep_alive_obj = self._cur_keep_alive_list.pop()

            # id_keep_alive_obj = id(keep_alive_obj)
            # assert id_keep_alive_obj in old_sub_obj_ids
            # self._sub_obj_ids[self._cur_deepcopy_obj_id].append(id_keep_alive_obj)

            if not self._is_atomic(keep_alive_obj):
                self._keep_alive_dict[id(keep_alive_obj)] = keep_alive_obj
            else:
                self._keep_alive_dict[id(keep_alive_obj)] = None

    def teardown_deepcopy(self):
        # Also seems to be unnecessary now. This is for recovering from exceptions during deepcopy
        # that would leave the memo dict in an inconsistent state. This should now be handled by
        # SnapshotHolder.take_snapshot().
        #
        # for possibly_added_obj in self._sub_obj_ids[self._cur_deepcopy_obj_id]:
        #     if possibly_added_obj in self and possibly_added_obj not in self._keep_alive_dict:
        #         del self[possibly_added_obj]

        if self._cur_deepcopy_obj_id and \
                (self._cur_deepcopy_obj_id in self._sub_obj_ids
                 and self._cur_deepcopy_obj_id not in self._keep_alive_dict):
            del self._sub_obj_ids[self._cur_deepcopy_obj_id]

        self._cur_deepcopy_obj_id = None
        self._cur_keep_alive_list = []

    @staticmethod
    def _is_atomic(obj: object) -> bool:
        from copy import _deepcopy_atomic, _deepcopy_dispatch  # type: ignore[attr-defined]
        try:
            return type(obj) is tuple or _deepcopy_dispatch[type(obj)] is _deepcopy_atomic
        except KeyError:
            return False

    def __setitem__(self, key, obj):
        # try:
        #     print(f'{key},{id(obj)}: {obj} [{type(obj)}]')
        # except AttributeError:
        #     print(f'{key},{id(obj)}: [{type(obj)}]')
        #
        # if isinstance(obj, dict):
        #     print({k: id(v) for k, v in obj.items()})

        if key != id(self):
            if not self._is_atomic(obj):
                self.data[key] = obj
            self._register_key_as_sub_obj_of_cur_deepcopy_obj(key)

    def __getitem__(self, key: int) -> _ObjT | list[_ObjT]:  # type: ignore[override]
        if key == id(self):
            return self._cur_keep_alive_list
        else:
            ret = super().__getitem__(key)
            # print(f'Getting {key}')
            self._register_key_as_sub_obj_of_cur_deepcopy_obj(key)
            return ret

    def _register_key_as_sub_obj_of_cur_deepcopy_obj(self, key: int) -> None:
        if self._cur_deepcopy_obj_id is not None:
            self._sub_obj_ids[self._cur_deepcopy_obj_id].append(key)

    def recursively_remove_deleted_objs(
        self,
        keys_for_deleted_objs: SetDeque[int],
    ):
        try:
            # print(f'keys_for_deleted_objs: {keys_for_deleted_objs}')
            # print(f'self.get_deepcopy_object_ids(): {self.get_deepcopy_object_ids()}')
            keys_to_delete = self._remove_deleted_objs(keys_for_deleted_objs)
        except Exception as e:
            print(f'Error in recursively_remove_deleted_objs: {repr(e)}')
            traceback.print_exc()
            raise

        # for deleted_key in deleted_keys:
        #     if deleted_key in keys_for_deleted_objs:
        #         keys_for_deleted_objs.remove(deleted_key)
        keys_for_deleted_objs.clear()
        keys_for_deleted_objs.extend(keys_to_delete)

    def _remove_deleted_objs(self, keys_for_deleted_objs: SetDeque[int]) -> SetDeque[int]:
        # keys_to_delete = SetDeque(key for key in keys_for_deleted_objs if key in self)
        keys_to_delete = SetDeque[int](keys_for_deleted_objs)
        # print(f'_remove_deleted_objs({keys_to_delete})')
        # deleted_keys: SetDeque[int] = SetDeque()

        while True:
            any_keys_deleted_this_iteration = False
            retry_keys: SetDeque[int] = SetDeque()
            while len(keys_to_delete) > 0:
                # print(f'len(keys_to_delete): {len(keys_to_delete)}')
                # print(f'keys_to_delete: {keys_to_delete}')
                key = keys_to_delete.popleft()

                if key not in self.data:
                    if key in self._keep_alive_dict:  # happens occasionally with e.g. tuples
                        keys_to_delete = self._add_sub_obj_ids_to_deletion_keys(key, keys_to_delete)
                        self._delete_memo_entry(key)
                    continue

                # obj = self.data[key]
                # print(f'obj: {obj}')
                ref_count = sys.getrefcount(self.data[key])
                # print(f'{key}: {repr(self.data[key])} has {ref_count} references')
                # for k, v in self.data.items():
                #     print(f'{k}: {repr(v)}, id(val)={id(v)}')
                # k = 0
                # v = 0
                ref_count_target = 2
                # print(f'ref_count_target: {ref_count_target}')
                # for i, ref in enumerate(gc.get_referrers(self.data[key])):
                #     try:
                #         print(f'Reference {i}')
                #         print('------------')
                #         print(f'{type(ref)}: {ref}')
                #         print(*gc.get_referrers(ref))
                #     except Exception as e:
                #         print(f'Error: {repr(e)}')
                #         pass
                # del ref
                # loc = locals()
                # print(f'locals(): {loc}')
                # del loc

                if ref_count <= ref_count_target:
                    # print(f'Now deleting {key}: {self.data[key]}')
                    keys_to_delete = self._add_sub_obj_ids_to_deletion_keys(key, keys_to_delete)
                    self._delete_memo_entry(key)
                    any_keys_deleted_this_iteration = True
                    # deleted_keys.append(key)
                else:
                    retry_keys.append(key)

            keys_to_delete = SetDeque(key for key in retry_keys if key in self)
            if not any_keys_deleted_this_iteration:
                break

        return keys_to_delete

    def _add_sub_obj_ids_to_deletion_keys(self, key: int,
                                          keys_to_delete: SetDeque[int]) -> SetDeque[int]:
        if key in self._sub_obj_ids:
            for i, sub_obj_id in enumerate(self._sub_obj_ids[key]):
                if sub_obj_id != key and sub_obj_id not in keys_to_delete:
                    # print(f'Adding {sub_obj_id} to keys_to_delete')
                    keys_to_delete.insert(i, sub_obj_id)

        return keys_to_delete

    def _delete_memo_entry(self, key):
        # print(f'Now deleting {key}: {self[key]}')
        #
        # print(f'memo_dict: {self}')
        # print(f'keep_alive_dict: {self._keep_alive_dict}')
        # print(f'sub_obj_ids: {self._sub_obj_ids}')

        if key in self:
            del self[key]
        if key in self._keep_alive_dict:
            del self._keep_alive_dict[key]
        if key in self._sub_obj_ids:
            del self._sub_obj_ids[key]

        # print(f'Now deleted {key}')
        #
        # print(f'memo_dict: {self}')
        # print(f'keep_alive_dict: {self._keep_alive_dict}')
        # print(f'sub_obj_ids: {self._sub_obj_ids}')


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
class SnapshotWrapper(Generic[_ObjT, _ContentsT]):
    id: int
    snapshot: _ContentsT

    def taken_of_same_obj(self, obj: _ObjT) -> bool:
        return self.id == id(obj)

    def differs_from(self, obj: _ObjT) -> bool:
        return not all_equals(self.snapshot, obj)


obj_getattr = object.__getattribute__
obj_setattr = object.__setattr__


class SnapshotHolder(WeakKeyRefContainer[_HasContentsT,
                                         IsSnapshotWrapper[_HasContentsT, _ContentsT]],
                     Generic[_HasContentsT, _ContentsT]):
    def __init__(self) -> None:
        super().__init__()
        self._deepcopy_memo = RefCountMemoDict[_ContentsT]()
        self._deepcopy_content_ids_for_deleted_objs: SetDeque[int] = SetDeque()

    def __setitem__(self, obj: _HasContentsT, value: IsSnapshotWrapper[_HasContentsT,
                                                                       _ContentsT]) -> None:
        raise TypeError(f"'{self.__class__.__name__}' object does not support item assignment")

    def clear(self) -> None:
        self._deepcopy_content_ids_for_deleted_objs.clear()
        self._deepcopy_memo.clear()
        super().clear()

    def all_are_empty(self, debug: bool = False) -> bool:
        _deepcopy_memo_all_are_empty = self._deepcopy_memo.all_are_empty(debug=debug)

        _all_are_empty = (
            len(self) == 0 and len(self._deepcopy_content_ids_for_deleted_objs) == 0
            and _deepcopy_memo_all_are_empty)

        if debug:
            print()
            print(f'SnapshotHolder.all_are_empty(): {_all_are_empty}')
            print('-------------------------')
            print(f'len(self): {len(self)}')
            print(f'self.get_deepcopy_content_ids(): '
                  f'{self.get_deepcopy_content_ids()}')
            print(f'self.get_deepcopy_content_ids_scheduled_for_deletion(): '
                  f'{self.get_deepcopy_content_ids_scheduled_for_deletion()}')
            print(f'self._deepcopy_memo.all_are_empty(): {_deepcopy_memo_all_are_empty}')

            if len(self) > 0:
                print('=========================')
                for key, val in self._value_dict.items():
                    print(f'{key}: {repr(val)}')

        return _all_are_empty

    def get_deepcopy_content_ids(self) -> SetDeque[int]:
        return self._deepcopy_memo.get_deepcopy_object_ids()

    def get_deepcopy_content_ids_scheduled_for_deletion(self) -> SetDeque[int]:
        return self._deepcopy_content_ids_for_deleted_objs

    def schedule_deepcopy_content_ids_for_deletion(self, *keys: int) -> None:
        for key in keys:
            if key in self._deepcopy_memo.get_deepcopy_object_ids():
                self._deepcopy_content_ids_for_deleted_objs.append(key)

    def delete_scheduled_deepcopy_content_ids(self) -> None:
        keys_for_deleted_objs = self._deepcopy_content_ids_for_deleted_objs
        if len(keys_for_deleted_objs) > 0:
            # self._deepcopy_content_ids_for_deleted_objs = SetDeque()
            deepcopy_memo = obj_getattr(self, '_deepcopy_memo')
            deepcopy_memo.recursively_remove_deleted_objs(keys_for_deleted_objs)

    def take_snapshot_setup(self) -> None:
        gc.disable()

    def take_snapshot_teardown(self) -> None:
        self.delete_scheduled_deepcopy_content_ids()
        gc.enable()

    def take_snapshot(self, obj: _HasContentsT) -> None:
        try:
            # Delete scheduled content in the deepcopy memo if the new object is reusing an old id.
            # This deletion might not succeed, e.g. if the current snapshot holds a reference to the
            # old object. In those case, setup_deepcopy() will raise an AssertionError, which should
            # trigger a new attempt to deepcopy without the memo dict.

            if id(obj.contents) in self.get_deepcopy_content_ids():
                self.delete_scheduled_deepcopy_content_ids()

            obj_copy: _ContentsT

            with setup_and_teardown_callback_context(
                    setup_func=self._deepcopy_memo.setup_deepcopy,
                    setup_func_args=(obj.contents,),
                    exception_func=self._deepcopy_memo.teardown_deepcopy,
                    teardown_func=self._deepcopy_memo.teardown_deepcopy,
            ):

                obj_copy = deepcopy(obj.contents, self._deepcopy_memo)  # type: ignore[arg-type]
                self._deepcopy_memo.keep_alive_after_deepcopy()
        except (TypeError, ValueError, ValidationError, AssertionError) as exp:
            print(f'Error in deepcopy with memo dict: {exp}. '
                  f'Attempting deepcopy without memo dict.')
            try:
                # print(f'object contents after retry: {obj.contents}')
                obj_copy = deepcopy(obj.contents)
            except (TypeError, ValueError, ValidationError, AssertionError) as exp:
                print(f'Error in deepcopy without memo dict: {exp}. '
                      f'Attempting simple copy.')
                obj_copy = copy(obj.contents)

        # Eventual old snapshot object is being kept alive until this point, but is scheduled for
        # deletion after the next line. In many cases (but not all), this happens before
        # take_snapshot_teardown() is called, which triggers deletion of any unreferenced
        # fragments still kept alive in the memo dict.

        super().__setitem__(obj, SnapshotWrapper(id(obj), obj_copy))


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
