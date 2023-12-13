from dataclasses import dataclass, field

import pytest_cases as pc

from omnipy.modules.json.datasets import (JsonDataset,
                                          JsonDictDataset,
                                          JsonDictOfDictsDataset,
                                          JsonDictOfDictsOfScalarsDataset,
                                          JsonDictOfListsDataset,
                                          JsonDictOfListsOfDictsDataset,
                                          JsonDictOfListsOfScalarsDataset,
                                          JsonDictOfNestedListsDataset,
                                          JsonDictOfScalarsDataset,
                                          JsonListDataset,
                                          JsonListOfDictsDataset,
                                          JsonListOfDictsOfScalarsDataset,
                                          JsonListOfListsDataset,
                                          JsonListOfListsOfScalarsDataset,
                                          JsonListOfNestedDictsDataset,
                                          JsonListOfScalarsDataset,
                                          JsonNestedDictsDataset,
                                          JsonNestedListsDataset,
                                          JsonNoDictsDataset,
                                          JsonNoListsDataset,
                                          JsonScalarDataset)
from omnipy.modules.json.models import (JsonDictModel,
                                        JsonDictOfDictsModel,
                                        JsonDictOfDictsOfScalarsModel,
                                        JsonDictOfListsModel,
                                        JsonDictOfListsOfDictsModel,
                                        JsonDictOfListsOfScalarsModel,
                                        JsonDictOfNestedListsModel,
                                        JsonDictOfScalarsModel,
                                        JsonListModel,
                                        JsonListOfDictsModel,
                                        JsonListOfDictsOfScalarsModel,
                                        JsonListOfListsModel,
                                        JsonListOfListsOfScalarsModel,
                                        JsonListOfNestedDictsModel,
                                        JsonListOfScalarsModel,
                                        JsonModel,
                                        JsonNestedDictsModel,
                                        JsonNestedListsModel,
                                        JsonNoDictsModel,
                                        JsonNoListsModel,
                                        JsonScalarModel)
from omnipy.modules.json.typedefs import JsonScalar as JS

from ...helpers.classes import CaseInfo
from .raw.examples import (b_bool,
                           b_dict,
                           b_float,
                           b_int,
                           b_list,
                           b_none,
                           b_set,
                           b_str,
                           b_tuple,
                           e_bool_key_dict,
                           e_float_key_dict,
                           e_int_key_dict,
                           e_none_key_dict)


@pc.case(id='test_json_scalar', tags=[])
def case_json_scalar() -> CaseInfo:
    @dataclass
    class ScalarDataPoints:
        #
        # JsonScalarModel
        #

        s_none: None = b_none
        s_int: int = b_int
        s_float: float = b_float
        s_str: str = b_str
        s_bool: bool = b_bool
        err_s_list: list[JS] = field(default_factory=lambda: b_list)
        err_s_dict: dict[str, JS] = field(default_factory=lambda: dict(b_dict))
        err_s_tuple: tuple[JS, ...] = b_tuple
        err_s_set: set[JS] = field(default_factory=lambda: set(b_set))

    return CaseInfo(
        name='test_json_scalar',
        prefix2model_classes={'s': (JsonScalarModel,)},
        prefix2dataset_classes={'s': (JsonScalarDataset,)},
        data_points=ScalarDataPoints(),
    )


@pc.case(id='test_json_list', tags=[])
def case_json_list() -> CaseInfo:
    @dataclass
    class JsonListDataPoints:
        #
        # JsonListModel
        #

        err_l_none: None = b_none
        err_l_int: int = b_int
        err_l_float: float = b_float
        err_l_str: str = b_str
        err_l_bool: bool = b_bool
        l_list: list[JS] = field(default_factory=lambda: list(b_list))
        err_l_dict: dict[str, JS] = field(default_factory=lambda: dict(b_dict))
        l_tuple: tuple[JS, ...] = b_tuple  # Orig: err_l_tuple. Due to parsing to list
        l_set: set[JS] = field(
            default_factory=lambda: set(b_set))  # Orig: err_l_tuple. Due to parsing to list

    return CaseInfo(
        name='test_json_list',
        prefix2model_classes={'l': (JsonListModel,)},
        prefix2dataset_classes={'l': (JsonListDataset,)},
        data_points=JsonListDataPoints(),
    )


@pc.case(id='test_json_dict', tags=[])
def case_json_dict() -> CaseInfo:
    @dataclass
    class JsonDictDataPoints:
        #
        # JsonDictModel
        #

        err_d_none: None = b_none
        err_d_int: int = b_int
        err_d_float: float = b_float
        err_d_str: str = b_str
        err_d_bool: bool = b_bool
        err_d_list: list[JS] = field(default_factory=lambda: list(b_list))
        d_dict: dict[str, JS] = field(default_factory=lambda: dict(b_dict))

        # Orig: err_d_int_key_dict. Due to parsing to str
        d_int_key_dict: dict[int, JS] = field(default_factory=lambda: dict(e_int_key_dict))

        # Orig: err_d_float_key_dict. Due to parsing to str
        d_float_key_dict: dict[float, JS] = field(default_factory=lambda: dict(e_float_key_dict))

        # Orig: err_d_bool_key_dict. Due to parsing to str
        d_bool_key_dict: dict[bool, JS] = field(default_factory=lambda: dict(e_bool_key_dict))

        err_d_none_key_dict: dict[None, JS] = field(default_factory=lambda: dict(e_none_key_dict))
        err_d_tuple: tuple[JS, ...] = b_tuple
        err_d_set: set[JS] = field(default_factory=lambda: set(b_set))

    return CaseInfo(
        name='test_json_dict',
        prefix2model_classes={'d': (JsonDictModel,)},
        prefix2dataset_classes={'d': (JsonDictDataset,)},
        data_points=JsonDictDataPoints(),
    )


