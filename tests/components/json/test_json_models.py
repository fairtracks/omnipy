"""Case-driven and focused tests for JSON models."""

from dataclasses import fields
import os
from textwrap import dedent
from typing import Annotated, Any, TypeAlias

import pytest
import pytest_cases as pc

from omnipy.components.json.models import (
    _JsonAnyDictM,
    _JsonAnyListM,
    _JsonDictM,
    _JsonListM,
    JsonCustomDictModel,
    JsonCustomListModel,
    JsonDictModel,
    JsonDictOfDictsModel,
    JsonDictOfScalarsModel,
    JsonListModel,
    JsonListOfScalarsModel,
    JsonModel,
    JsonScalarModel,
)
from omnipy.components.json.typedefs import JsonScalar
from omnipy.util.pydantic import ValidationError

from ...helpers.protocols import AssertModelOrValFunc
from ..helpers.classes import CaseInfo


@pc.parametrize_with_cases('case', cases='.cases.json_data')
def test_json_models(case: CaseInfo) -> None:
    """Validate JSON model classes against shared cases."""
    for field in fields(case.data_points):
        name = field.name
        for model_cls in case.model_classes_for_data_point(name):
            data = getattr(case.data_points, name)

            # print('\n---')
            # print(f'Field name: {name}')
            # print(f'Model class: {model_cls.__name__}')
            # print(f'Data input: {data}')

            if case.data_point_should_fail(name):
                with pytest.raises(ValidationError):
                    model_cls(data)
                # print(f'Error: {e}')
            else:
                model_obj = model_cls(data)  # noqa: F841

                # print(f'repr(model_obj): {repr(model_obj)}')
                # print(f'model_obj.content: {model_obj.content}')
                # print(f'model_obj.to_data(): {model_obj.to_data()}')
                # print(f'model_obj.to_json(): {model_obj.to_json(pretty=True)}')


MyJsonDictOfScalarsModel: TypeAlias = JsonCustomDictModel[JsonScalar]
MyJsonListOfScalarsModel: TypeAlias = JsonCustomListModel[JsonScalar]


def test_json_model_consistency_basic() -> None:
    """Keep base JSON model specializations consistent."""
    example_dict_data = {'abc': 2312}
    assert JsonModel(example_dict_data).content == _JsonAnyDictM(__root__={'abc': 2312})
    assert JsonDictModel(example_dict_data).content == _JsonAnyDictM(__root__={'abc': 2312})
    assert JsonDictOfScalarsModel(example_dict_data).content == _JsonDictM[JsonScalar](
        __root__={'abc': 2312}
    )
    assert MyJsonDictOfScalarsModel(example_dict_data).content == _JsonDictM[JsonScalar](
        __root__={'abc': 2312}
    )

    example_list_data = ['abc', 2312]
    assert JsonModel(example_list_data).content == _JsonAnyListM(__root__=['abc', 2312])
    assert JsonListModel(example_list_data).content == _JsonAnyListM(__root__=['abc', 2312])
    assert JsonListOfScalarsModel(example_list_data).content == _JsonListM[JsonScalar](
        __root__=['abc', 2312]
    )
    assert MyJsonListOfScalarsModel(example_list_data).content == _JsonListM[JsonScalar](
        __root__=['abc', 2312]
    )


def test_json_model_consistency_with_none() -> None:
    """Keep JSON model specializations consistent with None values."""
    example_dict_data = {'abc': None}
    assert JsonModel(example_dict_data).content == _JsonAnyDictM(__root__={'abc': None})

    assert JsonDictModel(example_dict_data).content == _JsonAnyDictM(__root__={'abc': None})

    assert JsonDictOfScalarsModel(example_dict_data).content == _JsonDictM[JsonScalar](
        __root__={'abc': None}
    )

    assert MyJsonDictOfScalarsModel(example_dict_data).content == _JsonDictM[JsonScalar](
        __root__={'abc': None}
    )

    example_list_data = ['abc', None]
    assert JsonModel(example_list_data).content == _JsonAnyListM(__root__=['abc', None])

    assert JsonListModel(example_list_data).content == _JsonAnyListM(__root__=['abc', None])

    assert JsonListOfScalarsModel(example_list_data).content == _JsonListM[JsonScalar](
        __root__=['abc', None]
    )

    assert MyJsonListOfScalarsModel(example_list_data).content == _JsonListM[JsonScalar](
        __root__=['abc', None]
    )


