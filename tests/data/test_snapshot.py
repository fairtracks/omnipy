from collections import UserDict, UserList
from copy import copy
import gc
from typing import Generic

import pytest

from omnipy.data.snapshot import SnapshotHolder, SnapshotWrapper
from omnipy.shared.protocols.data import ContentT, HasContent, IsSnapshotHolder
import omnipy.util.pydantic as pyd
from omnipy.util.setdeque import SetDeque


class HasContentMixin(Generic[ContentT]):
    @property
    def content(self) -> ContentT:
        return self.data

    @content.setter
    def content(self, value: ContentT) -> None:
        self.data = value

    #
    # def __deepcopy__(self, memo=None):
    #     print(f'__deepcopy__() called for {id(self)}: {self}')
    #     ret = self.__class__(deepcopy(self.data, memo))
    #     # memo[id(self)] = ret
    #     print(f'  memo: {memo}, {type(memo)}')
    #     return ret

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.content})'


class MyList(HasContentMixin[list], UserList):
    ...


class MyDict(HasContentMixin[dict], UserDict):
    ...


def _take_snapshot(snapshot_holder: IsSnapshotHolder, obj: HasContent) -> None:
    snapshot_holder.take_snapshot_setup()
    snapshot_holder.take_snapshot(obj)
    snapshot_holder.take_snapshot_teardown()


def test_snapshot_holder_all_are_empty_and_clear() -> None:
    snapshot_holder = SnapshotHolder[MyList, list]()
    assert snapshot_holder.all_are_empty()

    my_list = MyList([123, 234])

    snapshot_holder.take_snapshot(my_list)
    assert not snapshot_holder.all_are_empty()
    assert len(snapshot_holder) == 1

    snapshot_holder.clear()
    assert snapshot_holder.all_are_empty()

    my_other_list = MyList([234, 345])

    snapshot_holder.take_snapshot(my_other_list)
    assert not snapshot_holder.all_are_empty()
    assert len(snapshot_holder) == 1

    id_my_other_list_content = id(my_other_list.content)

    del my_other_list

    assert not snapshot_holder.all_are_empty()
    assert len(snapshot_holder) == 0

    snapshot_holder.schedule_deepcopy_content_ids_for_deletion(id_my_other_list_content)
    snapshot_holder.delete_scheduled_deepcopy_content_ids()

    assert snapshot_holder.all_are_empty()

    something_else = [2, 3, 4]
    snapshot_holder.take_snapshot(my_list)
    snapshot_holder.schedule_deepcopy_content_ids_for_deletion(
        *[id(my_list.content), id(something_else)])

    del my_list
    snapshot_holder.delete_scheduled_deepcopy_content_ids()

    assert snapshot_holder.all_are_empty()


# TODO: Refactor into smaller tests
def test_snapshots() -> None:
    snapshot_holder = SnapshotHolder[MyList | MyDict, list | dict]()

    my_list = MyList([1, 3, 5])
    assert my_list.content == [1, 3, 5]

    assert my_list not in snapshot_holder
    assert snapshot_holder.get(my_list) is None

    with pytest.raises(KeyError):
        snapshot_holder[my_list]

    with pytest.raises(TypeError):
        snapshot_holder[my_list] = my_list  # type: ignore[assignment]

    assert len(snapshot_holder) == 0

    _take_snapshot(snapshot_holder, my_list)

    assert my_list in snapshot_holder
    assert snapshot_holder.get(my_list) is snapshot_holder[my_list]
    assert isinstance(snapshot_holder[my_list], SnapshotWrapper)

    snapshot = snapshot_holder[my_list]
    assert snapshot.id == id(my_list)
    assert snapshot.taken_of_same_obj(my_list) is True

    assert snapshot.snapshot == my_list.content
    assert snapshot.differs_from(my_list) is False

    assert id(snapshot.snapshot) != id(my_list)

    assert snapshot.taken_of_same_obj(copy(my_list)) is False
    assert snapshot.differs_from(copy(my_list)) is False

    my_other_list = MyList([my_list])
    my_list.append(7)
    assert snapshot.taken_of_same_obj(my_list) is True
    assert snapshot.differs_from(my_list) is True
    assert my_list == MyList([1, 3, 5, 7])
    assert my_other_list == MyList([[1, 3, 5, 7]])

    my_list_from_snapshot = snapshot.snapshot
    assert my_list_from_snapshot == [1, 3, 5]

    # the snapshot is a (preferably deep) copy of the old object
    assert my_list_from_snapshot is not my_list.content

    my_dict = MyDict({1: 2, 3: 4})

    my_dict[5] = my_list_from_snapshot
    assert my_dict == MyDict({1: 2, 3: 4, 5: [1, 3, 5]})

    assert my_dict not in snapshot_holder
    _take_snapshot(snapshot_holder, my_dict)
    assert snapshot_holder[my_dict].taken_of_same_obj(my_dict) is True
    assert snapshot_holder[my_dict].differs_from(my_dict) is False

    del my_dict[5]
    assert my_dict == MyDict({1: 2, 3: 4})
    assert snapshot_holder[my_dict].taken_of_same_obj(my_dict) is True
    assert snapshot_holder[my_dict].differs_from(my_dict) is True

    assert len(snapshot_holder) == 2

    del my_dict
    assert len(snapshot_holder) == 1

    del my_list
    assert len(snapshot_holder) == 1

    my_list = my_other_list[0]
    assert my_list in snapshot_holder

    del my_list
    del my_other_list
    assert len(snapshot_holder) == 0


