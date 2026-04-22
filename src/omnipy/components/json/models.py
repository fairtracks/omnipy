from typing import Any, cast, Generic, Mapping, overload, Sequence, Type, TypeAlias

from typing_extensions import TypeVar

from omnipy.data.model import Model
from omnipy.data.typechecks import is_model_instance
from omnipy.shared.protocols.builtins import IsBool, IsDict, IsFloat, IsInt, IsList, IsStr
from omnipy.shared.protocols.content import (IsDictContent,
                                             IsDictOfDictsContent,
                                             IsDictOfListsContent,
                                             IsListContent,
                                             IsListOfDictsContent,
                                             IsListOfListsContent)
from omnipy.shared.typing import TYPE_CHECKER, TYPE_CHECKING
from omnipy.util.helpers import ensure_plain_type
import omnipy.util.pydantic as pyd

from .helpers import parse_str_as_json
from .typedefs import JsonScalar

if TYPE_CHECKING:
    from omnipy.data._mimic_models import Model_bool, Model_float, Model_int, Model_str
    from omnipy.data.model import PlainModel

# # IsMapping[str, int]
#
# sddddf: IsMapping[int, str] = {1: "foo", 2: "bar"}
# ssd: IsKeysView[int] = {1: "foo", 2: "bar"}.keys()
# sssd: IsDictKeys[int, str] = {1: "foo", 2: "bar"}.keys()
#
# kkjah: IsMappingProxyType[str, str] = MappingProxyType({"d": 'S'})

#
# Private models
#

# Basic building block models

if TYPE_CHECKING:
    _JsonBaseT = TypeVar(
        '_JsonBaseT', bound='_JsonAnyUnionContent | _JsonListM | _JsonDictM', default='JsonScalar')

else:
    _JsonBaseT = TypeVar(
        '_JsonBaseT', bound='_JsonAnyUnion | _JsonListM | _JsonDictM', default='JsonScalar')


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

if TYPE_CHECKING:

    class _JsonAnyListM(
            _JsonListM['_JsonAnyUnion'],
            IsListContent['_JsonAnyUnionContent'],
    ):
        ...

    class _JsonAnyDictM(
            _JsonDictM['_JsonAnyUnion'],
            IsDictContent[str, '_JsonAnyUnionContent'],
    ):
        ...

    class _JsonNestedListsM(
            _JsonListM['_JsonOnlyListsUnion'],
            IsListContent['_JsonOnlyListsUnionContent'],
    ):
        ...

    class _JsonNestedDictsM(
            _JsonDictM['_JsonOnlyDictsUnion'],
            IsDictContent[str, '_JsonOnlyDictsUnionContent'],
    ):
        ...
else:

    class _JsonAnyListM(_JsonListM['_JsonAnyUnion']):
        ...

    class _JsonAnyDictM(_JsonDictM['_JsonAnyUnion']):
        ...

    class _JsonNestedListsM(_JsonListM['_JsonOnlyListsUnion']):
        ...

    class _JsonNestedDictsM(_JsonDictM['_JsonOnlyDictsUnion']):
        ...


# TypeAliases
# TODO: Consider whether these TypeAliases are needed in pydantic v2. In v1 they are needed to for
#       the hack for propagating None to work. Removing this level will simplify JSON models.
#       If updated, also update frozen models

if TYPE_CHECKING:
    _JsonListOrDictContent: TypeAlias = (
        _JsonAnyListM | Sequence['_JsonAnyUnionContent']
        | _JsonAnyDictM | Mapping[str, '_JsonAnyUnionContent'])
    _JsonAnyUnionContent: TypeAlias = JsonScalar | _JsonListOrDictContent
    _JsonNestedListsContent: TypeAlias = Sequence['_JsonOnlyListsUnionContent']
    _JsonNestedDictsContent: TypeAlias = Mapping[str, '_JsonOnlyDictsUnionContent']
    _JsonOnlyListsUnionContent: TypeAlias = JsonScalar | _JsonNestedListsM | _JsonNestedListsContent
    _JsonOnlyDictsUnionContent: TypeAlias = JsonScalar | _JsonNestedDictsM | _JsonNestedDictsContent