@pc.case(id='test_json', tags=[])
def case_json() -> CaseInfo:
    @dataclass
    class JsonDataPoints:
        #
        # JsonModel
        #

        j_none: None = b_none
        j_int: int = b_int
        j_float: float = b_float
        j_str: str = b_str
        j_bool: bool = b_bool
        j_list: list[JS] = field(default_factory=lambda: list(b_list))
        j_dict: dict[str, JS] = field(default_factory=lambda: dict(b_dict))

        # Orig: err_j_int_key_dict. Due to parsing to str
        j_int_key_dict: dict[int, JS] = \
            field(default_factory=lambda: dict(e_int_key_dict))

        # Orig: err_j_float_key_dict. Due to parsing to str
        j_float_key_dict: dict[float, JS] = \
            field(default_factory=lambda: dict(e_float_key_dict))

        # Orig: err_j_bool_key_dict. Due to parsing to str
        j_bool_key_dict: dict[bool, JS] = \
            field(default_factory=lambda: dict(e_bool_key_dict))

        err_j_none_key_dict: dict[None, JS] = field(default_factory=lambda: dict(e_none_key_dict))

        # Orig: err_j_tuple. Due to parsing to list
        j_tuple: tuple[JS, ...] = b_tuple

        # Orig: err_j_set. Due to parsing to list
        j_set: set[JS] = field(default_factory=lambda: set(b_set))

    return CaseInfo(
        name='test_json',
        prefix2model_classes={'j': (JsonModel,)},
        prefix2dataset_classes={'j': (JsonDataset,)},
        data_points=JsonDataPoints(),
    )


@pc.case(id='test_json_nested', tags=[])
def case_json_nested() -> CaseInfo:
    _two_level_list: list[JS | list[JS] | dict[str, JS]] = b_list + [list(b_list)] + [dict(b_dict)]
    _two_level_dict: dict[str, str | list[JS] | dict[str, JS]] = {
        'a': b_str, 'b': list(b_list), 'c': dict(b_dict)
    }

    @dataclass
    class JsonNestedDataPoints:
        #
        # JsonListModel and JsonModel
        #

        # Origs: l_two_level_list, j_two_level_list
        lj_two_level_list: list[JS | list[JS] | dict[str, JS]] = \
            field(default_factory=lambda: _two_level_list)

        err_lj_two_level_none_key_list: list[JS | dict[None, bool]] = \
            field(default_factory=lambda: list(b_list) + [dict(e_none_key_dict)])

        # Origs: err_l_two_level_int_key_list, err_j_two_level_int_key_list. Due to parsing to str
        lj_two_level_int_key_list: list[JS | dict[int, None]] = \
            field(default_factory=lambda: list(b_list) + [dict(e_int_key_dict)])

        # Origs: err_l_two_level_set_list, err_j_two_level_set_list. Due to parsing to list
        lj_two_level_set_list: list[JS | dict[str, JS] | set[JS]] = \
            field(default_factory=lambda: list(b_list) + [dict(b_dict)] + [set(b_set)])

        # Origs: l_three_level_list, j_three_level_list
        lj_three_level_list: list[JS | list[JS] | dict[str, JS]
                                  | list[JS | list[JS] | dict[str, JS]]
                                  | dict[str, str | list[JS] | dict[str, JS]]] = \
            field(default_factory=lambda: list(b_list + [list(b_list), dict(b_dict),
                                                         list(_two_level_list),
                                                         dict(_two_level_dict)]))

        #
        # JsonListModel and JsonModel
        #

        # Origs: d_two_level_dict, j_two_level_dict
        dj_two_level_dict: dict[str, str | list[JS] | dict[str, JS]] = \
            field(default_factory=lambda: _two_level_dict)

        err_dj_two_level_none_key_dicts: dict[str, JS | dict[None, bool]] = \
            field(default_factory=lambda: {'f': dict(e_none_key_dict)})

        # Origs: err_d_two_level_bool_key_dict, err_j_two_level_bool_key_dict. Due to parsing to str
        dj_two_level_bool_key_dict: dict[str, list[JS] | dict[bool, str]] = \
            field(default_factory=lambda: {'f': list(b_list), 'g': dict(e_bool_key_dict)})

        # Origs: err_d_two_level_set_dict, err_j_two_level_set_dict. Due to parsing to list
        dj_two_level_set_dict: dict[str, list[JS] | set[JS]] = \
            field(default_factory=lambda: {'f': list(b_list), 'g': set(b_set)})

        # Origs: d_three_level_dict, j_three_level_dict
        dj_three_level_dict: dict[str, int | list[JS] | dict[str, JS]
                                  | list[JS | list[JS] | dict[str, JS]]
                                  | dict[str, str | list[JS] | dict[str, JS]]] = \
            field(default_factory=lambda: {'a': b_int, 'b': list(b_list), 'c': dict(b_dict),
                                           'd': list(_two_level_list), 'e': dict(_two_level_dict)})

    return CaseInfo(
        name='test_json_nested',
        prefix2model_classes={
            'lj': (JsonListModel, JsonModel),
            'dj': (JsonDictModel, JsonModel),
        },
        prefix2dataset_classes={
            'lj': (JsonListDataset, JsonDataset),
            'dj': (JsonDictDataset, JsonDataset),
        },
        data_points=JsonNestedDataPoints(),
    )


