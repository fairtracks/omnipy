from types import MappingProxyType

import pytest

from omnipy.modules.general.typedefs import FrozenDict


def test_frozendict_empty():
    empty_frozen_dict = FrozenDict()

    assert empty_frozen_dict == MappingProxyType({})

    with pytest.raises(KeyError):
        assert empty_frozen_dict['a']

    with pytest.raises(TypeError):
        assert empty_frozen_dict.update({'a': 'b'})


def test_frozendict_simple():
    simple_frozen_dict = FrozenDict({'a': 'b', 'c': 'd'})

    assert simple_frozen_dict == MappingProxyType({'a': 'b', 'c': 'd'})

    assert simple_frozen_dict['a'] == 'b'

    with pytest.raises(TypeError):
        simple_frozen_dict['a'] = 'e'

    with pytest.raises(TypeError):
        assert simple_frozen_dict.update({'a': 'e'})

    tuple_init_frozen_dict = FrozenDict((('a', 'b'), ('c', 'd')))
    assert tuple_init_frozen_dict == simple_frozen_dict


def test_nested_frozendict_mutable():
    nested_frozen_dict = FrozenDict({'nested': {}})

    assert nested_frozen_dict == MappingProxyType({'nested': {}})

    assert nested_frozen_dict['nested'] == {}

    with pytest.raises(TypeError):
        nested_frozen_dict['nested'] = {'a': 'b'}

    with pytest.raises(TypeError):
        assert nested_frozen_dict.update({'nested': {'a': 'b'}})

    nested_frozen_dict['nested']['a'] = 'b'
    assert nested_frozen_dict == MappingProxyType({'nested': {'a': 'b'}})
