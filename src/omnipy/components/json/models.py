"""JSON model classes for validating and serializing JSON-compatible content.

This module defines Omnipy's public JSON model variants, ranging from scalar-only
models to specialized list/dict containers and generic custom container models.
"""

from typing import Any, cast, Generic, Mapping, overload, Sequence, Type, TypeAlias

from typing_extensions import TypeVar

from omnipy.data.model import is_model_instance, Model
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
    from omnipy.data._typing.mimic_models import (Model_bool,
                                                  Model_float,
                                                  Model_int,
                                                  Model_str,
                                                  PlainModel)

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
    """Model wrapper for JSON-compatible lists used in internal type composition.

    This internal model represents list-shaped JSON content where each item is
    constrained to a JSON-compatible type parameter.
    """

    ...


class _JsonDictM(
        Model[dict[str, _JsonBaseT]],
        Generic[_JsonBaseT],
):
    """Model wrapper for JSON-compatible dicts used in internal type composition.

    This internal model represents dict-shaped JSON content where keys are
    strings and values are constrained to a JSON-compatible type parameter.
    """

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
    """Provide JSON-string pre-parsing behavior for model classes.

    Classes using this mixin can transparently accept serialized JSON in string
    form and convert it into parsed model content before the regular validation
    pipeline runs.
    """
    @classmethod
    def start_chars_for_json_content(cls) -> str:
        """Return leading characters that should trigger JSON-string parsing.

        Returns:
            Characters that mark a string as candidate serialized JSON content.
        """

        return '[{0123456789-tfn'  # not [{"0123456789-tfn'

    @classmethod
    def _parse_data(cls, data: Any) -> _RootT:
        """Parse potential JSON-string input into model content.

        Args:
            data: Raw input value that may be plain content or serialized JSON.

        Returns:
            Parsed model content when ``data`` is a JSON-like string that can be
            decoded, otherwise the original input content.
        """

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
    """Model for validated JSON data.

    This model accepts and validates any JSON-compatible value, including
    scalars, arrays, and objects with arbitrary nesting depth.
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

    def to_json_str(self, pretty: bool = True) -> str:
        """Serialize validated JSON content to a JSON string.

        Args:
            pretty: Whether to return indented human-readable JSON.

        Returns:
            JSON string representation of this model's content.
        """
        return self.to_json(pretty=pretty)

    @classmethod
    def from_json_str(cls, json_content: str) -> 'JsonModel':
        """Parse a JSON string into a validated ``JsonModel`` instance.

        Args:
            json_content: Serialized JSON document to parse and validate.

        Returns:
            JsonModel: New model instance containing the parsed JSON content.
        """
        return cast(JsonModel, cls.parse_raw(json_content, proto=pyd.Protocol.json))


class JsonListOrDictModel(ParseStrAsJsonMixin[_JsonListOfDictUnion], Model[_JsonListOfDictUnion]):
    """JsonListOrDictModel is a general JSON model supporting any JSON
    content except scalar data.
    """
    @classmethod
    def start_chars_for_json_content(cls) -> str:
        """Return leading characters for non-scalar JSON-string parsing.

        Returns:
            Characters that mark a string as candidate serialized JSON lists or dicts.
        """

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
    """JSON model restricted to scalar JSON values.

    Supports only ``None``, ``int``, ``float``, ``str``, and ``bool``.
    Lists and dicts (JSON objects) are not supported.

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
        """Validate JSON values whose root is an array.

        This type-checking variant mirrors the runtime ``JsonListModel`` and
        enforces a list/array at the top level, while allowing arbitrary
        JSON-compatible values within nested positions.
        """

        ...

else:

    class JsonListModel(Model[_JsonAnyListM]):
        """
        JsonListModel is a limited JSON model supporting only JSON content
        that has a list (or "array" in JSON nomenclature) at the root. The
        content of the top-level list can be any JSON content, though, any
        levels deep.

        """


