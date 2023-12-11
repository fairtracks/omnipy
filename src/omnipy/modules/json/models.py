from typing import Generic, Type, TypeAlias, TypeVar

from omnipy.data.model import Model

from .typedefs import JsonScalar

#
# Private models
#

# Basic building block models

_JsonBaseT = TypeVar(
    '_JsonBaseT', bound='JsonScalarM | JsonListM | JsonDictM | JsonAnyListM | JsonAnyDictM')


class JsonScalarM(Model[JsonScalar]):
    ...


class JsonListM(Model[list[_JsonBaseT]], Generic[_JsonBaseT]):
    ...


class JsonDictM(Model[dict[str, _JsonBaseT]], Generic[_JsonBaseT]):
    ...


# Note: This intermediate level of JSON models is needed for two reasons. 1) as targets for
#       .updateForwardRefs(), as this does not seem to work properly directly on a generic model
#       (e.g. `JsonListM['_JsonAnyUnion'].updateForwardRefs()`), at least in pydantic v1.
#       But even if this is fixed in pydantic v2, or more probably in python 3.13 with PEP649, the
#       intermediate level is still needed due to the other reason: 2) For consistency in the
#       hierarchy of JSON models, as tested in e.g. `test_json_model_consistency_basic()`. The
#       intermediate level of models seems a good solution to make sure the level of the model
#       hierarchy stays the same for e.g. `JsonModel` and `JsonDictModel`.


class JsonAnyListM(JsonListM['_JsonAnyUnion']):
    ...


class JsonAnyDictM(JsonDictM['_JsonAnyUnion']):
    ...


class JsonOnlyListsM(JsonListM['_JsonOnlyListsUnion']):
    ...


class JsonOnlyDictsM(JsonDictM['_JsonOnlyDictsUnion']):
    ...


# TypeAliases
# TODO: Consider whether these TypeAliases are needed in pydantic v2. In v1 they are needed to for
#       the hack for propagating None to work. Removing this level will simplify JSON models.
#       If updated, also update frozen models

_JsonAnyUnion: TypeAlias = JsonScalarM | JsonAnyListM | JsonAnyDictM
_JsonOnlyListsUnion: TypeAlias = JsonScalarM | JsonOnlyListsM
_JsonOnlyDictsUnion: TypeAlias = JsonScalarM | JsonOnlyDictsM

_JsonListOfScalarsM: TypeAlias = JsonListM[JsonScalarM]

_JsonDictOfScalarsM: TypeAlias = JsonDictM[JsonScalarM]

# Basic models needs to update their forward_refs with type aliases declared above

JsonAnyListM.update_forward_refs()
JsonAnyDictM.update_forward_refs()
JsonOnlyListsM.update_forward_refs()
JsonOnlyDictsM.update_forward_refs()

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

JsonScalarModel: TypeAlias = JsonScalarM
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


class JsonListModel(Model[JsonAnyListM]):
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


class JsonListOfListsModel(Model[JsonListM[JsonAnyListM]]):
    ...


class JsonListOfListsOfScalarsModel(Model[JsonListM[_JsonListOfScalarsM]]):
    ...


class JsonListOfDictsModel(Model[JsonListM[JsonAnyDictM]]):
    ...


class JsonListOfDictsOfScalarsModel(Model[JsonListM[_JsonDictOfScalarsM]]):
    ...


# Dict at the top level


class JsonDictModel(Model[JsonAnyDictM]):
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


class JsonDictOfListsModel(Model[JsonDictM[JsonAnyListM]]):
    ...


class JsonDictOfListsOfScalarsModel(Model[JsonDictM[_JsonListOfScalarsM]]):
    ...


class JsonDictOfDictsModel(Model[JsonDictM[JsonAnyDictM]]):
    ...


class JsonDictOfDictsOfScalarsModel(Model[JsonDictM[_JsonDictOfScalarsM]]):
    ...


# Nested models


class JsonNoDictsModel(Model[_JsonOnlyListsUnion]):
    ...


class JsonNestedListsModel(Model[JsonOnlyListsM]):
    ...


class JsonNoListsModel(Model[_JsonOnlyDictsUnion]):
    ...


class JsonNestedDictsModel(Model[JsonOnlyDictsM]):
    ...


# More specific models


class JsonListOfNestedDictsModel(Model[JsonListM[JsonOnlyDictsM]]):
    ...


class JsonDictOfNestedListsModel(Model[JsonDictM[JsonOnlyListsM]]):
    ...


class JsonDictOfListsOfDictsModel(Model[JsonDictM[JsonListM[JsonAnyDictM]]]):
    ...


# Custom models


class JsonCustomModel(Model[JsonListM[_JsonBaseT]], Generic[_JsonBaseT]):
    ...


class JsonCustomListModel(Model[JsonListM[_JsonBaseT]], Generic[_JsonBaseT]):
    ...


class JsonCustomDictModel(Model[JsonDictM[_JsonBaseT]], Generic[_JsonBaseT]):
    ...


# Add note of dict keys to models containing dicts

_NOTE_ON_DICT_KEYS = """
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
    """

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