def test_snapshot_deepcopy_reuse_objects() -> None:
    snapshot_holder = SnapshotHolder['MyMemoDeletingList', list | dict]()

    # def finalize(content_id: int) -> None:
    #     print(f'finalize() called for {content_id}')
    #     if snapshot_holder is not None:
    #         # self_id = id(self)
    #         # obj.content = []
    #         try:
    #             # snapshot_holder.recursively_remove_deleted_obj_from_deepcopy_memo(content_id)
    #             snapshot_holder.schedule_deepcopy_content_ids_for_deletion(content_id)
    #         except (AttributeError) as exp:
    #             print(exp)
    #             print(snapshot_holder._deepcopy_memo)

    class MyMemoDeletingList(MyList):
        def __init__(self, content: list) -> None:
            super().__init__(content)
            # weakref.finalize(self, finalize, content_id=id(self.content))

        def __del__(self):
            content_id = id(self.content)
            # print(f'__del__ called for {content_id}')
            self.content = []
            if snapshot_holder is not None:
                snapshot_holder.schedule_deepcopy_content_ids_for_deletion(content_id)

    class MyPydanticModel(pyd.BaseModel):
        my_list: MyMemoDeletingList

        class Config:
            arbitrary_types_allowed = True

    def _inner_test_snapshot_deepcopy_reuse_objects(
            snapshot_holder: SnapshotHolder[MyMemoDeletingList, list | dict]) -> None:

        inner = MyMemoDeletingList([2, 4])
        middle = MyMemoDeletingList([{1, 3}, inner])
        outer = MyMemoDeletingList([0, MyPydanticModel(my_list=middle), 5])

        _take_snapshot(snapshot_holder, outer)
        _take_snapshot(snapshot_holder, middle)
        _take_snapshot(snapshot_holder, inner)

        assert type(outer[1].my_list[-1]) is type(middle[-1]) is type(inner) is MyMemoDeletingList
        assert id(outer[1].my_list[-1]) == id(middle[-1]) == id(inner)

        assert type(snapshot_holder[outer].snapshot[1].my_list[-1]) \
               is type(snapshot_holder[middle].snapshot[-1]) \
               is MyMemoDeletingList
        assert id(snapshot_holder[outer].snapshot[1].my_list[-1]) \
               == id(snapshot_holder[middle].snapshot[-1])

        assert type(outer[1].my_list[-1].content) is type(middle[-1].content) is type(
            inner.content) is list
        assert id(outer[1].my_list[-1].content) == id(middle[-1].content) == id(inner.content)

        assert type(snapshot_holder[outer].snapshot[1].my_list[-1].content) \
               is type(snapshot_holder[middle].snapshot[-1].content) \
               is type(snapshot_holder[inner].snapshot) \
               is list
        assert id(snapshot_holder[outer].snapshot[1].my_list[-1].content) \
               == id(snapshot_holder[middle].snapshot[-1].content) \
               == id(snapshot_holder[inner].snapshot)

        assert type(outer[1].my_list.content) is type(middle.content) is list
        assert id(outer[1].my_list.content) == id(middle.content)

        assert type(snapshot_holder[outer].snapshot[1].my_list.content) \
               is type(snapshot_holder[middle].snapshot) \
               is list
        assert id(snapshot_holder[outer].snapshot[1].my_list.content) \
               == id(snapshot_holder[middle].snapshot)

    # snapshot_holder = SnapshotHolder[MyMemoDeletingList, list]()
    _inner_test_snapshot_deepcopy_reuse_objects(snapshot_holder)
    snapshot_holder.delete_scheduled_deepcopy_content_ids()
    assert len(snapshot_holder.get_deepcopy_content_ids()) == 0


def test_snapshot_deepcopy_exception_cleanup() -> None:
    class Dynamite:
        def __deepcopy__(self, memo={}):
            memo[id(memo)].append(self)
            memo[id(self)] = copy(self)
            raise RuntimeError('Boom!')

    class DynamiteCrate(HasContentMixin[Dynamite]):
        def __init__(self, data: Dynamite) -> None:
            self.data = data

    snapshot_holder = SnapshotHolder[DynamiteCrate | MyList, Dynamite | list]()

    my_list = MyList([1, 3, 5])
    assert snapshot_holder.all_are_empty()

    _take_snapshot(snapshot_holder, my_list)

    assert len(snapshot_holder) == 1
    assert snapshot_holder.get_deepcopy_content_ids() == SetDeque((id(my_list.content),))
    # assert len(snapshot_holder._deepcopy_memo._keep_alive_dict) == 1

    try:
        dynamite_crate = DynamiteCrate(Dynamite())
        _take_snapshot(snapshot_holder, dynamite_crate)
    except RuntimeError:
        pass

    assert len(snapshot_holder) == 1
    assert snapshot_holder.get_deepcopy_content_ids() == SetDeque((id(my_list.content),))
    # assert len(snapshot_holder._deepcopy_memo._keep_alive_dict) == 1


