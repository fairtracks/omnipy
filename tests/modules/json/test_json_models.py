from dataclasses import fields
import os
from textwrap import dedent
from typing import TypeAlias

from pydantic import ValidationError
import pytest
import pytest_cases as pc

from omnipy.modules.json.models import (_JsonDictOfScalarsM,
                                        JsonAnyDictM,
                                        JsonAnyListM,
                                        JsonCustomDictModel,
                                        JsonCustomListModel,
                                        JsonDictM,
                                        JsonDictModel,
                                        JsonDictOfDictsModel,
                                        JsonDictOfScalarsModel,
                                        JsonListM,
                                        JsonListModel,
                                        JsonListOfScalarsModel,
                                        JsonModel,
                                        JsonScalarM,
                                        JsonScalarModel)

from ..helpers.classes import CaseInfo


@pc.parametrize_with_cases('case', cases='.cases.json_data')
def test_json_models(case: CaseInfo) -> None:
    for field in fields(case.data_points):
        name = field.name
        for model_cls in case.model_classes_for_data_point(name):
            data = getattr(case.data_points, name)

            print('\n---')
            print(f'Field name: {name}')
            print(f'Model class: {model_cls.__name__}')
            print(f'Data input: {data}')

            if case.data_point_should_fail(name):
                with pytest.raises(ValidationError) as e:
                    model_cls(data)
                print(f'Error: {e}')
            else:

                model_obj = model_cls(data)
                print(f'repr(model_obj): {repr(model_obj)}')
                print(f'model_obj.contents: {model_obj.contents}')
                print(f'model_obj.to_data(): {model_obj.to_data()}')
                print(f'model_obj.to_json(): {model_obj.to_json(pretty=True)}')


def test_json_model_consistency_basic():
    MyJsonDictOfScalarsModel: TypeAlias = JsonCustomDictModel[JsonScalarM]
    MyJsonListOfScalarsModel: TypeAlias = JsonCustomListModel[JsonScalarM]

    example_dict_data = {'abc': 2312}
    assert JsonModel(example_dict_data) == JsonModel(
        __root__=JsonAnyDictM(__root__={'abc': JsonScalarM(__root__=2312)}))
    assert JsonDictModel(example_dict_data) == JsonDictModel(
        __root__=JsonAnyDictM(__root__={'abc': JsonScalarM(__root__=2312)}))
    assert JsonDictOfScalarsModel(example_dict_data) == JsonDictOfScalarsModel(
        __root__=_JsonDictOfScalarsM(__root__={'abc': JsonScalarM(__root__=2312)}))
    assert MyJsonDictOfScalarsModel(example_dict_data) == MyJsonDictOfScalarsModel(
        __root__=JsonDictM[JsonScalarM](__root__={
            'abc': JsonScalarM(__root__=2312)
        }))

    example_list_data = ['abc', 2312]
    assert JsonModel(example_list_data) == JsonModel(
        __root__=JsonAnyListM(__root__=[JsonScalarM(__root__='abc'), JsonScalarM(__root__=2312)]))
    assert JsonListModel(example_list_data) == JsonListModel(
        __root__=JsonAnyListM(__root__=[JsonScalarM(__root__='abc'), JsonScalarM(__root__=2312)]))
    assert JsonListOfScalarsModel(example_list_data) == JsonListOfScalarsModel(
        __root__=JsonAnyListM(__root__=[JsonScalarM(__root__='abc'), JsonScalarM(__root__=2312)]))
    assert MyJsonListOfScalarsModel(example_list_data) == MyJsonListOfScalarsModel(
        __root__=JsonListM[JsonScalarM](
            __root__=[JsonScalarM(__root__='abc'), JsonScalarM(__root__=2312)]))


# TODO: Revisit test_json_model_consistency_none_known_issue after pydantic v2 is supported.
@pytest.mark.skipif(
    os.getenv('OMNIPY_FORCE_SKIPPED_TEST') != '1',
    reason=dedent("""\
      Known issue with omnipy hack for pydantic v1. None values are not pushed to the JsonScalarM
      model, but stays at the JsonAnyDictM or JsonAnyListM parent. Not captured by equals for some
      reason (another bug?), so added check based on `.contents`.
      """))
def test_json_model_consistency_none_known_issue():
    MyJsonDictOfScalarsModel: TypeAlias = JsonCustomDictModel[JsonScalarM]
    MyJsonListOfScalarsModel: TypeAlias = JsonCustomListModel[JsonScalarM]

    example_dict_data = {'abc': None}
    assert JsonModel(example_dict_data) == JsonModel(
        __root__=JsonAnyDictM(__root__={'abc': JsonScalarM(__root__=None)}))

    assert JsonDictModel(example_dict_data) == JsonDictModel(
        __root__=JsonAnyDictM(__root__={'abc': JsonScalarM(__root__=None)}))

    assert JsonDictOfScalarsModel(example_dict_data) == JsonDictOfScalarsModel(
        __root__=_JsonDictOfScalarsM(__root__={'abc': JsonScalarM(__root__=None)}))

    assert MyJsonDictOfScalarsModel(example_dict_data) == MyJsonDictOfScalarsModel(
        __root__=JsonDictM[JsonScalarM](__root__={
            'abc': JsonScalarM(__root__=None)
        }))

    example_list_data = ['abc', None]
    assert JsonModel(example_list_data) == JsonModel(
        __root__=JsonAnyListM(__root__=[JsonScalarM(__root__='abc'), JsonScalarM(__root__=None)]))

    assert JsonListModel(example_list_data) == JsonListModel(
        __root__=JsonAnyListM(__root__=[JsonScalarM(__root__='abc'), JsonScalarM(__root__=None)]))

    assert JsonListOfScalarsModel(example_list_data) == JsonListOfScalarsModel(
        __root__=JsonAnyListM(__root__=[JsonScalarM(__root__='abc'), JsonScalarM(__root__=None)]))

    assert MyJsonListOfScalarsModel(example_list_data) == MyJsonListOfScalarsModel(
        __root__=JsonListM[JsonScalarM](
            __root__=[JsonScalarM(__root__='abc'), JsonScalarM(__root__=None)]))


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
def test_json_model_operations():
    a = JsonDictModel({'a': 1, 'b': 2, 'c': 3})
    a['c'] = 3

    b = JsonScalarM(1)
    assert (b + 1).contents == 2

    c = JsonScalarModel(1)
    assert (c + 1).contents == 2


def test_json_known_bug():
    c = JsonDictOfDictsModel({'a': {'b': {'c': 123}}})

    with pytest.raises(ValidationError):
        c['a'] = [123, 434]

    assert c.to_data() == {'a': {'b': {'c': 123}}}

    c = JsonDictOfDictsModel({'a': {'b': {'c': 123}}})

    # with pytest.raises(ValidationError):
    c['a'] = []

    assert c.to_data() == {'a': {}}
