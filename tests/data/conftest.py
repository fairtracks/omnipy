import gc

import pytest

from omnipy.data.model import Model


@pytest.fixture(scope='function', autouse=True)
def assert_snapshot_holder_and_deepcopy_memo_is_empty():
    snapshot_holder = Model.data_class_creator.snapshot_holder
    assert snapshot_holder.all_is_empty()
    yield
    gc.collect()
    snapshot_holder.delete_scheduled()
    assert snapshot_holder.all_is_empty()