@pc.case(id='test_json_list_on_top', tags=[])
def case_json_list_on_top() -> CaseInfo:
    @dataclass
    class JsonListOnTopDataPoints:

        #
        # JsonListOfScalarsModel
        #

        err_l_list_of_scalars_none: None = b_none
        err_l_list_of_scalars_int: int = b_int
        err_l_list_of_scalars_float: float = b_float
        err_l_list_of_scalars_str: str = b_str
        err_l_list_of_scalars_bool: bool = b_bool
        l_list_of_scalars_list: list[JS] = field(default_factory=lambda: list(b_list))
        err_l_list_of_scalars_dict: dict[str, JS] = field(default_factory=lambda: dict(b_dict))

        # Orig: err_l_list_of_scalars_tuple. Due to parsing to list
        l_list_of_scalars_tuple: tuple[JS, ...] = b_tuple

        # Orig: err_l_list_of_scalars_set. Due to parsing to list
        l_list_of_scalars_set: set[JS] = field(default_factory=lambda: set(b_set))

        err_l_list_of_scalars_with_list_at_level_two: list[JS | list[JS]] = \
            field(default_factory=lambda: list(b_list + [list(b_list)]))
        err_l_list_of_scalars_with_dict_at_level_two: list[JS | dict[str, JS]] = \
            field(default_factory=lambda: list(b_list + [dict(b_dict)]))

        #
        # JsonListOfListsModel
        #

        err_l_list_of_lists_none: None = b_none
        err_l_list_of_lists_int: int = b_int
        err_l_list_of_lists_list_of_none: list[None] = field(default_factory=lambda: [b_none])
        err_l_list_of_lists_one_level: list[JS] = field(default_factory=lambda: list(b_list))
        l_list_of_lists: list[list[JS]] = \
            field(default_factory=lambda: [list(b_list), list(b_list)])
        err_l_list_of_lists_with_dict_at_level_two: list[list[JS] | dict[str, JS]] = \
            field(default_factory=lambda: [list(b_list), dict(b_dict)])
        err_l_list_of_lists_with_scalars_at_level_two: list[JS | list[JS]] = \
            field(default_factory=lambda: list(b_list + [list(b_list)]))
        l_list_of_lists_three_levels: list[list[JS | list[JS] | dict[str, JS]]] = \
            field(default_factory=lambda: [list(b_list), [list(b_list), dict(b_dict)]])

        #
        # JsonListOfListsOfScalarsModel
        #

        err_l_list_of_lists_of_scalar_none: None = b_none
        err_l_list_of_lists_of_scalars_float: float = b_float
        err_l_list_of_lists_of_scalar_list_of_none: list[None] = \
            field(default_factory=lambda: [b_none])
        err_l_list_of_lists_of_scalars_one_level: list[JS] = \
            field(default_factory=lambda: list(b_list))
        l_list_of_lists_of_scalars: list[list[JS]] = \
            field(default_factory=lambda: [list(b_list), list(b_list)])
        err_l_list_of_lists_of_scalars_with_dict_at_level_two: list[list[JS] | dict[str, JS]] = \
            field(default_factory=lambda: [list(b_list), dict(b_dict)])
        err_l_list_of_lists_of_scalars_with_scalars_at_level_two: list[JS | list[JS]] = \
            field(default_factory=lambda: list(b_list + [list(b_list)]))
        err_l_list_of_lists_of_scalars_three_levels: list[list[JS] | list[list[JS]]] = \
            field(default_factory=lambda: [list(b_list), [list(b_list)]])

        #
        # JsonListOfDictsModel
        #

        err_l_list_of_dicts_none: None = b_none
        err_l_list_of_dicts_str: str = b_str
        err_l_list_of_dicts_list_of_none: list[None] = field(default_factory=lambda: [b_none])
        err_l_list_of_dicts_one_level: list[JS] = field(default_factory=lambda: list(b_list))
        l_list_of_dicts: list[dict[str, JS]] = \
            field(default_factory=lambda: [dict(b_dict), dict(b_dict)])
        err_l_list_of_dicts_with_list_at_level_two: list[dict[str, JS] | list[JS]] = \
            field(default_factory=lambda: [dict(b_dict), list(b_list)])
        err_l_list_of_dicts_with_scalars_at_level_two: list[JS | dict[str, JS]] = \
            field(default_factory=lambda: list(b_list + [dict(b_dict)]))
        l_list_of_dicts_three_levels: list[dict[str, JS | list[JS]]] = \
            field(default_factory=lambda: [dict(b_dict), {'a': list(b_list)}])

        #
        # JsonListOfDictsOfScalarsModel
        #

        err_l_list_of_dicts_of_scalars_none: None = b_none
        err_l_list_of_dicts_of_scalars_bool: bool = b_bool
        err_l_list_of_dicts_of_scalars_list_of_none: list[None] = \
            field(default_factory=lambda: [b_none])
        err_l_list_of_dicts_of_scalars_one_level: list[JS] = \
            field(default_factory=lambda: list(b_list))
        l_list_of_dicts_of_scalars: list[dict[str, JS]] = \
            field(default_factory=lambda: [dict(b_dict), dict(b_dict)])
        err_l_list_of_dicts_of_scalars_with_list_at_level_two: list[dict[str, JS] | list[JS]] = \
            field(default_factory=lambda: [dict(b_dict), list(b_list)])
        err_l_list_of_dicts_of_scalars_with_scalars_at_level_two: list[JS | dict[str, JS]] = \
            field(default_factory=lambda: list(b_list + [dict(b_dict)]))
        err_l_list_of_dicts_of_scalars_three_levels: list[dict[str, JS | list[JS]]] = \
            field(default_factory=lambda: [dict(b_dict), {'a': list(b_list)}])

    return CaseInfo(
        name='test_json_list_on_top',
        prefix2model_classes={
            'l_list_of_scalars': (JsonListOfScalarsModel,),
            'l_list_of_lists_of_scalars': (JsonListOfListsOfScalarsModel,),
            'l_list_of_lists': (JsonListOfListsModel,),
            'l_list_of_dicts_of_scalars': (JsonListOfDictsOfScalarsModel,),
            'l_list_of_dicts': (JsonListOfDictsModel,),
        },
        prefix2dataset_classes={
            'l_list_of_scalars': (JsonListOfScalarsDataset,),
            'l_list_of_lists_of_scalars': (JsonListOfListsOfScalarsDataset,),
            'l_list_of_lists': (JsonListOfListsDataset,),
            'l_list_of_dicts_of_scalars': (JsonListOfDictsOfScalarsDataset,),
            'l_list_of_dicts': (JsonListOfDictsDataset,),
        },
        data_points=JsonListOnTopDataPoints(),
    )


