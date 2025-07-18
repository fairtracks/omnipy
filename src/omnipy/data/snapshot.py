from copy import copy, deepcopy
from dataclasses import dataclass
import gc
from typing import Generic

from pydantic import ValidationError

from omnipy.shared.protocols.data import ContentT, HasContentT, IsSnapshotWrapper, ObjContraT
from omnipy.util.contexts import setup_and_teardown_callback_context
from omnipy.util.helpers import all_equals
from omnipy.util.memo import RefCountMemoDict
from omnipy.util.setdeque import SetDeque
from omnipy.util.weak import WeakKeyRefContainer


@dataclass
class SnapshotWrapper(Generic[ObjContraT, ContentT]):
    id: int
    snapshot: ContentT

    def taken_of_same_obj(self, obj: ObjContraT) -> bool:
        return self.id == id(obj)

    def differs_from(self, obj: ObjContraT) -> bool:
        return not all_equals(self.snapshot, obj)


obj_getattr = object.__getattribute__
obj_setattr = object.__setattr__


class SnapshotHolder(WeakKeyRefContainer[HasContentT, IsSnapshotWrapper[HasContentT, ContentT]],
                     Generic[HasContentT, ContentT]):
    def __init__(self) -> None:
        super().__init__()
        self._deepcopy_memo = RefCountMemoDict[ContentT]()
        self._deepcopy_content_ids_for_deleted_objs: SetDeque[int] = SetDeque()

    def __setitem__(self, key: HasContentT, value: IsSnapshotWrapper[HasContentT,
                                                                     ContentT]) -> None:
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

    def take_snapshot(self, obj: HasContentT) -> None:
        try:
            # Delete scheduled content in the deepcopy memo if the new object is reusing an old id.
            # This deletion might not succeed, e.g. if the current snapshot holds a reference to the
            # old object. In those case, setup_deepcopy() will raise an AssertionError, which should
            # trigger a new attempt to deepcopy without the memo dict.

            if id(obj.content) in self.get_deepcopy_content_ids():
                self.delete_scheduled_deepcopy_content_ids()

            obj_copy: ContentT

            with setup_and_teardown_callback_context(
                    setup_func=self._deepcopy_memo.setup_deepcopy,
                    setup_func_args=(obj.content,),
                    exception_func=self._deepcopy_memo.teardown_deepcopy,
                    teardown_func=self._deepcopy_memo.teardown_deepcopy,
            ):

                obj_copy = deepcopy(obj.content, self._deepcopy_memo)  # type: ignore[arg-type]
                self._deepcopy_memo.keep_alive_after_deepcopy()
        except (TypeError, ValueError, ValidationError, AssertionError) as exp:
            print(f'Error in deepcopy with memo dict: {exp}. '
                  f'Attempting deepcopy without memo dict.')
            try:
                # print(f'object content after retry: {obj.content}')
                obj_copy = deepcopy(obj.content)
            except (TypeError, ValueError, ValidationError, AssertionError) as exp:
                print(f'Error in deepcopy without memo dict: {exp}. '
                      f'Attempting simple copy.')
                obj_copy = copy(obj.content)

        # Eventual old snapshot object is being kept alive until this point, but is scheduled for
        # deletion after the next line. In many cases (but not all), this happens before
        # take_snapshot_teardown() is called, which triggers deletion of any unreferenced
        # fragments still kept alive in the memo dict.

        super().__setitem__(obj, SnapshotWrapper(id(obj), obj_copy))
