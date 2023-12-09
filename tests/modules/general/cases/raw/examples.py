from omnipy.modules.general.typedefs import FrozenDict

f_none = None
f_int = 123
f_str = 'abc'
ej_type = type(str)
f_complex = 2 + 3j
f_list = [f_none, f_int, f_str, f_complex]
f_dict = {'a': f_none, 'b': f_int, 'c': f_str, 'd': f_complex}
f_tuple = (f_none, f_int, f_str, f_complex)
ej_tuple_iterable_scalar = (f_int, f_str, {})
ej_tuple_wrong_scalar = (f_int, f_str, ej_type)
f_frozendict = FrozenDict({'a': f_none, 1: f_int, 1 + 2j: f_str, 'd': f_complex})
ej_frozendict_iterable_scalar = {'a': f_none, 1: f_int, 1 + 2j: f_str, 'd': (1, 2)}
ej_frozendict_iterable_scalar_empty = {'a': f_none, 1: f_int, 1 + 2j: f_str, 'd': ()}
ej_frozendict_wrong_scalar = {'a': f_none, 'b': f_int, 'c': f_str, 'd': ej_type}
f_set = {f_none, f_int, f_str, f_complex}

e_int_key_dict = {f_int: f_none}
e_complex_key_dict = {f_complex: f_int}
e_none_key_dict = {f_none: f_complex}