if TYPE_CHECKING:

    class JsonListOfScalarsModel(
            PlainModel[_JsonListOfScalars],
            IsListContent[JsonScalar],
    ):
        """Validate JSON arrays containing only scalar values.

        This variant restricts each top-level item to a JSON scalar
        (``null``, number, string, or boolean).
        """

        ...

    class JsonListOfListsModel(
            PlainModel[_JsonListM[_JsonAnyListM]],
            IsListOfListsContent[_JsonAnyListM, _JsonAnyUnionContent],
    ):
        """Validate JSON arrays whose elements are JSON arrays.

        The top-level value must be an array, and each element must also be an
        array that may contain general JSON-compatible content.
        """

        ...

    class JsonListOfListsOfScalarsModel(
            PlainModel[_JsonListM[_JsonListOfScalars]],
            IsListOfListsContent[JsonListOfScalarsModel, JsonScalar],
    ):
        """Validate JSON arrays of scalar-only nested arrays.

        Both the top-level array and each nested array are constrained so that
        leaf values are JSON scalars.
        """

        ...

    class JsonListOfDictsModel(
            PlainModel[_JsonListM[_JsonAnyDictM]],
            IsListOfDictsContent[_JsonAnyDictM, str, _JsonAnyUnionContent],
    ):
        """Validate JSON arrays whose elements are JSON objects.

        Each top-level item must be an object/dict with string keys and
        JSON-compatible values.
        """

        ...

    class JsonListOfDictsOfScalarsModel(
            PlainModel[_JsonListM[_JsonDictOfScalars]],
            IsListOfDictsContent['JsonDictOfScalarsModel', str, JsonScalar],
    ):
        """Validate JSON arrays of objects with scalar-only values.

        Each object in the top-level array must map string keys to JSON scalar
        values only.
        """

        ...

else:

    class JsonListOfScalarsModel(Model[_JsonListOfScalars]):
        """Validate JSON arrays that contain only scalar values.

        This model accepts top-level JSON arrays where each item is one of the
        JSON scalar types (`null`, number, string, or boolean).
        """

        ...

    class JsonListOfListsModel(Model[_JsonListM[_JsonAnyListM]]):
        """Validate JSON arrays whose items are JSON arrays.

        This model enforces one array nesting level at the top level, while
        allowing each nested array to contain general JSON-compatible content.
        """

        ...

    class JsonListOfListsOfScalarsModel(Model[_JsonListM[_JsonListOfScalars]]):
        """Validate JSON arrays of scalar-only JSON arrays.

        This model requires a top-level array where each nested array contains
        only JSON scalar values.
        """

        ...

    class JsonListOfDictsModel(Model[_JsonListM[_JsonAnyDictM]]):
        """Validate JSON arrays whose items are JSON objects.

        This model accepts a top-level array and enforces that every element is
        a JSON object with string keys and JSON-compatible values.
        """

        ...

    class JsonListOfDictsOfScalarsModel(Model[_JsonListM[_JsonDictOfScalars]]):
        """Validate JSON arrays of scalar-only JSON objects.

        This model accepts top-level arrays where each object value is limited
        to JSON scalar types.
        """

        ...


# Dict at the top level

if TYPE_CHECKING:

    class JsonDictModel(PlainModel[_JsonAnyDictM], IsDictContent[str, _JsonAnyUnionContent]):
        """Validate JSON values whose root is an object.

        This type-checking variant mirrors the runtime ``JsonDictModel`` and
        requires a dict/object at the top level with string keys and
        JSON-compatible nested values.
        """

        ...

else:

    class JsonDictModel(Model[_JsonAnyDictM]):
        """
        JsonDictModel is a limited JSON model supporting only JSON content
        that has a dict (or "object" in JSON nomenclature) at the root.
        The values of the top-level dict can be any JSON content, though,
        any levels deep.

        """


