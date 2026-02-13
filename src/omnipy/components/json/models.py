import typing
from typing import Any, Generic, overload, Type, TypeAlias

from typing_extensions import TypeVar

from omnipy.data.model import Model
from omnipy.data.typechecks import is_model_instance
import omnipy.util._pydantic as pyd
from omnipy.util.helpers import ensure_plain_type

from .helpers import parse_str_as_json
from .typedefs import JsonScalar

#
# Private models
#

# Basic building block models

_JsonBaseT = TypeVar(
    '_JsonBaseT',
    bound='JsonScalar | _JsonListM | _JsonDictM | _JsonAnyListM | _JsonAnyDictM',
    default='JsonScalar')

if typing.TYPE_CHECKING:
    from omnipy.data._mimic_models import (Model_bool,
                                           Model_dict,
                                           Model_float,
                                           Model_int,
                                           Model_list,
                                           Model_str)

    class _JsonListM(Model_list[_JsonBaseT], Generic[_JsonBaseT]):
        ...

    class _JsonDictM(
            Model_dict[str, _JsonBaseT],
            Generic[_JsonBaseT],
    ):
        ...
else:

    class _JsonListM(Model[list[_JsonBaseT]], Generic[_JsonBaseT]):
        ...

    class _JsonDictM(
            Model[dict[str, _JsonBaseT]],
            Generic[_JsonBaseT],
    ):
        ...


# Note: This intermediate level of JSON models is needed for two reasons:
#     1) as targets for .update_forward_refs(), as this does not seem to
#     work properly directly on a generic model (e.g.
#     `_JsonListM['_JsonAnyUnion'].update_forward_refs()`), at least in
#     pydantic v1. But even if this is fixed in pydantic v2, or more
#     probably in python 3.13 with PEP649, the intermediate level is still
#     needed due to the other reason:
#     2) For consistency in the hierarchy of JSON models, as tested in e.g.
#     `test_json_model_consistency_basic()`. The intermediate level of
#     models seems a good solution to make sure the level of the model
#     hierarchy stays the same for e.g. `JsonModel` and `JsonDictModel`.

if typing.TYPE_CHECKING:

    class _JsonAnyListM(Model_list['_JsonAnyUnion']):
        ...

    class _JsonAnyDictM(Model_dict[str, '_JsonAnyUnion']):
        ...

    class _JsonOnlyListsM(Model_list['_JsonOnlyListsUnion']):
        ...

    class _JsonOnlyDictsM(Model_dict[str, '_JsonOnlyDictsUnion']):
        ...
else:

    class _JsonAnyListM(_JsonListM['_JsonAnyUnion']):
        ...

    class _JsonAnyDictM(_JsonDictM['_JsonAnyUnion']):
        ...

    class _JsonOnlyListsM(_JsonListM['_JsonOnlyListsUnion']):
        ...

    class _JsonOnlyDictsM(_JsonDictM['_JsonOnlyDictsUnion']):
        ...


# TypeAliases
# TODO: Consider whether these TypeAliases are needed in pydantic v2. In v1 they are needed to for
#       the hack for propagating None to work. Removing this level will simplify JSON models.
#       If updated, also update frozen models

if typing.TYPE_CHECKING:
    _JsonAnyUnion: TypeAlias = (
        JsonScalar
        | _JsonAnyListM | list['_JsonAnyUnion']
        | _JsonAnyDictM | dict[str, '_JsonAnyUnion'])
    _JsonOnlyListsUnion: TypeAlias = JsonScalar | _JsonOnlyListsM | list['_JsonOnlyListsUnion']
    _JsonOnlyDictsUnion: TypeAlias = JsonScalar | _JsonOnlyDictsM | dict[str, '_JsonOnlyDictsUnion']
else:
    _JsonAnyUnion: TypeAlias = JsonScalar | _JsonAnyListM | _JsonAnyDictM
    _JsonOnlyListsUnion: TypeAlias = JsonScalar | _JsonOnlyListsM
    _JsonOnlyDictsUnion: TypeAlias = JsonScalar | _JsonOnlyDictsM

_JsonListOfScalars: TypeAlias = _JsonListM[JsonScalar]

_JsonDictOfScalars: TypeAlias = _JsonDictM[JsonScalar]

# Basic models needs to update their forward_refs with type aliases
# declared above

_JsonAnyListM.update_forward_refs()
_JsonAnyDictM.update_forward_refs()
_JsonOnlyListsM.update_forward_refs()
_JsonOnlyDictsM.update_forward_refs()

#
# Exportable models
#

# General

# Note: Since parsing JSON strings is potentially ambiguous (a string can
#       be a valid JSON string, but also a string representing JSON
#       entities), strings starting with a quote are not parsed as JSON
#       entities.

if typing.TYPE_CHECKING:

    class JsonModel(Model[Model[None] | Model_int | Model_float | Model_str | Model_bool
                          | Model_list['_JsonAnyUnion'] | Model_dict[str, '_JsonAnyUnion']]):
        ...

