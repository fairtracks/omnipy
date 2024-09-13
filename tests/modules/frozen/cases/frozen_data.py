from dataclasses import dataclass, field
import os
from textwrap import dedent
from typing import Type, TypeAlias

import pytest
import pytest_cases as pc

from modules.general.cases.raw.examples import (e_complex_key_dict,
                                                e_int_key_dict,
                                                e_none_key_dict,
                                                ej_frozendict_iter_scalar,
                                                ej_frozendict_iter_scalar_empty,
                                                ej_frozendict_wrong_scalar,
                                                ej_tuple_iterable_scalar,
                                                ej_tuple_wrong_scalar,
                                                ej_type,
                                                f_complex,
                                                f_dict,
                                                f_frozendict,
                                                f_int,
                                                f_list,
                                                f_none,
                                                f_set,
                                                f_str,
                                                f_tuple)
from modules.helpers.classes import CaseInfo
from omnipy.modules.frozen.datasets import (NestedFrozenDictsDataset,
                                            NestedFrozenDictsOrTuplesDataset,
                                            NestedFrozenTuplesDataset)
from omnipy.modules.frozen.models import (NestedFrozenDictsOrTuplesModel,
                                          NestedFrozenOnlyDictsModel,
                                          NestedFrozenOnlyTuplesModel)
from omnipy.modules.frozen.typedefs import FrozenDict

FSK: TypeAlias = int | str | complex  # for keys
FSV: TypeAlias = None | int | str | complex  # for values


@pc.case(id='test_frozen_tuples', tags=[])
def case_test_frozen_tuples() -> CaseInfo:
    @dataclass
    class FrozenTuplesDataPoints:
        #
        # NestedFrozenTuplesModel, NestedFrozenTuplesModel[FSV]
        #

        err_ft_none: None = f_none
        err_ft_int: int = f_int
        err_ft_str: str = f_str
        err_ft_complex: complex = f_complex
        err_ft_type: Type = ej_type
        ft_tuple: tuple[FSV, ...] = f_tuple  # Orig: err_l_tuple. Here obviously supported
        err_ft_tuple_iterable_scalar: tuple = ej_tuple_iterable_scalar
        ftnp_tuple_wrong_scalar: tuple = ej_tuple_wrong_scalar
        err_ftp_tuple_wrong_scalar: tuple = ej_tuple_wrong_scalar
        err_ft_frozendict: FrozenDict[FSK, FSV] = (
            field(default_factory=lambda: FrozenDict[FSK, FSV](f_frozendict)))
        ft_list: list[FSV] = field(default_factory=lambda: list(f_list))  # parsing to tuple
        err_ft_dict: dict[str, FSV] = field(default_factory=lambda: dict(f_dict))
        ft_set: set[FSV] = field(
            default_factory=lambda: set(f_set))  # Orig: err_l_tuple. Due to parsing to tuple

    return CaseInfo(
        name='test_frozen_tuples',
        prefix2model_classes={
            'ft_': (NestedFrozenOnlyTuplesModel, NestedFrozenOnlyTuplesModel[FSV]),
            'ftnp_': (NestedFrozenOnlyTuplesModel,),
            'ftp_': (NestedFrozenOnlyTuplesModel[FSV],),
        },
        prefix2dataset_classes={
            'ft_': (NestedFrozenTuplesDataset, NestedFrozenTuplesDataset[FSV]),
            'ftnp_': (NestedFrozenTuplesDataset,),
            'ftp_': (NestedFrozenTuplesDataset[FSV],),
        },
        data_points=FrozenTuplesDataPoints(),
    )