if TYPE_CHECKING:

    class JsonDictOfScalarsModel(
            PlainModel[_JsonDictOfScalars],
            IsDictContent[str, JsonScalar],
    ):
        """Validate JSON objects whose values are scalar values.

        All top-level values must be JSON scalars, while keys remain strings.
        """

        ...

    class JsonDictOfListsModel(
            PlainModel[_JsonDictM[_JsonAnyListM]],
            IsDictOfListsContent[str, _JsonAnyListM, _JsonAnyUnionContent],
    ):
        """Validate JSON objects whose values are JSON arrays.

        Each top-level object value must be an array with JSON-compatible
        nested content.
        """

        ...

    class JsonDictOfListsOfScalarsModel(
            PlainModel[_JsonDictM[_JsonListOfScalars]],
            IsDictOfListsContent[str, JsonListOfScalarsModel, JsonScalar],
    ):
        """Validate JSON objects whose values are scalar-only arrays.

        Each top-level object value must be an array whose elements are JSON
        scalars.
        """

        ...

    class JsonDictOfDictsModel(
            PlainModel[_JsonDictM[_JsonAnyDictM]],
            IsDictOfDictsContent[str, _JsonAnyDictM, str, _JsonAnyUnionContent],
    ):
        """Validate JSON objects whose values are JSON objects.

        Each top-level value must itself be an object with string keys and
        JSON-compatible values.
        """

        ...

    class JsonDictOfDictsOfScalarsModel(
            PlainModel[_JsonDictM[_JsonDictOfScalars]],
            IsDictOfDictsContent[str, JsonDictOfScalarsModel, str, JsonScalar],
    ):
        """Validate nested JSON objects with scalar-only leaves.

        Top-level values must be objects that map string keys to JSON scalar
        values.
        """

        ...

else:

    class JsonDictOfScalarsModel(Model[_JsonDictOfScalars]):
        """Validate JSON objects whose values are scalar values.

        This model accepts top-level JSON objects and requires all values to be
        JSON scalar types.
        """

        ...

    class JsonDictOfListsModel(Model[_JsonDictM[_JsonAnyListM]]):
        """Validate JSON objects whose values are JSON arrays.

        This model enforces a top-level object shape where each value is a JSON
        array containing JSON-compatible content.
        """

        ...

    class JsonDictOfListsOfScalarsModel(Model[_JsonDictM[_JsonListOfScalars]]):
        """Validate JSON objects whose values are scalar-only JSON arrays.

        This model accepts top-level objects where each value is an array of
        JSON scalar values.
        """

        ...

    class JsonDictOfDictsModel(Model[_JsonDictM[_JsonAnyDictM]]):
        """Validate JSON objects whose values are JSON objects.

        This model enforces a top-level object where each value is another JSON
        object containing JSON-compatible values.
        """

        ...

    class JsonDictOfDictsOfScalarsModel(Model[_JsonDictM[_JsonDictOfScalars]]):
        """Validate JSON objects whose values are scalar-only JSON objects.

        This model accepts top-level objects where each nested object contains
        only JSON scalar values.
        """

        ...


# Nested models


class JsonOnlyListsModel(Model[_JsonOnlyListsUnion]):
    """Model for JSON content composed only of scalars and nested arrays.

    This model accepts JSON scalars and recursively nested JSON arrays, but it
    rejects JSON objects anywhere in the structure.
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
        def __new__(cls, value: IsList | _JsonNestedListsM) -> _JsonNestedListsM:
            ...

        @overload
        def __new__(cls, value: object) -> AnyJsonOnlyListsModel:
            ...

        def __new__(cls, value: _JsonOnlyListsUnionContent | object) -> AnyJsonOnlyListsModel:
            ...


class JsonOnlyDictsModel(Model[_JsonOnlyDictsUnion]):
    """Model for JSON content composed only of scalars and nested objects.

    This model accepts JSON scalars and recursively nested JSON objects, but it
    rejects JSON arrays anywhere in the structure.
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
        """Validate recursively nested JSON arrays with scalar leaves.

        This model captures list-only JSON hierarchies where recursion ends at
        scalar values.
        """

        ...

    class JsonNestedDictsModel(
            PlainModel[_JsonNestedDictsM],
            IsDictContent[str, _JsonOnlyDictsUnionContent],
    ):
        """Validate recursively nested JSON objects with scalar leaves.

        This model captures object-only JSON hierarchies where recursion ends at
        scalar values.
        """

        ...

