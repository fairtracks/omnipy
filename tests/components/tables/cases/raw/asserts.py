from typing import Mapping

import pytest

from omnipy.components.json.typedefs import JsonScalar


def assert_row_iter(row_idx: int, row: Mapping[str, JsonScalar]) -> None:
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