# TODO: Revisit test_error_list_of_single_dict_with_two_elements_known_issue after pydantic v2 is
#       supported.
@pytest.mark.skipif(
    os.getenv('OMNIPY_FORCE_SKIPPED_TEST') != '1',
    reason=dedent("""\
      Known issue with pydantic v1 due to attempting to parse a list of tuples to a dictionary.
      Here the inner dict is treated as a sequence, which returns the keys.
      """),
)
def test_error_list_of_single_dict_with_two_elements_known_issue():
    """Document the known pydantic v1 list-of-dict issue."""
    with pytest.raises(ValidationError):
        a = JsonDictModel([{'a': 1, 'b': 2}])
        assert a.to_data() == {'a': 'b'}


# TODO: Revisit test_json_known_issue after pydantic v2 is supported.
@pytest.mark.usefixtures('runtime')
@pytest.mark.skipif(
    os.getenv('OMNIPY_FORCE_SKIPPED_TEST') != '1',
    reason=dedent("""\
        Due to "feature" in pydantic v1:

        ```
        class MyDict(pyd.BaseModel):
            dict_of_scalars: dict[str, int] = {'a': 123}
            dict_of_dicts: dict[str, dict[str, int]] = {'a': {'x': 123}}

        >>> MyDict(dict_of_scalars=[])
        MyDict(dict_of_scalars={}, dict_of_dicts={'a': {'x': 123}})
        >>> MyDict(dict_of_scalars={'a': []})
        [...]
        pydantic.error_wrappers.ValidationError: 1 validation error for MyDict
        dict_of_scalars -> a
          value is not a valid integer (type=type_error.integer)
        >>> MyDict(dict_of_dicts={'a': []})
        MyDict(dict_of_scalars={'a': 123}, dict_of_dicts={'a': {}})

        Pydantic v2 fails all these validations.

        While v1 behavior is consistent with the builtin dict (`dict([]) == {}`), it may cause
        hard-to-detect bugs. While Omnipy in general moves in the direction of as broadly
        interoperable parsing as possible, the stricter v2 behavior is in this case preferable.
    """),
)
def test_error_dict_with_empty_list_known_issue():
    """Document known pydantic v1 empty-list dict behavior."""
    with pytest.raises(ValidationError):
        # A dict value of [] is interpreted by pydantic v1 as an empty dict
        dict_model = JsonDictModel([])
        assert dict_model.to_data() == {}

    dict_of_scalars_model = JsonDictOfScalarsModel({'a': 123})

    with pytest.raises(ValidationError):
        # Setting an integer value of a nested dict to [] fails validation as expected
        dict_of_scalars_model['a'] = []  # pyright: ignore[reportArgumentType]

    dict_of_dicts_model = JsonDictOfDictsModel({'a': {'x': 123}})

    with pytest.raises(ValidationError):
        # However, setting the value of a nested dict of dicts to [] should also fail
        dict_of_dicts_model['a'] = []
        assert dict_of_dicts_model.to_data() == {'a': {}}


# TODO: Write tests for misc model operations relevant for JSON data. Try to avoid overlap with
#       with test_model.


@pytest.mark.usefixtures('runtime')
def test_json_model_operations(
    assert_model_if_dyn_conv_else_val: Annotated[AssertModelOrValFunc, pytest.fixture],
):
    """Exercise common item access and merge operations."""

    a = JsonListModel([1, 2, 3])
    assert_model_if_dyn_conv_else_val(a[0], int, 1)

    b = JsonModel([1, 2, 3])
    assert_model_if_dyn_conv_else_val(b[0], int, 1)

    c = JsonDictModel({'a': 1, 'b': 2, 'c': 3})
    assert_model_if_dyn_conv_else_val(c['c'], int, 3)

    c |= JsonDictModel({'b': 4, 'd': 5})
    assert_model_if_dyn_conv_else_val(c['b'], int, 4)
    assert_model_if_dyn_conv_else_val(c['c'], int, 3)
    assert_model_if_dyn_conv_else_val(c['d'], int, 5)

    d = JsonModel({'a': 1, 'b': 2, 'c': 3})
    assert_model_if_dyn_conv_else_val(d['c'], int, 3)

    d |= JsonModel({'b': 4, 'd': 5})
    assert_model_if_dyn_conv_else_val(c['b'], int, 4)
    assert_model_if_dyn_conv_else_val(c['c'], int, 3)
    assert_model_if_dyn_conv_else_val(c['d'], int, 5)

    e = JsonScalarModel(1)
    assert (e + 1).content == 2


