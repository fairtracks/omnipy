from typing import Annotated, Iterator

import pytest


@pytest.fixture(scope='function', autouse=True)
def autouse_assert_snapshot_holder_and_deepcopy_memo_is_empty(
    assert_snapshot_holder_and_deepcopy_memo_are_empty_before_and_after: Annotated[Iterator[None],
                                                                                   pytest.fixture]
) -> Iterator[None]:
    return assert_snapshot_holder_and_deepcopy_memo_are_empty_before_and_after
