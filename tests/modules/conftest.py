from typing import Annotated, Iterator

import pytest


@pytest.fixture(scope='function', autouse=True)
def assert_snapshot_holder_and_deepcopy_memo_are_empty(
        assert_snapshot_holder_and_deepcopy_memo_are_empty) -> Iterator[None]:
    return assert_snapshot_holder_and_deepcopy_memo_are_empty