else:

    class JsonNestedListsModel(Model[_JsonNestedListsM]):
        """Validate nested JSON arrays whose leaves are scalar values.

        This model captures recursively nested JSON arrays that eventually
        terminate in JSON scalar values.
        """

        ...

    class JsonNestedDictsModel(Model[_JsonNestedDictsM]):
        """Validate nested JSON objects whose leaves are scalar values.

        This model captures recursively nested JSON objects that eventually
        terminate in JSON scalar values.
        """

        ...


# More specific models

if TYPE_CHECKING:

    class JsonListOfNestedDictsModel(
            PlainModel[_JsonListM[_JsonNestedDictsM]],
            IsListOfDictsContent[JsonNestedDictsModel, str, _JsonOnlyDictsUnionContent],
    ):
        """Validate JSON arrays whose items are nested JSON objects.

        Each top-level element must be a recursively nested object structure
        with scalar leaves.
        """

        ...

    class JsonDictOfNestedListsModel(
            PlainModel[_JsonDictM[_JsonNestedListsM]],
            IsDictOfListsContent[str, JsonNestedListsModel, _JsonOnlyListsUnionContent],
    ):
        """Validate JSON objects whose values are nested JSON arrays.

        Each top-level value must be a recursively nested array structure with
        scalar leaves.
        """

        ...

    class JsonDictOfListsOfDictsModel(
            PlainModel[_JsonDictM[_JsonListM[_JsonAnyDictM]]],
            IsDictOfListsContent[str, JsonListOfDictsModel, Mapping[str, '_JsonAnyUnionContent']],
    ):
        """Validate JSON objects whose values are arrays of objects.

        Each top-level value must be an array where every element is a JSON
        object.
        """

        ...

else:

    class JsonListOfNestedDictsModel(Model[_JsonListM[_JsonNestedDictsM]]):
        """Validate JSON arrays whose items are nested JSON objects.

        This model accepts top-level arrays where each element is a recursively
        nested JSON object structure.
        """

        ...

    class JsonDictOfNestedListsModel(Model[_JsonDictM[_JsonNestedListsM]]):
        """Validate JSON objects whose values are nested JSON arrays.

        This model accepts top-level objects where each value is a recursively
        nested JSON array structure.
        """

        ...

    class JsonDictOfListsOfDictsModel(Model[_JsonDictM[_JsonListM[_JsonAnyDictM]]]):
        """Validate JSON objects whose values are arrays of JSON objects.

        This model enforces top-level object values to be arrays where each
        element is a JSON object.
        """

        ...


# Custom models

if TYPE_CHECKING:

    class JsonCustomListModel(
            PlainModel[_JsonListM[_JsonBaseT]],
            IsListContent[_JsonBaseT],
            Generic[_JsonBaseT],
    ):
        """Validate JSON arrays constrained to a custom item type.

        This generic model allows callers to define list-shaped JSON models with
        explicit JSON-compatible element constraints.
        """

        ...

    class JsonCustomDictModel(
            PlainModel[_JsonDictM[_JsonBaseT]],
            IsDictContent[str, _JsonBaseT],
            Generic[_JsonBaseT],
    ):
        """Validate JSON objects constrained to a custom value type.

        This generic model allows callers to define object-shaped JSON models
        with explicit JSON-compatible value constraints.
        """

        ...

else:

    class JsonCustomListModel(Model[_JsonListM[_JsonBaseT]], Generic[_JsonBaseT]):
        """Validate JSON arrays constrained to a JSON-compatible item type.

        This generic model supports defining list-shaped JSON models with a
        caller-specified JSON-compatible item constraint.
        """

        ...

    class JsonCustomDictModel(Model[_JsonDictM[_JsonBaseT]], Generic[_JsonBaseT]):
        """Validate JSON objects constrained to a JSON-compatible value type.

        This generic model supports defining object-shaped JSON models with a
        caller-specified JSON-compatible value constraint.
        """

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