_JsonAnyUnion: TypeAlias = JsonScalar | _JsonAnyListM | _JsonAnyDictM
_JsonListOfDictUnion: TypeAlias = _JsonAnyListM | _JsonAnyDictM
_JsonOnlyListsUnion: TypeAlias = JsonScalar | _JsonNestedListsM
_JsonOnlyDictsUnion: TypeAlias = JsonScalar | _JsonNestedDictsM

_JsonListOfScalars: TypeAlias = _JsonListM[JsonScalar]
_JsonDictOfScalars: TypeAlias = _JsonDictM[JsonScalar]

# Basic models needs to update their forward_refs with type aliases
# declared above

_JsonAnyListM.update_forward_refs()
_JsonAnyDictM.update_forward_refs()
_JsonNestedListsM.update_forward_refs()
_JsonNestedDictsM.update_forward_refs()

# Exportable models
#

# General

# Note: Since parsing JSON strings is potentially ambiguous (a string can
#       be a valid JSON string, but also a string representing JSON
#       entities), strings starting with a quote are not parsed as JSON
#       entities.

AnyJsonScalarModel: TypeAlias = Model[None] | Model[int] | Model[float] | Model[str] | Model[bool]

AnyJsonOnlyListsModel: TypeAlias = AnyJsonScalarModel | _JsonNestedListsM
AnyJsonOnlyDictsModel: TypeAlias = AnyJsonScalarModel | _JsonNestedDictsM
AnyJsonListOrDictModel: TypeAlias = _JsonAnyListM | _JsonAnyDictM
AnyJsonModel: TypeAlias = AnyJsonScalarModel | AnyJsonListOrDictModel

_RootT = TypeVar('_RootT')


class ParseStrAsJsonMixin(Generic[_RootT]):
    @classmethod
    def start_chars_for_json_content(cls) -> str:
        return '[{0123456789-tfn'  # not [{"0123456789-tfn'

    @classmethod
    def _parse_data(cls, data: Any) -> _RootT:
        cls_as_model = cast(type[Model[_RootT]], cls)
        if isinstance(data, str):
            if len(data) > 0 and data[0] in cls.start_chars_for_json_content():
                # Potentially a string representing JSON entities.
                parsed_json = parse_str_as_json(data)
                if not isinstance(parsed_json, pyd.UndefinedType):
                    if isinstance(parsed_json, str):
                        return cast(_RootT, parsed_json)
                    return cls_as_model(parsed_json).content

        return cast(_RootT, data)


class JsonModel(ParseStrAsJsonMixin[_JsonAnyUnion], Model[_JsonAnyUnion]):
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

    if TYPE_CHECKING and TYPE_CHECKER != 'mypy':

        @overload
        def __new__(cls, value: None) -> Model[None]:
            ...

        @overload
        def __new__(cls, value: IsBool) -> Model_bool:  # pyright: ignore[reportOverlappingOverload]
            ...

        @overload
        def __new__(cls, value: IsInt) -> Model_int:
            ...

        @overload
        def __new__(cls, value: IsFloat) -> Model_float:
            ...

        @overload
        def __new__(cls, value: IsList | _JsonAnyListM) -> _JsonAnyListM:
            ...

        @overload
        def __new__(cls, value: IsDict | _JsonAnyDictM) -> _JsonAnyDictM:
            ...

        @overload
        def __new__(cls, value: IsStr | object) -> AnyJsonModel:
            ...

        def __new__(cls, value: _JsonAnyUnionContent | object) -> AnyJsonModel:
            ...


class JsonListOrDictModel(ParseStrAsJsonMixin[_JsonListOfDictUnion], Model[_JsonListOfDictUnion]):
    """JsonListOrDictModel is a general JSON model supporting any JSON
    content except scalar data.

    Examples:
        >>> my_json = JsonListOrDictModel([True, {'a': None, 'b': [1, 12.5, 'abc']}])
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
        ...     my_json = JsonListOrDictModel(123)  # scalars not supported
        ... except Exception as e:
        ...     print(str(e).splitlines()[0])
        34 validation errors for JsonListOrDictModel
    """
    @classmethod
    def start_chars_for_json_content(cls) -> str:
        return '[{'

    if TYPE_CHECKING and TYPE_CHECKER != 'mypy':

        @overload
        def __new__(cls, value: IsList | _JsonAnyListM) -> _JsonAnyListM:
            ...

        @overload
        def __new__(cls, value: IsDict | _JsonAnyDictM) -> _JsonAnyDictM:
            ...

        @overload
        def __new__(cls, value: IsStr | object) -> AnyJsonListOrDictModel:
            ...

        def __new__(cls, value: _JsonListOrDictContent | object) -> AnyJsonListOrDictModel:
            ...