@pc.case(id='test_json_dict_on_top', tags=[])
def case_json_dict_on_top() -> CaseInfo:
    @dataclass
    class JsonDictOnTopDataPoints:

        #
        # JsonDictOfScalarsModel
        #

        err_d_dict_of_scalars_none: None = b_none
        err_d_dict_of_scalars_int: int = b_int
        err_d_dict_of_scalars_float: float = b_float
        err_d_dict_of_scalars_str: str = b_str
        err_d_dict_of_scalars_bool: bool = b_bool
        err_d_dict_of_scalars_list: list[JS] = field(default_factory=lambda: list(b_list))
        d_dict_of_scalars_dict: dict[str, JS] = field(default_factory=lambda: dict(b_dict))

        # Orig: err_d_dict_of_scalars_int_key_dict. Due to parsing to str
        d_dict_of_scalars_int_key_dict: dict[int, JS] = \
            field(default_factory=lambda: dict(e_int_key_dict))

        # Orig: err_d_dict_of_scalars_float_key_dict. Due to parsing to str
        d_dict_of_scalars_float_key_dict: dict[float, JS] = \
            field(default_factory=lambda: dict(e_float_key_dict))

        # Orig: err_d_dict_of_scalars_bool_key_dict. Due to parsing to str
        d_dict_of_scalars_bool_key_dict: dict[bool, JS] = \
            field(default_factory=lambda: dict(e_bool_key_dict))

        err_d_dict_of_scalars_none_key_dict: dict[None, JS] = \
            field(default_factory=lambda: dict(e_none_key_dict))

        err_d_dict_of_scalars_tuple: tuple[JS, ...] = b_tuple
        err_d_dict_of_scalars_set: set[JS] = field(default_factory=lambda: set(b_set))
        err_d_dict_of_scalars_with_list_at_level_two: dict[str, JS | list[JS]] = \
            field(default_factory=lambda: {'a': b_bool, 'b': list(b_list)})
        err_d_dict_of_scalars_with_dict_at_level_two: dict[str, JS | dict[str, JS]] = \
            field(default_factory=lambda: {'a': b_bool, 'b': dict(b_dict)})

        #
        # JsonDictOfListsModel
        #

        err_d_dict_of_lists_none: None = b_none
        err_d_dict_of_lists_int: int = b_int
        err_d_dict_of_lists_dict_of_none: dict[str, None] = \
            field(default_factory=lambda: {'a': b_none})
        err_d_dict_of_lists_one_level: dict[str, JS] = field(default_factory=lambda: dict(b_dict))
        d_dict_of_lists: dict[str, list[JS]] = \
            field(default_factory=lambda: {'a': list(b_list), 'b': list(b_list)})
        err_d_dict_of_lists_with_dict_at_level_two: dict[str, list[JS] | dict[str, JS]] = \
            field(default_factory=lambda: {'a': list(b_list), 'b': dict(b_dict)})
        err_d_dict_of_lists_with_scalars_at_level_two: dict[str, float | list[JS]] = \
            field(default_factory=lambda: {'a': b_float, 'b': list(b_list)})
        d_dict_of_lists_three_levels: dict[str, list[JS | dict[str, None | list[JS]]]] = \
            field(default_factory=lambda: {'a': list(b_list),
                                           'b': [{'x': b_none, 'y': list(b_list)}]})

        #
        # JsonDictOfListsOfScalarsModel
        #

        err_d_dict_of_lists_of_scalars_none: None = b_none
        err_d_dict_of_lists_of_scalars_float: float = b_float
        err_d_dict_of_lists_of_scalars_one_level: dict[str, JS] = \
            field(default_factory=lambda: dict(b_dict))
        err_d_dict_of_lists_of_scalars_dict_of_none: dict[str, None] = \
            field(default_factory=lambda: {'a': b_none})
        d_dict_of_lists_of_scalars: dict[str, list[JS]] = \
            field(default_factory=lambda: {'a': list(b_list), 'b': list(b_list)})
        err_d_dict_of_lists_of_scalars_with_dict_at_level_two: \
            dict[str, list[JS] | dict[str, JS]] = \
            field(default_factory=lambda: {'a': list(b_list), 'b': dict(b_dict)})
        err_d_dict_of_lists_of_scalars_with_scalars_at_level_two: dict[str, JS | list[JS]] = \
            field(default_factory=lambda: {'a': b_none, 'b': list(b_list)})
        err_d_dict_of_lists_of_scalars_three_levels: dict[str, list[JS] | list[list[JS]]] = \
            field(default_factory=lambda: {'a': list(b_list), 'b': [list(b_list)]})

        #
        # JsonDictOfDictsModel
        #

        err_d_dict_of_dicts_none: None = b_none
        err_d_dict_of_dicts_str: str = b_str
        d_dict_of_dicts_empty_dict: dict[str, JS] = field(default_factory=lambda: {})
        err_d_dict_of_dicts_dict_of_none: dict[str, None] = \
            field(default_factory=lambda: {'a': b_none})
        err_d_dict_of_dicts_one_level: dict[str, JS] = field(default_factory=lambda: dict(b_dict))
        d_dict_of_dicts: dict[str, dict[str, JS]] = \
            field(default_factory=lambda: {'a': {}, 'b': dict(b_dict)})
        # Orig: err_d_dict_of_dicts_with_empty_list_at_level_two. Due to parsing to dict (v1)
        d_dict_of_dicts_with_empty_list_at_level_two: dict[str, dict[str, JS] | list[JS]] = \
            field(default_factory=lambda: {'a': {}, 'b': dict(b_dict), 'c': []})
        err_d_dict_of_dicts_with_list_at_level_two: dict[str, dict[str, JS] | list[JS]] = \
            field(default_factory=lambda: {'a': {}, 'b': dict(b_dict), 'c': list(b_list)})
        err_d_dict_of_dicts_with_scalars_at_level_two: dict[str, JS | dict[str, JS]] = \
            field(default_factory=lambda: {'a': b_str, 'b': {}, 'c': dict(b_dict)})
        d_dict_of_dicts_three_levels: dict[str, dict[str, JS | list[JS] | dict[str, JS]]] = \
            field(default_factory=lambda: {'a': dict(b_dict),
                                           'b': {'w': [], 'x': list(b_list),
                                                 'y': {}, 'z': dict(b_dict)}})

        #
        # JsonDictOfDictsOfScalarsModel
        #

        err_d_dict_of_dicts_of_scalars_none: None = b_none
        err_d_dict_of_dicts_of_scalars_bool: bool = b_bool
        d_dict_of_dicts_of_scalars_empty_dict: dict[str, JS] = field(default_factory=lambda: {})
        err_d_dict_of_dicts_of_scalars_dict_of_none: dict[str, None] = \
            field(default_factory=lambda: {'a': b_none})
        err_d_dict_of_dicts_of_scalars_one_level: dict[str, JS] = \
            field(default_factory=lambda: dict(b_dict))
        d_dict_of_dicts_of_scalars: dict[str, dict[str, JS]] = \
            field(default_factory=lambda: {'a': {}, 'b': dict(b_dict)})
        # Orig: d_dict_of_dicts_of_scalars_with_empty_list_at_level_two. Due to parsing to dict (v1)
        d_dict_of_dicts_of_scalars_with_empty_list_at_level_two: \
            dict[str, dict[str, JS] | list[JS]] = \
            field(default_factory=lambda: {'a': {}, 'b': dict(b_dict), 'c': []})
        err_d_dict_of_dicts_of_scalars_with_list_at_level_two: \
            dict[str, dict[str, JS] | list[JS]] = \
            field(default_factory=lambda: {'a': {}, 'b': dict(b_dict), 'c': list(b_list)})
        err_d_dict_of_dicts_of_scalars_with_scalars_at_level_two: dict[str, JS | dict[str, JS]] = \
            field(default_factory=lambda: {'a': b_str, 'b': {}, 'c': dict(b_dict)})
        err_d_dict_of_dicts_of_scalars_three_levels_empty_dict: \
            dict[str, dict[str, JS | dict[str, JS]]] = \
            field(default_factory=lambda: {'a': dict(b_dict), 'b': {'x': {}}})
        err_d_dict_of_dicts_of_scalars_three_levels_dict: \
            dict[str, dict[str, JS | dict[str, JS]]] = \
            field(default_factory=lambda: {'a': dict(b_dict), 'b': {'x': dict(b_dict)}})

    return CaseInfo(
        name='test_json_dict_on_top',
        prefix2model_classes={
            'd_dict_of_scalars': (JsonDictOfScalarsModel,),
            'd_dict_of_lists_of_scalars': (JsonDictOfListsOfScalarsModel,),
            'd_dict_of_lists': (JsonDictOfListsModel,),
            'd_dict_of_dicts_of_scalars': (JsonDictOfDictsOfScalarsModel,),
            'd_dict_of_dicts': (JsonDictOfDictsModel,),
        },
        prefix2dataset_classes={
            'd_dict_of_scalars': (JsonDictOfScalarsDataset,),
            'd_dict_of_lists_of_scalars': (JsonDictOfListsOfScalarsDataset,),
            'd_dict_of_lists': (JsonDictOfListsDataset,),
            'd_dict_of_dicts_of_scalars': (JsonDictOfDictsOfScalarsDataset,),
            'd_dict_of_dicts': (JsonDictOfDictsDataset,),
        },
        data_points=JsonDictOnTopDataPoints(),
    )


