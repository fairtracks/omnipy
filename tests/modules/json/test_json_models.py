from dataclasses import fields
import os
from textwrap import dedent
from typing import Annotated, TypeAlias

from pydantic import ValidationError
import pytest
import pytest_cases as pc

from omnipy.api.protocols.public.hub import IsRuntime
from omnipy.modules.json.models import (_JsonAnyDictM,
                                        _JsonAnyListM,
                                        _JsonDictM,
                                        _JsonListM,
                                        _JsonScalarM,
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

from ...helpers.functions import assert_model_or_val
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
                with pytest.raises(ValidationError) as e:
                    model_cls(data)
                # print(f'Error: {e}')
            else:
                model_obj = model_cls(data)

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


# TODO: Revisit test_json_model_consistency_none_known_issue after pydantic v2 is supported.
@pytest.mark.skipif(
    os.getenv('OMNIPY_FORCE_SKIPPED_TEST') != '1',
    reason=dedent("""\
      Known issue with omnipy hack for pydantic v1. None values are not pushed to the _JsonScalarM
      model, but stays at the _JsonAnyDictM or _JsonAnyListM parent. Not captured by equals for some
      reason (another bug?), so added check based on `.contents`.
      """))
def test_json_model_consistency_none_known_issue():
    MyJsonDictOfScalarsModel: TypeAlias = JsonCustomDictModel[_JsonScalarM]
    MyJsonListOfScalarsModel: TypeAlias = JsonCustomListModel[_JsonScalarM]

    example_dict_data = {'abc': None}
    assert JsonModel(example_dict_data).contents == _JsonAnyDictM(__root__={'abc': None})

    assert JsonDictModel(example_dict_data).contents == _JsonAnyDictM(__root__={'abc': None})

    assert JsonDictOfScalarsModel(example_dict_data).contents == _JsonDictM[_JsonScalarM](
        __root__={
            'abc': None
        })

    assert MyJsonDictOfScalarsModel(example_dict_data).contents == _JsonDictM[_JsonScalarM](
        __root__={
            'abc': None
        })

    example_list_data = ['abc', None]
    assert JsonModel(example_list_data).contents == _JsonAnyListM(__root__=['abc', None])

    assert JsonListModel(example_list_data).contents == _JsonAnyListM(__root__=['abc', None])

    assert JsonListOfScalarsModel(example_list_data).contents == _JsonListM[_JsonScalarM](
        __root__=['abc', None])

    assert MyJsonListOfScalarsModel(example_list_data).contents == _JsonListM[_JsonScalarM](
        __root__=['abc', None])


# TODO: Revisit test_error_list_of_single_dict_with_two_elements and
#  case_frozen_dicts_no_type_args_known_issue after pydantic v2 is supported.
@pytest.mark.skipif(
    os.getenv('OMNIPY_FORCE_SKIPPED_TEST') != '1',
    reason=dedent("""\
      Known issue with pydantic v1 due to attempting to parse a list of tuples to a dictionary.
      Here the inner dict is treated as a sequence, which returns the keys.
      """))
def test_error_list_of_single_dict_with_two_elements():
    with pytest.raises(ValidationError):
        a = JsonDictModel([{'a': 1, 'b': 2}])
        assert a.to_data() == {'a': 'b'}


# TODO: Write tests for misc model operations relevant for JSON data. Try to avoid overlap with
#       with test_model.
@pytest.mark.parametrize('dyn_convert', [False, True])
def test_json_model_operations(
    runtime: Annotated[IsRuntime, pytest.fixture],
    dyn_convert: bool,
):
    runtime.config.data.dynamically_convert_elements_to_models = dyn_convert

    a = JsonListModel([1, 2, 3])
    assert_model_or_val(dyn_convert, a[0], int, 1)

    b = JsonModel([1, 2, 3])
    assert_model_or_val(dyn_convert, b[0], int, 1)

    c = JsonDictModel({'a': 1, 'b': 2, 'c': 3})
    assert_model_or_val(dyn_convert, c['c'], int, 3)

    c |= JsonDictModel({'b': 4, 'd': 5})
    assert_model_or_val(dyn_convert, c['b'], int, 4)
    assert_model_or_val(dyn_convert, c['c'], int, 3)
    assert_model_or_val(dyn_convert, c['d'], int, 5)

    d = JsonModel({'a': 1, 'b': 2, 'c': 3})
    assert_model_or_val(dyn_convert, d['c'], int, 3)

    d |= JsonModel({'b': 4, 'd': 5})
    assert_model_or_val(dyn_convert, c['b'], int, 4)
    assert_model_or_val(dyn_convert, c['c'], int, 3)
    assert_model_or_val(dyn_convert, c['d'], int, 5)

    e = _JsonScalarM(1)
    assert (e + 1).contents == 2

    f = JsonScalarModel(1)
    assert (f + 1).contents == 2


def test_json_known_bug():
    c = JsonDictOfDictsModel({'a': {'b': {'c': 123}}})

    with pytest.raises(ValidationError):
        c['a'] = [123, 434]

    assert c.to_data() == {'a': {'b': {'c': 123}}}

    c = JsonDictOfDictsModel({'a': {'b': {'c': 123}}})

    # with pytest.raises(ValidationError):
    c['a'] = []

    assert c.to_data() == {'a': {}}
