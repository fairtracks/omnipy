from typing import Annotated

import pytest

from omnipy.api.protocols.public.hub import IsRuntime
from omnipy.modules.json.datasets import (JsonDictDataset,
                                          JsonDictOfDictsDataset,
                                          JsonDictOfListsOfDictsDataset,
                                          JsonListDataset,
                                          JsonListOfDictsDataset)
from omnipy.modules.json.flows import (transpose_dict_of_dicts_2_list_of_dicts,
                                       transpose_dicts_of_lists_of_dicts_2_lists_of_dicts)
from omnipy.modules.json.tasks import transpose_dicts_2_lists


def test_transpose_empty_dicts_2_nothing(runtime: Annotated[IsRuntime, pytest.fixture]):
    out_dataset = transpose_dicts_2_lists.run(JsonDictDataset(dict(abc={}, bcd={})))
    assert type(out_dataset) is JsonListDataset
    assert out_dataset.to_data() == {}


def test_transpose_dict_of_numbers_2_lists_of_numbers(runtime: Annotated[IsRuntime,
                                                                         pytest.fixture],):

    in_dataset = JsonDictDataset(dict(abc={'a': 123}, bcd={'a': 456}))
    out_dataset_1 = transpose_dicts_2_lists.run(in_dataset)
    assert type(out_dataset_1) is JsonListDataset
    assert out_dataset_1.to_data() == {'a': [123, 456]}

    in_dataset_2 = JsonDictDataset(dict(abc={'a': 123, 'b': 321}, bcd={'a': 456, 'c': 654}))
    out_dataset_2 = transpose_dicts_2_lists.run(in_dataset_2)
    assert type(out_dataset_2) is JsonListDataset
    assert out_dataset_2.to_data() == {'a': [123, 456], 'b': [321], 'c': [654]}


def test_transpose_dicts_of_various_2_lists_of_various(runtime: Annotated[IsRuntime,
                                                                          pytest.fixture],):

    out_dataset = transpose_dicts_2_lists.run(
        JsonDictDataset(
            dict(
                abc={
                    'a': [{
                        'x': 33.2, 'y': 14.5
                    }, {
                        'x': 9.2, 'y': 21.3
                    }],
                    'b': [1, 2, 3],
                },
                bcd={
                    'a': {
                        'x': 2.34, 'y': 3.3
                    },
                    'b': [4, 5, 6],
                    'c': 654,
                })),)
    assert type(out_dataset) is JsonListDataset
    assert out_dataset.to_data() == {
        'a': [{
            '_omnipy_id': 'abc_0', 'x': 33.2, 'y': 14.5
        }, {
            '_omnipy_id': 'abc_1', 'x': 9.2, 'y': 21.3
        }, {
            '_omnipy_id': 'bcd_0', 'x': 2.34, 'y': 3.3
        }],
        'b': [1, 2, 3, 4, 5, 6],
        'c': [654]
    }


def test_transpose_dict_of_dicts_2_list_of_dicts(runtime: Annotated[IsRuntime, pytest.fixture],):

    out_dataset = transpose_dict_of_dicts_2_list_of_dicts.run(
        JsonDictOfDictsDataset(
            dict(
                abc={
                    'a': {
                        'x': True, 'y': None
                    }, 'b': {
                        'i': 123, 'ii': 234
                    }
                },
                bcd={
                    'a': {
                        'x': False
                    }, 'b': {
                        'i': 312, 'iii': 423
                    }
                },
            )),
        id_key='myid',
    )
    assert type(out_dataset) is JsonListOfDictsDataset
    assert out_dataset.to_data() == {
        'a': [
            {
                'myid': 'abc_0', 'x': True, 'y': None
            },
            {
                'myid': 'bcd_0', 'x': False
            },
        ],
        'b': [{
            'myid': 'abc_0', 'i': 123, 'ii': 234
        }, {
            'myid': 'bcd_0', 'i': 312, 'iii': 423
        }],
    }


def test_transpose_dicts_of_lists_of_dicts_2_lists_of_dicts(runtime: Annotated[IsRuntime,
                                                                               pytest.fixture],):

    out_dataset = transpose_dicts_of_lists_of_dicts_2_lists_of_dicts.run(
        JsonDictOfListsOfDictsDataset(
            dict(
                real={
                    'People': [{
                        'First name': 'Elvis',
                        'Last name': 'Presley',
                    }, {
                        'First name': 'Marilyn',
                        'Last name': 'Monroe',
                    }, {
                        'First name': 'Muhammad',
                        'Last name': 'Ali',
                    }],
                    'Cities': [
                        {
                            'Name': 'New York',
                            'Country': {
                                'Name': 'USA', 'Anthem': 'The Star-Spangled Banner'
                            }
                        },
                        {
                            'Name': 'Tbilisi',
                            'Country': {
                                'Name': 'Georgia', 'Anthem': 'Tavisupleba'
                            }
                        },
                    ],
                },
                fictional={
                    'People': [{
                        'First name': 'Clark',
                        'Last name': 'Kent',
                    }, {
                        'First name': 'Mister',
                        'Last name': 'Mxyzptlk',
                    }],
                    'Cities': [
                        {
                            'Name': 'Metropolis',
                            'Country': {
                                'Name': 'USA', 'Anthem': 'The Star-Spangled Banner'
                            }
                        },
                        {
                            'Name': 'Dark City',
                            'Country': None,
                        },
                    ],
                })),
        id_key='local_id')
    assert type(out_dataset) is JsonListOfDictsDataset
    assert out_dataset.to_data() == {
        'People': [
            {
                'local_id': 'real_0',
                'First name': 'Elvis',
                'Last name': 'Presley',
            },
            {
                'local_id': 'real_1',
                'First name': 'Marilyn',
                'Last name': 'Monroe',
            },
            {
                'local_id': 'real_2',
                'First name': 'Muhammad',
                'Last name': 'Ali',
            },
            {
                'local_id': 'fictional_0',
                'First name': 'Clark',
                'Last name': 'Kent',
            },
            {
                'local_id': 'fictional_1',
                'First name': 'Mister',
                'Last name': 'Mxyzptlk',
            },
        ],
        'Cities': [
            {
                'local_id': 'real_0',
                'Name': 'New York',
                'Country': {
                    'Name': 'USA', 'Anthem': 'The Star-Spangled Banner'
                }
            },
            {
                'local_id': 'real_1',
                'Name': 'Tbilisi',
                'Country': {
                    'Name': 'Georgia', 'Anthem': 'Tavisupleba'
                }
            },
            {
                'local_id': 'fictional_0',
                'Name': 'Metropolis',
                'Country': {
                    'Name': 'USA', 'Anthem': 'The Star-Spangled Banner'
                }
            },
            {
                'local_id': 'fictional_1',
                'Name': 'Dark City',
                'Country': None,
            },
        ],
    }