def test_snapshot_holder_deepcopy_memo_status_delete_and_clear() -> None:
    snapshot_holder = SnapshotHolder[MyList, list | dict]()

    my_first_list = MyList([1, 3, 5])
    my_second_list = MyList([2, 4, 6])
    my_third_list = MyList([my_second_list, my_second_list])

    content_id_first_list = id(my_first_list.content)
    content_id_second_list = id(my_second_list.content)
    content_id_third_list = id(my_third_list.content)

    _take_snapshot(snapshot_holder, my_first_list)
    _take_snapshot(snapshot_holder, my_third_list)

    assert len(snapshot_holder) == 2
    assert snapshot_holder.get_deepcopy_content_ids() == SetDeque((
        content_id_first_list,
        content_id_third_list,
    ))
    assert snapshot_holder.get_deepcopy_content_ids_scheduled_for_deletion() == SetDeque()

    snapshot_holder.schedule_deepcopy_content_ids_for_deletion(content_id_first_list)

    assert len(snapshot_holder) == 2
    assert snapshot_holder.get_deepcopy_content_ids() == SetDeque((
        content_id_first_list,
        content_id_third_list,
    ))
    assert snapshot_holder.get_deepcopy_content_ids_scheduled_for_deletion() == SetDeque(
        (content_id_first_list,))

    # Duplicates are ignored
    snapshot_holder.schedule_deepcopy_content_ids_for_deletion(content_id_first_list)

    assert len(snapshot_holder) == 2
    assert snapshot_holder.get_deepcopy_content_ids() == SetDeque((
        content_id_first_list,
        content_id_third_list,
    ))
    assert snapshot_holder.get_deepcopy_content_ids_scheduled_for_deletion() == SetDeque(
        (content_id_first_list,))

    # Not deleted if there are still references to the content object. Object is still
    # scheduled for deletion, just in case
    snapshot_holder.delete_scheduled_deepcopy_content_ids()

    assert len(snapshot_holder) == 2
    assert snapshot_holder.get_deepcopy_content_ids() == SetDeque((
        content_id_first_list,
        content_id_third_list,
    ))
    assert snapshot_holder.get_deepcopy_content_ids_scheduled_for_deletion() == SetDeque(
        (content_id_first_list,))

    # Automatic deletion of snapshots from snapshot_holder, but no automatic deletion of
    # objects from deepcopy_memo, even if already scheduled for deletion
    del my_first_list

    gc.collect()

    assert len(snapshot_holder) == 1
    assert snapshot_holder.get_deepcopy_content_ids() == SetDeque((
        content_id_first_list,
        content_id_third_list,
    ))
    assert snapshot_holder.get_deepcopy_content_ids_scheduled_for_deletion() == SetDeque(
        (content_id_first_list,))

    # Delete scheduled object at controlled places
    snapshot_holder.delete_scheduled_deepcopy_content_ids()

    assert len(snapshot_holder) == 1
    assert snapshot_holder.get_deepcopy_content_ids() == SetDeque((content_id_third_list,))
    assert snapshot_holder.get_deepcopy_content_ids_scheduled_for_deletion() == SetDeque()

    # Content ids for non-snapshot objects are ignored, even if cached in the deepcopy_memo, here
    # as a result of deepcopy() of my_third_list
    snapshot_holder.schedule_deepcopy_content_ids_for_deletion(content_id_second_list)

    assert len(snapshot_holder) == 1
    assert snapshot_holder.get_deepcopy_content_ids() == SetDeque((content_id_third_list,))
    assert snapshot_holder.get_deepcopy_content_ids_scheduled_for_deletion() == SetDeque()

    # Clear() should remove all snapshots, deepcopy_memo objects and scheduled deletions
    snapshot_holder.schedule_deepcopy_content_ids_for_deletion(content_id_third_list)

    assert len(snapshot_holder) == 1
    assert snapshot_holder.get_deepcopy_content_ids() == SetDeque((content_id_third_list,))
    assert snapshot_holder.get_deepcopy_content_ids_scheduled_for_deletion() == SetDeque(
        (content_id_third_list,))

    snapshot_holder.clear()

    assert len(snapshot_holder) == 0
    assert snapshot_holder.get_deepcopy_content_ids() == SetDeque()
    assert snapshot_holder.get_deepcopy_content_ids_scheduled_for_deletion() == SetDeque()