@pc.case(id='test_json_nested_lists', tags=[])
def case_json_nested_lists() -> CaseInfo:
    @dataclass
    class JsonNestedListsDataPoints:

        #
        # JsonNoDictsModel
        #

        v_no_dicts_none: None = b_none
        v_no_dicts_int: int = b_int
        v_no_dicts_float: float = b_float
        v_no_dicts_str: str = b_str
        v_no_dicts_bool: bool = b_bool
        v_no_dicts_list: list[JS] = field(default_factory=lambda: list(b_list))
        err_v_no_dicts_dict: dict[str, JS] = field(default_factory=lambda: dict(b_dict))

        # Orig: err_v_no_dicts_tuple. Due to parsing to list
        v_no_dicts_tuple: tuple[JS, ...] = b_tuple

        # Orig: err_v_no_dicts_set. Due to parsing to list
        v_no_dicts_set: set[JS] = field(default_factory=lambda: set(b_set))

        v_no_dicts_list_of_none: list[None] = field(default_factory=lambda: [b_none])
        err_v_no_dicts_dict_of_none: dict[str, None] = field(default_factory=lambda: {'a': b_none})
        v_no_dicts_two_levels: list[JS | list[JS]] = \
            field(default_factory=lambda: list(b_list + [list(b_list)]))
        v_no_dicts_three_levels: list[JS | list[JS | list[JS]]] = \
            field(default_factory=lambda: list(b_list + [list(b_list), [list(b_list)]]))
        err_v_no_dicts_with_dict_of_none_level_two: list[JS | dict[str, None]] = \
            field(default_factory=lambda: [{'a': b_none}])
        err_v_no_dicts_with_dict_level_two: list[JS | dict[str, JS]] = \
            field(default_factory=lambda: list(b_list + [dict(b_dict)]))
        err_v_no_dicts_with_dict_level_three: list[JS | list[JS | dict[str, JS]]] = \
            field(default_factory=lambda: list(b_list + [list(b_list + [dict(b_dict)])]))

        #
        # JsonNestedListsModel
        #

        err_v_nested_lists_none: None = b_none
        err_v_nested_lists_int: int = b_int
        err_v_nested_lists_float: float = b_float
        err_v_nested_lists_str: str = b_str
        err_v_nested_lists_bool: bool = b_bool
        v_nested_lists_list: list[JS] = field(default_factory=lambda: list(b_list))
        err_v_nested_lists_dict: dict[str, JS] = field(default_factory=lambda: dict(b_dict))

        # Orig: err_v_nested_lists_tuple. Due to parsing to list
        v_nested_lists_tuple: tuple[JS, ...] = b_tuple

        # Orig: err_v_nested_lists_set. Due to parsing to list
        v_nested_lists_set: set[JS] = field(default_factory=lambda: set(b_set))

        v_nested_lists_list_of_none: list[None] = \
            field(default_factory=lambda: [b_none])
        err_v_nested_lists_dict_of_none: dict[str, None] = \
            field(default_factory=lambda: {'a': b_none})
        v_nested_lists_two_levels: list[JS | list[JS]] = \
            field(default_factory=lambda: list(b_list + [list(b_list)]))
        v_nested_lists_three_levels: list[JS | list[JS | list[JS]]] = \
            field(default_factory=lambda: list(b_list + [list(b_list), [list(b_list)]]))
        err_v_nested_lists_with_dict_of_none_level_two: list[dict[str, None]] = \
            field(default_factory=lambda: [{'a': b_none}])
        err_v_nested_lists_with_dict_level_two: list[JS | dict[str, JS]] = \
            field(default_factory=lambda: list(b_list + [dict(b_dict)]))
        err_v_nested_lists_with_dict_level_three: list[JS | list[JS | dict[str, JS]]] = \
            field(default_factory=lambda: list(b_list + [list(b_list + [dict(b_dict)])]))

    return CaseInfo(
        name='test_json_nested_lists',
        prefix2model_classes={
            'v_no_dicts': (JsonNoDictsModel,),
            'v_nested_lists': (JsonNestedListsModel,),
        },
        prefix2dataset_classes={
            'v_no_dicts': (JsonNoDictsDataset,),
            'v_nested_lists': (JsonNestedListsDataset,),
        },
        data_points=JsonNestedListsDataPoints(),
    )


