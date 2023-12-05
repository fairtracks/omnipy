from __future__ import annotations

from typing import Dict, Generic, List, Optional, Type, TypeAlias, TypeVar, Union

from omnipy.data.model import Model

from .typedefs import JsonScalar

#
# Private models
#

# Basic building block models

_JsonBaseT = TypeVar(
    '_JsonBaseT',
    bound=Optional[Union['_JsonScalarM',
                         '_JsonBaseListM',
                         '_JsonBaseDictM',
                         '_JsonListM',
                         '_JsonDictM']])


class _JsonScalarM(Model[JsonScalar]):
    ...


class _JsonBaseListM(Model[List[_JsonBaseT]], Generic[_JsonBaseT]):
    ...


class _JsonBaseDictM(Model[Dict[str, _JsonBaseT]], Generic[_JsonBaseT]):
    ...


# Optional is workaround for test_union_nested_model_classes_inner_forwardref_generic_list_of_none
class _JsonListM(_JsonBaseListM[Optional['_JsonAnyUnion']]):
    ...


# Optional is workaround for test_union_nested_model_classes_inner_forwardref_generic_list_of_none
class _JsonDictM(_JsonBaseDictM[Optional['_JsonAnyUnion']]):
    ...


# Optional is workaround for test_union_nested_model_classes_inner_forwardref_generic_list_of_none
class _JsonNoDictsM(_JsonBaseListM[Optional['_JsonNoDictsUnion']]):
    ...


# Optional is workaround for test_union_nested_model_classes_inner_forwardref_generic_list_of_none
class _JsonNoListsM(_JsonBaseDictM[Optional['_JsonNoListsUnion']]):
    ...


# class _JsonAnyUnion(Model[Union[_JsonScalarM, _JsonListM, _JsonDictM]]):
#     ...

# TypeAliases

_JsonAnyUnion: TypeAlias = Union[_JsonScalarM, _JsonListM, _JsonDictM]
_JsonNoDictsUnion: TypeAlias = Union[_JsonScalarM, _JsonNoDictsM]
_JsonNoListsUnion: TypeAlias = Union[_JsonScalarM, _JsonNoListsM]

# Optional is workaround for test_union_nested_model_classes_inner_forwardref_generic_list_of_none
_JsonListOfScalarsM: TypeAlias = _JsonBaseListM[Optional[_JsonScalarM]]

# Optional is workaround for test_union_nested_model_classes_inner_forwardref_generic_list_of_none
_JsonDictOfScalarsM: TypeAlias = _JsonBaseDictM[Optional[_JsonScalarM]]

# Basic models needs to update their forward_refs with type aliases declared above

_JsonListM.update_forward_refs(_JsonAnyUnion=_JsonAnyUnion)
_JsonDictM.update_forward_refs()
_JsonNoDictsM.update_forward_refs()
_JsonNoListsM.update_forward_refs()

#
# Exportable models
#

# General


class JsonModel(Model[_JsonAnyUnion]):
    """
    JsonModel is a general JSON model supporting any JSON content, any levels deep.

    Examples:
        >>> my_int_json = JsonModel(123)
        >>> my_int_json.to_data()
        123
        >>> my_int_json.to_json()
        '123'
        >>> my_json = JsonModel([True, {'a': None, 'b': [1, 12.5, 'abc']}])
        >>> my_json.to_data()
        [True, {'a': None, 'b': [1, 12.5, 'abc']}]
        >>> my_json.to_json()
        '[true, {"a": null, "b": [1, 12.5, "abc"]}]'
        >>> print(my_json.to_json(pretty=True))
        [
          true,
          {
            "a": null,
            "b": [
              1,
              12.5,
              "abc"
            ]
          }
        ]
        >>> try:
        ...     my_json = JsonModel([{'a': [1, 2, 1+2j]}])  # nested complex number
        ... except Exception as e:
        ...     print(str(e).splitlines()[0])
        34 validation errors for JsonModel
    """


# Scalars


class JsonScalarModel(Model[_JsonScalarM]):
    """
    JsonScalarModel is a limited JSON model supporting only scalar JSON content, e.g. the basic
    types: `None`, `int`, `float`, `str`, and `bool`. Lists and dicts (or "objects") are not
    supported.

    Examples:
        >>> my_none = JsonScalarModel(None)
        >>> my_none.to_data(), my_none.to_json()
        (None, 'null')
        >>> my_int = JsonScalarModel(123)
        >>> my_int.to_data(), my_int.to_json()
        (123, '123')
        >>> my_float = JsonScalarModel(12.3)
        >>> my_float.to_data(), my_float.to_json()
        (12.3, '12.3')
        >>> my_str = JsonScalarModel('abc')
        >>> my_str.to_data(), my_str.to_json()
        (abc, '"abc"')
        >>> my_bool = JsonScalarModel(False)
        >>> my_bool.to_data(), my_bool.to_json()
        (False, '"false"')
        >>> try:
        ...     my_json = JsonScalarModel([123])
        ... except Exception as e:
        ...     print(str(e).splitlines()[0])
        6 validation errors for JsonScalarModel
    """


# List at the top level