@pc.case(id='test_frozen_tuples_no_type_args', tags=[])
def case_test_frozen_tuples_no_type_args() -> CaseInfo:
    @dataclass
    class FrozenTuplesNoTypeArgsDataPoints:
        #
        # NestedFrozenTuplesModel
        #

        ft_tuple_wrong_scalar: tuple = ej_tuple_wrong_scalar

    return CaseInfo(
        name='test_frozen_tuples_no_type_args',
        prefix2model_classes={'ft': (NestedFrozenOnlyTuplesModel,)},
        prefix2dataset_classes={'ft': (NestedFrozenTuplesDataset,)},
        data_points=FrozenTuplesNoTypeArgsDataPoints(),
    )


@pc.case(id='test_frozen_dicts', tags=[])
def case_frozen_dicts() -> CaseInfo:
    @dataclass
    class FrozenDictsDataPoints:
        #
        # NestedFrozenDictsModel, NestedFrozenDictsModel[FSK, FSV]
        #

        err_fd_none: None = f_none
        err_fd_int: int = f_int
        err_fd_str: str = f_str
        err_fd_complex: complex = f_complex
        err_fd_type: Type = ej_type

        err_fd_tuple: tuple[FSV, ...] = f_tuple
        fd_frozendict: FrozenDict[FSK, FSV] = (
            field(default_factory=lambda: FrozenDict[FSK, FSV](f_frozendict)))
        err_fd_frozendict_iterable_scalar: FrozenDict[FSK, FSV] = (
            field(default_factory=lambda: FrozenDict[FSK, FSV](ej_frozendict_iter_scalar)))
        err_fd_frozendict_iterable_scalar_empty: FrozenDict[FSK, FSV] = (
            field(default_factory=lambda: FrozenDict[FSK, FSV](ej_frozendict_iter_scalar_empty)))
        fdnp_frozendict_wrong_scalar: FrozenDict[FSK, FSV] = (
            field(default_factory=lambda: FrozenDict[FSK, FSV](ej_frozendict_wrong_scalar)))
        err_fdp_frozendict_wrong_scalar: FrozenDict[FSK, FSV] = (
            field(default_factory=lambda: FrozenDict[FSK, FSV](ej_frozendict_wrong_scalar)))

        err_fd_list: list[FSV] = field(default_factory=lambda: list(f_list))
        fd_dict: dict[str, FSV] = field(default_factory=lambda: dict(f_dict))

        # Orig: err_d_int_key_dict. Due to parsing to str
        fd_int_key_dict: dict[int, FSV] = field(default_factory=lambda: dict(e_int_key_dict))

        fd_complex_key_dict: dict[float,
                                  FSV] = field(default_factory=lambda: dict(e_complex_key_dict))

        err_fd_none_key_dict: dict[None, FSV] = field(default_factory=lambda: dict(e_none_key_dict))
        err_fd_set: set[FSV] = field(default_factory=lambda: set(f_set))

    return CaseInfo(
        name='test_frozen_dicts',
        prefix2model_classes={
            'fd_': (NestedFrozenOnlyDictsModel, NestedFrozenOnlyDictsModel[FSK, FSV]),
            'fdnp_': (NestedFrozenOnlyDictsModel,),
            'fdp_': (NestedFrozenOnlyDictsModel[FSK, FSV],)
        },
        prefix2dataset_classes={
            'fd_': (NestedFrozenDictsDataset, NestedFrozenDictsDataset[FSK, FSV]),
            'fdnp_': (NestedFrozenDictsDataset,),
            'fdp_': (NestedFrozenDictsDataset[FSK, FSV],),
        },
        data_points=FrozenDictsDataPoints(),
    )