# Scalars


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

    if TYPE_CHECKING and TYPE_CHECKER != 'mypy':

        @overload
        def __new__(cls, value: None) -> Model[None]:
            ...

        @overload
        def __new__(cls, value: IsBool) -> Model_bool:  # pyright: ignore[reportOverlappingOverload]
            ...

        @overload
        def __new__(cls, value: IsInt) -> Model_int:
            ...

        @overload
        def __new__(cls, value: IsFloat) -> Model_float:
            ...

        @overload
        def __new__(cls, value: IsStr) -> Model_str:
            ...

        @overload
        def __new__(cls, value: object) -> AnyJsonScalarModel:
            ...

        def __new__(cls, value: JsonScalar | object) -> AnyJsonScalarModel:
            ...


# List at the top level

if TYPE_CHECKING:

    class JsonListModel(PlainModel[_JsonAnyListM], IsListContent[_JsonAnyUnionContent]):
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


if TYPE_CHECKING:

    class JsonListOfScalarsModel(
            PlainModel[_JsonListOfScalars],
            IsListContent[JsonScalar],
    ):
        ...

    class JsonListOfListsModel(
            PlainModel[_JsonListM[_JsonAnyListM]],
            IsListOfListsContent[_JsonAnyListM, _JsonAnyUnionContent],
    ):
        ...

    class JsonListOfListsOfScalarsModel(
            PlainModel[_JsonListM[_JsonListOfScalars]],
            IsListOfListsContent[JsonListOfScalarsModel, JsonScalar],
    ):
        ...

    class JsonListOfDictsModel(
            PlainModel[_JsonListM[_JsonAnyDictM]],
            IsListOfDictsContent[_JsonAnyDictM, str, _JsonAnyUnionContent],
    ):
        ...

    class JsonListOfDictsOfScalarsModel(
            PlainModel[_JsonListM[_JsonDictOfScalars]],
            IsListOfDictsContent['JsonDictOfScalarsModel', str, JsonScalar],
    ):
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

if TYPE_CHECKING:

    class JsonDictModel(PlainModel[_JsonAnyDictM], IsDictContent[str, _JsonAnyUnionContent]):
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


if TYPE_CHECKING:

    class JsonDictOfScalarsModel(
            PlainModel[_JsonDictOfScalars],
            IsDictContent[str, JsonScalar],
    ):
        ...

    class JsonDictOfListsModel(
            PlainModel[_JsonDictM[_JsonAnyListM]],
            IsDictOfListsContent[str, _JsonAnyListM, _JsonAnyUnionContent],
    ):
        ...

    class JsonDictOfListsOfScalarsModel(
            PlainModel[_JsonDictM[_JsonListOfScalars]],
            IsDictOfListsContent[str, JsonListOfScalarsModel, JsonScalar],
    ):
        ...

    class JsonDictOfDictsModel(
            PlainModel[_JsonDictM[_JsonAnyDictM]],
            IsDictOfDictsContent[str, _JsonAnyDictM, str, _JsonAnyUnionContent],
    ):
        ...

    class JsonDictOfDictsOfScalarsModel(
            PlainModel[_JsonDictM[_JsonDictOfScalars]],
            IsDictOfDictsContent[str, JsonDictOfScalarsModel, str, JsonScalar],
    ):
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


class JsonOnlyListsModel(Model[_JsonOnlyListsUnion]):
    if TYPE_CHECKING and TYPE_CHECKER != 'mypy':

        @overload
        def __new__(cls, value: None) -> Model[None]:
            ...

        @overload
        def __new__(cls, value: IsBool) -> Model_bool:  # pyright: ignore[reportOverlappingOverload]
            ...

        @overload
        def __new__(cls, value: IsInt) -> Model_int:
            ...

        @overload
        def __new__(cls, value: IsFloat) -> Model_float:
            ...

        @overload
        def __new__(cls, value: IsStr) -> Model_str:
            ...

        @overload
        def __new__(cls, value: IsList | _JsonNestedListsM) -> _JsonNestedListsM:
            ...

        @overload
        def __new__(cls, value: object) -> AnyJsonOnlyListsModel:
            ...

        def __new__(cls, value: _JsonOnlyListsUnionContent | object) -> AnyJsonOnlyListsModel:
            ...


