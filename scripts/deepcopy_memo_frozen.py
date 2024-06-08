from typing import TypeAlias

from omnipy.modules.general.models import Model, NestedFrozenDictsOrTuplesModel
from tests.modules.general.cases.raw.examples import (e_complex_key_dict,
                                                      e_int_key_dict,
                                                      e_none_key_dict,
                                                      ej_frozendict_iterable_scalar,
                                                      ej_frozendict_iterable_scalar_empty,
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

FSK: TypeAlias = int | str | complex  # for keys
FSV: TypeAlias = None | int | str | complex  # for values


def run_nested_frozen_dicts_or_tuples_model() -> None:
    _two_level_list: list[FSV | list[FSV] | dict[str, FSV]] = \
            f_list + [list(f_list)] + [dict(f_dict)]
    _two_level_dict: dict[str, str | list[FSV] | dict[str, FSV]] = \
            {'a': f_str, 'b': list(f_list), 'c': dict(f_dict)}

    number_model = Model[int](123)

    print(number_model.snapshot_holder._deepcopy_memo)

    number_model.snapshot_holder._deepcopy_memo.clear()

    print(number_model.snapshot_holder._deepcopy_memo)

    nested_frozen_dicts_or_tuples = (
        list(f_list + [list(f_list), dict(f_dict), list(_two_level_list), dict(_two_level_dict)]))
    nested_frozen_dicts_or_tuples_model = NestedFrozenDictsOrTuplesModel(
        nested_frozen_dicts_or_tuples)

    print(len(number_model.snapshot_holder._deepcopy_memo))
    k = 0
    v = 0
    for k, v in number_model.snapshot_holder._deepcopy_memo.items():
        print(f'{k}: {v}')
    del k
    del v

    del nested_frozen_dicts_or_tuples_model
    number_model.snapshot_holder.delete_scheduled_deepcopy_content_ids()
    print(number_model.snapshot_holder._deepcopy_memo)

    assert len(number_model.snapshot_holder._deepcopy_memo) == 0


run_nested_frozen_dicts_or_tuples_model()