@pc.case(id='test_frozen_dicts_or_tuples', tags=[])
def case_frozen_dicts_or_tuples() -> CaseInfo:
    @dataclass
    class FrozenDictsOrTuplesDataPoints:
        #
        # NestedFrozenDictsOrTuplesModel, NestedFrozenDictsOrTuplesModel[FSK, FSV]
        #

        ftd_none: None = f_none
        ftd_int: int = f_int
        ftd_str: str = f_str
        ftd_complex: complex = f_complex
        ftdnp_type: Type = ej_type
        err_ftdp_type: Type = ej_type

        ftd_tuple: tuple[FSV, ...] = f_tuple
        ftd_frozendict: FrozenDict[FSK, FSV] = (
            field(default_factory=lambda: FrozenDict[FSK, FSV](f_frozendict)))
        ftd_list: list[FSV] = field(default_factory=lambda: list(f_list))
        ftd_dict: dict[str, FSV] = field(default_factory=lambda: dict(f_dict))

        # Orig: err_d_int_key_dict. Due to parsing to str
        ftd_int_key_dict: dict[int, FSV] = field(default_factory=lambda: dict(e_int_key_dict))

        ftd_complex_key_dict: dict[float,
                                   FSV] = field(default_factory=lambda: dict(e_complex_key_dict))

        err_ftd_none_key_dict: dict[None,
                                    FSV] = field(default_factory=lambda: dict(e_none_key_dict))
        ftd_set: set[FSV] = field(default_factory=lambda: set(f_set))

    return CaseInfo(
        name='test_frozen_dicts_or_tuples',
        prefix2model_classes={
            'ftd_': (NestedFrozenDictsOrTuplesModel, NestedFrozenDictsOrTuplesModel[FSK, FSV]),
            'ftdnp_': (NestedFrozenDictsOrTuplesModel,),
            'ftdp_': (NestedFrozenDictsOrTuplesModel[FSK, FSV],),
        },
        prefix2dataset_classes={
            'ftd_': (NestedFrozenDictsOrTuplesDataset, NestedFrozenDictsOrTuplesDataset[FSK, FSV]),
            'ftdnp_': (NestedFrozenDictsOrTuplesDataset,),
            'ftdp_': (NestedFrozenDictsOrTuplesDataset[FSK, FSV],),
        },
        data_points=FrozenDictsOrTuplesDataPoints(),
    )