else:

    class JsonModel(Model[_JsonAnyUnion]):
        """
        JsonModel is a general JSON model supporting any JSON content, any
        levels deep.

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
        @classmethod
        def _parse_data(cls, data: _JsonAnyUnion) -> _JsonAnyUnion:
            if isinstance(data, str):
                # Refusing to parse strings starting with a quote
                if len(data) > 0 and data[0] in '[{0123456789-tfn':  # not [{"0123456789-tfn'
                    # Potentially a string representing JSON entities.
                    parsed_json = parse_str_as_json(data)
                    if parsed_json is not pyd.Undefined:
                        if isinstance(parsed_json, str):
                            return parsed_json
                        return cls(parsed_json).content

            return data


# Scalars

if typing.TYPE_CHECKING:
    _JsonScalarMimicModels: TypeAlias = Model[
        None] | Model_int | Model_float | Model_str | Model_bool

    T = TypeVar('T', bound=_JsonScalarMimicModels)

    class _JsonScalarModel(Model[T], Generic[T]):
        @overload
        def __new__(cls, value: None) -> Model[None]:  # type: ignore[misc]
            ...

        @overload
        def __new__(cls, value: bool) -> Model_bool:  # type: ignore[misc]
            ...

        @overload
        def __new__(cls, value: int) -> Model_int:  # type: ignore[misc]
            ...

        @overload
        def __new__(cls, value: float) -> Model_float:  # type: ignore[misc]
            ...

        @overload
        def __new__(cls, value: str) -> Model_str:  # type: ignore[misc]
            ...

        def __new__(cls, value: JsonScalar) -> _JsonScalarMimicModels:  # type: ignore[misc]
            ...

    JsonScalarModel: TypeAlias = _JsonScalarModel[Model[None] | Model_int | Model_float | Model_str
                                                  | Model_bool]

else:

    class JsonScalarModel(Model[JsonScalar]):
        """
        JsonScalarModel is a limited JSON model supporting only scalar JSON
        content, e.g. the basic types: `None`, `int`, `float`, `str`, and
        `bool`. Lists and dicts (or "objects") are not supported.

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

if typing.TYPE_CHECKING:

    class JsonListModel(Model_list['_JsonAnyUnion']):
        ...

else:

    class JsonListModel(Model[_JsonAnyListM]):
        """
        JsonListModel is a limited JSON model supporting only JSON content
        that has a list (or "array" in JSON nomenclature) at the root. The
        content of the top-level list can be any JSON content, though, any
        levels deep.

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


if typing.TYPE_CHECKING:

    class JsonListOfScalarsModel(Model_list[JsonScalar]):
        ...

    class JsonListOfListsModel(Model_list[
            Model_list['_JsonAnyUnion'] | list['_JsonAnyUnion'],
    ]):
        ...

    class JsonListOfListsOfScalarsModel(Model[Model_list[
            Model_list[JsonScalar] | list[JsonScalar],
    ]]):
        ...

    class JsonListOfDictsModel(Model[Model_list[
            Model_dict[str, '_JsonAnyUnion'] | dict[str, '_JsonAnyUnion'],
    ]]):
        ...

    class JsonListOfDictsOfScalarsModel(Model[Model_list[
            Model_dict[str, JsonScalar] | dict[str, JsonScalar],
    ]]):
        ...
else:

    class JsonListOfScalarsModel(Model[_JsonListOfScalars]):
        ...

    class JsonListOfListsModel(Model[_JsonListM[_JsonAnyListM]]):
        ...

    class JsonListOfListsOfScalarsModel(Model[_JsonListM[_JsonListOfScalars]]):
        ...

    class JsonListOfDictsModel(Model[_JsonListM[_JsonAnyDictM]]):
        ...

    class JsonListOfDictsOfScalarsModel(Model[_JsonListM[_JsonDictOfScalars]]):
        ...


# Dict at the top level

if typing.TYPE_CHECKING:

    class JsonDictModel(Model_dict[str, '_JsonAnyUnion']):
        ...

else:

    class JsonDictModel(Model[_JsonAnyDictM]):
        """
        JsonDictModel is a limited JSON model supporting only JSON content
        that has a dict (or "object" in JSON nomenclature) at the root.
        The values of the top-level dict can be any JSON content, though,
        any levels deep.

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


if typing.TYPE_CHECKING:

    class JsonDictOfScalarsModel(Model_dict[str, JsonScalar]):
        ...

    class JsonDictOfListsModel(Model[Model_dict[
            str,
            Model_list['_JsonAnyUnion'] | list['_JsonAnyUnion'],
    ]]):
        ...

    class JsonDictOfListsOfScalarsModel(Model[Model_dict[
            str,
            Model_list[JsonScalar] | list[JsonScalar],
    ]]):
        ...

    class JsonDictOfDictsModel(Model[Model_dict[
            str,
            Model_dict[str, '_JsonAnyUnion'] | dict[str, '_JsonAnyUnion'],
    ]]):
        ...

    class JsonDictOfDictsOfScalarsModel(Model[Model_dict[
            str,
            Model_dict[str, JsonScalar] | dict[str, JsonScalar],
    ]]):
        ...
