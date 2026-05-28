from collections.abc import Iterable
from typing import Annotated, Mapping

import pytest

from omnipy.shared.protocols.hub.runtime import IsRuntime
from omnipy.shared.protocols.typing import IsMapping
from omnipy.util.contexts import hold_and_reset_prev_attrib_value

from .helpers.protocols import AssertColumnWiseMappings, AssertRowIter


@pytest.fixture(scope='function')
def assert_row_iter(runtime: Annotated[IsRuntime, pytest.fixture]) -> AssertRowIter:
    def _assert_row_iter(row_idx: int, row: IsMapping[str, object]) -> None:
        with hold_and_reset_prev_attrib_value(
                runtime.config.data.model,
                'dynamically_convert_elements_to_models',
        ):
            runtime.config.data.model.dynamically_convert_elements_to_models = False
            assert len(row) == 4
            assert tuple(row) == ('a', 'b', 'c', 'd')
            assert tuple(row.keys()) == ('a', 'b', 'c', 'd')

            if row_idx == 0:
                assert isinstance(row, Mapping)
                assert row['a'] == '1'
                assert row['b'] == 2
                assert row['c'] is True
                assert row['d'] is None
                assert dict(row) == {
                    'a': '1',
                    'b': 2,
                    'c': True,
                    'd': None,
                }
                assert tuple(row.values()) == ('1', 2, True, None)
            elif row_idx == 1:
                assert isinstance(row, Mapping)
                assert row['a'] == '4'
                assert row['b'] == 5
                assert row['c'] is None
                assert row['d'] == 'abc'
                assert dict(row) == {
                    'a': '4',
                    'b': 5,
                    'c': None,
                    'd': 'abc',
                }
                assert tuple(row.values()) == ('4', 5, None, 'abc')

            with pytest.raises(KeyError):
                row['non_existent_column']

            with pytest.raises(TypeError):
                row['a'] = 'new_value'  # type: ignore[index]

            with pytest.raises(TypeError):
                del row['a']  # type: ignore[attr-defined]

    return _assert_row_iter


@pytest.fixture(scope='function')
def assert_column_wise_mappings(
        runtime: Annotated[IsRuntime, pytest.fixture]) -> AssertColumnWiseMappings:
    def _assert_column_wise_mappings(
        a: IsMapping[str, Iterable[object]],
        b: IsMapping[str, Iterable[object]],
    ) -> None:
        assert set(a.keys()) == set(b.keys())

        with hold_and_reset_prev_attrib_value(
                runtime.config.data.model,
                'dynamically_convert_elements_to_models',
        ):
            runtime.config.data.model.dynamically_convert_elements_to_models = False
            for key in a.keys():
                a_col = list(a[key])
                b_col = list(b[key])
                assert len(a_col) == len(b_col)
                for i in range(len(a_col)):
                    assert a_col[i] == b_col[i]

    return _assert_column_wise_mappings