@pc.case(id='test_nested_frozen_dicts_or_tuples', tags=[])
def case_nested_frozen_dicts_or_tuples() -> CaseInfo:
    _two_level_list: list[FSV | list[FSV] | dict[str, FSV]] = \
        f_list + [list(f_list)] + [dict(f_dict)]
    _two_level_dict: dict[str, str | list[FSV] | dict[str, FSV]] = \
        {'a': f_str, 'b': list(f_list), 'c': dict(f_dict)}

    @dataclass
    class NestedFrozenDictsOrTuplesDataPoints:
        #
        # NestedFrozenDictsOrTuplesModel, NestedFrozenDictsOrTuplesModel[FSK, FSV]
        #

        # Origs: l_two_level_list, j_two_level_list
        nft_two_level_list: list[FSV | list[FSV] | dict[str, FSV]] = \
            field(default_factory=lambda: _two_level_list)

        err_nft_two_level_none_key_list: list[FSV | dict[None, bool]] = \
            field(default_factory=lambda: list(f_list) + [dict(e_none_key_dict)])

        # Origs: err_l_two_level_int_key_list, err_j_two_level_int_key_list. Due to parsing to str
        nft_two_level_int_key_list: list[FSV | dict[int, None]] = \
            field(default_factory=lambda: list(f_list) + [dict(e_int_key_dict)])

        # Origs: err_l_two_level_set_list, err_j_two_level_set_list. Due to parsing to list
        nft_two_level_set_list: list[FSV | dict[str, FSV] | set[FSV]] = \
            field(default_factory=lambda: list(f_list) + [dict(f_dict)] + [set(f_set)])

        # Origs: l_three_level_list, j_three_level_list
        nft_three_level_list: list[FSV | list[FSV] | dict[str, FSV]
                                   | list[FSV | list[FSV] | dict[str, FSV]]
                                   | dict[str, str | list[FSV] | dict[str, FSV]]] = \
            field(default_factory=lambda: list(f_list + [list(f_list), dict(f_dict),
                                                         list(_two_level_list),
                                                         dict(_two_level_dict)]))

        #
        # NestedFrozenDictsOrTuplesModel, NestedFrozenDictsOrTuplesModel[FSK, FSV]
        #

        # Origs: d_two_level_dict, j_two_level_dict
        nfd_two_level_dict: dict[str, str | list[FSV] | dict[str, FSV]] = \
            field(default_factory=lambda: _two_level_dict)

        err_nfd_two_level_none_key_dicts: dict[str, FSV | dict[None, bool]] = \
            field(default_factory=lambda: {'f': dict(e_none_key_dict)})

        # Origs: err_d_two_level_bool_key_dict, err_j_two_level_bool_key_dict. Due to parsing to str
        nfd_two_level_complex_key_dict: dict[str, list[FSV] | dict[bool, str]] = \
            field(default_factory=lambda: {'f': list(f_list), 'g': dict(e_complex_key_dict)})

        # Origs: err_d_two_level_set_dict, err_j_two_level_set_dict. Due to parsing to list
        nfd_two_level_set_dict: dict[str, list[FSV] | set[FSV]] = \
            field(default_factory=lambda: {'f': list(f_list), 'g': set(f_set)})

        # Origs: d_three_level_dict, j_three_level_dict
        nfd_three_level_dict: dict[str, int | list[FSV] | dict[str, FSV]
                                   | list[FSV | list[FSV] | dict[str, FSV]]
                                   | dict[str, str | list[FSV] | dict[str, FSV]]] = \
            field(default_factory=lambda: {'a': f_int, 'b': list(f_list), 'c': dict(f_dict),
                                           'd': list(_two_level_list), 'e': dict(_two_level_dict)})

    return CaseInfo(
        name='test_nested_frozen_dicts_or_tuples',
        prefix2model_classes={
            'nft_': (NestedFrozenDictsOrTuplesModel, NestedFrozenDictsOrTuplesModel[FSK, FSV]),
            'nfd_': (NestedFrozenDictsOrTuplesModel, NestedFrozenDictsOrTuplesModel[FSK, FSV]),
        },
        prefix2dataset_classes={
            'nft_': (NestedFrozenDictsOrTuplesDataset, NestedFrozenDictsOrTuplesDataset[FSK, FSV]),
            'nfd_': (NestedFrozenDictsOrTuplesDataset, NestedFrozenDictsOrTuplesDataset[FSK, FSV]),
        },
        data_points=NestedFrozenDictsOrTuplesDataPoints(),
    )


@pc.case(id='test_nested_frozen_tuples', tags=[])
def case_nested_frozen_tuples() -> CaseInfo:
    @dataclass
    class NestedFrozenTuplesDataPoints:

        #
        # NestedFrozenTuplesModel, NestedFrozenTuplesModel[FSV]
        #

        nft_list_of_none: list[None] = \
            field(default_factory=lambda: [f_none])
        err_nft_dict_of_none: dict[str, None] = \
            field(default_factory=lambda: {'a': f_none})
        nftnp_tuple_wrong_scalar: tuple = ej_tuple_wrong_scalar
        err_nftp_tuple_wrong_scalar: tuple = ej_tuple_wrong_scalar
        nft_two_levels: list[FSV | list[FSV]] = \
            field(default_factory=lambda: list(f_list + [list(f_list)]))
        nft_three_levels: list[FSV | list[FSV | list[FSV]]] = \
            field(default_factory=lambda: list(f_list + [list(f_list), [list(f_list)]]))
        err_nft_with_dict_of_none_level_two: list[dict[str, None]] = \
            field(default_factory=lambda: [{'a': f_none}])
        err_nft_with_dict_level_two: list[FSV | dict[str, FSV]] = \
            field(default_factory=lambda: list(f_list + [dict(f_dict)]))
        err_nft_with_dict_level_three: list[FSV | list[FSV | dict[str, FSV]]] = \
            field(default_factory=lambda: list(f_list + [list(f_list + [dict(f_dict)])]))
        nftnp_with_wrong_scalar_level_three: list[FSV | list[FSV | dict[str, FSV]]] = \
            field(default_factory=lambda: list(f_list + [list(f_list + [ej_tuple_wrong_scalar])]))
        err_nftp_with_wrong_scalar_level_three: list[FSV | list[FSV | dict[str, FSV]]] = \
            field(default_factory=lambda: list(f_list + [list(f_list + [ej_tuple_wrong_scalar])]))

    return CaseInfo(
        name='test_nested_frozen_tuples',
        prefix2model_classes={
            'nft_': (NestedFrozenOnlyTuplesModel, NestedFrozenOnlyTuplesModel[FSV]),
            'nftnp_': (NestedFrozenOnlyTuplesModel,),
            'nftp_': (NestedFrozenOnlyTuplesModel[FSV],),
        },
        prefix2dataset_classes={
            'nft_': (NestedFrozenTuplesDataset, NestedFrozenTuplesDataset[FSV]),
            'nftnp_': (NestedFrozenTuplesDataset,),
            'nftp_': (NestedFrozenTuplesDataset[FSV],),
        },
        data_points=NestedFrozenTuplesDataPoints(),
    )