@pc.case(id='test_json_nested_dicts', tags=[])
def case_json_nested_dicts() -> CaseInfo:
    @dataclass
    class JsonNestedDictsDataPoints:
        #
        # JsonNoListsModel
        #

        v_no_lists_none: None = b_none
        v_no_lists_int: int = b_int
        v_no_lists_float: float = b_float
        v_no_lists_str: str = b_str
        v_no_lists_bool: bool = b_bool
        err_v_no_lists_list: list[JS] = field(default_factory=lambda: list(b_list))
        v_no_lists_dict: dict[str, JS] = field(default_factory=lambda: dict(b_dict))

        # Orig: err_v_no_lists_int_key_dict. Due to parsing to str
        v_no_lists_int_key_dict: dict[int, JS] = field(default_factory=lambda: dict(e_int_key_dict))

        # Orig: err_v_no_lists_float_key_dict. Due to parsing to str
        v_no_lists_float_key_dict: dict[float, JS] = \
            field(default_factory=lambda: dict(e_float_key_dict))

        # Orig: err_v_no_lists_bool_key_dict. Due to parsing to str
        v_no_lists_bool_key_dict: dict[bool, JS] = \
            field(default_factory=lambda: dict(e_bool_key_dict))

        err_v_no_lists_none_key_dict: dict[None, JS] = \
            field(default_factory=lambda: dict(e_none_key_dict))
        err_v_no_lists_tuple: tuple[JS, ...] = b_tuple
        err_v_no_lists_set: set[JS] = field(default_factory=lambda: set(b_set))

        err_v_no_lists_list_of_none: list[None] = field(default_factory=lambda: [b_none])
        v_no_lists_dict_of_none: dict[str, None] = field(default_factory=lambda: {'a': b_none})
        v_no_lists_two_levels: dict[str, dict[str, JS]] = \
            field(default_factory=lambda: {'a': dict(b_dict), 'b': dict(b_dict)})
        v_no_lists_three_levels: dict[str, dict[str, JS | dict[str, JS]]] = \
            field(default_factory=lambda: {'a': dict(b_dict), 'b': {'x': dict(b_dict)}})
        err_v_no_lists_with_list_of_none_level_two: dict[str, list[None]] = \
            field(default_factory=lambda: {'a': [b_none]})
        err_v_no_lists_with_list_level_two: dict[str, dict[str, JS] | list[JS]] = \
            field(default_factory=lambda: {'a': dict(b_dict), 'b': list(b_list)})
        err_v_no_lists_with_list_level_three: dict[str, dict[str, JS | list[JS]]] = \
            field(default_factory=lambda: {'a': dict(b_dict), 'b': {'x': list(b_list)}})

        #
        # JsonNestedDictsModel
        #

        err_v_nested_dicts_none: None = b_none
        err_v_nested_dicts_int: int = b_int
        err_v_nested_dicts_float: float = b_float
        err_v_nested_dicts_str: str = b_str
        err_v_nested_dicts_bool: bool = b_bool
        err_v_nested_dicts_list: list[JS] = field(default_factory=lambda: list(b_list))
        v_nested_dicts_dict: dict[str, JS] = field(default_factory=lambda: dict(b_dict))

        # Orig: err_v_nested_dicts_int_key_dict. Due to parsing to str
        v_nested_dicts_int_key_dict: dict[int, JS] = \
            field(default_factory=lambda: dict(e_int_key_dict))

        # Orig: err_v_nested_dicts_float_key_dict. Due to parsing to str
        v_nested_dicts_float_key_dict: dict[float, JS] = \
            field(default_factory=lambda: dict(e_float_key_dict))

        # Orig: err_v_nested_dicts_bool_key_dict. Due to parsing to str
        v_nested_dicts_bool_key_dict: dict[bool, JS] = \
            field(default_factory=lambda: dict(e_bool_key_dict))

        err_v_nested_dicts_none_key_dict: dict[None, JS] = \
            field(default_factory=lambda: dict(e_none_key_dict))
        err_v_nested_dicts_tuple: tuple[JS, ...] = b_tuple
        err_v_nested_dicts_set: set[JS] = field(default_factory=lambda: set(b_set))

        err_v_nested_dicts_list_of_none: list[None] = \
            field(default_factory=lambda: [b_none])
        v_nested_dicts_dict_of_none: dict[str, None] = \
            field(default_factory=lambda: {'a': b_none})
        v_nested_dicts_two_levels: dict[str, dict[str, JS]] = \
            field(default_factory=lambda: {'a': dict(b_dict), 'b': dict(b_dict)})
        v_nested_dicts_three_levels: dict[str, dict[str, JS | dict[str, JS]]] = \
            field(default_factory=lambda: {'a': dict(b_dict), 'b': {'x': dict(b_dict)}})
        err_v_nested_dicts_with_list_of_none_level_two: dict[str, list[None]] = \
            field(default_factory=lambda: {'a': [b_none]})
        err_v_nested_dicts_with_list_level_two: dict[str, dict[str, JS] | list[JS]] = \
            field(default_factory=lambda: {'a': dict(b_dict), 'b': list(b_list)})
        err_v_nested_dicts_with_list_level_three: dict[str, dict[str, JS | list[JS]]] = \
            field(default_factory=lambda: {'a': dict(b_dict), 'b': {'x': list(b_list)}})

    return CaseInfo(
        name='test_json_nested_dicts',
        prefix2model_classes={
            'v_no_lists': (JsonNoListsModel,),
            'v_nested_dicts': (JsonNestedDictsModel,),
        },
        prefix2dataset_classes={
            'v_no_lists': (JsonNoListsDataset,),
            'v_nested_dicts': (JsonNestedDictsDataset,),
        },
        data_points=JsonNestedDictsDataPoints(),
    )