class JsonListModel(Model[_JsonListM]):
    """
    JsonListModel is a limited JSON model supporting only JSON content that has a list (or "array"
    in JSON nomenclature) at the root. The contents of the top-level list can be any JSON content,
    though, any levels deep.

    Examples:
        >>> my_json = JsonListModel([True, {'a': None, 'b': [1, 12.5, 'abc']}])
        >>> my_json.to_data()
        [True, {'a': None, 'b': [1, 12.5, 'abc']}]
        >>> my_json.to_json()
        '[true, {"a": null, "b": [1, 12.5, "abc"]}]'
        >>> print(my_json.to_json(pretty=True))
        [
          true,
          {
            "a": null,
            "b": [
              1,
              12.5,
              "abc"
            ]
          }
        ]
        >>> try:
        ...     my_json = JsonListModel({'a': None, 'b': [1, 12.5, {'abc': 123}]})
        ... except Exception as e:
        ...     print(str(e).splitlines()[0])
        3 validation errors for JsonListModel
    """


class JsonListOfScalarsModel(Model[_JsonListOfScalarsM]):
    ...


class JsonListOfListsModel(Model[_JsonBaseListM[_JsonListM]]):
    ...


class JsonListOfListsOfScalarsModel(Model[_JsonBaseListM[_JsonListOfScalarsM]]):
    ...


class JsonListOfDictsModel(Model[_JsonBaseListM[_JsonDictM]]):
    ...


class JsonListOfDictsOfScalarsModel(Model[_JsonBaseListM[_JsonDictOfScalarsM]]):
    ...


# Dict at the top level


class JsonDictModel(Model[_JsonDictM]):
    """
    JsonDictModel is a limited JSON model supporting only JSON content that has a dict (or "object"
    in JSON nomenclature) at the root. The values of the top-level dict can be any JSON content,
    though, any levels deep.

    Examples:
        >>> my_json = JsonDictModel({'a': None, 'b': [1, 12.5, {'abc': 123}]})
        >>> my_json.to_data()
        {'a': None, 'b': [1, 12.5, {'abc': 123}]}
        >>> my_json.to_json()
        '{"a": null, "b": [1, 12.5, {"abc": 123}]}'
        >>> print(my_json.to_json(pretty=True))
        {
          "a": null,
          "b": [
            1,
            12.5,
            {
              "abc": 123
            }
          ]
        }
        >>> try:
        ...     my_json = JsonDictModel([True, {'a': None, 'b': [1, 12.5, 'abc']}])
        ... except Exception as e:
        ...     print(str(e).splitlines()[0])
        3 validation errors for JsonDictModel
    """


class JsonDictOfScalarsModel(Model[_JsonDictOfScalarsM]):
    ...


class JsonDictOfListsModel(Model[_JsonBaseDictM[_JsonListM]]):
    ...


class JsonDictOfListsOfScalarsModel(Model[_JsonBaseDictM[_JsonListOfScalarsM]]):
    ...


class JsonDictOfDictsModel(Model[_JsonBaseDictM[_JsonDictM]]):
    ...


class JsonDictOfDictsOfScalarsModel(Model[_JsonBaseDictM[_JsonDictOfScalarsM]]):
    ...


# Nested models


class JsonNoDictsModel(Model[_JsonNoDictsUnion]):
    ...


class JsonNestedListsModel(Model[_JsonNoDictsM]):
    ...


class JsonNoListsModel(Model[_JsonNoListsUnion]):
    ...


class JsonNestedDictsModel(Model[_JsonNoListsM]):
    ...


# More specific models


class JsonListOfNestedDictsModel(Model[_JsonBaseListM[_JsonNoListsM]]):
    ...


class JsonDictOfNestedListsModel(Model[_JsonBaseDictM[_JsonNoDictsM]]):
    ...


class JsonDictOfListsOfDictsModel(Model[_JsonBaseDictM[_JsonBaseListM[_JsonDictM]]]):
    ...


# Custom models

JsonCustomScalarModel: TypeAlias = Optional[_JsonScalarM]


class JsonCustomListModel(Model[_JsonBaseListM[_JsonBaseT]], Generic[_JsonBaseT]):
    ...


class JsonCustomDictModel(Model[_JsonBaseDictM[_JsonBaseT]], Generic[_JsonBaseT]):
    ...


# Add note of dict keys to models containing dicts

_NOTE_ON_DICT_KEYS = '''
    Note:
        JSON dicts (or "objects") only supports strings as keys. By default, however, omnipy
        JSON models parse the basic types `float`, `int`, and `bool` as strings if used as keys
        in JSON dicts/objects.

        Example:

            >>> my_dict = JsonModel({'a': None, 0.5: 12.3, 1: 123, False: True})
            >>> my_dict.to_data()
            {'a': None, '0.5': 12.3, '1': 123, 'False': True}
            >>> my_dict.to_json()
            '{"a": null, "0.5": 12.3, "1": 123, "False": true}'
    '''

_dict_related_json_model_classes: list[Type[Model]] = [
    JsonModel,
    JsonDictModel,
    JsonDictOfScalarsModel,
    JsonDictOfListsModel,
    JsonDictOfListsOfScalarsModel,
    JsonDictOfDictsModel,
    JsonDictOfDictsOfScalarsModel,
    JsonNoListsModel,
    JsonNestedListsModel,
    JsonListOfNestedDictsModel,
    JsonDictOfNestedListsModel,
    JsonDictOfListsOfDictsModel,
    JsonCustomDictModel,
]

for _dict_related_json_model_cls in _dict_related_json_model_classes:
    if _dict_related_json_model_cls.__doc__:
        _dict_related_json_model_cls.__doc__ += _NOTE_ON_DICT_KEYS