@pc.case(id='test_nested_frozen_dicts', tags=[])
def case_nested_frozen_dicts() -> CaseInfo:
    @dataclass
    class NestedFrozenDictsDataPoints:

        #
        # NestedFrozenDictsModel, NestedFrozenDictsModel[FSK, FSV]
        #

        err_nfd_list_of_none: list[None] = \
            field(default_factory=lambda: [f_none])
        nfd_dict_of_none: dict[str, None] = \
            field(default_factory=lambda: {'a': f_none})
        nfd_two_levels: dict[str, dict[str, FSV]] = \
            field(default_factory=lambda: {'a': dict(f_dict), 'b': dict(f_dict)})
        nfd_three_levels: dict[str, dict[str, FSV | dict[str, FSV]]] = \
            field(default_factory=lambda: {'a': dict(f_dict), 'b': {'x': dict(f_dict)}})
        err_nfd_with_list_of_none_level_two: dict[str, list[None]] = \
            field(default_factory=lambda: {'a': [f_none]})
        err_nfd_with_list_level_two: dict[str, dict[str, FSV] | list[FSV]] = \
            field(default_factory=lambda: {'a': dict(f_dict), 'b': list(f_list)})
        err_nfd_with_list_level_three: dict[str, dict[str, FSV | list[FSV]]] = \
            field(default_factory=lambda: {'a': dict(f_dict), 'b': {'x': list(f_list)}})
        nfdnp_with_wrong_scalar_level_three: dict[str, dict[str, FSV | list[FSV]]] = \
            field(default_factory=lambda:
            {'a': dict(f_dict), 'b': {'x': ej_frozendict_wrong_scalar}})
        err_nfdp_with_wrong_scalar_level_three: dict[str, dict[str, FSV | list[FSV]]] = \
            field(default_factory=lambda:
            {'a': dict(f_dict), 'b': {'x': ej_frozendict_wrong_scalar}})

    return CaseInfo(
        name='test_nested_frozen_dicts',
        prefix2model_classes={
            'nfd_': (NestedFrozenOnlyDictsModel, NestedFrozenOnlyDictsModel[FSK, FSV]),
            'nfdnp_': (NestedFrozenOnlyDictsModel,),
            'nfdp_': (NestedFrozenOnlyDictsModel[FSK, FSV],),
        },
        prefix2dataset_classes={
            'nfd_': (NestedFrozenDictsDataset, NestedFrozenDictsDataset[FSK, FSV]),
            'nfdnp_': (NestedFrozenDictsDataset,),
            'nfdp_': (NestedFrozenDictsDataset[FSK, FSV],),
        },
        data_points=NestedFrozenDictsDataPoints(),
    )