@pc.case(id='test_json_more_specific_types', tags=[])
def case_json_more_specific_types() -> CaseInfo:
    @dataclass
    class JsonMoreSpecificTypesDataPoints:
        #
        # JsonListOfNestedDictsModel
        #

        err_m_list_of_nested_dicts_none: None = b_none
        err_m_list_of_nested_dicts_int: int = b_int
        err_m_list_of_nested_dicts_float: float = b_float
        err_m_list_of_nested_dicts_str: str = b_str
        err_m_list_of_nested_dicts_bool: bool = b_bool
        err_m_list_of_nested_dicts_list: list[JS] = \
            field(default_factory=lambda: list(b_list))
        err_m_list_of_nested_dicts_dict: dict[str, JS] = \
            field(default_factory=lambda: dict(b_dict))
        err_m_list_of_nested_dicts_tuple: tuple[JS, ...] = b_tuple
        err_m_list_of_nested_dicts_set: set[JS] = \
            field(default_factory=lambda: set(b_set))

        err_m_list_of_nested_dicts_list_of_none: list[None] = \
            field(default_factory=lambda: [b_none])
        err_m_list_of_nested_dicts_dict_of_none: dict[str, None] = \
            field(default_factory=lambda: {'a': b_none})
        m_list_of_nested_dicts_list_of_dict_of_none: list[dict[str, None]] = \
            field(default_factory=lambda: [{'a': b_none}])
        m_list_of_nested_dicts_two_levels: list[dict[str, JS]] = \
            field(default_factory=lambda: [dict(b_dict)])
        m_list_of_nested_dicts_list_of_dict_of_dict_of_none: list[dict[str, dict[str, None]]] = \
            field(default_factory=lambda: [{'a': {'b': b_none}}])
        m_list_of_nested_dicts_three_levels: list[dict[str, dict[str, JS]]] = \
            field(default_factory=lambda: [{'a': dict(b_dict), 'b': dict(b_dict)}])
        m_list_of_nested_dicts_four_levels: list[dict[str, dict[str, JS | dict[str, JS]]]] = \
            field(default_factory=lambda: [{'a': dict(b_dict), 'b': {'x': dict(b_dict)}}])
        err_m_list_of_nested_dicts_with_list_of_none_level_two: list[list[None]] = \
            field(default_factory=lambda: [[b_none]])
        err_m_list_of_nested_dicts_with_list_level_two: list[list[JS]] = \
            field(default_factory=lambda: [list(b_list)])
        err_m_list_of_nested_dicts_with_list_of_none_level_three: \
            list[dict[str, dict[str, list[None]]]] = \
            field(default_factory=lambda: [{'a': {'b': [b_none]}}])
        err_m_list_of_nested_dicts_with_list_level_three: \
            list[dict[str, dict[str, JS] | list[JS]]] = \
            field(default_factory=lambda: [{'a': dict(b_dict), 'b': list(b_list)}])
        err_m_list_of_nested_dicts_with_list_level_four: \
            list[dict[str, dict[str, JS | list[JS]]]] = \
            field(default_factory=lambda: [{'a': dict(b_dict), 'b': {'x': list(b_list)}}])

        #
        # JsonDictOfNestedListsModel
        #

        err_m_dict_of_nested_lists_none: None = b_none
        err_m_dict_of_nested_lists_int: int = b_int
        err_m_dict_of_nested_lists_float: float = b_float
        err_m_dict_of_nested_lists_str: str = b_str
        err_m_dict_of_nested_lists_bool: bool = b_bool
        err_m_dict_of_nested_lists_list: list[JS] = field(default_factory=lambda: list(b_list))
        err_m_dict_of_nested_lists_dict: dict[str, JS] = field(default_factory=lambda: dict(b_dict))
        err_m_dict_of_nested_lists_tuple: tuple[JS, ...] = b_tuple
        err_m_dict_of_nested_lists_set: set[JS] = field(default_factory=lambda: set(b_set))

        err_m_dict_of_nested_lists_list_of_none: list[None] = \
            field(default_factory=lambda: [b_none])
        err_m_dict_of_nested_lists_dict_of_none: dict[str, None] = \
            field(default_factory=lambda: {'a': b_none})
        m_dict_of_nested_lists_dict_of_list_of_none: dict[str, list[None]] = \
            field(default_factory=lambda: {'a': [b_none]})
        m_dict_of_nested_lists_two_levels: dict[str, list[JS]] = \
            field(default_factory=lambda: {'a': list(b_list), 'b': list(b_list)})

        # Orig: err_m_dict_of_nested_lists_int_key_dict. Due to parsing to str
        m_dict_of_nested_lists_int_key_dict: dict[int, list[JS]] = \
            field(default_factory=lambda: {b_int: list(b_list)})

        # Orig: err_m_dict_of_nested_lists_float_key_dict. Due to parsing to str
        m_dict_of_nested_lists_float_key_dict: dict[float, list[JS]] = \
            field(default_factory=lambda: {b_float: list(b_list)})

        # Orig: err_m_dict_of_nested_lists_bool_key_dict. Due to parsing to str
        m_dict_of_nested_lists_bool_key_dict: dict[bool, list[JS]] = \
            field(default_factory=lambda: {b_bool: list(b_list)})

        err_m_dict_of_nested_lists_none_key_dict: dict[None, list[JS]] = \
            field(default_factory=lambda: {b_none: list(b_list)})
        m_dict_of_nested_lists_dict_of_list_of_list_of_none: dict[str, list[list[JS]]] = \
            field(default_factory=lambda: {'a': [[b_none]]})
        m_dict_of_nested_lists_three_levels: dict[str, list[JS | list[JS]]] = \
            field(default_factory=lambda: {'a': list(b_list), 'b': [list(b_list)]})
        m_dict_of_nested_lists_four_levels: dict[str, list[JS | list[JS | list[JS]]]] = \
            field(default_factory=lambda: {'a': list(b_list), 'b': [list(b_list), [list(b_list)]]})
        err_m_dict_of_nested_lists_with_dict_of_none_level_two: dict[str, dict[str, None]] = \
            field(default_factory=lambda: {'a': {'b': b_none}})
        err_m_dict_of_nested_lists_with_dict_level_two: dict[str, dict[str, JS]] = \
            field(default_factory=lambda: {'a': dict(b_dict)})
        err_m_dict_of_nested_lists_with_dict_of_none_level_three: \
            dict[str, list[dict[str, None]]] = \
            field(default_factory=lambda: {'a': [{'b': b_none}]})
        err_m_dict_of_nested_lists_with_dict_level_three: dict[str, list[JS | dict[str, JS]]] = \
            field(default_factory=lambda: {'a': list(b_list), 'b': [dict(b_dict)]})
        err_m_dict_of_nested_lists_with_dict_level_four: \
            dict[str, list[JS | list[JS | dict[str, JS]]]] = \
            field(default_factory=lambda: {'a': list(b_list), 'b': [list(b_list), [dict(b_dict)]]})

        #
        # JsonDictOfListsOfDictsModel
        #

        err_m_dict_of_lists_of_dicts_none: None = b_none
        err_m_dict_of_lists_of_dicts_float: float = b_float
        err_m_dict_of_lists_of_dicts_list_of_none: list[None] = \
            field(default_factory=lambda: [b_none])
        err_m_dict_of_lists_of_dicts_dict_of_none: dict[str, None] = \
            field(default_factory=lambda: {'a': b_none})
        err_m_dict_of_lists_of_dicts_one_level: dict[str, JS] = \
            field(default_factory=lambda: dict(b_dict))
        err_m_dict_of_lists_of_dicts_dict_of_list_of_none: dict[str, list[None]] = \
            field(default_factory=lambda: {'a': [b_none]})
        err_m_dict_of_lists_of_dicts_two_levels: dict[str, list[JS]] = \
            field(default_factory=lambda: {'a': list(b_list), 'b': list(b_list)})
        m_dict_of_lists_of_dicts_dict_of_list_of_dict_of_none: dict[str, list[dict[str, None]]] = \
            field(default_factory=lambda: {'a': [{'b': b_none}]})
        m_dict_of_lists_of_dicts_three_levels: dict[str, list[dict[str, JS]]] = \
            field(default_factory=lambda: {'a': [dict(b_dict)], 'b': [dict(b_dict)]})
        m_dict_of_lists_of_dicts_four_levels: dict[str, list[dict[str, JS | list[JS]]]] = \
            field(default_factory=lambda:
                  {'a': [dict(b_dict)], 'b': [{'a': b_str, 'b': list(b_list)}]})
        err_m_dict_of_lists_of_dicts_with_dict_of_none_level_two: dict[str, dict[str, None]] = \
            field(default_factory=lambda: {'a': {'b': b_none}})
        err_m_dict_of_lists_of_dicts_with_dict_level_two: \
            dict[str, list[dict[str, JS]] | dict[str, dict[str, JS]]] = \
            field(default_factory=lambda: {'a': [dict(b_dict)], 'b': {'x': dict(b_dict)}})
        err_m_dict_of_lists_of_dicts_with_scalar_level_two: dict[str, JS | list[dict[str, JS]]] = \
            field(default_factory=lambda: {'a': b_str, 'b': [dict(b_dict)]})
        err_m_dict_of_lists_of_dicts_with_list_of_none_level_three: dict[str, list[list[None]]] = \
            field(default_factory=lambda: {'a': [[b_none]]})
        err_m_dict_of_lists_of_dicts_with_list_level_three: \
            dict[str, list[dict[str, JS] | list[JS]]] = \
            field(default_factory=lambda: {'a': [dict(b_dict)], 'b': [list(b_list)]})

    return CaseInfo(
        name='test_json_more_specific_types',
        prefix2model_classes={
            'm_list_of_nested_dicts': (JsonListOfNestedDictsModel,),
            'm_dict_of_nested_lists': (JsonDictOfNestedListsModel,),
            'm_dict_of_lists_of_dicts': (JsonDictOfListsOfDictsModel,),
        },
        prefix2dataset_classes={
            'm_list_of_nested_dicts': (JsonListOfNestedDictsDataset,),
            'm_dict_of_nested_lists': (JsonDictOfNestedListsDataset,),
            'm_dict_of_lists_of_dicts': (JsonDictOfListsOfDictsDataset,),
        },
        data_points=JsonMoreSpecificTypesDataPoints(),
    )