else:

    class JsonDictOfScalarsModel(Model[_JsonDictOfScalars]):
        ...

    class JsonDictOfListsModel(Model[_JsonDictM[_JsonAnyListM]]):
        ...

    class JsonDictOfListsOfScalarsModel(Model[_JsonDictM[_JsonListOfScalars]]):
        ...

    class JsonDictOfDictsModel(Model[_JsonDictM[_JsonAnyDictM]]):
        ...

    class JsonDictOfDictsOfScalarsModel(Model[_JsonDictM[_JsonDictOfScalars]]):
        ...


# Nested models

if typing.TYPE_CHECKING:

    class JsonOnlyListsModel(Model[_JsonScalarMimicModels | Model_list['_JsonOnlyListsUnion']]):
        ...

    class JsonNestedListsModel(Model_list['_JsonOnlyListsUnion']):
        ...

    class JsonOnlyDictsModel(Model[_JsonScalarMimicModels | Model_dict[
            str,
            '_JsonOnlyDictsUnion',
    ]]):
        ...

    class JsonNestedDictsModel(Model_dict[str, '_JsonOnlyDictsUnion']):
        ...

else:

    class JsonOnlyListsModel(Model[_JsonOnlyListsUnion]):
        ...

    class JsonNestedListsModel(Model[_JsonOnlyListsM]):
        ...

    class JsonOnlyDictsModel(Model[_JsonOnlyDictsUnion]):
        ...

    class JsonNestedDictsModel(Model[_JsonOnlyDictsM]):
        ...


# More specific models

if typing.TYPE_CHECKING:

    class JsonListOfNestedDictsModel(Model_list[
            Model_dict[str, '_JsonOnlyDictsUnion'] | dict[str, '_JsonOnlyDictsUnion'],
    ]):
        ...

    class JsonDictOfNestedListsModel(Model_dict[
            str,
            Model_list['_JsonOnlyListsUnion'] | list['_JsonOnlyListsUnion'],
    ]):
        ...

    class JsonDictOfListsOfDictsModel(Model_dict[
            str,
            Model_list[Model_dict[str, '_JsonAnyUnion'] | dict[str, '_JsonAnyUnion']],
    ]):
        ...

else:

    class JsonListOfNestedDictsModel(Model[_JsonListM[_JsonOnlyDictsM]]):
        ...

    class JsonDictOfNestedListsModel(Model[_JsonDictM[_JsonOnlyListsM]]):
        ...

    class JsonDictOfListsOfDictsModel(Model[_JsonDictM[_JsonListM[_JsonAnyDictM]]]):
        ...


# Custom models

if typing.TYPE_CHECKING:

    class JsonCustomListModel(Model_list[_JsonBaseT], Generic[_JsonBaseT]):
        ...

    class JsonCustomDictModel(Model_dict[str, _JsonBaseT], Generic[_JsonBaseT]):
        ...

else:

    class JsonCustomListModel(Model[_JsonListM[_JsonBaseT]], Generic[_JsonBaseT]):
        ...

    class JsonCustomDictModel(Model[_JsonDictM[_JsonBaseT]], Generic[_JsonBaseT]):
        ...


# Add note of dict keys to models containing dicts

_NOTE_ON_DICT_KEYS = """
    Note:
        JSON dicts (or "objects") only supports strings as keys. By
        default, however, omnipy JSON models parse the basic types
        `float`, `int`, and `bool` as strings if used as keys in JSON
        dicts/objects.

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
    JsonListOfDictsModel,
    JsonListOfDictsOfScalarsModel,
    JsonOnlyDictsModel,
    JsonNestedDictsModel,
    JsonListOfNestedDictsModel,
    JsonDictOfNestedListsModel,
    JsonDictOfListsOfDictsModel,
    JsonCustomDictModel,
]

for _dict_related_json_model_cls in _dict_related_json_model_classes:
    if _dict_related_json_model_cls.__doc__:
        _dict_related_json_model_cls.__doc__ += _NOTE_ON_DICT_KEYS

_rest_of_the_json_model_classes: list[Type[Model]] = [
    JsonScalarModel,
    JsonListModel,
    JsonListOfScalarsModel,
    JsonListOfListsModel,
    JsonListOfListsOfScalarsModel,
    JsonOnlyListsModel,
    JsonNestedListsModel,
    JsonCustomListModel,
]

_internal_model_classes: list[Type[Model]] = [
    _JsonListM, _JsonDictM, _JsonAnyListM, _JsonAnyDictM, _JsonOnlyListsM, _JsonOnlyDictsM
]

_all_json_model_classes: list[Type[Model]] = (
    _dict_related_json_model_classes + _rest_of_the_json_model_classes + _internal_model_classes)


def is_json_model_instance_hack(obj: Any) -> bool:
    """
    Check if the given class is a JSON model class. Temporary solution
    to identify JSON model classes for output formatting.

    (Does not work for JsonCustomListModel and JsonCustomDictModel)

    Args:
        cls: The class to check.

    Returns:
        True if the class is a JSON model class, False otherwise.
    """

    if is_model_instance(obj):
        plain_class = ensure_plain_type(obj.__class__)
        return plain_class in _all_json_model_classes
    return False
