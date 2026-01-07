from omnipy.components.json.typedefs import JsonScalar

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
