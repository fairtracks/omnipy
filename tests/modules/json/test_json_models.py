from dataclasses import fields
import os
from textwrap import dedent
from typing import Annotated, TypeAlias

import pytest
import pytest_cases as pc

from omnipy.api.protocols.public.hub import IsRuntime
from omnipy.modules.json.models import (_JsonAnyDictM,
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
                                        JsonScalarModel)
from omnipy.modules.json.typedefs import JsonScalar
from omnipy.util.pydantic import ValidationError

from ...helpers.protocols import AssertModelOrValFunc
from ..helpers.classes import CaseInfo


@pc.parametrize_with_cases('case', cases='.cases.json_data')
def test_json_models(case: CaseInfo) -> None:
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
                # print(f'model_obj.contents: {model_obj.contents}')
                # print(f'model_obj.to_data(): {model_obj.to_data()}')
                # print(f'model_obj.to_json(): {model_obj.to_json(pretty=True)}')


def test_json_model_consistency_basic():
    MyJsonDictOfScalarsModel: TypeAlias = JsonCustomDictModel[JsonScalar]
    MyJsonListOfScalarsModel: TypeAlias = JsonCustomListModel[JsonScalar]

    example_dict_data = {'abc': 2312}
    assert JsonModel(example_dict_data).contents == _JsonAnyDictM(__root__={'abc': 2312})
    assert JsonDictModel(example_dict_data).contents == _JsonAnyDictM(__root__={'abc': 2312})
    assert JsonDictOfScalarsModel(example_dict_data).contents == _JsonDictM[JsonScalar](
        __root__={
            'abc': 2312
        })
    assert MyJsonDictOfScalarsModel(example_dict_data).contents == _JsonDictM[JsonScalar](
        __root__={
            'abc': 2312
        })

    example_list_data = ['abc', 2312]
    assert JsonModel(example_list_data).contents == _JsonAnyListM(__root__=['abc', 2312])
    assert JsonListModel(example_list_data).contents == _JsonAnyListM(__root__=['abc', 2312])
    assert JsonListOfScalarsModel(example_list_data).contents == _JsonListM[JsonScalar](
        __root__=['abc', 2312])
    assert MyJsonListOfScalarsModel(example_list_data).contents == _JsonListM[JsonScalar](
        __root__=['abc', 2312])


def test_json_model_consistency_with_none() -> None:
    MyJsonDictOfScalarsModel: TypeAlias = JsonCustomDictModel[JsonScalar]
    MyJsonListOfScalarsModel: TypeAlias = JsonCustomListModel[JsonScalar]

    example_dict_data = {'abc': None}
    assert JsonModel(example_dict_data).contents == _JsonAnyDictM(__root__={'abc': None})

    assert JsonDictModel(example_dict_data).contents == _JsonAnyDictM(__root__={'abc': None})

    assert JsonDictOfScalarsModel(example_dict_data).contents == _JsonDictM[JsonScalar](
        __root__={
            'abc': None
        })

    assert MyJsonDictOfScalarsModel(example_dict_data).contents == _JsonDictM[JsonScalar](
        __root__={
            'abc': None
        })

    example_list_data = ['abc', None]
    assert JsonModel(example_list_data).contents == _JsonAnyListM(__root__=['abc', None])

    assert JsonListModel(example_list_data).contents == _JsonAnyListM(__root__=['abc', None])

    assert JsonListOfScalarsModel(example_list_data).contents == _JsonListM[JsonScalar](
        __root__=['abc', None])

    assert MyJsonListOfScalarsModel(example_list_data).contents == _JsonListM[JsonScalar](
        __root__=['abc', None])


# TODO: Revisit test_error_list_of_single_dict_with_two_elements_known_issue after pydantic v2 is
#       supported.
@pytest.mark.skipif(
    os.getenv('OMNIPY_FORCE_SKIPPED_TEST') != '1',
    reason=dedent("""\
      Known issue with pydantic v1 due to attempting to parse a list of tuples to a dictionary.
      Here the inner dict is treated as a sequence, which returns the keys.
      """))
def test_error_list_of_single_dict_with_two_elements_known_issue():
    with pytest.raises(ValidationError):
        a = JsonDictModel([{'a': 1, 'b': 2}])
        assert a.to_data() == {'a': 'b'}


# TODO: Revisit test_json_known_issue after pydantic v2 is supported.
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
    """))
def test_error_dict_with_empty_list_known_issue(runtime: Annotated[IsRuntime, pytest.fixture]):
    dict_model = JsonDictModel()

    with pytest.raises(ValidationError):
        # A dict value of [] is interpreted by pydantic v1 as an empty dict
        dict_model = []
        assert dict_model.to_data() == {}

    dict_of_scalars_model = JsonDictOfScalarsModel({'a': 123})

    with pytest.raises(ValidationError):
        # Setting an integer value of a nested dict to [] validates as expected
        dict_of_scalars_model['a'] = []

    dict_of_dicts_model = JsonDictOfDictsModel({'a': {'x': 123}})

    with pytest.raises(ValidationError):
        # However, setting the value of a nested dict of dicts to [] still fails
        dict_of_dicts_model['a'] = []
        assert dict_of_dicts_model.to_data() == {'a': {}}


# TODO: Write tests for misc model operations relevant for JSON data. Try to avoid overlap with
#       with test_model.


def test_json_model_operations(
    runtime: Annotated[IsRuntime, pytest.fixture],
    assert_model_if_dyn_conv_else_val: Annotated[AssertModelOrValFunc, pytest.fixture],
):

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
    assert (e + 1).contents == 2