class JsonOnlyDictsModel(Model[_JsonOnlyDictsUnion]):
    if TYPE_CHECKING and TYPE_CHECKER != 'mypy':

        @overload
        def __new__(cls, value: None) -> Model[None]:
            ...

        @overload
        def __new__(cls, value: IsBool) -> Model_bool:  # pyright: ignore[reportOverlappingOverload]
            ...

        @overload
        def __new__(cls, value: IsInt) -> Model_int:
            ...

        @overload
        def __new__(cls, value: IsFloat) -> Model_float:
            ...

        @overload
        def __new__(cls, value: IsStr) -> Model_str:
            ...

        @overload
        def __new__(cls, value: IsDict | _JsonNestedDictsM) -> _JsonNestedDictsM:
            ...

        @overload
        def __new__(cls, value: object) -> AnyJsonOnlyDictsModel:
            ...

        def __new__(cls, value: _JsonOnlyDictsUnionContent | object) -> AnyJsonOnlyDictsModel:
            ...


if TYPE_CHECKING:

    class JsonNestedListsModel(
            PlainModel[_JsonNestedListsM],
            IsListContent[_JsonOnlyListsUnionContent],
    ):
        ...

    class JsonNestedDictsModel(
            PlainModel[_JsonNestedDictsM],
            IsDictContent[str, _JsonOnlyDictsUnionContent],
    ):
        ...

else:

    class JsonNestedListsModel(Model[_JsonNestedListsM]):
        ...

    class JsonNestedDictsModel(Model[_JsonNestedDictsM]):
        ...


# More specific models

if TYPE_CHECKING:

    class JsonListOfNestedDictsModel(
            PlainModel[_JsonListM[_JsonNestedDictsM]],
            IsListOfDictsContent[JsonNestedDictsModel, str, _JsonOnlyDictsUnionContent],
    ):
        ...

    class JsonDictOfNestedListsModel(
            PlainModel[_JsonDictM[_JsonNestedListsM]],
            IsDictOfListsContent[str, JsonNestedListsModel, _JsonOnlyListsUnionContent],
    ):
        ...

    class JsonDictOfListsOfDictsModel(
            PlainModel[_JsonDictM[_JsonListM[_JsonAnyDictM]]],
            IsDictOfListsContent[str, JsonListOfDictsModel, Mapping[str, '_JsonAnyUnionContent']],
    ):
        ...

else:

    class JsonListOfNestedDictsModel(Model[_JsonListM[_JsonNestedDictsM]]):
        ...

    class JsonDictOfNestedListsModel(Model[_JsonDictM[_JsonNestedListsM]]):
        ...

    class JsonDictOfListsOfDictsModel(Model[_JsonDictM[_JsonListM[_JsonAnyDictM]]]):
        ...


# Custom models

if TYPE_CHECKING:

    class JsonCustomListModel(
            PlainModel[_JsonListM[_JsonBaseT]],
            IsListContent[_JsonBaseT],
            Generic[_JsonBaseT],
    ):
        ...

    class JsonCustomDictModel(
            PlainModel[_JsonDictM[_JsonBaseT]],
            IsDictContent[str, _JsonBaseT],
            Generic[_JsonBaseT],
    ):
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
    _JsonListM, _JsonDictM, _JsonAnyListM, _JsonAnyDictM, _JsonNestedListsM, _JsonNestedDictsM
]

_all_json_model_classes: list[Type[Model]] = (
    _dict_related_json_model_classes + _rest_of_the_json_model_classes + _internal_model_classes)


def is_json_model_instance_hack(obj: Any) -> bool:
    """
    Check if the given object is an instance of a JSON model class.
    Temporary solution to identify JSON model classes for output formatting.

    (Does not work for JsonCustomListModel and JsonCustomDictModel)

    Args:
        obj: The object to check.

    Returns:
        True if the object is an instance of a JSON model class, False
        otherwise.
    """

    if is_model_instance(obj):
        plain_class = ensure_plain_type(obj.__class__)
        return plain_class in _all_json_model_classes
    return False
