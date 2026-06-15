from math import nan

from omnipy.components.json.typedefs import JsonScalar

from ...helpers.classes import ListLikeNoAdd

# JsonScalar

column_wise_dict_of_lists_data: dict[str, list[JsonScalar]] = {
    'a': ['1', '4'],
    'b': [2, 5],
    'c': [True, None],
    'd': [None, 'abc'],
}
other_col_wise_dict_of_lists_data: dict[str, list[JsonScalar]] = {
    'a': ['7', '2'],
    'b': [8, 3],
    'c': [False, None],
    'd': ['def', 'ghi'],
}
other_non_overlapping_col_wise_dict_of_lists_data: dict[str, list[JsonScalar]] = {
    'a': ['7', '2'],
    'c': [False, None],
    'd': ['def', 'ghi'],
    'e': [23.4, 32.3],
}
col_wise_dict_of_empty_lists_data: dict[str, list[JsonScalar]] = {
    'a': [], 'b': [], 'c': [], 'd': []
}
other_row_wise_list_of_dicts_data: list[dict[str, JsonScalar]] = [
    {
        'a': '7',
        'b': 8,
        'c': False,
        'd': 'def',
    },
    {
        'a': '2',
        'b': 3,
        'c': None,
        'd': 'ghi',
    },
]
concat_col_wise_data: dict[str, list[JsonScalar]] = {
    'a': ['1', '4', '7', '2'],
    'b': [2, 5, 8, 3],
    'c': [True, None, False, None],
    'd': [None, 'abc', 'def', 'ghi'],
}
concat_non_overlapping_col_wise_data: dict[str, list[JsonScalar]] = {
    'a': ['1', '4', '7', '2'],
    'b': [2, 5, None, None],
    'c': [True, None, False, None],
    'd': [None, 'abc', 'def', 'ghi'],
    'e': [None, None, 23.4, 32.3],
}
reverse_concat_col_wise_data: dict[str, list[JsonScalar]] = {
    'a': ['7', '2', '1', '4'],
    'b': [8, 3, 2, 5],
    'c': [False, None, True, None],
    'd': ['def', 'ghi', None, 'abc'],
}
reverse_concat_non_overlapping_col_wise_data: dict[str, list[JsonScalar]] = {
    'a': ['7', '2', '1', '4'],
    'b': [None, None, 2, 5],
    'c': [False, None, True, None],
    'd': ['def', 'ghi', None, 'abc'],
    'e': [23.4, 32.3, None, None],
}

# int

column_wise_dict_of_int_data: dict[str, list[int]] = {
    'a': [1, 4],
    'b': [2, 5],
}

column_wise_dict_of_other_int_data: dict[str, list[int]] = {
    'a': [7, 2],
    'c': [5, 2],
}

col_wise_list_likes_of_int_data: dict[str, ListLikeNoAdd[int]] = {
    'a': ListLikeNoAdd[int]([1, 4]),
    'b': ListLikeNoAdd[int]([2, 5]),
}

concat_col_wise_list_likes_of_int_data: dict[str, ListLikeNoAdd[int]] = {
    'a': ListLikeNoAdd[int]([1, 4, 7, 2]),
    'b': ListLikeNoAdd[int]([2, 5, 0, 0]),
    'c': ListLikeNoAdd[int]([0, 0, 5, 2]),
}

reversed_concat_col_wise_list_likes_of_int_data: dict[str, ListLikeNoAdd[int]] = {
    'a': ListLikeNoAdd[int]([7, 2, 1, 4]),
    'b': ListLikeNoAdd[int]([0, 0, 2, 5]),
    'c': ListLikeNoAdd[int]([5, 2, 0, 0]),
}

# float

row_wise_dict_of_other_float_data: list[dict[str, float]] = [
    {
        'c': 3.5
    },
    {
        'a': 8.1, 'b': 8.1
    },
]

concat_col_wise_list_likes_of_float_data: dict[str, ListLikeNoAdd[float]] = {
    'a': ListLikeNoAdd[float]([1.0, 4.0, nan, 8.1]),
    'b': ListLikeNoAdd[float]([2.0, 5.0, nan, 8.1]),
    'c': ListLikeNoAdd[float]([nan, nan, 3.5, nan]),
}

reversed_concat_col_wise_list_likes_of_float_data: dict[str, ListLikeNoAdd[float]] = {
    'a': ListLikeNoAdd[float]([nan, 8.1, 1.0, 4.0]),
    'b': ListLikeNoAdd[float]([nan, 8.1, 2.0, 5.0]),
    'c': ListLikeNoAdd[float]([3.5, nan, nan, nan]),
}
