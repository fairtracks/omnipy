from collections import defaultdict, UserDict
import gc
import sys
import traceback
from typing import Generic

from typing_extensions import TypeVar

from omnipy.util.setdeque import SetDeque

_ObjT = TypeVar('_ObjT', bound=object)


class RefCountMemoDict(UserDict[int, _ObjT], Generic[_ObjT]):
    def __init__(self) -> None:
        super().__init__()
        self._cur_deepcopy_obj_id: int | None = None
        self._cur_keep_alive_list: list[_ObjT | None] = []
        self._keep_alive_dict: dict[int, _ObjT | None] = {}
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
                    ref = None
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
                    if ref is not None:
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

    def __getitem__(self, key: int) -> _ObjT | list[_ObjT | None]:  # type: ignore[override]
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