# Note: Since parsing JSON strings is potentially ambiguous (a string can
#       be a valid JSON string, but also a string representing JSON
#       entities), a JSON string literal is only decoded if the decoded
#       string would not itself be parsed as JSON entities. Otherwise
#       (e.g. '"12"') the quoted form is kept.


@pc.parametrize(
    'json_string, expected_data',
    [
        ('{"a": 1, "b": 2}', {'a': 1, 'b': 2}),
        ('[1, 2, 3]', [1, 2, 3]),
        ('{"a": [1, -2.5, null, true]}', {'a': [1, -2.5, None, True]}),
        ('"A simple JSON string"', 'A simple JSON string'),
        ('"\\"A simple JSON string\\""', '"\\"A simple JSON string\\""'),
        ('"Hello": 234', '"Hello": 234'),
        ('12', 12),
        ('"12"', '"12"'),
        ('"1\\u0032"', '"12"'),
        ('0.25', 0.25),
        ('"0.25"', '"0.25"'),
        ('null', None),
        ('"null"', '"null"'),
        ('false', False),
        ('"false"', '"false"'),
    ],
)
def test_json_parsing_of_json_strings(json_string: str, expected_data: Any) -> None:
    """Parse JSON strings into the expected JSON model data."""
    assert JsonModel(json_string).to_data() == expected_data

    if isinstance(expected_data, str):
        assert JsonModel(json_string).content == expected_data
    else:
        assert JsonModel(json_string) == JsonModel(expected_data)

    # This would fail if decoded JSON string literals were parsed further
    assert JsonModel(JsonModel(json_string)).to_data() == expected_data


# Note: Strings that JSON-string parsing would change (e.g. '123', which is
#       parsed as an int) cannot be JsonModel content. Their quoted form
#       (e.g. '"123"') is used instead, which to_json() exports as the JSON
#       text for the unquoted string.


@pc.parametrize(
    'data, expected_json',
    [
        ('"123"', '"123"'),
        ('"true"', '"true"'),
        ('"[1, 2]"', '"[1, 2]"'),
        ('"12\\u0033"', '"123"'),
        ('"[\\"\\u00e6\\"]"', '"[\\"æ\\"]"'),
        ('"\\"x\\""', '"\\"x\\""'),
        ('"A simple JSON string"', '"A simple JSON string"'),
        ('"Hello": 234', '"\\"Hello\\": 234"'),
        ('line1\nline2', '"line1\\nline2"'),
        (' "123"', '" \\"123\\""'),
        ('hello', '"hello"'),
        ('123 apples', '"123 apples"'),
        ('', '""'),
        ('"unterminated', '"\\"unterminated"'),
        (123, '123'),
        (None, 'null'),
        ([1, '2', '"3"'], '[\n  1,\n  "2",\n  "\\"3\\""\n]'),
        ({'k': '123'}, '{\n  "k": "123"\n}'),
    ],
)
def test_json_model_to_json_round_trip(data: Any, expected_json: str) -> None:
    """Export JSON text that from_json() and direct loading parse back to the same content."""
    model = JsonModel(data)
    assert model.to_json() == expected_json

    loaded = JsonModel()
    loaded.from_json(model.to_json())
    assert loaded.to_data() == model.to_data()
    assert JsonModel(loaded.to_data()).to_data() == model.to_data()

    assert JsonModel(model.to_json()).to_data() == model.to_data()


@pc.parametrize(
    'json_content, expected_data',
    [
        ('"hello"', 'hello'),
        ('"A simple JSON string"', 'A simple JSON string'),
        ('"\\"x\\""', '"\\"x\\""'),
        ('"123"', '"123"'),
        ('"12\\u0033"', '"123"'),
        ('"123"\n', '"123"'),
        (' "hello" ', 'hello'),
        ('123', 123),
        ('[1, "2"]', [1, '2']),
        ('{"k": "123"}', {'k': '123'}),
    ],
)
def test_json_model_from_json_parses_standard_json(json_content: str, expected_data: Any) -> None:
    """Decode standard JSON once, keeping the quoted form only where needed."""
    model = JsonModel()
    model.from_json(json_content)
    assert model.to_data() == expected_data


@pc.parametrize('json_content', ['hello', '"unterminated', ''])
def test_json_model_from_json_invalid_json(json_content: str) -> None:
    """Reject text that is not JSON, unlike direct loading."""
    model = JsonModel([1])
    with pytest.raises(ValidationError):
        model.from_json(json_content)
    assert model.to_data() == [1]
